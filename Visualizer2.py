import numpy as np
import pygame
import pyaudio
import os
import random
import math
import colorsys
import pygame.freetype
import psutil
from Particle import ParticleManager
from StarManager import StarManager

class Visualizer:
    
    # Pygame variables
    running = True
    font = None
    font_color = (255, 255, 255)  # Color del texto

    # Pyaudio variables
    p = pyaudio.PyAudio()
    volume = 0
    sensitivity = 1.0
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    # Screen variables
    screen = None
    actual_resolution = (640, 480)
    center_x, center_y = actual_resolution[0] / 2, actual_resolution[1] / 2
    # 10 Types of resolutions 16:9
    resolutions = [ (640, 480), (800, 600), (960, 540), (1024, 576), (1280, 720), (1366, 768), (1600, 900), (1920, 1080), (2560, 1440), (3840, 2160) ]
    fps = 60
    fullscreen = False
    
    # Visualizer variables
    particle_manager = None
    max_particles = 50
    particle_speed = 1
    image_size = 1
    image_current_scale = 1
    current_function = None
    change_mode = "random"
    last_time = 0
    effect_duration = 10000  # Duración de cada efecto en milisegundos
    last_function_change_time = 0
    
    # Image variables
    image_path = os.path.join(os.path.dirname(__file__), "logo.png")
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
        self.clock = pygame.time.Clock()
        self.screen_info = pygame.display.Info()

              
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.actual_resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.actual_resolution)
            
        
        self.actual_resolution = (640, 480)
        self.center_x = self.actual_resolution[0] / 2
        self.center_y = self.actual_resolution[1] / 2

        self.time_to_change_effect = 10 * self.fps
        self.particle_size = self.actual_resolution[0] / 100
        self.particle_speed = self.actual_resolution[0] / 100
        
        #Carga fuente
        self.font =  pygame.freetype.Font(None, 14)
        
        # Carga de la imagen
        self.fire_sign = pygame.image.load(self.image_path).convert_alpha()
        self.fire_sign = pygame.transform.scale(self.fire_sign, (246, 205))
        self.fire_sign_rect = self.fire_sign.get_rect()

         # All drawing functions or classes
        # self.drawing_functions = [
        #                 self.spectrum_wave,
        #                 self.rotation_circles,
        #                 self.background_color,
        #                 self.bouncy_image,
        #                 self.spectrum_semicircles, 
        #                 self.circular_wave, 
        #                 self.frequency_spectrum,
        #                 self.shooting_stars,
        #                 ]
        
        self.drawing_functions = [self.shooting_stars]
        
        self.chargeParticles()
        self.current_function = random.choice(self.drawing_functions)
    
    def chargeParticles(self):
        self.particle_manager = ParticleManager(self.max_particles, self.screen, self.actual_resolution[0], self.actual_resolution[1])
        self.star_manager = StarManager(10, self.screen, self.actual_resolution[0], self.actual_resolution[1])
        
    def start(self):
        while self.running:
            
            self.hotkeys()
                        
            audio_data = np.frombuffer(self.stream.read(self.CHUNK), dtype=np.int16)
            self.volume = max(abs(audio_data.min()), abs(audio_data.max())) * self.sensitivity
            
            self.screen.fill((0,0,0))
            self.current_function(audio_data)  # Ejecuta la función actual
            
            if pygame.time.get_ticks() - self.last_function_change_time >= self.effect_duration and self.change_mode != "static":
                self.current_function = self.next_effect()
                self.last_function_change_time = pygame.time.get_ticks()
            
            # Calcula el volumen máximo de la señal de audio
            
            self.draw_center_image(audio_data)

            # Particles
            self.particle_manager.move_particles(audio_data, self.volume)
            self.particle_manager.update_particles()
            self.particle_manager.update_scale(audio_data, self.volume)
            
            # Dibuja el texto de depuración en la esquina inferior derecha si el modo de depuración está activado
            if self.debug_mode:
                self.debug()
            
            pygame.display.flip()
            
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        pygame.quit()

    def draw_center_image(self, audio_data):

        scale_change_speed = 0.5  # Ajusta la velocidad según desees
        max_volume = 32768  # Valor máximo de volumen
        max_scale = 2.0  # Escala máxima de la imagen (ajusta según desees)
        target_scale = 1 + (max_scale - 1) * self.volume / max_volume
        
        # Interpola suavemente entre el tamaño actual y el tamaño objetivo
        self.image_current_scale += (target_scale - self.image_current_scale) * scale_change_speed
        
        # Escala la imagen según el tamaño actual
        scaled_fire_sign = pygame.transform.scale(
            self.fire_sign, 
            (int(self.fire_sign_rect.width * self.image_current_scale), 
             int(self.fire_sign_rect.height * self.image_current_scale))
            )

        # Dibuja la imagen en el centro de la pantalla
        self.screen.blit(scaled_fire_sign, (self.center_x - scaled_fire_sign.get_rect().width / 2, self.center_y - scaled_fire_sign.get_rect().height / 2))        

    def spectrum_wave(self, audio_data):
        line_width = 10
        num_points = 8
        points = []

        for i in range(num_points):
            index = i * len(audio_data) // num_points
            x = i * self.actual_resolution[0] // num_points
            y = (audio_data[index] + 32768) * self.actual_resolution[1] // 65535
            points.append((x, y))
            
        # And the last line between the last point and the final of screen
        x = self.actual_resolution[0]
        y = (audio_data[-1] + 32768) * self.actual_resolution[1] // 65535
        points.append((x, y))

        color = self.Rcolor()
        for i in range(1, len(points)):
            pygame.draw.line(self.screen, color, points[i - 1], points[i], line_width)
    
    def spectrum_semicircles(self, audio_data):
        
        num_semicircles = 2

        for i in range(num_semicircles):

            rotation_speed = self.volume / 32768
            angle = pygame.time.get_ticks() * rotation_speed
            radius = int(random.randint(50, 150) * (1 + self.volume / 32768))

            color = self.Rcolor()

            start_angle = angle % (2 * np.pi)
            end_angle = start_angle + np.pi

            # Calculate the width of the arc based on the volume
            arc_width = int(self.volume / 32768 * 10)  # You can adjust the multiplier as needed

            pygame.draw.arc(self.screen, color, (self.center_x - radius, self.center_y - radius, radius * 2, radius * 2), start_angle, end_angle, arc_width)
    
    def shooting_stars(self, audio_data):
        self.star_manager.draw_shooting_stars()
        self.star_manager.update_stars()
    
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
            return random.choice(self.drawing_functions)
        else:
            # Calcula el índice de la función actual y recoge la siguiente función o la primera si es la última
            current_function_index = self.drawing_functions.index(self.current_function)
            next_function_index = current_function_index + 1 if current_function_index < len(self.drawing_functions) - 1 else 0
            return self.drawing_functions[next_function_index]
         
    def debug(self):
        current_time = pygame.time.get_ticks()
        
        elapsed_time = current_time - self.last_time
        if elapsed_time > 0:
            current_fps = int(1000 / elapsed_time)
        
        self.last_time = current_time

        current_fps = int(1000 / elapsed_time)
        
        current_function_name = self.current_function.__name__
        
        # Dibuja el texto de depuración en la esquina inferior derecha
        fps_text = f"FPS: {current_fps}"
        self.font.render_to(self.screen, (10, self.actual_resolution[1] - 40), fps_text, self.font_color)

        # Dibuja las resoluciones disponibles y la resolución actual en la esquina inferior izquierda
        current_resolution_text = f"Resolución actual: {self.actual_resolution[0]}x{self.actual_resolution[1]}"
        self.font.render_to(self.screen, (10, self.actual_resolution[1] - 70), current_resolution_text, self.font_color)
        
        # Dibuja el nombre de la función actual en la esquina superior izquierda
        current_function_text = f"Función actual: {current_function_name}"
        self.font.render_to(self.screen, (10, 10), current_function_text, self.font_color)
        
        # Dibuja el modo de cambio de efecto actual en la esquina superior derecha
        change_mode_text = f"Modo de cambio de efecto: {self.change_mode}"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, 10), change_mode_text, self.font_color)
        
        #Dibuja el tiempo que queda para que cambie el siguiente efecto
        time_left_text = f"Tiempo restante: {int((self.effect_duration - (current_time - self.last_function_change_time)) / 1000)}s"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, 40), time_left_text, self.font_color)
        
        # Dibuja el número de partículas en la esquina inferior izquierda
        num_particles_text = f"Número de partículas: "
        self.font.render_to(self.screen, (10, self.actual_resolution[1] - 100), num_particles_text + str(self.particle_manager.getNumParticles()) , self.font_color)
        
        # Dibuja la amplitud máxima en la esquina inferior izquierda
        max_amplitude_text = f"Amplitud máxima: NaN"
        self.font.render_to(self.screen, (10, self.actual_resolution[1] - 130), max_amplitude_text, self.font_color)
        
        #Dibuja el uso de la CPU y la temperatura en la esquina inferior izquierda
        cpu_usage_text = f"Uso de la CPU: {psutil.cpu_percent()}%"
        self.font.render_to(self.screen, (10, self.actual_resolution[1] - 160), cpu_usage_text, self.font_color)
        
        cpu_temp_text = f"Temperatura de la CPU: "
        self.font.render_to(self.screen, (10, self.actual_resolution[1] - 190), cpu_temp_text + str(self.getCPUTemp()) + "ºC", self.font_color)
        
        self.font.render_to(self.screen, (10, self.actual_resolution[1] - 220), "Sensibilidad: " + str(self.sensitivity), self.font_color)
        
        self.font.render_to(self.screen, (10, self.actual_resolution[1] - 250), "Volumen: " + str(self.volume), self.font_color)
        
        margin = 20
        margin_height = 20
        # In right corner show de hot keys
        ctrlP_text = "Ctrl+P: Cambiar entre pantalla completa y ventana"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, self.actual_resolution[1] - margin), ctrlP_text, self.font_color)
        
        margin += margin_height
        
        ctrlR_text = "Ctrl+R: Cambiar el modo de cambio de efecto"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, self.actual_resolution[1] - margin), ctrlR_text, self.font_color)
        
        margin += margin_height
        
        ctrlS_text = "Ctrl+S: Cambiar al siguiente efecto"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, self.actual_resolution[1] - margin), ctrlS_text, self.font_color)
        
        margin += margin_height
        
        ctrlD_text = "Ctrl+D: Activar/desactivar el modo de depuración"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, self.actual_resolution[1] - margin), ctrlD_text, self.font_color)
        
        margin += margin_height
        
        CtrlE_text = "Ctrl+E: Cambiar la resolución +"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, self.actual_resolution[1] - margin), CtrlE_text, self.font_color)
        
        margin += margin_height
        
        CtrlW_text = "Ctrl+W: Cambiar la resolución -"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, self.actual_resolution[1] - margin), CtrlW_text, self.font_color)        
        
        margin += margin_height
        
        CtrlPlus_text = "Ctrl++: Aumentar la sensibilidad"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, self.actual_resolution[1] - margin), CtrlPlus_text, self.font_color)
        
        margin += margin_height
        
        CtrlMinus_text = "Ctrl+-: Disminuir la sensibilidad"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, self.actual_resolution[1] - margin), CtrlMinus_text, self.font_color)
        
        margin += margin_height
        
        ctrlQ_text = "Ctrl+Q: Salir"
        self.font.render_to(self.screen, (self.actual_resolution[0] - 400, self.actual_resolution[1] - margin), ctrlQ_text, self.font_color)
        
    def hotkeys(self):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.running = False
                elif event.key == pygame.K_p and pygame.key.get_mods() & pygame.KMOD_CTRL:

                    self.fullscreen = not self.fullscreen
                    
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(self.actual_resolution, pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode(self.actual_resolution)
                        
                    self.onScreenChange()
                    
                elif event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if self.debug_mode:
                        self.debug_mode = False
                    else:
                        self.debug_mode = True
                    
                # Verificar si se presiona Ctrl+R para cambiar el modo de cambio de efecto
                elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Modes random, sequential and static
                    if self.change_mode == "random":
                        self.change_mode = "sequential"
                    elif self.change_mode == "sequential":
                        self.change_mode = "static"
                    else:
                        self.change_mode = "random"

                # Verificar si se presiona Ctrl+S para cambiar al siguiente efecto
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if self.change_mode == "random":
                        self.change_mode = "sequential"
                       
                    self.current_function = self.next_effect()
                    self.last_function_change_time = pygame.time.get_ticks()
                    
                #Cambiar la resolucion a la siguiente
                elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.actual_resolution = self.resolutions[(self.resolutions.index(self.actual_resolution) + 1) % len(self.resolutions)]
                    
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(self.actual_resolution, pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode(self.actual_resolution)
                        
                    self.onScreenChange()
                    self.chargeParticles()
                
                elif event.key == pygame.K_w and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.actual_resolution = self.resolutions[(self.resolutions.index(self.actual_resolution) - 1) % len(self.resolutions)]
                    
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(self.actual_resolution, pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode(self.actual_resolution)
                    
                    self.onScreenChange()
                    self.chargeParticles()
                #Cambiar la sensibilidad
                elif event.key == pygame.K_PLUS and pygame.key.get_mods() & pygame.KMOD_CTRL and float(self.sensitivity) < 3.0:
                    self.sensitivity += 0.1
                elif event.key == pygame.K_MINUS and pygame.key.get_mods() & pygame.KMOD_CTRL and float(self.sensitivity) > 0.1:
                    self.sensitivity -= 0.1
               
    def onScreenChange(self):
        #Calcula las nuevas posiciones centrales
        self.center_x = self.actual_resolution[0] / 2 
        self.center_y = self.actual_resolution[1] / 2
        
        #Calcula el nuevo tamaño de las partículas
        self.particle_size = self.actual_resolution[0] / 100
        
        #Calcula la nueva velocidad de las partículas
        self.particle_speed = self.actual_resolution[0] / 100
    
    def Rcolor(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    def getCPUTemp(self):
        try:
            tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
            cpu_temp = tempFile.read()
            tempFile.close()
            return float(cpu_temp)/1000
        except:
            return 0
        
visualizer = Visualizer()
visualizer.start()