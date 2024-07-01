import pygame
import random
import math
from Managers.particle_manager import ParticleManager

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
        new_stars = []  # Lista para almacenar las estrellas que permanecen en la pantalla

        # Dibuja las bolas de gravedad si los puntos de gravedad están definidos
        if self.gravity_centers:
            self.draw_gravity_centers()

        for star in self.stars:
            x = int(star['x'])
            y = int(star['y'])
            brightness = star['brightness']
            size = star['size']

            # Dibuja el rastro de estrellas
            i = 0.7
            for point in star['trail']:
                px, py, color = point
                pygame.draw.circle(self.screen, self.tone_to_color(), (px, py), int(size * i))
                i += .2
            # Dibuja la estrella actual
            pygame.draw.circle(self.screen, self.tone_to_color(), (int(x), int(y)), int(size * i))

            # Agrega la posición actual al rastro
            star['trail'].append((x, y, self.tone_to_color()))

            # Limita la longitud del rastro
            if len(star['trail']) > 3:
                star['trail'].pop(0)

            # Calcula el desplazamiento en función del ángulo
            angle = star['angle']
            dx = math.cos(angle) * self.star_speed
            dy = math.sin(angle) * self.star_speed

            # Aplica la gravedad si hay puntos de gravedad definidos
            for center in self.gravity_centers:
                gx, gy, size = center['x'], center['y'], center['size']
                dx_center = gx - x
                dy_center = gy - y
                distance_center = math.sqrt(dx_center ** 2 + dy_center ** 2)

                # Evitar la división por cero
                if distance_center > 0:
                    gravity_direction = math.atan2(dy_center, dx_center)
                    gravity_force = self.gravity_strength / distance_center
                    dx += math.cos(gravity_direction) * gravity_force
                    dy += math.sin(gravity_direction) * gravity_force

            star['x'] += dx
            star['y'] += dy
            self.change_star_direction(star, math.atan2(dy, dx))

            # Si la estrella sigue en la pantalla, guárdala en la lista de estrellas que permanecen
            if 0 <= x <= self.width and 0 <= y <= self.height:
                new_stars.append(star)

        # Reemplaza la lista de estrellas con las que permanecen en la pantalla
        self.stars[:] = new_stars

    def update_stars(self):
        if len(self.stars) < self.max_particles:  # Limita la cantidad de estrellas
            self.stars.append(self.create_star())

    def tone_to_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
