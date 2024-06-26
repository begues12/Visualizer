import numpy as np
import pygame
import pyaudio
import os
import random
import math
import colorsys
import pygame.freetype
import psutil
from Managers.particle_manager import ParticleManager
from StarManager import StarManager
from panel_control import ControlPanel
from threading import Thread
from Managers.audio_manager import AudioManager
from Effects.center_image import CenterImage
from Effects.spectrum_wave import SpectrumWave
from Effects.spectrum_semicircles import SpectrumSemicircles
from Effects.shooting_starts import ShootingStars

class Visualizer:
    
    # Pygame variables
    running = True
    font = None
    font_color = (255, 255, 255)  # Color del texto

    # Screen variables
    screen = None
    actual_resolution = (640, 480)
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
    change_mode = "static"
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
                        # self.background_color,
                        # self.bouncy_image,
                        # self.spectrum_semicircles, 
                        # self.circular_wave, 
                        # self.frequency_spectrum,
                        # self.shooting_stars,
                        ]
        
        self.active_effects = list(self.drawing_functions)

        self.chargeParticles()
        self.current_function = random.choice(self.active_effects)        
        
    def chargeParticles(self):
        self.particle_manager = ParticleManager(self.max_particles, self.screen, self.actual_resolution[0], self.actual_resolution[1])
        self.star_manager = StarManager(10, self.screen, self.actual_resolution[0], self.actual_resolution[1])
        
    def start(self):
        while self.running:
                                    
            audio_data = self.audioManager.getAudioData()
            self.volume = self.audioManager.getVolume()
            
            self.screen.fill((0,0,0))
            
            # If has draw function, execute it
            if self.current_function and hasattr(self.current_function, 'draw'):
                self.current_function.draw(audio_data)  # Ejecuta la función actual
            
            if pygame.time.get_ticks() - self.last_function_change_time >= self.effect_duration and self.change_mode != "static":
                self.current_function = self.next_effect()
                self.last_function_change_time = pygame.time.get_ticks()
            
            # Calcula el volumen máximo de la señal de audio
            
            self.center_image.draw(audio_data)

            # Particles
            self.particle_manager.move_particles(audio_data, self.volume, self.clock.get_time())
            self.particle_manager.update_particles()
            # self.particle_manager.update_scale(audio_data, self.volume)
            
            # Dibuja el texto de depuración en la esquina inferior derecha si el modo de depuración está activado
            if self.debug_mode:
                self.debug()
            
            pygame.display.flip()
            
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        pygame.quit()
    
    def get_audio_manager(self):
        return self.audioManager
        
    def get_particle_manager(self):
        return self.particle_manager
    
    def get_screen_center(self):
        return self.center_x, self.center_y

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
        

    def shooting_stars(self, audio_data):
        self.star_manager.draw_shooting_stars()
        self.star_manager.update_stars()
        self.star_manager.update_gravity_centers()
    
    def frequency_spectrum(self, audio_data):
        num_bands = 10
        band_height = self.actual_resolution[1] // num_bands

        for i in reversed(range(num_bands)):  # Invierte el orden del bucle
            band_data = audio_data[i * len(audio_data) // num_bands:(i + 1) * len(audio_data) // num_bands]
            color = self.Rcolor()
            y = self.actual_resolution[1] - (i + 1) * band_height  # Ajusta la coordenada 'y'
            rect = pygame.Rect(0, y, int(self.volume / 32768 * self.actual_resolution[0]), band_height)
            pygame.draw.rect(self.screen, color, rect)
    
    def rotation_circles(self, audio_data):
        center_x = self.actual_resolution[0] // 2
        center_y = self.actual_resolution[1] // 2
        angle = 0
        max_radius = 250
        num_points = 10
        angle_step = 6 * math.pi / num_points
        
        for _ in range(num_points):
            x = center_x + int(max_radius * math.cos(angle))
            y = center_y + int(max_radius * math.sin(angle))
            scaled_radius = 30 * (1 + self.volume / 32768)
            color = self.Rcolor()
            pygame.draw.circle(self.screen, color, (x, y), int(scaled_radius))
            angle += angle_step

    def circular_wave(self, audio_data):
        radius = int(self.volume / 32768 * 2000 + 20)  # Convierte el valor a un entero usando int()
        color = self.Rcolor()
        center = (int(self.center_x), int(self.center_y))  
        pygame.draw.circle(self.screen, color, center, radius)

    def background_color(self, audio_data):
    # Define un umbral para el volumen alto
        high_volume_threshold = 10000  # Ajusta este valor según tus preferencias

        # Cambia el color de fondo si el volumen supera el umbral
        if self.volume > high_volume_threshold:
            color = self.Rcolor()  # Cambia el color como prefieras
        else:
            color = (0, 0, 0)  # Color de fondo predeterminado cuando el volumen no es alto

        self.screen.fill(color)
        
    def bouncy_image(self, audio_data):
        num_logos = 10
        if not hasattr(self, "logos"):
            # Inicializa la lista de logos si aún no existe
            self.logos = []

            for _ in range(num_logos):
                logo = pygame.image.load(self.image_path).convert_alpha()
                logo_width, logo_height = logo.get_width(), logo.get_height()
                x = random.randint(0, self.actual_resolution[0])
                y = random.randint(0, self.actual_resolution[1])
                scale = 0.2 + (self.volume / 32768)
                angle = random.uniform(0, 360)

                # Agrega el logo inicializado a la lista
                self.logos.append({"image": logo, "width": logo_width, "height": logo_height,
                                "x": x, "y": y, "scale": scale, "angle": angle})

        for logo in self.logos:
            # Calcula el desplazamiento basado en la velocidad
            speed = 5  # Puedes ajustar la velocidad según tus preferencias
            dx = speed * math.cos(math.radians(logo["angle"]))
            dy = speed * math.sin(math.radians(logo["angle"]))

            # Mueve el logo
            logo["x"] += dx
            logo["y"] += dy

            # Rebotar en las paredes
            if logo["x"] < 0 or logo["x"] + logo["width"] > self.actual_resolution[0]:
                logo["angle"] = 180 - logo["angle"]
            if logo["y"] < 0 or logo["y"] + logo["height"] > self.actual_resolution[1]:
                logo["angle"] = 360 - logo["angle"]

            # Dibuja el logo
            scaled_logo = pygame.transform.rotozoom(logo["image"], logo["angle"], logo["scale"])
            color = self.Rcolor()
            alpha = 255
            colorized_logo = pygame.Surface(scaled_logo.get_size(), pygame.SRCALPHA)
            colorized_logo.fill((color[0], color[1], color[2], alpha))
            colorized_logo.blit(scaled_logo, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(colorized_logo, (logo["x"], logo["y"]))
                
    def next_effect(self):
        if self.change_mode == "random":
            return random.choice(self.active_effects)
        else:
            current_function_index = self.active_effects.index(self.current_function)
            next_function_index = current_function_index + 1 if current_function_index < len(self.active_effects) - 1 else 0
            return self.active_effects[next_function_index]
         
    def debug_info(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_time
        if elapsed_time > 0:
            current_fps = int(1000 / elapsed_time)
        
        self.last_time = current_time
        current_function_name = self.current_function.get_effect_name() if self.current_function else "None"

        debug_data = {
            "FPS": current_fps,
            "current_function": current_function_name,
            "change_mode": self.change_mode,
            "time_left": int((self.effect_duration - (current_time - self.last_function_change_time)) / 1000),
            "num_particles": self.particle_manager.getNumParticles(),
            "max_amplitude": "NaN",
            "cpu_usage": psutil.cpu_percent(),
            "cpu_temp": self.getCPUTemp(),
            "sensitivity": self.audioManager.sensitivity,
            "volume": self.get_audio_manager().getVolume(),
            "resolution": f"{self.actual_resolution[0]}x{self.actual_resolution[1]}"
        }

        return debug_data
    
    def some_function(self):
        pass

    def getCPUTemp(self):
        # Suponiendo que esta función devuelve la temperatura de la CPU
        return 42.0  # Ejemplo

    
    def onScreenChange(self):
        #Calcula las nuevas posiciones centrales
        self.center_x = self.actual_resolution[0] / 2 
        self.center_y = self.actual_resolution[1] / 2
        
        #Calcula el nuevo tamaño de las partículas
        self.particle_size = self.actual_resolution[0] / 100
        
        #Calcula la nueva velocidad de las partículas
        self.particle_speed = self.actual_resolution[0] / 100
    

    def getCPUTemp(self):
        try:
            tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
            cpu_temp = tempFile.read()
            tempFile.close()
            return float(cpu_temp)/1000
        except:
            return 0
        
def run_visualizer(control_panel):
    visualizer = control_panel.visualizer
    visualizer.start()
        
if __name__ == "__main__":
    control_panel = ControlPanel(Visualizer())
    visualizer_thread = Thread(target=run_visualizer, args=(control_panel,))
    visualizer_thread.start()
    control_panel.root.mainloop()
    