import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import xml.etree.ElementTree as ET

MOVE_AXES = [
    ("X", "HIDMultiAxis_X"),
    ("Y", "HIDMultiAxis_Y"),
    ("Z", "HIDMultiAxis_Z"),
]
ROT_AXES = [
    ("Rx", "HIDMultiAxis_Rx"),
    ("Ry", "HIDMultiAxis_Ry"),
    ("Rz", "HIDMultiAxis_Rz"),
]

KEYCODE_TO_LABEL = {
    "4": "A", "5": "B", "6": "C", "7": "D", "8": "E", "9": "F",
    "A": "G", "B": "H", "C": "I", "D": "J", "E": "K", "F": "L",
    "10": "M", "11": "N", "12": "O", "13": "P", "14": "Q", "15": "R",
    "16": "S", "17": "T", "18": "U", "19": "V", "1A": "W", "1B": "X",
    "1C": "Y", "1D": "Z",
    "1E": "1", "1F": "2", "20": "3", "21": "4", "22": "5", "23": "6",
    "24": "7", "25": "8", "26": "9", "27": "0",
    "28": "Enter", "29": "Esc", "2A": "Backspace", "2B": "Tab",
    "2C": "Space", "2D": "-", "2E": "=", "2F": "[", "30": "]", "31": "\\",
    "32": "#", "33": ";", "34": "'", "35": "`", "36": ",", "37": ".", "38": "/",
    "39": "CapsLock",
    "3A": "F1", "3B": "F2", "3C": "F3", "3D": "F4", "3E": "F5", "3F": "F6",
    "40": "F7", "41": "F8", "42": "F9", "43": "F10", "44": "F11", "45": "F12",
    "4F": "Right", "50": "Left", "51": "Down", "52": "Up",
    # ... weitere Tasten
}
LABEL_TO_KEYCODE = {v: k for k, v in KEYCODE_TO_LABEL.items()}
KEYCODES = list(LABEL_TO_KEYCODE.keys())

OUTPUT_ACTIONS = [
    "KB_Keystroke",
    "HIDMouse_Wheel",
]

def shorten_path(path, maxlen=60):
    if len(path) <= maxlen:
        return path
    parts = path.split(os.sep)
    if len(parts) > 2:
        return parts[0] + os.sep + "..." + os.sep + parts[-1]
    return "..." + path[-maxlen:]

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

root = tk.Tk()
root.title("SpacePilot Pro Achsen-Editor")

root.geometry("950x900")
root.minsize(950, 900)
root.maxsize(950, 900)

# --- Menüleiste / Buttonleiste ---
menu_frame = tk.Frame(root)
menu_frame.pack(fill="x", padx=10, pady=(8,0))
tk.Button(menu_frame, text="XML laden", command=lambda: ask_for_xml()).pack(side="left", padx=3)
tk.Button(menu_frame, text="XML speichern", command=lambda: save_xml()).pack(side="left", padx=3)
tk.Button(menu_frame, text="Exit", command=lambda: exit_app()).pack(side="right", padx=3)

# --- Dateipfad-Anzeige oben ---
loaded_file_var = tk.StringVar(value="Keine Datei geladen.")
loaded_file_label = tk.Label(root, textvariable=loaded_file_var, anchor="w", relief="groove", width=80)
loaded_file_label.pack(fill="x", padx=10)
def update_loaded_file(path):
    display = shorten_path(path, 70)
    loaded_file_var.set(display)
    loaded_file_label.tooltip = ToolTip(loaded_file_label, path)

# --- Statusleiste (unten) ---
status_var = tk.StringVar(value="Bereit.")
tk.Label(root, textvariable=status_var, relief="sunken", anchor="w").pack(fill="x", side="bottom")

# --- XML-Logik-Platzhalter ---
current_xml_path = None

def ask_for_xml():
    global current_xml_path
    filename = filedialog.askopenfilename(
        title="Bitte XML-Datei wählen",
        filetypes=[("XML-Dateien", "*.xml"), ("Alle Dateien", "*.*")]
    )
    if filename:
        current_xml_path = filename
        update_loaded_file(filename)
        status_var.set(f"Geladen: {os.path.basename(filename)}")
        load_axes_from_xml(filename)
    else:
        status_var.set("Keine XML geladen.")

def save_xml():
    global current_xml_path
    if not current_xml_path:
        filename = filedialog.asksaveasfilename(
            title="XML-Datei speichern unter...",
            defaultextension=".xml",
            filetypes=[("XML-Dateien", "*.xml"), ("Alle Dateien", "*.*")]
        )
        if not filename:
            status_var.set("Speichern abgebrochen.")
            return
        current_xml_path = filename
        update_loaded_file(filename)
    else:
        filename = current_xml_path

    # Backup anlegen
    if os.path.exists(filename):
        bak_path = filename + ".bak"
        try:
            shutil.copy2(filename, bak_path)
        except Exception as e:
            messagebox.showwarning("Backup fehlgeschlagen", f"Backup konnte nicht erstellt werden:\n{e}")

    try:
        tree = ET.parse(filename)
        root_xml = tree.getroot()
    except Exception:
        # Neue Datei anlegen, falls sie noch nicht existiert oder fehlerhaft ist
        root_xml = ET.Element("AppCfg")
        tree = ET.ElementTree(root_xml)

    # --- Devices/AxisBank Struktur finden oder anlegen ---
    devices = root_xml.find("Devices")
    if devices is None:
        devices = ET.SubElement(root_xml, "Devices")
    # Wir nehmen einfach das erste Device mit AxisBank oder erzeugen eines
    device = None
    for d in devices.findall("Device"):
        if d.find("AxisBank") is not None:
            device = d
            break
    if device is None:
        device = ET.SubElement(devices, "Device")
        ET.SubElement(device, "ID").text = "ID_Standard_3D_Mouse"
    axis_bank = device.find("AxisBank")
    if axis_bank is None:
        axis_bank = ET.SubElement(device, "AxisBank")
        ET.SubElement(axis_bank, "Name").text = "Default"
        ET.SubElement(axis_bank, "ID").text = "Default"

    # Lösche existierende Achsen (wir schreiben alle neu)
    for old_axis in axis_bank.findall("Axis"):
        axis_bank.remove(old_axis)

    # Schreibe aktuelle GUI-Daten in die XML
    for vals in axes_state:
        action_id = vals["axis_id"]
        # Split-Check
        if not vals["enabled"].get():
            continue
        if vals["split"].get():
            # Bereich 1 (min1, max1)
            write_axis_to_xml(axis_bank, action_id, vals["min1"].get(), vals["max1"].get(),
                              vals["output1"].get(), vals["key1"].get(), vals["deadband"].get())
            # Bereich 2 (min2, max2)
            write_axis_to_xml(axis_bank, action_id, vals["min2"].get(), vals["max2"].get(),
                              vals["output2"].get(), vals["key2"].get(), vals["deadband"].get())
        else:
            write_axis_to_xml(axis_bank, action_id, vals["min_single"].get(), vals["max_single"].get(),
                              vals["output_single"].get(), vals["key_single"].get(), vals["deadband"].get())

    # Schreibe XML in Datei
    ET.indent(tree, space="  ", level=0)
    try:
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        status_var.set(f"Gespeichert: {os.path.basename(filename)}")
    except Exception as e:
        messagebox.showerror("Speichern fehlgeschlagen", f"Fehler: {e}")

def write_axis_to_xml(axis_bank, action_id, min_val, max_val, output_id, key_label, deadband_val):
    axis = ET.SubElement(axis_bank, "Axis")
    ET.SubElement(axis, "Enabled").text = "true"
    inp = ET.SubElement(axis, "Input")
    ET.SubElement(inp, "ActionID").text = action_id
    ET.SubElement(inp, "Min").text = str(min_val)
    ET.SubElement(inp, "Max").text = str(max_val)
    ET.SubElement(inp, "Deadband").text = str(deadband_val)   # <-- Hierhin!
    out = ET.SubElement(axis, "Output")
    ET.SubElement(out, "ActionID").text = output_id
    if output_id == "KB_Keystroke":
        ks = ET.SubElement(out, "KeyStroke")
        key_code = LABEL_TO_KEYCODE.get(key_label, key_label)
        ET.SubElement(ks, "Key").text = key_code
        ET.SubElement(out, "RepeatStyle").text = "PressAndHold"


def exit_app():
    if messagebox.askokcancel("Beenden", "Wirklich beenden?"):
        root.destroy()

axes_state = []

main_axes_frame = tk.Frame(root)
main_axes_frame.pack(fill="both", expand=True, padx=10, pady=5)
main_axes_frame.pack_propagate(False)

move_axes_frame = tk.LabelFrame(main_axes_frame, text="Bewegen/Zoomen (X, Y, Z)", padx=10, pady=5)
move_axes_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
rot_axes_frame = tk.LabelFrame(main_axes_frame, text="Rotation (Rx, Ry, Rz)", padx=10, pady=5)
rot_axes_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
main_axes_frame.grid_columnconfigure(0, weight=1)
main_axes_frame.grid_columnconfigure(1, weight=1)

root.update_idletasks()
MIN_FRAME_HEIGHT = 520
move_axes_frame.config(height=MIN_FRAME_HEIGHT)
rot_axes_frame.config(height=MIN_FRAME_HEIGHT)
move_axes_frame.grid_propagate(False)
rot_axes_frame.grid_propagate(False)

def show_hide_key_combo(combo_widget, output_var):
    if output_var.get() == "KB_Keystroke":
        combo_widget.grid()
    else:
        combo_widget.grid_remove()

def toggle_axis_enabled(idx):
    vals = axes_state[idx]
    enabled = vals["enabled"].get()
    if enabled:
        vals["content_frame"].pack(fill="x")
        output_var = vals["output_single"]
        axis_id = vals["axis_id"]
        if output_var.get() in OUTPUT_ACTIONS:
            output_var.set(axis_id)
        show_hide_key_combo(vals["key_single_widget"], vals["output_single"])
        show_hide_key_combo(vals["key1_widget"], vals["output1"])
        show_hide_key_combo(vals["key2_widget"], vals["output2"])
    else:
        vals["content_frame"].pack_forget()

def toggle_axis_split(idx):
    vals = axes_state[idx]
    split = vals["split"].get()
    if split:
        vals["bereich_single_frame"].grid_remove()
        vals["bereich_split_frame"].grid()
        vals["min1"].set("-512")
        vals["max1"].set("0")
        vals["min2"].set("1")
        vals["max2"].set("511")
    else:
        vals["bereich_split_frame"].grid_remove()
        vals["bereich_single_frame"].grid()
        vals["min_single"].set("-512")
        vals["max_single"].set("511")

def add_axis_ui(parent_frame, axis_name, action_id, idx, row_index):
    frame = tk.LabelFrame(parent_frame, text=f"{axis_name}-Achse", padx=10, pady=5)
    frame.grid(row=row_index, column=0, sticky="ew", pady=5)
    enabled_var = tk.BooleanVar(value=False)
    enable_check = tk.Checkbutton(frame, text="Aktiviert", variable=enabled_var,
                                  command=lambda i=idx: toggle_axis_enabled(i))
    enable_check.pack(anchor="w")
    content_frame = tk.Frame(frame)

    tk.Label(content_frame, text=f"Input: {action_id}", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0,2))
    split_var = tk.BooleanVar(value=False)
    split_check = tk.Checkbutton(content_frame, text="Aufgeteilt", variable=split_var,
                                 command=lambda i=idx: toggle_axis_split(i))
    split_check.grid(row=0, column=1, sticky="w", pady=(0,2))
    tk.Label(content_frame, text="Deadband:").grid(row=0, column=2, sticky="w", padx=(16,0), pady=(0,2))
    deadband_var = tk.StringVar(value="100")
    tk.Entry(content_frame, width=8, textvariable=deadband_var).grid(row=0, column=3, sticky="w", pady=(0,2))

    bereich_single_frame = tk.Frame(content_frame)
    bereich_single_frame.grid(row=1, column=0, columnspan=4, sticky="w", padx=18, pady=(0,2))
    min_single = tk.StringVar(value="-512")
    max_single = tk.StringVar(value="511")
    tk.Label(bereich_single_frame, text="Min:").grid(row=0, column=0, sticky="w")
    tk.Entry(bereich_single_frame, width=6, textvariable=min_single).grid(row=0, column=1)
    tk.Label(bereich_single_frame, text="Max:").grid(row=0, column=2, sticky="w")
    tk.Entry(bereich_single_frame, width=6, textvariable=max_single).grid(row=0, column=3)
    tk.Label(bereich_single_frame, text="Output:").grid(row=0, column=4, sticky="w")
    output_choices = OUTPUT_ACTIONS + [action_id]
    output_single = tk.StringVar(value=action_id)
    output_combo = ttk.Combobox(bereich_single_frame, textvariable=output_single, values=output_choices, width=18, state="readonly")
    output_combo.grid(row=0, column=5)
    key_single = tk.StringVar(value="W")
    key_single_combo = ttk.Combobox(bereich_single_frame, textvariable=key_single, values=KEYCODES, width=12, state="readonly")
    key_single_combo.grid(row=0, column=6)
    show_hide_key_combo(key_single_combo, output_single)
    output_single.trace_add("write", lambda *args, k=key_single_combo, o=output_single: show_hide_key_combo(k, o))

    bereich_split_frame = tk.Frame(content_frame)
    bereich_split_frame.grid(row=1, column=0, columnspan=4, sticky="w", padx=18, pady=(0,2))
    min1 = tk.StringVar(value="-512")
    max1 = tk.StringVar(value="0")
    tk.Label(bereich_split_frame, text="Min:").grid(row=0, column=0, sticky="w")
    tk.Entry(bereich_split_frame, width=6, textvariable=min1).grid(row=0, column=1)
    tk.Label(bereich_split_frame, text="Max:").grid(row=0, column=2, sticky="w")
    tk.Entry(bereich_split_frame, width=6, textvariable=max1).grid(row=0, column=3)
    tk.Label(bereich_split_frame, text="Output:").grid(row=0, column=4, sticky="w")
    output1 = tk.StringVar(value=action_id)
    output1_combo = ttk.Combobox(bereich_split_frame, textvariable=output1, values=output_choices, width=18, state="readonly")
    output1_combo.grid(row=0, column=5)
    key1 = tk.StringVar(value="W")
    key1_combo = ttk.Combobox(bereich_split_frame, textvariable=key1, values=KEYCODES, width=12, state="readonly")
    key1_combo.grid(row=0, column=6)
    show_hide_key_combo(key1_combo, output1)
    output1.trace_add("write", lambda *args, k=key1_combo, o=output1: show_hide_key_combo(k, o))

    min2 = tk.StringVar(value="1")
    max2 = tk.StringVar(value="511")
    tk.Label(bereich_split_frame, text="Min:").grid(row=1, column=0, sticky="w")
    tk.Entry(bereich_split_frame, width=6, textvariable=min2).grid(row=1, column=1)
    tk.Label(bereich_split_frame, text="Max:").grid(row=1, column=2, sticky="w")
    tk.Entry(bereich_split_frame, width=6, textvariable=max2).grid(row=1, column=3)
    tk.Label(bereich_split_frame, text="Output:").grid(row=1, column=4, sticky="w")
    output2 = tk.StringVar(value=action_id)
    output2_combo = ttk.Combobox(bereich_split_frame, textvariable=output2, values=output_choices, width=18, state="readonly")
    output2_combo.grid(row=1, column=5)
    key2 = tk.StringVar(value="S")
    key2_combo = ttk.Combobox(bereich_split_frame, textvariable=key2, values=KEYCODES, width=12, state="readonly")
    key2_combo.grid(row=1, column=6)
    show_hide_key_combo(key2_combo, output2)
    output2.trace_add("write", lambda *args, k=key2_combo, o=output2: show_hide_key_combo(k, o))

    axes_state.append({
        "idx": idx,
        "enabled": enabled_var,
        "split": split_var,
        "frame": frame,
        "content_frame": content_frame,
        "split_check": split_check,
        "bereich_single_frame": bereich_single_frame,
        "bereich_split_frame": bereich_split_frame,
        "min_single": min_single, "max_single": max_single, "output_single": output_single, "key_single": key_single,
        "key_single_widget": key_single_combo,
        "min1": min1, "max1": max1, "output1": output1, "key1": key1,
        "key1_widget": key1_combo,
        "min2": min2, "max2": max2, "output2": output2, "key2": key2,
        "key2_widget": key2_combo,
        "deadband": deadband_var,
        "axis_id": action_id
    })
    bereich_split_frame.grid_remove()

    def toggle_split_visibility(i=idx):
        if axes_state[i]["enabled"].get():
            axes_state[i]["split_check"].grid()
        else:
            axes_state[i]["split_check"].grid_remove()
    enabled_var.trace_add("write", lambda *args, i=idx: toggle_split_visibility(i))
    toggle_split_visibility(idx)
    toggle_axis_enabled(idx)
    toggle_axis_split(idx)

for i, (axis_name, action_id) in enumerate(MOVE_AXES):
    add_axis_ui(move_axes_frame, axis_name, action_id, i, row_index=i)
for i, (axis_name, action_id) in enumerate(ROT_AXES):
    add_axis_ui(rot_axes_frame, axis_name, action_id, i+len(MOVE_AXES), row_index=i)

def load_axes_from_xml(filename):
    # Reset GUI to defaults
    for vals in axes_state:
        idx = vals["idx"]
        vals["enabled"].set(False)
        vals["split"].set(False)
        toggle_axis_enabled(idx)
        toggle_axis_split(idx)
        vals["min_single"].set("-512")
        vals["max_single"].set("511")
        vals["output_single"].set(vals["axis_id"])
        vals["key_single"].set("W")
        vals["min1"].set("-512")
        vals["max1"].set("0")
        vals["output1"].set(vals["axis_id"])
        vals["key1"].set("W")
        vals["min2"].set("1")
        vals["max2"].set("511")
        vals["output2"].set(vals["axis_id"])
        vals["key2"].set("S")
        vals["deadband"].set("100")
    try:
        tree = ET.parse(filename)
        root_xml = tree.getroot()
        devices = root_xml.find("Devices")
        if devices is None:
            return
        # Sammle pro ActionID alle zugehörigen Axis-Daten
        parsed_axes = {}
        for device in devices.findall("Device"):
            axis_bank = device.find("AxisBank")
            if axis_bank is None:
                continue
            for axis in axis_bank.findall("Axis"):
                enabled = axis.findtext("Enabled", "false").lower() == "true"
                input_elem = axis.find("Input")
                output_elem = axis.find("Output")
                if input_elem is None or output_elem is None:
                    continue
                action_id = input_elem.findtext("ActionID", "")
                min_val = input_elem.findtext("Min", "-512")
                max_val = input_elem.findtext("Max", "511")
                deadband_val = axis.findtext("Deadband", "100")
                output_action_id = output_elem.findtext("ActionID", "")
                key_elem = output_elem.find("KeyStroke")
                key_val = ""
                if key_elem is not None:
                    key_val = key_elem.findtext("Key", "W")
                key_label = KEYCODE_TO_LABEL.get(key_val.upper(), key_val.upper())

                axis_info = {
                    "enabled": enabled,
                    "min": min_val,
                    "max": max_val,
                    "deadband": deadband_val,
                    "output_action_id": output_action_id,
                    "key_label": key_label
                }
                parsed_axes.setdefault(action_id, []).append(axis_info)
        # Trage ins UI ein
        for vals in axes_state:
            idx = vals["idx"]
            action_id = vals["axis_id"]
            axis_list = parsed_axes.get(action_id, [])
            if not axis_list:
                continue
            # Nur ein Bereich → kein Split
            if len(axis_list) == 1:
                info = axis_list[0]
                vals["enabled"].set(info["enabled"])
                toggle_axis_enabled(idx)
                vals["split"].set(False)
                toggle_axis_split(idx)
                vals["min_single"].set(info["min"])
                vals["max_single"].set(info["max"])
                vals["deadband"].set(info["deadband"])
                outid = info["output_action_id"]
                if outid == action_id:
                    vals["output_single"].set(outid)
                elif outid == "KB_Keystroke":
                    vals["output_single"].set("KB_Keystroke")
                    vals["key_single"].set(info["key_label"])
                elif outid == "HIDMouse_Wheel":
                    vals["output_single"].set("HIDMouse_Wheel")
                else:
                    vals["output_single"].set(outid)
            # Zwei Bereiche → Split
            elif len(axis_list) == 2:
                vals["enabled"].set(True)
                toggle_axis_enabled(idx)
                vals["split"].set(True)
                toggle_axis_split(idx)
                # Ordne Bereich1 = min<0, Bereich2 = min>=0
                infos = sorted(axis_list, key=lambda a: int(a["min"]))
                info1, info2 = infos
                vals["min1"].set(info1["min"])
                vals["max1"].set(info1["max"])
                vals["min2"].set(info2["min"])
                vals["max2"].set(info2["max"])
                vals["deadband"].set(info1["deadband"])
                outid1, outid2 = info1["output_action_id"], info2["output_action_id"]
                if outid1 == action_id:
                    vals["output1"].set(outid1)
                elif outid1 == "KB_Keystroke":
                    vals["output1"].set("KB_Keystroke")
                    vals["key1"].set(info1["key_label"])
                elif outid1 == "HIDMouse_Wheel":
                    vals["output1"].set("HIDMouse_Wheel")
                else:
                    vals["output1"].set(outid1)
                if outid2 == action_id:
                    vals["output2"].set(outid2)
                elif outid2 == "KB_Keystroke":
                    vals["output2"].set("KB_Keystroke")
                    vals["key2"].set(info2["key_label"])
                elif outid2 == "HIDMouse_Wheel":
                    vals["output2"].set("HIDMouse_Wheel")
                else:
                    vals["output2"].set(outid2)
    except Exception as e:
        messagebox.showerror("Fehler beim Laden der XML", f"Fehler: {e}")

root.after(100, ask_for_xml)
root.mainloop()
