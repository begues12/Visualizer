import random
import json

class Effect:
    def __init__(self, effect_name, visualizer, screen):
        self.effect_name = effect_name  
        self.visualizer = visualizer 
        self.config = {}
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2
        self.config_file = ""
        
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
    
    def save_config_to_file(self, file_path):
        with open(self.config_file, 'w') as file:
            json.dump(self.config_file, file)
    
    def load_config_from_file(self, file_path):
        self.check_config(self.config_file)
        
        with open(file_path, 'r') as file:
            self.config = json.load(file)
            