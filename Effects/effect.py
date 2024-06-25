class Effect:
    def __init__(self, effect_name, visualizer, particle_manager):
        self.effect_name = effect_name  # Nombre del efecto
        self.visualizer = visualizer  # Referencia al objeto Visualizer para acceder a sus atributos
        self.config = {}
        
    def draw(self, audio_data):
        raise NotImplementedError("This method should be overridden by subclasses.")
