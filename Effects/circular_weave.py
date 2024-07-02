from Effects.effect import Effect
import pygame
import numpy as np
import random

class CircularWeave(Effect):
    
    def __init__(self, visualizer):
        super().__init__(
            "Circular Weave",
            visualizer,
            visualizer.get_screen()
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
        pygame.draw.ellipse(self.screen, color, (self.center_x - radius, self.center_y - radius, radius * 2, radius * 2))