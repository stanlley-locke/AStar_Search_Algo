# model/grid_state.py
from collections import deque
from typing import Deque, List, Tuple

class GridState:
    def __init__(self, rows=32, cols=52):
        self.rows = rows
        self.cols = cols
        self.grid = [[1.0 for _ in range(cols)] for _ in range(rows)]
        self.original_grid = [row[:] for row in self.grid]
        self.start = (rows - 1, 0)
        self.goal = (0, cols - 1)
        self.waypoints: List[Tuple[int, int]] = []
        self.influence_map = None
        self.fov_enabled = False
        self.fov_radius = 5
        self.visible_cells = set()
        self.moving_obstacles = []
        self.undo_stack: Deque = deque(maxlen=50)
        self.redo_stack: Deque = deque(maxlen=50)

    def save_undo(self):
        self.undo_stack.append((
            [row[:] for row in self.grid],
            self.start,
            self.goal,
            self.waypoints[:]
        ))
        self.redo_stack.clear()

    def restore_from_undo(self, state):
        self.grid, self.start, self.goal, self.waypoints = state
        self.original_grid = [row[:] for row in self.grid]