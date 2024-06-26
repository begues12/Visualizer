from Effects.effect import Effect
import pygame

class SpectrumWave(Effect):
    
    def __init__(self, visualizer):
        super().__init__(
            "Spectrum Wave", 
            visualizer,
            visualizer.particle_manager
            )
        
        self.config = {
            "line_width": 10,
            "num_points": 8
        }
    
    def draw(self, audio_data):
        line_width = self.config["line_width"]
        num_points = self.config["num_points"]
        points = []

        for i in range(num_points):
            index = i * len(audio_data) // num_points
            x = i * self.visualizer.actual_resolution[0] // num_points
            y = (audio_data[index] + 32768) * self.visualizer.actual_resolution[1] // 65535
            points.append((x, y))

        x = self.visualizer.actual_resolution[0]
        y = (audio_data[-1] + 32768) * self.visualizer.actual_resolution[1] // 65535
        points.append((x, y))

        color = self.random_color()
        for i in range(1, len(points)):
            pygame.draw.line(self.visualizer.screen, color, points[i - 1], points[i], line_width)
