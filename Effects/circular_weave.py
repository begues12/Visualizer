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
            "radius": self.screen.get_height(),
            "max_radius": self.screen.get_height()
        }
        self.config_file = "Effects/configs/circular_weave_config.json"
        self.load_config_from_file(self.config_file)
        
        # Asegurar que max_radius existe después de cargar la configuración
        if "max_radius" not in self.config:
            self.config["max_radius"] = self.screen.get_height() // 2
        
        
    def draw(self, audio_data):
        # Obtener volumen normalizado (0.0 a 1.0)
        volume = self.audio_manager.get_volume(audio_data)
        volume_normalized = min(1.0, volume / 32768.0)
        
        # Calcular el radio máximo que ocupe BASTANTE de la pantalla
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        # Usar el 80% de la pantalla para que se vea mucho más grande
        max_screen_radius = int(min(screen_width, screen_height) * 0.8)  # 80% del radio total
        
        # Escalar el radio desde un mínimo hasta el máximo grande
        min_radius = 50  # Radio mínimo más grande para mejor visibilidad
        radius = int(min_radius + (volume_normalized * (max_screen_radius - min_radius)))
        
        # Dibujar círculo que ocupa bastante pantalla y RELLENADO
        color = self.random_color()
        pygame.draw.circle(self.screen, color, (self.center_x, self.center_y), radius)  # Sin grosor = rellenado
        
    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()
        self.config["max_radius"] = height // 2