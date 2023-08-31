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


class SpecConstants:
    EMPTY_SPACE: str = " "
    EMPTY_STRING: str = ""
    UNKNOWN_SYMBOL: str = "𖡄 "


class AudioConstants:
    SOUND_PATH: str = get_binary_file_path("sounds/")
    SAVE_DIR: str = platform_depending_save_folder()
    LONG_SOUND: str = "long"
    SHORT_SOUND: str = "short"
    DEFAULT_AUDIO_FORMAT: str = "wav"
    DEFAULT_BINARY_FORMAT: str = "bin"


class MorseConstants:
    ENGLISH: str = "EN"
    CYRILLIC_DEFAULT: str = "CYRILLIC"
    UKRAINIAN: str = "UA"
    RUSSIAN: str = "RU"
    OTHER: str = "OTHER"
    LONG_SYMBOL: str = "-"
    SHORT_SYMBOL: str = "."
    PLAY_TEXT: str = "\u25B6"
    STOP_TEXT: str = "STOP"
    PAUSE_BETWEEN_SOUNDS_MS: int = 200
    DEFAULT_FONT_STYLE_NAME: str = "Georgia"
    DEFAULT_FONT_SIZE: int = 20
    MESSAGEBOX_EXIT_TIMEOUT_MS: int = 500
