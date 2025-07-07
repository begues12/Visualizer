import pygame
import random
import numpy as np
import colorsys
from Effects.effect import Effect

class FrequencyWaterfall(Effect):
    def __init__(self, visualizer):
        super().__init__("Color Matrix Rain", visualizer, visualizer.get_screen())
        self.screen = visualizer.get_screen()
        self.audio_manager = visualizer.get_audio_manager()
        self.config = {
            "columns": 48,  # Menos columnas = más rápido
            "speed": 8,
            "font_size": 20,
            "trail_length": 12  # Menos trail = más rápido
        }
        self.drops = []
        self.width = self.get_width()
        self.height = self.get_height()
        self.font = pygame.font.SysFont("consolas", self.config["font_size"], bold=True)
        self.reset_drops()

    def reset_drops(self):
        self.drops = []
        col_width = self.width // self.config["columns"]
        for i in range(self.config["columns"]):
            x = i * col_width
            y = random.randint(-self.height, 0)
            self.drops.append({
                "x": x,
                "y": y,
                "trail": [y - j * self.config["font_size"] for j in range(self.config["trail_length"])],
                "char": self.random_char()
            })

    def random_char(self):
        return chr(random.randint(33, 126))

    def on_screen_resize(self, width, height):
        self.width = width
        self.height = height
        self.reset_drops()

    def draw(self, audio_data):
        # Fade general para dejar rastro
        fade_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, 60))  # Un poco más de alfa para limpiar más rápido
        self.screen.blit(fade_surface, (0, 0))

        freq_data = self.audio_manager.get_frequency_data()
        col_width = self.width // self.config["columns"]
        max_freq = np.argmax(freq_data)
        direction = 1 if max_freq < len(freq_data) // 2 else -1

        # Pre-renderiza un solo carácter para el trail (verde Matrix)
        trail_char = self.font.render('|', True, (80, 255, 80, 120))

        for i, drop in enumerate(self.drops):
            freq_idx = int(i * len(freq_data) / self.config["columns"])
            freq_val = freq_data[freq_idx]
            # Color Matrix para la cabeza
            head_color = (min(255, 80 + freq_val // 2), min(255, 255), min(255, 80 + freq_val // 3))
            head_text = self.font.render(drop["char"], True, head_color)
            self.screen.blit(head_text, (int(drop["x"]), int(drop["y"])))

            # Dibuja trail (solo un carácter y color para todo el trail)
            for t, ty in enumerate(drop["trail"][1:]):
                alpha = max(30, 180 - t * (150 // self.config["trail_length"]))
                # Usamos el mismo surface pero cambiamos la posición y el alpha
                trail_surface = trail_char.copy()
                trail_surface.set_alpha(alpha)
                self.screen.blit(trail_surface, (int(drop["x"]), int(ty)))

            # Actualiza trail
            drop["trail"].insert(0, drop["y"])
            if len(drop["trail"]) > self.config["trail_length"]:
                drop["trail"].pop()

            # Mueve la gota
            drop["y"] += direction * (self.config["speed"] + freq_val // 120)
            # Reinicia si sale de pantalla
            if direction == 1 and drop["y"] > self.height:
                drop["y"] = random.randint(-self.height // 4, 0)
                drop["trail"] = [drop["y"] - j * self.config["font_size"] for j in range(self.config["trail_length"])]
            elif direction == -1 and drop["y"] < -self.config["font_size"]:
                drop["y"] = self.height + random.randint(0, self.height // 4)
                drop["trail"] = [drop["y"] + j * self.config["font_size"] for j in range(self.config["trail_length"])]
            # Cambia el carácter de la cabeza de vez en cuando
            if random.random() < 0.08:
                drop["char"] = self.random_char()
                
    def on_screen_resize(self, width, height):
        self.width = width
        self.height = height
        self.screen = self.visualizer.get_screen()
        self.font = pygame.font.SysFont("consolas", self.config["font_size"], bold=True)
        self.reset_drops()