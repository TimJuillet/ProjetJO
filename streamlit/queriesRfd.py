STADES_QUERIES = {
    "Informations complètes des stades": """
    PREFIX : <http://example.org/olympics#>
    SELECT * WHERE {
        SERVICE <http://localhost/service/JO/getInfosStade?name=STADE DE FRANCE> {
            ?x ?y ?z
        }
    }
    """,
    "Événements par stade": """
        PREFIX : <http://example.org/olympics#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?stadium ?event ?discipline ?date ?capacity WHERE {
            # Obtenir les informations du stade depuis le service
            SERVICE <http://localhost/service/JO/getInfosStade?name=STADE DE FRANCE> {
                ?stadeUri ?y ?z .
                {
                    ?stadeUri :name ?stadium ;
                            :hasCapacity ?capacity .
                }
            }
            
            # Combiner avec les données des événements locaux
            ?eventUri a :Event ;
                    :name ?event ;
                    :belongsToDiscipline ?discipline ;
                    :isScheduledAtTime ?date ;
                    :takesPlaceAt ?venueUri .
            ?venueUri :name ?stadium .
            
            FILTER(?stadium = "STADE DE FRANCE")
        }
        ORDER BY ?date
        """
}

EQUIPES_QUERIES = {
   "Toutes les équipes par pays" : """
       PREFIX : <http://example.org/olympics#>
       PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
       SELECT ?team ?name ?country
       WHERE {
       ?team a :Team ;
              :name ?name ;
              :represent ?country.

       BIND(STRAFTER(STR(?country), "#") AS ?country)
       BIND(REPLACE(?name, "%20", " ") AS ?name)
       BIND(REPLACE(?country, "%20", " ") AS ?country)
       }
       ORDER BY DESC(?country)
       """
    ,
    "Tous les pays participants": """
       PREFIX : <http://example.org/olympics#>
       PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
       SELECT DISTINCT ?country
       WHERE {
       ?team a :Team ;
              :represent ?country .
       BIND(STRAFTER(STR(?country), "#") AS ?country)
       
       BIND(REPLACE(?country, "%20", " ") AS ?country)
       }
       ORDER BY DESC(?country)
       """
}

MEDAILLES_QUERIES={
   "Médaillé d'or par discipline": """
       PREFIX : <http://example.org/olympics#>
       
       SELECT ?Athlete_Or_Team ?Discipline ?Trial ?Date WHERE {
       ?performance :awarded :Gold ;
                     :hasEvent ?event ;
                     :playedBy ?Athlete_Or_Team ;
                     :isScheduledAtTime ?Date .
       
       BIND(STRAFTER(STR(?Athlete_Or_Team), "#") AS ?Athlete_Or_Team)
       BIND(REPLACE(?Athlete_Or_Team, "%20", " ") AS ?Athlete_Or_Team)
       
       ?event :name ?Trial ;
       :belongsToDiscipline ?Discipline.
       BIND(REPLACE(?Trial, "%20", " ") AS ?Trial)
       }
       ORDER BY ?Discipline ?Date
       """,
       "Medaille details (type, athlete , event, date..) ": """
        PREFIX : <http://example.org/olympics#>
        SELECT ?athleteName ?surname ?medalType ?country ?discipline ?trail ?date
        WHERE {
            ?performance :awarded ?medal ;
                         :playedBy ?athlete ;
                         :hasEvent ?trail ;
                         :isScheduledAtTime ?date .
            ?athlete :isPersonOf ?person;
            :represent ?country.
            ?trail :belongsToDiscipline ?discipline .
            ?person :name ?athleteName ;
                    :surname ?surname .
            BIND(REPLACE(STRAFTER(STR(?medal), "#"), "%20", " ") AS ?medalType)
            BIND(REPLACE(STRAFTER(STR(?discipline), "#"), "%20", " ") AS ?discipline)
            BIND(REPLACE(STRAFTER(STR(?trail), "#"), "%20", " ") AS ?trail)
        }
        ORDER BY DESC(?date)
    """,

}

ATHLETES_QUERIES={
    "Athletes par pays": """
        PREFIX : <http://example.org/olympics#>
        SELECT ?country ?Name ?surname ?gender ?birthDate
        WHERE {
            ?athlete a :Athlete ;
                     :represent ?country ;
                     :isPersonOf ?person .
            ?person :name ?Name ;
                    :surname ?surname;
                    :gender ?gender;
                    :birthDate ?birthDate.
            BIND(REPLACE(?country, "%20", " ") AS ?country)
        }
        ORDER BY ?country
    """,
    "Athletes par discipline": """
        PREFIX : <http://example.org/olympics#>
        SELECT DISTINCT ?discipline ?athleteName ?surname
        WHERE {
            ?performance :playedBy ?athlete ;
                         :hasEvent ?trial .
            ?trial :belongsToDiscipline ?discipline .
            ?athlete :isPersonOf ?person .
            ?person :name ?athleteName ;
                    :surname ?surname .
       #      BIND(REPLACE(STRAFTER(STR(?discipline), "#"), "%20", " ") AS ?discipline)
        }
        ORDER BY ?discipline
    """,
    "Athletes par medaille": """
        PREFIX : <http://example.org/olympics#>
        SELECT ?athleteName ?surname ?medalType ?country ?discipline ?trail ?date
        WHERE {
            ?performance :awarded ?medal ;
                         :playedBy ?athlete ;
                         :hasEvent ?trail ;
                         :isScheduledAtTime ?date .
            ?athlete :isPersonOf ?person;
            :represent ?country.
            ?trail :belongsToDiscipline ?discipline .
            ?person :name ?athleteName ;
                    :surname ?surname .
            BIND(REPLACE(STRAFTER(STR(?medal), "#"), "%20", " ") AS ?medalType)
            BIND(REPLACE(STRAFTER(STR(?discipline), "#"), "%20", " ") AS ?discipline)
            BIND(REPLACE(STRAFTER(STR(?trail), "#"), "%20", " ") AS ?trail)
        }
        ORDER BY DESC(?date)
    """,
    "Nombre d'athlètes médaillés par pays": """
        PREFIX : <http://example.org/olympics#>
        SELECT ?country (COUNT(DISTINCT ?athlete) AS ?total)
        WHERE {
            ?athlete a :Athlete ;
                     :represent ?country .
            BIND(REPLACE(STRAFTER(STR(?country), "#"), "%20", " ") AS ?country)
        }
        GROUP BY ?country
        ORDER BY DESC(?total)
    """
}

DISCIPLINES_QUERIES={
    "Nombre de femmes et homme par discipline": """
        PREFIX : <http://example.org/olympics#>
        SELECT ?discipline ?gender (COUNT(?athlete) AS ?count)
        WHERE {
            ?athlete a :Athlete ;
                     :isPersonOf ?person .
            ?person :gender ?gender .
            
            ?performance :playedBy ?athlete ;
                         :hasEvent ?trial .
            ?trial :belongsToDiscipline ?discipline .
            BIND(REPLACE(STRAFTER(STR(?discipline), "#"), "%20", " ") AS ?discipline)
        }
        GROUP BY ?discipline
    """,
    
    "Nombre d'athletes par discipline": """
        PREFIX : <http://example.org/olympics#>
        SELECT ?discipline (COUNT(DISTINCT ?athlete) AS ?total)
        WHERE {
            ?performance :playedBy ?athlete ;
                         :hasEvent ?trial .
            ?trial :belongsToDiscipline ?discipline .
            BIND(REPLACE(STRAFTER(STR(?discipline), "#"), "%20", " ") AS ?discipline)
        }
        GROUP BY ?discipline
    """,
    
    "Nombre de medailles par discipline": """
        PREFIX : <http://example.org/olympics#>
        SELECT ?discipline (COUNT(?medal) AS ?totalMedals)
        WHERE {
            ?performance :awarded ?medal ;
                         :hasEvent ?trial .
            ?trial :belongsToDiscipline ?discipline .
            BIND(REPLACE(STRAFTER(STR(?discipline), "#"), "%20", " ") AS ?discipline)
        }
        GROUP BY ?discipline
        ORDER BY DESC(?totalMedals)
    """,
    
    "Pays le plus medaille par discipline": """
        PREFIX : <http://example.org/olympics#>
        SELECT ?discipline ?country (COUNT(?medal) AS ?medals)
        WHERE {
            ?performance :awarded ?medal ;
                         :playedBy ?athlete ;
                         :hasEvent ?trial .
            ?athlete :represent ?country .
            ?trial :belongsToDiscipline ?discipline .
            BIND(REPLACE(STRAFTER(STR(?discipline), "#"), "%20", " ") AS ?discipline)
            BIND(REPLACE(STRAFTER(STR(?country), "#"), "%20", " ") AS ?country)
        }
        GROUP BY ?discipline ?country
        ORDER BY ?discipline ASC(?medals)
    """
}