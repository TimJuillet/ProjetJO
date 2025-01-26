import streamlit as st
import pandas as pd
from rdflib import Graph, Namespace, OWL, RDF, RDFS
from pyvis.network import Network
import tempfile
from streamlit_folium import folium_static
import folium
from queries import PRESET_QUERIES

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
    """Charge les données RDF depuis les fichiers Turtle"""
    g = Graph()
    g.bind('olympics', OLYMPICS)
    g.bind('owl', OWL)
    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)

    try:
        for file_path in ["../data/struct/olympic.ttl", "../data/data/output_og_24.ttl"]:
            try:
                g.parse(file_path, format="turtle")
                st.sidebar.success(f"Fichier {file_path} chargé avec succès")
            except Exception as e:
                st.sidebar.warning(f"Erreur lors du chargement de {file_path}: {str(e)}")
        return g
    except Exception as e:
        st.error(f"Erreur critique lors du chargement des données: {str(e)}")
        return None

def execute_query(g, query):
    """Exécute une requête SPARQL"""
    if g is None:
        st.error("Graphe non initialisé")
        return None
    try:
        results = g.query(query)
        if len(results) == 0:
            st.warning("La requête n'a retourné aucun résultat.")
            return pd.DataFrame()
        return pd.DataFrame(results, columns=results.vars)
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
        return pd.DataFrame()

def display_validation_rules(results_df):
    """Affiche les règles de validation SHACL"""
    if results_df is None or results_df.empty:
        st.error("Aucune donnée SHACL disponible.")
        return

    if 'shape' not in results_df.columns or 'targetClass' not in results_df.columns:
        st.error("Les colonnes 'shape' ou 'targetClass' sont absentes des résultats.")
        return

    for shape in results_df['shape'].unique():
        shape_data = results_df[results_df['shape'] == shape]
        st.markdown(f"**Shape: {shape}**")
        st.markdown(f"Target Class: {shape_data['targetClass'].iloc[0]}")
        constraints = []
        for _, row in shape_data.iterrows():
            if pd.notna(row['property']):
                constraint = f"- Property: {row['property']}"
                if pd.notna(row['minCount']):
                    constraint += f" (min: {row['minCount']})"
                if pd.notna(row['maxCount']):
                    constraint += f" (max: {row['maxCount']})"
                if pd.notna(row['datatype']):
                    constraint += f" (type: {row['datatype']})"
                constraints.append(constraint)
        if constraints:
            st.markdown("Constraints:")
            for constraint in constraints:
                st.markdown(constraint)
        st.markdown("---")

def display_statistics(results_df):
    """Affiche les statistiques sous forme de graphique"""
    if results_df is None or results_df.empty:
        st.error("Aucune donnée disponible pour les statistiques.")
        return

    if 'classUri' not in results_df.columns or 'count' not in results_df.columns:
        st.error("Les colonnes 'classUri' ou 'count' sont absentes des résultats.")
        return

    results_df['classUri'] = results_df['classUri'].apply(lambda x: str(x).split('#')[-1])
    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown("### Statistiques par classe")
        st.dataframe(results_df)

    with col2:
        st.markdown("### Distribution des instances")
        st.bar_chart(data=results_df.set_index('classUri')['count'])

def main():
    st.title("🏅 Explorateur SPARQL - JO Paris 2024")
    g = load_graph()

    if g is None:
        st.error("Impossible de continuer sans données valides.")
        return

    st.sidebar.title("Navigation")
    query_choice = st.sidebar.radio("Choisissez une requête pré-enregistrée", list(PRESET_QUERIES.keys()))
    st.header("Résultats de la requête")

    with st.expander("Voir la requête SPARQL"):
        st.code(PRESET_QUERIES[query_choice], language="sparql")

    results = execute_query(g, PRESET_QUERIES[query_choice])

    if query_choice == "Validation SHACL":
        display_validation_rules(results)
    elif query_choice == "Statistiques des données":
        display_statistics(results)
    else:
        if results is not None and not results.empty:
            st.dataframe(results, use_container_width=True)

if __name__ == "__main__":
    main()
