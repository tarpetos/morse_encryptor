from typing import Dict


def encrypt(text_data: str, working_dict: Dict[str, str]) -> str:
    text_data = text_data.upper()
    text_data_list = list(text_data)
    print(text_data_list)

    encrypted_message = ''.join(
        ' ' if char == ' ' else ('𖡄 ' if char not in working_dict.keys() else working_dict[f'{char}'] + ' ')
        for char in text_data_list
    )

    return encrypted_message.strip()


def get_key_by_value(working_dict: Dict[str, str], value: str) -> str:
    for key, val in working_dict.items():
        if val == value:
            return key
    return '𖡄'


def decrypt(encrypted_data: str, working_dict: Dict[str, str]) -> str:
    encrypted_data_list = encrypted_data.split(' ')
    print(encrypted_data_list)

    decrypted_message = ''.join(
        ' ' if enc_char == '' else get_key_by_value(working_dict, enc_char)
        for enc_char in encrypted_data_list
    )
    return decrypted_message.strip()
