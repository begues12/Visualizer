import random
import json

class Effect:
    def __init__(self, effect_name, visualizer, particle_manager):
        self.effect_name = effect_name  
        self.visualizer = visualizer 
        self.config = {}
    
    def get_config(self):
        return self.config
    
    def save_config(self, config):
        self.config = config
    
    def set_index_color(self, n):
        # ZeroDivisionError: integer division or modulo by zero
        if n == 0:
            n = 1
            
        self.color = (255 // n + 1, 255 // n + 1, 255 // n  + 1)
    
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
    
    def save_config_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.config, file)
    
    def load_config_from_file(self, file_path):
        self.check_config(file_path)
        
        with open(file_path, 'r') as file:
            self.config = json.load(file)
            