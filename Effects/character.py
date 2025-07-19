import pygame
import math
import numpy as np
from Effects.effect import Effect
import random

class FluidFrequencyVisualizer(Effect):
    def __init__(self, visualizer):
        super().__init__("Fluid Frequency", visualizer, visualizer.get_screen())
        self.screen = visualizer.get_screen()
        self.audio_manager = visualizer.get_audio_manager()
        
        # Centro de la pantalla
        self.center_x = self.screen.get_width() // 2
        self.center_y = self.screen.get_height() // 2
        
        # Un solo blob central grande
        self.blob = {
            'x': self.center_x,
            'y': self.center_y,
            'radius': 520,
            'base_radius': 320
        }
        
        # Variables para análisis de audio
        self.freq_bands = {
            'bass': 0.0,      # Graves (0-250 Hz)
            'mid': 0.0,       # Medios (250-4000 Hz)  
            'treble': 0.0     # Agudos (4000+ Hz)
        }
        
        # Suavizado de valores
        self.volume_smooth = 0.0
        self.bass_smooth = 0.0
        self.mid_smooth = 0.0
        self.treble_smooth = 0.0
        
        # Animación
        self.time = 0
        self.beat_intensity = 0.0
        
        # Configuración de deformación
        self.num_points = 32  # Número de puntos del perímetro para deformación
        self.deformation_points = [0.0] * self.num_points
        self.deformation_intensity = 2.0  # Multiplicador de deformación (1.0 = normal, 2.0 = doble intensidad)
        
    def analyze_frequency_bands(self, freq_data):
        """Analiza las frecuencias en bandas de graves, medios y agudos"""
        if len(freq_data) < 32:
            return
            
        # Dividir el espectro en bandas
        total_bins = len(freq_data)
        
        # Graves: primeros 20% de bins (aproximadamente 0-4kHz si sample rate = 44.1kHz)
        bass_end = int(total_bins * 0.2)
        # Medios: 20%-70% de bins (aproximadamente 4-14kHz)
        mid_end = int(total_bins * 0.7)
        # Agudos: 70%-100% de bins (aproximadamente 14-22kHz)
        
        bass_energy = np.mean(freq_data[:bass_end]) if bass_end > 0 else 0
        mid_energy = np.mean(freq_data[bass_end:mid_end]) if mid_end > bass_end else 0
        treble_energy = np.mean(freq_data[mid_end:]) if len(freq_data) > mid_end else 0
        
        # Normalizar
        max_val = 32768.0
        self.freq_bands['bass'] = min(1.0, bass_energy / max_val)
        self.freq_bands['mid'] = min(1.0, mid_energy / max_val)
        self.freq_bands['treble'] = min(1.0, treble_energy / max_val)
        
    def smooth_values(self, volume_normalized):
        """Suaviza los valores de audio para animaciones fluidas"""
        smoothing = 0.9  # Factor de suavizado (0-1, más alto = más suave)
        
        # Suavizar volumen
        self.volume_smooth = self.volume_smooth * smoothing + volume_normalized * (1 - smoothing)
        
        # Suavizar bandas de frecuencia
        self.bass_smooth = self.bass_smooth * smoothing + self.freq_bands['bass'] * (1 - smoothing)
        self.mid_smooth = self.mid_smooth * smoothing + self.freq_bands['mid'] * (1 - smoothing)
        self.treble_smooth = self.treble_smooth * smoothing + self.freq_bands['treble'] * (1 - smoothing)
        
        # Calcular intensidad del beat (cambios súbitos en graves)
        bass_change = abs(self.freq_bands['bass'] - self.bass_smooth)
        self.beat_intensity = max(0, bass_change * 2.0)
        
    def generate_deformed_blob_points(self):
        """Genera puntos del perímetro deformado del blob según el audio"""
        points = []
        
        # Radio base dinámico según volumen
        base_radius = self.blob['base_radius'] * (0.5 + self.volume_smooth * 1.5)
        
        for i in range(self.num_points):
            angle = (i / self.num_points) * 2 * math.pi
            
            # Deformaciones según diferentes frecuencias (aplicando multiplicador de intensidad)
            
            # Graves: deformación lenta y amplia (ondas largas)
            bass_deform = self.bass_smooth * 30 * self.deformation_intensity * math.sin(angle * 2 + self.time * 2)
            
            # Medios: deformación media (ondas medianas)
            mid_deform = self.mid_smooth * 20 * self.deformation_intensity * math.sin(angle * 4 + self.time * 3)
            
            # Agudos: deformación rápida y pequeña (ondas cortas)
            treble_deform = self.treble_smooth * 15 * self.deformation_intensity * math.sin(angle * 8 + self.time * 5)
            
            # Beat: pulsaciones súbitas
            beat_deform = self.beat_intensity * 25 * self.deformation_intensity * math.sin(angle * 3)
            
            # Movimiento orgánico base
            organic_deform = 10 * self.deformation_intensity * math.sin(angle * 3 + self.time * 1.5) * math.cos(angle * 2 + self.time)
            
            # Radio final con todas las deformaciones
            total_deform = bass_deform + mid_deform + treble_deform + beat_deform + organic_deform
            radius = base_radius + total_deform
            
            # Asegurar radio mínimo
            radius = max(30, radius)
            
            # Calcular posición del punto
            x = self.blob['x'] + radius * math.cos(angle)
            y = self.blob['y'] + radius * math.sin(angle)
            
            points.append((x, y))
            
        return points
        
    def get_dynamic_color(self):
        """Calcula el color dinámico basado en las frecuencias"""
        # Color base según predominancia de frecuencias
        
        # Rojo para graves
        red = int(255 * self.bass_smooth)
        
        # Verde para medios  
        green = int(255 * self.mid_smooth)
        
        # Azul para agudos
        blue = int(255 * self.treble_smooth)
        
        # Intensidad mínima para visibilidad
        red = max(50, red)
        green = max(50, green)
        blue = max(50, blue)
        
        # Modulación temporal para variación
        time_mod = (math.sin(self.time * 2) + 1) / 2
        red = int(red * (0.7 + 0.3 * time_mod))
        green = int(green * (0.7 + 0.3 * math.sin(self.time * 2.5 + 1)))
        blue = int(blue * (0.7 + 0.3 * math.sin(self.time * 3 + 2)))
        
        return (red, green, blue)
        
    def draw_smooth_blob(self, points, color):
        """Dibuja el blob con curvas suaves usando splines"""
        if len(points) < 3:
            return
            
        # Crear puntos de control para curvas Bezier
        smooth_points = []
        num_segments = len(points)
        
        for i in range(num_segments):
            p0 = points[i]
            p1 = points[(i + 1) % num_segments]
            p2 = points[(i + 2) % num_segments]
            
            # Interpolar varios puntos entre cada par de puntos originales
            for t in np.linspace(0, 1, 8):  # 8 puntos interpolados por segmento
                # Interpolación cuadrática simple para suavizar
                x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
                y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
                smooth_points.append((x, y))
        
        # Dibujar el blob relleno
        if len(smooth_points) > 2:
            pygame.draw.polygon(self.screen, color, smooth_points)
            
            # Borde más brillante
            border_color = tuple(min(255, c + 50) for c in color)
            pygame.draw.polygon(self.screen, border_color, smooth_points, 3)
    
    def draw(self, audio_data):
        # Fondo negro
        self.screen.fill((0, 0, 0))
        
        # Obtener datos de audio
        freq_data = self.audio_manager.get_frequency_data(audio_data)
        if len(freq_data) == 0:
            freq_data = np.zeros(512)
            
        volume = self.audio_manager.get_volume(audio_data)
        volume_normalized = min(1.0, volume / 32768.0)
        
        # Actualizar tiempo
        self.time += 0.05
        
        # Analizar bandas de frecuencia
        self.analyze_frequency_bands(freq_data)
        
        # Suavizar valores
        self.smooth_values(volume_normalized)
        
        # Generar puntos deformados del blob
        blob_points = self.generate_deformed_blob_points()
        
        # Obtener color dinámico
        blob_color = self.get_dynamic_color()
        
        # Dibujar el blob
        self.draw_smooth_blob(blob_points, blob_color)
        
        # Efecto de centro brillante
        center_intensity = (self.volume_smooth + self.beat_intensity) * 0.5
        if center_intensity > 0.1:
            center_color = tuple(min(255, int(c * 1.5)) for c in blob_color)
            center_radius = int(20 * center_intensity)
            pygame.draw.circle(self.screen, center_color, 
                             (int(self.blob['x']), int(self.blob['y'])), 
                             center_radius)
        
        return self.screen
    
    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()
        self.center_x = width // 2
        self.center_y = height // 2
        self.blob['x'] = self.center_x
        self.blob['y'] = self.center_y
        
    def set_deformation_intensity(self, intensity):
        """
        Ajusta la intensidad de deformación del blob
        Args:
            intensity (float): Multiplicador de deformación
                - 0.5 = Deformación suave
                - 1.0 = Deformación normal
                - 2.0 = Deformación intensa
                - 3.0 = Deformación extrema
        """
        self.deformation_intensity = max(0.1, intensity)  # Mínimo 0.1 para evitar que desaparezca
        
    def get_deformation_intensity(self):
        """Obtiene la intensidad de deformación actual"""
        return self.deformation_intensity