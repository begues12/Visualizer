from Effects.effect import Effect
import pygame

class BackgroundColor(Effect):
    
    def __init__(self, visualizer):
        super().__init__(
            "Background Color",
            visualizer,
            visualizer.get_screen()
            )
        self.audio_manager = visualizer.get_audio_manager()
        self.screen = visualizer.get_screen()
        self.config = {
            "high_volume_threshold": 10000
        }
        self.config_file = "Effects/configs/background_color_config.json"
        self.load_config_from_file(self.config_file)

    
    def draw(self, audio_data):
        high_volume_threshold = 10000  
        if self.audio_manager.get_volume(audio_data) > high_volume_threshold:
            color = self.random_color()
        else:
            color = (0, 0, 0)  

        self.screen.fill(color)
        
    def on_screen_resize(self, width, height):
        self.screen = self.visualizer.get_screen()
