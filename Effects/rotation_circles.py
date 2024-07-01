import random
import math
import pygame
import numpy as np
from Effects.effect import Effect

class RotationCircles(Effect):
    
    def __init__(self, visualizer):
        super().__init__("Rotation Circles", visualizer, visualizer.particle_manager)
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()
        self.width, self.height = self.screen.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2

        
        self.config_file = "Effects/configs/rotation_circles_config.json"
        self.load_config_from_file(self.config_file)
        self.config = {
            "num_points": 10,
            "max_radius": 250,
            "angle_step": 6 * math.pi / 10,
            "rotation_speed": 0.01
        }
        self.current_angle = 0
        self.angles = [i * self.config["angle_step"] for i in range(self.config["num_points"])]
        self.colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(self.config["num_points"])]
        
    def draw(self, audio_data):
        max_radius = self.config["max_radius"]
        volume_scale = 30 * (1 + self.audio_manager.getVolume() / 32768)
        self.current_angle += self.config["rotation_speed"]

        for i, base_angle in enumerate(self.angles):
            angle = self.current_angle + base_angle
            x = self.center_x + max_radius * math.cos(angle)
            y = self.center_y + max_radius * math.sin(angle)
            pygame.draw.circle(self.screen, self.colors[i], (int(x), int(y)), int(volume_scale))
