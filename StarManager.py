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

        # Deteccion de golpes para lanzar rafagas de estrellas
        self.energy_history = []
        self.last_beat_time = 0

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
    
    def update_audio(self, audio_data, volume, audio_manager=None):
        """Actualiza intensidades de audio y lanza rafagas de estrellas en los golpes."""
        self.current_volume = volume
        self.audio_intensity = min(1.0, volume / 32768.0) if volume > 0 else 0.0

        self.bass_intensity = self.mid_intensity = self.treble_intensity = 0.0
        if audio_manager:
            freq = audio_manager.get_frequency_data(audio_data)
            if len(freq) > 0:
                bass_end = len(freq) // 6
                mid_end = len(freq) // 2
                self.bass_intensity = min(1.0, sum(freq[:bass_end]) / max(1, bass_end) / 16384.0)
                self.mid_intensity = min(1.0, sum(freq[bass_end:mid_end]) / max(1, mid_end - bass_end) / 16384.0)
                self.treble_intensity = min(1.0, sum(freq[mid_end:]) / max(1, len(freq) - mid_end) / 16384.0)

        # Golpe = energia de graves muy por encima de su media reciente
        self.energy_history.append(self.bass_intensity)
        if len(self.energy_history) > 43:
            self.energy_history.pop(0)
        avg = sum(self.energy_history) / len(self.energy_history)
        now = pygame.time.get_ticks()
        if (self.bass_intensity > avg * 1.4 + 0.05
                and now - self.last_beat_time > 140):
            self.last_beat_time = now
            for _ in range(3 + int(self.audio_intensity * 5)):
                self.stars.append(self.create_star())

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

    def _draw_trail(self, layer, star, now, brightness, size, trail_len, color_offset):
        """Dibuja el rastro de llama de una estrella sobre la capa aditiva."""
        for idx, (px, py) in enumerate(star['trail']):
            fade = (idx + 1) / trail_len
            flicker = 0.85 + 0.15 * math.sin(now * 8 + idx * 0.3)
            color = self.get_fire_color(brightness, fade * flicker, color_offset)
            radius = max(1, int(size * (0.5 + fade * 1.3) * (1 + self.audio_intensity * 0.6)))
            pygame.draw.circle(layer, color, (int(px), int(py)), radius)

    def _draw_core(self, layer, x, y, size, brightness, color_offset):
        """Dibuja el nucleo brillante de la estrella sobre la capa aditiva."""
        core_color = self.get_fire_color(brightness, 1.0, color_offset)
        r = max(2, int(size * (1.0 + self.audio_intensity * 0.6)))
        pygame.draw.circle(layer, tuple(int(c * 0.4) for c in core_color), (x, y), r * 2)
        pygame.draw.circle(layer, core_color, (x, y), r)
        white_core = (255, 255, 220) if self.audio_intensity < 0.6 else (210, 235, 255)
        pygame.draw.circle(layer, white_core, (x, y), max(1, r // 2))

    def draw_shooting_stars(self):
        w, h = self.width, self.height
        # Superficie aditiva reutilizada entre frames (mejor para Raspberry Pi)
        layer = getattr(self, "_layer", None)
        if layer is None or layer.get_size() != (w, h):
            self._layer = pygame.Surface((w, h), pygame.SRCALPHA)
            layer = self._layer
        else:
            layer.fill((0, 0, 0, 0))
        now = pygame.time.get_ticks() / 1000.0
        new_stars = []

        for star in self.stars:
            x = int(star['x'])
            y = int(star['y'])
            brightness = star['brightness']
            size = star['size']

            trail_len = 18 + int(self.audio_intensity * 22)
            star['trail'].append((x, y))
            if len(star['trail']) > trail_len:
                star['trail'].pop(0)
            color_offset = (now * 0.15 + size * 0.05) % 1.0

            self._draw_trail(layer, star, now, brightness, size, len(star['trail']), color_offset)
            self._draw_core(layer, x, y, size, brightness, color_offset)

            # Movimiento: velocidad propia de la estrella + atraccion de gravedad
            angle = star['angle']
            speed = star.get('speed', self.star_speed)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            for center in self.gravity_centers:
                ddx = center['x'] - x
                ddy = center['y'] - y
                dist = math.hypot(ddx, ddy)
                if dist > 0:
                    force = self.gravity_strength / dist
                    gdir = math.atan2(ddy, ddx)
                    dx += math.cos(gdir) * force
                    dy += math.sin(gdir) * force

            star['x'] += dx
            star['y'] += dy
            star['angle'] = math.atan2(dy, dx)

            if -20 <= star['x'] <= w + 20 and -20 <= star['y'] <= h + 20:
                new_stars.append(star)

        self.stars[:] = new_stars
        self.screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

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