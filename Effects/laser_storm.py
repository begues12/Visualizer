import pygame
import math
import colorsys
import random
import numpy as np
from Effects.effect import Effect


class LaserStorm(Effect):
    """Rayos laser que salen del centro y estallan con cada golpe."""

    def __init__(self, visualizer):
        super().__init__("Laser Storm", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()

        defaults = {
            "sensitivity": 1.4,     # sensibilidad al golpe
            "num_beams": 12,        # numero de rayos
            "beam_width": 4,        # grosor del rayo
            "rotation_speed": 0.4,  # giro continuo
            "flash": 90,            # destello por golpe
            "glow": 1.0,            # resplandor
        }
        self.config_meta = {
            "sensitivity": {"min": 1.0, "max": 3.0, "step": 0.05, "label": "Sensibilidad al golpe"},
            "num_beams": {"min": 2, "max": 40, "step": 1, "label": "Numero de rayos"},
            "beam_width": {"min": 1, "max": 16, "step": 1, "label": "Grosor del rayo"},
            "rotation_speed": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Velocidad de giro"},
            "flash": {"min": 0, "max": 255, "step": 5, "label": "Destello"},
            "glow": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Resplandor"},
        }
        self.config_file = "Effects/configs/laser_storm_config.json"
        loaded = {}
        try:
            self.load_config_from_file(self.config_file)
            loaded = self.config
        except Exception:
            pass
        self.config = {k: loaded.get(k, dv) for k, dv in defaults.items()}

        self.energy = []
        self.last_beat = 0
        self.offset = 0.0       # angulo de giro
        self.spin = 0.0         # empujon de giro por golpe (decae)
        self.brightness = 0.0   # brillo global (pico en golpe, decae)
        self.flash = 0.0
        self.hue = 0.0

    def _beat(self, audio_data):
        freq = self.audio_manager.get_frequency_data(audio_data)
        if len(freq) == 0:
            return False, 0.0
        bass = float(np.mean(freq[:max(1, len(freq) // 8)]))
        self.energy.append(bass)
        if len(self.energy) > 43:
            self.energy.pop(0)
        avg = sum(self.energy) / len(self.energy)
        now = pygame.time.get_ticks()
        ratio = bass / (avg + 1e-6)
        if ratio > self.config["sensitivity"] and now - self.last_beat > 90:
            self.last_beat = now
            return True, float(np.clip((ratio - self.config["sensitivity"]) + 0.4, 0.3, 1.0))
        return False, 0.0

    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        self.screen = screen
        w, h = screen.get_size()
        cx, cy = w // 2, h // 2
        cfg = self.config

        # Estela oscura
        fade = self.get_layer("fade", clear=False)
        fade.fill((0, 0, 0, 70))
        screen.blit(fade, (0, 0))

        volume = min(1.0, self.audio_manager.get_volume(audio_data) / 32768.0)

        beat, strength = self._beat(audio_data)
        if beat:
            self.brightness = 255
            self.spin += random.uniform(-0.5, 0.5) + 0.3 * strength
            self.hue = (self.hue + 0.1 + 0.2 * strength) % 1.0
            self.flash = max(self.flash, cfg["flash"] * strength)

        # Giro continuo + empujon del golpe
        self.offset += cfg["rotation_speed"] * 0.02 + self.spin * 0.05
        self.spin *= 0.85
        self.brightness *= 0.86

        # Los rayos siempre laten un poco con el volumen
        bright = max(self.brightness, 60 + 140 * volume)
        length = math.hypot(w, h)
        n = max(2, int(cfg["num_beams"]))
        width = max(1, int(cfg["beam_width"]))
        glow_f = cfg["glow"] * (0.4 + 0.6 * (bright / 255.0))
        f = bright / 255.0

        layer = self.get_layer("main")
        for i in range(n):
            a = self.offset + (i / n) * 2 * math.pi
            ex = cx + math.cos(a) * length
            ey = cy + math.sin(a) * length
            hue = (self.hue + i / n * 0.15) % 1.0
            base = np.array(colorsys.hsv_to_rgb(hue, 0.9, 1.0)) * 255
            # Glow ancho + nucleo brillante
            pygame.draw.line(layer, tuple(int(c * 0.22 * glow_f) for c in base),
                             (cx, cy), (ex, ey), max(4, width * 4))
            pygame.draw.line(layer, tuple(int(min(255, c * (0.4 + 0.6 * f))) for c in base),
                             (cx, cy), (ex, ey), width)
            pygame.draw.line(layer, (int(255 * f), int(255 * f), int(255 * f)),
                             (cx, cy), (ex, ey), max(1, width // 2))
        screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

        # Destello de golpe
        if self.flash > 2:
            overlay = self.get_layer("flash", clear=False)
            v = int(min(255, self.flash))
            overlay.fill((v, v, v))
            screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            self.flash *= 0.78

        # Nucleo central brillante
        core = int(8 + 30 * volume + 20 * f)
        if core > 1:
            surf = pygame.Surface((core * 2, core * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 255), (core, core), core)
            screen.blit(surf, (cx - core, cy - core), special_flags=pygame.BLEND_ADD)

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
