import pygame
import numpy as np
import random
from Effects.effect import Effect


class LightningStrike(Effect):
    def __init__(self, visualizer):
        super().__init__(
            "Lightning Strike",
            visualizer,
            visualizer.get_screen()
        )
        self.screen = visualizer.get_screen()

        # Parametros configurables desde el panel web (Effects/configs/*.json)
        self.config = {
            "sensitivity": 1.5,     # cuanto debe superar el grave a su media para contar como golpe
            "cooldown": 110,        # ms minimos entre rayos
            "max_strikes": 6,       # rayos simultaneos maximos
            "flash_intensity": 170, # brillo del destello de trueno (0-255)
            "bolt_width": 3,        # grosor del rayo
            "num_branches": 2,      # ramificaciones por rayo
        }
        self.config_meta = {
            "sensitivity": {"min": 1.0, "max": 3.0, "step": 0.05, "label": "Sensibilidad al golpe"},
            "cooldown": {"min": 40, "max": 600, "step": 10, "label": "Enfriamiento (ms)"},
            "max_strikes": {"min": 1, "max": 16, "step": 1, "label": "Rayos simultaneos"},
            "flash_intensity": {"min": 0, "max": 255, "step": 5, "label": "Destello de trueno"},
            "bolt_width": {"min": 1, "max": 10, "step": 1, "label": "Grosor del rayo"},
            "num_branches": {"min": 0, "max": 6, "step": 1, "label": "Ramificaciones"},
        }
        self.config_file = "Effects/configs/lightning_strike_config.json"
        self.load_config_from_file(self.config_file)

        self.strike_duration = 140  # ms que permanece visible el rayo
        self.active_strikes = []
        self.last_strike_time = 0
        self.flash = 0.0            # nivel actual del destello de trueno
        self.energy_history = []    # historial de energia de graves para detectar golpes

    # ------------------------------------------------------------ deteccion
    def _bass_energy(self, audio_data):
        freq = self.visualizer.audioManager.get_frequency_data(audio_data)
        if len(freq) == 0:
            return 0.0
        return float(np.mean(freq[:max(1, len(freq) // 8)]))

    def draw(self, audio_data):
        self.screen = self.visualizer.get_screen()
        cfg = self.config
        now = pygame.time.get_ticks()

        # --- Deteccion de golpe: energia instantanea vs media reciente ---
        bass = self._bass_energy(audio_data)
        self.energy_history.append(bass)
        if len(self.energy_history) > 60:
            self.energy_history.pop(0)
        avg = np.mean(self.energy_history) if self.energy_history else 0.0
        ratio = bass / (avg + 1e-6)

        is_beat = (
            ratio > cfg["sensitivity"]
            and now - self.last_strike_time > cfg["cooldown"]
            and len(self.active_strikes) < int(cfg["max_strikes"])
        )

        if is_beat:
            strength = float(np.clip((ratio - cfg["sensitivity"]) / cfg["sensitivity"] + 0.4, 0.3, 1.0))
            bolts = self.generate_strike(int(cfg["num_branches"]))
            n = len(bolts[0])
            self.active_strikes.append({
                "bolts": bolts,
                "phase": "fall",            # cae -> impacta
                "progress": 1.0,
                "fall_speed": max(1.0, n / 9.0),  # ~9 frames en descender
                "brightness": 255,
                "strength": strength,
            })
            self.last_strike_time = now
            # Pequeno resplandor mientras cae; el gran destello es al impactar
            self.flash = max(self.flash, cfg["flash_intensity"] * 0.25 * strength)

        # --- Destello de trueno (blanco que se desvanece) ---
        if self.flash > 2:
            overlay = self.get_layer("flash", clear=False)
            overlay.fill((255, 255, 255, int(min(255, self.flash))))
            self.screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            self.flash *= 0.80  # decaimiento

        # --- Dibuja y actualiza rayos activos ---
        width = max(1, int(cfg["bolt_width"]))
        still_active = []
        for strike in self.active_strikes:
            main = strike["bolts"][0]
            n = len(main)

            if strike["phase"] == "fall":
                # El rayo desciende: se dibuja solo la parte ya recorrida
                strike["progress"] += strike["fall_speed"]
                p = min(n, int(strike["progress"]))
                self.draw_polyline(main[:p], 255, width)
                self._draw_head(main[p - 1], width)  # cabeza brillante que cae
                if strike["progress"] >= n:
                    # Impacto: fogonazo del rayo completo + destello de pantalla
                    strike["phase"] = "flash"
                    strike["brightness"] = 255
                    self.flash = max(self.flash, cfg["flash_intensity"] * strike["strength"])
                still_active.append(strike)
            else:
                # Fogonazo: rayo entero + ramas, con parpadeo, desvaneciendo
                flick = 1.0 if random.random() > 0.25 else random.uniform(0.5, 0.85)
                b = strike["brightness"]
                self.draw_polyline(main, int(b * flick), width + 1)
                for branch in strike["bolts"][1:]:
                    self.draw_polyline(branch, int(b * 0.7 * flick), max(1, width - 1))
                strike["brightness"] -= 15
                if strike["brightness"] > 0:
                    still_active.append(strike)
        self.active_strikes = still_active

    def _draw_head(self, point, width):
        """Cabeza incandescente en la punta del rayo que cae."""
        gr = max(4, width * 5)
        glow = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (110, 160, 255), (gr, gr), gr)
        pygame.draw.circle(glow, (220, 235, 255), (gr, gr), max(2, gr // 2))
        pygame.draw.circle(glow, (255, 255, 255), (gr, gr), max(1, gr // 4))
        self.screen.blit(glow, (int(point[0] - gr), int(point[1] - gr)), special_flags=pygame.BLEND_ADD)

    # ------------------------------------------------------------ geometria
    def generate_strike(self, num_branches):
        w = self.screen.get_width()
        h = self.screen.get_height()
        start_x = random.randint(w // 4, w * 3 // 4)
        end_y = random.randint(int(h * 0.7), int(h * 0.95))
        main = self._bolt_path(start_x, 0, end_y, segments=14)

        bolts = [main]
        for _ in range(max(0, num_branches)):
            if len(main) < 4:
                break
            i = random.randint(2, len(main) - 2)
            bx, by = main[i]
            branch_len = random.randint(int(h * 0.1), int(h * 0.3))
            bolts.append(self._bolt_path(bx, by, by + branch_len, segments=6, spread=1.4))
        return bolts

    def _bolt_path(self, x, y, end_y, segments, spread=1.0):
        points = [(x, y)]
        seg_len = max(1, (end_y - y) // segments)
        for _ in range(segments):
            angle = random.uniform(-np.pi / 5, np.pi / 5)
            x += int(np.sin(angle) * seg_len * 1.1 * spread)
            y += int(seg_len * (0.8 + 0.4 * random.random()))
            points.append((x, y))
        return points

    def draw_polyline(self, points, brightness, width):
        if len(points) < 2:
            return
        # f desvanece el rayo escalando el color (BLEND_ADD ignora el alpha)
        f = max(0.0, min(1.0, brightness / 255.0))
        layer = self.get_layer("bolt")
        # Capas de mayor a menor grosor: glow azul ancho -> nucleo blanco caliente
        pygame.draw.lines(layer, (int(50 * f), int(90 * f), int(200 * f)), False, points, max(8, width * 6))
        pygame.draw.lines(layer, (int(90 * f), int(140 * f), int(255 * f)), False, points, max(5, width * 3))
        pygame.draw.lines(layer, (int(160 * f), int(200 * f), int(255 * f)), False, points, max(3, width + 1))
        pygame.draw.lines(layer, (int(255 * f), int(255 * f), int(255 * f)), False, points, max(1, width - 1))
        self.screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

    def on_screen_resize(self, width, height):
        super().on_screen_resize(width, height)
        self.screen = self.visualizer.get_screen()
        self.active_strikes.clear()
