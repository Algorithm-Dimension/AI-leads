import re

from unidecode import unidecode


def extract_variables(text):
    pattern = r"{([^}]+)}"
    variables = re.findall(pattern, text)
    return list(set(variables))


def filter_dictionary(input_dict, key_list):
    filtered_dict = {key: input_dict[key] for key in key_list if key in input_dict}
    return filtered_dict


def clean_str_unidecode(string: str) -> str:
    clean_string = unidecode(string).replace(" ", "").lower()
    return clean_string


def clean_str_classic(string: str) -> str:
    clean_string = string.strip().lower().title()
    return clean_string
