import csv
import json
import os
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD
import re
from datetime import datetime
from constants import \
    BlankCoordinateLongitude, \
    BlankCoordinateLatitude, \
    BlankCoordinateWritting, \
    BlankCoordinateName, \
    BlankCoordinateDescription, \
    BlankHeight, \
    BlankWeight, \
    BlankBirthDate, \
    BlankDeathDate, \
    BlankIsDisabled, \
    BlankHasResultUnit, \
    BlankHasResult, \
    separator, \
    namespace, \
    olympicsParameters

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

    SET_OPERATION = 'SET'
    ADD_OPERATION = 'ADD'

    def set_operation(self, subject_predicate_object):
        """
        Fonction pour ajouter des triplets avec la méthode set().
        """
        self.g.set(subject_predicate_object)

    def add_operation(self, subject_predicate_object):
        """
        Fonction pour ajouter des triplets avec la méthode add().
        """
        self.g.add(subject_predicate_object)

    def choose_operation(self, operation):
        """
        Retourne une fonction en fonction de l'opération choisie.

        :param operation: 'set' ou 'add' pour déterminer l'opération.
        :return: Fonction qui exécute l'opération choisie (set_operation ou add_operation).
        """
        if operation == self.SET_OPERATION:
            return self.set_operation
        elif operation == self.ADD_OPERATION:
            return self.add_operation
        else:
            raise ValueError("Opération non valide. Utilisez 'set' ou 'add'.")

    def checkIfURIExists(self, name):
        uri = URIRef(self.EX[name])
        if (uri, None, None) in self.g:
            return True
        else:
            return False

    def get_property_values(self, element_name, property_name):
        """
        Récupère les valeurs d'une propriété pour un élément donné, en utilisant RDFLib.

        :param element_name: Le nom de l'élément (URI simplifié, par ex. "EquipeDeFrance").
        :param property_name: Le nom de la propriété (URI simplifié, par ex. "hasMember").
        :return: Liste des noms simplifiés des objets liés par la propriété.
        """
        element_uri = URIRef(self.EX[element_name])
        property_uri = URIRef(self.EX[property_name])

        # Récupérer tous les objets liés par la propriété
        objects = [
            obj
            for _, _, obj in self.g.triples((element_uri, property_uri, None))
        ]

        # Transformer les URIRef en noms simplifiés
        simplified_values = []
        for obj in objects:
            if isinstance(obj, URIRef):  # Si l'objet est un URI
                simplified_values.append(self.g.qname(obj).split(":")[-1])
            else:
                simplified_values.append(str(obj))
        return simplified_values

    def createTeam(self, operation, teamWirtting, teamName, teamDescription, isDisabled, hasMember: list, represent):
        if teamWirtting in self.teams:
            return False
        operation = self.choose_operation(operation)
        team_uri = URIRef(self.EX[teamWirtting])
        self.g.set((team_uri, RDF.type, self.EX["Team"]))
        if teamName:
            operation((team_uri, self.EX["name"], Literal(teamName, datatype=XSD.string)))
        if teamDescription:
            operation((team_uri, self.EX["description"], Literal(teamDescription, datatype=XSD.string)))
        if isDisabled:
            operation((team_uri, self.EX["isDisabled"], Literal(isDisabled, datatype=XSD.boolean)))
        if represent:
            operation((team_uri, self.EX["represent"], URIRef(self.EX[represent])))
        if hasMember:
            for member in hasMember:
                operation((team_uri, self.EX["hasMember"], URIRef(self.EX[member])))
        self.teams[teamWirtting] = team_uri
        return True

    def createPerson(self, operation, personWriting, surname, height, weight, birthDate, deathDate, gender, hasNationality,
                     isDisabled, personName, personDescription):
        if personWriting in self.persons:
            return False
        operation = self.choose_operation(operation)
        person_uri = URIRef(self.EX[personWriting])
        self.g.set((person_uri, RDF.type, self.EX["Person"]))
        if surname:
            operation((person_uri, self.EX["surname"], Literal(surname, datatype=XSD.string)))
        if height:
            operation((person_uri, self.EX["height"], Literal(height, datatype=XSD.decimal)))
        if weight:
            operation((person_uri, self.EX["weight"], Literal(weight, datatype=XSD.decimal)))
        if birthDate:
            operation((person_uri, self.EX["birthDate"], Literal(birthDate, datatype=XSD.date)))
        if deathDate:
            operation((person_uri, self.EX["deathDate"], Literal(deathDate, datatype=XSD.date)))
        if gender:
            operation((person_uri, self.EX["gender"], Literal(gender, datatype=XSD.string)))
        if hasNationality:
            operation((person_uri, self.EX["hasNationality"], URIRef(self.EX[hasNationality])))
        if isDisabled:
            operation((person_uri, self.EX["isDisabled"], Literal(isDisabled, datatype=XSD.boolean)))
        if personName:
            operation((person_uri, self.EX["name"], Literal(personName, datatype=XSD.string)))
        if personDescription:
            operation((person_uri, self.EX["description"], Literal(personDescription, datatype=XSD.string)))

        self.persons[personWriting] = person_uri
        return True

    def createAthlete(self, operation, athleteWriting, isPartOfTeam: list, isPersonOf, isDisabled, represent):
        if athleteWriting in self.athletes:
            return False
        operation = self.choose_operation(operation)
        athlete_uri = URIRef(self.EX[athleteWriting])
        self.g.set((athlete_uri, RDF.type, self.EX["Athlete"]))
        if isDisabled:
            operation((athlete_uri, self.EX["isDisabled"], Literal(isDisabled, datatype=XSD.boolean)))
        if represent:
            operation((athlete_uri, self.EX["represent"], URIRef(self.EX[represent])))
        if isPartOfTeam :
            for team in isPartOfTeam:
                operation((athlete_uri, self.EX["isPartOfTeam"], URIRef(self.EX[team])))
        if isPersonOf:
            operation((athlete_uri, self.EX["isPersonOf"], URIRef(self.EX[isPersonOf])))
        self.athletes[athleteWriting] = athlete_uri
        return True

    def createUnits(self, operation, unitWriting, unitsInScientificDomain, unitName, unitDescription):
        if unitWriting in self.units:
            return False
        operation = self.choose_operation(operation)
        unit_uri = URIRef(self.EX[unitWriting])
        self.g.set((unit_uri, RDF.type, self.EX["Unit"]))
        if unitsInScientificDomain:
            operation((unit_uri, self.EX["unitsInScientificDomain"], Literal(unitsInScientificDomain, datatype=XSD.string)))
        if unitName:
            operation((unit_uri, self.EX["unitName"], Literal(unitName, datatype=XSD.string)))
        if unitDescription:
            operation((unit_uri, self.EX["unitDescription"], Literal(unitDescription, datatype=XSD.string)))
        self.units[unitWriting] = unit_uri
        return True

    def createCountry(self, operation, countryWriting, countryName, countryCode, Coordinate, countryDescription):
        if countryWriting in self.countries:
            return False
        operation = self.choose_operation(operation)
        country_uri = URIRef(self.EX[countryWriting])
        self.g.set((country_uri, RDF.type, self.EX["Country"]))
        if countryName:
            operation((country_uri, self.EX["countryName"], Literal(countryName, datatype=XSD.string)))
        if countryDescription:
            operation((country_uri, self.EX["countryDescription"], Literal(countryDescription, datatype=XSD.string)))
        if countryCode:
            operation((country_uri, self.EX["countryCode"], Literal(countryCode, datatype=XSD.string)))
        if Coordinate:
            operation((country_uri, self.EX["Coordinate"], URIRef(self.EX[Coordinate])))
        self.countries[countryWriting] = country_uri
        return True

    def createCity(self, operation, cityWriting, cityName, cityDescription, cityCode, Coordinate, hasCountry):
        if cityWriting in self.cities:
            return False
        operation = self.choose_operation(operation)
        city_uri = URIRef(self.EX[cityWriting])
        self.g.set((city_uri, RDF.type, self.EX["City"]))
        if cityName:
            operation((city_uri, self.EX["cityName"], Literal(cityName, datatype=XSD.string)))
        if cityDescription:
            operation((city_uri, self.EX["cityDescription"], Literal(cityDescription, datatype=XSD.string)))
        if cityCode:
            operation((city_uri, self.EX["cityCode"], Literal(cityCode, datatype=XSD.string)))
        if Coordinate:
            operation((city_uri, self.EX["Coordinate"], URIRef(self.EX[Coordinate])))
        if hasCountry:
            operation((city_uri, self.EX["hasCountry"], URIRef(self.EX[hasCountry])))
        self.cities[cityWriting] = city_uri
        return True

    def createVenue(self, operation, venueWriting, venueName, venueDescription, Coordinate, hasCity, hasCountry, hasCode,
                    hasCapacity, hostEvent: list):
        if venueWriting in self.venues:
            return False
        operation = self.choose_operation(operation)
        venue_uri = URIRef(self.EX[venueWriting])
        self.g.set((venue_uri, RDF.type, self.EX["Venue"]))
        if venueName:
            operation((venue_uri, self.EX["venueName"], Literal(venueName, datatype=XSD.string)))
        if venueDescription:
            operation((venue_uri, self.EX["venueDescription"], Literal(venueDescription, datatype=XSD.string)))
        if Coordinate:
            operation((venue_uri, self.EX["Coordinate"], URIRef(self.EX[Coordinate])))
        if hasCity:
            operation((venue_uri, self.EX["hasCity"], URIRef(self.EX[hasCity])))
        if hasCountry:
            operation((venue_uri, self.EX["hasCountry"], URIRef(self.EX[hasCountry])))
        if hasCode:
            operation((venue_uri, self.EX["hasCode"], Literal(hasCode, datatype=XSD.string)))
        if hasCapacity:
            operation((venue_uri, self.EX["hasCapacity"], Literal(hasCapacity, datatype=XSD.decimal)))
        if hostEvent:
            for event in hostEvent:
                operation((venue_uri, self.EX["hosts"], URIRef(self.EX[event])))
        self.venues[venueWriting] = venue_uri
        return True

    def createOlympics(self, operation, olympicWriting, hostCountry, season, hasOfficialCity, hasTrial, hasVenue, startDate,
                       endDate, olympicHasEvent, hasAnnexCity=None, name=None, description=None):
        if olympicWriting in self.olympics:
            return False
        operation = self.choose_operation(operation)
        olympic_uri = URIRef(self.EX[olympicWriting])
        self.g.set((olympic_uri, RDF.type, self.EX["Olympics"]))
        if hostCountry:
            operation((olympic_uri, self.EX["hostCountry"], URIRef(self.EX[hostCountry])))
        if season:
            operation((olympic_uri, self.EX["season"], Literal(season, datatype=XSD.string)))
        if hasOfficialCity:
            operation((olympic_uri, self.EX["hasOfficialCity"], URIRef(self.EX[hasOfficialCity])))
        if hasTrial:
            for trial in hasTrial:
                operation((olympic_uri, self.EX["hasTrial"], URIRef(self.EX[trial])))
        if hasVenue:
            for venue in hasVenue:
                operation((olympic_uri, self.EX["hasVenue"], URIRef(self.EX[venue])))
        if startDate:
            operation((olympic_uri, self.EX["startDate"], Literal(startDate, datatype=XSD.date)))
        if endDate:
            operation((olympic_uri, self.EX["endDate"], Literal(endDate, datatype=XSD.date)))
        if olympicHasEvent:
            for event in olympicHasEvent:
                operation((olympic_uri, self.EX["olympicHasEvent"], URIRef(self.EX[event])))
        if hasAnnexCity:
            for annex_city in hasAnnexCity:
                operation((olympic_uri, self.EX["hasAnnexCity"], URIRef(self.EX[annex_city])))
        if name:
            operation((olympic_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((olympic_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createDiscipline(self, operation, disciplineWriting, disciplineHasTrial, name=None, description=None):
        if disciplineWriting in self.disciplines:
            return False
        operation = self.choose_operation(operation)
        discipline_uri = URIRef(self.EX[disciplineWriting])
        self.g.set((discipline_uri, RDF.type, self.EX["Discipline"]))
        if disciplineHasTrial:
            for trial in disciplineHasTrial:
                operation((discipline_uri, self.EX["disciplineHasTrial"], URIRef(self.EX[trial])))
        if name:
            operation((discipline_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((discipline_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createEvent(self, operation, eventWriting, belongsToTrial, hasDate,
                    eventHasPerformance, belongToOlympics, hasParticipant : list,
                    hostedBy : list,
                    name=None, description=None):
        if eventWriting in self.olympics:
            return False
        operation = self.choose_operation(operation)
        event_uri = URIRef(self.EX[eventWriting])
        self.g.set((event_uri, RDF.type, self.EX["Event"]))
        if belongsToTrial:
            operation((event_uri, self.EX["belongsToTrial"], URIRef(self.EX[belongsToTrial])))
        if hasDate:
            operation((event_uri, self.EX["hasDate"], Literal(hasDate, datatype=XSD.dateTime)))
        if eventHasPerformance:
            for performance in eventHasPerformance:
                operation((event_uri, self.EX["eventHasPerformance"], URIRef(self.EX[performance])))
        if belongToOlympics:
            for participant in hasParticipant:
                operation((event_uri, self.EX["hasParticipant"], URIRef(self.EX[participant])))
        if hostedBy:
            for venue in hostedBy:
                operation((event_uri, self.EX["hostedBy"], URIRef(self.EX[venue])))
        if belongToOlympics:
            operation((event_uri, self.EX["belongToOlympics"], URIRef(self.EX[belongToOlympics])))
        if name:
            operation((event_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((event_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createTrial(self, operation, trialWriting, belongsToDiscipline, isTeamTrial, name=None, description=None):
        if trialWriting in self.trial:
            return False
        operation = self.choose_operation(operation)
        trial_uri = URIRef(self.EX[trialWriting])
        self.g.set((trial_uri, RDF.type, self.EX["Trial"]))
        if belongsToDiscipline:
            operation((trial_uri, self.EX["belongsToDiscipline"], URIRef(self.EX[belongsToDiscipline])))
        if isTeamTrial:
            operation((trial_uri, self.EX["isTeamTrial"], Literal(isTeamTrial, datatype=XSD.boolean)))
        if name:
            operation((trial_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((trial_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createPerformance(self, operation, performanceWriting, hasResult, rank, hasEvent, playedBy, hasResultUnit,
                          isScheduledAtTime, awarded=None, name=None, description=None):
        if performanceWriting in self.olympics:
            return False
        operation = self.choose_operation(operation)
        performance_uri = URIRef(self.EX[performanceWriting])
        self.g.set((performance_uri, RDF.type, self.EX["Performance"]))
        if hasResult:
            operation((performance_uri, self.EX["hasResult"], Literal(hasResult, datatype=XSD.string)))
        if rank:
            operation((performance_uri, self.EX["rank"], Literal(rank, datatype=XSD.string)))
        if hasEvent:
            operation((performance_uri, self.EX["hasEvent"], URIRef(self.EX[hasEvent])))
        if playedBy:
            operation((performance_uri, self.EX["playedBy"], URIRef(self.EX[playedBy])))
        if hasResultUnit:
            operation((performance_uri, self.EX["hasResultUnit"], URIRef(self.EX[hasResultUnit])))
        if isScheduledAtTime:
            operation((performance_uri, self.EX["isScheduledAtTime"], Literal(isScheduledAtTime, datatype=XSD.dateTime)))
        if awarded:
            operation((performance_uri, self.EX["awarded"], URIRef(self.EX[awarded])))
        if name:
            operation((performance_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((performance_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createMedal(self, operation, medalWriting, name=None, description=None):
        if medalWriting in self.medals:
            return False
        operation = self.choose_operation(operation)
        medal_uri = URIRef(self.EX[medalWriting])
        self.g.set((medal_uri, RDF.type, self.EX["Medal"]))
        if name:
            operation((medal_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((medal_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createWorldRecord(self, operation, recordWriting, recordForTrial, recordHasPerformance, name=None, description=None):
        if recordWriting in self.records:
            return False
        operation = self.choose_operation(operation)
        record_uri = URIRef(self.EX[recordWriting])
        self.g.set((record_uri, RDF.type, self.EX["WorldRecord"]))
        if recordForTrial:
            operation((record_uri, self.EX["recordForTrial"], URIRef(self.EX[recordForTrial])))
        if recordHasPerformance:
            operation((record_uri, self.EX["recordHasPerformance"], URIRef(self.EX[recordHasPerformance])))
        if name:
            operation((record_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((record_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createOlympicRecord(self, operation, recordWriting, recordForTrial, recordHasPerformance, name=None, description=None):
        if recordWriting in self.records:
            return False
        operation = self.choose_operation(operation)
        record_uri = URIRef(self.EX[recordWriting])
        self.g.set((record_uri, RDF.type, self.EX["OlympicRecord"]))
        if recordForTrial:
            operation((record_uri, self.EX["recordForTrial"], URIRef(self.EX[recordForTrial])))
        if recordHasPerformance:
            operation((record_uri, self.EX["recordHasPerformance"], URIRef(self.EX[recordHasPerformance])))
        if name:
            operation((record_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((record_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createOlympicCommittee(self, operation, committeeWriting, recordForTrial, recordHasPerformance, name=None,
                               description=None):
        if committeeWriting in self.committees:
            return False
        operation = self.choose_operation(operation)
        committee_uri = URIRef(self.EX[committeeWriting])
        self.g.set((committee_uri, RDF.type, self.EX["OlympicCommittee"]))
        if recordForTrial:
            operation((committee_uri, self.EX["recordForTrial"], URIRef(self.EX[recordForTrial])))
        if recordHasPerformance:
            operation((committee_uri, self.EX["recordHasPerformance"], URIRef(self.EX[recordHasPerformance])))
        if name:
            operation((committee_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((committee_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True

    def createCoordinate(self, operation, coordinateWriting, hasLongitude, hasLatitude, name=None, description=None):
        if coordinateWriting in self.coordinates:
            return
        operation = self.choose_operation(operation)
        coordinate_uri = URIRef(self.EX[coordinateWriting])
        self.g.set((coordinate_uri, RDF.type, self.EX["Coordinate"]))
        if hasLongitude:
            operation((coordinate_uri, self.EX["hasLongitude"], Literal(hasLongitude, datatype=XSD.decimal)))
        if hasLatitude:
            operation((coordinate_uri, self.EX["hasLatitude"], Literal(hasLatitude, datatype=XSD.decimal)))
        if name:
            operation((coordinate_uri, self.EX["name"], Literal(name, datatype=XSD.string)))
        if description:
            operation((coordinate_uri, self.EX["description"], Literal(description, datatype=XSD.string)))
        return True