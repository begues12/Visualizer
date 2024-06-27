

        def setup_particles_tab(self, parent):
        particle_frame = ttk.Frame(parent)
        particle_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Control deslizante para la cantidad de partículas
        ttk.Label(particle_frame, text="Max Particles:").grid(row=0, column=0, pady=5, padx=5)
        self.max_particles_var = IntVar(value=self.visualizer.max_particles)
        max_particles_scale = ttk.Entry(particle_frame, textvariable=self.max_particles_var)
        max_particles_scale.bind("<Return>", lambda event: self.update_max_particles(max_particles_scale.get()))
        max_particles_scale.grid(row=0, column=1, pady=5, padx=5)

        # Control deslizante para la velocidad de las partículas
        ttk.Label(particle_frame, text="Particle Speed:").grid(row=1, column=0, pady=5, padx=5)
        self.particle_speed_var = DoubleVar(value=self.visualizer.particle_speed)
        particle_speed_scale = ttk.Scale(particle_frame, from_=0.1, to=10.0, orient='horizontal', variable=self.particle_speed_var, command=self.update_particle_speed)
        particle_speed_scale.grid(row=1, column=1, pady=5, padx=5)

        # Control deslizante para el tamaño de las partículas
        ttk.Label(particle_frame, text="Particle Size:").grid(row=2, column=0, pady=5, padx=5)
        self.particle_size_var = DoubleVar(value=self.visualizer.particle_size)
        particle_size_scale = ttk.Scale(particle_frame, from_=1, to=100, orient='horizontal', variable=self.particle_size_var, command=self.update_particle_size)
        particle_size_scale.grid(row=2, column=1, pady=5, padx=5)
        
        
        