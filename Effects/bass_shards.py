import pygame
import math
import colorsys
import random
import numpy as np
from Effects.effect import Effect


def _c(x):
    return max(0, min(255, int(x)))


class BassShards(Effect):
    """La pantalla tiembla y estallan esquirlas desde el centro en cada bajazo."""

    def __init__(self, visualizer):
        super().__init__("Bass Shards", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()

        defaults = {
            "sensitivity": 1.3,
            "num_shards": 20,   # esquirlas por explosion
            "speed": 13,        # velocidad de salida
            "shake": 16,        # temblor de pantalla
            "glow": 1.0,
        }
        self.config_meta = {
            "sensitivity": {"min": 1.0, "max": 3.0, "step": 0.05, "label": "Sensibilidad al golpe"},
            "num_shards": {"min": 4, "max": 60, "step": 1, "label": "Esquirlas por golpe"},
            "speed": {"min": 3, "max": 30, "step": 1, "label": "Velocidad"},
            "shake": {"min": 0, "max": 40, "step": 1, "label": "Temblor"},
            "glow": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Resplandor"},
        }
        self.config_file = "Effects/configs/bass_shards_config.json"
        loaded = {}
        try:
            self.load_config_from_file(self.config_file)
            loaded = self.config
        except Exception:
            pass
        self.config = {k: loaded.get(k, dv) for k, dv in defaults.items()}

        self.shards = []
        self.rings = []
        self.shake_amt = 0.0
        self.hue = 0.02   # naranja/rojo agresivo

    def _explode(self, cx, cy, strength):
        n = int(self.config["num_shards"])
        spd = self.config["speed"]
        for _ in range(n):
            a = random.uniform(0, 2 * math.pi)
            v = spd * (0.5 + random.random()) * (0.7 + strength)
            self.shards.append({
                "x": cx, "y": cy,
                "vx": math.cos(a) * v, "vy": math.sin(a) * v,
                "rot": random.uniform(0, 2 * math.pi),
                "vrot": random.uniform(-0.3, 0.3),
                "size": random.randint(8, 26),
                "hue": (self.hue + random.uniform(-0.06, 0.06)) % 1.0,
                "life": 1.0,
            })
        self.rings.append({"r": 6.0, "strength": strength})

    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        self.screen = screen
        w, h = screen.get_size()
        cx, cy = w // 2, h // 2
        cfg = self.config

        fade = self.get_layer("fade", clear=False)
        fade.fill((0, 0, 0, 85))
        screen.blit(fade, (0, 0))

        volume = min(1.0, self.audio_manager.get_volume(audio_data) / 32768.0)
        beat, strength = self.detect_beat(audio_data, cfg["sensitivity"], cooldown=110)
        if beat:
            self.hue = (self.hue + 0.08) % 1.0
            self.shake_amt = cfg["shake"] * strength
            self._explode(cx, cy, strength)

        # Temblor de pantalla (se aplica al dibujar)
        ox = random.uniform(-self.shake_amt, self.shake_amt)
        oy = random.uniform(-self.shake_amt, self.shake_amt)
        self.shake_amt *= 0.82

        layer = self.get_layer("main")
        glow_f = cfg["glow"]

        # Ondas de impacto
        max_r = math.hypot(w, h) * 0.5
        alive_rings = []
        for ring in self.rings:
            ring["r"] += 18 * (0.7 + ring["strength"])
            if ring["r"] < max_r:
                f = 1.0 - ring["r"] / max_r
                col = (_c(255 * f), _c(120 * f), _c(40 * f))
                pygame.draw.circle(layer, col, (int(cx + ox), int(cy + oy)), int(ring["r"]), max(2, int(6 * f)))
                alive_rings.append(ring)
        self.rings = alive_rings

        # Esquirlas (triangulos que salen volando)
        alive = []
        for s in self.shards:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["vx"] *= 0.98
            s["vy"] *= 0.98
            s["rot"] += s["vrot"]
            s["life"] -= 0.02
            if s["life"] <= 0:
                continue
            f = s["life"]
            base = np.array(colorsys.hsv_to_rgb(s["hue"], 0.9, 1.0)) * 255
            col = (_c(base[0] * f), _c(base[1] * f), _c(base[2] * f))
            sz = s["size"] * (0.6 + 0.6 * f)
            px, py = s["x"] + ox, s["y"] + oy
            pts = []
            for k in range(3):
                a = s["rot"] + k * (2 * math.pi / 3)
                pts.append((px + math.cos(a) * sz, py + math.sin(a) * sz))
            # Glow + esquirla
            gcol = (_c(base[0] * 0.3 * glow_f * f), _c(base[1] * 0.3 * glow_f * f), _c(base[2] * 0.3 * glow_f * f))
            pygame.draw.polygon(layer, gcol, [(px + (x - px) * 1.8, py + (y - py) * 1.8) for x, y in pts])
            pygame.draw.polygon(layer, col, pts)
            alive.append(s)
        self.shards = alive

        screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

        # Nucleo central palpitante
        core_r = int(6 + 30 * volume + self.shake_amt)
        if core_r > 1:
            base = np.array(colorsys.hsv_to_rgb(self.hue, 0.9, 1.0)) * 255
            surf = pygame.Surface((core_r * 2, core_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (_c(base[0]), _c(base[1]), _c(base[2])), (core_r, core_r), core_r)
            pygame.draw.circle(surf, (255, 255, 255), (core_r, core_r), max(1, core_r // 2))
            screen.blit(surf, (int(cx + ox - core_r), int(cy + oy - core_r)), special_flags=pygame.BLEND_ADD)

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
        self.shards.clear()
        self.rings.clear()
