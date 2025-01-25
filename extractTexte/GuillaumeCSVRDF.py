import csv
import json
import os
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

def check_and_create_file(file_path : str):
    """
    Check if the file exists, if not create it.

    Parameters:
        file_path (str): The file path.
    """
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write()

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

class CSV2RDF :

    def __init__(self, data_path : str, output_path : str, csv_file : str, jsonld_file : str, rdf_file : str, file_to_overwrite : list or str = None):
        self.data_path = data_path
        self.output_path = output_path
        self.csv_file = os.path.join(self.data_path, csv_file)
        self.jsonld_file = os.path.join(self.data_path, jsonld_file)
        self.rdf_file = os.path.join(self.output_path, rdf_file)
        self.file_to_overwrite = file_to_overwrite
        self.dictionnary_file_name = {
            "must": self.csv_file,
            "should": [
                self.jsonld_file,
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


    def generate_type_matrix_mapping(self, base_property_url : str, base_value_url : str) :
        """
        Generate a JSON-LD mapping for the type matrix CSV file.

        Parameters:
            base_property_url (str): The base URL for the property.
            base_value_url (str): The base URL for the value.
        """
        mapping = {
            "@context": "http://www.w3.org/ns/csvw",
            "url": self.csv_file,
            "tableSchema": {
                "columns": []
            }
        }

        with open(self.csv_file, encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)

        mapping["tableSchema"]["columns"].append({
            "name": "Attacking",
            "titles": "Attacking",
            "propertyUrl": "http://schema.org/type"
        })

        for header in headers[1:]:
            mapping["tableSchema"]["columns"].append({
                "name": header,
                "titles": header,
                "datatype": "decimal",
                "propertyUrl": base_property_url,
                "valueUrl": base_value_url + header
            })

        self.jsonld_mapping = {
            "json" : mapping
        }

    def save_type_matrix_mapping(self):
        """
        Write the JSON-LD mapping to a file.
        """
        write_in_file(self.jsonld_file, self.jsonld_mapping)


    def create_rdf(self, namespace : dict, callable_function : callable):
        """
        Convert the CSV file to RDF and save it to a file.

        Parameters:
            namespace (dict): The namespace dictionary.
            callable_function (callable): The function to apply on the RDF graph.
        """
        g = Graph()
        for prefix, uri in namespace.items():
            g.bind(prefix, uri[0])

        with open(self.csv_file, encoding="utf-8") as f:
            callable_function(g, f, namespace)

        g.serialize(destination=self.rdf_file, format="turtle")
        print(f"RDF exporté avec succès dans {self.rdf_file}")

namespace = {
    "ex": ("http://example.org/", Namespace("http://example.org/")),
    "schema": ("http://schema.org/", Namespace("http://schema.org/"))
}

def function_generate_rdf(g, f, namespace : dict) :
    """
    Convert the CSV file to RDF and add it to the graph.

    Parameters:
        g (Graph): The RDF graph.
        f (file): The CSV file.
        namespace (dict): The namespace dictionary.

    Returns:
        None
    """
    EX = namespace["ex"][1]
    SCHEMA = namespace["schema"][1]
    reader = csv.DictReader(f)
    for row in reader:
        attacking_type = row["Attacking"]
        attacking_uri = URIRef(EX[attacking_type])
        g.add((attacking_uri, RDF.type, SCHEMA["type"]))

        for col, value in row.items():
            if col != "Attacking" :
                defensive_uri = URIRef(EX[col])
                if value == "0.5":
                    g.add((attacking_uri, EX["isNotEffectiveAgainst"], defensive_uri))
                elif value == "0":
                    g.add((attacking_uri, EX["hasNoEffectAgainst"], defensive_uri))
                elif value == "2":
                    g.add((attacking_uri, EX["isEffectiveAgainst"], defensive_uri))
                elif value == "1":
                    g.add((attacking_uri, EX["isNeutralAgainst"], defensive_uri))

csv2rdf = CSV2RDF("data", "output", "type_matrix.csv", "type_matrix_mapping.json", "type_matrix.ttl", "all")
csv2rdf.generate_type_matrix_mapping("http://example.org/interactionWith", "http://example.org/")
csv2rdf.save_type_matrix_mapping()
csv2rdf.create_rdf(namespace, function_generate_rdf)

