# config.py
import argparse
import math

# Heuristic functions
def manhattan(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
def euclidean(a, b): return math.hypot(a[0]-b[0], a[1]-b[1])
def octile(a, b):
    dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
    return (math.sqrt(2)-1) * min(dx, dy) + max(dx, dy)
def chebyshev(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

# Heuristic names for UI
HEURISTICS = ["Manhattan", "Euclidean", "Octile", "Chebyshev"]

# Heuristic function map (for runtime use)
HEURISTIC_FUNCS = {
    "Manhattan": manhattan,
    "Euclidean": euclidean,
    "Octile": octile,
    "Chebyshev": chebyshev
}

ALGORITHMS = ["A*", "Dijkstra", "Greedy Best-First"]

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--heuristic", default="Octile", choices=HEURISTICS)
    p.add_argument("--weight", type=float, default=1.0)
    p.add_argument("--no-diagonal", action="store_true")
    p.add_argument("--allow-corner-cut", action="store_true")
    p.add_argument("--interval", type=int, default=50)
    return p.parse_args()