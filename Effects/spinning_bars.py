import pygame
import math
from Effects.effect import Effect

class SpinningBarsEffect(Effect):
    def __init__(self, visualizer):
        super().__init__("Spinning Bars", visualizer, visualizer.get_screen())
        self.config = {
            "num_bars": 32,
            "max_bar_height": 200,
            "rotation_speed": 0.05,  # Velocidad de rotación en radianes por frame
            "bar_width": 2  # Ancho de las barras en píxeles
        }
        self.config_file = "Effects/configs/spinning_bars_config.json"
        self.load_config_from_file(self.config_file)
        self.angle = 0  # Ángulo inicial de las barras

    def draw(self, audio_data):
        center_x, center_y = self.get_center_x(), self.get_center_y()
        angle_step = 2 * math.pi / self.config["num_bars"]

        for i in range(self.config["num_bars"]):
            frequency_index = i * len(audio_data) // self.config["num_bars"]
            bar_height = (audio_data[frequency_index] + 32768) * self.config["max_bar_height"] // 65536
            
            angle = self.angle + i * angle_step
            x_end = center_x + bar_height * math.cos(angle)
            y_end = center_y + bar_height * math.sin(angle)

            pygame.draw.line(self.screen, self.random_color(), (center_x, center_y), (x_end, y_end), self.config["bar_width"])

        self.angle += self.config["rotation_speed"]  # Actualizar el ángulo para la siguiente frame
        pygame.display.flip()  # Actualizar la pantalla

    def on_screen_resize(self, new_width, new_height):
        super().on_screen_resize(new_width, new_height)  # Actualizar dimensiones si es necesario

