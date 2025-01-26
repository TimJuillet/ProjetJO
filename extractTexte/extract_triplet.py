import nltk
from nltk.tokenize import sent_tokenize
from pathlib import Path
from transformers import pipeline
import pandas as pd

class TripletExtractor:
    def __init__(self, model_name='Babelscape/rebel-large'):
        """Initialize the triplet extractor with REBEL model"""
        # Download required NLTK data
        nltk.download("punkt", quiet=True)
        
        # Initialize the REBEL model
        self.triplet_extractor = pipeline('text2text-generation', 
                                        model=model_name, 
                                        tokenizer=model_name)
        print("Triplet extractor loaded successfully")

    def extract_triplets(self, text):
        """Extract triplets from text using REBEL model"""
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

    def process_text_file(self, input_file_path, output_csv_path):
        """Process a text file and save extracted triplets to CSV"""
        # Read input text
        input_path = Path(input_file_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file_path}")

        text = input_path.read_text(encoding='utf-8')
        
        # Split text into chunks
        chunks = text.split("\n\n")
        print(f"Processing {len(chunks)} text chunks...")

        all_triplets = []
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Skip empty chunks
                # Extract triplets using REBEL
                extracted_text = self.triplet_extractor.tokenizer.batch_decode(
                    [self.triplet_extractor(chunk, return_tensors=True, return_text=False)[0]["generated_token_ids"]]
                )
                
                # Parse the extracted triplets
                chunk_triplets = self.extract_triplets(extracted_text[0])
                all_triplets.extend(chunk_triplets)
                
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(chunks)} chunks")

        # Convert to DataFrame and save to CSV
        if all_triplets:
            df = pd.DataFrame(all_triplets)
            df.to_csv(output_csv_path, index=False)
            print(f"Extracted {len(all_triplets)} triplets and saved to {output_csv_path}")
        else:
            print("No triplets were extracted from the text")

        return all_triplets

def main():
    # Example usage
    extractor = TripletExtractor()
    
    input_file = "text.txt"  
    output_file = "extracted_triplets.csv" 
    
    try:
        extractor.process_text_file(input_file, output_file)
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()