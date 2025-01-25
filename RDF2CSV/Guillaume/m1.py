import csv
import json
import os
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD
import re
from datetime import datetime

def convertir_en_rdf_dateTime(date_str):
    # Convertir la chaîne de date en un objet datetime
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")

    # Convertir l'objet datetime en une chaîne au format xsd:dateTime
    rdf_dateTime = date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

    return rdf_dateTime

def obtenir_premier_terme(chaine):
    # Séparer la chaîne par des espaces et retourner le premier terme
    return chaine.split()[0]

def separer_nom_prenom(chaine):
    # Séparer la chaîne par des espaces
    parts = chaine.split()

    # Le prénom est toujours la première partie, tout en minuscule
    prenom = parts[0].capitalize()

    # Le nom est tout ce qui reste, tout en majuscule
    nom = " ".join(parts[1:]).upper()

    # Retourner les deux valeurs
    return prenom, nom

def normalize_string(s):
    s = s.lower()  # Mettre en minuscule
    s = re.sub(r'\d+', '', s)  # Supprimer les chiffres
    s = s.strip()  # Supprimer les espaces avant et après
    s = ' '.join(s.split())  # Supprimer les espaces multiples
    return s

def capitalize_words(s):
    # Mettre en majuscule chaque début de mot
    return ' '.join(word.capitalize() for word in s.split())

def check_and_create_file(file_path : str):
    """
    Check if the file exists, if not create it.

    Parameters:
        file_path (str): The file path.
    """
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write()

def write_in_file(file_path : str, content : dict):
    """
    Write the content to a file.
    Check if the file exists, if not create it.
    Check if the file extension is in the content dictionary.

    Parameters:
        file_path (str): The file path.
        content (dict): The content to write
    """
    check_and_create_file(file_path)

    file_extension = os.path.splitext(file_path)[1][1:]

    if file_extension in content:
        with open(file_path, 'w') as file:
            json.dump(content[file_extension], file, indent=4)
        print(f"The data has been written to the file '{file_path}'.")
    else:
        print(f"The file extension '{file_extension}' is not in the content dictionary.")

class CSV2RDF :

    def __init__(self, data_path : str, output_path : str, csv_file : str, jsonld_file : str, rdf_file : str, file_to_overwrite : list or str = None):
        self.data_path = data_path
        self.output_path = output_path
        self.csv_file = os.path.join(self.data_path, csv_file)
        self.jsonld_file = os.path.join(self.data_path, jsonld_file)
        self.rdf_file = os.path.join(self.output_path, rdf_file)
        self.file_to_overwrite = file_to_overwrite
        self.dictionnary_file_name = {
            "must": self.csv_file,
            "should": [
                self.jsonld_file,
                self.rdf_file
            ],
        }
        self.check_and_create()

    def remove_overwrite_files(self):
        if not self.file_to_overwrite:
            return
        if self.file_to_overwrite == "all":
            self.file_to_overwrite = self.dictionnary_file_name["should"]
        if not isinstance(self.file_to_overwrite, list):
            return
        for file_path in self.file_to_overwrite:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"The file '{file_path}' has been removed.")

    def check_and_create(self):
        """
        Check if the required files exist in the folders.
        Create the 'data_path' and 'output_path' directories if they do not exist.
        If the 'must' file does not exist, raise a FileNotFoundError.
        If the 'should' files do not exist, create them in the data folder.

        Raises:
            FileNotFoundError: If the 'must' file is not found in the data folder.
        """
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)

        if not os.path.isfile(self.dictionnary_file_name["must"]):
            raise FileNotFoundError(
                f"The required file '{self.dictionnary_file_name['must']}' is not found in the data folder '{self.data_path}'."
            )

        self.remove_overwrite_files()

        for should_file_path, should_file_name in zip(self.dictionnary_file_name["should"], self.dictionnary_file_name["should"]):
            if not os.path.isfile(should_file_path):
                with open(should_file_path, 'w') as file:
                    file.write('{}')
                print(f"The file '{should_file_name}' has been created in the data folder '{self.data_path}'.")


    def generate_type_matrix_mapping(self, base_property_url : str, base_value_url : str) :
        """
        Generate a JSON-LD mapping for the type matrix CSV file.

        Parameters:
            base_property_url (str): The base URL for the property.
            base_value_url (str): The base URL for the value.
        """
        mapping = {
            "@context": "http://www.w3.org/ns/csvw",
            "url": self.csv_file,
            "tableSchema": {
                "columns": []
            }
        }

        with open(self.csv_file, encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)

        mapping["tableSchema"]["columns"].append({
            "name": "Attacking",
            "titles": "Attacking",
            "propertyUrl": "http://schema.org/type"
        })

        for header in headers[1:]:
            mapping["tableSchema"]["columns"].append({
                "name": header,
                "titles": header,
                "datatype": "decimal",
                "propertyUrl": base_property_url,
                "valueUrl": base_value_url + header
            })

        self.jsonld_mapping = {
            "json" : mapping
        }

    def save_type_matrix_mapping(self):
        """
        Write the JSON-LD mapping to a file.
        """
        write_in_file(self.jsonld_file, self.jsonld_mapping)


    def create_rdf(self, namespace : dict, callable_function : callable):
        """
        Convert the CSV file to RDF and save it to a file.

        Parameters:
            namespace (dict): The namespace dictionary.
            callable_function (callable): The function to apply on the RDF graph.
        """

        olympicsParameters = {
            "name": "2024_Summer_Olympics",
            "hostCountry": "France",
            "season": "Summer",
            "hasOfficialCity": "Paris",
            "hasTrial": None,
            "hasVenue": None,
            "startDate": "2024-07-26",
            "endDate": "2024-08-11",
            "olympicHasEvent": None,
            "hasAnnexCity": None,
            "description": "The 2024 Summer Olympics, officially known as the Games of the XXXIII Olympiad, and commonly known as Paris 2024, is a forthcoming international multi-sport event that is scheduled to take place from 26 July to 11 August 2024 in Paris, France."
        }

        g = Graph()
        for prefix, uri in namespace.items():
            g.bind(prefix, uri[0])

        with open(self.csv_file, encoding="utf-8") as f:
            callable_function(g, f, namespace, olympicsParameters)

        g.serialize(destination=self.rdf_file, format="turtle")
        print(f"RDF exporté avec succès dans {self.rdf_file}")

namespace = {
    "": ("http://example.org/olympics#", Namespace("http://example.org/olympics#")),
    "rdf": ("http://www.w3.org/1999/02/22-rdf-syntax-ns#", Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")),
    "owl": ("http://www.w3.org/2002/07/owl#", Namespace("http://www.w3.org/2002/07/owl#")),
    "rdfs": ("http://www.w3.org/2000/01/rdf-schema#", Namespace("http://www.w3.org/2000/01/rdf-schema#")),
    "dc": ("http://purl.org/dc/elements/1.1/", Namespace("http://purl.org/dc/elements/1.1/")),
    "xsd": ("http://www.w3.org/2001/XMLSchema#", Namespace("http://www.w3.org/2001/XMLSchema#")),
    "schema": ("http://schema.org/", Namespace("http://schema.org/")),
    "dbpedia": ("http://dbpedia.org/resource/", Namespace("http://dbpedia.org/resource/")),
}



def function_generate_rdf(g, f, namespace: dict, olympicsParameters: dict):
    constructorRDF = ConstructRDF(g, namespace)
    reader = csv.DictReader(f, delimiter=';')

    BlankCoordinateLongitude = 0.
    BlankCoordinateLatitude = -90.
    BlankCoordinateWritting = "blank_coordinate"
    BlankCoordinateName = "Blank Coordinate"
    BlankCoordinateDescription = "Blank Coordinate for missing data"
    BlankHeight = 0
    BlankWeight = 0
    BlankBirthDate = "1900-01-01"
    BlankDeathDate = "1900-01-02"
    BlankIsDisabled = False
    BlankHasResultUnit = "blank_unit"
    BlankHasResult = "-1"
    separator = "%20"

    constructorRDF.createCoordinate(BlankCoordinateWritting, BlankCoordinateLongitude, BlankCoordinateLatitude, BlankCoordinateName, BlankCoordinateDescription)

    olympicsTrial = []
    olympicsVenue = []
    olympicsEvent = []

    for row in reader:
        is_team_event = normalize_string(row["Name"]) == normalize_string(row["Country"])
        countryName = capitalize_words(normalize_string(row["Country"])).replace(" ", separator)
        discplineName = capitalize_words(normalize_string(row["Discipline"])).replace(" ", separator)
        countryCode = row["Country_code"]
        athleteName = row["Name"].replace(" ", separator)
        personWritting = row["Name"].replace(" ", separator) + "_person"
        trialName = row["Event"].replace(" ", separator)
        trialDescription = row["url_event"]
        prenom, nom = separer_nom_prenom(row["Name"])
        if row["Gender"] == "M":
            gender = "Male"
        else :
            gender = "Female"
        date = convertir_en_rdf_dateTime(row["Medal_date"])
        medalName = row["\ufeffMedal_type"].replace(" ", separator)
        medalWritting = obtenir_premier_terme(row["\ufeffMedal_type"])
        rank = row["Medal_code"]
        performanceWritting = trialName + "_" + athleteName + "_" + date
        performanceName = row["\ufeffMedal_type"] + " " + row["Event"] + " " + row["Name"] + " " + date
        performanceDescription = "Performance of " + row["Name"] + " in " + row["Event"] + " at the " + row["\ufeffMedal_type"] + " on " + date
        eventWritting = trialName + "_" + date
        eventName = row["Event"] + " " + date
        eventDescription = "Event " + row["Event"] + " at the " + row["\ufeffMedal_type"] + " on " + date

        constructorRDF.createCountry(countryName, countryName, countryCode, BlankCoordinateWritting, None)
        constructorRDF.createDiscipline(discplineName, None, discplineName, None)
        success = constructorRDF.createTrial(trialName, discplineName, is_team_event, trialName, trialDescription)
        if success:
            olympicsTrial.append(trialName)
        constructorRDF.createPerson(personWritting, nom, BlankHeight, BlankWeight, BlankBirthDate, BlankDeathDate, gender, countryName, BlankIsDisabled, prenom, None)
        constructorRDF.createAthlete(athleteName, None, personWritting, BlankIsDisabled, countryName)
        constructorRDF.createMedal(medalWritting, medalName, None)
        constructorRDF.createPerformance(performanceWritting, BlankHasResult, rank, trialName, athleteName, BlankHasResultUnit, date, medalWritting, performanceName, performanceDescription)
        success = constructorRDF.createEvent(eventWritting, trialName, date, performanceWritting, olympicsParameters["name"], eventName, eventDescription)
        if success:
            olympicsEvent.append(eventWritting)

    olympicsParameters["hasTrial"] = olympicsTrial
    olympicsParameters["hasVenue"] = olympicsVenue
    olympicsParameters["olympicHasEvent"] = olympicsEvent
    constructorRDF.createOlympics(olympicsParameters["name"],
                                  olympicsParameters["hostCountry"],
                                  olympicsParameters["season"],
                                  olympicsParameters["hasOfficialCity"],
                                  olympicsParameters["hasTrial"],
                                  olympicsParameters["hasVenue"],
                                  olympicsParameters["startDate"],
                                  olympicsParameters["endDate"],
                                  olympicsParameters["olympicHasEvent"],
                                  olympicsParameters["hasAnnexCity"],
                                  olympicsParameters["name"],
                                  olympicsParameters["description"])

class ConstructRDF:

    def __init__(self, g, namespace: dict):
        self.g = g
        self.namespace = namespace
        self.EX = namespace[""][1]
        self.RDF = namespace["rdf"][1]
        self.XSD = namespace["xsd"][1]
        self.countries = {}
        self.disciplines = {}
        self.trial = {}
        self.athletes = {}
        self.teams = {}
        self.persons = {}
        self.units = {}
        self.cities = {}
        self.venues = {}
        self.olympics = {}
        self.medals = {}
        self.records = {}
        self.committees = {}
        self.coordinates = {}

    def createTeam(self, teamWirtting, teamName, teamDescription, isDisabled, hasMember: list, represent):
        if teamWirtting in self.teams:
            return False
        team_uri = URIRef(self.EX[teamWirtting])
        self.g.add((team_uri, RDF.type, self.EX["Team"]))
        if teamName:
            self.g.add((team_uri, self.EX["name"], Literal(teamName, datatype=XSD.string)))
        if teamDescription:
            self.g.add((team_uri, self.EX["description"], Literal(teamDescription, datatype=XSD.string)))
        self.g.add((team_uri, self.EX["isDisabled"], Literal(isDisabled, datatype=XSD.boolean)))
        self.g.add((team_uri, self.EX["represent"], URIRef(self.EX[represent])))
        for member in hasMember:
            self.g.add((team_uri, self.EX["hasMember"], URIRef(self.EX[member])))
        self.teams[teamWirtting] = team_uri
        return True

    def createPerson(self, personWriting, surname, height, weight, birthDate, deathDate, gender, hasNationality,
                     isDisabled, personName, personDescription):
        if personWriting in self.persons:
            return False
        person_uri = URIRef(self.EX[personWriting])
        self.g.add((person_uri, RDF.type, self.EX["Person"]))
        self.g.add((person_uri, self.EX["surname"], Literal(surname, datatype=XSD.string)))
        self.g.add((person_uri, self.EX["height"], Literal(height, datatype=XSD.decimal)))
        self.g.add((person_uri, self.EX["weight"], Literal(weight, datatype=XSD.decimal)))
        self.g.add((person_uri, self.EX["birthDate"], Literal(birthDate, datatype=XSD.date)))

        if deathDate:
            self.g.add((person_uri, self.EX["deathDate"], Literal(deathDate, datatype=XSD.date)))

        self.g.add((person_uri, self.EX["gender"], Literal(gender, datatype=XSD.string)))
        self.g.add((person_uri, self.EX["hasNationality"], URIRef(self.EX[hasNationality])))
        self.g.add((person_uri, self.EX["isDisabled"], Literal(isDisabled, datatype=XSD.boolean)))
        if personName:
            self.g.add((person_uri, self.EX["name"], Literal(personName, datatype=XSD.string)))
        if personDescription:
            self.g.add((person_uri, self.EX["description"], Literal(personDescription, datatype=XSD.string)))

        self.persons[personWriting] = person_uri
        return True

    def createAthlete(self, athleteWriting, isPartOfTeam: list, isPersonOf, isDisabled, represent):
        if athleteWriting in self.athletes:
            return False
        athlete_uri = URIRef(self.EX[athleteWriting])
        self.g.add((athlete_uri, RDF.type, self.EX["Athlete"]))
        self.g.add((athlete_uri, self.EX["isDisabled"], Literal(isDisabled, datatype=XSD.boolean)))
        self.g.add((athlete_uri, self.EX["represent"], URIRef(self.EX[represent])))
        if isPartOfTeam :
            for team in isPartOfTeam:
                self.g.add((athlete_uri, self.EX["isPartOfTeam"], URIRef(self.EX[team])))
        self.g.add((athlete_uri, self.EX["isPersonOf"], URIRef(self.EX[isPersonOf])))
        self.athletes[athleteWriting] = athlete_uri
        return True

    def createUnits(self, unitWriting, unitsInScientificDomain, unitName, unitDescription):
        if unitWriting in self.units:
            return False
        unit_uri = URIRef(self.EX[unitWriting])
        self.g.add((unit_uri, RDF.type, self.EX["Unit"]))
        self.g.add((unit_uri, self.EX["unitsInScientificDomain"], Literal(unitsInScientificDomain, datatype=XSD.string)))
        if unitName:
            self.g.add((unit_uri, self.EX["unitName"], Literal(unitName, datatype=XSD.string)))
        if unitDescription:
            self.g.add((unit_uri, self.EX["unitDescription"], Literal(unitDescription, datatype=XSD.string)))
        self.units[unitWriting] = unit_uri
        return True

    def createCountry(self, countryWriting, countryName, countryCode, Coordinate, countryDescription):
        if countryWriting in self.countries:
            return False
        country_uri = URIRef(self.EX[countryWriting])
        self.g.add((country_uri, RDF.type, self.EX["Country"]))
        if countryName:
            self.g.add((country_uri, self.EX["countryName"], Literal(countryName, datatype=XSD.string)))
        if countryDescription:
            self.g.add((country_uri, self.EX["countryDescription"], Literal(countryDescription, datatype=XSD.string)))
        if countryCode:
            self.g.add((country_uri, self.EX["countryCode"], Literal(countryCode, datatype=XSD.string)))
        self.g.add((country_uri, self.EX["Coordinate"], URIRef(self.EX[Coordinate])))
        self.countries[countryWriting] = country_uri
        return True

    def createCity(self, cityWriting, cityName, cityDescription, cityCode, Coordinate, hasCountry):
        if cityWriting in self.cities:
            return False
        city_uri = URIRef(self.EX[cityWriting])
        self.g.add((city_uri, RDF.type, self.EX["City"]))
        if cityName:
            self.g.add((city_uri, self.EX["cityName"], Literal(cityName, datatype=XSD.string)))
        if cityDescription:
            self.g.add((city_uri, self.EX["cityDescription"], Literal(cityDescription, datatype=XSD.string)))
        if cityCode:
            self.g.add((city_uri, self.EX["cityCode"], Literal(cityCode, datatype=XSD.string)))
        self.g.add((city_uri, self.EX["Coordinate"], URIRef(self.EX[Coordinate])))
        self.g.add((city_uri, self.EX["hasCountry"], URIRef(self.EX[hasCountry])))
        self.cities[cityWriting] = city_uri
        return True

    def createVenue(self, venueWriting, venueName, venueDescription, Coordinate, hasCity, hasCountry, hasCode,
                    hasCapacity, hostEvent: list):
        if venueWriting in self.venues:
            return False
        venue_uri = URIRef(self.EX[venueWriting])
        self.g.add((venue_uri, RDF.type, self.EX["Venue"]))
        if venueName:
            self.g.add((venue_uri, self.EX["venueName"], Literal(venueName, datatype=XSD.string)))
        if venueDescription:
            self.g.add((venue_uri, self.EX["venueDescription"], Literal(venueDescription, datatype=XSD.string)))
        self.g.add((venue_uri, self.EX["Coordinate"], URIRef(self.EX[Coordinate])))
        self.g.add((venue_uri, self.EX["hasCity"], URIRef(self.EX[hasCity])))
        self.g.add((venue_uri, self.EX["hasCountry"], URIRef(self.EX[hasCountry])))
        if hasCode:
            self.g.add((venue_uri, self.EX["hasCode"], Literal(hasCode, datatype=XSD.string)))
        self.g.add((venue_uri, self.EX["hasCapacity"], Literal(hasCapacity, datatype=XSD.decimal)))
        for event in hostEvent:
            self.g.add((venue_uri, self.EX["hosts"], URIRef(self.EX[event])))
        self.venues[venueWriting] = venue_uri
        return True

    def createOlympics(self, olympicWriting, hostCountry, season, hasOfficialCity, hasTrial, hasVenue, startDate,
                       endDate, olympicHasEvent, hasAnnexCity=None, name=None, description=None):
        if olympicWriting in self.olympics:
            return False
        olympic_uri = URIRef(self.EX[olympicWriting])
        self.g.add((olympic_uri, RDF.type, self.EX["Olympics"]))
        self.g.add((olympic_uri, self.EX["hostCountry"], URIRef(self.EX[hostCountry])))
        self.g.add((olympic_uri, self.EX["season"], URIRef(self.EX[season])))
        self.g.add((olympic_uri, self.EX["hasOfficialCity"], URIRef(self.EX[hasOfficialCity])))
        for trial in hasTrial:
            self.g.add((olympic_uri, self.EX["hasTrial"], URIRef(self.EX[trial])))
        for venue in hasVenue:
            self.g.add((olympic_uri, self.EX["hasVenue"], URIRef(self.EX[venue])))
        self.g.add((olympic_uri, self.EX["startDate"], Literal(startDate, datatype=XSD.date)))
        self.g.add((olympic_uri, self.EX["endDate"], Literal(endDate, datatype=XSD.date)))
        for event in olympicHasEvent:
            self.g.add((olympic_uri, self.EX["olympicHasEvent"], URIRef(self.EX[event])))
        if hasAnnexCity:
            for annex_city in hasAnnexCity:
                self.g.add((olympic_uri, self.EX["hasAnnexCity"], URIRef(self.EX[annex_city])))
        if name:
            self.g.add((olympic_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((olympic_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createDiscipline(self, disciplineWriting, disciplineHasTrial, name=None, description=None):
        if disciplineWriting in self.disciplines:
            return False
        discipline_uri = URIRef(self.EX[disciplineWriting])
        self.g.add((discipline_uri, RDF.type, self.EX["Discipline"]))
        if disciplineHasTrial:
            for trial in disciplineHasTrial:
                self.g.add((discipline_uri, self.EX["disciplineHasTrial"], URIRef(self.EX[trial])))
        if name:
            self.g.add((discipline_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((discipline_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createEvent(self, eventWriting, belongsToTrial, hasDate, eventHasPerformance, belongToOlympics, name=None,
                    description=None):
        if eventWriting in self.olympics:
            return False
        event_uri = URIRef(self.EX[eventWriting])
        self.g.add((event_uri, RDF.type, self.EX["Event"]))
        self.g.add((event_uri, self.EX["belongsToTrial"], URIRef(self.EX[belongsToTrial])))
        self.g.add((event_uri, self.EX["hasDate"], Literal(hasDate, datatype=XSD.dateTime)))
        for performance in eventHasPerformance:
            self.g.add((event_uri, self.EX["eventHasPerformance"], URIRef(self.EX[performance])))
        self.g.add((event_uri, self.EX["belongToOlympics"], URIRef(self.EX[belongToOlympics])))
        if name:
            self.g.add((event_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((event_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createTrial(self, trialWriting, belongsToDiscipline, isTeamTrial, name=None, description=None):
        if trialWriting in self.trial:
            return False
        trial_uri = URIRef(self.EX[trialWriting])
        self.g.add((trial_uri, RDF.type, self.EX["Trial"]))
        self.g.add((trial_uri, self.EX["belongsToDiscipline"], URIRef(self.EX[belongsToDiscipline])))
        self.g.add((trial_uri, self.EX["isTeamTrial"], Literal(isTeamTrial, datatype=XSD.boolean)))
        if name:
            self.g.add((trial_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((trial_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createPerformance(self, performanceWriting, hasResult, rank, hasEvent, playedBy, hasResultUnit,
                          isScheduledAtTime, awarded=None, name=None, description=None):
        if performanceWriting in self.olympics:
            return False
        performance_uri = URIRef(self.EX[performanceWriting])
        self.g.add((performance_uri, RDF.type, self.EX["Performance"]))
        self.g.add((performance_uri, self.EX["hasResult"], Literal(hasResult, datatype=XSD.string)))
        self.g.add((performance_uri, self.EX["rank"], Literal(rank, datatype=XSD.string)))
        self.g.add((performance_uri, self.EX["hasEvent"], URIRef(self.EX[hasEvent])))
        self.g.add((performance_uri, self.EX["playedBy"], URIRef(self.EX[playedBy])))
        self.g.add((performance_uri, self.EX["hasResultUnit"], URIRef(self.EX[hasResultUnit])))
        self.g.add((performance_uri, self.EX["isScheduledAtTime"], Literal(isScheduledAtTime, datatype=XSD.dateTime)))
        if awarded:
            self.g.add((performance_uri, self.EX["awarded"], URIRef(self.EX[awarded])))
        if name:
            self.g.add((performance_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((performance_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createMedal(self, medalWriting, name=None, description=None):
        if medalWriting in self.medals:
            return False
        medal_uri = URIRef(self.EX[medalWriting])
        self.g.add((medal_uri, RDF.type, self.EX["Medal"]))
        if name:
            self.g.add((medal_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((medal_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createWorldRecord(self, recordWriting, recordForTrial, recordHasPerformance, name=None, description=None):
        if recordWriting in self.records:
            return False
        record_uri = URIRef(self.EX[recordWriting])
        self.g.add((record_uri, RDF.type, self.EX["WorldRecord"]))
        self.g.add((record_uri, self.EX["recordForTrial"], URIRef(self.EX[recordForTrial])))
        self.g.add((record_uri, self.EX["recordHasPerformance"], URIRef(self.EX[recordHasPerformance])))
        if name:
            self.g.add((record_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((record_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createOlympicRecord(self, recordWriting, recordForTrial, recordHasPerformance, name=None, description=None):
        if recordWriting in self.records:
            return False
        record_uri = URIRef(self.EX[recordWriting])
        self.g.add((record_uri, RDF.type, self.EX["OlympicRecord"]))
        self.g.add((record_uri, self.EX["recordForTrial"], URIRef(self.EX[recordForTrial])))
        self.g.add((record_uri, self.EX["recordHasPerformance"], URIRef(self.EX[recordHasPerformance])))
        if name:
            self.g.add((record_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((record_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createOlympicCommittee(self, committeeWriting, recordForTrial, recordHasPerformance, name=None,
                               description=None):
        if committeeWriting in self.committees:
            return False
        committee_uri = URIRef(self.EX[committeeWriting])
        self.g.add((committee_uri, RDF.type, self.EX["OlympicCommittee"]))
        self.g.add((committee_uri, self.EX["recordForTrial"], URIRef(self.EX[recordForTrial])))
        self.g.add((committee_uri, self.EX["recordHasPerformance"], URIRef(self.EX[recordHasPerformance])))
        if name:
            self.g.add((committee_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((committee_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createCoordinate(self, coordinateWriting, hasLongitude, hasLatitude, name=None, description=None):
        if coordinateWriting in self.coordinates:
            return
        coordinate_uri = URIRef(self.EX[coordinateWriting])
        self.g.add((coordinate_uri, RDF.type, self.EX["Coordinate"]))
        self.g.add((coordinate_uri, self.EX["hasLongitude"], Literal(hasLongitude, datatype=XSD.decimal)))
        self.g.add((coordinate_uri, self.EX["hasLatitude"], Literal(hasLatitude, datatype=XSD.decimal)))
        if name:
            self.g.add((coordinate_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            self.g.add((coordinate_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

csv2rdf = CSV2RDF("data", "output", "paris.csv", "type_matrix_mappinself.g.json", "type_matrix.ttl", "all")
#csv2rdf.generate_type_matrix_mapping("http://example.org/interactionWith", "http://example.org/")
#csv2rdf.save_type_matrix_mapping()
csv2rdf.create_rdf(namespace, function_generate_rdf)






























