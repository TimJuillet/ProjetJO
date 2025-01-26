import json
import os
import re
from datetime import datetime


def transformer_date(date_str):
    # Convertir la chaîne de date en objet datetime
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

    # Reformater la date selon le format demandé
    new_format = date_obj.strftime("%d_%m_%Y_at_time_%Hh%M")

    return new_format

def convertir_en_rdf_dateTime(date_str):
    # Convertir la chaîne de date en un objet datetime
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")

    # Convertir l'objet datetime en une chaîne au format xsd:dateTime
    rdf_dateTime = date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

    return rdf_dateTime

def obtenir_premier_terme(chaine):
    # Séparer la chaîne par des espaces et retourner le premier terme
    return chaine.split()[0]

def separer_nom_prenom(chaine):
    # Séparer la chaîne par des espaces
    parts = chaine.split()

    # Le prénom est toujours la première partie, tout en minuscule
    prenom = parts[0].capitalize()

    # Le nom est tout ce qui reste, tout en majuscule
    nom = " ".join(parts[1:]).upper()

    # Retourner les deux valeurs
    return prenom, nom

def normalize_string(s):
    s = s.lower()  # Mettre en minuscule
    s = re.sub(r'\d+', '', s)  # Supprimer les chiffres
    s = s.strip()  # Supprimer les espaces avant et après
    s = ' '.join(s.split())  # Supprimer les espaces multiples
    return s

def capitalize_words(s):
    # Mettre en majuscule chaque début de mot
    return ' '.join(word.capitalize() for word in s.split())

def check_and_create_file(file_path : str):
    """
    Check if the file exists, if not create it.

    Parameters:
        file_path (str): The file path.
    """
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write()
        print(f"The file '{file_path}' has been created.")
        return False
    return True

def write_in_file(file_path : str, content : dict):
    """
    Write the content to a file.
    Check if the file exists, if not create it.
    Check if the file extension is in the content dictionary.

    Parameters:
        file_path (str): The file path.
        content (dict): The content to write
    """
    check_and_create_file(file_path)

    file_extension = os.path.splitext(file_path)[1][1:]

    if file_extension in content:
        with open(file_path, 'w') as file:
            json.dump(content[file_extension], file, indent=4)
        print(f"The data has been written to the file '{file_path}'.")
    else:
        print(f"The file extension '{file_extension}' is not in the content dictionary.")