# ui/dialogs.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
from core.database import MapDatabase

class Dialogs:
    @staticmethod
    def open_map_db(root, callbacks):
        db = MapDatabase()
        db_window = tk.Toplevel(root)
        db_window.title("Map Database")
        db_window.geometry("600x400")
        listbox = tk.Listbox(db_window, width=80, height=20)
        listbox.pack(pady=10, padx=10)
        maps = db.load_maps()
        for map_id, name, tags, rating in maps:
            tag_list = json.loads(tags)
            listbox.insert(tk.END, f"[{rating}★] {name} - Tags: {', '.join(tag_list) if tag_list else 'none'}")
        def load_selected():
            selection = listbox.curselection()
            if selection:
                map_id = maps[selection[0]][0]
                map_data = db.get_map_by_id(map_id)
                if map_data:
                    callbacks["load_map_data"](map_data)
                    db_window.destroy()
        ttk.Button(db_window, text="Load Selected", command=load_selected).pack(pady=5)
        ttk.Button(db_window, text="Close", command=db_window.destroy).pack(pady=5)

    @staticmethod
    def save_map_dialog():
        name = simpledialog.askstring("Save Map", "Map name:")
        if not name: return None, None, None
        tags = simpledialog.askstring("Save Map", "Tags (comma-separated):", initialvalue="")
        rating = simpledialog.askinteger("Save Map", "Rating (0-5):", minvalue=0, maxvalue=5, initialvalue=3)
        return name, tags or "", rating or 0