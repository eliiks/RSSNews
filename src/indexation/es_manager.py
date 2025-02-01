"""
La classe ElasticSearchManager gère les connexions, insertions et recherches avec l'API Python d'ElasticSearch
"""

from collection.item import Item
from utils.globals import CATEGORIES, ATTRIBUTES
from elasticsearch import Elasticsearch, helpers
import json

class ElasticSearchManager:
    def __init__(self, config_path):
        """
        Crée une instance ElasticSearchManager

        :param index_name: le nom de l'index dans lequel on souhaite insérer/chercher des données
        :type index_name: str
        :param config_path: le chemin vers la configuration du serveur ElasticSearch
        :type config_path: str
        """
        
        self.host = ""
        self.api_key = ""
        self.index_name = ""

        """
        self.user = ""
        self.password = ""
        self.ca_cert = ""
        """

        self.instance = None
        self.is_connected = False
        self.set_config(config_path)
    
    def set_index_name(self, index_name):
        """
        Configure le nom de l'index sur lequel insérer/chercher les données

        :param index_name: le nom de l'index dans lequel on souhaite insérer/chercher des données
        :type index_name: str
        """
        self.index_name = index_name
    
    def set_config(self, config_path):
        """
        Configure les identifiants du serveur sur lequel se connecter à partir d'un fichier JSON
        La syntaxe du fichier JSON est décrite dans le README

        :param config_path: le chemin vers la configuration du serveur ElasticSearch
        :type config_path: str 
        """
        # Lecture et passage en dictionnaire de la configuration JSON
        f = open(config_path)
        config = json.load(f)

        self.host = config["host"]
        self.api_key = config["api_key"]
        self.index_name = config["index_name"]

        """
        self.user = config["user"]
        self.password = config["password"]
        self.ca_cert = config["ca_cert"]
        """

    def connect(self):
        """
        Etablit une connexion avec le serveur ElasticSearch
        """
        if (self.instance is None) or (self.is_connected == False):
            self.instance = Elasticsearch(self.host, api_key=self.api_key)

        if not self.instance.ping():
            raise ValueError("ElasticSearchManager : connexion échouée avec le serveur ElasticSearch\n")
        else:
            self.is_connected = True
    
    def disconnect(self):
        """
        Se déconnecte du serveur ElasticSearch
        """
        self.instance.transport.close()

        if not self.instance.ping(): 
            self.is_connected = False
        else: 
            raise ValueError("ElasticSearchManager : fermeture échouée de la connexion avec le serveur ElasticSearch")
    
    def index(self, item):
        """
        Index un item RSS dans la base de donnée ElasticSearch

        :param item: item RSS à indexer
        :type item: Item 
        """
        # Passage de l'objet Item en objet dict pour respecter le format voulu par l'API Python d'ElasticSearch
        doc = item.to_dictionnary()

        if self.is_connected:
            self.instance.index(index=self.index_name, id=doc["id"], document=doc, refresh=True, timeout=None)
        else:
            print("ElasticSearchManager : connexion non établie avec le serveur ElasticSearch, veuillez utiliser la méthode \"connect\" avant toutes opérations\n")
        
    def search(self, query):
        """
        Effectue une recherche dans la base de donnée ElasticSearch à partir d'une requête fournie

        :param query: Requête à effectuer dans la base de donnée
        :type query: dict
        """
        if self.is_connected:
            result = self.instance.search(index=self.index_name, query=query)

            print("\n---------------------------- RETOUR DE VOTRE RECHERCHE -----------------------------------\n")
            if result.get('hits') is not None and result['hits'].get('hits') is not None:
                docs = result['hits']['hits'][:]
                for i,doc in enumerate(docs):
                    item = Item()
                    print("Item n°", i+1, " / index = " + doc["_index"] + ", score = ", doc["_score"], end="")
                    item.load_from_dictionnary(doc['_source'])
                    print(item)
            else:
                print({})
            print("\n----------------------------   FIN DE VOTRE RECHERCHE  -----------------------------------\n")
        else:
            print("ElasticSearchManager : connexion non établie avec le serveur ElasticSearch, veuillez utiliser la méthode \"connect\" avant toutes opérations\n")

    def get_all_articles(self, lang):
        """
        Retourne tous les articles d'une langue précisée

        :param lang: la langue des articles à chercher
        :type lang: str
        """
        docs = []

        if self.is_connected:
            docs = helpers.scan(self.instance, index=self.index_name, body={"query":{"match": {"lang":lang}}})
        else:
            print("ElasticSearchManager : connexion non établie avec le serveur ElasticSearch, veuillez utiliser la méthode \"connect\" avant toutes opérations\n")
        return docs

    def get_total_articles(self):
        """
        Retourne le nombre total d'éléments de la base ElasticSearch. 
        
        :return : Le nombre d'éléments de la base
        :rtype : int
        """
        count = 0
        
        if self.is_connected:
            count = self.instance.count(index=self.index_name)['count']
        else:
            print("ElasticSearchManager : connexion non établie avec le serveur ElasticSearch, veuillez utiliser la méthode \"connect\" avant toutes opérations\n")
        return count

    def get_count_for_cat(self, cat_name, attribute_name, lang='fr'):
        """
        Retourne le nombre d'éléments pour une catégorie et une langue données. 
            
        :param cat_name: Le nom de la catégorie (ex : sport)
        :type cat_name: str
        :param attribute_name: Le nom de l'attribut sur lequel on effectue la recherche (ex : feed_category)
        :type attribute_name: str
        :param lang: La langue que l'on souhaite (fr ou en). fr est la valeur par défaut
        :type lang: str
        :return : Le nombre d'éléments pour la catégorie et la base choisies
        :rtype : int
        """
        if self.is_connected:
            count = self.instance.count(index=self.index_name, body = {
                                                    "query": {
                                                        "bool": {
                                                            "must": [
                                                                {"match": {attribute_name: cat_name}},
                                                                {"match": {'lang': lang}}
                                                                ]
                                                        }
                                                    }
                                                })['count']
        else:
            print("ElasticSearchManager : connexion non établie avec le serveur ElasticSearch, veuillez utiliser la méthode \"connect\" avant toutes opérations\n")
        return count

    def wrong_language(self):
        """
        Retourne le nombre d'éléments qui n'ont ni la langue 'fr' ni la langue 'en' 
            
        :return : Le nombre d'éléments qui n'ont ni la langue 'fr' ni la langue 'en' 
        :rtype : int
        """
        if self.is_connected:
            count = self.instance.count(index=self.index_name, body = {
                                                    "query": {
                                                        "bool": {
                                                                "must_not" : [ 
                                                                    {"match": {'lang': 'fr'}},
                                                                    {"match": {'lang': 'en'}}
                                                                    ]
                                                                }
                                                        }
                                                    })['count']
        else:
            print("ElasticSearchManager : connexion non établie avec le serveur ElasticSearch, veuillez utiliser la méthode \"connect\" avant toutes opérations\n")
        return count

    def get_stats(self):
        """
        Affiche les informations statistiques de la base : le nombre total d'éléments et le nombre d'éléments par catégorie et langue
        """
        print("---- DEBUT DES STATS DE LA BASE DE DONNEES ----")

        try:
            self.connect()
        except ValueError as v:
            print(v, end="")
            print("---- FIN DES STATS DE LA BASE DE DONNEES ----\n")
            return
        
        accfr = 0
        accen = 0
        for index, cat in enumerate(CATEGORIES):
            count = self.get_count_for_cat(cat, ATTRIBUTES[4], "fr")
            accfr += count
            print(f'CAT_NAME : {cat} | LANG : {"fr"} | COUNT : {count}')

            count = self.get_count_for_cat(cat, ATTRIBUTES[4], "en")
            accen += count
            print(f'CAT_NAME : {cat} | LANG : {"en"} | COUNT : {count}')
        print(f'Total FR : {accfr}')
        print(f'Total EN : {accen}')
        print(f"Total mauvaise langue : ", self.wrong_language())
        print("Total d'éléments dans la base : ", self.get_total_articles())
        self.disconnect()

        print("---- FIN DES STATS DE LA BASE DE DONNEES ----\n")