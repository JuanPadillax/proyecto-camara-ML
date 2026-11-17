import numpy as np
import sounddevice as sd

class AudioDetector:
    def __init__(self, sample_rate=44100, block_size=2048):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.audio_status = "Inicializando..."
        self.volume_level = 0.0
        self.stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            return
        
        # Calcular la energía del sonido mediante RMS (Root Mean Square)
        rms = np.sqrt(np.mean(indata**2))
        self.volume_level = float(rms)
        
        # Clasificación en tiempo real basada en la energía espectral
        if rms < 0.015:
            self.audio_status = "SILENCIO"
        elif rms < 0.07:
            self.audio_status = "VOZ / AMBIENTE"
        else:
            self.audio_status = "MUSICA DETECTADA"

    def start(self):
        """Inicia la escucha del micrófono en segundo plano."""
        try:
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                callback=self._audio_callback
            )
            self.stream.start()
        except Exception as e:
            self.audio_status = "Error de Microfono"

    def stop(self):
        """Detiene la captura de audio limpiamente."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
    def get_bar_length(self, max_width=150):
        """Retorna el largo de la barra de volumen para el HUD."""
        scaled = int(self.volume_level * 1000)
        return min(scaled, max_width)