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
    olympicsParameters

from ConstructRDF import ConstructRDF


def function_for_medal_og_24(reader, constructorRDF):
    olympicsTrial = []
    olympicsVenue = []
    olympicsEvent = []
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
        eventWritting = trialName + "_" + transformer_date(date)
        eventName = row["Event"] + " " + transformer_date(date)
        eventDescription = "Event " + row["Event"] + " on " + transformer_date(date)
        eventParticipants =[]
        eventPerformances = [performanceWritting]
        eventHostedBy = []

        globalOperation = ConstructRDF.ADD_OPERATION

        constructorRDF.createCountry(globalOperation, countryName, countryName, countryCode, BlankCoordinateWritting, None)
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
                                    BlankWeight, BlankBirthDate, BlankDeathDate,
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