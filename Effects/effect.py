import random
import json
import pygame
import numpy as np

class Effect:
    def __init__(self, effect_name, visualizer, screen):
        self.effect_name = effect_name
        self.visualizer = visualizer
        self.config = {}
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2
        self.config_file = ""
        self._layers = {}

    def detect_beat(self, audio_data, sensitivity=1.4, cooldown=100):
        """Detecta un golpe de graves (energia instantanea vs media reciente).
        Devuelve (es_golpe, fuerza 0..1). Compartido por los efectos agresivos.
        """
        am = self.visualizer.get_audio_manager()
        freq = am.get_frequency_data(audio_data)
        if len(freq) == 0:
            return False, 0.0
        bass = float(np.mean(freq[:max(1, len(freq) // 8)]))
        hist = getattr(self, "_beat_hist", None)
        if hist is None:
            hist = []
            self._beat_hist = hist
        hist.append(bass)
        if len(hist) > 43:
            hist.pop(0)
        avg = sum(hist) / len(hist)
        now = pygame.time.get_ticks()
        ratio = bass / (avg + 1e-6)
        if ratio > sensitivity and now - getattr(self, "_beat_last", 0) > cooldown:
            self._beat_last = now
            return True, float(min(1.0, max(0.3, (ratio - sensitivity) + 0.4)))
        return False, 0.0

    def get_layer(self, name="main", clear=True):
        """Devuelve una superficie SRCALPHA del tamano de la pantalla, reutilizada
        entre frames (evita reservar memoria cada frame -> clave en Raspberry Pi).
        """
        size = self.visualizer.get_screen().get_size()
        layer = self._layers.get(name)
        if layer is None or layer.get_size() != size:
            layer = pygame.Surface(size, pygame.SRCALPHA)
            self._layers[name] = layer
        elif clear:
            layer.fill((0, 0, 0, 0))
        return layer
        
    def get_width(self):    
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_center_x(self):
        return self.center_x
    
    def get_center_y(self):
        return self.center_y
    
    def get_config(self):
        return self.config
    
    def save_config(self, config):
        self.config = config
    
    def set_index_color(self, n):
        # ZeroDivisionError: integer division or modulo by zero
        if n == 0:
            n = 1
            
        self.color = (255 // n + 1, 255 // n + 1, 255 // n  + 1)
        return self.color
    
    def on_screen_resize(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
    
    def get_config(self):
        return self.config
    
    def set_color(self, color):
        self.color = color
    
    def random_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    def get_effect_name(self):
        return self.effect_name
    
    def draw(self, audio_data):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def check_config(self, file_path):
        # If not exists, create a new file
        try:
            with open(file_path, 'r') as file:
                pass
        except FileNotFoundError:
            with open(file_path, 'w') as file:
                json.dump(self.config, file)
    
    def get_config_file(self):
        return self.config_file
    
    def save_config_to_file(self, file_path=None):
        path = file_path or self.config_file
        with open(path, 'w') as file:
            json.dump(self.config, file, indent=4)
    
    def load_config_from_file(self, file_path):
        self.check_config(self.config_file)

        with open(file_path, 'r') as file:
            data = json.load(file)
        # Mezcla en vez de reemplazar: conserva las claves definidas en el codigo
        # aunque el archivo sea antiguo y no las tenga (evita KeyError al recargar).
        if isinstance(data, dict):
            self.config.update(data)
            