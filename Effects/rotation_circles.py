import random
import math
import pygame
import numpy as np
import colorsys
from Effects.effect import Effect

class RotationCircles(Effect):
    def __init__(self, visualizer):
        super().__init__("Rotation Circles", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()
        self.config_file = "Effects/configs/rotation_circles_config.json"
        self.load_config_from_file(self.config_file)
        self.config = {
            "num_points": 18,
            "max_radius": 260,
            "angle_step": 2 * math.pi / 18,
            "rotation_speed": 0.018
        }
        self.current_angle = 0

    def draw(self, audio_data):
        # Fade para dejar rastro suave
        fade_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, 32))
        self.screen.blit(fade_surface, (0, 0))

        max_radius = self.config["max_radius"]
        num_points = self.config["num_points"]
        self.current_angle += self.config["rotation_speed"]

        # Normaliza el audio para usarlo en los radios y colores
        audio_data = audio_data.astype(np.int32)
        if np.max(np.abs(audio_data)) > 0:
            audio_norm = audio_data / np.max(np.abs(audio_data))
        else:
            audio_norm = np.zeros_like(audio_data)

        for i in range(num_points):
            base_angle = i * self.config["angle_step"]
            angle = self.current_angle + base_angle
            freq_idx = int(i * len(audio_norm) / num_points)
            freq_val = audio_norm[freq_idx]
            # Radio modulado por la frecuencia
            radius = max_radius * (0.7 + 0.3 * abs(freq_val))
            x = self.get_center_x() + radius * math.cos(angle)
            y = self.get_center_y() + radius * math.sin(angle)

            # Color arcoíris animado
            hue = (i / num_points + self.current_angle * 0.12) % 1.0
            sat = 0.8 + 0.2 * abs(freq_val)
            val = 0.8 + 0.2 * abs(freq_val)
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            color = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

            # Glow suave
            for r in range(18, 0, -6):
                alpha = int(60 * (r / 18))
                glow_color = (*color, alpha)
                pygame.draw.circle(self.screen, glow_color, (int(x), int(y)), r)

            # Círculo principal
            circle_radius = int(12 + 18 * abs(freq_val))
            pygame.draw.circle(self.screen, color, (int(x), int(y)), circle_radius)
            
    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()