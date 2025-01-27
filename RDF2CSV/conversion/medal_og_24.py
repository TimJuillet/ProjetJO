from utils import \
    transformer_date, \
    convertir_en_rdf_dateTime, \
    obtenir_premier_terme, \
    separer_nom_prenom, \
    normalize_string, \
    capitalize_words, \
    check_and_create_file, \
    write_in_file

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
    olympicsParameters, \
    pathToVenueData


from ConstructRDF import ConstructRDF
from venues_og_24 import generate_discipline_to_venue_dictionary_from_csv


def function_for_medal_og_24(reader, constructorRDF):
    dicionaryDisciplineToVenue = generate_discipline_to_venue_dictionary_from_csv(pathToVenueData)

    olympicsTrial = []
    olympicsVenue = []
    olympicsEvent = []
    disciplineToTrialDict = {}
    disciplineToParametersDict = {}
    globalOperation = ConstructRDF.ADD_OPERATION
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
        medalName = row["Medal_type"].replace(" ", separator)
        medalWritting = obtenir_premier_terme(row["Medal_type"])
        rank = row["Medal_code"]
        performanceWritting = trialName + "_" + athleteName + "_" + transformer_date(date)
        performanceName = row["Medal_type"] + " " + row["Event"] + " " + row["Name"] + " " + transformer_date(date)
        performanceDescription = "Performance of " + row["Name"] + " in " + row["Event"] + " at the " + row["Medal_type"] + " on " + transformer_date(date)
        eventWritting = discplineName + "_" + trialName + "_" + transformer_date(date)
        eventName = capitalize_words(normalize_string(row["Discipline"])) + " " + row["Event"] + " " + transformer_date(date)
        eventDescription = "Event " + row["Event"] + " on " + transformer_date(date)
        eventParticipants =[]
        eventPerformances = [performanceWritting]
        eventHostedBy = []
        if discplineName in dicionaryDisciplineToVenue:
            eventHostedBy = dicionaryDisciplineToVenue[discplineName]

        globalOperation = ConstructRDF.ADD_OPERATION

        constructorRDF.createCountry(globalOperation, countryName, countryName, countryCode, BlankCoordinateWritting, None)


        if discplineName not in disciplineToTrialDict:
            disciplineToTrialDict[discplineName] = [trialName]
            disciplineParameters = {}
            disciplineParameters["name"] = discplineName
            disciplineParameters["description"] = None
            disciplineParameters["globalOperation"] = globalOperation
            disciplineParameters["disciplineWriting"] = discplineName
            disciplineToParametersDict[discplineName] = disciplineParameters
        else:
            disciplineToTrialDict[discplineName].append(trialName)

        constructorRDF.createDiscipline(globalOperation, discplineName, None, discplineName, None)
        success = constructorRDF.createTrial(globalOperation, trialName, discplineName, is_team_event, trialName, trialDescription)
        if success:
            olympicsTrial.append(trialName)

        if is_team_event:
            teamWritting = trialName + countryName + "_team"
            teamName = trialName + " " + row["Country"] + " team"
            teamDescription = "Team of " + row["Country"] + " in " + trialName
            hasMember = []
            constructorRDF.createTeam(globalOperation, teamWritting, teamName, teamDescription, BlankIsDisabled, hasMember, countryName)
        else :
            constructorRDF.createPerson(globalOperation, personWritting, nom, BlankHeight,
                                    BlankWeight, BlankBirthDate, None,
                                    gender, countryName, BlankIsDisabled, prenom, None)
            constructorRDF.createAthlete(globalOperation, athleteName, None, personWritting, BlankIsDisabled, countryName)



        constructorRDF.createMedal(globalOperation, medalWritting, medalName, None)
        constructorRDF.createPerformance(globalOperation, performanceWritting, BlankHasResult,
                                         rank, trialName, athleteName,
                                         BlankHasResultUnit, date, medalWritting,
                                         performanceName, performanceDescription)
        success = constructorRDF.createEvent(globalOperation, eventWritting, trialName,
                                             date, eventPerformances,
                                             olympicsParameters["name"], eventParticipants, eventHostedBy,
                                             eventName, eventDescription)
        if success:
            olympicsEvent.append(eventWritting)

    for disciplineName, trialList in disciplineToTrialDict.items():
        disciplineParameters = disciplineToParametersDict[disciplineName]
        constructorRDF.createDiscipline(disciplineParameters["globalOperation"], disciplineParameters["disciplineWriting"],
                                        trialList, disciplineParameters["name"], disciplineParameters["description"])

    olympicsParameters["hasTrial"] = olympicsTrial
    olympicsParameters["hasVenue"] = olympicsVenue
    olympicsParameters["olympicHasEvent"] = olympicsEvent
    constructorRDF.createOlympics(globalOperation, olympicsParameters["name"],
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