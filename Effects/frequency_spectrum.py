from Effects.effect import Effect
import pygame
import numpy as np
import random

class FrequencySpectrum(Effect):
    def __init__(self, visualizer):
        super().__init__(
            "Frequency Spectrum",
            visualizer,
            visualizer.particle_manager
            )
        self.screen = visualizer.get_screen()
        self.audio_manager = visualizer.get_audio_manager()
        self.config = {
            "num_semicircles": 2,
            "max_radius": 150,
            "min_radius": 50,
            "arc_width": 10,   
        }
        self.config_file = "Effects/configs/frequency_spectrum_config.json"
        self.load_config_from_file(self.config_file)
        
    def draw(self, audio_data):
        
        num_bands = 10
        band_height = self.screen.get_height() // num_bands

        for i in reversed(range(num_bands)):  # Invierte el orden del bucle
            color = self.set_index_color(i)
            y = self.screen.get_height() - band_height * i
            rect = pygame.Rect(0, y, int(self.audio_manager.getVolume() / 32768 * self.screen.get_width()), band_height)