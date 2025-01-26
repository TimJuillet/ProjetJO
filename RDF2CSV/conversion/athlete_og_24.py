from utils import \
    transformer_date, \
    convertir_en_rdf_dateTime, \
    obtenir_premier_terme, \
    separer_nom_prenom, \
    normalize_string, \
    capitalize_words, \
    check_and_create_file, \
    write_in_file, \
    addXDays

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


def function_for_athlete_og_24(reader, constructorRDF):
    globalOperation = ConstructRDF.SET_OPERATION
    for row in reader:
        givenName= capitalize_words(row["Preferred Given Name"].replace(" ", separator))
        familyName= row["Preferred Family Name"].replace(" ", separator).upper()
        if familyName == "" or givenName == "":
            continue
        dateOfBirth = row["Date of Birth"]
        #death = birthday+ 1 day
        dateOfDeath = addXDays(dateOfBirth, 1)
        personWriting = givenName + separator + familyName + "_person"
        if not constructorRDF.checkIfURIExists(personWriting):
            continue
        print(familyName, givenName, dateOfBirth)

        constructorRDF.createPerson(operation = globalOperation,
                                    personWriting = personWriting,
                                    surname = familyName,
                                    personName = givenName,
                                    birthDate = dateOfBirth,
                                    height = None,
                                    weight = None,
                                    deathDate = None,
                                    gender = None,
                                    hasNationality = None,
                                    isDisabled = None,
                                    personDescription = None)
