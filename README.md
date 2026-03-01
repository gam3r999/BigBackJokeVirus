# 📂 BigBackJokeVirus

![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)

A harmless, 100% reversible "malware" simulation designed for pranking friends. This script triggers a heavy sequence of audio cues, visual GDI glitches, image popups, and a fake BSOD (Blue Screen of Death).

> **⚠️ Disclaimer:** This script is for educational and prank purposes only. Do not use it on systems without explicit permission. It is designed to be annoying and startling, but it does not delete files or damage hardware.

---

## 🛠 Features

* **Dual-Channel Audio:** Plays music.wav and byebyte.wav simultaneously using separate mixer channels for maximum "earrape" effect.
* **GDI Chaos:** 9 different screen-warping effects (Inversion, Sine Wobble, Zoom Tunnel, Kaleidoscope, Swirl, etc.).
* **Image Popups:** Spawns multiple top-most windows flashing images/GIFs from your local /images folder.
* **Wallpaper Hijack:** Backs up the original wallpaper path to a temp folder and swaps it for a prank image.
* **Fake BSOD:** A full-screen, un-escapable fake crash screen to finish the sequence.

---

## 📂 Folder Structure

To compile or run successfully, you must maintain this structure in your project directory:

.
├── big_back_virus.py   # The main prank script
├── music.wav           # Main background audio (Big Back)
├── byebyte.wav         # Secondary audio layer (Must be .wav)
├── bsod.png            # The image used for the fake crash
└── images/             # Folder containing your prank images/GIFs

---

## 🚀 Installation & Usage

### 1. Requirements
Ensure you have Python 3.8+ installed. Install the necessary libraries via terminal:
pip install pygame pillow

### 2. Running the Script
To run the Python version directly:
python big_back_virus.py

### 3. Compiling to Portable EXE
If you want to bundle everything into a single executable file to send to a friend, use PyInstaller:
pyinstaller --noconfirm --onefile --windowed --add-data "images;images" --add-data "music.wav;." --add-data "byebyte.wav;." --add-data "bsod.png;." "big_back_virus.py"

*The resulting file will be in the /dist folder.*

---

## 🕒 Timeline Sequence

| Time | Action |
| :--- | :--- |
| 0s | music.wav begins playing (Big Back theme). |
| 6s | Screen popups spawn + GDI effects start + byebyte.wav joins the audio. |
| 36s | Desktop wallpaper changes to a prank image. |
| 38s | Popups close and the Fake BSOD covers the entire screen. |
| 58s | Script exits, GDI effects stop, and audio cuts. |

---

## 📜 License

This project is licensed under the Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license.

* Attribution: You must give appropriate credit.
* NonCommercial: You may not use the material for commercial purposes.
* ShareAlike: If you remix, transform, or build upon the material, you must distribute your contributions under the same license.

View the Full License Text (https://creativecommons.org/licenses/by-nc-sa/4.0/) for more details.
