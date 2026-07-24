import pygame
import os


class CenterImage:
    def __init__(self, image, visualizer, screen, image_name="logo2.png"):
        self.screen = screen
        self.visualizer = visualizer
        self.audio_manager = visualizer.get_audio_manager()

        self.image = image
        self.original_rect = self.image.get_rect()
        self.image_name = image_name

        self.max_scale = 2.0            # potencia de agrandado (cuanto crece con el sonido)
        self.scale_change_speed = 0.12  # velocidad de reaccion (0.02 lento .. 0.5 rapido)
        self.base_size = 1.0            # tamano base de la imagen
        self.image_current_scale = 1.0
        self.center_x, self.center_y = self.visualizer.get_screen_center()

    def draw(self, audio_data):
        target_scale = 1 + (self.max_scale - 1) * self.audio_manager.get_volume(audio_data) / self.audio_manager.max_volume
        self.image_current_scale += (target_scale - self.image_current_scale) * self.scale_change_speed

        total = self.base_size * self.image_current_scale
        new_width = max(1, int(self.original_rect.width * total))
        new_height = max(1, int(self.original_rect.height * total))

        scaled_image = pygame.transform.scale(self.image, (new_width, new_height))
        new_rect = scaled_image.get_rect(center=(self.center_x, self.center_y))
        self.screen.blit(scaled_image, new_rect.topleft)

    def set_image_by_path(self, image_path):
        """Cambia la imagen central conservando su tamano nativo."""
        self.image = pygame.image.load(image_path).convert_alpha()
        self.original_rect = self.image.get_rect()
        self.image_name = os.path.basename(image_path)

    def load_image(self, image_path, width, height):
        # Compatibilidad: carga y escala a un tamano concreto
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(width), int(height)))
        self.original_rect = self.image.get_rect()
        self.image_name = os.path.basename(image_path)

    def set_max_scale(self, value):
        self.max_scale = max(1.0, float(value))

    def set_speed(self, value):
        self.scale_change_speed = max(0.01, min(1.0, float(value)))

    def set_base_size(self, value):
        self.base_size = max(0.05, float(value))

    def recalculate_center(self):
        self.center_x, self.center_y = self.visualizer.get_screen_center()

    def on_screen_resize(self, width, height):
        self.center_x, self.center_y = self.visualizer.get_screen_center()
