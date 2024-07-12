import numpy as np
import pygame
import pyaudio
import os
import random
import math
import pygame.freetype
import psutil
from Managers.particle_manager import ParticleManager
from panel_control import ControlPanel
from threading import Thread
from Managers.audio_manager import AudioManager
from Effects.center_image import CenterImage
from Effects.spectrum_wave import SpectrumWave
from Effects.spectrum_semicircles import SpectrumSemicircles
from Effects.shooting_starts import ShootingStars
from Effects.frequency_spectrum import FrequencySpectrum
from Effects.background_color import BackgroundColor
from Effects.rotation_circles import RotationCircles
from Effects.circular_weave import CircularWeave
from Effects.frequency_waterfall import FrequencyWaterfall
from Effects.spinning_bars import SpinningBarsEffect

class Visualizer:
    
    # Pygame variables
    running = True
    font = None
    font_color = (255, 255, 255)  # Color del texto

    # Screen variables
    screen = None
    actual_resolution = (1280, 720)
    center_x, center_y = actual_resolution[0] / 2, actual_resolution[1] / 2
    # 10 Types of resolutions 16:9
    resolutions = [ (640, 480), (800, 600), (960, 540), (1024, 576), (1280, 720), (1366, 768), (1600, 900), (1920, 1080), (2560, 1440), (3840, 2160) ]
    fps = 60
    fullscreen = False
    
    audioManager = AudioManager()
    
    # Visualizer variables
    particle_manager = None
    max_particles = 50
    particle_speed = 1
    image_size = 1
    image_current_scale = 1
    current_function = None
    change_mode = "static"  # Modo de cambio de efecto: "static", "random" o "sequential"
    last_time = 0
    effect_duration = 10000  # Duración de cada efecto en milisegundos
    last_function_change_time = 0
    
    
    # Image variables
    image_path = os.path.join(os.path.dirname(__file__), "logo2.png")
    fire_sign = None
    fire_sign_rect = None

    drawing_functions = []
    
    # Debug variables
    debug_mode = False
    
    def __init__(self):
        pygame.init()
        pygame.font.init()  # Initialize the pygame font module
        pygame.freetype.init()  # Initialize the pygame FreeType library
        pygame.display.set_caption("Audio Visualizer")
        pygame.display.set_icon(pygame.image.load(self.image_path))
        self.clock = pygame.time.Clock()
        self.screen_info = pygame.display.Info()

        actual_resolution = (self.screen_info.current_w, self.screen_info.current_h)
       
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.actual_resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.actual_resolution)
            
        
        self.actual_resolution = (self.screen.get_width(), self.screen.get_height())
       
        self.particle_manager = ParticleManager(self.max_particles, self.screen, self.actual_resolution[0], self.actual_resolution[1])
       
        self.center_x = self.actual_resolution[0] / 2
        self.center_y = self.actual_resolution[1] / 2

        self.time_to_change_effect = 10 * self.fps
        self.particle_size = self.actual_resolution[0] / 100
        self.particle_speed = self.actual_resolution[0] / 100
        #Carga fuente
        self.font =  pygame.freetype.Font(None, 14)
        
        self.center_image = CenterImage(pygame.image.load(self.image_path), self, self.screen)
        
        
        # All drawing functions or classes
        self.drawing_functions = [
                        SpectrumWave(self),
                        SpectrumSemicircles(self),
                        ShootingStars(self),
                        FrequencySpectrum(self),
                        BackgroundColor(self),
                        RotationCircles(self),
                        CircularWeave(self),
                        ]
        
        self.active_effects = list(self.drawing_functions)

        self.chargeParticles()
        self.current_function = random.choice(self.active_effects)        
        
    def chargeParticles(self):
        self.particle_manager = ParticleManager(self.max_particles, self.screen, self.actual_resolution[0], self.actual_resolution[1])
        
    def start(self):
        while self.running:
            # Obtén datos de audio y volumen una sola vez por iteración
            audio_data = self.audioManager.getAudioData()
            volume = self.audioManager.getVolume()

            # Actualiza la pantalla y la imagen central
            self.screen.fill((0, 0, 0))

            # Ejecuta la función de dibujo actual si existe
            if self.current_function and hasattr(self.current_function, 'draw'):
                self.current_function.draw(audio_data)

            self.center_image.draw(audio_data)
        
            # Cambia la función de efecto según el tiempo y modo
            current_time = pygame.time.get_ticks()
            if (current_time - self.last_function_change_time >= self.effect_duration and
                self.change_mode != "static"):
                self.current_function = self.next_effect()
                self.last_function_change_time = current_time

            # Manejo de partículas
            self.particle_manager.move_particles(audio_data, volume, self.clock.get_time())
            self.particle_manager.update_particles()

            # Modo de depuración
            if self.debug_mode:
                self.debug()

            # Actualiza la pantalla
            pygame.display.flip()

        # Limpieza final al terminar el bucle
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        pygame.quit()

    
    def get_screen(self):
        return self.screen
    
    def get_audio_manager(self):
        return self.audioManager
        
    def get_particle_manager(self):
        return self.particle_manager
    
    def get_screen_center(self):
        return self.screen.get_width() / 2, self.screen.get_height() / 2

    def change_resolution(self, width, height):
        self.actual_resolution = (width, height)
        self.onScreenChange()
        
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.actual_resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.actual_resolution)
            
        self.onScreenChange()
    
    def update_active_effects(self, active_effect_names):
        self.active_effects = [effect for effect in self.drawing_functions if effect.get_effect_name() in active_effect_names]
        
        if not self.active_effects:
            self.active_effects = [self.idle_effect]  # Suponiendo que existe un efecto de reposo
        
    def idle_effect(self, audio_data):
        self.screen.fill((0, 0, 0))  # Simplemente rellena la pantalla de negro o muestra un mensaje.
        self.font.render_to(self.screen, (10, 10), "No active effects.", (255, 255, 255))
            
    def next_effect(self):
        if self.change_mode == "random":
            return random.choice(self.active_effects)
        else:
            current_function_index = self.active_effects.index(self.current_function)
            next_function_index = current_function_index + 1 if current_function_index < len(self.active_effects) - 1 else 0
            return self.active_effects[next_function_index]
         
    
    def onScreenChange(self):
        #Calcula las nuevas posiciones centrales
        self.center_image.recalculate_center()
        self.center_x = self.actual_resolution[0] / 2 
        self.center_y = self.actual_resolution[1] / 2
        self.current_function.on_screen_resize(self.actual_resolution[0], self.actual_resolution[1])

        
def run_visualizer(control_panel):
    visualizer = control_panel.visualizer
    visualizer.start()
        
if __name__ == "__main__":
    control_panel = ControlPanel(Visualizer())
    visualizer_thread = Thread(target=run_visualizer, args=(control_panel,))
    visualizer_thread.start()
    control_panel.root.mainloop()
    