import tkinter as tk
from tkinter import ttk    

class Effects:
    
    def __init__(self, parent):
        self.parent = parent
        self.effects_status = {
            "Color": tk.BooleanVar(),
            "Size": tk.BooleanVar(),
            "Speed": tk.BooleanVar(),
            "Direction": tk.BooleanVar(),
            "Shape": tk.BooleanVar(),
            "Opacity": tk.BooleanVar(),
            "Rotation": tk.BooleanVar(),
            "Position": tk.BooleanVar()
        }
        self.order_var = tk.StringVar()
        self.order_var.set("static")

    def tab(self, parent):
        # Contenido de la pestaña de efectos
        effects_frame = ttk.Frame(parent)
        effects_frame.pack(padx=10, pady=10, fill='both', expand=True)

        label = ttk.Label(effects_frame, text="Effects Control")
        label.grid(row=0, column=0, columnspan=2, pady=5, padx=5)

        for effect_name, var in self.effects_status.items():
            checkbutton = ttk.Checkbutton(effects_frame, text=effect_name, variable=var, onvalue=True, offvalue=False, command=self.update_effect_status)
            checkbutton.grid(sticky='w', row=list(self.effects_status.keys()).index(effect_name) + 1, column=0, columnspan=2, pady=5, padx=5)

        label_order = ttk.Label(effects_frame, text="Effects Order:")
        label_order.grid(row=len(self.effects_status) + 1, column=0, pady=5, padx=5)

        option_menu = ttk.OptionMenu(effects_frame, self.order_var, "static", "static", "random", "sequential", command=self.update_order)
        option_menu.grid(row=len(self.effects_status) + 1, column=1, pady=5, padx=5)
        
        next_button = ttk.Button(effects_frame, text="Apply Changes", command=self.apply_changes)
        next_button.grid(row=len(self.effects_status) + 2, column=0, columnspan=2, pady=5, padx=5)
        
        prev_button = ttk.Button(effects_frame, text="Toggle Debug Mode", command=self.toggle_debug_mode)
        prev_button.grid(row=len(self.effects_status) + 3, column=0, columnspan=2, pady=5, padx=5)