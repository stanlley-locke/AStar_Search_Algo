# ui/theme.py
import tkinter as tk
from tkinter import ttk
import sys

def detect_system_theme():
    """Simple heuristic: default to dark on macOS/Linux, light on Windows — or just use dark as default."""
    # You can enhance this later with platform-specific checks
    return "dark"  # or "light" if you prefer

def apply_theme(root, canvas):
    system_theme = detect_system_theme()
    
    if system_theme == "dark":
        # Apple Dark Mode
        bg = "#FFFFFF"        # Window background
        fg = "#000000"        # Text
        sidebar_bg = "#252529" # Sidebar
        button_bg = "#1313D6"  # Button default
        button_active = "#0C0C8F"
        accent = "#14DB0D"     # Apple blue
        is_dark = True
    else:
        # Apple Light Mode
        bg = "#FFFFFF"
        fg = "#000000"
        sidebar_bg = "#F5F5F7"
        button_bg = "#E5E5EA"
        button_active = "#D1D1D6"
        accent = "#007AFF"     # Apple blue (light variant)
        is_dark = False

    # Apply to root
    root.configure(bg=bg)
    
    # Configure ttk styles
    style = ttk.Style()
    
    # Frames
    style.configure("TFrame", background=bg)
    
    # Labels
    style.configure("TLabel", background=bg, foreground=fg, font=("SF Pro", 11))
    
    # Buttons
    style.configure("TButton",
                    background=button_bg,
                    foreground=fg,
                    font=("SF Pro", 11),
                    borderwidth=0,
                    padding=(10, 6))
    style.map("TButton", background=[("active", button_active)])
    
    # Accent button (for primary actions like "Run")
    style.configure("Accent.TButton",
                    background=accent,
                    foreground="white",
                    font=("SF Pro", 11, "bold"),
                    padding=(10, 6))
    style.map("Accent.TButton", background=[("active", "#0062CC" if is_dark else "#0057D9")])
    
    # Radio buttons
    style.configure("TRadiobutton", background=bg, foreground=fg, font=("SF Pro", 10))
    
    # Optional: apply to canvas if provided
    if canvas:
        canvas.configure(bg=bg, highlightthickness=0)

    return {
        "bg": bg,
        "fg": fg,
        "sidebar_bg": sidebar_bg,
        "button_bg": button_bg,
        "accent": accent,
        "is_dark": is_dark
    }