from StarManager import StarManager
import pygame
from Effects.effect import Effect

class ShootingStars(Effect):
    
    def __init__(self, visualizer):
        super().__init__(
            "Shooting Stars",
            visualizer,
            visualizer.get_screen()
            )
        self.visualizer = visualizer
        self.star_manager = StarManager(
            self.visualizer.get_particle_manager().get_max_particles(),
            self.visualizer.screen, 
            self.width,
            self.height
            )
        
    def draw(self, audio_data):
        self.star_manager.draw_shooting_stars()
        self.star_manager.update_stars()
        self.star_manager.update_gravity_centers()
        
    def on_screen_resize(self, width, height):
        self.star_manager.width = width
        self.star_manager.height = height
        self.star_manager.screen = self.visualizer.get_screen()