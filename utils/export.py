# utils/export.py
import tkinter.filedialog as filedialog

def export_path_to_csv(path):
    if not path:
        return None
    path_str = "\n".join([f"{r},{c}" for (r,c) in path])
    filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
    if filepath:
        with open(filepath, 'w') as f:
            f.write("row,col\n")
            f.write(path_str)
        return filepath
    return None