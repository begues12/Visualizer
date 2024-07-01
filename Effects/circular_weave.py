from Effects.effect import Effect
import pygame
import numpy as np
import random

class CircularWeave(Effect):
    
    def __init__(self, visualizer):
        super().__init__(
            "Spectrum Semicircles",
            visualizer,
            visualizer.particle_manager
        )
        
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()
        self.config = {
            "radius": 150,
        }
        self.config_file = "Effects/configs/circular_weave_config.json"
        self.load_config_from_file(self.config_file)
        
        
    def draw(self, audio_data):
        radius = int(self.audio_manager.getVolume() / 32768 * self.config["radius"])
        color = self.random_color()
        center = (int(self.screen.get_width() / 2), int(self.screen.get_height() / 2))
        pygame.draw.ellipse(self.screen, (23, 23, 23), (center[0] - radius, center[1] - radius, radius * 2, radius * 2), 1)