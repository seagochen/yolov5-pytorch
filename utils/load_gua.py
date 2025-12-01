import json
import os


def load_json_from_folder(folder: str):
    data_dict = {}
    for file in os.listdir(folder):
        if file.endswith('.json'):
            with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                data_dict.update(data)
    return data_dict


def load_gua(gua_folder: str):
    # Load the json files from the gua_folder and combine them into a single dictionary
    gua_dict = load_json_from_folder(gua_folder)
    return gua_dict


if __name__ == '__main__':

    # Load the gua dictionary
    gua_dict = load_gua('data/gua')
    print(gua_dict)