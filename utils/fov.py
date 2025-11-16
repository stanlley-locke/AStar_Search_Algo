# utils/fov.py
def calculate_fov(grid, center, radius):
    visible = set()
    r0, c0 = center
    for r in range(max(0, r0 - radius), min(len(grid), r0 + radius + 1)):
        for c in range(max(0, c0 - radius), min(len(grid[0]), c0 + radius + 1)):
            if abs(r - r0) + abs(c - c0) <= radius:
                visible.add((r, c))
    return visible