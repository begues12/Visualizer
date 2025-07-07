import pygame
import math
import colorsys
from Effects.effect import Effect

class SpinningBarsEffect(Effect):
    def __init__(self, visualizer):
        super().__init__("Spinning Bars", visualizer, visualizer.get_screen())
        self.config = {
            "num_bars": 64,
            "max_bar_height": 320,
            "rotation_speed": 0.035,
            "bar_width": 4
        }
        self.config_file = "Effects/configs/spinning_bars_config.json"
        self.load_config_from_file(self.config_file)
        self.angle = 0

    def draw(self, audio_data):
        audio_data = audio_data.astype("int32")
        center_x, center_y = self.get_center_x(), self.get_center_y()
        angle_step = 2 * math.pi / self.config["num_bars"]

        # Fade para dejar rastro suave
        fade_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, 38))  # Ajusta el alfa para más/menos rastro
        self.screen.blit(fade_surface, (0, 0))

        # Glow radial en el centro
        for r in range(80, 0, -16):
            alpha = int(60 * (r / 80))
            pygame.draw.circle(self.screen, (120, 200, 255, alpha), (int(center_x), int(center_y)), r)

        for i in range(self.config["num_bars"]):
            frequency_index = i * len(audio_data) // self.config["num_bars"]
            bar_height = (audio_data[frequency_index] + 32768) * self.config["max_bar_height"] // 65536
            bar_height = max(10, bar_height)

            angle = self.angle + i * angle_step

            # HSV arcoíris animado
            hue = (i / self.config["num_bars"] + self.angle * 0.12) % 1.0
            sat = 0.85
            val = 1.0
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            color = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

            # Gradiente de color en la barra
            for j in range(8):
                frac = j / 8
                inner_height = bar_height * frac
                x_end = center_x + inner_height * math.cos(angle)
                y_end = center_y + inner_height * math.sin(angle)
                grad_color = (
                    int(color[0] * (1 - frac) + 255 * frac),
                    int(color[1] * (1 - frac) + 255 * frac),
                    int(color[2] * (1 - frac) + 255 * frac)
                )
                width = max(1, int(self.config["bar_width"] * (1 - frac) + 1))
                pygame.draw.line(self.screen, grad_color, (center_x, center_y), (x_end, y_end), width)

            # Glow en la punta de la barra
            tip_x = center_x + bar_height * math.cos(angle)
            tip_y = center_y + bar_height * math.sin(angle)
            pygame.draw.circle(self.screen, color + (120,), (int(tip_x), int(tip_y)), 8)

        self.angle += self.config["rotation_speed"]

    def on_screen_resize(self, new_width, new_height):
        # No necesitas guardar width/height, pero puedes recalcular si dependes de ellos
        self.screen = self.visualizer.get_screen()