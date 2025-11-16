# ui/sidebar.py
import tkinter as tk
from tkinter import ttk
from config import ALGORITHMS, HEURISTICS

class Sidebar:
    def __init__(self, parent, callbacks):
        self.frame = ttk.Frame(parent, width=280)
        self.callbacks = callbacks
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.frame, text="Mode", font=("SF Pro", 12, "bold")).pack(pady=(10,5), anchor="w", padx=20)
        self.mode_var = tk.StringVar(value="obstacle")
        modes = [("Obstacle (L-click)", "obstacle"), ("Terrain Cost (R-click)", "terrain"),
                 ("Place Start", "start"), ("Place Goal", "goal"), ("Place Waypoint", "waypoint")]
        for text, val in modes:
            ttk.Radiobutton(self.frame, text=text, variable=self.mode_var, value=val,
                            command=lambda v=val: self.callbacks["set_mode"](v)).pack(anchor="w", padx=20, pady=2)

        ttk.Label(self.frame, text="Algorithm", font=("SF Pro", 12, "bold")).pack(pady=(15,5), anchor="w", padx=20)
        self.algo_var = tk.StringVar(value="A*")
        algo_combo = ttk.Combobox(self.frame, textvariable=self.algo_var, values=ALGORITHMS, state="readonly")
        algo_combo.pack(fill="x", padx=20, pady=2)
        algo_combo.bind("<<ComboboxSelected>>", lambda e: self.callbacks["set_algo"](self.algo_var.get()))

        ttk.Label(self.frame, text="Heuristic", font=("SF Pro", 12, "bold")).pack(pady=(10,5), anchor="w", padx=20)
        self.heur_var = tk.StringVar(value="Octile")
        heur_combo = ttk.Combobox(self.frame, textvariable=self.heur_var, values=HEURISTICS, state="readonly")
        heur_combo.pack(fill="x", padx=20, pady=2)
        heur_combo.bind("<<ComboboxSelected>>", lambda e: self.callbacks["set_heuristic"](self.heur_var.get()))

        weight_frame = ttk.Frame(self.frame)
        weight_frame.pack(fill="x", padx=20, pady=2)
        ttk.Label(weight_frame, text="Weight:").pack(side="left")
        self.weight_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(weight_frame, from_=0.1, to=5.0, increment=0.1, textvariable=self.weight_var, width=6).pack(side="right")
        self.weight_var.trace("w", lambda *a: self.callbacks["set_weight"](self.weight_var.get()))

        self.diag_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.frame, text="Allow Diagonal Moves", variable=self.diag_var,
                        command=lambda: self.callbacks["set_diagonal"](self.diag_var.get())).pack(anchor="w", padx=20, pady=2)
        self.corner_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.frame, text="Prevent Corner Cutting", variable=self.corner_var,
                        command=lambda: self.callbacks["set_corner_cut"](self.corner_var.get())).pack(anchor="w", padx=20, pady=2)

        fov_frame = ttk.Frame(self.frame)
        fov_frame.pack(fill="x", padx=20, pady=2)
        self.fov_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(fov_frame, text="Field of View", variable=self.fov_var,
                        command=lambda: self.callbacks["toggle_fov"]()).pack(side="left")
        self.fov_radius_var = tk.IntVar(value=5)
        ttk.Spinbox(fov_frame, from_=1, to=20, textvariable=self.fov_radius_var, width=5).pack(side="right")
        self.fov_radius_var.trace("w", lambda *a: self.callbacks["set_fov_radius"](self.fov_radius_var.get()))

        ttk.Label(self.frame, text="Grid Size", font=("SF Pro", 12, "bold")).pack(pady=(15,5), anchor="w", padx=20)
        size_frame = ttk.Frame(self.frame)
        size_frame.pack(fill="x", padx=20)
        self.rows_var = tk.IntVar(value=33)
        self.cols_var = tk.IntVar(value=52)
        ttk.Spinbox(size_frame, from_=5, to=100, textvariable=self.rows_var, width=5).pack(side="left")
        ttk.Spinbox(size_frame, from_=5, to=100, textvariable=self.cols_var, width=5).pack(side="left", padx=5)
        ttk.Button(self.frame, text="Resize Grid", command=lambda: self.callbacks["resize_grid"](self.rows_var.get(), self.cols_var.get())).pack(fill="x", padx=20, pady=5)

        actions = [
            ("▶️ Run Search", self.callbacks["run_search"]),
            ("⏸️ Pause", self.callbacks["pause_search"]),
            ("↺ Reset", self.callbacks["reset_search"]),
            ("🧩 Generate Maze", self.callbacks["generate_maze"]),
            ("➕ Add Moving Obstacle", self.callbacks["add_moving_obstacle"]),
            ("🌡️ Set Influence Map", self.callbacks["set_influence_map"]),
            ("💾 Save Map", self.callbacks["save_map"]),
            ("📂 Load Map", self.callbacks["load_map"]),
            ("🗃️ Map Database", self.callbacks["open_db"]),
        ]
        for text, cmd in actions:
            style = "Accent.TButton" if "Run" in text else "TButton"
            ttk.Button(self.frame, text=text, style=style, command=cmd).pack(fill="x", padx=20, pady=2)

        ttk.Label(self.frame, text="Live Statistics", font=("SF Pro", 12, "bold")).pack(pady=(15,5), anchor="w", padx=20)
        self.stats_text = tk.Text(self.frame, height=10, font=("Consolas", 9))
        self.stats_text.pack(fill="both", expand=True, pady=5)
        self.stats_text.config(state="disabled")

        self.frame.pack_propagate(False)