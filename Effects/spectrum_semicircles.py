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
            "num_semicircles": 2,
            "max_radius": 150,
            "min_radius": 50,
            "arc_width_multiplier": 10,  # Múltiplo del ancho del arco basado en volumen
            "rotation_speed_multiplier": 0.01  # Múltiplo para la velocidad de rotación
        }
        self.config_file = "Effects/configs/spectrum_semicircles_config.json"
        self.load_config_from_file(self.config_file)
        
    def draw(self, audio_data):
        num_semicircles = self.config["num_semicircles"]
        volume_level = self.audio_manager.getVolume() / 32768  # Pre-calcular esto mejora la eficiencia
        
        angle_increment = volume_level * self.config["rotation_speed_multiplier"]
        current_angle = pygame.time.get_ticks() * angle_increment
        center_x, center_y = self.visualizer.get_screen_center()

        for _ in range(num_semicircles):
            radius = int(random.randint(self.config["min_radius"], self.config["max_radius"]) * (1 + volume_level))
            color = self.random_color()
            start_angle = current_angle % (2 * np.pi)
            end_angle = start_angle + np.pi
            arc_width = int(volume_level * self.config["arc_width_multiplier"])
            
            rect = (center_x - radius, center_y - radius, radius * 2, radius * 2)
            pygame.draw.arc(self.visualizer.screen, color, rect, start_angle, end_angle, arc_width)
