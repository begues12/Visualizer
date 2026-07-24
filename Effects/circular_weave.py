from Effects.effect import Effect
import pygame
import math
import colorsys
import numpy as np


def _c(x):
    return max(0, min(255, int(x)))


class CircularWeave(Effect):
    """Tejido circular (string-art) que se transforma con la musica."""

    def __init__(self, visualizer):
        super().__init__("Circular Weave", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()

        defaults = {
            "points": 120,     # numero de puntos del circulo
            "line_width": 1,   # grosor de la cuerda
            "speed": 1.0,      # velocidad de transformacion
            "rotation": 0.2,   # rotacion continua
            "glow": 1.0,       # resplandor
        }
        self.config_meta = {
            "points": {"min": 20, "max": 260, "step": 2, "label": "Puntos"},
            "line_width": {"min": 1, "max": 6, "step": 1, "label": "Grosor de cuerda"},
            "speed": {"min": 0.0, "max": 4.0, "step": 0.1, "label": "Velocidad"},
            "rotation": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Rotacion"},
            "glow": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Resplandor"},
        }
        self.config_file = "Effects/configs/circular_weave_config.json"
        loaded = {}
        try:
            self.load_config_from_file(self.config_file)
            loaded = self.config
        except Exception:
            pass
        self.config = {k: loaded.get(k, dv) for k, dv in defaults.items()}

        self.k = 2.0        # multiplicador de la "tabla de multiplicar" (morphing)
        self.rot = 0.0
        self.hue = 0.5

    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        self.screen = screen
        w, h = screen.get_size()
        cx, cy = w // 2, h // 2
        cfg = self.config
        screen.fill((0, 0, 0))

        volume = min(1.0, self.audio_manager.get_volume(audio_data) / 32768.0)
        freq = self.audio_manager.get_frequency_data(audio_data)
        if len(freq) > 8:
            bass = min(1.0, float(np.mean(freq[:len(freq) // 8])) / 20000.0)
            treble = min(1.0, float(np.mean(freq[len(freq) // 2:])) / 8000.0)
        else:
            bass = treble = 0.0

        # El radio late con los graves, la transformacion corre con los agudos
        radius = min(w, h) * 0.42 * (0.55 + 0.5 * volume + 0.25 * bass)
        self.k += (0.004 + 0.05 * treble) * cfg["speed"]
        self.rot += cfg["rotation"] * 0.01
        self.hue = (self.hue + 0.0015 + 0.02 * treble) % 1.0

        n = max(4, int(cfg["points"]))
        width = max(1, int(cfg["line_width"]))
        glow_f = cfg["glow"]
        k = self.k

        # Posiciones precalculadas de los puntos del circulo
        pts = []
        for i in range(n):
            a = self.rot + (i / n) * 2 * math.pi
            pts.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius))

        layer = self.get_layer("main")
        for i in range(n):
            j = (i * k) % n                 # conecta i -> i*k (mod n): tejido tipo mandala
            j0 = int(j) % n
            j1 = (j0 + 1) % n
            frac = j - int(j)
            # Interpola la posicion destino para que el patron morfee suave
            x2 = pts[j0][0] + (pts[j1][0] - pts[j0][0]) * frac
            y2 = pts[j0][1] + (pts[j1][1] - pts[j0][1]) * frac

            hue = (self.hue + i / n * 0.6) % 1.0
            base = np.array(colorsys.hsv_to_rgb(hue, 0.9, 1.0)) * 255
            f = 0.4 + 0.6 * volume
            glow = (_c(base[0] * 0.18 * glow_f), _c(base[1] * 0.18 * glow_f), _c(base[2] * 0.18 * glow_f))
            core = (_c(base[0] * (0.4 + 0.6 * f)), _c(base[1] * (0.4 + 0.6 * f)), _c(base[2] * (0.4 + 0.6 * f)))
            pygame.draw.line(layer, glow, pts[i], (x2, y2), max(2, width * 3))
            pygame.draw.line(layer, core, pts[i], (x2, y2), width)

        screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
