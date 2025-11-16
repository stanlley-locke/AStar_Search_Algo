# 🧭 A* Pathfinding Studio — Apple-Inspired Pathfinding Environment

![A* Pathfinding Studio](https://via.placeholder.com/800x400/1C1C1E/FFFFFF?text=A*+Pathfinding+Studio)  
*Advanced pathfinding visualization with moving obstacles, FOV, waypoints, and more.*

---

## 🚀 Features

- **Multi-Algorithm Support**: A*, Dijkstra, Greedy Best-First
- **Dynamic Environments**: 
  - 🌀 Moving obstacles (rotating walls, flowing rivers)
  - 🌡️ Influence maps / heatmaps
  - 👁️ Field of View (FOV) & Fog of War
- **Advanced Pathing**:
  - 📍 Multi-waypoint path sequencing
  - 🧩 Auto maze generation (recursive backtracker)
- **Persistence**:
  - 💾 Save/load maps as JSON
  - 🗃️ SQLite map database with tags & ratings
- **Professional UI**:
  - 🌓 Dark/Light theme (Apple-inspired)
  - 🖱️ Drag-to-draw obstacles & terrain
  - 📊 Real-time performance stats (nodes/sec, path cost)
- **Hotkeys**: SPACE, R, S, Z, Y, C, L, E, M, W, F

---

## 📥 Installation

### Option 1: Run from Source (Requires Python)

1. **Install Python 3.9+**  
   Download from [python.org](https://python.org)

2. **Clone or download this repository**

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt