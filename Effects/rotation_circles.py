import random
import math
import pygame
import numpy as np
import colorsys
from Effects.effect import Effect

class RotationCircles(Effect):
    def __init__(self, visualizer):
        super().__init__("Dark Spectrum", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()
        self.config_file = "Effects/configs/rotation_circles_config.json"
        self.load_config_from_file(self.config_file)
        
        # Configuración para ambiente techno oscuro ULTRA OPTIMIZADO
        self.config = {
            "spectrum_bars": 20,  # Reducido más para mejor rendimiento
            "smoke_particles": 20,  # Reducido significativamente
            "max_height": self.screen.get_height() * 0.9,
            "bass_threshold": 0.2,
            "color_shift_speed": 0.08
        }
        
        # Estado del visualizador MEJORADO
        self.time = 0
        self.bass_history = []
        self.color_phase = 0
        self.rotation_angle = 0  # Para rotación dinámica
        self.pulse_intensity = 0  # Para efectos de pulsación
        self.wave_offset = 0  # Para ondas en las barras
        
        # Partículas de humo
        self.smoke_particles = []
        self.init_smoke_particles()
        
        # Suavizado de espectro MÁS REACTIVO
        self.spectrum_smooth = np.zeros(self.config["spectrum_bars"])
        self.smoothing_factor = 0.4  # Menos suavizado para más agresividad
        
        # Cache para optimización
        self.color_cache = {}
        self.cache_counter = 0
        
    def init_smoke_particles(self):
        """Inicializa las partículas de humo"""
        for _ in range(self.config["smoke_particles"]):
            particle = {
                'x': random.randint(0, self.screen.get_width()),
                'y': random.randint(0, self.screen.get_height()),
                'vel_x': random.uniform(-1.2, 1.2),  # Velocidad reducida
                'vel_y': random.uniform(-2.0, -0.4),  # Movimiento vertical optimizado
                'size': random.uniform(3, 12),  # Partículas más grandes
                'alpha': random.randint(40, 120),  # Más opacas
                'color_offset': random.uniform(0, 2 * math.pi),
                'energy': 0.0,
                'pulse_phase': random.uniform(0, 2 * math.pi)  # Para pulsación individual
            }

            self.smoke_particles.append(particle)

    def get_dark_techno_color(self, intensity, bass_energy):
        """Genera colores oscuros y atmosféricos para ambiente techno OPTIMIZADO"""
        # Cache de colores para mejor rendimiento
        cache_key = int(intensity * 10) * 100 + int(bass_energy * 10)
        if cache_key in self.color_cache:
            return self.color_cache[cache_key]
        
        # Base de colores oscuros techno: púrpuras, azules, rojos profundos
        base_hue = (self.color_phase + intensity * 0.3) % 1.0
        
        # Colores MÁS saturados y agresivos
        saturation = 0.8 + bass_energy * 0.2
        
        # Brillo más alto para colores más intensos
        brightness = 0.4 + intensity * 0.6 + bass_energy * 0.3
        
        # Convertir HSV a RGB
        r, g, b = colorsys.hsv_to_rgb(base_hue, saturation, brightness)
        
        # Intensificar para ambiente techno agresivo (simplificado)
        if base_hue < 0.3 or base_hue > 0.7:  # Rojos/Magentas
            r = min(1.0, r * 1.4)
        else:  # Azules/Púrpuras
            b = min(1.0, b * 1.4)
        
        # Asegurar que los valores estén en rango válido [0, 255]
        color = (
            max(0, min(255, int(r * 255))),
            max(0, min(255, int(g * 255))),
            max(0, min(255, int(b * 255)))
        )
        
        # Guardar en cache (limpiar cache cada 100 llamadas)
        self.cache_counter += 1
        if self.cache_counter > 100:
            self.color_cache.clear()
            self.cache_counter = 0
        else:
            self.color_cache[cache_key] = color
            
        return color
        
    def draw_spectrum_bars(self, freq_data, bass_energy):
        """Dibuja barras de espectro reactivas con efecto de humo MEJORADO"""
        bar_width = self.screen.get_width() / self.config["spectrum_bars"]
        center_x = self.screen.get_width() // 2
        
        # Crear bins de frecuencia para las barras
        freq_bins = np.array_split(freq_data[:len(freq_data)//2], self.config["spectrum_bars"])
        
        for i, freq_bin in enumerate(freq_bins):
            if len(freq_bin) == 0:
                continue
                
            # Energía de esta barra
            raw_energy = np.mean(freq_bin)
            normalized_energy = min(1.0, raw_energy / 32768.0)
            
            # Suavizar MENOS para mayor reactividad
            smoothing = self.smoothing_factor
            self.spectrum_smooth[i] = (self.spectrum_smooth[i] * smoothing + 
                                     normalized_energy * (1 - smoothing))
            
            # Amplificar la energía para barras más altas y agresivas
            amplified_energy = min(1.0, self.spectrum_smooth[i] * 1.5)
            
            # MEJORA: Efecto de onda en las barras
            wave_factor = 1 + 0.3 * math.sin(self.wave_offset + i * 0.2)
            
            # MEJORA: Pulsación desde el centro
            distance_from_center = abs(i - self.config["spectrum_bars"] // 2) / (self.config["spectrum_bars"] // 2)
            pulse_factor = 1 + self.pulse_intensity * (1 - distance_from_center) * 0.5
            
            # Altura de la barra con efectos mejorados
            bar_height = int(amplified_energy * self.config["max_height"] * wave_factor * pulse_factor)
            
            if bar_height > 5:
                x = int(i * bar_width)
                
                # Color dinámico con más variación
                color_intensity = (i / self.config["spectrum_bars"] + self.time * 0.1) % 1.0
                color = self.get_dark_techno_color(color_intensity, bass_energy)
                
                # MEJORA: Barras que se inclinan ligeramente hacia el centro
                lean_angle = (i - self.config["spectrum_bars"] // 2) * 0.02
                
                # Dibujar barra ULTRA OPTIMIZADA con inclinación
                for h in range(0, bar_height, 8):  # Paso aún más grande
                    alpha = int(255 * (1 - h / bar_height) * 0.8)
                    current_y = self.screen.get_height() - h
                    
                    # Desplazamiento horizontal por inclinación (simplificado)
                    lean_offset = int(h * lean_angle)
                    
                    # Color con fade hacia arriba (simplificado)
                    fade_factor = 1 - (h / bar_height) * 0.4
                    faded_color = tuple(int(c * fade_factor) for c in color)
                    
                    # Crear superficie con alpha MÁS GRUESA
                    smoke_surf = pygame.Surface((int(bar_width) - 1, 8), pygame.SRCALPHA)
                    smoke_surf.fill((*faded_color, alpha))
                    self.screen.blit(smoke_surf, (x + lean_offset, current_y - 8))
                    
    def update_smoke_particles(self, freq_data):
        """Actualiza las partículas de humo atmosférico"""
        screen_w, screen_h = self.screen.get_size()
        
        # Energía promedio para influir en el humo
        avg_energy = np.mean(freq_data[:len(freq_data)//4]) / 32768.0
        
        for particle in self.smoke_particles:
            # Movimiento influenciado por la música SIMPLIFICADO
            particle['energy'] = 0.8 * particle['energy'] + 0.2 * avg_energy
            
            # Actualizar fase de pulsación individual (menos frecuente)
            particle['pulse_phase'] += 0.15 + particle['energy'] * 0.2
            
            # Velocidad base + influencia musical SIMPLIFICADA
            music_influence_x = math.sin(self.time + particle['color_offset']) * particle['energy'] * 0.6
            music_influence_y = -particle['energy'] * 1.0
            
            particle['x'] += particle['vel_x'] + music_influence_x
            particle['y'] += particle['vel_y'] + music_influence_y
            
            # Resetear partículas que salen de pantalla
            if particle['y'] < -10:
                particle['y'] = screen_h + 10
                particle['x'] = random.randint(0, screen_w)
            elif particle['x'] < -10 or particle['x'] > screen_w + 10:
                particle['x'] = random.randint(0, screen_w)
                
            # Tamaño dinámico con la música SIMPLIFICADO
            base_size = particle['size']
            pulse_factor = 1 + math.sin(particle['pulse_phase']) * 0.3
            particle['current_size'] = base_size * (0.6 + particle['energy'] * 0.8) * pulse_factor
            
    def draw_smoke_particles(self, bass_energy):
        """Dibuja las partículas de humo con colores dinámicos OPTIMIZADO"""
        for particle in self.smoke_particles:
            # Color basado en posición y energía
            color_phase = (particle['color_offset'] + self.color_phase) % (2 * math.pi)
            intensity = particle['energy']
            
            color = self.get_dark_techno_color(color_phase / (2 * math.pi), bass_energy)
            
            # Validar que el color sea válido
            if not isinstance(color, tuple) or len(color) != 3:
                color = (100, 100, 200)  # Color de respaldo
            
            # Asegurar que todos los valores de color sean enteros válidos
            color = tuple(max(0, min(255, int(c))) for c in color)
            
            # Alpha dinámico SIMPLIFICADO
            alpha = int(particle['alpha'] * (0.5 + intensity * 0.5))
            alpha = max(0, min(255, alpha))
            
            # OPTIMIZACIÓN: Usar círculos simples más eficientes
            radius = max(2, int(particle['current_size']))
            
            try:
                # Dibujar círculo directo en pantalla - MÁS RÁPIDO
                pygame.draw.circle(self.screen, color, 
                                 (int(particle['x']), int(particle['y'])), 
                                 radius)
            except (ValueError, TypeError):
                continue

    def draw(self, audio_data):
        # Fondo negro profundo con ligero tinte MÁS DRAMÁTICO
        self.screen.fill((2, 2, 20))
        
        # Actualizar tiempo y animaciones MÁS RÁPIDO
        self.time += 0.15
        self.color_phase += self.config["color_shift_speed"]
        if self.color_phase > 1.0:
            self.color_phase = 0.0
            
        # MEJORA: Actualizar efectos de animación
        self.rotation_angle += 0.02
        self.wave_offset += 0.1

        # Obtener datos de audio
        freq_data = self.audio_manager.get_frequency_data(audio_data)
        if len(freq_data) == 0:
            freq_data = np.zeros(512)
            
        # Calcular energía de graves para efectos especiales
        bass_bins = len(freq_data) // 8
        bass_energy = np.mean(freq_data[:bass_bins]) / 32768.0 if bass_bins > 0 else 0
        
        # MEJORA: Actualizar intensidad de pulsación basada en el audio
        target_pulse = bass_energy * 0.8
        self.pulse_intensity = self.pulse_intensity * 0.8 + target_pulse * 0.2
        
        # Mantener historial de graves para detección de beats
        self.bass_history.append(bass_energy)
        if len(self.bass_history) > 10:
            self.bass_history.pop(0)
            
        # Actualizar partículas de humo
        self.update_smoke_particles(freq_data)
        
        # Dibujar humo de fondo
        self.draw_smoke_particles(bass_energy)
        
        # Dibujar espectro principal
        self.draw_spectrum_bars(freq_data, bass_energy)
        
        # Efecto de flash ULTRA OPTIMIZADO
        if len(self.bass_history) > 5:
            recent_avg = np.mean(self.bass_history[-3:])
            if bass_energy > recent_avg * 1.4 and bass_energy > self.config["bass_threshold"]:
                flash_intensity = int(40 * min(1.0, bass_energy))
                flash_color = self.get_dark_techno_color(self.color_phase, bass_energy)
                
                # Flash simple y eficiente
                overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                overlay.fill((*flash_color, flash_intensity))
                self.screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()
        # Reinicializar partículas para nueva resolución
        self.smoke_particles = []
        self.init_smoke_particles()
        # Actualizar configuración OPTIMIZADA
        self.config["max_height"] = height * 0.9