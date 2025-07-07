from Effects.effect import Effect
import pygame
import numpy as np
import math
import colorsys

class Kaleidoscope(Effect):
    def __init__(self, visualizer):
        super().__init__(
            "Kaleidoscope",
            visualizer,
            visualizer.get_screen()
        )
        self.config = {
            "num_points": 120,
            "num_segments": 8,  # Número de "espejos"
            "radius": min(self.get_width(), self.get_height()) // 2 - 20,
            "line_width": 10
        }
        self.config_file = "Effects/configs/kaleidoscope_config.json"
        self.load_config_from_file(self.config_file)

    def draw(self, audio_data):
        screen = self.visualizer.screen
        width, height = self.get_width(), self.get_height()
        center_x, center_y = width // 2, height // 2

        # Prepara la onda base (puedes usar el audio o una función sinusoidal)
        audio_data = audio_data.astype(np.int32)
        num_points = self.config["num_points"]
        base_radius = self.config["radius"]
        num_segments = self.config["num_segments"]
        line_width = self.config["line_width"]

        # Normaliza y suaviza el audio
        if np.max(np.abs(audio_data)) > 0:
            audio_norm = audio_data / np.max(np.abs(audio_data))
        else:
            audio_norm = np.zeros_like(audio_data)
        window = 7
        kernel = np.ones(window) / window
        smooth_audio = np.convolve(audio_norm, kernel, mode='same')

        # --- Volumen actual (normalizado) ---
        volume = self.visualizer.audioManager.get_volume(audio_data)
        max_volume = getattr(self.visualizer.audioManager, "max_volume", 32768)
        volume_norm = min(volume / max_volume, 1.0)

        # Animación de rotación (más lento y sensible al volumen)
        time = pygame.time.get_ticks() * 0.00018  # Más lento (antes 0.0005)
        angle_offset = time * (0.5 + volume_norm * 1.5)  # Gira más rápido si hay más volumen

        # Calcula los puntos de la onda base (radio reacciona al volumen)
        points = []
        for i in range(num_points):
            idx = i * len(smooth_audio) // num_points
            angle = 2 * math.pi * i / num_points
            # El radio base crece con el volumen
            radius = base_radius * (0.6 + 0.25 * smooth_audio[idx] + 0.25 * volume_norm)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))

        # Dibuja la onda reflejada en varios segmentos
        for seg in range(num_segments):
            seg_angle = 2 * math.pi * seg / num_segments + angle_offset
            # Color reacciona al volumen (más saturado y brillante con más volumen)
            color_hue = (seg / num_segments + time * 0.2) % 1.0
            color_sat = 0.5 + 0.5 * volume_norm
            color_val = 0.7 + 0.3 * volume_norm
            rgb = colorsys.hsv_to_rgb(color_hue, color_sat, color_val)
            color = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            rot_points = []
            for x, y in points:
                # Rota cada punto alrededor del centro
                dx, dy = x - center_x, y - center_y
                angle = math.atan2(dy, dx) + seg_angle
                r = math.hypot(dx, dy)
                rx = center_x + r * math.cos(angle)
                ry = center_y + r * math.sin(angle)
                rot_points.append((rx, ry))
            # Dibuja la línea
            pygame.draw.aalines(screen, color, True, rot_points, blend=1)
            
    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()
        self.config["radius"] = min(width, height) // 2 - 20