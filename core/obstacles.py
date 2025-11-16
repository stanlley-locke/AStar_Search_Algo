# core/obstacles.py
class MovingObstacle:
    def __init__(self, positions, period=50, cost=0.0):
        self.positions = positions
        self.period = period
        self.cost = cost
        self.phase = 0

    def get_current_cells(self):
        idx = self.phase % len(self.positions)
        pos = self.positions[idx]
        return pos if isinstance(pos, list) else [pos]

    def update(self):
        self.phase += 1