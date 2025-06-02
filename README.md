# SpacePilot XML Editor

Mit dem **SpacePilot XML Editor** kannst du die Achsenbelegungen von 3Dconnexion SpacePilot/SpaceMouse-Geräten bequem über eine grafische Benutzeroberfläche bearbeiten.

---

## Features

- Öffnen, Bearbeiten und Speichern von 3Dconnexion XML-Konfigurationen
- Unterstützt geteilte Achsenbereiche (z.B. Keybindings für Vorwärts/Rückwärts)
- Keycodes werden übersichtlich als Tasten angezeigt und gespeichert
- Automatisches Backup der Originaldatei vor dem Überschreiben (`*.bak`)
- Übersichtliche Bedienung ohne Installation (als EXE nutzbar)
- Standard-Speicherort: Öffnet automatisch den 3Dconnexion-Konfigurationsordner
- Unterstützung für alle Hauptachsen (X, Y, Z, Rx, Ry, Rz)
- Deadband einstellbar
- Keine externen Abhängigkeiten außer Standard-Python + tkinter

---

## Installation & Nutzung

1. **Starten der App:**  
   - Als Python-Skript:  
     ```bash
     python main.py
     ```
   - Als Windows-EXE:  
     Einfach die `SpacePilot-XML-Editor.exe` doppelklicken (kein Python nötig).

2. **XML öffnen:**  
   Beim ersten Öffnen startet der Dialog direkt im 3Dconnexion-Konfigurationsordner (`%APPDATA%\3Dconnexion\3DxWare\Cfg`).  
   Dort findest du deine Gerätekonfigurationen.

3. **Bearbeiten & Speichern:**  
   - Änderungen an den Achsen oder Tasten werden sofort im UI sichtbar.
   - Beim Speichern wird immer automatisch ein Backup (`.bak`) der alten Datei angelegt.

---

## Hinweise

- **Backup:**  
  Vor jedem Speichern wird die originale XML automatisch als `.bak` gesichert.
- **Release-Version:**  
  Dies ist die erste veröffentlichte Version (`v1.0.0`).  
  Rückmeldungen, Featurewünsche oder Bugreports gerne als GitHub-Issue!
- **Lizenz:**  
  GNU GPL v3

---

