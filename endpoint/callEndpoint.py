import requests
import urllib.parse

# Définir l'URL de l'endpoint SPARQL µService
endpoint_url = "http://localhost/service/JO/getInfosStade"

# Nom du stade à rechercher
stade_name = "STADE DE FRANCE"
#stade_name = "I930660048"

# Encodage correct du nom du stade
stade_name_encoded = urllib.parse.quote(stade_name)  # encodage correct une seule fois

# Requête SPARQL
sparql_query = """
SELECT * WHERE {
  ?sub ?pred ?obj .
}
"""

# Configuration de la requête HTTP
params = {"name": stade_name}  # Utiliser le nom encodé correctement
headers = {
    "Accept": "application/sparql-results+json",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Effectuer la requête HTTP POST
try:
    response = requests.post(
        endpoint_url, 
        params=params, 
        data={"query": sparql_query}, 
        headers=headers)

    # Vérifier le statut de la réponse
    if response.status_code == 200:
        # Afficher les résultats
        results = response.json()
        print("Résultats de la requête SPARQL :")
        for binding in results.get("results", {}).get("bindings", []):
            print(binding)
    else:
        print(f"Erreur HTTP {response.status_code}: {response.text}")

except requests.RequestException as e:
    print(f"Erreur lors de la requête : {e}")
