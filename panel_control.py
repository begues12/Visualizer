import os
import pygame
from tkinter import Tk, Listbox, Button, IntVar, DoubleVar, Frame, Label, SINGLE, END, OptionMenu, StringVar, Entry, Checkbutton, BooleanVar, Canvas, Scrollbar, VERTICAL, LEFT
from tkinter import ttk

class ControlPanel:
    def __init__(self, visualizer):
        print("Control Panel")
        self.visualizer         = visualizer
        self.particle_manager   = visualizer.get_particle_manager()
        self.audio_manager      = visualizer.get_audio_manager()
        self.root = Tk()
        self.root.title("Control Panel")
        self.effects_status = {name: BooleanVar(value=True) for name in [func.get_effect_name() for func in self.visualizer.drawing_functions]}
        self.order_var = StringVar(value="random")
        self.time_var = DoubleVar(value=self.visualizer.effect_duration / 1000)  # Convertir a segundos
        self.current_effect_var = StringVar(value=self.visualizer.current_function.get_effect_name())
        
        self.create_widgets()
        self.update()
        self.last_selected_image = None

    def create_widgets(self):
        tab_control = ttk.Notebook(self.root)

        tab_images = ttk.Frame(tab_control)
        tab_basic_config = ttk.Frame(tab_control)
        tab_effects = ttk.Notebook(tab_control)
        tab_particles = ttk.Frame(tab_control)  
        tab_debug = ttk.Frame(tab_control)
        tab_settings = ttk.Frame(tab_control)
        
        tab_control.add(tab_images, text='Images')
        tab_control.add(tab_basic_config, text='Basic Config')
        tab_control.add(tab_effects, text='Effects')
        tab_control.add(tab_particles, text='Particles')  # Añadir la pestaña de partículas
        tab_control.add(tab_debug, text='Debug')
        tab_control.add(tab_settings, text='Settings')
        
        tab_control.pack(expand=1, fill="both")

        self.setup_images_tab(tab_images)
        self.setup_basic_config_tab(tab_basic_config)
        self.setup_effects_tab(tab_effects)
        self.setup_particles_tab(tab_particles)
        self.setup_settings_tab(tab_settings)
        self.setup_debug_tab(tab_debug)

        self.root.geometry("800x600")

    def setup_images_tab(self, parent):
        image_frame = ttk.Frame(parent)
        image_frame.pack(padx=10, pady=10, fill='both', expand=True)

        label = ttk.Label(image_frame, text="Available Images")
        label.grid(row=0, column=0, columnspan=2, pady=5, padx=5)  # Extender la etiqueta a dos columnas

        self.image_listbox = Listbox(image_frame, selectmode='single', width=50)
        self.image_listbox.bind("<<ListboxSelect>>", lambda event: self.load_image_size_entries())
        self.image_listbox.grid(row=1, column=0, columnspan=2, pady=5, padx=5)  # Extender el Listbox a dos columnas

        self.load_images()

        # Entrada para la anchura de la imagen
        ttk.Label(image_frame, text="Width:").grid(row=2, column=0, pady=5, padx=5)
        self.image_width_entry = Entry(image_frame)
        self.image_width_entry.grid(row=2, column=1, pady=5, padx=5)

        # Entrada para la altura de la imagen
        ttk.Label(image_frame, text="Height:").grid(row=3, column=0, pady=5, padx=5)
        self.image_height_entry = Entry(image_frame)
        self.image_height_entry.grid(row=3, column=1, pady=5, padx=5)

        # Entrada para el factor de escala
        ttk.Label(image_frame, text="Scale Factor:").grid(row=4, column=0, pady=5, padx=5)
        self.scale_factor_entry = Entry(image_frame)
        self.scale_factor_entry.insert(0, "1.0")
        self.scale_factor_entry.grid(row=4, column=1, pady=5, padx=5)

        # Botón para cambiar la imagen seleccionada
        button = ttk.Button(image_frame, text="Change Image", command=self.change_image)
        button.grid(row=5, column=0, columnspan=2, pady=5, padx=5)  # Extender el botón a dos columnas


    def setup_effects_tab(self, notebook):
        for effect in self.visualizer.drawing_functions:
            effect_frame = ttk.Frame(notebook)
            notebook.add(effect_frame, text=effect.get_effect_name())
            self.setup_effect_config(effect, effect_frame)
        
        save_button = ttk.Button(notebook, text="Save Effects Configuration", command=self.save_effects_configuration)
        save_button.pack(pady=10, padx=10)

    def setup_basic_config_tab(self, parent):
        
        
        ttk.Label(parent, text="Current Effect: ").grid(row=0, column=0, pady=5, padx=5)
        ttk.Label(parent, text=self.visualizer.current_function.get_effect_name()).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(parent, text="Effect Change Time (s):").grid(row=1, column=0, pady=5, padx=5)
    
        time_entry = ttk.Entry(parent, textvariable=self.time_var)
        time_entry.grid(row=2, column=1, pady=5, padx=5)
        time_entry.bind("<Return>", lambda event: self.update_time())

        ttk.Label(parent, text="Change Effect:").grid(row=3, column=0, pady=5, padx=5)
        effects = [effect.get_effect_name() for effect in self.visualizer.drawing_functions]
        current_effect_menu = ttk.OptionMenu(parent, self.current_effect_var, self.current_effect_var.get(), *effects, command=self.change_current_effect)
        current_effect_menu.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(parent, text="Effects Order:").grid(row=4, column=0, pady=5, padx=5)
        option_menu = ttk.OptionMenu(parent, self.order_var, "static", "static", "random", "sequential", command=self.update_order)
        option_menu.grid(row=4, column=1, pady=5, padx=5)

    def update_time(self):
        self.visualizer.effect_duration = self.time_var.get() * 1000  # Convertir a milisegundos
        print(f"Effect change time updated to {self.time_var.get()} seconds")

    def change_current_effect(self, effect_name):
        for effect in self.visualizer.drawing_functions:
            if effect.get_effect_name() == effect_name:
                self.visualizer.current_function = effect
                break
        print(f"Current effect changed to {effect_name}")

    
    def setup_effect_config(self, effect, parent):
        config = effect.get_config()
        row = 0
        for key, value in config.items():
            ttk.Label(parent, text=f"{key}:").grid(row=row, column=0, pady=5, padx=5)
            entry = Entry(parent)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, pady=5, padx=5)
            row += 1

        ttk.Button(parent, text="Update Config", command=lambda e=effect: self.update_effect_config(e, parent)).grid(row=row, column=0, columnspan=2, pady=5, padx=5)

    def update_effect_config(self, effect, parent):
        config = effect.get_config()
        for row, key in enumerate(config.keys()):
            entry = parent.grid_slaves(row=row, column=1)[0]
            config[key] = type(config[key])(entry.get())
        effect.save_config(config)

    def save_effects_configuration(self):
        for effect in self.visualizer.drawing_functions:
            effect.save_config_to_file(effect.get_config_file())
        
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

    def setup_debug_tab(self, parent):
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

        
    def load_images(self):
        image_folder = os.path.join(os.path.dirname(__file__), "images")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        for file_name in os.listdir(image_folder):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.image_listbox.insert(END, file_name)

    def change_image(self):
        selected_index = self.last_selected_image
        if selected_index:
            file_name = self.image_listbox.get(selected_index)
            image_folder = os.path.join(os.path.dirname(__file__), "images")
            file_path = os.path.join(image_folder, file_name)
            width_entry = int(float(self.image_width_entry.get()) * float(self.scale_factor_entry.get()))
            height_entry = int(float(self.image_height_entry.get()) * float(self.scale_factor_entry.get()))
            self.visualizer.center_image.load_image(file_path, width_entry, height_entry)

    def save_effects_configuration(self):
        for effect in self.visualizer.drawing_functions:
            file_path = os.path.join(os.path.dirname(__file__), f"{effect.get_effect_name().replace(' ', '_')}_config.json")
            effect.save_config_to_file(file_path)
    
    def toggle_debug_mode(self):
        self.visualizer.debug_mode = not self.visualizer.debug_mode

    def change_sensitivity(self, delta):
        self.audio_manager.sensitivity = max(0.1, min(3.0, self.visualizer.sensitivity + delta))

    def update_sensitivity(self, new_value):
        self.audio_manager.sensitivity = float(new_value)
        print(f"Sensitivity updated to {new_value}")

    
    def change_resolution(self, resolution):
        width, height = map(int, resolution.split('x'))
        self.visualizer.change_resolution(width, height)
        self.particle_manager.onScreenResize(width, height)

    def change_screen(self, screen):
        screen_num = int(screen.split()[1]) - 1
        self.visualizer.change_screen(screen_num)

    def toggle_fullscreen(self):
        self.visualizer.toggle_fullscreen()

    def load_image_size_entries(self):
        if self.image_listbox.curselection():
            self.last_selected_image = self.image_listbox.curselection()
            image_folder = os.path.join(os.path.dirname(__file__), "images")
            # Load image size and set entries
            image_name = self.image_listbox.get(self.last_selected_image)
            image_path = os.path.join(image_folder, image_name)
            image = pygame.image.load(image_path)
            self.image_width_entry.delete(0, END)
            self.image_width_entry.insert(0, str(image.get_width()))
            self.image_height_entry.delete(0, END)  
            self.image_height_entry.insert(0, str(image.get_height()))
    
    def update(self):
        self.root.update_idletasks()
        self.root.update()
        self.root.after(100, self.update)

    def update_effect_status(self):
        active_effects = [name for name, var in self.effects_status.items() if var.get()]
        self.visualizer.update_active_effects(active_effects)

    def update_order(self, value):
        self.visualizer.change_mode = value

    def update_max_particles(self, new_value):
        self.visualizer.particle_manager.max_particles = int(new_value)
        print(f"Max particles updated to {new_value}")

    def update_particle_speed(self, new_value):
        self.visualizer.particle_manager.particle_speed = float(new_value)
        print(f"Particle speed updated to {new_value}")

    def update_particle_size(self, new_value):
        self.visualizer.particle_manager.particle_size = float(new_value)
        print(f"Particle size updated to {new_value}")

    def update_debug_tab(self):
        # debug_info = self.visualizer.debug_info()
        # for key, value in debug_info.items():
        #     self.debug_labels[key].config(text=str(value))
        pass
    def update(self):
        self.update_debug_tab()
        self.root.update_idletasks()
        self.root.update()
        self.root.after(1000, self.update)

    
    def apply_changes(self):
        self.update_effect_status()
        active_effects_names = [name for name, var in self.effects_status.items() if var.get()]
        self.visualizer.update_active_effects(active_effects_names)
        self.update_order(self.order_var.get())