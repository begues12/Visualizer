import pygame
import math
import colorsys
import random
from Effects.effect import Effect

class SpinningBarsEffect(Effect):
    def __init__(self, visualizer):
        super().__init__("Techno Orbs", visualizer, visualizer.get_screen())
        # Configuración por defecto
        self.config = {
            "num_orbs": 10,  # Menos orbes para mucho más espacio entre ellos
            "orbit_radius": 380,  # Radio más amplio
            "rotation_speed": 0.02,  # Más lento para movimiento natural
            "orb_size": 15,  # Orbes un poco más grandes para compensar menor cantidad
            "pulse_intensity": 1.0,  # Reducido para movimiento más sutil
            "bass_threshold": 0.3,
            "natural_oscillation": 1.2,  # Mayor oscilación natural
            "orbit_variation": 0.5,  # Mayor variación en los radios orbitales
            "individual_speed_factor": 0.3  # Factor para velocidades individuales
        }
        self.config_file = "Effects/configs/spinning_bars_config.json"
        self.load_config_from_file(self.config_file)
        
        # Asegurar compatibilidad con configuraciones antiguas
        if "num_orbs" not in self.config:
            self.config["num_orbs"] = 10
        if "orbit_radius" not in self.config:
            self.config["orbit_radius"] = 380
        if "orb_size" not in self.config:
            self.config["orb_size"] = 15
        if "pulse_intensity" not in self.config:
            self.config["pulse_intensity"] = 1.0
        if "bass_threshold" not in self.config:
            self.config["bass_threshold"] = 0.3
        if "rotation_speed" not in self.config:
            self.config["rotation_speed"] = 0.02
        if "natural_oscillation" not in self.config:
            self.config["natural_oscillation"] = 1.2
        if "orbit_variation" not in self.config:
            self.config["orbit_variation"] = 0.5
        if "individual_speed_factor" not in self.config:
            self.config["individual_speed_factor"] = 0.3
            
        self.angle = 0
        self.bass_history = []
        self.time = 0
        
        # Variables para movimiento natural
        self.orb_phases = [random.uniform(0, 2 * math.pi) for _ in range(32)]  # Fases individuales
        self.orb_speeds = [random.uniform(0.6, 1.4) for _ in range(32)]  # Velocidades más variadas
        self.orb_oscillations = [random.uniform(0.8, 1.5) for _ in range(32)]  # Oscilaciones individuales

    def draw(self, audio_data):
        try:
            # Obtener datos de audio del manager
            audio_manager = self.visualizer.get_audio_manager()
            volume = audio_manager.get_volume(audio_data)
            volume_normalized = min(1.0, volume / 32768.0)
            
            # Obtener datos de frecuencia
            freq_data = audio_manager.get_frequency_data(audio_data)
            if len(freq_data) == 0:
                freq_data = [0] * 512
                
            # Calcular energía de graves para efectos techno
            bass_bins = len(freq_data) // 8
            bass_energy = sum(freq_data[:bass_bins]) / (bass_bins * 32768.0) if bass_bins > 0 else 0
            bass_energy = min(1.0, bass_energy)
            
        except Exception as e:
            # Valores por defecto si hay error con el audio
            volume_normalized = 0.1
            freq_data = [100] * 512
            bass_energy = 0.1
        
        # Mantener historial de graves
        self.bass_history.append(bass_energy)
        if len(self.bass_history) > 10:
            self.bass_history.pop(0)
        
        center_x, center_y = self.get_center_x(), self.get_center_y()
        
        # Validar que tenemos la configuración correcta
        num_orbs = self.config.get("num_orbs", 32)
        angle_step = 2 * math.pi / num_orbs if num_orbs > 0 else 0.1
        
        # Fondo con fade techno oscuro
        fade_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        fade_surface.fill((5, 5, 20, 45))  # Azul muy oscuro techno
        self.screen.blit(fade_surface, (0, 0))
        
        # Pulso central reactivo al bass
        bass_threshold = self.config.get("bass_threshold", 0.3)
        if bass_energy > bass_threshold:
            for r in range(int(60 * bass_energy), 0, -8):
                alpha = int(40 * bass_energy * (r / (60 * bass_energy)))
                # Colores techno: púrpura, azul, magenta
                hue = (self.time * 0.5 + bass_energy) % 1.0
                rgb = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
                color = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
                pygame.draw.circle(self.screen, (*color, alpha), (int(center_x), int(center_y)), r, 3)
        
        # Dibujar orbes exteriores techno con movimiento natural
        orbit_radius = self.config.get("orbit_radius", 380)
        orb_size_base = self.config.get("orb_size", 15)
        pulse_intensity = self.config.get("pulse_intensity", 1.0)
        natural_osc = self.config.get("natural_oscillation", 1.2)
        orbit_var = self.config.get("orbit_variation", 0.5)
        individual_speed = self.config.get("individual_speed_factor", 0.3)
        
        for i in range(num_orbs):
            # Obtener energía específica para este orbe
            freq_index = i * len(freq_data) // num_orbs
            orb_energy = freq_data[freq_index] / 32768.0 if freq_index < len(freq_data) else 0
            orb_energy = min(1.0, orb_energy)
            
            # Ángulo con rotación individual más natural
            base_angle = self.angle + i * angle_step
            individual_phase = self.orb_phases[i] if i < len(self.orb_phases) else 0
            individual_speed_mult = self.orb_speeds[i] if i < len(self.orb_speeds) else 1.0
            individual_osc = self.orb_oscillations[i] if i < len(self.orb_oscillations) else 1.0
            
            # Movimiento individual más orgánico
            angle = base_angle + individual_phase + (self.time * individual_speed * individual_speed_mult)
            
            # Radio dinámico con oscilación natural individual
            base_radius = orbit_radius * (0.7 + orbit_var * individual_osc)
            oscillation = natural_osc * math.sin(self.time * 0.5 + individual_phase) * 0.3
            dynamic_radius = base_radius * (0.9 + 0.3 * orb_energy + oscillation)
            
            # Posición del orbe con micro-variaciones para movimiento más orgánico
            micro_offset_x = 15 * math.sin(self.time * 0.3 + individual_phase * 2)
            micro_offset_y = 15 * math.cos(self.time * 0.4 + individual_phase * 1.5)
            
            orb_x = center_x + dynamic_radius * math.cos(angle) + micro_offset_x
            orb_y = center_y + dynamic_radius * math.sin(angle) + micro_offset_y
            
            # Color techno dinámico más variado
            hue = (i / num_orbs + self.time * 0.2 + orb_energy * 0.3 + individual_phase * 0.1) % 1.0
            sat = 0.7 + orb_energy * 0.3
            val = 0.5 + orb_energy * 0.5
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            color = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            
            # Tamaño del orbe reactivo con variación individual
            size_variation = 1.0 + (individual_osc - 1.0) * 0.2  # Variación sutil en tamaño base
            orb_size = int(orb_size_base * size_variation * (0.8 + orb_energy * pulse_intensity))
            
            # Glow exterior del orbe más pronunciado para orbes más espaciados
            glow_range = 12 if orb_energy > 0.5 else 8
            for glow_r in range(orb_size + glow_range, orb_size, -2):
                glow_alpha = int(35 * (1 - (glow_r - orb_size) / glow_range) * (0.6 + orb_energy * 0.4))
                pygame.draw.circle(self.screen, (*color, glow_alpha), (int(orb_x), int(orb_y)), glow_r)
            
            # Orbe principal
            pygame.draw.circle(self.screen, color, (int(orb_x), int(orb_y)), orb_size)
            
            # Core brillante
            core_size = max(2, orb_size // 2)
            core_color = tuple(min(255, c + 80) for c in color)
            pygame.draw.circle(self.screen, core_color, (int(orb_x), int(orb_y)), core_size)
            
            # Estela de energía mejorada si hay mucha energía
            if orb_energy > 0.5:
                trail_length = int(15 * orb_energy)  # Estela más corta pero más intensa
                for t in range(trail_length):
                    trail_factor = t / trail_length
                    trail_angle = angle - t * 0.08 * individual_speed_mult
                    trail_radius = dynamic_radius - t * 3
                    trail_x = center_x + trail_radius * math.cos(trail_angle)
                    trail_y = center_y + trail_radius * math.sin(trail_angle)
                    trail_alpha = int(120 * (1 - trail_factor) * orb_energy)
                    trail_size = max(1, int(orb_size * (1 - trail_factor * 0.7)))
                    
                    trail_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                    trail_color = tuple(int(c * (1 - trail_factor * 0.3)) for c in color)
                    pygame.draw.circle(trail_surf, (*trail_color, trail_alpha), (trail_size, trail_size), trail_size)
                    self.screen.blit(trail_surf, (int(trail_x - trail_size), int(trail_y - trail_size)), 
                                   special_flags=pygame.BLEND_ADD)
        
        # Flash techno en beats fuertes
        if len(self.bass_history) > 5:
            recent_avg = sum(self.bass_history[-3:]) / 3
            if bass_energy > recent_avg * 1.5 and bass_energy > bass_threshold:
                flash_intensity = int(40 * bass_energy)
                flash_hue = (self.time * 0.8) % 1.0
                flash_rgb = colorsys.hsv_to_rgb(flash_hue, 1.0, 1.0)
                flash_color = (int(flash_rgb[0]*255), int(flash_rgb[1]*255), int(flash_rgb[2]*255))
                
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((*flash_color, flash_intensity))
                self.screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Actualizar animación con movimiento más orgánico
        rotation_speed = self.config.get("rotation_speed", 0.02)
        self.angle += rotation_speed
        self.time += 0.08  # Tiempo más lento para movimiento más suave

    def on_screen_resize(self, new_width, new_height):
        # No necesitas guardar width/height, pero puedes recalcular si dependes de ellos
        self.screen = self.visualizer.get_screen()