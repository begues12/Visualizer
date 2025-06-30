import pygame
from Effects.effect import Effect
import os
class CenterImage:
    def __init__(self, image, visualizer, screen):
        self.screen = screen
        self.visualizer = visualizer
        self.audio_manager = visualizer.get_audio_manager()
        
        self.image = image
        self.original_rect = self.image.get_rect()
        
        self.max_scale = 2.0
        self.scale_change_speed = 0.12  # Más suave, ajusta entre 0.08 y 0.25
        self.image_current_scale = 1.0
        self.center_x, self.center_y = self.visualizer.get_screen_center()

    def draw(self, audio_data):
        target_scale = 1 + (self.max_scale - 1) * self.audio_manager.get_volume(audio_data) / self.audio_manager.max_volume
        self.image_current_scale += (target_scale - self.image_current_scale) * self.scale_change_speed
        
        new_width = int(self.original_rect.width * self.image_current_scale)
        new_height = int(self.original_rect.height * self.image_current_scale)

        scaled_image = pygame.transform.scale(self.image, (new_width, new_height))
        new_rect = scaled_image.get_rect(center=(self.center_x, self.center_y))

        self.screen.blit(scaled_image, new_rect.topleft)

    def load_image(self, image_path, width, height):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(width * self.image_current_scale), 
                                                        int(height * self.image_current_scale)))
        self.original_rect = self.image.get_rect()

    def recalculate_center(self):
        self.center_x, self.center_y = self.visualizer.get_screen_center()