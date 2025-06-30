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

        # Add 3 random gravity centers with different sizes
        for _ in range(3):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            center_size = random.randint(20, 40)  # Cambia estos valores para ajustar el tamaño
            size = random.randint(center_size + 50, center_size + 150)  # Cambia estos valores para ajustar el tamaño
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            self.add_gravity_center(x, y, size, center_size, dx, dy)
    
    def update(self, audio_data, volume):
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

        speed = random.randint(5, 10)
        brightness = random.randint(100, 255)
        size = random.randint(1, 15)

        return {'x': x, 'y': y, 'speed': speed, 'brightness': brightness, 'trail': [], 'size': size, 'angle': angle}

    def add_gravity_center(self, x, y, size, size_center, dx, dy):
        self.gravity_centers.append({'x': x, 'y': y, 'size': size, 'size_center': size_center, 'dx': dx, 'dy': dy})

    def update_gravity_centers(self):
        for center in self.gravity_centers:
            x, y, size, dx, dy = center['x'], center['y'], center['size'], center['dx'], center['dy']

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

            # --- Dibuja el rastro con gradiente y color animado ---
            trail_len = 18  # Rastro más largo y suave
            star['trail'].append((x, y))
            if len(star['trail']) > trail_len:
                star['trail'].pop(0)

            # Cada estrella tiene un desfase de color para que no sean todas iguales
            color_offset = (now * 0.18 + size * 0.07) % 1.0

            for idx, (px, py) in enumerate(star['trail']):
                fade = idx / trail_len
                # El color cambia a lo largo del rastro y con el tiempo
                color = self.tone_to_color(brightness, fade, color_offset)
                alpha = int(255 * (fade * 0.7 + 0.2))  # Más transparente al inicio
                trail_surface = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, color + (alpha,), (size*2, size*2), int(size * (0.7 + fade)))
                self.screen.blit(trail_surface, (px - size*2, py - size*2), special_flags=pygame.BLEND_PREMULTIPLIED)

            # --- Dibuja la estrella principal con halo animado ---
            # El color del núcleo también evoluciona
            core_color = self.tone_to_color(brightness, 1.0, color_offset)
            halo_surface = pygame.Surface((size*7, size*7), pygame.SRCALPHA)
            pygame.draw.circle(halo_surface, (255, 255, 255, 60), (size*3, size*3), int(size*2.8))
            pygame.draw.circle(halo_surface, core_color + (180,), (size*3, size*3), int(size*1.5))
            pygame.draw.circle(halo_surface, (255, 255, 255, 240), (size*3, size*3), int(size*0.8))
            self.screen.blit(halo_surface, (x - size*3, y - size*3), special_flags=pygame.BLEND_PREMULTIPLIED)

            # Movimiento y física igual que antes
            angle = star['angle']
            dx = math.cos(angle) * self.star_speed
            dy = math.sin(angle) * self.star_speed

            for center in self.gravity_centers:
                gx, gy, size = center['x'], center['y'], center['size']
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

    def tone_to_color(self, brightness=255, fade=1.0, color_offset=0.0):
        # Color arcoíris animado: el tono evoluciona con el tiempo y el fade del rastro
        hue = (color_offset + fade * 0.35) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.7 + 0.3 * fade, 0.7 + 0.3 * fade)
        return (int(r * brightness), int(g * brightness), int(b * brightness))

    def update_stars(self):
        if len(self.stars) < self.max_particles:  # Limita la cantidad de estrellas
            self.stars.append(self.create_star())