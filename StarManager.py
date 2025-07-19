import pygame
import random
import math
from Managers.particle_manager import ParticleManager
import colorsys
import time

class StarManager:
    def __init__(self, max_particles, screen, width, height):
        self.max_particles = 10
        self.stars = []  # Lista para las estrellas
        self.screen = screen
        self.width = int(width)
        self.height = int(height)
        self.gravity_centers = []
        self.gravity_strength = 40  # Fuerza de gravedad (ajusta según sea necesario)
        self.star_speed = 7  # Velocidad constante de las estrellas
        self.particle_manager = ParticleManager(max_particles, screen, width, height)
        
        # Variables para efectos de audio
        self.current_volume = 0
        self.audio_intensity = 0.0
        self.bass_intensity = 0.0
        self.mid_intensity = 0.0
        self.treble_intensity = 0.0

        # Add 3 random gravity centers with different sizes
        for _ in range(3):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            center_size = random.randint(20, 40)  # Cambia estos valores para ajustar el tamaño
            size = random.randint(center_size + 50, center_size + 150)  # Cambia estos valores para ajustar el tamaño
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            self.add_gravity_center(x, y, size, center_size, dx, dy)
    
    def update(self, audio_data, volume, audio_manager=None):
        # Calcular intensidad de sonido para efectos de color
        self.current_volume = volume
        self.audio_intensity = min(1.0, volume / 32768.0) if volume > 0 else 0.0
        
        # Variables para frecuencias específicas
        self.bass_intensity = 0.0
        self.mid_intensity = 0.0
        self.treble_intensity = 0.0
        
        # Obtener datos de frecuencia si está disponible el audio_manager
        if audio_manager:
            freq_data = audio_manager.get_frequency_data(audio_data)
            if len(freq_data) > 0:
                # Dividir el espectro en graves, medios y agudos
                bass_end = len(freq_data) // 6      # Primeros ~17% para graves
                mid_end = len(freq_data) // 2       # Del 17% al 50% para medios
                # El resto (50% - 100%) para agudos
                
                # Calcular energía de graves (20Hz - 250Hz aprox)
                bass_energy = sum(freq_data[:bass_end]) / max(1, bass_end)
                self.bass_intensity = min(1.0, bass_energy / 16384.0)  # Más sensible
                
                # Calcular energía de medios (250Hz - 4kHz aprox)
                mid_energy = sum(freq_data[bass_end:mid_end]) / max(1, mid_end - bass_end)
                self.mid_intensity = min(1.0, mid_energy / 16384.0)  # Más sensible
                
                # Calcular energía de agudos (4kHz+ aprox)
                treble_energy = sum(freq_data[mid_end:]) / max(1, len(freq_data) - mid_end)
                self.treble_intensity = min(1.0, treble_energy / 16384.0)  # Más sensible
            else:
                self.bass_intensity = 0.0
                self.mid_intensity = 0.0
                self.treble_intensity = 0.0
        else:
            self.bass_intensity = 0.0
            self.mid_intensity = 0.0
            self.treble_intensity = 0.0
        
        self.update_stars()
        self.update_gravity_centers()
        self.particle_manager.update_scale(audio_data, volume)
        self.particle_manager.update_particles()
        
        self.draw_shooting_stars()
        self.particle_manager.move_particles(audio_data, volume)
    
    def create_star(self):
        margin = 10
        side = random.randint(0, 3)  # Lado de la pantalla (0-3: arriba, derecha, abajo, izquierda)

        if side == 0:  # Arriba
            x = random.randint(margin, self.width - margin)
            y = margin
        elif side == 1:  # Derecha
            x = self.width - margin
            y = random.randint(margin, self.height - margin)
        elif side == 2:  # Abajo
            x = random.randint(margin, self.width - margin)
            y = self.height - margin
        else:  # Izquierda
            x = margin
            y = random.randint(margin, self.height - margin)

        angle = random.uniform(0, 2 * math.pi)
        if side % 2 == 0:  # Si la estrella está en un lado vertical (arriba o abajo)
            angle += random.uniform(-math.pi / 4, math.pi / 4)  # Ángulo ligeramente inclinado
        else:
            angle += random.uniform(math.pi / 4, 3 * math.pi / 4)  # Ángulo ligeramente inclinado

        speed = random.randint(3, 8)  # Velocidad más variable para movimiento de llamas
        brightness = random.randint(150, 255)  # Brillo más alto para efecto de fuego
        size = random.randint(2, 12)  # Tamaño ajustado para llamas

        return {'x': x, 'y': y, 'speed': speed, 'brightness': brightness, 'trail': [], 'size': size, 'angle': angle}

    def add_gravity_center(self, x, y, size, size_center, dx, dy):
        self.gravity_centers.append({'x': x, 'y': y, 'size': size, 'size_center': size_center, 'dx': dx, 'dy': dy})

    def update_gravity_centers(self):
        for center in self.gravity_centers:
            x, y, _, dx, dy = center['x'], center['y'], center['size'], center['dx'], center['dy']

            # Actualiza la posición de los centros de gravedad
            x += dx
            y += dy

            # Rebote en los bordes de la pantalla
            if x < 0 or x > self.width:
                dx *= -1
            if y < 0 or y > self.height:
                dy *= -1

            center['x'] = x
            center['y'] = y
            center['dx'] = dx
            center['dy'] = dy

    def change_star_direction(self, star, new_angle):
        star['angle'] = new_angle

    def draw_gravity_centers(self):
        for center in self.gravity_centers:
            x, y, size = center['x'], center['y'], center['size']
            pygame.draw.circle(self.screen, self.tone_to_color(), (int(x), int(y)), center['size_center'])
            pygame.draw.circle(self.screen, self.tone_to_color(), (int(x), int(y)), size, 1)

    def draw_flame_trail(self, star, now, brightness, size, trail_len, color_offset):
        """Dibuja el rastro de llamas de una estrella"""
        for idx, (px, py) in enumerate(star['trail']):
            fade = idx / trail_len
            
            # Crear efecto de parpadeo/flicker como fuego real
            flicker = 0.8 + 0.2 * math.sin(now * 8 + idx * 0.3)
            
            # Color de fuego que cambia con el audio
            color = self.get_fire_color(brightness, fade * flicker, color_offset)
            alpha = int(255 * (fade * 0.6 + 0.3) * flicker)  # Alpha con parpadeo
            alpha = max(0, min(255, alpha))  # Validar alpha
            
            # Múltiples capas para efecto de fuego más realista
            flame_size = max(1, int(size * (0.8 + fade * 0.7) * (1 + self.audio_intensity * 0.5)))
            
            # Capa externa (más difusa)
            outer_surface = pygame.Surface((flame_size*6, flame_size*6), pygame.SRCALPHA)
            outer_color = tuple(int(c * 0.6) for c in color)  # Color más tenue
            pygame.draw.circle(outer_surface, outer_color, 
                             (flame_size*3, flame_size*3), flame_size*2)
            outer_surface.set_alpha(alpha//3)
            self.screen.blit(outer_surface, (px - flame_size*3, py - flame_size*3), 
                           special_flags=pygame.BLEND_ADD)
            
            # Capa interna (más intensa)
            inner_surface = pygame.Surface((flame_size*4, flame_size*4), pygame.SRCALPHA)
            pygame.draw.circle(inner_surface, color, 
                             (flame_size*2, flame_size*2), flame_size)
            inner_surface.set_alpha(alpha)
            self.screen.blit(inner_surface, (px - flame_size*2, py - flame_size*2), 
                           special_flags=pygame.BLEND_ADD)
    
    def draw_flame_core(self, x, y, size, brightness, now, color_offset):
        """Dibuja el núcleo central de la llama"""
        # Pulsación basada en el audio
        pulse = 1.0 + self.audio_intensity * 0.3 + 0.1 * math.sin(now * 6)
        
        # Color del núcleo más intenso
        core_color = self.get_fire_color(brightness, 1.0, color_offset)
        
        # Halo exterior (resplandor de la llama)
        halo_size = max(1, int(size * 4 * pulse))
        halo_surface = pygame.Surface((halo_size*2, halo_size*2), pygame.SRCALPHA)
        
        # Gradiente de resplandor (más difuso hacia afuera)
        for i in range(3, 0, -1):
            halo_radius = max(1, int(halo_size * (i * 0.4)))
            halo_color = tuple(max(0, min(255, int(c * (0.5 + i * 0.2)))) for c in core_color)
            
            # Dibujar círculo sin alpha en el color
            pygame.draw.circle(halo_surface, halo_color, 
                             (halo_size, halo_size), halo_radius)
        
        # Aplicar alpha a toda la superficie
        halo_surface.set_alpha(60)
        self.screen.blit(halo_surface, (x - halo_size, y - halo_size), 
                       special_flags=pygame.BLEND_ADD)
        
        # Núcleo central brillante
        core_size = max(1, int(size * 1.2 * pulse))
        core_surface = pygame.Surface((core_size*4, core_size*4), pygame.SRCALPHA)
        
        # Centro blanco-amarillo muy brillante (corazón de la llama)
        white_core = (255, 255, 200) if self.audio_intensity < 0.6 else (200, 230, 255)
        pygame.draw.circle(core_surface, white_core, 
                         (core_size*2, core_size*2), max(1, int(core_size * 0.5)))
        
        # Anillo de color de fuego alrededor
        pygame.draw.circle(core_surface, core_color, 
                         (core_size*2, core_size*2), core_size, 2)
        
        # Aplicar transparencia al núcleo
        core_surface.set_alpha(200)
        self.screen.blit(core_surface, (x - core_size*2, y - core_size*2), 
                       special_flags=pygame.BLEND_ADD)

    def draw_shooting_stars(self):
        new_stars = []

        if self.gravity_centers:
            self.draw_gravity_centers()

        now = pygame.time.get_ticks() / 1000.0  # Tiempo en segundos

        for star in self.stars:
            x = int(star['x'])
            y = int(star['y'])
            brightness = star['brightness']
            size = star['size']

            # --- Actualizar rastro de llamas ---
            trail_len = 25 + int(self.audio_intensity * 15)  # Rastro más largo con sonido alto
            star['trail'].append((x, y))
            if len(star['trail']) > trail_len:
                star['trail'].pop(0)

            # Cada llama tiene un desfase de color para variación
            color_offset = (now * 0.15 + size * 0.05) % 1.0

            # Dibujar rastro de llamas
            self.draw_flame_trail(star, now, brightness, size, trail_len, color_offset)
            
            # Dibujar núcleo de llama
            self.draw_flame_core(x, y, size, brightness, now, color_offset)

            # Movimiento y física
            angle = star['angle']
            dx = math.cos(angle) * self.star_speed
            dy = math.sin(angle) * self.star_speed

            for center in self.gravity_centers:
                gx, gy, _ = center['x'], center['y'], center['size']
                dx_center = gx - x
                dy_center = gy - y
                distance_center = math.sqrt(dx_center ** 2 + dy_center ** 2)
                if distance_center > 0:
                    gravity_direction = math.atan2(dy_center, dx_center)
                    gravity_force = self.gravity_strength / distance_center
                    dx += math.cos(gravity_direction) * gravity_force
                    dy += math.sin(gravity_direction) * gravity_force

            star['x'] += dx
            star['y'] += dy
            self.change_star_direction(star, math.atan2(dy, dx))

            if 0 <= x <= self.width and 0 <= y <= self.height:
                new_stars.append(star)

        self.stars[:] = new_stars

    def get_fire_color(self, brightness=255, fade=1.0, color_offset=0.0):
        """Genera colores de fuego que cambian según graves, medios y agudos"""
        
        # Validar parámetros de entrada
        brightness = max(0, min(255, brightness))
        fade = max(0.0, min(1.0, fade))
        color_offset = max(0.0, color_offset % 1.0)
        
        # Determinar el color base según las frecuencias dominantes
        bass_weight = self.bass_intensity * 2.0      # Graves más prominentes
        mid_weight = self.mid_intensity * 1.5        # Medios moderados
        treble_weight = self.treble_intensity * 1.0  # Agudos normales
        
        total_weight = bass_weight + mid_weight + treble_weight
        
        if total_weight > 0.1:  # Si hay suficiente señal de audio
            # Normalizar pesos
            bass_norm = bass_weight / total_weight
            mid_norm = mid_weight / total_weight
            treble_norm = treble_weight / total_weight
            
            # Colores base para cada frecuencia
            bass_color = (255, 60, 10)    # Rojo-naranja intenso (graves)
            mid_color = (255, 180, 30)    # Amarillo-naranja (medios)
            treble_color = (80, 160, 255) # Azul brillante (agudos)
            
            # Mezclar colores según dominancia
            r = int(bass_color[0] * bass_norm + mid_color[0] * mid_norm + treble_color[0] * treble_norm)
            g = int(bass_color[1] * bass_norm + mid_color[1] * mid_norm + treble_color[1] * treble_norm)
            b = int(bass_color[2] * bass_norm + mid_color[2] * mid_norm + treble_color[2] * treble_norm)
            
            # Intensificar el color según la intensidad total
            intensity_boost = min(1.5, 1.0 + self.audio_intensity)
            r = int(r * intensity_boost)
            g = int(g * intensity_boost)
            b = int(b * intensity_boost)
            
        else:
            # Sin audio significativo: fuego tradicional
            fire_progress = fade * 0.8 + color_offset * 0.2
            
            if fire_progress < 0.3:
                r, g, b = 200, 30, 10    # Rojo profundo
            elif fire_progress < 0.6:
                r, g, b = 255, 100, 20   # Naranja
            else:
                r, g, b = 255, 200, 50   # Amarillo-blanco
        
        # Aplicar brillo y fade
        r = int(r * (brightness / 255.0) * fade)
        g = int(g * (brightness / 255.0) * fade)
        b = int(b * (brightness / 255.0) * fade)
        
        # Asegurar que los valores estén en rango válido [0, 255]
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        return (r, g, b)

    def tone_to_color(self, brightness=255, fade=1.0, color_offset=0.0):
        # Usar el nuevo sistema de colores de fuego
        return self.get_fire_color(brightness, fade, color_offset)

    def update_stars(self):
        if len(self.stars) < self.max_particles:  # Limita la cantidad de estrellas
            self.stars.append(self.create_star())