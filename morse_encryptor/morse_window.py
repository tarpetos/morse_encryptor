import os
import threading
from tkinter import messagebox

import customtkinter as ctk
import pygame

from typing import Dict, Any, Optional

from .constants import AudioConstants, MorseConstants
from .alphabet import MORSE_CODE_DICT
from .audio_transformer import (
    AudioBuilder,
    AudioController,
    binary_reader,
)
from .encryption_decryption import encrypt, decrypt, EMPTY_SPACE


class MorsePlayer:
    def __init__(self):
        pass


class MorseTranslator:
    def __init__(self):
        pass


class MorseUI:
    def __init__(self):
        pass


class MorseApp:
    def __init__(self):
        pass


class Window(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.main_frame = ctk.CTkFrame(self)

        self.entry_enc_modifier = ctk.StringVar()
        self.entry_dec_modifier = ctk.StringVar()
        self.radio_button_selector = ctk.StringVar()
        self.slider_value = ctk.IntVar()

        self.entry_enc_modifier.trace("w", self.entry_modified)
        self.entry_dec_modifier.trace("w", self.entry_modified)

        self.entry_enc = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.entry_enc_modifier,
            font=(
                MorseConstants.DEFAULT_FONT_STYLE_NAME,
                MorseConstants.DEFAULT_FONT_SIZE,
            ),
        )
        self.entry_dec = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.entry_dec_modifier,
            font=(
                MorseConstants.DEFAULT_FONT_STYLE_NAME,
                MorseConstants.DEFAULT_FONT_SIZE,
            ),
        )
        self.clear_entries_button = ctk.CTkButton(
            self.main_frame, text="CLEAR", command=lambda: self.clear_entry()
        )

        self.entry_enc.bind("<Button-3>", self.activate_entry_enc)
        self.entry_dec.bind("<Button-3>", self.activate_entry_dec)
        self.entry_enc.bind(
            "<Double-Button-3>",
            lambda event: self.copy_to_clipboard(
                event, self.entry_enc, self.main_frame
            ),
        )
        self.entry_dec.bind(
            "<Double-Button-3>",
            lambda event: self.copy_to_clipboard(
                event, self.entry_dec, self.main_frame
            ),
        )

        self.radio_button_selector.set(MorseConstants.ENGLISH)
        self.en_radio_button = self.radio_button_creator(MorseConstants.ENGLISH)
        self.ua_radio_button = self.radio_button_creator(MorseConstants.UKRAINIAN)
        self.ru_radio_button = self.radio_button_creator(MorseConstants.RUSSIAN)

        self.play_morse_sound_button = ctk.CTkButton(
            self.main_frame,
            text=MorseConstants.PLAY_TEXT,
            command=lambda: self.start_voice(),
        )

        self.slider_value.set(MorseConstants.DEFAULT_FONT_SIZE)
        self.font_size_slider = ctk.CTkSlider(
            self.main_frame,
            from_=MorseConstants.DEFAULT_FONT_SIZE - 10,
            to=MorseConstants.DEFAULT_FONT_SIZE * 10,
            variable=self.slider_value,
            command=self.font_slider_lister,
        )

        pygame.mixer.init()
        short_sound_path, long_sound_path = self.load_sounds()
        self.dot_sound = pygame.mixer.Sound(short_sound_path)
        self.dash_sound = pygame.mixer.Sound(long_sound_path)

        # default activation of encryption field
        self.entry_dec.configure(state="readonly")
        self.entry_activated = "enc"
        self.en_radio_button.select()

        self.max_dec_length = 0
        self.place_elements()

        self.running_event = threading.Event()
        self.thread = None
        self.stop_voice_flag = False
        self.EXIT_FLAG = False
        self.protocol("WM_DELETE_WINDOW", self.on_window_closing)

    def place_elements(self):
        self.entry_enc.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)
        self.clear_entries_button.pack(fill=ctk.BOTH, padx=100, pady=(0, 5))
        self.entry_dec.pack(fill=ctk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.font_size_slider.pack(fill=ctk.BOTH, padx=5, pady=(0, 5))

        self.en_radio_button.pack(
            side=ctk.LEFT,
            fill=ctk.BOTH,
            expand=True,
            padx=(5, 0),
        )
        self.ua_radio_button.pack(
            side=ctk.LEFT,
            fill=ctk.BOTH,
            expand=True,
        )
        self.ru_radio_button.pack(
            side=ctk.LEFT,
            fill=ctk.BOTH,
            expand=True,
        )
        self.play_morse_sound_button.pack(
            side=ctk.RIGHT,
            fill=ctk.BOTH,
            expand=True,
            padx=(0, 5),
            pady=(0, 5),
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

    def load_sounds(self) -> Optional[tuple[str, str]]:
        full_long_sound_path = os.path.join(
            AudioConstants.SAVE_DIR,
            f"{AudioConstants.LONG_SOUND}.{AudioConstants.DEFAULT_AUDIO_FORMAT}",
        )
        full_short_sound_path = os.path.join(
            AudioConstants.SAVE_DIR,
            f"{AudioConstants.SHORT_SOUND}.{AudioConstants.DEFAULT_AUDIO_FORMAT}",
        )

        self.build_audio_from_binary(AudioConstants.LONG_SOUND)
        self.build_audio_from_binary(AudioConstants.SHORT_SOUND)

        return full_short_sound_path, full_long_sound_path

    def play_sound(self, data: str):
        temp_length = len(data)

        if temp_length > self.max_dec_length:
            if data.endswith(MorseConstants.LONG_SYMBOL):
                self.dash_sound.play()
            elif data.endswith(MorseConstants.SHORT_SYMBOL):
                self.dot_sound.play()
        self.max_dec_length = temp_length

    def voice_encrypted_input(self, data: str):
        if not data:
            return

        symbol_sound_mapping = {
            MorseConstants.LONG_SYMBOL: self.dash_sound,
            MorseConstants.SHORT_SYMBOL: self.dot_sound,
        }

        for char in data:
            if self.stop_voice_flag:
                break
            if char in symbol_sound_mapping:
                symbol_sound_mapping[char].play()
                pygame.time.wait(MorseConstants.PAUSE_BETWEEN_SOUNDS_MS)

        if self.EXIT_FLAG:
            return

        self.play_morse_sound_button.configure(
            text=MorseConstants.PLAY_TEXT, command=lambda: self.start_voice()
        )

    def start_voice(self):
        data: str = self.entry_dec.get()

        if not self.check_str_for_dot_and_dash(data):
            return

        self.play_morse_sound_button.configure(
            text=MorseConstants.STOP_TEXT, command=lambda: self.stop_voice()
        )
        self.stop_voice_flag = False

        if self.thread is None or not self.thread.is_alive():
            self.running_event.clear()
            self.thread = threading.Thread(
                target=self.voice_encrypted_input, args=(data,)
            )
            self.thread.start()

    def stop_voice(self):
        self.stop_voice_flag = True
        self.running_event.set()

    def on_window_closing(self):
        self.EXIT_FLAG = True

        alive_threads = threading.enumerate()
        if len(alive_threads) > 1:
            self.stop_voice()

        self.destroy()

    def font_slider_lister(self, event):
        self.entry_enc.configure(
            font=(MorseConstants.DEFAULT_FONT_STYLE_NAME, int(event))
        )
        self.entry_dec.configure(
            font=(MorseConstants.DEFAULT_FONT_STYLE_NAME, int(event))
        )

    def clear_entry(self):
        self.entry_enc.delete(0, ctk.END)
        self.entry_dec.delete(0, ctk.END)

    @staticmethod
    def alphabet_creator(selector_choice: str) -> Dict[str, str]:
        result_dict: Dict = {}

        if selector_choice == MorseConstants.ENGLISH:
            result_dict.update(MORSE_CODE_DICT[selector_choice])
        else:
            result_dict.update(MORSE_CODE_DICT[MorseConstants.CYRILLIC_DEFAULT])
            result_dict.update(MORSE_CODE_DICT[selector_choice])

        result_dict.update(MORSE_CODE_DICT[MorseConstants.OTHER])

        return result_dict

    @staticmethod
    def check_str_for_dot_and_dash(text: str) -> bool:
        allowed_symbols = (
            MorseConstants.SHORT_SYMBOL,
            MorseConstants.LONG_SYMBOL,
            EMPTY_SPACE,
        )
        return False if not text else all(char in allowed_symbols for char in text)

    @staticmethod
    def build_audio_from_binary(sound_name: str):
        audio_builder = AudioBuilder()
        audio_controller = AudioController(f"{sound_name}")
        file_data = binary_reader(f"{sound_name}")
        audio_controller.execute(audio_builder, binary_data=file_data)

    @staticmethod
    def copy_to_clipboard(event, entry: ctk.CTkEntry, root: ctk.CTkFrame):
        entry_text = entry.get()
        entry.select_range(0, ctk.END)
        root.clipboard_clear()
        root.clipboard_append(entry_text)
        root.update()
        root.after(
            MorseConstants.MESSAGEBOX_EXIT_TIMEOUT_MS,
            lambda: root.event_generate("<Return>"),
        )
        messagebox.showinfo("Success", "Copied!")
