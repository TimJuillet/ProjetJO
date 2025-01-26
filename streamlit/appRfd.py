import streamlit as st
import pandas as pd
import requests
from rdflib import Graph, Namespace
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
}

def load_graph():
    """Charge les données RDF depuis le fichier Turtle"""
    g = Graph()
    g.parse("data.ttl", format="turtle")
    g.parse("../data/data/output_og_24.ttl",format="turtle")
    return g

def execute_query(g, query):
    """Exécute une requête SPARQL et retourne les résultats sous forme de DataFrame"""
    results = g.query(query)
    return pd.DataFrame(results, columns=results.vars)

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
    
    # Dropdown pour les thèmes.
    item_choice = st.sidebar.selectbox(
        "Choisissez un thème préenregistré",
        ["Stades", "Equipes","Medailles","Athletes","Disciplines"]
    )
    # if item 1 chosen display this
    if item_choice != None:
        st.write(f"List des requetes pour : {item_choice}")
        query_choice = st.sidebar.radio(
        "Choisissez une requête pré-enregistrée",
        list(query_mapping.get(item_choice).keys())
        )
        with st.expander("Voir la requête SPARQL"):
            st.code(query_mapping.get(item_choice)[query_choice], language="sparql")
    
    # Zone principale
    st.header("Résultats de la requête")
    
    # Exécution de la requête
    try:
        if item_choice != None:
            results_df = execute_query(g, query_mapping.get(item_choice)[query_choice])        
        # Affichage des résultats
        st.dataframe(results_df, use_container_width=True)
        
        # Métriques
        if 'capacity' in results_df.columns:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nombre de sites", len(results_df))
            with col2:
                st.metric("Capacité totale", f"{results_df['capacity'].sum():,}")
            with col3:
                st.metric("Capacité moyenne", f"{int(results_df['capacity'].mean()):,}")
        
        # Export des données
        if not results_df.empty:
            st.sidebar.download_button(
                label="📥 Télécharger les résultats (CSV)",
                data=results_df.to_csv(index=False).encode('utf-8'),
                file_name=f"jo_paris_2024_{query_choice.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {str(e)}")

if __name__ == "__main__":
    main()