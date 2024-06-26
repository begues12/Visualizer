
class Debug:
    
    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.debug_labels = {}
         
    
    def gui(self, parent):
        self.debug_labels = {}
        debug_frame = ttk.Frame(parent)
        debug_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Crear etiquetas para cada dato de debug
        row = 0
        for key in ["FPS", "current_function", "change_mode", "time_left", "num_particles", "max_amplitude", "cpu_usage", "cpu_temp", "sensitivity", "volume", "resolution"]:
            label = ttk.Label(debug_frame, text=f"{key}:")
            label.grid(row=row, column=0, pady=5, padx=5, sticky='w')
            value_label = ttk.Label(debug_frame, text="")
            value_label.grid(row=row, column=1, pady=5, padx=5, sticky='w')
            self.debug_labels[key] = value_label
            row += 1
