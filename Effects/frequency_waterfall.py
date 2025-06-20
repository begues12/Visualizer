import pygame
import random
import math
import time
from Effects.effect import Effect

class FrequencyWaterfall(Effect):
    def __init__(self, visualizer):
        super().__init__("Frequency Waterfall", visualizer, visualizer.get_screen())
        self.config_file = "Effects/configs/frequency_waterfall_config.json"
        self.load_config_from_file(self.config_file)
        self.color_base = (0, 100, 255)  # Base de color azul para las gotas de agua
        self.particle_list = []  # Lista para almacenar las partículas
        self.audio_manager = visualizer.get_audio_manager()
        # Configuración por defecto si no se carga desde el archivo
        if "particle_speed" not in self.config:
            self.config["particle_speed"] = 5
        if "max_particle_size" not in self.config:
            self.config["max_particle_size"] = 5
        if "color_intensity_increment" not in self.config:
            self.config["color_intensity_increment"] = 100

    def update_particles(self, volume, freq_data):
        if random.randint(0, 10) < volume / 1000:
            new_particle = {
                "pos": (random.randint(0, self.width), 0),
                "velocity": volume / 8000 + freq_data[10] / 256 * self.config["particle_speed"],
                "color": (self.color_base[0], self.color_base[1], min(255, self.color_base[2] + volume / self.config["color_intensity_increment"]))
            }
            self.particle_list.append(new_particle)

        for particle in self.particle_list:
            particle["pos"] = (particle["pos"][0], particle["pos"][1] + particle["velocity"])
            if particle["pos"][1] > self.height:
                self.particle_list.remove(particle)

    def draw(self, audio_data):
        self.screen.fill((0, 0, 0))  # Limpiar pantalla para la nueva frame
        freq_data = self.audio_manager.getFrequencyData()
        volume = self.audio_manager.get_volume(audio_data)

        self.update_particles(volume, freq_data)

        for particle in self.particle_list:
            pygame.draw.circle(self.screen, particle["color"], (int(particle["pos"][0]), int(particle["pos"][1])), self.config["max_particle_size"])
