import pygame
import numpy as np
import math
import random
import colorsys
from Effects.effect import Effect

class FrequencySpectrum(Effect):
    def __init__(self, visualizer):
        super().__init__(
            "Energy Orb",
            visualizer,
            visualizer.get_screen()
        )
        self.screen = visualizer.get_screen()
        self.audio_manager = visualizer.get_audio_manager()
        
        # Configuración por defecto optimizada para rendimiento
        self.config = {
            "base_radius": self.screen.get_height(),
            "max_radius": self.screen.get_height(),
            "num_particles": 35,  # Reducido de 60 a 25
            "num_rings": 4        # Reducido de 5 a 3
        }
        
        # Cargar configuración solo si existe y es válida
        self.config_file = "Effects/configs/frequency_spectrum_config.json"
        try:
            self.load_config_from_file(self.config_file)
            # Asegurar que tenemos todas las claves necesarias
            if "num_particles" not in self.config:
                self.config["num_particles"] = 35
            if "num_rings" not in self.config:
                self.config["num_rings"] = 4
            if "base_radius" not in self.config:
                self.config["base_radius"] = self.screen.get_height() // 2
            if "max_radius" not in self.config:
                self.config["max_radius"] = self.screen.get_height()
        except:
            # Si hay error cargando config, usar valores por defecto
            pass
        self.energy_level = 0.0
        self.phase = 0
        self.particles = []
        self.core_pulse = 0.0
        
        # Inicializar partículas de energía
        for _ in range(self.config["num_particles"]):
            self.particles.append({
                'angle': random.uniform(0, 2 * math.pi),
                'distance': random.uniform(50, 350),
                'speed': random.uniform(0.02, 0.08),
                'size': random.uniform(2, 6),
                'hue': random.uniform(0, 1)
            })

    def draw(self, audio_data):
        # Obtener datos de frecuencia y calcular energía total
        freq_data = self.audio_manager.get_frequency_data(audio_data)
        if len(freq_data) == 0:
            freq_data = np.zeros(512)
        
        # Calcular energía total (simplificado para rendimiento)
        total_energy = np.mean(freq_data[:64]) if len(freq_data) > 64 else 0  # Solo primeros 64 samples
        bass_energy = np.mean(freq_data[:16]) if len(freq_data) > 16 else 0   # Solo primeros 16 para bass
        
        # Suavizar la transición de energía
        target_energy = min(1.0, total_energy * 3.0)
        self.energy_level = 0.8 * self.energy_level + 0.2 * target_energy
        
        # Pulso del núcleo
        self.core_pulse = 0.9 * self.core_pulse + 0.1 * bass_energy
        
        w, h = self.screen.get_size()
        center_x, center_y = w // 2, h // 2
        
        # Fondo negro limpio
        self.screen.fill((0, 0, 0))
        
        # Radio dinámico de la bola de energía
        base_radius = self.config["base_radius"]
        energy_radius = base_radius + (self.config["max_radius"] - base_radius) * self.energy_level
        
        # NÚCLEO CENTRAL - pulsa con el bass
        core_size = int(20 + 40 * self.core_pulse)
        core_color = self._get_energy_color(self.core_pulse, 1.0)
        try:
            pygame.draw.circle(self.screen, core_color, (center_x, center_y), core_size)
            
            # Núcleo brillante interno
            inner_core = max(5, core_size // 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), inner_core)
        except ValueError:
            # Si hay error, dibujar núcleo simple
            pygame.draw.circle(self.screen, (255, 100, 100), (center_x, center_y), 30)
        
        # ANILLOS DE ENERGÍA - simplificados para mejor rendimiento
        for ring in range(self.config["num_rings"]):
            ring_energy = bass_energy if ring % 2 == 0 else total_energy
            
            ring_radius = int(energy_radius * (0.5 + 0.4 * ring))
            ring_color = self._get_energy_color(ring_energy, 0.8)
            
            # Dibujar anillo simple sin variaciones complejas
            try:
                pygame.draw.circle(self.screen, ring_color, (center_x, center_y), ring_radius, 3)
            except ValueError:
                pass
        
        # PARTÍCULAS DE ENERGÍA - optimizadas
        for particle in self.particles:
            # Actualizar posición de partícula (simplificado)
            particle['angle'] += particle['speed'] * (1 + self.energy_level * 0.5)
            
            # Distancia simplificada
            actual_distance = particle['distance'] + self.energy_level * 30
            
            # Posición de la partícula
            px = center_x + int(actual_distance * math.cos(particle['angle']))
            py = center_y + int(actual_distance * math.sin(particle['angle']))
            
            # Tamaño fijo para mejor rendimiento
            particle_size = int(particle['size'] * (0.8 + self.energy_level * 0.4))
            
            # Color fijo basado en energía
            if self.energy_level > 0.7:
                particle_color = (255, 100, 100)  # Rojo
            elif self.energy_level > 0.4:
                particle_color = (255, 255, 100)  # Amarillo
            else:
                particle_color = (100, 150, 255)  # Azul
            
            # Dibujar partícula simple
            if particle_size > 0 and 0 <= px < w and 0 <= py < h:
                try:
                    pygame.draw.circle(self.screen, particle_color, (px, py), particle_size)
                except ValueError:
                    pass
        
        # RAYOS DE ENERGÍA - simplificados
        if self.energy_level > 0.7:  # Umbral más alto para activar rayos
            num_rays = 6  # Número fijo de rayos
            for i in range(num_rays):
                angle = (2 * math.pi * i / num_rays) + self.phase
                ray_length = int(energy_radius * 1.2)
                
                end_x = center_x + int(ray_length * math.cos(angle))
                end_y = center_y + int(ray_length * math.sin(angle))
                
                # Verificar límites simples
                if (0 <= end_x < w and 0 <= end_y < h):
                    ray_color = (255, 150, 150) if self.energy_level > 0.8 else (255, 255, 100)
                    pygame.draw.line(self.screen, ray_color, (center_x, center_y), (end_x, end_y), 2)
        
        # FLASH DE ENERGÍA EXTREMA - simplificado
        if self.energy_level > 0.9:  # Solo con energía muy alta
            # Flash simple sin superficies complejas
            flash_overlay = pygame.Surface((w, h))
            flash_overlay.set_alpha(30)
            flash_overlay.fill((255, 255, 255))
            self.screen.blit(flash_overlay, (0, 0))
        
        self.phase += 0.1  # Velocidad fija para mejor rendimiento
    
    def _get_energy_color(self, energy, intensity=1.0):
        """Obtiene un color basado en el nivel de energía"""
        if energy < 0.3:
            # Azul para energía baja
            return (int(100 * intensity), int(150 * intensity), int(255 * intensity))
        elif energy < 0.6:
            # Verde/Amarillo para energía media
            return (int(255 * energy * intensity), int(255 * intensity), int(100 * intensity))
        else:
            # Rojo/Naranja para energía alta
            return (int(255 * intensity), int(150 * (1-energy) * intensity), int(50 * intensity))
    
    def _hsv_to_rgb(self, h, s, v):
        """Convierte HSV a RGB"""
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()