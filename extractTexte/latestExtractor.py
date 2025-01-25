import pandas as pd
from transformers import pipeline
import nltk
from pathlib import Path

class OlympicsExtractor:
    def __init__(self):
        # Initialisation de REBEL
        self.extractor = pipeline('text2text-generation', 
                                model='Babelscape/rebel-large', 
                                tokenizer='Babelscape/rebel-large')
        
    def extract_triplets(self, text):
        """Extrait les triplets avec REBEL"""
        triplets = []
        relation, subject, relation, object_ = '', '', '', ''
        
        # Extraction avec REBEL
        text = text.strip()
        current = 'x'
        
        # Obtenir le texte généré par REBEL
        extracted = self.extractor(text, return_tensors=True, return_text=False)
        extracted_text = self.extractor.tokenizer.batch_decode(
            [extracted[0]["generated_token_ids"]]
        )[0]
        
        # Parser la sortie de REBEL
        for token in extracted_text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
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

    def process_text(self, text_path):
        """Traite le texte par morceaux"""
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Diviser en paragraphes pour traitement
        chunks = text.split('\n\n')
        all_triplets = []
        
        for chunk in chunks:
            if chunk.strip():
                # Extraire les triplets de chaque morceau
                chunk_triplets = self.extract_triplets(chunk)
                all_triplets.extend(chunk_triplets)
        
        return all_triplets

    def map_to_ontology(self, triplets):
        """Mappe les triplets vers l'ontologie"""
        mapped_triplets = []
        
        # Mapping des types
        type_mapping = {
            'est un pays': 'rdf:type|Country',
            'est une ville': 'rdf:type|City',
            'est un site': 'rdf:type|Venue',
            'est les jeux': 'rdf:type|Olympics',
            'situé dans': 'hasCity',
            'accueille': 'hasVenue',
            'se déroule à': 'hasOfficialCity'
        }
        
        for triplet in triplets:
            relation = triplet['type'].lower()
            
            # Chercher dans le mapping
            if relation in type_mapping:
                mapped_relation = type_mapping[relation]
                if '|' in mapped_relation:  # C'est un type
                    rel, type_class = mapped_relation.split('|')
                    mapped_triplets.append({
                        'head': triplet['head'],
                        'type': rel,
                        'tail': type_class
                    })
                else:  # C'est une relation
                    mapped_triplets.append({
                        'head': triplet['head'],
                        'type': mapped_relation,
                        'tail': triplet['tail']
                    })
        
        return mapped_triplets

    def save_triplets(self, triplets, output_path):
        """Sauvegarde les triplets en CSV"""
        df = pd.DataFrame(triplets)
        df.to_csv(output_path, index=False)
        print(f"\nSaved {len(triplets)} triplets to {output_path}")
        
        # Afficher les triplets extraits
        print("\nExtracted triplets:")
        for i, triplet in enumerate(triplets, 1):
            print(f"{i}. {triplet['head']} | {triplet['type']} | {triplet['tail']}")

def main():
    extractor = OlympicsExtractor()
    input_file = "text.txt"
    output_file = "olympic_triplets.csv"
    
    # Extraire les triplets
    print("Extracting triplets...")
    triplets = extractor.process_text(input_file)
    
    # Mapper à l'ontologie
    print("Mapping to ontology...")
    mapped_triplets = extractor.map_to_ontology(triplets)
    
    # Sauvegarder
    extractor.save_triplets(mapped_triplets, output_file)

if __name__ == "__main__":
    main()