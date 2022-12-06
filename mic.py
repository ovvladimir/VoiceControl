import sounddevice as sd
import numpy as np
from threading import Thread
from settings import *


class Microphone:
    def __init__(self):
        self.stream = sd.InputStream(channels=2, callback=self.audio_callback)
        self.duration = 0

    def start(self):
        Thread(target=self.update_frame, args=()).start()

    def update_frame(self):
        with self.stream:
            while self.stream:
                sd.sleep(self.duration)
                # if self.duration == 0: pass

    def audio_callback(self, indata, frames, time, status):
        self.volume_norm = np.linalg.norm(indata) * MAX_VOLUME
