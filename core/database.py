# core/database.py
import sqlite3
import json

class MapDatabase:
    def __init__(self, db_path="astar_maps.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    rows INTEGER,
                    cols INTEGER,
                    grid TEXT,
                    start TEXT,
                    goal TEXT,
                    waypoints TEXT,
                    tags TEXT,
                    rating INTEGER DEFAULT 0,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_map(self, name, rows, cols, grid, start, goal, waypoints=None, tags="", rating=0):
        grid_str = json.dumps(grid)
        start_str = json.dumps(start)
        goal_str = json.dumps(goal)
        waypoints_str = json.dumps(waypoints or [])
        tags_str = json.dumps([tag.strip() for tag in tags.split(',')] if tags else [])
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO maps (name, rows, cols, grid, start, goal, waypoints, tags, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, rows, cols, grid_str, start_str, goal_str, waypoints_str, tags_str, rating))
            conn.commit()

    def load_maps(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, name, tags, rating FROM maps ORDER BY created DESC")
            return cursor.fetchall()

    def get_map_by_id(self, map_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM maps WHERE id = ?", (map_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "rows": row[2],
                    "cols": row[3],
                    "grid": json.loads(row[4]),
                    "start": tuple(json.loads(row[5])),
                    "goal": tuple(json.loads(row[6])),
                    "waypoints": json.loads(row[7]),
                    "tags": json.loads(row[8]),
                    "rating": row[9]
                }
        return None