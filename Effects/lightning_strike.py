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
        self.strike_duration = 120  # ms
        self.cooldown = 120  # ms entre rayos
        self.volume_threshold = 0.25
        self.precompute_count = 200  # Precalcula 200 rayos
        self.precomputed_strikes = []
        self.precompute_strikes()
        self.active_strikes = []
        self.last_strike_time = 0

    def precompute_strikes(self):
        self.precomputed_strikes.clear()
        for _ in range(self.precompute_count):
            self.precomputed_strikes.append(self.generate_strike())

    def draw(self, audio_data):
        volume = self.visualizer.audioManager.get_volume(audio_data)
        max_volume = getattr(self.visualizer.audioManager, "max_volume", 32768)
        volume_norm = min(volume / max_volume, 1.0)

        now = pygame.time.get_ticks()
        if (now - self.last_strike_time > self.cooldown
                and volume_norm > self.volume_threshold
                and self.precomputed_strikes
                and len(self.active_strikes) < 8):  # Limita rayos simultáneos
            strike_points = self.precomputed_strikes.pop(0)
            self.precomputed_strikes.append(strike_points)  # Recicla el rayo
            strike = {
                "points": strike_points,
                "brightness": 255,
                "progress": 2,
                "start_time": now
            }
            self.active_strikes.append(strike)
            self.last_strike_time = now

        # Dibuja y actualiza todos los rayos activos
        new_active_strikes = []
        for strike in self.active_strikes:
            # Trueno/parpadeo (opcional, puedes comentar para más FPS)
            if random.random() < 0.10:
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((180, 180, 255, 40))
                self.screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

            self.draw_strike(strike["points"][:strike["progress"]], strike["brightness"], width=3)
            strike["brightness"] = max(0, strike["brightness"] - 30)
            if strike["progress"] < len(strike["points"]):
                strike["progress"] += 2
            elif now - strike["start_time"] <= self.strike_duration:
                pass
            else:
                continue
            new_active_strikes.append(strike)
        self.active_strikes = new_active_strikes

    def generate_strike(self):
        width = self.screen.get_width()
        height = self.screen.get_height()
        start_x = random.randint(width // 4, width * 3 // 4)
        start_y = 0
        end_y = random.randint(int(height * 0.7), int(height * 0.95))
        points = [(start_x, start_y)]
        num_segments = 14  # Menos segmentos para más eficiencia
        x, y = start_x, start_y
        for i in range(num_segments):
            seg_len = (end_y - start_y) // num_segments
            angle = random.uniform(-np.pi/6, np.pi/6)
            x += int(np.sin(angle) * seg_len * 0.7)
            y += int(seg_len * (0.8 + 0.4 * random.random()))
            points.append((x, y))
        return points

    def draw_strike(self, points, brightness, width=3):
        if len(points) < 2:
            return
        color = (200, 220, 255)
        pygame.draw.lines(
            self.screen,
            (*color, min(255, brightness)),
            False,
            points,
            max(1, width)
        )
        # Glow general (opcional, mucho más eficiente que uno por segmento)
        glow_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.lines(
            glow_surface,
            (180, 200, 255, 30),
            False,
            points,
            max(6, width * 2)
        )
        self.screen.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)
        
    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()
        self.precompute_strikes()