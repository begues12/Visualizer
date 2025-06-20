import pygame
import numpy as np
import math
import colorsys
from Effects.effect import Effect

class AuroraBars(Effect):
    def __init__(self, visualizer):
        super().__init__("Aurora Bars", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()
        self.config = {
            "num_bars": 64,
            "bar_width": 0,  # Calculado dinámicamente
            "max_bar_height": self.screen.get_height() * 0.8,
            "color_speed": 0.2
        }
        self.config_file = "Effects/configs/aurora_bars_config.json"
        self.load_config_from_file(self.config_file)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        if self.config["bar_width"] <= 0:
            self.config["bar_width"] = self.screen_width // self.config["num_bars"]

    def draw(self, audio_data):
        freq_data = self.audio_manager.get_frequency_data(audio_data)
        num_bars = self.config["num_bars"]
        bar_width = self.config["bar_width"]
        max_bar_height = self.config["max_bar_height"]
        base_y = self.screen_height

        # Normaliza el espectro para que las barras sean proporcionales
        freq_data = freq_data[:num_bars]
        if np.max(freq_data) > 0:
            freq_data = freq_data / np.max(freq_data)
        else:
            freq_data = np.zeros_like(freq_data)

        time_factor = pygame.time.get_ticks() * self.config["color_speed"] / 1000.0

        self.screen.fill((10, 10, 30))  # Fondo oscuro azulado

        for i in range(num_bars):
            bar_height = int(freq_data[i] * max_bar_height)
            # Gradiente de color tipo aurora usando HSV
            hue = (i / num_bars + time_factor) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
            color = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            x = i * bar_width
            y = base_y - bar_height
            pygame.draw.rect(self.screen, color, (x, y, bar_width - 2, bar_height), border_radius=bar_width // 3)