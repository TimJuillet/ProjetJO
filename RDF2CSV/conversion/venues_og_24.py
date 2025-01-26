import csv
import ast

from utils import \
    transformer_date, \
    convertir_en_rdf_dateTime, \
    obtenir_premier_terme, \
    separer_nom_prenom, \
    normalize_string, \
    capitalize_words, \
    check_and_create_file, \
    write_in_file



from constants import \
    BlankCoordinateLongitude, \
    BlankCoordinateLatitude, \
    BlankCoordinateWritting, \
    BlankCoordinateName, \
    BlankCoordinateDescription, \
    BlankHeight, \
    BlankWeight, \
    BlankBirthDate, \
    BlankDeathDate, \
    BlankIsDisabled, \
    BlankHasResultUnit, \
    BlankHasResult, \
    separator, \
    namespace, \
    olympicsParameters, \
    pathToVenueData

def generate_discipline_to_venue_dictionary_from_csv(file_path):
    """
    Lit un fichier CSV à partir du chemin donné et génère un dictionnaire
    associant chaque discipline à une liste de lieux.

    :param file_path: Chemin vers le fichier CSV
    :return: Dictionnaire associant les disciplines aux lieux
    """
    dictionary = {}

    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:

                venue = capitalize_words(normalize_string(row["venue"])).replace(" ", separator)
                discipline_row = row["sports"]

                # Convertir la chaîne de caractères en liste Python
                discipline_list = ast.literal_eval(discipline_row)

                for discipline in discipline_list:
                    disciplineFormatted = capitalize_words(normalize_string(discipline)).replace(" ", separator)
                    if disciplineFormatted in dictionary:
                        continue
                        #dictionary[disciplineFormatted].append(venue)
                        #print("Problème avec la discipline :", disciplineFormatted, "ayant plusieurs lieux :", dictionary[disciplineFormatted])
                    else:
                        dictionary[disciplineFormatted] = [venue]

    except FileNotFoundError:
        print(f"Le fichier {file_path} est introuvable.")
    except KeyError as e:
        print(f"Clé manquante dans le fichier CSV : {e}")


    return dictionary


