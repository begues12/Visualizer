import pygame
import math
import colorsys
import numpy as np
from Effects.effect import Effect


class FluidFrequencyVisualizer(Effect):
    def __init__(self, visualizer):
        super().__init__("Fluid Frequency", visualizer, visualizer.get_screen())
        self.screen = visualizer.get_screen()
        self.audio_manager = visualizer.get_audio_manager()

        self.center_x = self.screen.get_width() // 2
        self.center_y = self.screen.get_height() // 2
        self.blob = {'x': self.center_x, 'y': self.center_y}

        # Config editable desde el panel web
        defaults = {
            "base_size": 0.26,    # tamano base (fraccion de la pantalla)
            "deformation": 1.0,   # intensidad de la deformacion
            "glow": 1.0,          # intensidad del aura
            "color_speed": 1.0,   # velocidad de cambio de color
            "num_points": 40,     # resolucion del contorno
        }
        self.config_meta = {
            "base_size": {"min": 0.1, "max": 0.5, "step": 0.01, "label": "Tamano base"},
            "deformation": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Deformacion"},
            "glow": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Resplandor"},
            "color_speed": {"min": 0.0, "max": 4.0, "step": 0.1, "label": "Velocidad de color"},
            "num_points": {"min": 12, "max": 80, "step": 1, "label": "Detalle del contorno"},
        }
        self.config_file = "Effects/configs/character_config.json"
        loaded = {}
        try:
            self.load_config_from_file(self.config_file)
            loaded = self.config
        except Exception:
            pass
        self.config = {k: loaded.get(k, dv) for k, dv in defaults.items()}

        # Suavizado de audio
        self.vol_s = 0.0
        self.bass_s = 0.0
        self.mid_s = 0.0
        self.treble_s = 0.0
        self.pulse = 0.0     # golpe (decae)
        self.hue = 0.0
        self.time = 0.0

    def _analyze(self, freq):
        n = len(freq)
        if n < 8:
            return 0.0, 0.0, 0.0
        bass = float(np.mean(freq[:int(n * 0.15)]))
        mid = float(np.mean(freq[int(n * 0.15):int(n * 0.55)]))
        treble = float(np.mean(freq[int(n * 0.55):]))
        norm = 32768.0
        return min(1.0, bass / norm), min(1.0, mid / norm), min(1.0, treble / norm)

    def _blob_points(self, w, h):
        cfg = self.config
        n = max(8, int(cfg["num_points"]))
        di = cfg["deformation"]
        ref = min(w, h) / 540.0
        base_radius = cfg["base_size"] * min(w, h) * (0.55 + 1.15 * self.vol_s + 0.6 * self.pulse)
        min_radius = 0.07 * min(w, h)
        t = self.time
        pts = []
        for i in range(n):
            a = (i / n) * 2 * math.pi
            deform = (
                self.bass_s * 42 * di * ref * math.sin(a * 2 + t * 2)
                + self.mid_s * 26 * di * ref * math.sin(a * 4 + t * 3)
                + self.treble_s * 18 * di * ref * math.sin(a * 8 + t * 5)
                + self.pulse * 34 * di * ref * math.sin(a * 3)
                + 12 * di * ref * math.sin(a * 3 + t * 1.5) * math.cos(a * 2 + t)
            )
            r = max(min_radius, base_radius + deform)
            pts.append((self.blob['x'] + r * math.cos(a), self.blob['y'] + r * math.sin(a)))
        return pts

    def _smooth(self, points, steps=6):
        """Suaviza el contorno con interpolacion cuadratica cerrada."""
        n = len(points)
        out = []
        for i in range(n):
            p0 = points[i]
            p1 = points[(i + 1) % n]
            p2 = points[(i + 2) % n]
            for t in np.linspace(0, 1, steps):
                mt = 1 - t
                x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
                y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
                out.append((x, y))
        return out

    def _scale(self, pts, s):
        cx, cy = self.blob['x'], self.blob['y']
        return [(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in pts]

    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        self.screen = screen
        w, h = screen.get_size()
        self.blob['x'], self.blob['y'] = w // 2, h // 2
        screen.fill((0, 0, 0))

        # --- Audio ---
        freq = self.audio_manager.get_frequency_data(audio_data)
        if len(freq) == 0:
            freq = np.zeros(512)
        volume = min(1.0, self.audio_manager.get_volume(audio_data) / 32768.0)
        bass, mid, treble = self._analyze(freq)

        # Golpe = subida brusca de graves
        prev_bass = self.bass_s
        s = 0.85
        self.vol_s = self.vol_s * s + volume * (1 - s)
        self.bass_s = self.bass_s * s + bass * (1 - s)
        self.mid_s = self.mid_s * s + mid * (1 - s)
        self.treble_s = self.treble_s * s + treble * (1 - s)
        if bass - prev_bass > 0.06:
            self.pulse = min(1.0, self.pulse + (bass - prev_bass) * 4)
        self.pulse *= 0.88
        self.time += 0.04 + 0.05 * self.vol_s

        # --- Color HSV que rota y reacciona a las bandas ---
        self.hue = (self.hue + 0.0015 * self.config["color_speed"] + 0.02 * self.pulse) % 1.0
        hue = (self.hue + 0.15 * self.bass_s - 0.1 * self.treble_s) % 1.0
        sat = 0.55 + 0.35 * self.mid_s
        base = np.array(colorsys.hsv_to_rgb(hue, sat, 1.0)) * 255
        comp = np.array(colorsys.hsv_to_rgb((hue + 0.5) % 1.0, sat, 1.0)) * 255

        # --- Contorno suave ---
        pts = self._smooth(self._blob_points(w, h), steps=6)
        if len(pts) < 3:
            return

        glow_f = self.config["glow"] * (0.4 + 0.6 * self.vol_s)
        layer = self.get_layer("main")

        def col(rgb, f):
            return (int(min(255, rgb[0] * f)), int(min(255, rgb[1] * f)), int(min(255, rgb[2] * f)))

        # Aura exterior (grande y tenue) -> cuerpo -> nucleo brillante
        pygame.draw.polygon(layer, col(comp, 0.22 * glow_f), self._scale(pts, 1.45))
        pygame.draw.polygon(layer, col(base, 0.45 * glow_f), self._scale(pts, 1.18))
        pygame.draw.polygon(layer, col(base, 0.9), pts)
        pygame.draw.polygon(layer, col(base * 0.4 + np.array([255, 255, 255]) * 0.6, 0.85),
                            self._scale(pts, 0.55))
        screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

        # Nucleo central palpitante
        core_r = int((6 + 26 * self.vol_s + 30 * self.pulse))
        if core_r > 1:
            core = pygame.Surface((core_r * 2, core_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(core, (255, 255, 255), (core_r, core_r), core_r)
            pygame.draw.circle(core, col(base, 1.0), (core_r, core_r), core_r, max(1, core_r // 4))
            screen.blit(core, (self.blob['x'] - core_r, self.blob['y'] - core_r),
                        special_flags=pygame.BLEND_ADD)

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
        self.center_x = width // 2
        self.center_y = height // 2
        self.blob['x'] = self.center_x
        self.blob['y'] = self.center_y
