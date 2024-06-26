import os
import pygame
from tkinter import Tk, Listbox, Button, IntVar, DoubleVar, Frame, Label, SINGLE, END, OptionMenu, StringVar, Entry, Checkbutton, BooleanVar, Canvas, Scrollbar, VERTICAL, LEFT
from tkinter import ttk
from control_panel.images import ControlPanelImages

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

        self.create_widgets()
        self.update()
        self.last_selected_image = None

    def create_widgets(self):
        tab_control = ttk.Notebook(self.root)

        tab_images = ttk.Frame(tab_control)
        tab_effects = ttk.Frame(tab_control)
        tab_particles = ttk.Frame(tab_control)  
        tab_debug = ttk.Frame(tab_control)
        tab_settings = ttk.Frame(tab_control)
        
        tab_control.add(tab_images, text='Images')
        tab_control.add(tab_effects, text='Effects')
        tab_control.add(tab_particles, text='Particles')  # Añadir la pestaña de partículas
        tab_control.add(tab_debug, text='Debug')
        tab_control.add(tab_settings, text='Settings')
        
        tab_control.pack(expand=1, fill="both")

        self.ControlPanelImages().setup_images_tab(tab_images)
        self.setup_effects_tab(tab_effects)
        self.setup_particles_tab(tab_particles)
        self.setup_settings_tab(tab_settings)
        self.setup_debug_tab(tab_debug)

        self.root.geometry("800x600")
    

    def change_image(self):
        selected_index = self.last_selected_image
        if selected_index:
            file_name = self.image_listbox.get(selected_index)
            image_folder = os.path.join(os.path.dirname(__file__), "images")
            file_path = os.path.join(image_folder, file_name)
            width_entry = int(float(self.image_width_entry.get()) * float(self.scale_factor_entry.get()))
            height_entry = int(float(self.image_height_entry.get()) * float(self.scale_factor_entry.get()))
            self.visualizer.center_image.load_image(file_path, width_entry, height_entry)

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
        debug_info = self.visualizer.debug_info()
        for key, value in debug_info.items():
            self.debug_labels[key].config(text=str(value))

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