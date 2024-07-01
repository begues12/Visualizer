import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Debug:
    
    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.debug_labels = {
            "FPS": None,
            "current_function": None,
            "change_mode": None,
            "time_left": None,
            "num_particles": None,
            "max_amplitude": None,
            "cpu_usage": None,
            "cpu_temp": None,
            "sensitivity": None,
            "volume": None,
            "resolution": None
        }
         
    
    def tab(self, parent):
        self.debug_labels = {}
        debug_frame = ttk.Frame(parent)
        debug_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        row = 0
        for key in self.debug_labels:
            label = ttk.Label(debug_frame, text=f"{key}:")
            label.grid(row=row, column=0, pady=5, padx=5, sticky='w')
            value_label = ttk.Label(debug_frame, text="")
            value_label.grid(row=row, column=1, pady=5, padx=5, sticky='w')
            self.debug_labels[key] = value_label
            row += 1
