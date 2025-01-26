from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

class OlympicsRDFEnricher:
    def __init__(self):
        self.olympics = Namespace("http://example.org/olympics#")
        self.g = Graph()
        self.g.bind("olympics", self.olympics)

        # Définition des disciplines et leurs trials
        self.discipline_trials = {
            "tennis": {
                "label": "Tennis",
                "trials": [
                    ("tennis_singles", "Tennis Singles", False)
                ]
            },
            "athletics": {
                "label": "Athletics",
                "trials": [
                    ("athletic_100m", "Athletics 100m Sprint", False),
                    ("athletic_200m", "Athletics 200m Sprint", False),
                    ("athletic_triple_jump", "Athletics Triple Jump", False)
                ]
            },
            "judo": {
                "label": "Judo",
                "trials": [
                    ("judo_individual", "Judo Individual", False),
                    ("judo_team", "Judo Team Mixed", True)
                ]
            },
            "swimming": {
                "label": "Swimming",
                "trials": [
                    ("swimming_trial", "Swimming Competition", False)
                ]
            }
        }

    def enrich_disciplines_and_trials(self):
        olympics_2024 = self.olympics.jeux_olympiques_dété_de_2024

        # Enrichir chaque discipline et ses trials
        for disc_id, disc_info in self.discipline_trials.items():
            discipline_uri = self.olympics[disc_id]
            
            # Créer/Mettre à jour la discipline
            self.g.add((discipline_uri, RDF.type, self.olympics.Discipline))
            self.g.add((discipline_uri, RDFS.label, Literal(disc_info["label"])))

            # Créer/Mettre à jour les trials de cette discipline
            for trial_id, trial_label, is_team in disc_info["trials"]:
                trial_uri = self.olympics[trial_id]
                
                # Propriétés du trial
                self.g.add((trial_uri, RDF.type, self.olympics.Trial))
                self.g.add((trial_uri, RDFS.label, Literal(trial_label)))
                self.g.add((trial_uri, self.olympics.belongsToDiscipline, discipline_uri))
                self.g.add((trial_uri, self.olympics.isDisabled, Literal(False)))
                self.g.add((trial_uri, self.olympics.isTeamTrial, Literal(is_team)))
                
                # Lier le trial aux JO
                self.g.add((olympics_2024, self.olympics.hasTrial, trial_uri))

    def enrich_olympics_properties(self):
        # Enrichir les JO 2024
        olympics_2024 = self.olympics.jeux_olympiques_dété_de_2024
        paris_uri = self.olympics.paris
        venue_uri = self.olympics.venue_paris

        # Créer Paris et sa venue
        self.g.add((paris_uri, RDF.type, self.olympics.City))
        self.g.add((paris_uri, RDFS.label, Literal("Paris")))

        self.g.add((venue_uri, RDF.type, self.olympics.Venue))
        self.g.add((venue_uri, RDFS.label, Literal("Main Venue Paris")))

        # Ajouter les propriétés obligatoires
        olympics_properties = {
            self.olympics.endDate: Literal("2024-08-11", datatype=XSD.date),
            self.olympics.season: Literal("Summer"),
            self.olympics.hasOfficialCity: paris_uri,
            self.olympics.hasVenue: venue_uri
        }

        for prop, value in olympics_properties.items():
            self.g.add((olympics_2024, prop, value))

    def enrich_athlete_properties(self):
        # Enrichir Novak Djokovic
        novak_uri = self.olympics.novak_djokovic
        serbia_uri = self.olympics.serbia

        # Créer la Serbie
        self.g.add((serbia_uri, RDF.type, self.olympics.Country))
        self.g.add((serbia_uri, RDFS.label, Literal("Serbia")))

        # Ajouter les propriétés obligatoires
        athlete_properties = {
            self.olympics.surname: Literal("Djokovic"),
            self.olympics.height: Literal(188),
            self.olympics.weight: Literal(77000),
            self.olympics.birthDate: Literal("1987-05-22", datatype=XSD.date),
            self.olympics.gender: Literal("Male"),
            self.olympics.hasNationality: serbia_uri
        }

        for prop, value in athlete_properties.items():
            self.g.add((novak_uri, prop, value))

    def clean_duplicates(self):
        # Supprimer le label tennis en minuscules
        tennis_uri = self.olympics.tennis
        self.g.remove((tennis_uri, RDFS.label, Literal("tennis")))

    def enrich_rdf(self, input_file, output_file):
        # Charger le RDF initial
        self.g.parse(input_file, format="turtle")

        # Appliquer tous les enrichissements
        self.enrich_disciplines_and_trials()
        self.enrich_olympics_properties()
        self.enrich_athlete_properties()
        self.clean_duplicates()

        # Sauvegarder le résultat final
        self.g.serialize(destination=output_file, format="turtle")

def main():
    enricher = OlympicsRDFEnricher()
    enricher.enrich_rdf("olympics_output.ttl", "olympics_enriched.ttl")

if __name__ == "__main__":
    main()