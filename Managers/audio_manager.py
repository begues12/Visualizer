import pyaudio
import numpy as np

class AudioManager:
    # Constantes de clase para configuración de PyAudio
    RATE = 44100
    CHUNK = 1024
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    MAX_VOLUME = 32768

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)
        self.volume = 0.5
        self.sensitivity = 0.5
        self.max_volume = 32768

    def getFrequencyData(self):
        audio_data = self.getAudioData()
        # Apply FFT and return the magnitude (absolute value) of the FFT result
        frequency_data = np.fft.fft(audio_data)
        magnitude = np.abs(frequency_data)  # Convert complex numbers to real numbers (magnitude)
        return magnitude
    
    
    def getAudioData(self):
        try:
            data = self.stream.read(self.CHUNK)
            return np.frombuffer(data, dtype=np.int16)
        except IOError as e:
            print(f"Error reading audio data: {e}")
            return np.zeros(self.CHUNK, dtype=np.int16)

    def getVolume(self):
        audio_data = self.getAudioData()
        volume_level = max(abs(audio_data.min()), abs(audio_data.max())) * self.sensitivity
        return volume_level

    def setVolume(self, volume):
        self.volume = volume

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
