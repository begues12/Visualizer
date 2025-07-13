import pygame
import numpy as np
import math
from Effects.effect import Effect

class FrequencySpectrum(Effect):
    def __init__(self, visualizer):
        super().__init__(
            "Aggressive Spectrum",
            visualizer,
            visualizer.get_screen()
        )
        self.screen = visualizer.get_screen()
        self.audio_manager = visualizer.get_audio_manager()
        self.config = {
            "num_bands": 48
        }
        self.config_file = "Effects/configs/frequency_spectrum_config.json"
        self.load_config_from_file(self.config_file)
        self.last_heights = np.zeros(self.config["num_bands"])
        self.phase = 0

    def draw(self, audio_data):
        freq_data = self.audio_manager.get_frequency_data(audio_data)
        bands = self.config["num_bands"]
        w, h = self.screen.get_size()
        band_width = w // bands
        max_height = h * 0.92

        # Agrupa el espectro en bandas y normaliza
        band_vals = np.zeros(bands)
        if len(freq_data) > 0:
            band_size = max(1, len(freq_data) // bands)
            for i in range(bands):
                start = i * band_size
                end = start + band_size
                band_vals[i] = np.mean(freq_data[start:end])
            band_vals = band_vals / (np.max(band_vals) + 1e-6)

        # Fondo negro puro para contraste agresivo
        self.screen.fill((0, 0, 0))

        # Efecto: barras "pico" con bordes dentados y flashes rojos
        for i in range(bands):
            # Altura agresiva y animación de "temblor"
            target = band_vals[i] * max_height
            self.last_heights[i] = 0.5 * self.last_heights[i] + 0.5 * target
            bar_height = self.last_heights[i] + np.random.randint(-6, 6)
            x = i * band_width
            y = h - bar_height

            # Color: rojo intenso si la barra es alta, amarillo si media, blanco si baja
            if bar_height > h * 0.7:
                color = (255, 30 + np.random.randint(0, 80), 30 + np.random.randint(0, 40))
            elif bar_height > h * 0.4:
                color = (255, 200, 40)
            else:
                color = (220, 220, 220)

            # Dibuja barra dentada (zigzag)
            points = []
            steps = max(6, int(bar_height // 12))
            for s in range(steps + 1):
                px = x + band_width // 2 + int((band_width // 2) * math.sin(s + self.phase + i))
                py = int(h - (bar_height * s / steps) + np.random.randint(-2, 2))
                points.append((px, py))
            # Base de la barra
            points.append((x + band_width, h))
            points.append((x, h))
            pygame.draw.polygon(self.screen, color, points)

            # Flash blanco en la cima si la barra es muy alta
            if bar_height > h * 0.8:
                pygame.draw.circle(self.screen, (255, 255, 255), (x + band_width // 2, int(y)), band_width // 3)

        # Efecto de "onda" roja agresiva en la base
        for i in range(0, w, 8):
            offset = int(8 * math.sin(self.phase + i * 0.04))
            pygame.draw.line(self.screen, (255, 0, 0), (i, h - 2 + offset), (i + 8, h - 2 + offset), 3)

        self.phase += 0.18

    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()
        self.last_heights = np.zeros(self.config["num_bands"])