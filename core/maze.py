# core/maze.py
import random

def generate_maze(rows, cols, start=(0, 0)):
    # Ensure odd dimensions for recursive backtracker
    if rows % 2 == 0:
        rows -= 1
    if cols % 2 == 0:
        cols -= 1
    
    # Clamp start position to valid bounds
    start_r = max(0, min(start[0], rows - 1))
    start_c = max(0, min(start[1], cols - 1))
    start = (start_r, start_c)
    
    # Initialize grid and visited
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    
    # Start maze generation
    stack = [start]
    visited[start[0]][start[1]] = True
    directions = [(0,2), (2,0), (0,-2), (-2,0)]
    
    while stack:
        r, c = stack[-1]
        neighbors = []
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                neighbors.append((nr, nc, dr//2, dc//2))
        if neighbors:
            nr, nc, hr, hc = random.choice(neighbors)
            visited[nr][nc] = True
            grid[r + hr][c + hc] = 1
            grid[nr][nc] = 1
            stack.append((nr, nc))
        else:
            stack.pop()
    
    return grid