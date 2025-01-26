import csv
import json
import os
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD
import re
from datetime import datetime
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
    olympicsParameters

from utils import \
    transformer_date, \
    convertir_en_rdf_dateTime, \
    obtenir_premier_terme, \
    separer_nom_prenom, \
    normalize_string, \
    capitalize_words, \
    check_and_create_file, \
    write_in_file

from ConstructRDF import ConstructRDF

from medal_og_24 import function_for_medal_og_24
from athlete_og_24 import function_for_athlete_og_24

class CSV2RDF :

    def __init__(self, data_path : str, output_path : str, csv_file : str, rdf_file : str, file_to_overwrite : list or str = None, csvFileEncoding : str = "utf-8"):
        self.data_path = data_path
        self.output_path = output_path
        self.csv_file = os.path.join(self.data_path, csv_file)
        self.rdf_file = os.path.join(self.output_path, rdf_file)
        self.file_to_overwrite = file_to_overwrite
        self.csvFileEncoding = csvFileEncoding
        self.newTurtleFile = False
        self.dictionnary_file_name = {
            "must": self.csv_file,
            "should": [
                self.rdf_file
            ],
        }
        self.check_and_create()

    def remove_overwrite_files(self):
        if not self.file_to_overwrite:
            return
        if self.file_to_overwrite == "all":
            self.file_to_overwrite = self.dictionnary_file_name["should"]
        if not isinstance(self.file_to_overwrite, list):
            return
        for file_path in self.file_to_overwrite:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"The file '{file_path}' has been removed.")

    def check_and_create(self):
        """
        Check if the required files exist in the folders.
        Create the 'data_path' and 'output_path' directories if they do not exist.
        If the 'must' file does not exist, raise a FileNotFoundError.
        If the 'should' files do not exist, create them in the data folder.

        Raises:
            FileNotFoundError: If the 'must' file is not found in the data folder.
        """
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)

        if not os.path.isfile(self.dictionnary_file_name["must"]):
            raise FileNotFoundError(
                f"The required file '{self.dictionnary_file_name['must']}' is not found in the data folder '{self.data_path}'."
            )

        self.remove_overwrite_files()

        for should_file_path, should_file_name in zip(self.dictionnary_file_name["should"], self.dictionnary_file_name["should"]):
            if not os.path.isfile(should_file_path):
                with open(should_file_path, 'w') as file:
                    file.write('{}')
                print(f"The file '{should_file_name}' has been created in the data folder '{self.data_path}'.")
                self.newTurtleFile = True

    def create_rdf(self, namespace : dict, callable_function : callable):
        """
        Convert the CSV file to RDF and save it to a file.

        Parameters:
            namespace (dict): The namespace dictionary.
            callable_function (callable): The function to apply on the RDF graph.
        """

        g = Graph()
        if self.file_to_overwrite == None and self.newTurtleFile == False :
            g.parse(self.rdf_file, format="turtle")
        for prefix, uri in namespace.items():
            g.bind(prefix, uri[0])

        with open(self.csv_file, encoding=self.csvFileEncoding) as f:
            callable_function(g, f, namespace, self.csv_file)

        g.serialize(destination=self.rdf_file, format="turtle")
        print(f"RDF exporté avec succès dans {self.rdf_file}")

def function_generate_rdf(g, f, namespace: dict, fileName: str):
    constructorRDF = ConstructRDF(g, namespace)
    reader = csv.DictReader(f, delimiter=';')
    constructorRDF.createCoordinate(ConstructRDF.SET_OPERATION, BlankCoordinateWritting, BlankCoordinateLongitude, BlankCoordinateLatitude, BlankCoordinateName, BlankCoordinateDescription)
    if fileName == "../data\medal_og_24.csv":
        print("Processing the file 'medal_og_24.csv'")
        function_for_medal_og_24(reader, constructorRDF)
        return
    if fileName == "../data\\athlete_og_24.csv":
        print("Processing the file 'athlete_og_24.csv'")
        function_for_athlete_og_24(reader, constructorRDF)
        return
