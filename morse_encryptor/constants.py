import os
import platform
import sys


def get_binary_file_path(filename) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "morse_encryptor", filename)
    return os.path.join(os.path.dirname(__file__), filename)


def platform_depending_save_folder() -> str:
    sounds_folder_name = ".Morse (De)Coder Sounds/"

    if platform.system() == "Linux" or platform.system() == "MacOS":
        return os.path.expanduser(f"~/{sounds_folder_name}")
    elif platform.system() == "Windows":
        return os.path.expanduser(f"~/AppData/Roaming/{sounds_folder_name}")
        # return os.path.expandvars(f"C:/Users/$USERNAME/AppData/Roaming/{sounds_folder_name}/")


class AudioConstants:
    SOUND_PATH = get_binary_file_path("sounds/")
    SAVE_DIR = platform_depending_save_folder()
    LONG_SOUND = "long"
    SHORT_SOUND = "short"
    DEFAULT_AUDIO_FORMAT = "wav"
    DEFAULT_BINARY_FORMAT = "bin"


class MorseConstants:
    ENGLISH = "EN"
    CYRILLIC_DEFAULT = "CYRILLIC"
    UKRAINIAN = "UA"
    RUSSIAN = "RU"
    OTHER = "OTHER"
    LONG_SYMBOL = "-"
    SHORT_SYMBOL = "."
    PLAY_TEXT = "\u25B6"
    STOP_TEXT = "STOP"
    PAUSE_BETWEEN_SOUNDS_MS = 200
    DEFAULT_FONT_STYLE_NAME = "Georgia"
    DEFAULT_FONT_SIZE = 20
    MESSAGEBOX_EXIT_TIMEOUT_MS = 500
