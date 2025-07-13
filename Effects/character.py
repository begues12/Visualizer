import pygame
import math
import numpy as np
from Effects.effect import Effect

class RotatingMandala(Effect):
    def __init__(self, visualizer):
        super().__init__("Rotating Mandala", visualizer, visualizer.get_screen())
        # Cambia la ruta por la de tu imagen mandala
        self.mandala_img = pygame.image.load("assets/mandala.png").convert_alpha()
        self.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        self.angle = 0
        self.last_energy = 0

    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        w, h = screen.get_size()
        self.center = (w // 2, h // 2)

        # Calcula la "energía" de la música (puedes usar volumen, bajos, etc)
        freq_data = self.visualizer.get_audio_manager().get_frequency_data(audio_data)
        bass = np.mean(freq_data[:len(freq_data)//8]) if len(freq_data) > 0 else 0
        volume = min(self.visualizer.get_audio_manager().get_volume(audio_data) / 32768, 1.0)
        energy = 0.7 * bass / 5000 + 0.3 * volume  # Ajusta los pesos y divisores a tu gusto

        # Suaviza la energía para que la rotación sea fluida
        self.last_energy = 0.8 * self.last_energy + 0.2 * energy

        # La velocidad de giro depende de la energía
        self.angle += self.last_energy * 6  # Ajusta el multiplicador para más o menos velocidad

        # Rota la imagen
        rotated = pygame.transform.rotozoom(self.mandala_img, -self.angle, 1)
        rect = rotated.get_rect(center=self.center)
        screen.blit(rotated, rect)

    def on_screen_resize(self, width, height):
        self.center = (width // 2, height // 2)