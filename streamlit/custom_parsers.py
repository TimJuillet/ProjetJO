# custom_parsers.py
from rdflib import Graph
import datetime

class CustomGraph(Graph):
    """Graph personnalisé pour gérer les dates historiques"""
    
    def parse_date(self, value):
        """Parse les dates en gérant les dates négatives et invalides"""
        try:
            if not str(value).startswith('-'):
                return datetime.datetime.strptime(str(value), '%Y-%m-%d').date()
            return str(value)  # Retourne la chaîne pour les dates négatives
        except ValueError:
            return str(value)  # Retourne la chaîne pour les dates invalides
    
    def _loads_date(self, value):
        """Surcharge la méthode de chargement des dates"""
        return self.parse_date(value)