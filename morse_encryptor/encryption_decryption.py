from typing import Dict, List

from .constants import SpecConstants


def encrypt(text_data: str, working_dict: Dict[str, str]) -> str:
    text_data: str = text_data.upper()

    encrypted_message = [
        SpecConstants.EMPTY_SPACE
        if char == SpecConstants.EMPTY_SPACE
        else (
            working_dict.get(char, SpecConstants.UNKNOWN_SYMBOL)
            + SpecConstants.EMPTY_SPACE
        )
        for char in text_data
    ]
    return "".join(encrypted_message).strip()


def decrypt(encrypted_data: str, working_dict: Dict[str, str]) -> str:
    encrypted_data_list: List[str] = encrypted_data.split(SpecConstants.EMPTY_SPACE)

    decrypted_message = [
        SpecConstants.EMPTY_SPACE
        if enc_char == SpecConstants.EMPTY_STRING
        else next(
            (key for key, val in working_dict.items() if val == enc_char),
            SpecConstants.UNKNOWN_SYMBOL.strip(),
        )
        for enc_char in encrypted_data_list
    ]
    return "".join(decrypted_message)
