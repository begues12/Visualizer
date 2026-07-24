import pygame
import math
import random
import colorsys
import numpy as np
from Effects.effect import Effect


class ConcertLasers(Effect):
    """Laser de concierto: acumula tension en el build-up y estalla en el drop."""

    def __init__(self, visualizer):
        super().__init__("Concert Lasers", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()

        defaults = {
            "emitters": 2,
            "beams": 24,
            "spread": 80,          # apertura del abanico (grados)
            "sweep_range": 24,     # barrido de lado a lado (grados)
            "sweep_speed": 0.9,
            "beam_width": 2,
            "glow": 1.2,
            "sensitivity": 1.35,   # sensibilidad al golpe
            "drop_power": 1.0,     # intensidad del caos en el drop
        }
        self.config_meta = {
            "emitters": {"min": 1, "max": 4, "step": 1, "label": "Proyectores"},
            "beams": {"min": 6, "max": 48, "step": 1, "label": "Haces por abanico"},
            "spread": {"min": 20, "max": 140, "step": 2, "label": "Apertura (grados)"},
            "sweep_range": {"min": 0, "max": 60, "step": 1, "label": "Barrido (grados)"},
            "sweep_speed": {"min": 0.0, "max": 4.0, "step": 0.1, "label": "Velocidad de barrido"},
            "beam_width": {"min": 1, "max": 8, "step": 1, "label": "Grosor del haz"},
            "glow": {"min": 0.0, "max": 3.0, "step": 0.1, "label": "Resplandor / niebla"},
            "sensitivity": {"min": 1.0, "max": 3.0, "step": 0.05, "label": "Sensibilidad al golpe"},
            "drop_power": {"min": 0.0, "max": 2.0, "step": 0.1, "label": "Fuerza del drop"},
        }
        self.config_file = "Effects/configs/concert_lasers_config.json"
        loaded = {}
        try:
            self.load_config_from_file(self.config_file)
            loaded = self.config
        except Exception:
            pass
        self.config = {k: loaded.get(k, dv) for k, dv in defaults.items()}

        self.vol_hist = []
        self.bass_hist = []
        self.tension = 0.0     # nivel de build-up (0..1)
        self.drop = 0.0        # intensidad tras el drop (decae)
        self.hue = 0.33
        self.flash = 0.0
        self.t = 0.0
        self.last_beat = 0
        self.last_drop = 0
        self.last_strobe = 0

    # ------------------------------------------------ analisis de dinamica
    def _update_dynamics(self, audio_data):
        freq = self.audio_manager.get_frequency_data(audio_data)
        volume = min(1.0, self.audio_manager.get_volume(audio_data) / 32768.0)
        if len(freq) > 8:
            n = len(freq)
            bass = float(np.mean(freq[:n // 8]))
            treble = float(np.mean(freq[n // 2:]))
        else:
            bass = treble = 0.0

        # Historial de volumen -> deteccion de subida de energia (build-up)
        self.vol_hist.append(volume)
        if len(self.vol_hist) > 90:
            self.vol_hist.pop(0)
        short = np.mean(self.vol_hist[-12:])
        longm = np.mean(self.vol_hist) + 1e-6
        climb = float(np.clip((short - longm) / longm, 0.0, 1.0))
        treble_ratio = treble / (bass + treble + 1e-6)   # risers/redobles = muchos agudos
        tension_t = float(np.clip(0.8 * climb + 1.2 * volume * treble_ratio, 0.0, 1.0))
        # La tension sube/baja despacio (se acumula durante segundos)
        self.tension = float(np.clip(self.tension * 0.93 + tension_t * 0.07, 0.0, 1.0))

        # Golpe y DROP
        self.bass_hist.append(bass)
        if len(self.bass_hist) > 43:
            self.bass_hist.pop(0)
        avg = sum(self.bass_hist) / len(self.bass_hist)
        ratio = bass / (avg + 1e-6)
        now = pygame.time.get_ticks()
        beat = ratio > self.config["sensitivity"] and now - self.last_beat > 110
        if beat:
            self.last_beat = now
            self.hue = (self.hue + 0.11) % 1.0
            self.flash = max(self.flash, 45)
        # DROP: bajazo fuerte cuando venia acumulandose tension
        if (ratio > self.config["sensitivity"] * 1.5 and self.tension > 0.4
                and now - self.last_drop > 1400):
            self.last_drop = now
            self.drop = 1.0
            self.flash = max(self.flash, 230)
            self.tension *= 0.2  # liberacion
        self.drop *= 0.95

        # Strobe de build-up que se acelera segun sube la tension
        if self.tension > 0.28:
            interval = max(55, 420 - self.tension * 360)
            if now - self.last_strobe > interval:
                self.last_strobe = now
                self.flash = max(self.flash, 40 + 130 * self.tension)

        return volume, freq

    def _beam(self, layer, x, y, ang, length, color, width, glow_f, f):
        ex = x + math.cos(ang) * length
        ey = y + math.sin(ang) * length
        gl = tuple(int(min(255, c * 0.18 * glow_f)) for c in color)
        core = tuple(int(min(255, c * (0.35 + 0.65 * f))) for c in color)
        pygame.draw.line(layer, gl, (x, y), (ex, ey), max(3, width * 4))
        pygame.draw.line(layer, core, (x, y), (ex, ey), width)

    def draw(self, audio_data):
        screen = self.visualizer.get_screen()
        self.screen = screen
        w, h = screen.get_size()
        cfg = self.config

        # Estela / niebla (mas limpia en el drop para que reviente de luz)
        fade = self.get_layer("fade", clear=False)
        fade.fill((0, 0, 0, int(90 + 60 * self.drop)))
        screen.blit(fade, (0, 0))

        volume, freq = self._update_dynamics(audio_data)
        fmax = float(np.max(freq)) + 1e-6 if len(freq) else 1.0
        tension, drop = self.tension, self.drop

        # Color en el hue rota rapido durante el drop
        self.hue = (self.hue + 0.003 + 0.06 * drop) % 1.0
        self.t += 0.02 + 0.03 * volume + 0.12 * drop

        # --- Mapeo de la dinamica al movimiento ---
        # Build-up: abanico se cierra y apunta arriba, se pone blanco, sweep se frena.
        # Drop: abanico se abre de golpe, sweep muy rapido, color saturado y caotico.
        spread = math.radians(cfg["spread"]) * (0.5 + 0.5 * volume)
        spread *= float(np.clip(1 - 0.5 * tension + 1.3 * drop, 0.15, 2.5))
        sweep_amp = math.radians(cfg["sweep_range"]) * (1 - 0.7 * tension) + math.radians(cfg["sweep_range"]) * 1.6 * drop
        sweep_spd = cfg["sweep_speed"] * (1 + 1.6 * tension + 5 * drop * cfg["drop_power"])
        base_f = float(np.clip(0.3 + 0.6 * volume + 0.4 * tension + 0.7 * drop, 0, 1))
        sat = float(np.clip(1 - 0.8 * tension + drop, 0.12, 1.0))  # se blanquea en build-up
        width = max(1, int(cfg["beam_width"]))
        glow_f = cfg["glow"] * (0.5 + 0.6 * volume + 0.6 * drop)

        colored = np.array(colorsys.hsv_to_rgb(self.hue, sat, 1.0)) * 255
        white = np.array([255, 255, 255])

        n_beams = max(2, int(cfg["beams"]))
        n_emit = max(1, int(cfg["emitters"]))
        length = math.hypot(w, h) * 1.2
        layer = self.get_layer("main")
        emitters = [(int(w * (k + 1) / (n_emit + 1)), int(h * 0.82)) for k in range(n_emit)]

        for ei, (ox, oy) in enumerate(emitters):
            direction = 1 if ei % 2 == 0 else -1
            jitter = random.uniform(-1, 1) * 0.18 * drop  # caos en el drop
            for fan_idx, fan_color in enumerate((colored, white)):
                aim = (-math.pi / 2
                       + direction * math.sin(self.t * sweep_spd + fan_idx * 1.3) * sweep_amp
                       + jitter)
                for i in range(n_beams):
                    frac = i / (n_beams - 1) - 0.5
                    ang = aim + frac * spread
                    if len(freq):
                        bin_idx = int(abs(frac) * 2 * (len(freq) // 2 - 1))
                        mag = min(1.0, freq[bin_idx] / fmax)
                    else:
                        mag = 0.0
                    f = min(1.0, base_f * (0.55 + 0.7 * mag))
                    self._beam(layer, ox, oy, ang, length, fan_color, width, glow_f, f)

        screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

        # Puntos calientes de los proyectores
        for ox, oy in emitters:
            hr = int(10 + 26 * volume + 20 * drop)
            hot = pygame.Surface((hr * 2, hr * 2), pygame.SRCALPHA)
            pygame.draw.circle(hot, tuple(int(c) for c in colored), (hr, hr), hr)
            pygame.draw.circle(hot, (255, 255, 255), (hr, hr), max(2, hr // 2))
            screen.blit(hot, (ox - hr, oy - hr), special_flags=pygame.BLEND_ADD)

        # Strobe / fogonazo
        if self.flash > 2:
            overlay = self.get_layer("flash", clear=False)
            v = int(min(255, self.flash))
            overlay.fill((v, v, v))
            screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            self.flash *= 0.72

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
