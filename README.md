# 🎮 Cosmic Byte Ares Controller Manager

A desktop application for **real-time testing, calibration, and profile management** of the Cosmic Byte Ares gamepad (Xbox 360 protocol).

---

## ✨ Features

- 🕹️ **Live Input Monitoring** — Real-time axis, button, and D-pad (HAT) readings
- ⚙️ **Dead Zone & Sensitivity Control** — Fine-tune analog stick responsiveness
- 🔀 **Button Remapping** — Reassign any controller input to your preference
- 💾 **Profile System** — Save, load, and manage named configurations as JSON
- 📦 **Standalone Executable** — No Python installation needed for end users

---

## 🖥️ Requirements

- Python 3.8+
- Cosmic Byte Ares controller (or any Xbox 360 protocol gamepad)

Install dependencies:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
pygame-ce
PyQt5
pyinstaller
```

---

## 🚀 Running the App

```bash
python main.py
```

---

## 📦 Building the Executable

To build a standalone `.exe` for Windows:

```bash
python build.py
```

Output will be at:
```
dist/CosmicByteAresManager.exe
```

---

## 📁 Project Structure

```
├── main.py          # Entry point
├── ui.py            # PyQt5 GUI
├── controller.py    # Controller input handling (pygame-ce)
├── profiles.py      # Save/load JSON profiles
├── build.py         # PyInstaller build script
├── requirements.txt
└── profiles/        # Saved controller profiles (auto-created)
```

---

## 🎮 Controller Info

| Property | Value |
|----------|-------|
| Protocol | Xbox 360 |
| VID | 0x45e |
| PID | 0x28e |

---

## 📄 License

MIT License — free to use and modify.
