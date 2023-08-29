import os
import customtkinter as ctk
from pygame.mixer import Sound, init

from typing import Dict, Any

from .alphabet import MORSE_CODE_DICT
from .audio_transformer import (
    DEFAULT_AUDIO_FORMAT,
    LONG_SOUND,
    SHORT_SOUND,
    AudioBuilder,
    AudioController,
    binary_reader,
    SAVE_DIR,
)
from .encryption_decryption import encrypt, decrypt


class Window(ctk.CTk):
    ENGLISH: str = "EN"
    CYRILLIC_DEFAULT: str = "CYRILLIC"
    UKRAINIAN: str = "UA"
    RUSSIAN: str = "RU"
    OTHER: str = "OTHER"

    def __init__(self):
        super().__init__()
        self.main_frame = ctk.CTkFrame(self)

        self.entry_enc_modifier = ctk.StringVar()
        self.entry_dec_modifier = ctk.StringVar()
        self.radio_button_selector = ctk.StringVar()

        self.entry_enc_modifier.trace("w", self.entry_modified)
        self.entry_dec_modifier.trace("w", self.entry_modified)

        self.entry_enc = ctk.CTkEntry(
            self.main_frame, textvariable=self.entry_enc_modifier, font=("Georgia", 20)
        )
        self.entry_dec = ctk.CTkEntry(
            self.main_frame, textvariable=self.entry_dec_modifier, font=("Georgia", 20)
        )

        self.entry_enc.bind("<Button-3>", self.activate_entry_enc)
        self.entry_dec.bind("<Button-3>", self.activate_entry_dec)

        self.radio_button_selector.set(self.ENGLISH)
        self.en_radio_button = self.radio_button_creator(self.ENGLISH)
        self.ua_radio_button = self.radio_button_creator(self.UKRAINIAN)
        self.ru_radio_button = self.radio_button_creator(self.RUSSIAN)

        # default activation of encryption field
        self.entry_dec.configure(state="readonly")
        self.entry_activated = "enc"
        self.en_radio_button.select()

        self.max_dec_length = 0
        self.place_elements()

    def place_elements(self):
        self.entry_enc.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)
        self.entry_dec.pack(fill=ctk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.en_radio_button.pack(
            side=ctk.LEFT, fill=ctk.BOTH, expand=True, pady=(0, 5), padx=(75, 0)
        )
        self.ua_radio_button.pack(
            side=ctk.LEFT, fill=ctk.BOTH, expand=True, pady=(0, 5)
        )
        self.ru_radio_button.pack(
            side=ctk.LEFT, fill=ctk.BOTH, expand=True, pady=(0, 5)
        )
        self.main_frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

    def radio_button_creator(self, language: str) -> ctk.CTkRadioButton:
        return ctk.CTkRadioButton(
            self.main_frame,
            text=language,
            value=language,
            variable=self.radio_button_selector,
            command=lambda: self.radio_button_entries_reloader(language),
        )

    def radio_button_entries_reloader(self, language: str):
        self.radio_button_selector.set(language)
        working_dict = self.alphabet_creator(language)

        if self.entry_activated == "enc":
            self.reload_entries(self.entry_enc, self.entry_dec, encrypt, working_dict)
        elif self.entry_activated == "dec":
            self.reload_entries(self.entry_dec, self.entry_enc, decrypt, working_dict)

    def reload_entries(
        self,
        source_entry: ctk.CTkEntry,
        target_entry: ctk.CTkEntry,
        function,
        working_dict: Dict[str, str],
    ):
        current_data = source_entry.get()
        source_entry.delete(0, ctk.END)
        target_entry.delete(0, ctk.END)
        source_entry_modifier = (
            self.entry_enc_modifier
            if source_entry == self.entry_enc
            else self.entry_dec_modifier
        )
        target_entry_modifier = (
            self.entry_dec_modifier
            if target_entry == self.entry_dec
            else self.entry_enc_modifier
        )
        source_entry_modifier.set(current_data)
        target_entry_modifier.set(function(current_data, working_dict))

    def activate_entry_enc(self, event: Any):
        self.entry_enc.configure(state="normal")
        self.entry_dec.configure(state="readonly")
        self.entry_activated = "enc"

    def activate_entry_dec(self, event: Any):
        self.entry_dec.configure(state="normal")
        self.entry_enc.configure(state="readonly")
        self.entry_activated = "dec"

    def entry_modified(self, *args):
        user_choice: str = self.radio_button_selector.get()
        working_dict: Dict[str, str] = self.alphabet_creator(user_choice)

        if self.entry_activated == "enc":
            data: str = self.entry_enc.get()
            self.entry_dec_modifier.set(encrypt(data, working_dict))
        elif self.entry_activated == "dec":
            data: str = self.entry_dec.get()
            self.play_sound(data)
            self.entry_enc_modifier.set(decrypt(data, working_dict))

    def alphabet_creator(self, selector_choice: str) -> Dict[str, str]:
        result_dict: Dict = {}

        if selector_choice == self.ENGLISH:
            result_dict.update(MORSE_CODE_DICT[selector_choice])
        else:
            result_dict.update(MORSE_CODE_DICT[self.CYRILLIC_DEFAULT])
            result_dict.update(MORSE_CODE_DICT[selector_choice])

        result_dict.update(MORSE_CODE_DICT[self.OTHER])

        return result_dict

    def load_sound(self):
        full_long_sound_path = os.path.join(SAVE_DIR, f"{LONG_SOUND}.{DEFAULT_AUDIO_FORMAT}")
        full_short_sound_path = os.path.join(SAVE_DIR, f"{SHORT_SOUND}.{DEFAULT_AUDIO_FORMAT}")

        if os.path.exists(full_long_sound_path) and os.path.exists(full_short_sound_path):
            return full_long_sound_path, full_short_sound_path

        self.build_audio_from_binary(LONG_SOUND)
        self.build_audio_from_binary(SHORT_SOUND)

    def play_sound(self, data: str):
        self.load_sound()
        init()
        short_sound_path: str = os.path.join(SAVE_DIR, f"{SHORT_SOUND}.{DEFAULT_AUDIO_FORMAT}")
        long_sound_path: str = os.path.join(SAVE_DIR, f"{LONG_SOUND}.{DEFAULT_AUDIO_FORMAT}")
        dot_sound: Sound = Sound(short_sound_path)
        dash_sound: Sound = Sound(long_sound_path)

        temp_length = len(data)

        if temp_length > self.max_dec_length:
            dash_sound.play() if data.endswith("-") else (
                dot_sound.play() if data.endswith(".") else ...
            )
        self.max_dec_length = temp_length

    # def sound_loader(self, data: str):
    #     self.play_sound(data)

    @staticmethod
    def build_audio_from_binary(sound_name: str):
        audio_builder = AudioBuilder()
        audio_controller = AudioController(f"{sound_name}")
        file_data = binary_reader(f"{sound_name}")
        audio_controller.execute(audio_builder, binary_data=file_data)
