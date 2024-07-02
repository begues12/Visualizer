import pygame
import math
from Effects.effect import Effect

class InteractiveLinesEffect(Effect):
    def __init__(self, visualizer):
        super().__init__("Interactive Lines", visualizer, visualizer.get_screen())
        self.config = {
            "num_lines": 50,  # Número de líneas
            "line_width": 2,  # Grosor de las líneas
            "max_length": 300,  # Longitud máxima de las líneas
            "color_variation_speed": 5  # Velocidad a la que cambia el color
        }
        self.config_file = "Effects/configs/interactive_lines_config.json"
        self.load_config_from_file(self.config_file)
        self.line_angles = [i * (2 * math.pi / self.config["num_lines"]) for i in range(self.config["num_lines"])]  # Ángulos para las líneas

    def draw(self, audio_data):
        center_x, center_y = self.get_center_x(), self.get_center_y()
        self.screen.fill((0, 0, 0))  # Limpiar pantalla
        
        # Calcular datos de frecuencia si está disponible
        freq_data = self.audio_manager.get_frequency_data() if hasattr(self.audio_manager, 'get_frequency_data') else audio_data
        
        for i, angle in enumerate(self.line_angles):
            length = min(self.config["max_length"], (freq_data[i % len(freq_data)] / 255.0) * self.config["max_length"])
            end_x = center_x + length * math.cos(angle)
            end_y = center_y + length * math.sin(angle)
            color = (255, i * self.config["color_variation_speed"] % 255, 255 - (i * self.config["color_variation_speed"] % 255))
            pygame.draw.line(self.screen, color, (center_x, center_y), (end_x, end_y), self.config["line_width"])

        pygame.display.flip()  # Actualizar la pantalla

