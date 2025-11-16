# main.py
import tkinter as tk
from ui.app import AStarApp

def main():
    root = tk.Tk()
    root.title("A* Pathfinding Studio")
    root.geometry("1400x900")
    app = AStarApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()