# core/engine.py
import math
import heapq
from config import HEURISTICS

def manhattan(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
def euclidean(a, b): return math.hypot(a[0]-b[0], a[1]-b[1])
def octile(a, b):
    dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
    return (math.sqrt(2)-1) * min(dx, dy) + max(dx, dy)
def chebyshev(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

HEURISTIC_FUNCS = {
    "Manhattan": manhattan,
    "Euclidean": euclidean,
    "Octile": octile,
    "Chebyshev": chebyshev
}

class PathfindingEngine:
    def __init__(self, grid, algo="A*", heuristic="Octile", weight=1.0, allow_diagonal=True, prevent_corner_cutting=True):
        self.grid = grid
        self.algo = algo
        self.heuristic = HEURISTIC_FUNCS.get(heuristic, octile)
        self.weight = weight
        self.allow_diagonal = allow_diagonal
        self.prevent_corner_cutting = prevent_corner_cutting
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows else 0
        self.orth_cost = 1.0
        self.diag_cost = math.sqrt(2.0)

    def in_bounds(self, r, c): 
        return 0 <= r < self.rows and 0 <= c < self.cols
    def traversable(self, r, c): 
        return self.in_bounds(r, c) and self.grid[r][c] > 0

    def neighbors(self, r, c):
        orth = [(0,1), (0,-1), (1,0), (-1,0)]
        for dr, dc in orth:
            nr, nc = r + dr, c + dc
            if self.traversable(nr, nc):
                yield nr, nc, self.orth_cost * self.grid[nr][nc]
        if self.allow_diagonal:
            diag = [(1,1), (1,-1), (-1,1), (-1,-1)]
            for dr, dc in diag:
                nr, nc = r + dr, c + dc
                if not self.traversable(nr, nc): continue
                if self.prevent_corner_cutting:
                    if not (self.traversable(r+dr, c) and self.traversable(r, c+dc)): continue
                yield nr, nc, self.diag_cost * self.grid[nr][nc]

    def reconstruct_path(self, cells, dest):
        path = []
        r, c = dest
        if cells[r][c].get('parent', (-1,-1)) == (-1, -1): return path
        while cells[r][c]['parent'] != (r, c):
            path.append((r, c))
            r, c = cells[r][c]['parent']
        path.append((r, c))
        return path

    def search_generator(self, start, goal):
        if not (self.traversable(*start) and self.traversable(*goal)):
            raise ValueError("Start or goal is blocked or out of bounds")
        if start == goal:
            yield {'current': start, 'opened': set(), 'visited': [start], 'path': [start], 'done': True}
            return

        cells = [[{'parent': (-1,-1), 'f': float('inf'), 'g': float('inf'), 'h': 0.0} 
                  for _ in range(self.cols)] for _ in range(self.rows)]
        closed = [[False] * self.cols for _ in range(self.rows)]
        sr, sc = start
        gr, gc = goal

        cells[sr][sc]['g'] = 0.0
        cells[sr][sc]['h'] = self.heuristic((sr, sc), (gr, gc))
        if self.algo == "Dijkstra":
            cells[sr][sc]['f'] = cells[sr][sc]['g']
        elif self.algo == "Greedy Best-First":
            cells[sr][sc]['f'] = self.weight * cells[sr][sc]['h']
        else:
            cells[sr][sc]['f'] = cells[sr][sc]['g'] + self.weight * cells[sr][sc]['h']
        cells[sr][sc]['parent'] = (sr, sc)

        open_heap = []
        heapq.heappush(open_heap, (cells[sr][sc]['f'], 0, (sr, sc)))
        counter = 1
        opened = set()
        visited = []

        yield {'current': None, 'opened': set(opened), 'visited': list(visited), 'path': None, 'done': False}

        while open_heap:
            fval, _, (r, c) = heapq.heappop(open_heap)
            if closed[r][c]: continue
            if fval > cells[r][c]['f']: continue

            closed[r][c] = True
            visited.append((r, c))
            yield {'current': (r, c), 'opened': set(opened), 'visited': list(visited), 'path': None, 'done': False}

            for nr, nc, step in self.neighbors(r, c):
                if closed[nr][nc]: continue
                tentative_g = cells[r][c]['g'] + step
                if tentative_g < cells[nr][nc]['g']:
                    cells[nr][nc]['g'] = tentative_g
                    cells[nr][nc]['h'] = self.heuristic((nr, nc), (gr, gc))
                    if self.algo == "Dijkstra":
                        cells[nr][nc]['f'] = tentative_g
                    elif self.algo == "Greedy Best-First":
                        cells[nr][nc]['f'] = self.weight * cells[nr][nc]['h']
                    else:
                        cells[nr][nc]['f'] = tentative_g + self.weight * cells[nr][nc]['h']
                    cells[nr][nc]['parent'] = (r, c)
                    heapq.heappush(open_heap, (cells[nr][nc]['f'], counter, (nr, nc)))
                    counter += 1
                    opened.add((nr, nc))
                    yield {'current': (r, c), 'opened': set(opened), 'visited': list(visited), 'path': None, 'done': False}
                if (nr, nc) == (gr, gc):
                    path = self.reconstruct_path(cells, (gr, gc))
                    for _ in range(50):
                        yield {'current': (nr, nc), 'opened': set(opened), 'visited': list(visited), 'path': path, 'done': True}
                    return

        for _ in range(30):
            yield {'current': None, 'opened': set(opened), 'visited': list(visited), 'path': None, 'done': True}