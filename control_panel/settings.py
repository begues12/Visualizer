
    def setup_settings_tab(self, parent):
        # Contenido de la pestaña de ajustes
        settings_frame = ttk.Frame(parent)
        settings_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        ttk.Label(settings_frame, text="Sound Sensitivity:").grid(row=0, column=0, pady=5, padx=5)
        self.sensitivity_var = DoubleVar(value=self.audio_manager.sensitivity)  # Inicia con el valor actual de sensibilidad
        sensitivity_scale = ttk.Scale(settings_frame, from_=0.0, to=5.0, orient='horizontal', variable=self.sensitivity_var, command=self.update_sensitivity)
        sensitivity_scale.grid(row=0, column=1, pady=5, padx=5)
        
        # Asegúrate de que resolution_var es una StringVar y está correctamente inicializada
        self.resolution_var = StringVar(value=f"{self.visualizer.actual_resolution[0]}x{self.visualizer.actual_resolution[1]}")
        resolutions = [f"{res[0]}x{res[1]}" for res in self.visualizer.resolutions]
        
        # Asegúrate de pasar self.resolution_var al OptionMenu
        ttk.Label(settings_frame, text="Resolution:").grid(row=1, column=0, pady=5, padx=5)
        resolution_menu = ttk.OptionMenu(settings_frame, self.resolution_var, self.resolution_var.get(), *resolutions, command=self.change_resolution)
        resolution_menu.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(settings_frame, text="Screen:").grid(row=2, column=0, pady=5, padx=5)
        screen_options = [f"Screen {i+1}" for i in range(pygame.display.get_num_displays())]
        self.screen_var = StringVar(value="Screen 1")
        screen_menu = ttk.OptionMenu(settings_frame, self.screen_var, self.screen_var.get(), *screen_options, command=self.change_screen)
        screen_menu.grid(row=2, column=1, pady=5, padx=5)

        ttk.Button(settings_frame, text="Toggle Fullscreen", command=self.toggle_fullscreen).grid(row=3, column=0, columnspan=2, pady=5, padx=5)

        