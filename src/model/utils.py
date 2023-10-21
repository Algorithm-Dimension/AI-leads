import re

def extract_variables(text):
    pattern = r'{([^}]+)}'
    variables = re.findall(pattern, text)
    return list(set(variables))

def filter_dictionary(input_dict, key_list):
    filtered_dict = {key: input_dict[key] for key in key_list if key in input_dict}
    return filtered_dict