# SpacePilot XML Editor

The **SpacePilot XML Editor** lets you conveniently edit axis and button mappings for 3Dconnexion SpacePilot/SpaceMouse devices via a user-friendly graphical interface.

---

## Features

- Open, edit, and save 3Dconnexion XML configuration files
- Support for split axis ranges (e.g., keybindings for forward/backward)
- Keycodes are shown as readable keys and saved correctly
- Automatic backup of the original file before overwriting (`*.bak`)
- Easy to use, no installation required (can be used as EXE)
- Default directory: Opens in the 3Dconnexion configuration folder
- Supports all main axes (X, Y, Z, Rx, Ry, Rz)
- Adjustable deadband
- No dependencies except standard Python and tkinter

---

## Installation & Usage

1. **Start the app:**  
   - As Python script:  
     ```bash
     python main.py
     ```
   - As Windows EXE:  
     Simply double-click `SpacePilot-XML-Editor.exe` (no Python installation required).

2. **Open XML:**  
   The open dialog will initially point to the 3Dconnexion configuration folder (`%APPDATA%\3Dconnexion\3DxWare\Cfg`), where your device configs are located.

3. **Edit & Save:**  
   - Changes to axes or buttons are reflected instantly in the UI.
   - When saving, a backup (`.bak`) of the old file is always created automatically.

---

## Notes

- **Backup:**  
  Before each save, the original XML is backed up as a `.bak` file.
- **Release Version:**  
  This is the first public release (`v1.0.0`).  
  Feedback, feature requests, and bug reports are welcome via GitHub Issues!
- **License:**  
  GNU GPL v3

---


