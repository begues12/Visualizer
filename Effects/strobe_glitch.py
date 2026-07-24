import pygame
import colorsys
import random
import numpy as np
from Effects.effect import Effect


class StrobeGlitch(Effect):
    """Estrobo agresivo con barras neon y aberracion RGB en cada golpe."""

    def __init__(self, visualizer):
        super().__init__("Strobe Glitch", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()

        defaults = {
            "sensitivity": 1.3,
            "strobe": 200,       # intensidad del estrobo (0-255)
            "glitch": 1.0,       # cantidad de desplazamiento RGB
            "bars": 8,           # numero de barras glitch
        }
        self.config_meta = {
            "sensitivity": {"min": 1.0, "max": 3.0, "step": 0.05, "label": "Sensibilidad al golpe"},
            "strobe": {"min": 0, "max": 255, "step": 5, "label": "Estrobo"},
            "glitch": {"min": 0.0, "max": 4.0, "step": 0.1, "label": "Glitch RGB"},
            "bars": {"min": 1, "max": 24, "step": 1, "label": "Barras"},
        }
        self.config_file = "Effects/configs/strobe_glitch_config.json"
        loaded = {}
        try:
            self.load_config_from_file(self.config_file)
            loaded = self.config
        except Exception:
            pass
        self.config = {k: loaded.get(k, dv) for k, dv in defaults.items()}

        self.bars = []
        self.flash = 0.0
        self.hue = 0.0

    def _make_bars(self, w, h):
        n = max(1, int(self.config["bars"]))
        self.bars = []
        for _ in range(n):
            bh = random.randint(int(h * 0.02), int(h * 0.12))
            self.bars.append({
                "y": random.randint(0, h),
                "h": bh,
                "hue": (self.hue + random.uniform(-0.15, 0.15)) % 1.0,
            })

    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        self.screen = screen
        w, h = screen.get_size()
        cfg = self.config
        screen.fill((0, 0, 0))

        volume = min(1.0, self.audio_manager.get_volume(audio_data) / 32768.0)
        beat, strength = self.detect_beat(audio_data, cfg["sensitivity"], cooldown=70)
        if beat:
            self.hue = (self.hue + 0.13) % 1.0
            self._make_bars(w, h)
            self.flash = max(self.flash, cfg["strobe"] * strength)

        if not self.bars:
            self._make_bars(w, h)

        off = int(cfg["glitch"] * (5 + 22 * volume))
        layer = self.get_layer("main")
        for bar in self.bars:
            base = np.array(colorsys.hsv_to_rgb(bar["hue"], 1.0, 1.0)) * 255
            y, bh = bar["y"], bar["h"]
            # Tres copias desplazadas -> aberracion cromatica (R/G/B) aditiva
            pygame.draw.rect(layer, (int(base[0]), 0, 0), (-off, y, w, bh))
            pygame.draw.rect(layer, (0, int(base[1]), 0), (0, y, w, bh))
            pygame.draw.rect(layer, (0, 0, int(base[2])), (off, y, w, bh))
        screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

        # Lineas de escaneo (scanlines) para textura glitch
        if off > 0:
            for sy in range(0, h, 4):
                pygame.draw.line(screen, (0, 0, 0), (0, sy), (w, sy), 1)

        # Estrobo a pantalla completa
        if self.flash > 2:
            overlay = self.get_layer("flash", clear=False)
            v = int(min(255, self.flash))
            overlay.fill((v, v, v))
            screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            self.flash *= 0.60

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
        self.bars = []
