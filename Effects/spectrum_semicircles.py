import pygame
import numpy as np
import colorsys
import random
import math
from Effects.effect import Effect

class SpectrumSemicircles(Effect):
    def __init__(self, visualizer):
        super().__init__("Audio Flames", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = self.visualizer.get_screen()
        self.phase = 0
        self.num_flames = 8
        self.base_positions = []
        self.precalc_colors = []
        self.last_size = (0, 0)
        self._precalc_static()

    def _precalc_static(self):
        w, h = self.screen.get_size()
        self.base_positions = [int((i + 1) * w // (self.num_flames + 1)) for i in range(self.num_flames)]
        # Precalcula gradientes de color para lenguas secundarias
        self.precalc_colors = []
        for rel in np.linspace(0, 1, 10):
            hue = 0.09 - 0.06 * rel
            sat = 1.0
            val = 1.0 - 0.2 * rel
            color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, sat, val))
            self.precalc_colors.append(color)
        self.last_size = (w, h)

    def bezier_curve(self, points, steps=8):
        n = len(points) - 1
        result = []
        for t in np.linspace(0, 1, steps):
            x = 0
            y = 0
            for i, (px, py) in enumerate(points):
                bern = math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))
                x += px * bern
                y += py * bern
            result.append((int(x), int(y)))
        return result
    
    
    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        w, h = screen.get_size()
        if (w, h) != self.last_size:
            self._precalc_static()

        volume = min(self.audio_manager.get_volume(audio_data) / 32768, 1.0)
        freq_data = self.audio_manager.get_frequency_data()
        bass = np.mean(freq_data[:len(freq_data)//8]) if len(freq_data) > 0 else 0

        # Efecto de parpadeo rojo cuando las llamas son azules (volumen alto)
        if volume > 0.75:  # Reducido de 0.92 a 0.75 para mayor reactividad
            # Parpadeo rápido basado en el tiempo
            flash_time = pygame.time.get_ticks() * 0.015  # Velocidad del parpadeo
            flash_intensity = (math.sin(flash_time) + 1) * 0.5  # Valor entre 0 y 1
            flash_alpha = int(flash_intensity * 120 + 30)  # Alpha entre 30 y 150
            
            # Crear overlay rojo parpadeante
            red_overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            red_color = (255, 50, 50, flash_alpha)  # Rojo con alpha variable
            red_overlay.fill(red_color)
            screen.blit(red_overlay, (0, 0))
            
            # Overlay normal más tenue para no opacar el efecto rojo
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 20))
            screen.blit(overlay, (0, 0))
        else:
            # Overlay normal cuando no hay parpadeo
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 36))
            screen.blit(overlay, (0, 0))

        flame_width = w // (self.num_flames + 1)
        t = pygame.time.get_ticks() * 0.002
        base_y = h - 8

        rand_offsets = [random.random() for _ in range(self.num_flames)]
        rand_ints = [random.randint(0, 10) for _ in range(self.num_flames)]

        bezier = self.bezier_curve

        for i, x in enumerate(self.base_positions):
            base_height = (0.18 + 0.82 * volume) * h * (0.7 + 0.3 * np.sin(t + i * 0.7))
            flame_height = int(base_height * (0.85 + 0.3 * rand_offsets[i]))

            tip = (x, base_y - flame_height - rand_ints[i])
            left_base = (x - flame_width // 2, base_y)
            right_base = (x + flame_width // 2, base_y)
            ctrl1 = (x - flame_width // 3, base_y - int(flame_height * 0.5))
            ctrl2 = (x + flame_width // 3, base_y - int(flame_height * 0.5))

            color_center = (80, 180, 255) if volume > 0.75 else (255, 255, 180)  # Reducido umbral para mayor reactividad
            curve_left = bezier([left_base, ctrl1, tip], steps=8)
            curve_right = bezier([tip, ctrl2, right_base], steps=8)
            points = curve_left + curve_right
            pygame.draw.polygon(screen, color_center, points)

            # Lenguas secundarias
            num_tongues = 2
            tongue_rand_offsets = [random.random() for _ in range(num_tongues)]
            tongue_rand_ints = [random.randint(0, 8) for _ in range(num_tongues)]
            for j in range(num_tongues):
                rel = (j + 1) / (num_tongues + 1)
                tongue_height = int(flame_height * (0.5 + 0.4 * rel + 0.1 * tongue_rand_offsets[j]))
                tongue_tip = (
                    x + random.randint(-flame_width // 3, flame_width // 3),
                    base_y - tongue_height - tongue_rand_ints[j]
                )
                tongue_left = (x - int(flame_width * 0.4 * (1 - rel)), base_y)
                tongue_right = (x + int(flame_width * 0.4 * (1 - rel)), base_y)
                ctrl1 = (tongue_left[0] + flame_width // 6, base_y - int(tongue_height * 0.5))
                ctrl2 = (tongue_right[0] - flame_width // 6, base_y - int(tongue_height * 0.5))

                # Usa color precalculado
                if volume > 0.75:  # Reducido umbral para mayor reactividad
                    color = (80, 180, 255)
                else:
                    idx = min(int(rel * (len(self.precalc_colors) - 1)), len(self.precalc_colors) - 1)
                    color = self.precalc_colors[idx]

                tongue_curve_left = bezier([tongue_left, ctrl1, tongue_tip], steps=5)
                tongue_curve_right = bezier([tongue_tip, ctrl2, tongue_right], steps=5)
                tongue_points = tongue_curve_left + tongue_curve_right
                pygame.draw.polygon(screen, color, tongue_points)