from rdflib import Namespace

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