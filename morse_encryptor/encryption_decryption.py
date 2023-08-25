from typing import Dict, List

EMPTY_SPACE: str = ' '
EMPTY_STRING: str = ''
UNKNOWN_SYMBOL: str = '𖡄 '


def encrypt(text_data: str, working_dict: Dict[str, str]) -> str:
    text_data: str = text_data.upper()

    encrypted_message = [
        EMPTY_SPACE if char == EMPTY_SPACE else (working_dict.get(char, UNKNOWN_SYMBOL) + EMPTY_SPACE)
        for char in text_data
    ]
    return ''.join(encrypted_message).strip()


def decrypt(encrypted_data: str, working_dict: Dict[str, str]) -> str:
    encrypted_data_list: List[str] = encrypted_data.split(EMPTY_SPACE)

    decrypted_message = [
        EMPTY_SPACE if enc_char == EMPTY_STRING
        else next((key for key, val in working_dict.items() if val == enc_char), UNKNOWN_SYMBOL.strip())
        for enc_char in encrypted_data_list
    ]
    return ''.join(decrypted_message)
