PRESET_QUERIES = {
    "Liste des stades": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?venue ?name ?capacity WHERE {
        ?venue rdf:type :Venue ;
            :name ?name ;
            :hasCapacity ?capacity .
    }
    ORDER BY ?name
    """,
    
    "Stades par capacité": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?name ?capacity ?description WHERE {
        ?venue rdf:type :Venue ;
            :name ?name ;
            :description ?description ;
            :hasCapacity ?capacity .
    }
    ORDER BY DESC(?capacity)
    """,
    
    "Coordonnées des stades": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?name ?lat ?lon WHERE {
        ?venue rdf:type :Venue ;
            :name ?name ;
            :hasCoordinate ?coord .
        ?coord :hasLatitude ?lat ;
               :hasLongitude ?lon .
    }
    """,
    
    "Informations complètes des stades": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?name ?description ?capacity ?lat ?lon WHERE {
        ?venue rdf:type :Venue ;
            :name ?name ;
            :description ?description ;
            :hasCapacity ?capacity ;
            :hasCoordinate ?coord .
        ?coord :hasLatitude ?lat ;
               :hasLongitude ?lon .
    }
    """,
    
    "Service Stade de France": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT * WHERE {
        SERVICE <http://localhost/service/JO/getInfosStade?name=STADE DE FRANCE> {
            ?x ?y ?z
        }
    }
    """,
    
    "Visualisation des relations": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    CONSTRUCT {
        ?s ?p ?o
    }
    WHERE {
        ?s ?p ?o .
        FILTER(?s != owl:Class)
        FILTER(!isBlank(?s))
        FILTER(!isBlank(?o))
    }
    LIMIT 1000
    """,
        "TEST": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT * WHERE {
       ?x ?y ?z .
    }
    """,
}