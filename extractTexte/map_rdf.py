from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import pandas as pd
import re

class OlympicsRDFConverter:
    def __init__(self):
        self.olympics = Namespace("http://example.org/olympics#")
        self.g = Graph()
        self.g.bind("olympics", self.olympics)
        self.processed_triplets = set()
        self.current_olympics = None

    def clean_text(self, text):
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text

    def create_resource_uri(self, text, class_type=None):
        clean_id = self.clean_text(text)
        uri = self.olympics[clean_id]
        if class_type:
            self.g.add((uri, RDF.type, class_type))
        self.g.add((uri, RDFS.label, Literal(text)))
        return uri

    def get_olympics_uri(self, name):
        # On utilise toujours le même URI pour les JO 2024
        if "2024" in name:
            if not self.current_olympics:
                self.current_olympics = self.create_resource_uri(
                    "Jeux olympiques d'été de 2024", self.olympics.Olympics)
            return self.current_olympics
        return self.create_resource_uri(name, self.olympics.Olympics)

    def is_valid_triplet(self, head, relation, tail):
        # Pour les JO 2024, on vérifie si on n'a pas déjà traité ce type de relation
        if "2024" in head:
            relation_key = (self.clean_text("Jeux olympiques d'été de 2024"), relation, tail.lower())
            if relation_key in self.processed_triplets:
                return False
            self.processed_triplets.add(relation_key)
            return True

        # Pour les autres triplets, vérification simple des doublons
        triplet_key = (head.lower(), relation, tail.lower())
        if triplet_key in self.processed_triplets:
            return False
        self.processed_triplets.add(triplet_key)
        return True

    def convert_triplets_to_rdf(self, csv_path):
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            head, relation, tail = row['head'], row['type'], row['tail']
            
            # Ignorer les Jeux d'été sans année
            if head == "Jeux olympiques d'été":
                continue

            if not self.is_valid_triplet(head, relation, tail):
                continue

            if "Jeux olympiques" in head:
                olympics_uri = self.get_olympics_uri(head)
                if relation == "point in time":
                    year = tail
                    self.g.add((olympics_uri, self.olympics.startDate, 
                              Literal(f"{year}-07-26", datatype=XSD.date)))
                elif relation == "country":
                    country_uri = self.create_resource_uri(tail, self.olympics.Country)
                    self.g.add((olympics_uri, self.olympics.hostCountry, country_uri))

            elif relation == "sport":
                athlete_uri = self.create_resource_uri(head, self.olympics.Athlete)
                discipline_uri = self.create_resource_uri(tail, self.olympics.Discipline)
                self.g.add((athlete_uri, self.olympics.belongsToDiscipline, discipline_uri))
                self.g.add((athlete_uri, self.olympics.isDisabled, Literal(False)))

    def save_rdf(self, output_path):
        self.g.serialize(destination=output_path, format="turtle")

def main():
    converter = OlympicsRDFConverter()
    converter.convert_triplets_to_rdf("extracted_triplets.csv")
    converter.save_rdf("olympics_output.ttl")

if __name__ == "__main__":
    main()