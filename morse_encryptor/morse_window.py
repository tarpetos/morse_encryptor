import os
import threading
from tkinter import messagebox

import customtkinter as ctk
import pygame

from typing import Dict, Any, Optional, Tuple

from .constants import AudioConstants, MorseConstants, SpecConstants
from .alphabet import MORSE_CODE_DICT
from .audio_transformer import (
    AudioBuilder,
    AudioController,
    binary_reader,
)
from .encryption_decryption import encrypt, decrypt


class MorsePlayer:
    def __init__(self):
        pygame.mixer.init()
        short_sound_path, long_sound_path = self.load_sounds()
        self.dot_sound = pygame.mixer.Sound(short_sound_path)
        self.dash_sound = pygame.mixer.Sound(long_sound_path)
        self.stop_voice_flag = False
        self.thread = None
        self.TERMINATE_THREAD_FLAG = False
        self.running_event = threading.Event()

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

    def on_entry_edit(self, event) -> None:
        char_sound_mapping = {
            MorseConstants.LONG_SYMBOL: self.dash_sound,
            MorseConstants.SHORT_SYMBOL: self.dot_sound,
        }

        entered_char = event.char
        sound_to_play = char_sound_mapping.get(entered_char)

        if sound_to_play is not None:
            sound_to_play.play()

    def voice_encrypted_input(
        self, encrypted_entry: ctk.CTkEntry, sound_button: ctk.CTkButton
    ) -> None:
        data: str = encrypted_entry.get()
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

        if self.TERMINATE_THREAD_FLAG:
            return

        sound_button.configure(
            text=MorseConstants.PLAY_TEXT,
            command=lambda: self.start_voice(encrypted_entry, sound_button),
        )

    def start_voice(
        self, encrypted_entry: ctk.CTkEntry, sound_button: ctk.CTkButton
    ) -> None:
        data: str = encrypted_entry.get()

        if not self.check_str_for_dot_and_dash(data):
            return

        sound_button.configure(
            text=MorseConstants.STOP_TEXT, command=lambda: self.stop_voice()
        )
        self.stop_voice_flag = False

        if self.thread is None or not self.thread.is_alive():
            self.running_event.clear()
            self.thread = threading.Thread(
                target=self.voice_encrypted_input, args=(encrypted_entry, sound_button)
            )
            self.thread.start()

    def stop_voice(self) -> None:
        self.stop_voice_flag = True
        self.running_event.set()

    @staticmethod
    def check_str_for_dot_and_dash(text: str) -> bool:
        allowed_symbols = (
            MorseConstants.SHORT_SYMBOL,
            MorseConstants.LONG_SYMBOL,
            SpecConstants.EMPTY_SPACE,
        )
        return False if not text else all(char in allowed_symbols for char in text)

    @staticmethod
    def build_audio_from_binary(sound_name: str) -> None:
        audio_builder = AudioBuilder()
        audio_controller = AudioController(f"{sound_name}")
        file_data = binary_reader(f"{sound_name}")
        audio_controller.execute(audio_builder, binary_data=file_data)


class MorseTranslator:
    @staticmethod
    def encrypt_data(data: str, working_dict: Dict[str, str]):
        return encrypt(data, working_dict)

    @staticmethod
    def decrypt_data(data: str, working_dict: Dict[str, str]):
        return decrypt(data, working_dict)

    @staticmethod
    def alphabet_creator(selector_choice: str) -> Dict[str, str]:
        result_dict = {}

        if selector_choice == MorseConstants.ENGLISH:
            result_dict.update(MORSE_CODE_DICT[selector_choice])
        else:
            result_dict.update(MORSE_CODE_DICT[MorseConstants.CYRILLIC_DEFAULT])
            result_dict.update(MORSE_CODE_DICT[selector_choice])

        result_dict.update(MORSE_CODE_DICT[MorseConstants.OTHER])
        return result_dict


class MorseUI(ctk.CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_frame = ctk.CTkFrame(self)
        self.entry_enc = ctk.CTkEntry(self.main_frame)
        self.clear_entries_button = ctk.CTkButton(self.main_frame)
        self.entry_dec = ctk.CTkEntry(self.main_frame)
        self.font_size_slider = ctk.CTkSlider(self.main_frame)
        self.en_radio_button = ctk.CTkRadioButton(self.main_frame)
        self.ua_radio_button = ctk.CTkRadioButton(self.main_frame)
        self.ru_radio_button = ctk.CTkRadioButton(self.main_frame)
        self.play_morse_sound_button = ctk.CTkButton(self.main_frame)

    def place_elements(self) -> None:
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

    def font_slider_lister(self, event: Any) -> None:
        self.entry_enc.configure(
            font=(MorseConstants.DEFAULT_FONT_STYLE_NAME, int(event))
        )
        self.entry_dec.configure(
            font=(MorseConstants.DEFAULT_FONT_STYLE_NAME, int(event))
        )

    def clear_entry(
        self, entry_enc_modifier: ctk.StringVar, entry_dec_modifier: ctk.StringVar
    ) -> None:
        self.entry_enc.delete(0, ctk.END)
        self.entry_dec.delete(0, ctk.END)
        entry_dec_modifier.set(SpecConstants.EMPTY_STRING)
        entry_enc_modifier.set(SpecConstants.EMPTY_STRING)

    @staticmethod
    def copy_to_clipboard(event: Any, entry: ctk.CTkEntry, root: ctk.CTkFrame) -> None:
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


class MorseApp(MorseUI, MorsePlayer, MorseTranslator):
    def __init__(self):
        super().__init__()
        MorsePlayer.__init__(self)
        self.entry_activated = MorseConstants.ENCRYPTION_MODE_ACTIVE

        self.entry_enc_modifier = ctk.StringVar()
        self.entry_dec_modifier = ctk.StringVar()
        self.slider_value = ctk.IntVar()
        self.radio_button_selector = ctk.StringVar()

        self.init_ui_elements()
        self.set_default_values()
        self.bind_events()

    def init_ui_elements(self) -> None:
        self.entry_initializer(self.entry_enc, self.entry_enc_modifier)
        self.entry_initializer(self.entry_dec, self.entry_dec_modifier)
        self.entry_dec.configure(state="readonly")

        self.button_initializer(
            self.clear_entries_button,
            MorseConstants.CLEAR_BUTTON_TEXT,
            lambda: self.clear_entry(self.entry_enc_modifier, self.entry_dec_modifier),
        )
        self.button_initializer(
            self.play_morse_sound_button,
            MorseConstants.PLAY_TEXT,
            lambda: self.start_voice(self.entry_dec, self.play_morse_sound_button),
        )

        self.en_radio_button = self.radio_button_initializer(
            self.main_frame,
            MorseConstants.ENGLISH,
            self.radio_button_selector,
            lambda: self.radio_button_entries_reloader(MorseConstants.ENGLISH),
        )
        self.ua_radio_button = self.radio_button_initializer(
            self.main_frame,
            MorseConstants.UKRAINIAN,
            self.radio_button_selector,
            lambda: self.radio_button_entries_reloader(MorseConstants.UKRAINIAN),
        )
        self.ru_radio_button = self.radio_button_initializer(
            self.main_frame,
            MorseConstants.RUSSIAN,
            self.radio_button_selector,
            lambda: self.radio_button_entries_reloader(MorseConstants.RUSSIAN),
        )

        self.slider_initializer(
            self.font_size_slider,
            MorseConstants.SLIDER_MIN_VALUE,
            MorseConstants.SLIDER_MAX_VALUE,
            self.slider_value,
            self.font_slider_lister,
        )

    def set_default_values(self) -> None:
        self.radio_button_selector.set(MorseConstants.ENGLISH)
        self.slider_value.set(MorseConstants.DEFAULT_FONT_SIZE)

    def bind_events(self) -> None:
        self.entry_enc.bind("<Button-3>", self.activate_entry_enc)
        self.entry_dec.bind("<Button-3>", self.activate_entry_dec)
        self.entry_dec.bind("<Key>", self.on_entry_edit)
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

        self.entry_enc_modifier.trace("w", self.entry_modified)
        self.entry_dec_modifier.trace("w", self.entry_modified)

    def activate_entry_enc(self, event: Any) -> None:
        self.entry_enc.configure(state="normal")
        self.entry_dec.configure(state="readonly")
        self.entry_activated = MorseConstants.ENCRYPTION_MODE_ACTIVE
        self.entry_enc_activation_stripper()

    def entry_enc_activation_stripper(self) -> None:
        striped_data = self.entry_enc_modifier.get().strip()
        self.entry_enc.delete(0, ctk.END)
        self.entry_enc.insert(0, striped_data)

    def activate_entry_dec(self, event: Any) -> None:
        self.entry_dec.configure(state="normal")
        self.entry_enc.configure(state="readonly")
        self.entry_activated = MorseConstants.DECRYPTION_MODE_ACTIVE

    def entry_modified(self, *args) -> None:
        user_choice: str = self.radio_button_selector.get()
        working_dict: Dict[str, str] = self.alphabet_creator(user_choice)

        if self.entry_activated == MorseConstants.ENCRYPTION_MODE_ACTIVE:
            data: str = self.entry_enc.get()
            self.entry_dec_modifier.set(self.encrypt_data(data, working_dict))
        elif self.entry_activated == MorseConstants.DECRYPTION_MODE_ACTIVE:
            data: str = self.entry_dec.get()
            self.entry_enc_modifier.set(self.decrypt_data(data, working_dict))

    def radio_button_entries_reloader(self, language: str) -> None:
        self.radio_button_selector.set(language)
        working_dict = self.alphabet_creator(language)

        if self.entry_activated == MorseConstants.ENCRYPTION_MODE_ACTIVE:
            self.reload_entries(self.entry_enc, self.entry_dec, encrypt, working_dict)
            self.entry_enc.icursor(ctk.END)
        elif self.entry_activated == MorseConstants.DECRYPTION_MODE_ACTIVE:
            self.reload_entries(self.entry_dec, self.entry_enc, decrypt, working_dict)
            self.entry_dec.icursor(ctk.END)

    def reload_entries(
        self,
        source_entry: ctk.CTkEntry,
        target_entry: ctk.CTkEntry,
        function,
        working_dict: Dict[str, str],
    ) -> None:
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

    def run(
        self,
        window_name: str = "Morse (De)Coder",
        window_size: Tuple[int, int] = (
            MorseConstants.DEFAULT_MIN_WIDTH,
            MorseConstants.DEFAULT_MIN_HEIGHT,
        ),
    ) -> None:
        self.place_elements()
        self.protocol("WM_DELETE_WINDOW", self.on_window_closing)
        self.title(window_name)
        self.geometry(f"{window_size[0]}x{window_size[1]}")
        self.minsize(*window_size)
        self.mainloop()

    def on_window_closing(self) -> None:
        self.TERMINATE_THREAD_FLAG = True

        alive_threads = threading.enumerate()
        if len(alive_threads) > 1:
            self.stop_voice()

        self.destroy()

    @staticmethod
    def entry_initializer(entry: ctk.CTkEntry, variable: ctk.Variable) -> None:
        entry.configure(
            textvariable=variable,
            font=(
                MorseConstants.DEFAULT_FONT_STYLE_NAME,
                MorseConstants.DEFAULT_FONT_SIZE,
            ),
        )

    @staticmethod
    def button_initializer(button: ctk.CTkButton, text: str, command_func) -> None:
        button.configure(text=text, command=command_func)

    @staticmethod
    def slider_initializer(
        slider: ctk.CTkSlider,
        start_value: float,
        end_value: float,
        variable: ctk.Variable,
        command_func,
    ) -> None:
        slider.configure(
            from_=start_value, to=end_value, variable=variable, command=command_func
        )

    @staticmethod
    def radio_button_initializer(
        frame: ctk.CTkFrame,
        language: str,
        variable: ctk.Variable,
        command_func,
    ) -> ctk.CTkRadioButton:
        return ctk.CTkRadioButton(
            frame,
            text=language,
            value=language,
            variable=variable,
            command=command_func,
        )
