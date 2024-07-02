from Effects.effect import Effect
import pygame

class SpectrumWave(Effect):
    
    def __init__(self, visualizer):
        super().__init__(
            "Spectrum Wave", 
            visualizer,
            visualizer.get_screen()
            )
        
        self.config = {
            "line_width": 10,
            "num_points": 8
        }
        self.config_file = "Effects/configs/spectrum_wave_config.json"
        self.load_config_from_file(self.config_file)
    
    def draw(self, audio_data):
        line_width = self.config["line_width"]
        num_points = self.config["num_points"]
        points = []

        for i in range(num_points):
            index = i * len(audio_data) // num_points
            x = i * self.get_width() // num_points
            y = (audio_data[index] + 32768) * self.get_height() // 65535
            points.append((x, y))

        x = self.get_width()
        y = (audio_data[-1] + 32768) * self.get_height() // 65535
        points.append((x, y))

        color = self.random_color()
        for i in range(1, len(points)):
            pygame.draw.line(self.visualizer.screen, color, points[i - 1], points[i], line_width)
