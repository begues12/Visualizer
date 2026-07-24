import pygame
import math
import colorsys
import numpy as np
from Effects.effect import Effect


def _c(x):
    return max(0, min(255, int(x)))


class HyperTunnel(Effect):
    """Tunel de anillos que se lanza hacia ti y pega un zoom en cada golpe."""

    def __init__(self, visualizer):
        super().__init__("Hyper Tunnel", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()

        defaults = {
            "sensitivity": 1.35,
            "rings": 20,
            "speed": 1.0,
            "sides": 6,        # 0 = circulos, >2 = poligonos
            "rotation": 0.4,
            "glow": 1.0,
        }
        self.config_meta = {
            "sensitivity": {"min": 1.0, "max": 3.0, "step": 0.05, "label": "Sensibilidad al golpe"},
            "rings": {"min": 5, "max": 40, "step": 1, "label": "Anillos"},
            "speed": {"min": 0.2, "max": 4.0, "step": 0.1, "label": "Velocidad"},
            "sides": {"min": 0, "max": 12, "step": 1, "label": "Lados (0=circulo)"},
            "rotation": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Rotacion"},
            "glow": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Resplandor"},
        }
        self.config_file = "Effects/configs/hyper_tunnel_config.json"
        loaded = {}
        try:
            self.load_config_from_file(self.config_file)
            loaded = self.config
        except Exception:
            pass
        self.config = {k: loaded.get(k, dv) for k, dv in defaults.items()}

        self.phase = 0.0
        self.angle = 0.0
        self.zoom = 0.0
        self.hue = 0.6
        self.flash = 0.0

    def _ring_points(self, cx, cy, r, sides, rot):
        pts = []
        for i in range(sides):
            a = rot + (i / sides) * 2 * math.pi
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        return pts

    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        self.screen = screen
        w, h = screen.get_size()
        cx, cy = w // 2, h // 2
        cfg = self.config

        # Estela para dar sensacion de movimiento
        fade = self.get_layer("fade", clear=False)
        fade.fill((0, 0, 0, 80))
        screen.blit(fade, (0, 0))

        volume = min(1.0, self.audio_manager.get_volume(audio_data) / 32768.0)
        beat, strength = self.detect_beat(audio_data, cfg["sensitivity"], cooldown=90)
        if beat:
            self.zoom = min(1.5, self.zoom + 0.4 * strength)
            self.hue = (self.hue + 0.12) % 1.0
            self.flash = max(self.flash, 70 * strength)

        speed_eff = cfg["speed"] * (0.4 + 1.2 * volume) + self.zoom * 1.5
        self.phase = (self.phase + 0.012 * (1 + speed_eff)) % 1.0
        self.angle += cfg["rotation"] * 0.02 + self.zoom * 0.06
        self.zoom *= 0.88

        n = max(4, int(cfg["rings"]))
        sides = int(cfg["sides"])
        max_r = math.hypot(w, h) * 0.72 * (1 + 0.25 * self.zoom)
        glow_f = cfg["glow"]
        twist = math.pi * 1.5   # giro en espiral a lo largo de la profundidad

        # 1) Calcula todos los anillos (profundidad d: 0=lejos/centro, 1=cerca/borde)
        rings = []
        for i in range(n):
            d = ((i / n) + self.phase) % 1.0
            r = max_r * (d ** 1.7)   # espaciado en perspectiva (se juntan al fondo)
            rot = self.angle + d * twist
            if sides >= 3:
                verts = [(cx + math.cos(rot + 2 * math.pi * k / sides) * r,
                          cy + math.sin(rot + 2 * math.pi * k / sides) * r) for k in range(sides)]
            else:
                verts = None
            rings.append({"d": d, "r": r, "rot": rot, "verts": verts})

        layer = self.get_layer("main")

        # 2) Paredes del tunel: une los vertices de anillos contiguos en profundidad
        if sides >= 3:
            for i in range(n):
                a, b = rings[i], rings[(i + 1) % n]
                if b["d"] < a["d"]:
                    continue  # salta la costura del reciclaje
                d = a["d"]
                base = np.array(colorsys.hsv_to_rgb((self.hue + d * 0.5) % 1.0, 0.9, 1.0)) * 255
                f = 0.15 + 0.7 * d
                col = (_c(base[0] * f), _c(base[1] * f), _c(base[2] * f))
                wln = max(1, int(1 + 4 * d))
                for k in range(sides):
                    pygame.draw.line(layer, col, a["verts"][k], b["verts"][k], wln)

        # 3) Anillos
        for ring in rings:
            d, r = ring["d"], ring["r"]
            if r < 3:
                continue
            base = np.array(colorsys.hsv_to_rgb((self.hue + d * 0.5) % 1.0, 0.9, 1.0)) * 255
            f = 0.25 + 0.75 * d
            width = max(1, int(1 + 7 * d))
            core = (_c(base[0] * f), _c(base[1] * f), _c(base[2] * f))
            glow = (_c(base[0] * 0.22 * glow_f * d), _c(base[1] * 0.22 * glow_f * d), _c(base[2] * 0.22 * glow_f * d))
            if ring["verts"] is None:
                pygame.draw.circle(layer, glow, (cx, cy), int(r), max(3, width * 3))
                pygame.draw.circle(layer, core, (cx, cy), int(r), width)
            else:
                pygame.draw.polygon(layer, glow, ring["verts"], max(3, width * 3))
                pygame.draw.polygon(layer, core, ring["verts"], width)
        screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

        # Nucleo (punto de fuga) brillante
        core_r = int(5 + 24 * volume + 24 * self.zoom)
        if core_r > 1:
            base = np.array(colorsys.hsv_to_rgb(self.hue, 0.8, 1.0)) * 255
            surf = pygame.Surface((core_r * 2, core_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (_c(base[0]), _c(base[1]), _c(base[2])), (core_r, core_r), core_r)
            pygame.draw.circle(surf, (255, 255, 255), (core_r, core_r), max(1, core_r // 2))
            screen.blit(surf, (cx - core_r, cy - core_r), special_flags=pygame.BLEND_ADD)

        if self.flash > 2:
            overlay = self.get_layer("flash", clear=False)
            v = int(min(255, self.flash))
            overlay.fill((v, v, v))
            screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            self.flash *= 0.75

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
