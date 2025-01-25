import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline
import pandas as pd

class OntologyTripletExtractor:
    def __init__(self, model_name='Babelscape/rebel-large'):
        """Initialise l'extracteur de triplets basé sur REBEL."""
        nltk.download("punkt", quiet=True)
        self.triplet_extractor = pipeline('text2text-generation', 
                                          model=model_name, 
                                          tokenizer=model_name)
        print("Modèle REBEL chargé avec succès.")

        # Ontology-based mapping rules
        self.allowed_relations = {
            "located in the administrative territorial entity": ":hasCountry",
            "represents": ":represent",
            "participates in": ":participatesIn",
            "has performance": ":hasPerformance",
            "has coordinate": ":hasCoordinate",
            "hosts": ":hosts",
            "has capacity": ":hasCapacity",
        }
        self.entity_types = {
            "City": ":City",
            "Country": ":Country",
            "Venue": ":Venue",
            "Athlete": ":Athlete",
            "Event": ":Event",
            "Performance": ":Performance",
        }

    def extract_triplets(self, text):
        """Extrait des triplets depuis un texte en utilisant le modèle REBEL."""
        extracted_text = self.triplet_extractor(text, return_text=True, return_tensors=False)[0]['generated_text']
        print("Texte généré par REBEL :", extracted_text)  # Ligne de débogage
        triplets = self.parse_triplets(extracted_text)
        return self.filter_and_map_triplets(triplets)


    def parse_triplets(self, text):
        """Parse le texte généré par REBEL pour extraire des triplets."""
        triplets = []
        subject, relation, object_ = "", "", ""
        current = None

        for token in text.split():
            if token == "<triplet>":
                if subject and relation and object_:
                    triplets.append((subject.strip(), relation.strip(), object_.strip()))
                subject, relation, object_ = "", "", ""
                current = "subject"
            elif token == "<subj>":
                current = "subject"
            elif token == "<obj>":
                current = "object"
            elif token == "<rel>":
                current = "relation"
            else:
                if current == "subject":
                    subject += " " + token
                elif current == "relation":
                    relation += " " + token
                elif current == "object":
                    object_ += " " + token

        # Ajouter le dernier triplet
        if subject and relation and object_:
            triplets.append((subject.strip(), relation.strip(), object_.strip()))

        return triplets

    def filter_and_map_triplets(self, triplets):
        """Filtre et mappe les triplets selon les règles de l'ontologie."""
        mapped_triplets = []
        for subj, rel, obj in triplets:
            # Vérifie si la relation est dans l'ontologie
            if rel in self.allowed_relations:
                mapped_rel = self.allowed_relations[rel]
                mapped_triplets.append({
                    "subject": subj,
                    "relation": mapped_rel,
                    "object": obj
                })
        return mapped_triplets

    def process_text(self, text, output_csv=None):
        """Traite un texte et exporte les triplets extraits."""
        sentences = sent_tokenize(text)  # Diviser en phrases
        all_triplets = []

        for i, sentence in enumerate(sentences):
            print(f"Traitement de la phrase {i+1}/{len(sentences)} : {sentence}")  # Ligne de débogage
            triplets = self.extract_triplets(sentence)
            all_triplets.extend(triplets)

        # Exporter les résultats
        if output_csv:
            df = pd.DataFrame(all_triplets)
            df.to_csv(output_csv, index=False)
            print(f"Triplets sauvegardés dans {output_csv}.")
        
        return all_triplets


# Exemple d'utilisation
if __name__ == "__main__":
    text = """Les Jeux olympiques d'été de 2024 se dérouleront à Paris. 
    Les épreuves seront accueillies dans plusieurs sites célèbres de la capitale comme le Trocadéro, 
    la tour Eiffel, le Champ-de-Mars, les Invalides, la place de la Concorde et le Grand Palais. 
    Paris est la ville hôte de ces Jeux, qui sont organisés en France. 
    Les athlètes comme Teddy Riner, Clarisse Agbegnenou et Léon Marchand représentent la France. 
    La délégation française est une équipe qui vise 80 médailles."""
    
    extractor = OntologyTripletExtractor()
    triplets = extractor.process_text(text, output_csv="ontology_triplets.csv")
    print("Triplets extraits :", triplets)
