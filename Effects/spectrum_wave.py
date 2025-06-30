from Effects.effect import Effect
import pygame
import numpy as np

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
        audio_data = audio_data.astype(np.int32)
        line_width = self.config["line_width"]
        num_points = self.config["num_points"]
        points = []

        # Parámetros para la onda sinusoidal
        amplitude = self.get_height() * 0.08  # Puedes ajustar la amplitud
        frequency = 2 * np.pi / num_points    # 1 ciclo completo a lo largo de la línea
        phase = pygame.time.get_ticks() * 0.002  # Animación suave

        for i in range(num_points):
            index = i * len(audio_data) // num_points
            x = i * self.get_width() // num_points
            # Onda de audio normalizada como antes
            y_audio = ((audio_data[index] + 32768) * self.get_height()) // 65536
            # Suma la modulación sinusoidal
            y = int(y_audio + amplitude * np.sin(frequency * i + phase))
            points.append((x, y))

        # Último punto al final de la pantalla
        x = self.get_width()
        y_audio = ((audio_data[index] + 32768) * self.get_height()) // 65536
        y = int(y_audio + amplitude * np.sin(frequency * num_points + phase))
        points.append((x, y))

        color = self.random_color()
        for i in range(1, len(points)):
            pygame.draw.line(self.visualizer.screen, color, points[i - 1], points[i], line_width)
