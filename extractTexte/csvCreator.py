import csv
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

class OlympicsRDFConverter:
    def __init__(self):
        self.olympics_ns = Namespace("http://example.org/olympics#")
        self.g = Graph()
        self.g.bind("olympics", self.olympics_ns)
        
        # Initialize REBEL model
        self.triplet_extractor = pipeline('text2text-generation', 
                                        model='Babelscape/rebel-large', 
                                        tokenizer='Babelscape/rebel-large')

    def extract_triplets_from_text(self, text_path):
        """Extract triplets from text using REBEL model"""
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Split into chunks for processing
        chunks = text.split("\n\n")
        all_triplets = []
        
        for chunk in chunks:
            extracted_text = self.triplet_extractor.tokenizer.batch_decode(
                [self.triplet_extractor(chunk, return_tensors=True, return_text=False)[0]["generated_token_ids"]]
            )
            triplets = self.parse_rebel_output(extracted_text[0])
            all_triplets.extend(triplets)
            
        return all_triplets

    def parse_rebel_output(self, text):
        """Parse REBEL output into structured triplets"""
        triplets = []
        relation, subject, relation, object_ = '', '', '', ''
        text = text.strip()
        current = 'x'
        
        for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
            if token == "<triplet>":
                current = 't'
                if relation != '':
                    triplets.append({
                        'head': subject.strip(),
                        'type': relation.strip(),
                        'tail': object_.strip()
                    })
                relation = ''
                subject = ''
            elif token == "<subj>":
                current = 's'
                if relation != '':
                    triplets.append({
                        'head': subject.strip(),
                        'type': relation.strip(),
                        'tail': object_.strip()
                    })
                object_ = ''
            elif token == "<obj>":
                current = 'o'
                relation = ''
            else:
                if current == 't':
                    subject += ' ' + token
                elif current == 's':
                    object_ += ' ' + token
                elif current == 'o':
                    relation += ' ' + token

        if subject != '' and relation != '' and object_ != '':
            triplets.append({
                'head': subject.strip(),
                'type': relation.strip(),
                'tail': object_.strip()
            })
        return triplets

    def map_to_ontology(self, triplets):
        """Map extracted triplets to ontology classes and properties"""
        mapped_triples = []
        
        for triplet in triplets:
            # Map subject to appropriate class
            subject_uri = self.get_or_create_resource(triplet['head'])
            
            # Map predicate to ontology property
            predicate_uri = self.map_predicate(triplet['type'])
            
            # Map object to appropriate class or literal
            object_uri = self.get_or_create_resource(triplet['tail'])
            
            if all([subject_uri, predicate_uri, object_uri]):
                mapped_triples.append((subject_uri, predicate_uri, object_uri))
        
        return mapped_triples

    def get_or_create_resource(self, text):
        """Create or get URI for a resource based on text"""
        # Add logic to determine appropriate class and create URI
        # This is where you'll implement the mapping logic based on your ontology
        pass

    def map_predicate(self, relation):
        """Map extracted relation to ontology property"""
        # Add mapping logic for predicates
        # This should align with your ontology properties
        predicate_mapping = {
            "participates in": self.olympics_ns.participatesIn,
            "represents": self.olympics_ns.represent,
            "has nationality": self.olympics_ns.hasNationality,
            # Add more mappings based on your ontology
        }
        return predicate_mapping.get(relation.lower())

    def save_to_rdf(self, output_path, format="turtle"):
        """Save the graph to RDF file"""
        self.g.serialize(destination=output_path, format=format)

    def process_text_to_rdf(self, input_text_path, output_rdf_path):
        """Main processing pipeline"""
        # Extract triplets
        triplets = self.extract_triplets_from_text(input_text_path)
        
        # Map to ontology
        mapped_triples = self.map_to_ontology(triplets)
        
        # Add to graph
        for s, p, o in mapped_triples:
            self.g.add((s, p, o))
        
        # Save
        self.save_to_rdf(output_rdf_path)

# Usage
converter = OlympicsRDFConverter()
converter.process_text_to_rdf("text.txt", "olympics_output.ttl")