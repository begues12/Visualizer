import random

class Effect:
    def __init__(self, effect_name, visualizer, particle_manager):
        self.effect_name = effect_name  
        self.visualizer = visualizer 
        self.config = {}
    
    def save_config(self, config):
        self.config = config
        
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
