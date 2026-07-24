import pygame
import numpy as np
import math
import random
from Effects.effect import Effect


class SpectrumSemicircles(Effect):
    def __init__(self, visualizer):
        super().__init__("Audio Flames", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = self.visualizer.get_screen()

        defaults = {
            "num_flames": 9,     # numero de llamas
            "height": 1.0,       # multiplicador de altura
            "sway_speed": 1.0,   # velocidad del balanceo
            "flicker": 1.0,      # temblor por agudos
            "glow": 1.0,         # intensidad del resplandor
        }
        self.config_meta = {
            "num_flames": {"min": 3, "max": 20, "step": 1, "label": "Numero de llamas"},
            "height": {"min": 0.3, "max": 2.5, "step": 0.05, "label": "Altura"},
            "sway_speed": {"min": 0.0, "max": 4.0, "step": 0.1, "label": "Balanceo"},
            "flicker": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Temblor (agudos)"},
            "glow": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Resplandor"},
        }
        self.config_file = "Effects/configs/spectrum_semicircles_config.json"
        loaded = {}
        try:
            self.load_config_from_file(self.config_file)
            loaded = self.config
        except Exception:
            pass
        self.config = {k: loaded.get(k, dv) for k, dv in defaults.items()}

        # Suavizado de audio para movimiento fluido
        self.vol_s = 0.0
        self.bass_s = 0.0
        self.treble_s = 0.0

        self.last_size = (0, 0)
        self._num = 0
        self.positions = []
        self.phases = []
        self._precalc()

    def _precalc(self):
        w, h = self.screen.get_size()
        n = max(1, int(self.config["num_flames"]))
        self.positions = [int((i + 1) * w / (n + 1)) for i in range(n)]
        self.phases = [random.uniform(0, 2 * math.pi) for _ in range(n)]
        self.last_size = (w, h)
        self._num = n

    def _bezier(self, p0, p1, p2, steps=8):
        pts = []
        for t in np.linspace(0, 1, steps):
            mt = 1 - t
            x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
            y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
            pts.append((int(x), int(y)))
        return pts

    def _flame_poly(self, x, base_y, height, half_w):
        tip = (x, base_y - height)
        left = (x - half_w, base_y)
        right = (x + half_w, base_y)
        c1 = (x - int(half_w * 0.6), base_y - int(height * 0.5))
        c2 = (x + int(half_w * 0.6), base_y - int(height * 0.5))
        return self._bezier(left, c1, tip) + self._bezier(tip, c2, right)

    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        self.screen = screen
        w, h = screen.get_size()
        if (w, h) != self.last_size or int(self.config["num_flames"]) != self._num:
            self._precalc()

        # --- Audio: volumen + bandas, suavizado ---
        volume = min(self.audio_manager.get_volume(audio_data) / 32768.0, 1.0)
        freq = self.audio_manager.get_frequency_data(audio_data)
        if len(freq) > 0:
            bass = min(1.0, float(np.mean(freq[:max(1, len(freq) // 8)])) / 20000.0)
            treble = min(1.0, float(np.mean(freq[len(freq) // 2:])) / 8000.0)
        else:
            bass = treble = 0.0
        self.vol_s = self.vol_s * 0.8 + volume * 0.2
        self.bass_s = self.bass_s * 0.7 + bass * 0.3
        self.treble_s = self.treble_s * 0.6 + treble * 0.4

        # Estela: oscurece un poco el frame anterior en vez de borrarlo
        overlay = self.get_layer("fade", clear=False)
        overlay.fill((0, 0, 0, 40))
        screen.blit(overlay, (0, 0))

        cfg = self.config
        t = pygame.time.get_ticks() * 0.001
        base_y = h - 6
        flame_w = w // (self._num + 1)
        blue_hot = self.vol_s > 0.8  # llama azul cuando pega fuerte

        glow_layer = self.get_layer("glow")
        glow_f = cfg["glow"] * (0.4 + 0.6 * self.vol_s)

        for i, x in enumerate(self.positions):
            sway = math.sin(t * cfg["sway_speed"] + self.phases[i])
            flick = 1.0 + 0.18 * cfg["flicker"] * self.treble_s * math.sin(t * 20 + i)
            height = ((0.14 + 0.7 * self.vol_s + 0.5 * self.bass_s) * h
                      * cfg["height"] * (0.78 + 0.22 * sway) * flick)
            height = int(max(20, height))
            half_w = max(6, int(flame_w * 0.5))

            # Resplandor (llama ancha y tenue, aditiva) -- color limitado a 0..255
            def _c(x):
                return max(0, min(255, int(x)))
            glow_col = (_c(20 * glow_f), _c(60 * glow_f), _c(90 * glow_f)) if blue_hot \
                else (_c(120 * glow_f), _c(50 * glow_f), 0)
            pygame.draw.polygon(glow_layer, glow_col,
                                self._flame_poly(x, base_y, int(height * 1.05), int(half_w * 1.5)))

            # Cuerpo con degradado: exterior -> nucleo (poligonos anidados)
            if blue_hot:
                layers = [((20, 60, 200), 1.0, 1.0), ((80, 160, 255), 0.78, 0.6),
                          ((180, 220, 255), 0.5, 0.32), ((255, 255, 255), 0.28, 0.16)]
            else:
                layers = [((200, 40, 10), 1.0, 1.0), ((255, 120, 20), 0.8, 0.62),
                          ((255, 200, 60), 0.52, 0.34), ((255, 245, 200), 0.28, 0.16)]
            for color, hs, ws in layers:
                pygame.draw.polygon(screen, color,
                                    self._flame_poly(x, base_y, int(height * hs), max(3, int(half_w * ws))))

        screen.blit(glow_layer, (0, 0), special_flags=pygame.BLEND_ADD)

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
        self._precalc()
