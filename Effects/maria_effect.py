import pygame
import math
import random
import numpy as np
from Effects.effect import Effect

class MariaEffect(Effect):
    def __init__(self, visualizer):
        super().__init__("Gothic Chains", visualizer, visualizer.get_screen())
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()
        
        self.config = {
            "chain_segments": 12,  # Número de eslabones por cadena
            "chain_width": 80,     # Ancho de cada cadena
            "spike_length": 25,    # Longitud de las púas góticas
            "movement_range": 150, # Rango de movimiento vertical
            "bass_sensitivity": 1.5,
            "smoothing": 0.7,
            "mask_glow_intensity": 200,  # Intensidad del brillo de la máscara
            "mask_size": 0.4  # Tamaño de la máscara relativo a la pantalla
        }
        
        # Estado de las cadenas
        self.left_chain_y = 0
        self.right_chain_y = 0
        self.target_left_y = 0
        self.target_right_y = 0
        self.time = 0
        
        # Estado de la máscara LED
        self.mask_glow = 0
        self.mask_pulse = 0
        
        # Formas góticas precalculadas
        self.gothic_spikes = self._generate_gothic_shapes()
        
    def _generate_gothic_shapes(self):
        """Genera formas púntiagudas góticas para las cadenas"""
        spikes = []
        spike_length = int(self.config["spike_length"])
        
        for i in range(8):  # 8 tipos diferentes de púas
            spike = []
            # Púa principal puntiaguda - asegurar que sean enteros
            spike.append((0, -spike_length))
            spike.append((-8, -spike_length // 2))
            spike.append((-12, 0))
            spike.append((-8, spike_length // 2))
            spike.append((0, spike_length))
            spike.append((8, spike_length // 2))
            spike.append((12, 0))
            spike.append((8, -spike_length // 2))
            spikes.append(spike)
        return spikes
    
    def draw_led_mask(self, surface, center_x, center_y, bass_energy, volume):
        """Dibuja una máscara LED estilo Purge que se ilumina con la música"""
        # Tamaño de la máscara basado en la configuración y pantalla
        screen_height = surface.get_height()
        mask_radius = int(screen_height * self.config["mask_size"] / 2)
        
        # Intensidad del brillo basada en el audio
        glow_intensity = int(self.config["mask_glow_intensity"] * (0.3 + bass_energy * 0.7))
        
        # Color base: verde neón brillante
        base_green = (0, 255, 100)
        bright_green = (100, 255, 150)
        electric_green = (150, 255, 200)
        
        # Pulsación de la máscara
        pulse_factor = 1 + 0.3 * math.sin(self.time * 0.2) + 0.2 * bass_energy
        current_radius = int(mask_radius * pulse_factor)
        
        # Dibujar resplandor exterior (múltiples círculos con alpha)
        for i in range(8):
            glow_radius = current_radius + (i * 15)
            glow_alpha = max(0, glow_intensity - (i * 25))
            if glow_alpha > 0:
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*bright_green, glow_alpha), 
                                 (glow_radius, glow_radius), glow_radius)
                surface.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius), 
                           special_flags=pygame.BLEND_ADD)
        
        # Cara base de la máscara (negro)
        pygame.draw.circle(surface, (20, 20, 20), (center_x, center_y), current_radius)
        pygame.draw.circle(surface, (40, 40, 40), (center_x, center_y), current_radius, 3)
        
        # Ojos en X - líneas LED verdes
        eye_size = current_radius // 3
        eye_offset_x = current_radius // 4
        eye_offset_y = current_radius // 6
        line_width = max(3, int(6 * (0.5 + bass_energy * 0.5)))
        
        # Ojo izquierdo (X)
        left_eye_x = center_x - eye_offset_x
        left_eye_y = center_y - eye_offset_y
        
        # X izquierda
        pygame.draw.line(surface, electric_green,
                        (left_eye_x - eye_size, left_eye_y - eye_size),
                        (left_eye_x + eye_size, left_eye_y + eye_size), line_width)
        pygame.draw.line(surface, electric_green,
                        (left_eye_x - eye_size, left_eye_y + eye_size),
                        (left_eye_x + eye_size, left_eye_y - eye_size), line_width)
        
        # Ojo derecho (X)
        right_eye_x = center_x + eye_offset_x
        right_eye_y = center_y - eye_offset_y
        
        # X derecha
        pygame.draw.line(surface, electric_green,
                        (right_eye_x - eye_size, right_eye_y - eye_size),
                        (right_eye_x + eye_size, right_eye_y + eye_size), line_width)
        pygame.draw.line(surface, electric_green,
                        (right_eye_x - eye_size, right_eye_y + eye_size),
                        (right_eye_x + eye_size, right_eye_y - eye_size), line_width)
        
        # Sonrisa cosida - línea quebrada LED
        mouth_y = center_y + current_radius // 3
        mouth_width = current_radius // 2
        segments = 8
        
        points = []
        for i in range(segments + 1):
            x = center_x - mouth_width + (i * 2 * mouth_width // segments)
            # Crear forma de sonrisa cosida
            if i % 2 == 0:
                y = mouth_y + 10
            else:
                y = mouth_y - 5
            points.append((x, y))
        
        # Dibujar línea de sonrisa segmentada
        for i in range(len(points) - 1):
            pygame.draw.line(surface, electric_green, points[i], points[i + 1], line_width)
        
        # Puntadas verticales de la sonrisa
        for i in range(0, len(points), 2):
            if i < len(points):
                stitch_x = points[i][0]
                pygame.draw.line(surface, electric_green,
                               (stitch_x, mouth_y - 15), (stitch_x, mouth_y + 15), line_width // 2)
        
        # Efectos adicionales con beats fuertes
        if bass_energy > 0.8:
            # Rayos eléctricos alrededor de la máscara
            for _ in range(int(bass_energy * 8)):
                angle = random.uniform(0, 2 * math.pi)
                start_radius = current_radius + 10
                end_radius = current_radius + 30 + random.randint(0, 20)
                
                start_x = center_x + start_radius * math.cos(angle)
                start_y = center_y + start_radius * math.sin(angle)
                end_x = center_x + end_radius * math.cos(angle)
                end_y = center_y + end_radius * math.sin(angle)
                
                pygame.draw.line(surface, bright_green, 
                               (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)
    
    def draw_chain_link(self, surface, x, y, scale=1.0, spike_type=0):
        """Dibuja un eslabón de cadena gótico con púas"""
        # Validar parámetros de entrada
        x, y = int(x), int(y)
        scale = max(0.1, scale)  # Evitar escalas muy pequeñas
        spike_type = int(spike_type) % len(self.gothic_spikes)
        
        # Colores plateados góticos
        silver_dark = (120, 120, 130)
        silver_light = (180, 180, 190)
        silver_bright = (220, 220, 230)
        
        link_width = int(self.config["chain_width"] * scale)
        link_height = int(40 * scale)
        
        # Eslabón principal (rectángulo con bordes redondeados)
        link_rect = pygame.Rect(x - link_width // 2, y - link_height // 2, link_width, link_height)
        
        # Sombra del eslabón
        shadow_rect = pygame.Rect(x - link_width // 2 + 3, y - link_height // 2 + 3, link_width, link_height)
        pygame.draw.rect(surface, (40, 40, 50), shadow_rect, border_radius=8)
        
        # Eslabón principal
        pygame.draw.rect(surface, silver_dark, link_rect, border_radius=8)
        
        # Borde brillante superior
        highlight_rect = pygame.Rect(x - link_width // 2 + 2, y - link_height // 2 + 2, link_width - 4, link_height // 3)
        pygame.draw.rect(surface, silver_light, highlight_rect, border_radius=6)
        
        # Línea brillante superior
        pygame.draw.rect(surface, silver_bright, 
                        (x - link_width // 2 + 4, y - link_height // 2 + 4, link_width - 8, 3))
        
        # Púas góticas en los lados
        spike_points = self.gothic_spikes[spike_type % len(self.gothic_spikes)]
        
        # Púa izquierda - asegurar coordenadas enteras
        left_spike = []
        for px, py in spike_points:
            x_coord = int(x - link_width // 2 + px * scale)
            y_coord = int(y + py * scale)
            left_spike.append((x_coord, y_coord))
        
        if len(left_spike) >= 3:  # Asegurar que tenemos suficientes puntos
            pygame.draw.polygon(surface, silver_dark, left_spike)
            pygame.draw.polygon(surface, silver_light, left_spike, 2)
        
        # Púa derecha (reflejada) - asegurar coordenadas enteras
        right_spike = []
        for px, py in spike_points:
            x_coord = int(x + link_width // 2 - px * scale)
            y_coord = int(y + py * scale)
            right_spike.append((x_coord, y_coord))
            
        if len(right_spike) >= 3:  # Asegurar que tenemos suficientes puntos
            pygame.draw.polygon(surface, silver_dark, right_spike)
            pygame.draw.polygon(surface, silver_light, right_spike, 2)
        
        # Detalles góticos adicionales
        # Pequeñas púas en el centro del eslabón - asegurar coordenadas enteras
        center_spikes = [
            (int(x - 8), int(y - 15)), (int(x), int(y - 20)), (int(x + 8), int(y - 15)),
            (int(x + 8), int(y + 15)), (int(x), int(y + 20)), (int(x - 8), int(y + 15))
        ]
        if len(center_spikes) >= 3:
            pygame.draw.polygon(surface, silver_bright, center_spikes)
        
    def draw_chain(self, surface, side, chain_y, volume, bass_energy):
        """Dibuja una cadena completa gótica"""
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Posición X según el lado
        if side == "left":
            chain_x = 60
        else:  # right
            chain_x = screen_width - 60
            
        # Calcular movimiento vertical de la cadena
        chain_segments = self.config["chain_segments"]
        segment_spacing = screen_height // (chain_segments + 1)
        
        # Dibujar los eslabones de la cadena
        for i in range(chain_segments):
            # Posición Y base del eslabón
            base_y = segment_spacing * (i + 1) + chain_y
            
            # Agregar oscilación individual a cada eslabón
            oscillation = math.sin(self.time * 0.1 + i * 0.5) * 15 * volume
            link_y = base_y + oscillation
            
            # Escala basada en el volumen y posición
            scale = 0.8 + volume * 0.4 + bass_energy * 0.3
            
            # Tipo de púa basado en la posición y tiempo
            spike_type = (i + int(self.time * 0.5)) % len(self.gothic_spikes)
            
            # Dibujar el eslabón
            self.draw_chain_link(surface, chain_x, int(link_y), scale, spike_type)
            
            # Conectores entre eslabones
            if i < chain_segments - 1:
                next_base_y = segment_spacing * (i + 2) + chain_y
                next_oscillation = math.sin(self.time * 0.1 + (i + 1) * 0.5) * 15 * volume
                next_link_y = next_base_y + next_oscillation
                
                # Dibujar cadena conectora - asegurar coordenadas enteras
                connector_points = [
                    (int(chain_x - 5), int(link_y + 20)),
                    (int(chain_x + 5), int(link_y + 20)),
                    (int(chain_x + 5), int(next_link_y - 20)),
                    (int(chain_x - 5), int(next_link_y - 20))
                ]
                pygame.draw.polygon(surface, (100, 100, 110), connector_points)
                
                # Brillo en el conector - asegurar coordenadas enteras
                pygame.draw.line(surface, (160, 160, 170), 
                               (int(chain_x - 3), int(link_y + 22)), 
                               (int(chain_x - 3), int(next_link_y - 22)), 2)
    
    def draw(self, audio_data):
        # Fondo negro gótico
        self.screen.fill((0, 0, 0))
        
        # Obtener datos de audio
        volume = self.audio_manager.get_volume(audio_data)
        volume_normalized = min(1.0, volume / 32768.0)
        
        freq_data = self.audio_manager.get_frequency_data(audio_data)
        if len(freq_data) == 0:
            freq_data = [0] * 512
            
        # Calcular energía de graves para movimiento dramático
        bass_bins = len(freq_data) // 6
        bass_energy = np.mean(freq_data[:bass_bins]) / 32768.0 if bass_bins > 0 else 0
        bass_energy = min(1.0, bass_energy)
        
        # Dibujar máscara LED en el centro (detrás de las cadenas)
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2
        self.draw_led_mask(self.screen, center_x, center_y, bass_energy, volume_normalized)
        
        # Calcular movimiento objetivo de las cadenas
        movement_range = self.config["movement_range"]
        
        # Cadena izquierda se mueve principalmente con graves
        self.target_left_y = bass_energy * movement_range * self.config["bass_sensitivity"] * math.sin(self.time * 0.08)
        
        # Cadena derecha se mueve con volumen general y con desfase
        self.target_right_y = volume_normalized * movement_range * math.sin(self.time * 0.06 + math.pi / 3)
        
        # Suavizar movimiento
        smoothing = self.config["smoothing"]
        self.left_chain_y = self.left_chain_y * smoothing + self.target_left_y * (1 - smoothing)
        self.right_chain_y = self.right_chain_y * smoothing + self.target_right_y * (1 - smoothing)
        
        # Dibujar ambas cadenas (encima de la máscara)
        self.draw_chain(self.screen, "left", self.left_chain_y, volume_normalized, bass_energy)
        self.draw_chain(self.screen, "right", self.right_chain_y, volume_normalized, bass_energy)
        
        # Efecto de partículas góticas ocasionales
        if bass_energy > 0.7:
            for _ in range(int(bass_energy * 5)):
                particle_x = random.randint(0, self.screen.get_width())
                particle_y = random.randint(0, self.screen.get_height())
                particle_size = random.randint(1, 3)
                # Partículas verdes para combinar con la máscara
                pygame.draw.circle(self.screen, (100, 255, 150), (particle_x, particle_y), particle_size)
        
        # Actualizar tiempo
        self.time += 1
        
    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()
