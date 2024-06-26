class VisualizerManager:
    
    running = False
    visualizer = None
    
    audioManager = None
    
    def __init__(self, visualizer):
        self.visualizer = visualizer

    def visualize(self, data):
        self.visualizer.visualize(data)