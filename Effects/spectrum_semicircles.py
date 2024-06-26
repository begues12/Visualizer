from Effects.effect import Effect
import pygame
import numpy as np
import random

class SpectrumSemicircles(Effect):
    
    def __init__(self, visualizer):
        super().__init__(
            "Spectrum Semicircles",
            visualizer,
            visualizer.particle_manager
            )
        self.audio_manager = visualizer.get_audio_manager()
        self.config = {
            "num_semicircles": 2
        }
        
    def draw(self, audio_data):
        
        num_semicircles = 2

        for i in range(num_semicircles):

            rotation_speed = self.audio_manager.getVolume() / 32768 * 0.01
            angle = pygame.time.get_ticks() * rotation_speed
            radius = int(random.randint(50, 150) * (1 + self.audio_manager.getVolume() / 32768))

            color = self.random_color()

            start_angle = angle % (2 * np.pi)
            end_angle = start_angle + np.pi

            # Calculate the width of the arc based on the volume
            arc_width = int(self.audio_manager.getVolume() / 32768 * 10)  # You can adjust the multiplier as needed
            center_x, center_y = self.visualizer.get_screen_center()
            pygame.draw.arc(self.visualizer.screen, color, (center_x - radius, center_y - radius, radius * 2, radius * 2), start_angle, end_angle, arc_width)