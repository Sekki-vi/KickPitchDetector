import os, sys, math, threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Optional DnD
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKDND_AVAILABLE = True
except Exception:
    TKDND_AVAILABLE = False

# Numpy + audio backends
try:
    import numpy as np
except Exception as e:
    raise SystemExit("This app requires numpy. Install with: pip install numpy")

def safe_import_soundfile_or_librosa():
    """Prefer soundfile, fallback to librosa; return (backend_name, loader_fn)."""
    try:
        import soundfile as sf
        def load_sf(path, target_sr=48000):
            data, sr = sf.read(path, always_2d=False)
            if data.ndim == 2:
                data = data.mean(axis=1)
            if sr != target_sr:
                data = resample_linear(data, sr, target_sr)
                sr = target_sr
            return data.astype(np.float32), sr
        return "soundfile", load_sf
    except Exception:
        try:
            import librosa
            def load_lr(path, target_sr=48000):
                y, sr = librosa.load(path, sr=target_sr, mono=True)
                return y.astype(np.float32), sr
            return "librosa", load_lr
        except Exception:
            return None, None

#Constants
FRAME = 4096
HOP   = 256
MIN_HZ = 30.0
MAX_HZ = 150.0
LP_CUTOFF = 300.0

NOTE_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

def resample_linear(x, sr_in, sr_out):
    if sr_in == sr_out:
        return x
    ratio = sr_out / sr_in
    n_out = int(round(len(x) * ratio))
    t_in = np.linspace(0.0, 1.0, num=len(x), endpoint=False)
    t_out = np.linspace(0.0, 1.0, num=n_out, endpoint=False)
    return np.interp(t_out, t_in, x).astype(np.float32)

def lowpass_fft(x, sr, cutoff=300.0):
    n = len(x)
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, d=1.0/sr)
    mask = freqs <= cutoff
    X[~mask] = 0.0
    return np.fft.irfft(X, n=n).astype(np.float32)

def yin_cmndf(frame, min_tau, max_tau):
    N = len(frame)
    d = np.zeros(max_tau + 1, dtype=np.float64)
    for tau in range(1, max_tau + 1):
        diff = frame[:N - tau] - frame[tau:N]
        d[tau] = np.dot(diff, diff)
    cmndf = np.zeros_like(d)
    cmndf[0] = 1.0
    running = 0.0
    for tau in range(1, max_tau + 1):
        running += d[tau]
        cmndf[tau] = d[tau] * tau / running if running > 0 else 1.0
    thresh = 0.1
    tau_est = -1
    for tau in range(1, max_tau + 1):
        if cmndf[tau] < thresh:
            while tau + 1 <= max_tau and cmndf[tau + 1] < cmndf[tau]:
                tau += 1
            tau_est = tau
            break
    if tau_est < 0:
        rng = cmndf[min_tau:max_tau + 1]
        tau_est = int(np.argmin(rng)) + min_tau
    return tau_est

def hz_to_midi(hz):
    return 69.0 + 12.0 * math.log2(hz / 440.0)

def midi_to_name(midi):
    pc = int(midi) % 12
    octave = int(midi) // 12 - 1
    return f"{NOTE_NAMES[pc]}{octave}"

def detect_pitch(y, sr):
    # focus on sub content
    y = lowpass_fft(y, sr, cutoff=LP_CUTOFF)

    win = 0.5 * (1.0 - np.cos(2.0 * np.pi * np.arange(FRAME) / (FRAME - 1)))
    min_tau = max(1, int(sr / max(1.0, MAX_HZ)))
    max_tau = max(min_tau + 1, int(sr / max(1.0, MIN_HZ)))

    f0s = []
    for start in range(0, len(y) - FRAME, HOP):
        x = y[start:start+FRAME].astype(np.float64).copy()
        x *= win
        x -= x.mean()
        tau = yin_cmndf(x, min_tau, max_tau)
        f0 = sr / tau if tau > 0 else 0.0
        if MIN_HZ <= f0 <= MAX_HZ:
            f0s.append(f0)

    if not f0s:
        return None, None, None

    f0s = np.array(f0s, dtype=np.float64)
    hz = float(np.median(f0s))
    midi = int(round(hz_to_midi(hz)))
    note = midi_to_name(midi) if 0 <= midi <= 127 else "--"
    return hz, midi, note

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Kick Pitch Detector")
        self.root.geometry("520x320")
        self.backend_name, self.loader = safe_import_soundfile_or_librosa()
        if self.backend_name is None:
            messagebox.showerror("Missing dependency",
                                 "Please install either 'soundfile' (recommended) or 'librosa'.\n\npip install soundfile")
        self.build_ui()

    def build_ui(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        header = ttk.Label(self.root, text="Kick Pitch Detector",
                           font=("Segoe UI", 16, "bold"))
        header.pack(pady=(12, 6))

        info = ttk.Label(self.root, text=f"FRAME={FRAME}  HOP={HOP}   Range: {MIN_HZ:.0f}–{MAX_HZ:.0f} Hz (fixed)",
                         font=("Segoe UI", 10))
        info.pack(pady=(0, 8))

        # Drop zone or fallback
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        self.drop = tk.Label(frame, relief="ridge", bd=2, text="Drop audio file here (WAV/AIFF)\n—or— Click Browse",
                             font=("Segoe UI", 12), justify="center")
        self.drop.pack(fill="both", expand=True, pady=6)

        browse = ttk.Button(self.root, text="Browse...", command=self.browse)
        browse.pack(pady=(0, 8))

        # Results
        self.result = ttk.Label(self.root, text="—", font=("Segoe UI", 14))
        self.result.pack(pady=(4, 8))

        # Drag-and-drop binding
        if TKDND_AVAILABLE:
            # Register drop target
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
            self.drop.configure(text="Drop audio file here (WAV/AIFF)")
        else:
            self.drop.configure(text="Click Browse to choose an audio file (install tkinterdnd2 for drag-and-drop)")

    def browse(self):
        fn = filedialog.askopenfilename(title="Choose Audio File",
                                        filetypes=[("Audio files", "*.wav *.aif *.aiff *.flac *.mp3 *.ogg"),
                                                   ("All files", "*.*")])
        if fn:
            self.process_async(fn)

    def on_drop(self, event):
        data = event.data
        if isinstance(data, str):
            path = data.strip()
            if path.startswith("{") and path.endswith("}"):
                path = path[1:-1]
            if " " in path and not os.path.exists(path):
                path = path.split(" ")[0]
            self.process_async(path)

    def process_async(self, path):
        self.result.config(text="Analyzing…")
        t = threading.Thread(target=self._analyze_file, args=(path,), daemon=True)
        t.start()

    def _analyze_file(self, path):
        try:
            if self.loader is None:
                raise RuntimeError("Audio backend not available. Install 'soundfile' (pip install soundfile).")
            y, sr = self.loader(path, target_sr=48000)
            hz, midi, note = detect_pitch(y, sr)
            if hz is None:
                txt = "No stable pitch in 30–150 Hz. Try a longer sample."
            else:
                txt = f"Estimated: {hz:.2f} Hz   |   {note} (MIDI {midi})"
        except Exception as e:
            txt = f"Error: {e}"
        # Update UI
        def update():
            self.result.config(text=txt)
        self.root.after(0, update)

def main():
    if TKDND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
