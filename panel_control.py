import os
import json
import pygame
import psutil
import numpy as np
from tkinter import (
    Tk, Listbox, IntVar, DoubleVar, StringVar, BooleanVar,
    Entry, END, messagebox,
)
from tkinter import ttk


def _range_for(value):
    """Heuristica de (minimo, maximo, resolucion) para un valor de config."""
    is_int = isinstance(value, bool) is False and isinstance(value, int)
    v = abs(float(value))
    if is_int:
        return 0, max(10, int(v * 3) or 10), 1
    if v <= 1:
        return 0.0, max(1.0, v * 2), 0.01
    if v <= 10:
        return 0.0, max(10.0, v * 2), 0.05
    return 0.0, max(1.0, v * 3), 1.0


class ControlPanel:
    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.particle_manager = visualizer.get_particle_manager()
        self.audio_manager = visualizer.get_audio_manager()

        self.root = Tk()
        self.root.title("Audio Visualizer - Panel de Control")
        self.root.geometry("900x680")

        self.effects_status = {
            e.get_effect_name(): BooleanVar(value=True)
            for e in self.visualizer.drawing_functions
        }
        self.order_var = StringVar(value=self.visualizer.change_mode)
        self.time_var = DoubleVar(value=self.visualizer.effect_duration / 1000)
        self.current_effect_var = StringVar(
            value=self.visualizer.current_function.get_effect_name()
        )
        self.last_selected_image = None
        self.debug_labels = {}
        self.general_labels = {}

        self.create_widgets()
        self.update()

    # ------------------------------------------------------------------ UI
    def create_widgets(self):
        tabs = ttk.Notebook(self.root)
        self.tab_general = ttk.Frame(tabs)
        self.tab_effects = ttk.Frame(tabs)
        self.tab_effect_config = ttk.Notebook(tabs)
        self.tab_particles = ttk.Frame(tabs)
        self.tab_images = ttk.Frame(tabs)
        self.tab_settings = ttk.Frame(tabs)
        self.tab_debug = ttk.Frame(tabs)

        tabs.add(self.tab_general, text='General')
        tabs.add(self.tab_effects, text='Efectos')
        tabs.add(self.tab_effect_config, text='Config. Efecto')
        tabs.add(self.tab_particles, text='Particulas')
        tabs.add(self.tab_images, text='Imagenes')
        tabs.add(self.tab_settings, text='Ajustes')
        tabs.add(self.tab_debug, text='Debug')
        tabs.pack(expand=1, fill='both')

        self.setup_general_tab(self.tab_general)
        self.setup_effects_tab(self.tab_effects)
        self.setup_effect_config_tabs(self.tab_effect_config)
        self.setup_particles_tab(self.tab_particles)
        self.setup_images_tab(self.tab_images)
        self.setup_settings_tab(self.tab_settings)
        self.setup_debug_tab(self.tab_debug)

    def _labeled(self, parent, text, row):
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky='w', padx=8, pady=6)

    # ------------------------------------------------------------- General
    def setup_general_tab(self, parent):
        self._labeled(parent, "Efecto actual:", 0)
        lbl = ttk.Label(parent, text=self.current_effect_var.get(), font=('Segoe UI', 10, 'bold'))
        lbl.grid(row=0, column=1, sticky='w', padx=8, pady=6)
        self.general_labels['current_effect'] = lbl

        self._labeled(parent, "Cambiar efecto:", 1)
        names = [e.get_effect_name() for e in self.visualizer.drawing_functions]
        ttk.OptionMenu(
            parent, self.current_effect_var, self.current_effect_var.get(),
            *names, command=self.change_current_effect
        ).grid(row=1, column=1, sticky='w', padx=8, pady=6)

        self._labeled(parent, "Modo de cambio:", 2)
        ttk.OptionMenu(
            parent, self.order_var, self.order_var.get(),
            "static", "random", "sequential", command=self.update_order
        ).grid(row=2, column=1, sticky='w', padx=8, pady=6)

        self._labeled(parent, "Duracion por efecto (s):", 3)
        e = ttk.Entry(parent, textvariable=self.time_var, width=10)
        e.grid(row=3, column=1, sticky='w', padx=8, pady=6)
        e.bind("<Return>", lambda ev: self.update_time())
        ttk.Button(parent, text="Aplicar", command=self.update_time).grid(
            row=3, column=2, sticky='w', padx=4)

        btns = ttk.Frame(parent)
        btns.grid(row=4, column=0, columnspan=3, sticky='w', padx=8, pady=12)
        ttk.Button(btns, text="◀ Anterior", command=lambda: self.step_effect(-1)).pack(side='left', padx=4)
        ttk.Button(btns, text="Siguiente ▶", command=lambda: self.step_effect(1)).pack(side='left', padx=4)

    # ------------------------------------------------------------- Effects
    def setup_effects_tab(self, parent):
        ttk.Label(parent, text="Efectos activos (para modos random / sequential):").pack(
            anchor='w', padx=10, pady=(10, 4))

        grid = ttk.Frame(parent)
        grid.pack(fill='both', expand=True, padx=10)
        for i, e in enumerate(self.visualizer.drawing_functions):
            name = e.get_effect_name()
            ttk.Checkbutton(
                grid, text=name, variable=self.effects_status[name],
                command=self.apply_active_effects
            ).grid(row=i // 2, column=i % 2, sticky='w', padx=8, pady=3)

        bar = ttk.Frame(parent)
        bar.pack(anchor='w', padx=10, pady=10)
        ttk.Button(bar, text="Activar todos", command=lambda: self.set_all_effects(True)).pack(side='left', padx=4)
        ttk.Button(bar, text="Desactivar todos", command=lambda: self.set_all_effects(False)).pack(side='left', padx=4)

    def set_all_effects(self, value):
        for var in self.effects_status.values():
            var.set(value)
        self.apply_active_effects()

    def apply_active_effects(self):
        selected = [e for e in self.visualizer.drawing_functions
                    if self.effects_status[e.get_effect_name()].get()]
        if not selected:
            messagebox.showwarning("Efectos", "Debe haber al menos un efecto activo.")
            self.effects_status[self.visualizer.current_function.get_effect_name()].set(True)
            selected = [self.visualizer.current_function]
        self.visualizer.active_effects = selected
        if self.visualizer.current_function not in selected:
            self.visualizer.current_function = selected[0]
            self.current_effect_var.set(selected[0].get_effect_name())

    # -------------------------------------------------------- Effect config
    def setup_effect_config_tabs(self, notebook):
        for effect in self.visualizer.drawing_functions:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=effect.get_effect_name())
            self.build_effect_config(effect, frame)

    def build_effect_config(self, effect, container):
        for child in container.winfo_children():
            child.destroy()

        config = effect.get_config()
        if not config:
            ttk.Label(container, text="Este efecto no tiene parametros configurables.").pack(
                padx=12, pady=12, anchor='w')
            return

        grid = ttk.Frame(container)
        grid.pack(fill='x', padx=12, pady=10)

        for row, (key, value) in enumerate(config.items()):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                continue
            is_int = isinstance(value, int)
            lo, hi, res = _range_for(value)
            var = DoubleVar(value=float(value))

            ttk.Label(grid, text=f"{key}:").grid(row=row, column=0, sticky='w', padx=4, pady=5)
            scale = ttk.Scale(grid, from_=lo, to=hi, variable=var, length=260)
            scale.grid(row=row, column=1, padx=4, pady=5)
            entry = ttk.Entry(grid, textvariable=var, width=10)
            entry.grid(row=row, column=2, padx=4, pady=5)

            def on_change(*_a, k=key, v=var, i=is_int, cfg=config):
                try:
                    val = v.get()
                except Exception:
                    return
                cfg[k] = int(round(val)) if i else round(val, 4)

            var.trace_add('write', on_change)

        bar = ttk.Frame(container)
        bar.pack(anchor='w', padx=12, pady=8)
        ttk.Button(bar, text="Guardar en archivo",
                   command=lambda e=effect: self.save_effect_config(e)).pack(side='left', padx=4)
        ttk.Button(bar, text="Recargar de archivo",
                   command=lambda e=effect, c=container: self.reload_effect_config(e, c)).pack(side='left', padx=4)

    def save_effect_config(self, effect):
        try:
            effect.save_config_to_file(effect.get_config_file())
            messagebox.showinfo("Config", f"Configuracion de '{effect.get_effect_name()}' guardada.")
        except Exception as ex:
            messagebox.showerror("Config", f"No se pudo guardar: {ex}")

    def reload_effect_config(self, effect, container):
        try:
            effect.load_config_from_file(effect.get_config_file())
        except Exception as ex:
            messagebox.showerror("Config", f"No se pudo recargar: {ex}")
            return
        self.build_effect_config(effect, container)

    # ----------------------------------------------------------- Particles
    def setup_particles_tab(self, parent):
        self._labeled(parent, "Max. particulas:", 0)
        self.max_particles_var = IntVar(value=self.particle_manager.get_max_particles())
        e = ttk.Entry(parent, textvariable=self.max_particles_var, width=10)
        e.grid(row=0, column=1, sticky='w', padx=8, pady=6)
        e.bind("<Return>", lambda ev: self.update_max_particles())
        ttk.Button(parent, text="Aplicar", command=self.update_max_particles).grid(row=0, column=2, padx=4)

        self._labeled(parent, "Velocidad:", 1)
        self.particle_speed_var = DoubleVar(value=self.visualizer.particle_speed)
        ttk.Scale(parent, from_=0.1, to=10.0, variable=self.particle_speed_var,
                  command=self.update_particle_speed, length=240).grid(row=1, column=1, padx=8, pady=6)

        self._labeled(parent, "Tamano:", 2)
        self.particle_size_var = DoubleVar(value=self.visualizer.particle_size)
        ttk.Scale(parent, from_=1, to=100, variable=self.particle_size_var,
                  command=self.update_particle_size, length=240).grid(row=2, column=1, padx=8, pady=6)

    def update_max_particles(self):
        self.particle_manager.max_particles = int(self.max_particles_var.get())

    def update_particle_speed(self, _v):
        self.particle_manager.particle_speed = float(self.particle_speed_var.get())

    def update_particle_size(self, _v):
        self.particle_manager.particle_size = float(self.particle_size_var.get())

    # -------------------------------------------------------------- Images
    def setup_images_tab(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        ttk.Label(frame, text="Imagenes disponibles:").grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky='w')
        self.image_listbox = Listbox(frame, selectmode='single', width=50, height=8)
        self.image_listbox.bind("<<ListboxSelect>>", lambda ev: self.load_image_size_entries())
        self.image_listbox.grid(row=1, column=0, columnspan=2, pady=5, padx=5)
        self.load_images()

        ttk.Label(frame, text="Ancho:").grid(row=2, column=0, pady=5, padx=5, sticky='e')
        self.image_width_entry = Entry(frame)
        self.image_width_entry.grid(row=2, column=1, pady=5, padx=5, sticky='w')

        ttk.Label(frame, text="Alto:").grid(row=3, column=0, pady=5, padx=5, sticky='e')
        self.image_height_entry = Entry(frame)
        self.image_height_entry.grid(row=3, column=1, pady=5, padx=5, sticky='w')

        ttk.Label(frame, text="Factor de escala:").grid(row=4, column=0, pady=5, padx=5, sticky='e')
        self.scale_factor_entry = Entry(frame)
        self.scale_factor_entry.insert(0, "1.0")
        self.scale_factor_entry.grid(row=4, column=1, pady=5, padx=5, sticky='w')

        ttk.Button(frame, text="Cambiar imagen", command=self.change_image).grid(
            row=5, column=0, columnspan=2, pady=8, padx=5)

    def load_images(self):
        folder = os.path.join(os.path.dirname(__file__), "images")
        os.makedirs(folder, exist_ok=True)
        for name in os.listdir(folder):
            if name.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.image_listbox.insert(END, name)

    def load_image_size_entries(self):
        if not self.image_listbox.curselection():
            return
        self.last_selected_image = self.image_listbox.curselection()
        folder = os.path.join(os.path.dirname(__file__), "images")
        path = os.path.join(folder, self.image_listbox.get(self.last_selected_image))
        image = pygame.image.load(path)
        self.image_width_entry.delete(0, END)
        self.image_width_entry.insert(0, str(image.get_width()))
        self.image_height_entry.delete(0, END)
        self.image_height_entry.insert(0, str(image.get_height()))

    def change_image(self):
        if not self.last_selected_image:
            return
        folder = os.path.join(os.path.dirname(__file__), "images")
        path = os.path.join(folder, self.image_listbox.get(self.last_selected_image))
        scale = float(self.scale_factor_entry.get())
        w = int(float(self.image_width_entry.get()) * scale)
        h = int(float(self.image_height_entry.get()) * scale)
        self.visualizer.center_image.load_image(path, w, h)

    # ------------------------------------------------------------- Settings
    def setup_settings_tab(self, parent):
        self._labeled(parent, "Sensibilidad de sonido:", 0)
        self.sensitivity_var = DoubleVar(value=self.audio_manager.sensitivity)
        ttk.Scale(parent, from_=0.0, to=5.0, variable=self.sensitivity_var,
                  command=self.update_sensitivity, length=240).grid(row=0, column=1, padx=8, pady=6)

        self._labeled(parent, "Resolucion:", 1)
        self.resolution_var = StringVar(
            value=f"{self.visualizer.actual_resolution[0]}x{self.visualizer.actual_resolution[1]}")
        res = [f"{r[0]}x{r[1]}" for r in self.visualizer.resolutions]
        ttk.OptionMenu(parent, self.resolution_var, self.resolution_var.get(),
                       *res, command=self.change_resolution).grid(row=1, column=1, sticky='w', padx=8, pady=6)

        self._labeled(parent, "Pantalla:", 2)
        screens = [f"Screen {i + 1}" for i in range(pygame.display.get_num_displays())]
        self.screen_var = StringVar(value="Screen 1")
        ttk.OptionMenu(parent, self.screen_var, self.screen_var.get(),
                       *screens, command=self.change_screen).grid(row=2, column=1, sticky='w', padx=8, pady=6)

        ttk.Button(parent, text="Pantalla completa (on/off)",
                   command=self.toggle_fullscreen).grid(row=3, column=0, columnspan=2, sticky='w', padx=8, pady=12)

    def update_sensitivity(self, _v):
        self.audio_manager.set_sensitivity(float(self.sensitivity_var.get()))

    def change_resolution(self, resolution):
        w, h = map(int, resolution.split('x'))
        self.visualizer.change_resolution(w, h)
        self.particle_manager.onScreenResize(w, h)

    def change_screen(self, screen):
        self.visualizer.change_screen(int(screen.split()[1]) - 1)

    def toggle_fullscreen(self):
        self.visualizer.toggle_fullscreen()

    # ---------------------------------------------------------------- Debug
    def setup_debug_tab(self, parent):
        ttk.Button(parent, text="Toggle overlay debug (en pantalla)",
                   command=self.toggle_debug_mode).pack(anchor='w', padx=10, pady=8)
        frame = ttk.Frame(parent)
        frame.pack(padx=10, pady=6, fill='both', expand=True)
        keys = ["FPS", "efecto_actual", "modo_cambio", "tiempo_restante",
                "num_particulas", "amplitud_max", "cpu_%", "sensibilidad",
                "volumen", "resolucion"]
        for row, key in enumerate(keys):
            ttk.Label(frame, text=f"{key}:").grid(row=row, column=0, sticky='w', padx=5, pady=3)
            val = ttk.Label(frame, text="-")
            val.grid(row=row, column=1, sticky='w', padx=5, pady=3)
            self.debug_labels[key] = val

    def toggle_debug_mode(self):
        self.visualizer.debug_mode = not self.visualizer.debug_mode

    # ------------------------------------------------------------ Callbacks
    def change_current_effect(self, name):
        for e in self.visualizer.drawing_functions:
            if e.get_effect_name() == name:
                self.visualizer.current_function = e
                self.current_effect_var.set(name)
                break

    def step_effect(self, direction):
        effects = self.visualizer.active_effects or self.visualizer.drawing_functions
        try:
            idx = effects.index(self.visualizer.current_function)
        except ValueError:
            idx = 0
        self.visualizer.current_function = effects[(idx + direction) % len(effects)]
        self.current_effect_var.set(self.visualizer.current_function.get_effect_name())

    def update_order(self, value):
        self.visualizer.change_mode = value

    def update_time(self):
        self.visualizer.effect_duration = self.time_var.get() * 1000

    # --------------------------------------------------------- Refresh loop
    def update_debug_tab(self):
        v = self.visualizer
        try:
            audio = self.audio_manager.get_audio_data()
            ticks = pygame.time.get_ticks()
            time_left = max(0, (v.effect_duration - (ticks - v.last_function_change_time)) / 1000)
            values = {
                "FPS": f"{v.clock.get_fps():.1f}",
                "efecto_actual": v.current_function.get_effect_name(),
                "modo_cambio": v.change_mode,
                "tiempo_restante": f"{time_left:.1f} s" if v.change_mode != 'static' else "-",
                "num_particulas": self.particle_manager.getNumParticles(),
                "amplitud_max": int(np.max(np.abs(audio.astype(np.int32)))) if audio.size else 0,
                "cpu_%": f"{psutil.cpu_percent():.0f}",
                "sensibilidad": f"{self.audio_manager.sensitivity:.2f}",
                "volumen": f"{self.audio_manager.get_volume(audio):.0f}",
                "resolucion": f"{v.actual_resolution[0]}x{v.actual_resolution[1]}",
            }
            for key, label in self.debug_labels.items():
                label.config(text=str(values.get(key, "-")))
        except Exception:
            pass
        # Mantiene sincronizada la etiqueta de efecto actual del tab General
        if 'current_effect' in self.general_labels:
            self.general_labels['current_effect'].config(
                text=self.visualizer.current_function.get_effect_name())
        self.current_effect_var.set(self.visualizer.current_function.get_effect_name())

    def update(self):
        self.update_debug_tab()
        self.root.update_idletasks()
        self.root.after(300, self.update)
