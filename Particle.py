import pygame
import random
import math

class ParticleManager:
    def __init__(self, max_particles, screen, width, height):
        self.max_particles = max_particles
        self.particles = []
        self.screen = screen
        self.width = width
        self.height = height
        self.current_scale = 1.0  # Inicializa current_scale

    def create_particle(self, x, y, vx, vy):
        return {
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'color': self.tone_to_color(),
        }

    def tone_to_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def move_particles(self, audio_data, volume):
        particles_to_remove = []

        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            amplitude = volume
            particle['color'] = self.tone_to_color()

            # Verifica si la partícula está fuera de los límites de la pantalla
            if (
                particle['x'] < 0
                or particle['x'] > self.width
                or particle['y'] < 0
                or particle['y'] > self.height
            ):
                particles_to_remove.append(particle)
            else:
                # Dibuja la partícula solo si está dentro de los límites
                pygame.draw.circle(self.screen, particle['color'], (int(particle['x']), int(particle['y'])), int(amplitude / 32768 * 3 * self.current_scale) + random.randint(1, 2))

        # Elimina las partículas que están fuera de los límites
        for particle in particles_to_remove:
            self.particles.remove(particle)

    def update_particles(self, max_particles=40):
        if len(self.particles) < max_particles:  # Limita la cantidad de partículas
            for _ in range(5):  # Crea nuevas partículas de forma periódica (menos partículas)
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                self.particles.append(self.create_particle(x, y, random.uniform(-2, 2), random.uniform(-2, 2)))

    def update_scale(self, audio_data, volume):
        # Define una velocidad de cambio de escala
        scale_change_speed = 0.5  # Ajusta la velocidad según desees

        # Escala objetivo basada en el volumen del audio
        max_volume = 32768  # Valor máximo de volumen
        max_scale = 1.5  # Escala máxima de la imagen (ajusta según desees)
        target_scale = 1 + (max_scale - 1) * (volume / max_volume)

        # Interpola suavemente entre el tamaño actual y el tamaño objetivo
        self.current_scale += (target_scale - self.current_scale) * scale_change_speed

    def getNumParticles(self):
        return len(self.particles)