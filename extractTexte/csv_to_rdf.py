import csv
import os
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, OWL
import pandas as pd
from urllib.parse import quote
import re

class OlympicsRDFConverter:
    def __init__(self):
        self.olympics = Namespace("http://example.org/olympics#")
        self.g = Graph()
        
        # Utiliser les mêmes préfixes que l'ontologie d'origine
        self.g.bind("", self.olympics)  # préfixe par défaut
        self.g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        self.g.bind("owl", "http://www.w3.org/2002/07/owl#")
        self.g.bind("xsd", "http://www.w3.org/2001/XMLSchema#")

        # Liste des disciplines sportives connues
        self.sports = {
            'tennis', 'natation', 'athlétisme', 'football', 'basketball',
            'volleyball', 'judo', 'gymnastique', 'escrime', 'boxe'
        }

        # Liste des lieux connus à Paris
        self.paris_venues = {
            'tour eiffel', 'trocadéro', 'invalides', 'grand palais', 
            'champ-de-mars', 'place de la concorde', 'bercy'
        }

        # Liste des athlètes connus
        self.known_athletes = {
            'novak djokovic', 'letsile tebogo', 'thea lafond', 
            'julien alfred', 'sainte-lucie julien alfred'
        }

    def safe_uri(self, text):
        return quote(text.lower().replace(' ', '_'))

    def looks_like_person_name(self, text):
        """Vérifie si le texte ressemble à un nom de personne"""
        text_lower = text.lower()
        # Vérifie si c'est un athlète connu
        if text_lower in self.known_athletes:
            return True
        
        # Vérifie le format du nom (au moins deux mots, pas de chiffres)
        words = text_lower.split()
        if len(words) >= 2 and not any(char.isdigit() for char in text):
            # Vérifie qu'aucun mot n'est dans nos listes de lieux ou sports
            return not any(word in self.sports or word in self.paris_venues for word in words)
        return False

    def is_venue(self, text):
        """Déterminer si le texte correspond à un lieu"""
        text_lower = text.lower()
        venue_keywords = ['palais', 'stade', 'arena', 'centre', 'parc', 'place']
        return any(keyword in text_lower for keyword in venue_keywords) or \
               text_lower in self.paris_venues

    def is_sport(self, text):
        """Déterminer si le texte correspond à une discipline sportive"""
        return text.lower() in self.sports

    def map_subject_to_class(self, subject, context=None):
        """Map a subject to the appropriate ontology class"""
        subject_lower = subject.lower()
        
        # Venue detection - first priority
        if self.is_venue(subject):
            return self.olympics.Venue

        # Sport/Discipline detection
        if self.is_sport(subject):
            return self.olympics.Discipline

        # City detection
        if 'ville' in subject_lower or 'city' in subject_lower:
            return self.olympics.City

        # Olympic Games detection
        if 'jeux olympiques' in subject_lower or 'olympic games' in subject_lower:
            return self.olympics.Olympics

        # Team detection
        if any(keyword in subject_lower for keyword in ['équipe', 'team', 'délégation']):
            return self.olympics.Team

        # Athlete detection
        if self.looks_like_person_name(subject):
            return self.olympics.Athlete

        # Check if it's a year
        if subject.isdigit() and len(subject) == 4:
            return None  # We'll handle years as literals

        # Special cases
        if subject_lower == 'monde entier':
            return None  # Skip this entity or handle differently

        return self.olympics.Event  # Default fallback

    def map_predicate(self, relation):
        """Map relation type to ontology property"""
        relation_lower = relation.lower().strip()
        
        predicate_map = {
            'participates in': self.olympics.participatesIn,
            'represents': self.olympics.represent,
            'has nationality': self.olympics.hasNationality,
            'born in': self.olympics.birthDate,
            'located in': self.olympics.hasCity,
            'belongs to': self.olympics.belongsToDiscipline,
            'competes in': self.olympics.participatesIn,
            'won': self.olympics.awarded,
            'held in': self.olympics.hasVenue,
            'part of': self.olympics.belongsToDiscipline,
            'has record': self.olympics.recordHasPerformance,
            'sport': self.olympics.belongsToDiscipline,
            'point_in_time': self.olympics.startDate
        }
        
        mapped_predicate = predicate_map.get(relation_lower)
        if mapped_predicate:
            return mapped_predicate

        # Skip certain predicates entirely
        if relation_lower == 'located_in_the_administrative_territorial_entity':
            return None

        return self.olympics[self.safe_uri(relation)]

    def add_additional_triples(self, subject_uri, subject_class, entity_data):
        """Add additional triples based on the class type"""
        if subject_class == self.olympics.Venue:
            # Add hasCity relation for venues in Paris
            city_uri = URIRef(self.olympics['ville_de_paris'])
            self.g.add((subject_uri, self.olympics.hasCity, city_uri))
            self.g.add((city_uri, RDF.type, self.olympics.City))
            
        elif subject_class == self.olympics.Olympics:
            # Add standard Olympics properties
            self.g.add((subject_uri, self.olympics.season, Literal("Summer")))
            self.g.add((subject_uri, self.olympics.startDate, Literal("2024-07-26", datatype=XSD.date)))
            self.g.add((subject_uri, self.olympics.endDate, Literal("2024-08-11", datatype=XSD.date)))
            
            # Add host city relation
            city_uri = URIRef(self.olympics['ville_de_paris'])
            self.g.add((subject_uri, self.olympics.hasOfficialCity, city_uri))

    def process_csv_to_rdf(self, input_csv, output_rdf):
        """Convert CSV triplets to RDF format"""
        df = pd.read_csv(input_csv)
        print(f"Processing {len(df)} triplets...")
        
        for _, row in df.iterrows():
            try:
                # Process subject
                subject_class = self.map_subject_to_class(row['head'], row['type'])
                if not subject_class:  # Skip if no valid class mapping
                    continue
                    
                subject_uri = URIRef(self.olympics[self.safe_uri(row['head'])])
                self.g.add((subject_uri, RDF.type, subject_class))
                self.g.add((subject_uri, RDFS.label, Literal(row['head'])))
                
                # Map predicate
                predicate = self.map_predicate(row['type'])
                if not predicate:  # Skip if predicate is filtered out
                    continue
                
                # Process object
                if row['tail'].isdigit() and len(row['tail']) == 4:  # Year
                    object_value = Literal(row['tail'] + "-01-01", datatype=XSD.date)
                else:
                    object_class = self.map_subject_to_class(row['tail'], row['type'])
                    if object_class:
                        object_uri = URIRef(self.olympics[self.safe_uri(row['tail'])])
                        self.g.add((object_uri, RDF.type, object_class))
                        self.g.add((object_uri, RDFS.label, Literal(row['tail'])))
                        object_value = object_uri
                    else:
                        object_value = Literal(row['tail'])
                
                # Add main triple
                self.g.add((subject_uri, predicate, object_value))
                
                # Add additional triples
                self.add_additional_triples(subject_uri, subject_class, row)
                
            except Exception as e:
                print(f"Error processing row {row}: {str(e)}")
        
        # Save to file
        self.g.serialize(destination=output_rdf, format="turtle")
        print(f"RDF data saved to {output_rdf}")
        
        # Print statistics
        print(f"\nStatistics:")
        print(f"Total triples: {len(self.g)}")
        print(f"Unique subjects: {len(set(self.g.subjects()))}")
        print(f"Unique predicates: {len(set(self.g.predicates()))}")
        print(f"Unique objects: {len(set(self.g.objects()))}")

def main():
    converter = OlympicsRDFConverter()
    input_csv = "extracted_triplets.csv"
    output_rdf = "olympics_knowledge.ttl"
    
    try:
        converter.process_csv_to_rdf(input_csv, output_rdf)
    except Exception as e:
        print(f"Error converting CSV to RDF: {str(e)}")

if __name__ == "__main__":
    main()