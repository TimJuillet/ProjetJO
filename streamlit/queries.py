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
    "Structure de l'ontologie": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?class ?label ?comment ?superClass WHERE {
        ?class a owl:Class .
        OPTIONAL { ?class rdfs:label ?label }
        OPTIONAL { ?class rdfs:comment ?comment }
        OPTIONAL { ?class rdfs:subClassOf ?superClass }
        FILTER(!isBlank(?class))
    }
    ORDER BY ?class
    """,
    
    "Propriétés et contraintes": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?property ?type ?domain ?range ?label ?comment WHERE {
        ?property a ?type .
        FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
        OPTIONAL { ?property rdfs:label ?label }
        OPTIONAL { ?property rdfs:comment ?comment }
        OPTIONAL { ?property rdfs:domain ?domain }
        OPTIONAL { ?property rdfs:range ?range }
    }
    ORDER BY ?property
    """,
    
    "Validation SHACL": """
    PREFIX : <http://example.org/olympics#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    SELECT DISTINCT ?shape ?targetClass ?property ?minCount ?maxCount ?datatype WHERE {
        ?shape a sh:NodeShape ;
              sh:targetClass ?targetClass .
        OPTIONAL {
            ?shape sh:property ?propertyShape .
            ?propertyShape sh:path ?property .
            OPTIONAL { ?propertyShape sh:minCount ?minCount }
            OPTIONAL { ?propertyShape sh:maxCount ?maxCount }
            OPTIONAL { ?propertyShape sh:datatype ?datatype }
        }
    }
    """,
    
    "Hiérarchie des concepts": """
    PREFIX : <http://example.org/olympics#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?concept ?label ?broader ?broaderLabel WHERE {
        ?concept a skos:Concept ;
                skos:prefLabel ?label .
        OPTIONAL {
            ?concept skos:broader ?broader .
            ?broader skos:prefLabel ?broaderLabel
        }
    }
    ORDER BY ?label
    """,
    
    "Statistiques des données": """
    PREFIX : <http://example.org/olympics#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?class (COUNT(?instance) as ?count) WHERE {
        ?class a owl:Class .
        ?instance a ?class .
        FILTER(!isBlank(?class))
    }
    GROUP BY ?class
    ORDER BY DESC(?count)
    """
}