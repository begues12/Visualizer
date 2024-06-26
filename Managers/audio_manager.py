import pyaudio
import numpy as np

class AudioManager:
    
    p = pyaudio.PyAudio()
    volume = 0.5
    rate = 44100
    sensitivity = 0.5
    chunk = 1024
    channels = 1
    max_volume = 32768
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)
    
    def __init__(self):
        pass
    
    def getAudioData(self):
        return np.frombuffer(self.stream.read(self.chunk), dtype=np.int16)
    
    def setVolume(self, volume):
        self.volume = volume

    def getVolume(self):
        return max(abs(self.getAudioData().min()), abs(self.getAudioData().max())) * self.sensitivity