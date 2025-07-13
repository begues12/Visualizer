import random
import math
import pygame
import numpy as np
import colorsys
from Effects.effect import Effect

class RotationCircles(Effect):
    def __init__(self, visualizer):
        super().__init__("Techno Pulse", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()
        self.config_file = "Effects/configs/rotation_circles_config.json"
        self.load_config_from_file(self.config_file)
        self.config = {
            "num_rays": 32,
            "num_rings": 4,
            "max_radius": self.screen.get_height() // 2 - 60,
            "rotation_speed": 0.045
        }
        self.current_angle = 0

    def draw(self, audio_data):
        # Fondo negro puro para contraste techno
        self.screen.fill((0, 0, 0))

        max_radius = self.config["max_radius"]
        num_rays = self.config["num_rays"]
        num_rings = self.config["num_rings"]
        self.current_angle += self.config["rotation_speed"]

        # FFT para energía por banda
        freq_data = self.audio_manager.get_frequency_data(audio_data)
        if len(freq_data) == 0:
            freq_data = np.zeros(512)
        bands = np.array_split(freq_data[:num_rays * num_rings], num_rings)
        band_energies = [np.mean(b) for b in bands]
        global_energy = np.mean(freq_data[:len(freq_data)//6]) / 4000  # Bass para el pulso

        # Pulso central (baila con el bass)
        pulse_radius = int(60 + 80 * min(1.0, global_energy))
        pulse_alpha = min(255, 120 + int(120 * global_energy))
        pygame.draw.circle(self.screen, (255, 0, 80, pulse_alpha), (self.get_center_x(), self.get_center_y()), pulse_radius)
        pygame.draw.circle(self.screen, (255, 255, 255, 80), (self.get_center_x(), self.get_center_y()), pulse_radius // 2)

        # RAYOS: líneas que giran y vibran con la música
        for i in range(num_rays):
            angle = self.current_angle + 2 * math.pi * i / num_rays
            for ring in range(1, num_rings + 1):
                # Energía de la banda para este anillo
                idx = (ring - 1) * num_rays + i
                if idx < len(freq_data):
                    energy = min(1.0, freq_data[idx] / (np.max(freq_data) + 1e-6))
                else:
                    energy = 0.0
                # Longitud y color vibran con la energía
                length = int((max_radius / num_rings) * ring * (0.7 + 0.7 * energy))
                x1 = self.get_center_x() + int((max_radius / num_rings) * (ring - 1) * math.cos(angle))
                y1 = self.get_center_y() + int((max_radius / num_rings) * (ring - 1) * math.sin(angle))
                x2 = self.get_center_x() + int(length * math.cos(angle + 0.08 * math.sin(self.current_angle * 2 + i)))
                y2 = self.get_center_y() + int(length * math.sin(angle + 0.08 * math.sin(self.current_angle * 2 + i)))
                hue = (angle / (2 * math.pi) + self.current_angle * 0.2) % 1.0
                color = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                color = (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                width = int(2 + 6 * energy)
                pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width)

        # FLASH: destello blanco cuando el bass es muy alto
        if global_energy > 0.38:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, int(80 * min(1.0, global_energy))))
            self.screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()