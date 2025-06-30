from Effects.effect import Effect
import pygame
import numpy as np
import colorsys

class SpectrumSemicircles(Effect):
    def __init__(self, visualizer):
        super().__init__(
            "Spectrum Semicircles",
            visualizer,
            visualizer.get_screen()
        )
        self.audio_manager = visualizer.get_audio_manager()
        self.config = {
            "num_semicircles": 5,
            "max_radius": 200,
            "min_radius": 60,
            "arc_width_multiplier": 18,
            "rotation_speed_multiplier": 0.18
        }
        self.config_file = "Effects/configs/spectrum_semicircles_config.json"
        self.load_config_from_file(self.config_file)
        # Un ángulo suavizado para cada semicírculo
        self.smooth_angles = [0.0 for _ in range(self.config["num_semicircles"])]

    def draw(self, audio_data):
        screen = self.visualizer.screen
        center_x, center_y = self.get_center_x(), self.get_center_y()
        num_semicircles = self.config["num_semicircles"]
        min_radius = self.config["min_radius"]
        max_radius = self.config["max_radius"]

        # Fondo semitransparente para trailing suave
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 38))
        screen.blit(overlay, (0, 0))

        # Volumen normalizado
        volume_level = min(self.audio_manager.get_volume(audio_data) / 32768, 1.0)

        # Ángulo base objetivo animado
        time = pygame.time.get_ticks() / 1000.0
        base_angle = time * self.config["rotation_speed_multiplier"] * (0.5 + volume_level)

        smoothing = 0.12  # Suavizado exponencial

        for i in range(num_semicircles):
            t = i / max(num_semicircles - 1, 1)
            # Cada semicírculo tiene su propio ángulo objetivo, repartido en el círculo
            target_angle = base_angle + t * 2 * np.pi
            # Suaviza el ángulo de cada semicírculo
            self.smooth_angles[i] += (target_angle - self.smooth_angles[i]) * smoothing

            # El radio varía con el volumen y la posición
            radius = int(min_radius + t * (max_radius - min_radius) * (0.7 + 0.7 * volume_level))

            # Color según el ángulo (tono arcoíris)
            hue = (t + self.smooth_angles[i] * 0.15 + time * 0.08) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            color = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

            # Ángulos de inicio y fin para cada semicírculo, apuntando en direcciones diferentes
            start_angle = self.smooth_angles[i]
            end_angle = start_angle + np.pi

            # Grosor del arco suavizado por el volumen
            arc_width = max(3, int(3 + volume_level * self.config["arc_width_multiplier"]))

            rect = (center_x - radius, center_y - radius, 2 * radius, 2 * radius)
            pygame.draw.arc(screen, color, rect, start_angle, end_angle, arc_width)