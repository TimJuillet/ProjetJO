from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, OWL
import pandas as pd
import re

class OlympicsRDFConverter:
    def __init__(self):
        # Initialize namespaces
        self.olympics = Namespace("http://example.org/olympics#")
        self.g = Graph()
        self.g.bind("olympics", self.olympics)
        
        # Initialize property mappings based on ontology
        self.property_mappings = {
            "located in the administrative territorial entity": self.olympics.hasCity,
            "point in time": self.olympics.startDate,  # Using startDate for temporal information
            "sport": self.olympics.belongsToDiscipline,
            "part of": self.olympics.isPartOfTeam,
            "has part": self.olympics.hasTeam
        }
        
        # Initialize class mappings
        self.class_mappings = {
            "venue": self.olympics.Venue,
            "city": self.olympics.City,
            "athlete": self.olympics.Athlete,
            "discipline": self.olympics.Discipline,
            "team": self.olympics.Team
        }

    def clean_text(self, text):
        """Clean text for URI creation"""
        # Convert to lowercase and replace spaces with underscores
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text

    def create_resource_uri(self, text, class_type=None):
        """Create a proper URI for a resource"""
        clean_id = self.clean_text(text)
        uri = self.olympics[clean_id]
        
        # Add type information if provided
        if class_type:
            self.g.add((uri, RDF.type, class_type))
            
        # Add label
        self.g.add((uri, RDFS.label, Literal(text)))
        
        return uri

    def determine_resource_type(self, entity, relation):
        """Determine the appropriate class type for an entity based on context"""
        # Mapping rules based on relations and known entities
        if "ville" in entity.lower() or relation == "located in the administrative territorial entity":
            return self.olympics.City
        elif any(sport in entity.lower() for sport in ["tennis", "football", "basketball"]):
            return self.olympics.Discipline
        elif "délégation" in entity.lower() or "team" in entity.lower():
            return self.olympics.Team
        elif re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', entity):  # Pattern for person names
            return self.olympics.Athlete
        elif any(venue in entity.lower() for venue in ["palais", "stade", "arena", "tour", "champ"]):
            return self.olympics.Venue
        return None

    def convert_triplets_to_rdf(self, csv_path):
        """Convert extracted triplets to RDF following the ontology"""
        # Read triplets
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            head = row['head']
            relation = row['type']
            tail = row['tail']
            
            # Determine classes for head and tail
            head_type = self.determine_resource_type(head, relation)
            tail_type = self.determine_resource_type(tail, relation)
            
            # Create URIs
            head_uri = self.create_resource_uri(head, head_type)
            tail_uri = self.create_resource_uri(tail, tail_type)
            
            # Get predicate from mapping or create new one
            predicate = self.property_mappings.get(relation)
            if not predicate:
                # If no direct mapping exists, try to infer an appropriate property
                if relation == "sport":
                    # Create discipline and link it
                    discipline_uri = self.create_resource_uri(tail, self.olympics.Discipline)
                    self.g.add((head_uri, self.olympics.belongsToDiscipline, discipline_uri))
                else:
                    # Use default mapping
                    predicate = self.olympics[self.clean_text(relation)]
            
            if predicate:
                self.g.add((head_uri, predicate, tail_uri))
                
            # Add additional context based on ontology requirements
            if head_type == self.olympics.Athlete:
                # Add mandatory properties for athletes if not present
                self.g.add((head_uri, self.olympics.isDisabled, Literal("false", datatype=XSD.boolean)))
            elif head_type == self.olympics.Venue:
                # Add mandatory city relationship for venues
                if "Paris" in tail:
                    paris_uri = self.create_resource_uri("Paris", self.olympics.City)
                    self.g.add((head_uri, self.olympics.hasCity, paris_uri))

    def save_rdf(self, output_path):
        """Save the RDF graph to a file"""
        self.g.serialize(destination=output_path, format="turtle")

def main():
    converter = OlympicsRDFConverter()
    converter.convert_triplets_to_rdf("extracted_triplets.csv")
    converter.save_rdf("olympics_output.ttl")

if __name__ == "__main__":
    main()