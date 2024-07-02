import pygame
import math
import time
from Effects.effect import Effect

class FrequencySpectrum(Effect):
    def __init__(self, visualizer):
        super().__init__(
            "Frequency Spectrum",
            visualizer,
            visualizer.get_screen()
        )
        self.screen = visualizer.get_screen()
        self.audio_manager = visualizer.get_audio_manager()
        self.config = {
            "num_bands": 10
        }
        self.config_file = "Effects/configs/frequency_spectrum_config.json"
        self.load_config_from_file(self.config_file)
        self.screen_width = self.screen.get_width()
        self.phase = 0  # Initial phase for wave effect
        
        # Genera los colores basados en el número de bandas actual desde la configuración
        self.colors = [(0, 255 - i * (255 // self.config["num_bands"]), 0) for i in range(self.config["num_bands"])]

    def draw(self, audio_data):
        current_time = time.time() * 2  # Current time factor to modify the phase dynamically
        volume_base = self.audio_manager.getVolume() / 32768 * self.screen.get_height()

        for i in range(self.config["num_bands"]):
            phase_shift = (math.pi * 2) * (i / float(self.config["num_bands"]))
            volume_level = volume_base * (0.5 * math.sin(current_time + phase_shift) + 0.5)  # Sine wave modulation
            x = i * self.screen_width // self.config["num_bands"]
            y = self.screen.get_height() - volume_level
            rect = pygame.Rect(x, y, self.screen_width // self.config["num_bands"], volume_level)
            pygame.draw.rect(self.screen, self.colors[i], rect)

        self.phase += 0.05  # Increment phase
