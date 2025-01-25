import csv
import json
import os
from rdflib import Literal, Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from datetime import datetime

def function_generate_rdf(g, f, namespace):
    """
    Convert the CSV file to RDF using the Olympics ontology structure
    """
    OLYMPICS = namespace[""][1]  # Le préfixe par défaut ":"
    reader = csv.DictReader(f, delimiter=';')
    
    for row in reader:
        # Créer l'athlète
        athlete_uri = URIRef(OLYMPICS[row['Name'].lower().replace(' ', '_')])
        g.add((athlete_uri, RDF.type, OLYMPICS.Athlete))
        g.add((athlete_uri, OLYMPICS.name, Literal(row['Name'])))
        g.add((athlete_uri, OLYMPICS.gender, Literal(row['Gender'])))
        
        # Créer le pays
        country_uri = URIRef(OLYMPICS[row['Country'].lower().replace(' ', '_')])
        g.add((country_uri, RDF.type, OLYMPICS.Country))
        g.add((country_uri, OLYMPICS.name, Literal(row['Country'])))
        g.add((country_uri, OLYMPICS.hasCode, Literal(row['Country_code'])))
        
        # Lier l'athlète au pays
        g.add((athlete_uri, OLYMPICS.hasNationality, country_uri))
        
        # Créer la discipline
        discipline_uri = URIRef(OLYMPICS[row['Discipline'].lower().replace(' ', '_')])
        g.add((discipline_uri, RDF.type, OLYMPICS.Discipline))
        g.add((discipline_uri, OLYMPICS.name, Literal(row['Discipline'])))
        
        # Créer l'épreuve (Trial)
        trial_uri = URIRef(OLYMPICS[row['Event'].lower().replace(' ', '_')])
        g.add((trial_uri, RDF.type, OLYMPICS.Trial))
        g.add((trial_uri, OLYMPICS.name, Literal(row['Event'])))
        g.add((trial_uri, OLYMPICS.belongsToDiscipline, discipline_uri))
        
        # Créer l'événement spécifique
        event_uri = URIRef(OLYMPICS[f"event_{row['Code_Discipline']}_{row['Medal_code']}"])
        g.add((event_uri, RDF.type, OLYMPICS.Event))
        g.add((event_uri, OLYMPICS.belongsToTrial, trial_uri))
        try:
            event_date = datetime.strptime(row['Medal_date'], "%d/%m/%Y").strftime("%Y-%m-%d")
            g.add((event_uri, OLYMPICS.hasDate, Literal(event_date, datatype=XSD.date)))
        except ValueError as e:
            print(f"Date error for {row['Medal_date']}: {e}")
        
        # Créer la performance
        performance_uri = URIRef(OLYMPICS[f"perf_{row['Code_Discipline']}_{row['Medal_code']}"])
        g.add((performance_uri, RDF.type, OLYMPICS.Performance))
        g.add((performance_uri, OLYMPICS.playedBy, athlete_uri))
        g.add((performance_uri, OLYMPICS.hasEvent, event_uri))
        
        # Si l'athlète a gagné une médaille
        if row['Medal_type']:
            medal_uri = URIRef(OLYMPICS[row['Medal_type'].lower().replace(' ', '_')])
            g.add((medal_uri, RDF.type, OLYMPICS.Medal))
            g.add((medal_uri, OLYMPICS.name, Literal(row['Medal_type'])))
            g.add((performance_uri, OLYMPICS.awarded, medal_uri))

class CSV2RDF:
    def __init__(self, data_path: str, output_path: str, csv_file: str, rdf_file: str):
        self.data_path = data_path
        self.output_path = output_path
        self.csv_file = os.path.join(self.data_path, csv_file)
        self.rdf_file = os.path.join(self.output_path, rdf_file)
        
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)

    def create_rdf(self, namespace):
        g = Graph()
        
        # Bind namespaces
        g.bind("", "http://example.org/olympics#")
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)
        g.bind("xsd", XSD)

        with open(self.csv_file, encoding='utf-8-sig') as f:
            function_generate_rdf(g, f, namespace)

        g.serialize(destination=self.rdf_file, format="turtle")
        print(f"RDF exporté avec succès dans {self.rdf_file}")

def main():
    namespace = {
        "": ("http://example.org/olympics#", Namespace("http://example.org/olympics#"))
    }

    converter = CSV2RDF(
        data_path="data",
        output_path="output", 
        csv_file="paris.csv",
        rdf_file="paris.ttl"
    )
    converter.create_rdf(namespace)

if __name__ == "__main__":
    main()