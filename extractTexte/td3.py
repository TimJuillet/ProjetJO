from transformers import pipeline
import networkx as nx
import matplotlib.pyplot as plt
import os
import re
from tqdm import tqdm

# Initialize REBEL pipeline
triplet_extractor = pipeline('text2text-generation',
                             model='Babelscape/rebel-large',
                             tokenizer='Babelscape/rebel-large')


def chunk_text_by_sentences(text, sentences_per_chunk):
    
    abbreviations = r'(?<!Mr)(?<!Ms)(?<!Mrs)(?<!Dr)(?<!Prof)(?<![A-Z])'
    sentence_pattern = rf'{abbreviations}[.!?](?=\s+[A-Z])'
    text_marked = re.sub(sentence_pattern, r'\g<0>|SPLIT|', text)
    sentences = [s.strip() for s in text_marked.split('|SPLIT|')]
    sentences = [s for s in sentences if s]
    
    total_sentences = len(sentences)
    print(f"\nNombre total de phrases détectées : {total_sentences}")
    
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = ' '.join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk)
    
    print(f"Nombre de chunks créés : {len(chunks)}")
    print(f"Taille de chunk : {sentences_per_chunk} phrases par chunk")
    print(f"Capacité totale de traitement : {len(chunks) * sentences_per_chunk} phrases\n")

    return chunks, sentences


def extract_triplets(text):
    triplets = []
    relation, subject, object_ = '', '', ''
    current = 'x'
    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
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
        triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
    return triplets


def create_knowledge_graph(text):
    
    sentences_per_chunk = 3
    
    # Split text into chunks
    text_chunks, all_sentences = chunk_text_by_sentences(text, sentences_per_chunk=sentences_per_chunk)
    
    print("Démarrage de l'extraction des triplets...")
    
    # Extract triplets from each chunk with progress bar
    all_triplets = []
    for i, chunk in enumerate(tqdm(text_chunks, desc="Traitement des chunks", unit="chunk")):
        # Extract text using REBEL
        extracted_text = triplet_extractor.tokenizer.batch_decode([
            triplet_extractor(chunk,
                              return_tensors=True,
                              return_text=False,
                              num_beams=50,
                              early_stopping=True)[0]["generated_token_ids"]
        ])

        # Extract and add triplets from this chunk
        chunk_triplets = extract_triplets(extracted_text[0])
        
        # Afficher les phrases du chunk actuel
        start_idx = i * sentences_per_chunk
        end_idx = min((i + 1) * sentences_per_chunk, len(all_sentences))
        print(f"\nChunk {i+1} (phrases {start_idx + 1} à {end_idx}):")
        print("Phrases dans ce chunk:")
        for j in range(start_idx, end_idx):
            print(f"  Phrase {j+1}: {all_sentences[j]}")
        
        print(f"\nNombre de triplets extraits dans ce chunk : {len(chunk_triplets)}")
        for triplet in chunk_triplets:
            print(f"  {triplet['head']} -- {triplet['type']} --> {triplet['tail']}")
            
        all_triplets.extend(chunk_triplets)

    print(f"\nNombre TOTAL de triplets extraits : {len(all_triplets)}")
    print("\nCréation du graphe de connaissances avec TOUS les triplets...")
    
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges with progress bar
    for triplet in tqdm(all_triplets, desc="Ajout des nœuds et relations", unit="triplet"):
        G.add_node(triplet['head'])
        G.add_node(triplet['tail'])
        G.add_edge(triplet['head'], triplet['tail'], relation=triplet['type'])

    print(f"\nNombre total de nœuds dans le graphe : {G.number_of_nodes()}")
    print(f"Nombre total de relations dans le graphe : {G.number_of_edges()}")
    
    return G, all_triplets

def visualize_graph(G):
    print("\nCréation de la visualisation...")
    
    plt.figure(figsize=(24, 20))
    
    # Essayer d'abord le layout Kamada-Kawai qui minimise les croisements
    try:
        pos = nx.kamada_kawai_layout(G)
    except:
        # Si ça ne fonctionne pas, utiliser un spring layout optimisé
        pos = nx.spring_layout(
            G,
            k=30,
            iterations=5000,  # Plus d'itérations pour une meilleure convergence
            seed=42,
            scale=2.0      # Échelle plus grande
        )
    
    # Dessiner les arêtes d'abord (pour qu'elles soient derrière les nœuds)
    nx.draw_networkx_edges(
        G, 
        pos,
        edge_color='gray',
        arrows=True,
        arrowsize=20,
        width=2,
        alpha=0.6,
        connectionstyle="arc3,rad=0.2"  # Courber légèrement les arêtes pour réduire les croisements
    )
    
    # Dessiner les nœuds
    nx.draw_networkx_nodes(
        G, 
        pos,
        node_color='lightblue',
        node_size=4000,
        alpha=0.7,
        node_shape='o',
        edgecolors='black',
        linewidths=2
    )
    
    # Dessiner les labels des nœuds
    nx.draw_networkx_labels(
        G, 
        pos,
        font_size=10,
        font_weight='bold',
        font_family='sans-serif'
    )
    
    # Dessiner les labels des arêtes avec un meilleur positionnement
    edge_labels = nx.get_edge_attributes(G, 'relation')
    nx.draw_networkx_edge_labels(
        G, 
        pos,
        edge_labels=edge_labels,
        font_size=8,
        font_weight='bold',
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2),
        label_pos=0.5,    # Position du label sur l'arête
        rotate=False      # Ne pas faire pivoter les labels
    )
    
    plt.title("Knowledge Graph", fontsize=20, pad=20)
    plt.axis('off')
    
    # Ajuster les marges et le layout
    plt.margins(0.2)
    plt.tight_layout()
    
    return plt

def optimize_graph_layout(G):
    """Optimise la structure du graphe avant la visualisation."""
    # Supprimer les nœuds isolés
    G.remove_nodes_from(list(nx.isolates(G)))
    
    # Simplifier les arêtes multiples entre les mêmes nœuds
    edges_to_combine = {}
    for (u, v, data) in G.edges(data=True):
        if (u, v) in edges_to_combine:
            edges_to_combine[(u, v)].append(data['relation'])
        else:
            edges_to_combine[(u, v)] = [data['relation']]
    
    # Recréer le graphe avec les arêtes combinées
    H = nx.DiGraph()
    for (u, v), relations in edges_to_combine.items():
        if len(relations) > 1:
            # Combiner les relations multiples
            combined_relation = ' / '.join(set(relations))
        else:
            combined_relation = relations[0]
        H.add_edge(u, v, relation=combined_relation)
    
    return H


def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the text file (assumes the text file is in the same directory as the script)
    text_file_path = os.path.join(script_dir, 'text.txt')

    # Read text from file
    print("Lecture du fichier texte...")
    with open(text_file_path, 'r', encoding='utf-8') as file:
        text = file.read().strip()

    # Create knowledge graph
    graph, extracted_triplets = create_knowledge_graph(text)
    
    optimized_graph = optimize_graph_layout(graph)

    print("\nCréation de la visualisation...")

    # Visualize the graph
    plt = visualize_graph(optimized_graph)
    print("Affichage du graphe...")
    plt.show()


if __name__ == "__main__":
    main()