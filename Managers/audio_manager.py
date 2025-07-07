import pyaudio
import numpy as np
import threading

class AudioManager:
    RATE = 44100
    CHUNK = 2048  # Puedes probar 4096 para más suavidad
    CHANNELS = 1
    FORMAT = pyaudio.paInt16

    def __init__(self, device_index=None):
        self.p = pyaudio.PyAudio()
        self.device_index = device_index if device_index is not None else self._get_default_input_device()
        self.stream = self._open_stream()
        self.sensitivity = 0.5
        self.max_volume = np.iinfo(np.int16).max  # 32767 para int16

        # Buffer de audio y control de hilo
        self.latest_audio = np.zeros(self.CHUNK, dtype=np.int16)
        self.running = True
        self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.audio_thread.start()

    def _get_default_input_device(self):
        """Intenta encontrar un dispositivo de entrada válido (micrófono)."""
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev.get('maxInputChannels', 0) > 0:
                print(f"[AudioManager] Usando dispositivo de entrada: {dev['name']} (index {i})")
                return i
        print("[AudioManager] No se encontró dispositivo de entrada. Usando index 0.")
        return 0

    def _open_stream(self):
        """Abre el stream de audio, con manejo de errores."""
        try:
            return self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.CHUNK
            )
        except Exception as e:
            print(f"[AudioManager] Error al abrir el stream de audio: {e}")
            return None

    def _audio_loop(self):
        """Hilo que lee audio continuamente para suavidad."""
        while self.running:
            if self.stream is None:
                self.stream = self._open_stream()
                if self.stream is None:
                    self.latest_audio = np.zeros(self.CHUNK, dtype=np.int16)
                    continue
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.latest_audio = np.frombuffer(data, dtype=np.int16)
            except Exception as e:
                print(f"[AudioManager] Error leyendo audio: {e}")
                self.stream = None
                self.latest_audio = np.zeros(self.CHUNK, dtype=np.int16)

    def get_audio_data(self):
        """Devuelve el último chunk de audio leído por el hilo."""
        return self.latest_audio

    def get_frequency_data(self, audio_data=None):
        """Devuelve el espectro de frecuencias del audio."""
        if audio_data is None:
            audio_data = self.get_audio_data()
        audio_data = audio_data.astype(np.float32)
        frequency_data = np.fft.fft(audio_data)
        magnitude = np.abs(frequency_data)
        return magnitude[:len(magnitude)//2]  # Solo frecuencias positivas

    def get_volume(self, audio_data=None):
        """Devuelve el volumen normalizado del audio."""
        if audio_data is None:
            audio_data = self.get_audio_data()
        audio_data = audio_data.astype(np.int32)
        volume_level = np.max(np.abs(audio_data)) * self.sensitivity
        return float(volume_level)

    def set_sensitivity(self, value):
        """Permite ajustar la sensibilidad del volumen."""
        self.sensitivity = float(np.clip(value, 0.0, 10.0))

    def close(self):
        """Cierra el stream de audio de forma segura."""
        self.running = False
        try:
            if self.stream and self.stream.is_active():
                self.stream.stop_stream()
            if self.stream:
                self.stream.close()
            self.p.terminate()
        except Exception as e:
            print(f"[AudioManager] Error cerrando el stream de audio: {e}")