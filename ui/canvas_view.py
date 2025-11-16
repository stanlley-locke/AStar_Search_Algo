# ui/canvas_view.py
import tkinter as tk
from tkinter import ttk
from config import HEURISTIC_FUNCS

class CanvasView:
    def __init__(self, parent, theme, callbacks):
        self.parent = parent
        self.theme = theme
        self.callbacks = callbacks
        self.cell_size = 28
        self.create_widgets()

    def create_widgets(self):
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.frame, bg=self.theme["bg"], highlightthickness=0)
        self.scroll_x = ttk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.scroll_y = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Button-3>", lambda e: self.on_click(e, is_right=True))

    def on_click(self, event, is_right=False):
        canvasx = self.canvas.canvasx(event.x)
        canvasy = self.canvas.canvasy(event.y)
        c = int(canvasx // self.cell_size)
        r = int(canvasy // self.cell_size)
        self.callbacks["on_grid_click"](r, c, is_right)

    def on_drag(self, event):
        self.on_click(event, is_right=False)

    def draw_grid(self, state, visited, opened, current, path, last_g_values):
        self.canvas.delete("all")
        rows, cols = state.rows, state.cols
        self.canvas.configure(scrollregion=(0, 0, cols * self.cell_size, rows * self.cell_size))
        
        # Precompute heuristic if needed (for future heatmap)
        heuristic_cache = {}
        if state.goal:
            heuristic_func = HEURISTIC_FUNCS.get("Octile", lambda a,b: 0)
            for r in range(rows):
                for c in range(cols):
                    heuristic_cache[(r, c)] = heuristic_func((r, c), state.goal)

        for r in range(rows):
            for c in range(cols):
                if state.fov_enabled and (r, c) not in state.visible_cells:
                    color = "#1C1C1E"
                else:
                    cost = state.grid[r][c]
                    if cost == 0:
                        color = "#3A3A3C"
                    else:
                        base_cost = cost
                        if state.influence_map:
                            base_cost += state.influence_map[r][c]
                        t = min(1.0, (base_cost - 1.0) / 4.0)
                        r_val = int(50 + t * 180)
                        g_val = int(200 - t * 150)
                        b_val = 50
                        color = f"#{r_val:02x}{g_val:02x}{b_val:02x}"
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#444444")

        self.draw_point(state.start, "#30D158", "S")
        for i, wp in enumerate(state.waypoints):
            self.draw_point(wp, "#FF9F0A", str(i+1))
        self.draw_point(state.goal, "#0A84FF", "G")

        for (r, c) in visited:
            if not state.fov_enabled or (r, c) in state.visible_cells:
                self.draw_overlay(r, c, "#2c3e50")
        for (r, c) in opened:
            if (r, c) not in visited and (not state.fov_enabled or (r, c) in state.visible_cells):
                self.draw_overlay(r, c, "#f1c40f")
        if current and (not state.fov_enabled or current in state.visible_cells):
            self.draw_overlay(current[0], current[1], "#e74c3c", shape="diamond")
        if path:
            for i, (r, c) in enumerate(path):
                if not state.fov_enabled or (r, c) in state.visible_cells:
                    self.draw_overlay(r, c, "#2ecc71", shape="circle")
                    if i > 0:
                        pr, pc = path[i-1]
                        if (not state.fov_enabled or (pr, pc) in state.visible_cells) and (not state.fov_enabled or (r, c) in state.visible_cells):
                            self.canvas.create_line(
                                pc * self.cell_size + self.cell_size//2,
                                pr * self.cell_size + self.cell_size//2,
                                c * self.cell_size + self.cell_size//2,
                                r * self.cell_size + self.cell_size//2,
                                fill="#27ae60", width=3
                            )

    def draw_point(self, pos, color, label):
        r, c = pos
        x1 = c * self.cell_size + 4
        y1 = r * self.cell_size + 4
        x2 = x1 + self.cell_size - 8
        y2 = y1 + self.cell_size - 8
        self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="white", width=2)
        font = ("SF Pro", 10, "bold" if label in "SG" else "normal")
        self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text=label, fill="white", font=font)

    def draw_overlay(self, r, c, color, shape="square", tag="path"):
        x1 = c * self.cell_size
        y1 = r * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        if shape == "square":
            self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill=color, stipple="gray50")
        elif shape == "diamond":
            cx, cy = (x1+x2)//2, (y1+y2)//2
            self.canvas.create_polygon(cx, y1+6, x2-6, cy, cx, y2-6, x1+6, cy, fill=color, outline="white", width=1)
        elif shape == "circle":
            self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill=color, outline="white", width=1)