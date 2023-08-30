import os
import platform
import struct
import sys
from abc import ABC, abstractmethod
from typing import Any

import pydub
from pydub import AudioSegment


def get_binary_file_path(filename) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "morse_encryptor", filename)
    return os.path.join(os.path.dirname(__file__), filename)


SOUND_PATH = get_binary_file_path("sounds/")
SAVE_DIR = (
    os.path.expanduser("~/.Morse (De)Coder Sounds/")
    if platform.system() == "Linux"
    else os.path.expandvars(
        "C:/Users/$USERNAME/AppData/Roaming/.Morse (De)Coder Sounds/"
    )
)
LONG_SOUND = "long"
SHORT_SOUND = "short"
DEFAULT_AUDIO_FORMAT = "wav"
DEFAULT_BINARY_FORMAT = "bin"


class AudioTransformer(ABC):
    @abstractmethod
    def convert(self, filename: str, **kwargs) -> bytes | AudioSegment:
        pass

    @abstractmethod
    def save_file(self, data: bytes | Any, filename: str, **kwargs) -> None:
        pass


class AudioConverter(AudioTransformer):
    def convert(self, filename: str, path: str = SOUND_PATH, **kwargs) -> bytes:
        audio_file = os.path.join(path, f"{filename}.{DEFAULT_AUDIO_FORMAT}")
        audio = pydub.AudioSegment.from_mp3(audio_file)
        binary_data = audio.raw_data

        return binary_data

    def save_file(
        self, binary_data: bytes, filename: str, path: str = SOUND_PATH
    ) -> None:
        binary_full_path = os.path.join(path, f"{filename}.{DEFAULT_BINARY_FORMAT}")
        with open(binary_full_path, "wb") as bin_file:
            bin_file.write(binary_data)


class AudioBuilder(AudioTransformer):
    DEFAULT_FRAME_RATE = 8000
    DEFAULT_SAMPLE_WIDTH = 1
    DEFAULT_CHANNELS_NUM = 1

    def convert(
        self, filename: str, binary_data: bytes = None, path: str = SOUND_PATH
    ) -> AudioSegment:
        unpacked_data = struct.unpack(f"{len(binary_data)}B", binary_data)
        audio_segment = pydub.AudioSegment(
            data=bytes(unpacked_data),
            frame_rate=self.DEFAULT_FRAME_RATE,
            sample_width=self.DEFAULT_SAMPLE_WIDTH,
            channels=self.DEFAULT_CHANNELS_NUM,
        )
        return audio_segment

    def save_file(self, data: Any, filename: str, path: str = SAVE_DIR) -> None:
        self.check_save_path()
        full_path = os.path.join(path, f"{filename}.{DEFAULT_AUDIO_FORMAT}")
        data.export(full_path, format=f"{DEFAULT_AUDIO_FORMAT}")

    @staticmethod
    def check_save_path():
        if not os.path.exists(SAVE_DIR):
            os.mkdir(SAVE_DIR)


class AudioController:
    def __init__(self, filename: str):
        self.filename = filename

    def execute(self, audio_transformer: AudioTransformer, **kwargs) -> None:
        data = audio_transformer.convert(self.filename, **kwargs)
        audio_transformer.save_file(data, self.filename)


def binary_reader(filename: str, path: str = SOUND_PATH) -> bytes:
    binary_full_path = os.path.join(path, f"{filename}.{DEFAULT_BINARY_FORMAT}")
    with open(binary_full_path, "rb") as bin_file:
        file_data = bin_file.read()

    return file_data
