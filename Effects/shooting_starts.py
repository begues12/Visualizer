from StarManager import StarManager
import pygame

class ShootingStars:
    
    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.star_manager = StarManager(
            self.visualizer.particle_manager.max_particles, 
            self.visualizer.screen, 
            self.visualizer.actual_resolution[0], 
            self.visualizer.actual_resolution[1]
            )
        
    def draw(self, audio_data):
        self.star_manager.draw_shooting_stars()
        self.star_manager.update_stars()
        self.star_manager.update_gravity_centers()