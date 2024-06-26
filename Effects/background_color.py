from Effects.effect import Effect
import pygame

class BackgroundColor(Effect):
    
    def __init__(self, visualizer):
        super().__init__(
            "Background Color",
            visualizer,
            visualizer.particle_manager
            )
        self.audio_manager = visualizer.get_audio_manager()
        self.config = {
            "high_volume_threshold": 10000
        }

    
    def draw(self, audio_data):
        high_volume_threshold = 10000  
        if self.audio_manager.getVolume() > high_volume_threshold:
            color = self.Rcolor()  
        else:
            color = (0, 0, 0)  

        self.screen.fill(color)
