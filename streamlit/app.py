import streamlit as st
import pandas as pd
import requests
from rdflib import Graph, Namespace, URIRef, OWL, RDF, RDFS
from pyvis.network import Network
import networkx as nx
import json
import tempfile
from streamlit_folium import folium_static
import folium
from queriesRfd import *

# Configuration de la page
st.set_page_config(
    page_title="JO Paris 2024 - Explorateur SPARQL",
    page_icon="🏅",
    layout="wide"
)

# Map item_choice to the corresponding queries
query_mapping = {
    "Stades": STADES_QUERIES,
    "Equipes": EQUIPES_QUERIES,
    "Medailles": MEDAILLES_QUERIES,
    "Athletes": ATHLETES_QUERIES,
    "Disciplines": DISCIPLINES_QUERIES,
    "Visualisation": {
        "Relations": """
        PREFIX : <http://example.org/olympics#>
        CONSTRUCT {
            ?s ?p ?o
        }
        WHERE {
            ?s ?p ?o .
            FILTER(!isBlank(?s))
            FILTER(!isBlank(?o))
        }
        LIMIT 1000
        """
    }
}

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
        s_label = str(s).split('#')[-1].replace('%20', ' ')
        p_label = str(p).split('#')[-1].replace('%20', ' ')
        o_label = str(o).split('#')[-1].replace('%20', ' ')
        
        # Ajout des nœuds s'ils n'existent pas déjà
        if s_label not in added_nodes:
            net.add_node(s_label, label=s_label, title=str(s))
            added_nodes.add(s_label)
        if o_label not in added_nodes:
            net.add_node(o_label, label=o_label, title=str(o))
            added_nodes.add(o_label)
            
        # Ajout de l'arête
        net.add_edge(s_label, o_label, label=p_label, title=str(p))
    
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
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
        net.save_graph(tmp.name)
        with open(tmp.name, 'r', encoding='utf-8') as f:
            html_string = f.read()
        st.components.v1.html(html_string, height=800)

def create_map(df):
    """Crée une carte avec les stades"""
    if df is None or df.empty or 'lat' not in df.columns or 'lon' not in df.columns:
        st.error("Pas de données à afficher sur la carte")
        return
        
    try:
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)
        
        for idx, row in df.iterrows():
            popup_content = f"{row['name']}"
            if 'capacity' in row:
                popup_content += f"<br>Capacité: {row['capacity']}"
            if 'description' in row:
                popup_content += f"<br>{row['description']}"
                
            folium.Marker(
                [float(row['lat']), float(row['lon'])],
                popup=popup_content,
                tooltip=row['name']
            ).add_to(m)
        
        folium_static(m)
    except Exception as e:
        st.error(f"Erreur lors de la création de la carte: {str(e)}")

def load_graph():
    """Charge les données RDF depuis les deux fichiers Turtle"""
    g = Graph()
    try:
        # Liste des fichiers à charger
        files = [
            ("../data/data/output_og_24.ttl", "fichier des JO")        
            ]
        
        for file_path, description in files:
            try:
                g.parse(file_path, format="turtle")
                st.sidebar.success(f"{description} chargé avec succès")
            except Exception as e:
                st.sidebar.error(f"Erreur lors du chargement de {description}: {str(e)}")
                st.sidebar.info("Tentative de continuer avec les données disponibles...")
        
        return g
    except Exception as e:
        st.error(f"Erreur critique lors du chargement des données: {str(e)}")
        return None

def execute_query(g, query):
    """Exécute une requête SPARQL avec gestion des appels service"""
    if g is None:
        st.error("Graphe non initialisé")
        return None
        
    try:
        # Vérifier si c'est une requête pour les stades
        if "SERVICE" in query:
            import re
            
            # Extraire le nom du stade (entre name= et >)
            match = re.search(r'getInfosStade\?name=(.*?)>', query)
            if match:
                stade_name = match.group(1)
                
                # Ne pas utiliser quote() car les paramètres requests seront déjà encodés
                params = {
                    'query': """
                    SELECT DISTINCT * WHERE {
                        ?x ?y ?z
                    }
                    """,
                    'name': stade_name,  # Le nom tel quel, requests fera l'encodage
                    'querymode': 'sparql'
                }
                
                # Headers pour spécifier que nous attendons du JSON
                headers = {
                    'Accept': 'application/sparql-results+json'
                }
                
                # Faire l'appel HTTP au service
                response = requests.get(
                    "http://localhost/service/JO/getInfosStade",
                    params=params,
                    headers=headers
                )
                                
                if response.status_code == 200:
                    json_data = response.json()
                    
                    # Transformer la réponse JSON en DataFrame
                    records = []
                    current_record = {}
                    
                    for binding in json_data['results']['bindings']:
                        x_value = binding['x']['value'].split('#')[-1]
                        y_value = binding['y']['value'].split('#')[-1]
                        z_value = binding['z']['value']
                        
                        # Mapper les propriétés aux noms de colonnes
                        if 'name' in y_value.lower():
                            current_record['name'] = z_value
                        elif 'capacity' in y_value.lower():
                            current_record['capacity'] = int(z_value)
                        elif 'description' in y_value.lower():
                            current_record['description'] = z_value
                        elif 'latitude' in y_value.lower():
                            current_record['lat'] = float(z_value)
                        elif 'longitude' in y_value.lower():
                            current_record['lon'] = float(z_value)
                        
                        # Si nous avons toutes les infos nécessaires
                        if len(current_record) > 0 and 'name' in current_record:
                            if current_record not in records:
                                records.append(current_record.copy())
                    
                    return pd.DataFrame(records)
                else:
                    st.error(f"Erreur lors de l'appel au service: {response.status_code}")
                    st.error(f"Réponse du service: {response.text}")
                    return None
                    
        # Pour les autres requêtes, utiliser le comportement normal
        if "CONSTRUCT" in query:
            return g.query(query)
        
        results = g.query(query)
        df = pd.DataFrame(results, columns=results.vars)
        
        # Nettoyage des valeurs si nécessaire
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(lambda x: str(x).replace('%20', ' '))
                
        return df
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
        import traceback
        st.error(f"Détails de l'erreur: {traceback.format_exc()}")
        return None

def main():
    st.title("🏅 Explorateur SPARQL - JO Paris 2024")
    
    try:
        # Chargement du graphe
        g = load_graph()
        st.sidebar.success("Données chargées avec succès!")
    except Exception as e:
        st.sidebar.error(f"Erreur lors du chargement des données: {str(e)}")
        return

    # Sidebar pour la sélection des requêtes
    st.sidebar.title("Navigation")
    
    # Dropdown pour les thèmes
    item_choice = st.sidebar.selectbox(
        "Choisissez un thème préenregistré",
        ["Stades", "Equipes", "Medailles", "Athletes", "Disciplines", "Visualisation"]
    )

    if item_choice != None:
        st.write(f"Liste des requêtes pour : {item_choice}")
        query_choice = st.sidebar.radio(
            "Choisissez une requête pré-enregistrée",
            list(query_mapping.get(item_choice).keys())
        )

        with st.expander("Voir la requête SPARQL"):
            st.code(query_mapping.get(item_choice)[query_choice], language="sparql")

        try:
            results = execute_query(g, query_mapping.get(item_choice)[query_choice])

            # Traitement spécial pour la visualisation
            if item_choice == "Visualisation":
                create_graph_visualization(results)
            else:
                # Affichage standard des résultats
                if isinstance(results, pd.DataFrame) and not results.empty:
                    st.dataframe(results, use_container_width=True)

                    # Affichage de la carte pour les requêtes de stades avec coordonnées
                    if item_choice == "Stades" and "lat" in results.columns and "lon" in results.columns:
                        create_map(results)

                    # Export des données
                    st.sidebar.download_button(
                        label="📥 Télécharger les résultats (CSV)",
                        data=results.to_csv(index=False).encode('utf-8'),
                        file_name=f"jo_paris_2024_{query_choice.lower().replace(' ', '_')}.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Erreur lors de l'exécution de la requête: {str(e)}")

if __name__ == "__main__":
    main()