# 🥁 Kick Pitch Detector

**KickPitchDetector** is a standalone Python desktop application that analyzes audio samples to detect the **fundamental frequency (pitch)** of kick drums, optimized for the low-end range between **30 Hz and 150 Hz**.
It’s designed for music producers and sound designers who want a quick, lightweight way to identify the key of their drum samples without opening a full DAW.

---

## 🚀 Features

* 🎵 **Accurate Low-End Pitch Detection** using a customized **YIN/CMNDF** algorithm.
* 🪄 **Drag-and-Drop GUI** built with **Tkinter** for easy sample analysis.
* ⚙️ **Configurable Frequency Range** (default: 30–150 Hz).
* 💾 **Standalone Executable (.exe)** built with **PyInstaller** — no dependencies required.
* 📊 **Real-Time Display** of detected frequency and corresponding musical note.

---

## 🧠 How It Works

The program uses the **YIN algorithm** (with Cumulative Mean Normalized Difference Function) to estimate the fundamental frequency of transient signals.
Each sample’s waveform is analyzed frame-by-frame, returning the most stable pitch candidate within the defined range.

Algorithm overview:

1. Load `.wav` or `.aiff` file using **SoundFile** or **Librosa**.
2. Convert to mono and normalize amplitude.
3. Apply the YIN/CMNDF pitch detection method.
4. Filter results to stay within the **min_hz** and **max_hz** bounds.
5. Display the dominant frequency and musical note in the UI.

---

## 🧩 Tech Stack

| Category             | Tools / Libraries                         |
| -------------------- | ----------------------------------------- |
| **Language**         | Python 3.10 +                             |
| **Libraries**        | NumPy · SoundFile · Tkinter · PyInstaller |
| **Algorithm**        | YIN / CMNDF                               |
| **GUI Framework**    | Tkinter                                   |
| **OS Compatibility** | Windows (.exe), macOS (source)            |

---

## 📦 Installation

### Option 1: Run the Executable

1. Download the latest `.exe` from the [Releases](https://github.com/Sekki-vi/KickPitchDetector/releases) page.
2. Run `KickPitchDetector.exe` — no installation needed.

### Option 2: Run from Source

```bash
git clone https://github.com/Sekki-vi/KickPitchDetector.git
cd KickPitchDetector
pip install -r requirements.txt
python main.py
```

---

## 🧰 Usage

1. Open the app.
2. Drag and drop a kick sample (`.wav` or `.aiff`) into the window.
3. The detected **frequency** (Hz) and **musical note** appear instantly.

---

## 📸 Example Output

| Sample         | Detected Frequency | Note |
| -------------- | ------------------ | ---- |
| `kick_808.wav` | 55 Hz              | A1   |
| `deep_sub.wav` | 43 Hz              | F1   |

*(Add a screenshot of your GUI here if you have one!)*

---

## 🧪 Future Improvements

* Add batch processing for multiple samples.
* Display waveform visualization.
* Implement MIDI note export option.
* Add macOS/Linux standalone builds.

---

## 👨‍💻 Author

**Kenyon Jones**
Computer Science graduate & software developer passionate about music tech and creative audio tools.

* 📧 [kenyonj4@gmail.com](mailto:kenyonj4@gmail.com)
* 🌐 [Portfolio Website](https://your-portfolio-link.com)
* 💻 [GitHub @Sekki-vi](https://github.com/Sekki-vi)

---

Would you like me to make a **shorter version (for recruiters)** or a **visual version (with badges, emojis, and screenshots)** of this README next?


