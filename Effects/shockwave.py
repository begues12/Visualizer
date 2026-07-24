import pygame
import math
import colorsys
import numpy as np
from Effects.effect import Effect


class Shockwave(Effect):
    """Ondas expansivas que explotan en cada golpe de sonido."""

    def __init__(self, visualizer):
        super().__init__("Shockwave", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()

        defaults = {
            "sensitivity": 1.4,   # cuanto debe superar el golpe a la media
            "expand_speed": 16,   # velocidad de expansion de la onda
            "ring_width": 9,      # grosor del anillo
            "max_rings": 16,      # anillos simultaneos maximos
            "flash": 110,         # destello por golpe
            "glow": 1.0,          # intensidad del resplandor
        }
        self.config_meta = {
            "sensitivity": {"min": 1.0, "max": 3.0, "step": 0.05, "label": "Sensibilidad al golpe"},
            "expand_speed": {"min": 4, "max": 40, "step": 1, "label": "Velocidad de onda"},
            "ring_width": {"min": 2, "max": 24, "step": 1, "label": "Grosor del anillo"},
            "max_rings": {"min": 2, "max": 30, "step": 1, "label": "Anillos simultaneos"},
            "flash": {"min": 0, "max": 255, "step": 5, "label": "Destello"},
            "glow": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Resplandor"},
        }
        self.config_file = "Effects/configs/shockwave_config.json"
        loaded = {}
        try:
            self.load_config_from_file(self.config_file)
            loaded = self.config
        except Exception:
            pass
        self.config = {k: loaded.get(k, dv) for k, dv in defaults.items()}

        self.rings = []
        self.energy = []
        self.last_beat = 0
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

        # Estela: oscurece el frame anterior
        fade = self.get_layer("fade", clear=False)
        fade.fill((0, 0, 0, 60))
        screen.blit(fade, (0, 0))

        volume = min(1.0, self.audio_manager.get_volume(audio_data) / 32768.0)

        beat, strength = self._beat(audio_data)
        if beat and len(self.rings) < int(cfg["max_rings"]):
            self.hue = (self.hue + 0.08 + 0.2 * strength) % 1.0
            self.rings.append({"r": 8.0, "hue": self.hue, "strength": strength})
            self.flash = max(self.flash, cfg["flash"] * strength)

        max_r = math.hypot(w, h) * 0.55
        layer = self.get_layer("main")
        glow_f = cfg["glow"]
        speed = cfg["expand_speed"]

        alive = []
        for ring in self.rings:
            ring["r"] += speed * (0.7 + ring["strength"])
            if ring["r"] >= max_r:
                continue
            f = max(0.0, 1.0 - ring["r"] / max_r)  # desvanece al expandirse
            base = np.array(colorsys.hsv_to_rgb(ring["hue"], 0.9, 1.0)) * 255
            r = int(ring["r"])
            width = max(2, int(cfg["ring_width"] * f) + 1)
            # Resplandor ancho + anillo brillante (aditivo)
            pygame.draw.circle(layer, tuple(int(c * 0.25 * glow_f * f) for c in base),
                               (cx, cy), r, max(3, width * 3))
            pygame.draw.circle(layer, tuple(int(min(255, c * (0.5 + f))) for c in base),
                               (cx, cy), r, width)
            alive.append(ring)
        self.rings = alive

        screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

        # Destello de golpe
        if self.flash > 2:
            overlay = self.get_layer("flash", clear=False)
            v = int(min(255, self.flash))
            overlay.fill((v, v, v))
            screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            self.flash *= 0.78

        # Nucleo central que late con el volumen
        core = int(6 + 40 * volume)
        if core > 1:
            base = np.array(colorsys.hsv_to_rgb(self.hue, 0.8, 1.0)) * 255
            surf = pygame.Surface((core * 2, core * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, tuple(int(c) for c in base), (core, core), core)
            pygame.draw.circle(surf, (255, 255, 255), (core, core), max(1, core // 2))
            screen.blit(surf, (cx - core, cy - core), special_flags=pygame.BLEND_ADD)

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
        self.rings.clear()
