# ui/app.py
import tkinter as tk
from tkinter import ttk, messagebox
import time
import math
from config import parse_args
from core.engine import PathfindingEngine
from core.maze import generate_maze
from core.obstacles import MovingObstacle
from core.database import MapDatabase
from model.grid_state import GridState
from utils.fov import calculate_fov
from utils.export import export_path_to_csv
from ui.theme import apply_theme
from ui.sidebar import Sidebar
from ui.canvas_view import CanvasView
from ui.dialogs import Dialogs
import json

class AStarApp:
    def __init__(self, root):
        self.root = root
        self.args = parse_args()
        self.state = GridState(rows=30, cols=55)
        self.db = MapDatabase()
        self.animating = False
        self.search_gen = None
        self.last_path = []
        self.last_g_values = {}
        self.obstacle_animation_id = None
        self.mode = "obstacle"
        self.algo = "A*"
        self.heuristic = "Octile"
        self.weight = 1.0
        self.allow_diagonal = not self.args.no_diagonal
        self.prevent_corner = not self.args.allow_corner_cut

        # Apply theme
        self.theme = apply_theme(root, None)
        
        # Create UI
        main_pane = ttk.PanedWindow(root, orient="horizontal")
        main_pane.pack(fill="both", expand=True)
        
        callbacks = {
            "set_mode": self.set_mode,
            "set_algo": self.set_algo,
            "set_heuristic": self.set_heuristic,
            "set_weight": self.set_weight,
            "set_diagonal": self.set_diagonal,
            "set_corner_cut": self.set_corner_cut,
            "toggle_fov": self.toggle_fov,
            "set_fov_radius": self.set_fov_radius,
            "resize_grid": self.resize_grid,
            "run_search": self.run_search,
            "pause_search": self.pause_search,
            "reset_search": self.reset_search,
            "generate_maze": self.generate_maze,
            "add_moving_obstacle": self.add_moving_obstacle,
            "set_influence_map": self.set_influence_map,
            "save_map": self.save_map,
            "load_map": self.load_map,
            "open_db": self.open_map_db,
            "on_grid_click": self.on_grid_click
        }
        self.sidebar = Sidebar(main_pane, callbacks)
        main_pane.add(self.sidebar.frame)
        self.canvas_view = CanvasView(main_pane, self.theme, callbacks)
        main_pane.add(self.canvas_view.frame, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
        
        # Initial state
        self.update_fov()
        self.redraw()
        self.bind_keys()

    def bind_keys(self):
        self.root.bind("<space>", lambda e: self.pause_search() if self.animating else self.run_search())
        self.root.bind("<r>", lambda e: self.reset_search())
        self.root.bind("<s>", lambda e: self.step_search())
        self.root.bind("<z>", lambda e: self.undo())
        self.root.bind("<y>", lambda e: self.redo())
        self.root.bind("<c>", lambda e: self.clear_obstacles())
        self.root.bind("<l>", lambda e: self.load_map())
        self.root.bind("<e>", lambda e: self.export_path())
        self.root.bind("<m>", lambda e: self.generate_maze())
        self.root.bind("<w>", lambda e: self.set_mode("waypoint"))
        self.root.bind("<f>", lambda e: self.toggle_fov())

    # State setters
    def set_mode(self, mode): self.mode = mode
    def set_algo(self, algo): self.algo = algo
    def set_heuristic(self, heur): self.heuristic = heur
    def set_weight(self, w): self.weight = w
    def set_diagonal(self, v): self.allow_diagonal = v
    def set_corner_cut(self, v): self.prevent_corner = v
    def set_fov_radius(self, r): self.state.fov_radius = r; self.update_fov()
    def toggle_fov(self): 
        self.state.fov_enabled = not self.state.fov_enabled
        self.update_fov()
        self.redraw()
    def update_fov(self):
        if self.state.fov_enabled:
            self.state.visible_cells = calculate_fov(self.state.grid, self.state.start, self.state.fov_radius)
        else:
            self.state.visible_cells = set()

    def resize_grid(self, new_rows, new_cols):
        old_start, old_goal = self.state.start, self.state.goal
        old_waypoints = self.state.waypoints[:]
        old_grid = [row[:] for row in self.state.grid]
        self.state.rows, self.state.cols = new_rows, new_cols
        self.state.grid = [[1.0 for _ in range(new_cols)] for _ in range(new_rows)]
        self.state.original_grid = [row[:] for row in self.state.grid]
        for r in range(min(len(old_grid), new_rows)):
            for c in range(min(len(old_grid[0]), new_cols)):
                self.state.grid[r][c] = old_grid[r][c]
                self.state.original_grid[r][c] = old_grid[r][c]
        self.state.start = (min(old_start[0], new_rows-1), min(old_start[1], new_cols-1))
        self.state.goal = (min(old_goal[0], new_rows-1), min(old_goal[1], new_cols-1))
        self.state.waypoints = [(min(r, new_rows-1), min(c, new_cols-1)) for (r,c) in old_waypoints]
        self.redraw()
        self.canvas_view.canvas.configure(scrollregion=(0, 0, new_cols * self.canvas_view.cell_size, new_rows * self.canvas_view.cell_size))

    def on_grid_click(self, r, c, is_right):
        if not (0 <= r < self.state.rows and 0 <= c < self.state.cols):
            return
        if self.mode == "obstacle":
            self.state.grid[r][c] = 0.0 if self.state.grid[r][c] > 0 else 1.0
            self.state.original_grid[r][c] = self.state.grid[r][c]
            self.state.save_undo()
            self.redraw()
        elif self.mode == "terrain" and is_right:
            current = self.state.grid[r][c]
            if current == 0:
                self.state.grid[r][c] = 1.0
            elif current <= 1.0:
                self.state.grid[r][c] = 2.0
            elif current <= 2.0:
                self.state.grid[r][c] = 3.0
            elif current <= 3.0:
                self.state.grid[r][c] = 5.0
            else:
                self.state.grid[r][c] = 1.0
            self.state.original_grid[r][c] = self.state.grid[r][c]
            self.state.save_undo()
            self.redraw()
        elif self.mode == "start":
            if self.state.grid[r][c] > 0:
                self.state.start = (r, c)
                self.update_fov()
                self.redraw()
        elif self.mode == "goal":
            if self.state.grid[r][c] > 0:
                self.state.goal = (r, c)
                self.redraw()
        elif self.mode == "waypoint":
            if self.state.grid[r][c] > 0:
                self.state.waypoints.append((r, c))
                self.redraw()

    def run_search(self):
        if self.animating: return
        points = [self.state.start] + self.state.waypoints + [self.state.goal]
        for pt in points:
            r, c = pt
            if not (0 <= r < self.state.rows and 0 <= c < self.state.cols and self.state.grid[r][c] > 0):
                messagebox.showerror("Error", f"Point {pt} is invalid or blocked!")
                return
        try:
            if self.state.waypoints:
                full_path = self.solve_with_waypoints()
                if not full_path:
                    messagebox.showerror("Error", "No path found through all waypoints!")
                    return
                self.last_path = full_path
                self.animate_waypoint_path()
            else:
                engine = PathfindingEngine(
                    self.state.grid,
                    algo=self.algo,
                    heuristic=self.heuristic,
                    weight=self.weight,
                    allow_diagonal=self.allow_diagonal,
                    prevent_corner_cutting=self.prevent_corner
                )
                self.search_gen = engine.search_generator(self.state.start, self.state.goal)
                self.animating = True
                self.search_start_time = time.time()
                self.canvas_view.canvas.delete("search")
                # Initialize incremental state
                self._prev_visited = set()
                self._prev_opened = set()
                self._prev_path = []
                self._prev_current = None
                self.update_stats("Searching...")
                self.animate_step()
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to initialize search:\n{e}")
            self.animating = False
            self.search_gen = None

    def solve_with_waypoints(self):
        sequence = [self.state.start] + self.state.waypoints + [self.state.goal]
        full_path = []
        for i in range(len(sequence) - 1):
            path = self.find_path(sequence[i], sequence[i+1])
            if not path: return []
            full_path.extend(path[:-1] if full_path else path)
        return full_path

    def find_path(self, start, goal):
        try:
            engine = PathfindingEngine(
                self.state.grid,
                algo=self.algo,
                heuristic=self.heuristic,
                weight=self.weight,
                allow_diagonal=self.allow_diagonal,
                prevent_corner_cutting=self.prevent_corner
            )
            for state in engine.search_generator(start, goal):
                if state.get("path"):
                    return state["path"]
        except:
            return []
        return []

    def animate_step(self):
        if not self.animating or self.search_gen is None: return
        try:
            state = next(self.search_gen)
            self.update_from_state(state)
            self.root.after(20, self.animate_step)  # Faster loop for smoother performance
        except StopIteration:
            self.animating = False
        except Exception as e:
            self.animating = False
            messagebox.showerror("Search Error", f"Search failed:\n{e}")

    def animate_waypoint_path(self):
        self.animating = True
        self.canvas_view.canvas.delete("search")
        path = self.last_path
        step = 0
        def animate():
            nonlocal step
            if step >= len(path) or not self.animating:
                self.animating = False
                return
            r, c = path[step]
            self.canvas_view.draw_overlay(r, c, "#0e3cd4", shape="circle", tag="path")
            if step > 0:
                pr, pc = path[step-1]
                self.canvas_view.canvas.create_line(
                    pc * self.canvas_view.cell_size + self.canvas_view.cell_size//2,
                    pr * self.canvas_view.cell_size + self.canvas_view.cell_size//2,
                    c * self.canvas_view.cell_size + self.canvas_view.cell_size//2,
                    r * self.canvas_view.cell_size + self.canvas_view.cell_size//2,
                    fill="#192BC7", width=3, tags="path"
                )
            step += 1
            self.root.after(30, animate)
        animate()
        path_cost = 0.0
        for a, b in zip(path[:-1], path[1:]):
            dr = abs(a[0]-b[0]); dc = abs(a[1]-b[1])
            mult = math.sqrt(2) if (dr == 1 and dc == 1) else 1.0
            path_cost += mult * self.state.grid[b[0]][b[1]]
        self.update_stats("Path Found!", len(path), 0, len(path), path_cost, 0)

    def redraw(self):
        # Only draw base grid + static elements (no search state)
        self.canvas_view.draw_grid(
            self.state,
            [],  # visited
            set(),  # opened
            None,  # current
            [],  # path
            {}  # g_values
        )

    def update_from_state(self, state):
        if not isinstance(state, dict):
            return

        visited = state.get("visited") or []
        opened = state.get("opened") or set()
        path = state.get("path") or []
        current = state.get("current")
        done = state.get("done", False)

        # Store for export
        if path:
            self.last_path = path

        # Convert to sets for efficient diff
        visited_set = set(visited)
        opened_set = set(opened)

        # Get previous state (for incremental updates)
        prev_visited = getattr(self, '_prev_visited', set())
        prev_opened = getattr(self, '_prev_opened', set())
        prev_path = getattr(self, '_prev_path', [])
        prev_current = getattr(self, '_prev_current', None)

        # 1. Add newly visited nodes
        new_visited = visited_set - prev_visited
        for (r, c) in new_visited:
            if not self.state.fov_enabled or (r, c) in self.state.visible_cells:
                self.canvas_view.draw_overlay(r, c, "#2c3e50" if self.theme["is_dark"] else "#b0c4de", tag="visited")

        # 2. Add newly opened nodes (not visited)
        new_opened = (opened_set - visited_set) - prev_opened
        for (r, c) in new_opened:
            if not self.state.fov_enabled or (r, c) in self.state.visible_cells:
                self.canvas_view.draw_overlay(r, c, "#f1c40f", tag="opened")

        # 3. Update current node
        if current != prev_current:
            if prev_current:
                self.canvas_view.canvas.delete(f"current_{prev_current[0]}_{prev_current[1]}")
            if current and (not self.state.fov_enabled or current in self.state.visible_cells):
                self.canvas_view.draw_overlay(
                    current[0], current[1], "#e74c3c", shape="diamond", 
                    tag=f"current_{current[0]}_{current[1]}"
                )

        # 4. Update path (only if changed)
        if path != prev_path:
            self.canvas_view.canvas.delete("path")
            if path:
                for i, (r, c) in enumerate(path):
                    if not self.state.fov_enabled or (r, c) in self.state.visible_cells:
                        self.canvas_view.draw_overlay(r, c, "#2ecc71", shape="circle", tag="path")
                        if i > 0:
                            pr, pc = path[i-1]
                            if (not self.state.fov_enabled or (pr, pc) in self.state.visible_cells) and (not self.state.fov_enabled or (r, c) in self.state.visible_cells):
                                self.canvas_view.canvas.create_line(
                                    pc * self.canvas_view.cell_size + self.canvas_view.cell_size//2,
                                    pr * self.canvas_view.cell_size + self.canvas_view.cell_size//2,
                                    c * self.canvas_view.cell_size + self.canvas_view.cell_size//2,
                                    r * self.canvas_view.cell_size + self.canvas_view.cell_size//2,
                                    fill="#27ae60", width=3, tags="path"
                                )

        # Save current state for next update
        self._prev_visited = visited_set
        self._prev_opened = opened_set
        self._prev_path = path[:]
        self._prev_current = current

        # Update stats
        path_cost = 0.0
        if path:
            for a, b in zip(path[:-1], path[1:]):
                dr = abs(a[0]-b[0]); dc = abs(a[1]-b[1])
                mult = math.sqrt(2) if (dr == 1 and dc == 1) else 1.0
                path_cost += mult * self.state.grid[b[0]][b[1]]
        
        elapsed = time.time() - self.search_start_time if self.search_start_time else 0.001
        nodes_per_sec = len(visited) / elapsed if elapsed > 0 else 0
        status = "Path Found!" if done and path else "Searching..." if not done else "No Path"
        
        self.update_stats(status, len(visited), len(opened), len(path), path_cost, nodes_per_sec)

    def update_stats(self, status, visited=0, opened=0, path_len=0, total_cost=0.0, nodes_per_sec=0.0):
        text = f"Status: {status}\n"
        text += f"Visited: {visited}\n"
        text += f"Opened: {opened}\n"
        text += f"Path Nodes: {path_len}\n"
        text += f"Path Cost: {total_cost:.3f}\n"
        text += f"Speed: {nodes_per_sec:.1f} nodes/sec\n"
        self.sidebar.stats_text.config(state="normal")
        self.sidebar.stats_text.delete(1.0, "end")
        self.sidebar.stats_text.insert("end", text)
        self.sidebar.stats_text.config(state="disabled")

    def step_search(self):
        if self.animating: return
        if self.search_gen is None:
            self.run_search()
            return
        try:
            state = next(self.search_gen)
            self.update_from_state(state)
        except StopIteration:
            self.animating = False
        except Exception as e:
            self.animating = False
            messagebox.showerror("Step Error", str(e))

    def pause_search(self):
        self.animating = False

    def reset_search(self):
        self.animating = False
        self.search_gen = None
        # Clear incremental state
        if hasattr(self, '_prev_visited'):
            delattr(self, '_prev_visited')
            delattr(self, '_prev_opened')
            delattr(self, '_prev_path')
            delattr(self, '_prev_current')
        # Clear only search-related overlays
        self.canvas_view.canvas.delete("visited", "opened", "current_*", "path")
        self.update_stats("Ready")

    def undo(self):
        if self.state.undo_stack:
            self.state.redo_stack.append((
                [row[:] for row in self.state.grid],
                self.state.start,
                self.state.goal,
                self.state.waypoints[:]
            ))
            self.state.restore_from_undo(self.state.undo_stack.pop())
            self.redraw()

    def redo(self):
        if self.state.redo_stack:
            self.state.undo_stack.append((
                [row[:] for row in self.state.grid],
                self.state.start,
                self.state.goal,
                self.state.waypoints[:]
            ))
            self.state.restore_from_undo(self.state.redo_stack.pop())
            self.redraw()

    def clear_obstacles(self):
        self.state.save_undo()
        for r in range(self.state.rows):
            for c in range(self.state.cols):
                if self.state.grid[r][c] == 0 and (r, c) not in self.state.waypoints and (r, c) != self.state.start and (r, c) != self.state.goal:
                    self.state.grid[r][c] = 1.0
                    self.state.original_grid[r][c] = 1.0
        self.redraw()

    def clear_all(self):
        self.state.save_undo()
        self.state.grid = [[1.0 for _ in range(self.state.cols)] for _ in range(self.state.rows)]
        self.state.original_grid = [row[:] for row in self.state.grid]
        self.state.waypoints = []
        self.redraw()

    def new_map(self):
        self.state.grid = [[1.0 for _ in range(self.state.cols)] for _ in range(self.state.rows)]
        self.state.original_grid = [row[:] for row in self.state.grid]
        self.state.waypoints = []
        self.state.influence_map = None
        self.state.moving_obstacles = []
        if self.obstacle_animation_id:
            self.root.after_cancel(self.obstacle_animation_id)
            self.obstacle_animation_id = None
        self.redraw()

    def add_moving_obstacle(self):
        center_r, center_c = self.state.rows // 2, self.state.cols // 2
        positions = [
            [(center_r-1, center_c), (center_r, center_c), (center_r+1, center_c)],
            [(center_r, center_c-1), (center_r, center_c), (center_r, center_c+1)]
        ]
        self.state.moving_obstacles.append(MovingObstacle(positions, period=30, cost=0.0))
        self.animate_obstacles()

    def animate_obstacles(self):
        if not self.state.moving_obstacles:
            return
        for r in range(self.state.rows):
            for c in range(self.state.cols):
                if (r, c) != self.state.start and (r, c) != self.state.goal and (r, c) not in self.state.waypoints:
                    self.state.grid[r][c] = self.state.original_grid[r][c]
        for obs in self.state.moving_obstacles:
            obs.update()
            for (r, c) in obs.get_current_cells():
                if 0 <= r < self.state.rows and 0 <= c < self.state.cols:
                    self.state.grid[r][c] = obs.cost
        self.redraw()
        if self.obstacle_animation_id:
            self.root.after_cancel(self.obstacle_animation_id)
        self.obstacle_animation_id = self.root.after(200, self.animate_obstacles)

    def set_influence_map(self):
        center_r, center_c = self.state.rows // 2, self.state.cols // 2
        self.state.influence_map = [[0.0 for _ in range(self.state.cols)] for _ in range(self.state.rows)]
        for r in range(self.state.rows):
            for c in range(self.state.cols):
                dist = math.hypot(r - center_r, c - center_c)
                if dist < 8:
                    self.state.influence_map[r][c] = max(0.0, 1.0 - dist / 8.0) * 3.0
        self.redraw()

    def generate_maze(self):
        self.state.save_undo()
        raw_maze = generate_maze(self.state.rows, self.state.cols, start=self.state.start)
        for r in range(min(self.state.rows, len(raw_maze))):
            for c in range(min(self.state.cols, len(raw_maze[0]))):
                self.state.grid[r][c] = 1.0 if raw_maze[r][c] == 1 else 0.0
                self.state.original_grid[r][c] = self.state.grid[r][c]
        self.redraw()

    def open_map_db(self):
        Dialogs.open_map_db(self.root, {"load_map_data": self.load_map_data})

    def load_map_data(self, map_data):
        self.state.rows, self.state.cols = map_data["rows"], map_data["cols"]
        self.state.grid = map_data["grid"]
        self.state.original_grid = [row[:] for row in self.state.grid]
        self.state.start = map_data["start"]
        self.state.goal = map_data["goal"]
        self.state.waypoints = map_data.get("waypoints", [])
        self.state.influence_map = None
        self.state.moving_obstacles = []
        if self.obstacle_animation_id:
            self.root.after_cancel(self.obstacle_animation_id)
            self.obstacle_animation_id = None
        self.redraw()
        self.canvas_view.canvas.configure(scrollregion=(0, 0, self.state.cols * self.canvas_view.cell_size, self.state.rows * self.canvas_view.cell_size))

    def save_map(self):
        name, tags, rating = Dialogs.save_map_dialog()
        if name:
            self.db.save_map(name, self.state.rows, self.state.cols, self.state.grid, self.state.start, self.state.goal, self.state.waypoints, tags, rating)
            messagebox.showinfo("Saved", f"Map '{name}' saved to database!")

    def load_map(self):
        path = tk.filedialog.askopenfilename(filetypes=[("JSON Map", "*.json")])
        if not path: return
        try:
            with open(path) as f:
                data = json.load(f)
            self.state.rows, self.state.cols = data["rows"], data["cols"]
            self.state.grid = data["grid"]
            self.state.original_grid = [row[:] for row in self.state.grid]
            self.state.start = tuple(data["start"])
            self.state.goal = tuple(data["goal"])
            self.state.waypoints = data.get("waypoints", [])
            self.redraw()
            self.canvas_view.canvas.configure(scrollregion=(0, 0, self.state.cols * self.canvas_view.cell_size, self.state.rows * self.canvas_view.cell_size))
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def export_path(self):
        path = self.last_path
        if not path:
            messagebox.showwarning("Warning", "No path to export.")
            return
        filepath = export_path_to_csv(path)
        if filepath:
            messagebox.showinfo("Exported", f"Path saved to {filepath}")

    def on_closing(self):
        if self.obstacle_animation_id:
            self.root.after_cancel(self.obstacle_animation_id)
        self.root.destroy()