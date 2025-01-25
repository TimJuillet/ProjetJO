PRESET_QUERIES = {
    "Liste des stades": """
    PREFIX : <http://example.org/olympics#>
    
    SELECT ?venue ?name ?capacity WHERE {
        ?venue a :Venue ;
               :name ?name ;
               :hasCapacity ?capacity .
    }
    ORDER BY ?name
    """,
    
    "Stades par capacité": """
    PREFIX : <http://example.org/olympics#>
    
    SELECT ?name ?capacity ?description WHERE {
        ?venue a :Venue ;
               :name ?name ;
               :description ?description ;
               :hasCapacity ?capacity .
    }
    ORDER BY DESC(?capacity)
    """,
    
    "Coordonnées des stades": """
    PREFIX : <http://example.org/olympics#>
    
    SELECT ?name ?lat ?lon WHERE {
        ?venue a :Venue ;
               :name ?name ;
               :hasCoordinate ?coord .
        ?coord :hasLatitude ?lat ;
               :hasLongitude ?lon .
    }
    """,
    
    "Informations complètes des stades": """
    PREFIX : <http://example.org/olympics#>
    
    SELECT ?name ?description ?capacity ?lat ?lon WHERE {
        ?venue a :Venue ;
               :name ?name ;
               :description ?description ;
               :hasCapacity ?capacity ;
               :hasCoordinate ?coord .
        ?coord :hasLatitude ?lat ;
               :hasLongitude ?lon .
    }
    """
}