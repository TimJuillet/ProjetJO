import streamlit as st
import pandas as pd
import requests
from rdflib import Namespace, URIRef, OWL, RDF, RDFS
from pyvis.network import Network
import networkx as nx
import json
import tempfile
from streamlit_folium import folium_static
import folium
from queries import PRESET_QUERIES
from custom_parsers import CustomGraph

# Configuration de la page
st.set_page_config(
    page_title="JO Paris 2024 - Explorateur SPARQL",
    page_icon="🏅",
    layout="wide"
)

# Création des namespaces
OLYMPICS = Namespace("http://example.org/olympics#")

@st.cache_resource
def load_graph():
    """Charge les données RDF des JO depuis les deux fichiers TTL"""
    g = CustomGraph()
    
    # Bind des namespaces
    g.bind('olympics', OLYMPICS)
    g.bind('owl', OWL)
    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    
    try:
        # Liste des fichiers à charger
        files_to_load = [
            "../data/data/output_og_24.ttl",
            "../data/data/paris.ttl"
        ]
        
        # Charger chaque fichier
        for file_path in files_to_load:
            try:
                g.parse(file_path, format="turtle")
                st.sidebar.success(f"Fichier {file_path} chargé avec succès")
            except Exception as e:
                st.sidebar.warning(f"Erreur lors du chargement de {file_path}: {str(e)}")
                st.sidebar.info("Tentative de continuer avec les données disponibles...")
                continue
        
        return g
    except Exception as e:
        st.error(f"Erreur critique lors du chargement des données: {str(e)}")
        return None

def execute_query(g, query):
    """Exécute une requête SPARQL avec nettoyage et ordre correct des colonnes"""
    if g is None:
        st.error("Graphe non initialisé")
        return None
        
    try:
        if "CONSTRUCT" in query:
            return g.query(query)
        
        results = g.query(query)
        df = pd.DataFrame(results, columns=results.vars)
        
        # Nettoyage des données
        for col in df.columns:
            # Nettoyer les noms de colonnes
            new_col = col.split('/')[-1].replace('%20', ' ')
            df.rename(columns={col: new_col}, inplace=True)
            
            # Nettoyer les valeurs
            df[new_col] = df[new_col].apply(lambda x: (
                str(x)
                .split('#')[-1]  # Enlever la partie avant le #
                .split('/')[-1]  # Enlever les chemins
                .replace('%20', ' ')  # Remplacer %20 par espace
                .replace('_at_time_', ' ')  # Nettoyer les timestamps
                .replace('_', ' ')  # Remplacer underscore par espace
            ))
        
        # Réorganiser les colonnes pour avoir x, y, z dans cet ordre
        if set(['x', 'y', 'z']).issubset(df.columns):
            df = df[['x', 'y', 'z']]

        return df
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
        return None

def create_graph_visualization(construct_results):
    """Crée une visualisation du graphe avec pyvis"""
    if construct_results is None:
        st.error("Pas de données à visualiser")
        return
        
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    net.toggle_hide_edges_on_drag(True)
    net.barnes_hut()
    
    # Ajout des nœuds et des arêtes
    added_nodes = set()
    for s, p, o in construct_results:
        # Conversion des URIs en chaînes plus lisibles
        s_label = str(s).split('#')[-1]
        p_label = str(p).split('#')[-1]
        o_label = str(o).split('#')[-1]
        
        # Ajout des nœuds s'ils n'existent pas déjà
        if s_label not in added_nodes:
            net.add_node(s_label, label=s_label, title=str(s))
            added_nodes.add(s_label)
        if o_label not in added_nodes:
            net.add_node(o_label, label=o_label, title=str(o))
            added_nodes.add(o_label)
            
        # Ajout de l'arête
        net.add_edge(s_label, o_label, label=p_label, title=str(p))
    
    # Configuration du graphe
    net.set_options("""
    {
        "physics": {
            "barnesHut": {
                "gravitationalConstant": -2000,
                "centralGravity": 0.3,
                "springLength": 200
            },
            "maxVelocity": 50,
            "minVelocity": 0.75,
            "solver": "barnesHut"
        },
        "edges": {
            "smooth": {
                "type": "continuous",
                "forceDirection": "none"
            }
        }
    }
    """)
    
    # Sauvegarde temporaire et affichage
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
        net.save_graph(tmp.name)
        with open(tmp.name, 'r', encoding='utf-8') as f:
            html_string = f.read()
        st.components.v1.html(html_string, height=800)

def create_map(df):
    """Crée une carte avec les stades"""
    if df is None or df.empty:
        st.error("Pas de données à afficher sur la carte")
        return
        
    try:
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)
        
        for idx, row in df.iterrows():
            folium.Marker(
                [float(row['lat']), float(row['lon'])],
                popup=f"{row['name']}<br>Capacité: {row['capacity']}<br>{row['description']}",
                tooltip=row['name']
            ).add_to(m)
        
        folium_static(m)
    except Exception as e:
        st.error(f"Erreur lors de la création de la carte: {str(e)}")

def main():
    st.title("🏅 Explorateur SPARQL - JO Paris 2024")
    
    # Chargement du graphe
    g = load_graph()
    if g is None:
        st.error("Impossible de continuer sans données valides")
        return
    
    # Sidebar pour la sélection des requêtes
    st.sidebar.title("Navigation")
    query_choice = st.sidebar.radio(
        "Choisissez une requête pré-enregistrée",
        list(PRESET_QUERIES.keys())
    )
    
    # Zone principale
    st.header("Résultats de la requête")
    
    # Affichage de la requête SPARQL
    with st.expander("Voir la requête SPARQL"):
        st.code(PRESET_QUERIES[query_choice], language="sparql")
    
    # Exécution de la requête
    results = execute_query(g, PRESET_QUERIES[query_choice])
    
    if query_choice == "Visualisation des relations":
        # Affichage du graphe de relations
        create_graph_visualization(results)
    elif query_choice == "Informations complètes des stades":
        # Affichage du tableau et de la carte
        if isinstance(results, pd.DataFrame) and not results.empty:
            st.dataframe(results, use_container_width=True)
            create_map(results)
    else:
        # Affichage standard des résultats
        if isinstance(results, pd.DataFrame) and not results.empty:
            st.dataframe(results, use_container_width=True)
            
            # Métriques pour les requêtes avec capacité
            if 'capacity' in results.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nombre de sites", len(results))
                with col2:
                    st.metric("Capacité totale", f"{results['capacity'].sum():,}")
                with col3:
                    st.metric("Capacité moyenne", f"{int(results['capacity'].mean()):,}")
    
    # Export des données
    if isinstance(results, pd.DataFrame) and not results.empty:
        st.sidebar.download_button(
            label="📥 Télécharger les résultats (CSV)",
            data=results.to_csv(index=False).encode('utf-8'),
            file_name=f"jo_paris_2024_{query_choice.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()