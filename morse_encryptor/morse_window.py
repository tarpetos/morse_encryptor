import os
import tkinter as tk
import customtkinter as ctk
import pygame

from typing import Dict, Any

from .alphabet import MORSE_CODE_DICT
from .encryption_decryption import encrypt, decrypt


class Window(ctk.CTk):
    ENGLISH: str = 'EN'
    CYRILLIC_DEFAULT: str = 'CYRILLIC'
    UKRAINIAN: str = 'UA'
    RUSSIAN: str = 'RU'
    OTHER: str = 'OTHER'

    def __init__(self):
        super().__init__()
        self.entry_enc_modifier = tk.StringVar()
        self.entry_dec_modifier = tk.StringVar()
        self.radio_button_selector = tk.StringVar()

        self.entry_enc_modifier.trace('w', self.entry_modified)
        self.entry_dec_modifier.trace('w', self.entry_modified)

        self.entry_enc = ctk.CTkEntry(self, textvariable=self.entry_enc_modifier)
        self.entry_dec = ctk.CTkEntry(self, textvariable=self.entry_dec_modifier)

        self.entry_enc.bind('<Button-3>', self.activate_entry_enc)
        self.entry_dec.bind('<Button-3>', self.activate_entry_dec)

        self.radio_button_selector.set(self.ENGLISH)
        self.en_radio_button = self.radio_button_creator(self.ENGLISH)
        self.ua_radio_button = self.radio_button_creator(self.UKRAINIAN)
        self.ru_radio_button = self.radio_button_creator(self.RUSSIAN)

        # default activation of encryption field
        self.entry_dec.configure(state='readonly')
        self.entry_activated = 'enc'
        self.en_radio_button.select()

        # decrypted symbols sounds initialization
        pygame.mixer.init()
        short_sound_path = os.path.join('sounds', 'short.mp3')
        long_sound_path = os.path.join('sounds', 'long.mp3')
        self.dot_sound = pygame.mixer.Sound(short_sound_path)
        self.dash_sound = pygame.mixer.Sound(long_sound_path)
        self.max_dec_length = 0

        self.place_elements()

    def place_elements(self):
        self.entry_enc.pack(fill=tk.BOTH, expand=True)
        self.entry_dec.pack(fill=tk.BOTH, expand=True)
        self.en_radio_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ua_radio_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ru_radio_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def radio_button_creator(self, language: str) -> ctk.CTkRadioButton:
        return ctk.CTkRadioButton(
            self, text=language, value=language, variable=self.radio_button_selector,
            command=lambda: self.radio_button_entries_reloader(language)
        )

    def radio_button_entries_reloader(self, language: str):
        self.radio_button_selector.set(language)
        working_dict = self.alphabet_creator(language)

        if self.entry_activated == 'enc':
            self.reload_entries(self.entry_enc, self.entry_dec, encrypt, working_dict)
        elif self.entry_activated == 'dec':
            self.reload_entries(self.entry_dec, self.entry_enc, decrypt, working_dict)

    def reload_entries(
            self, source_entry: ctk.CTkEntry, target_entry: ctk.CTkEntry, function, working_dict: Dict[str, str]
    ):
        current_data = source_entry.get()
        source_entry.delete(0, tk.END)
        target_entry.delete(0, tk.END)
        source_entry_modifier = self.entry_enc_modifier if source_entry == self.entry_enc else self.entry_dec_modifier
        target_entry_modifier = self.entry_dec_modifier if target_entry == self.entry_dec else self.entry_enc_modifier
        source_entry_modifier.set(current_data)
        target_entry_modifier.set(function(current_data, working_dict))

    def activate_entry_enc(self, event: Any):
        self.entry_enc.configure(state='normal')
        self.entry_dec.configure(state='readonly')
        self.entry_activated = 'enc'

    def activate_entry_dec(self, event: Any):
        self.entry_dec.configure(state='normal')
        self.entry_enc.configure(state='readonly')
        self.entry_activated = 'dec'

    def entry_modified(self, *args):
        user_choice = self.radio_button_selector.get()
        working_dict = self.alphabet_creator(user_choice)

        if self.entry_activated == 'enc':
            data = self.entry_enc.get()
            self.entry_dec_modifier.set(encrypt(data, working_dict))
        elif self.entry_activated == 'dec':
            data = self.entry_dec.get()
            self.play_sound(data)
            self.entry_enc_modifier.set(decrypt(data, working_dict))

    def alphabet_creator(self, selector_choice: str) -> Dict[str, str]:
        result_dict = {}

        if selector_choice == self.ENGLISH:
            result_dict.update(MORSE_CODE_DICT[selector_choice])
        else:
            result_dict.update(MORSE_CODE_DICT[self.CYRILLIC_DEFAULT])
            result_dict.update(MORSE_CODE_DICT[selector_choice])

        result_dict.update(MORSE_CODE_DICT[self.OTHER])

        return result_dict

    def play_sound(self, data: str):
        temp_length = len(data)
        if temp_length > self.max_dec_length:
            self.dash_sound.play() if data.endswith('-') else (self.dot_sound.play() if data.endswith('.') else ...)
        self.max_dec_length = temp_length
