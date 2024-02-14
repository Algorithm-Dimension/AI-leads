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
    # Utiliser unidecode pour normaliser les caractères accentués et spéciaux
    clean_string = unidecode(string)
    # Utiliser une expression régulière pour ne garder que les lettres et les chiffres
    clean_string = re.sub(r"[^a-zA-Z0-9]", "", clean_string)
    # Convertir la chaîne en minuscules
    clean_string = clean_string.lower()
    return clean_string


def clean_str_classic(string: str) -> str:
    clean_string = string.strip().lower().title()
    return clean_string
