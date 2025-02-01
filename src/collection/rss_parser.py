"""
La classe RSSParser requête des flux RSS et collecte des posts
Il classifie chaque nouveau post dans une catégorie
"""

import os
import shutil
from collection.item import Item
from classification.classifiers import Classifiers
import time
import feedparser

class RSSParser:
    def __init__(self, RSS_urls_path):
        """
        Créé une instance de RSS Parser
        Charge la liste des URLS des flux RSS

        :param RSS_urls_path: le chemin du fichier listant les urls RSS et leurs catégories
        :type RSS_urls_path: str
        """
        self.urls = []
        self.classifier = Classifiers()

        self.load_RSS_urls(RSS_urls_path)
        
    def load_RSS_urls(self, RSS_urls_path):
        """
        Charge la liste des URLS des flux RSS

        :param list_RSS_path: le chemin vers le fichier listant les flux RSS
        :type list_RSS_path: str
        """
        lines = []
        with open(RSS_urls_path, "r") as f:
            lines = f.readlines()

        for l in lines:
            flux = l.replace(" ", "").replace("\n","").split(";")
            self.urls.append(flux)
    
    def start_parsing(self, es_manager, limit_per_feed=20):
        """
        Requête les flux RSS et collecte les items RSS

        :param es_manager: le manager de l'API ElasticSearch 
        :type es_manager: ElasticSearchManager
        :param limit_per_feed: la limite d'items RSS par flux source
        :type limit_per_feed: int
        """
        try:
            es_manager.connect()
        except ValueError as v:
            print(v)
            return
        
        try: 
            os.makedirs("../pages")
        except OSError:
            if not os.path.isdir("../pages"):
                raise

        for flux in self.urls:
            flux_url = flux[0]
            flux_category = flux[1]

            data = feedparser.parse(flux_url)
            if data.bozo == False or (hasattr(data, "status") and int(data.status) < 400):
                nb_posts = 0

                for post in data.entries:
                    # Elements obligatoires (non-renseigné = rejeté)
                    if(post.link == "") : continue
                    if(post.title == "") : continue

                    # Collection dans instance Item 
                    item = Item()
                    valide = item.load_from_RSS_post(post, flux_category, flux_url)

                    if valide:
                        # Classification du post
                        predictions = self.classifier.predict(item.content, item.lang)
                        item.set_predictions(predictions)

                        # Affichage post
                        print(item)
                    
                        # Stockage dans ElasticSearch
                        es_manager.index(item)
            
                        nb_posts = nb_posts + 1
                        if nb_posts==limit_per_feed : break
                    time.sleep(3)
            else:
                print("Flux error \n Ignored:", flux[0], " | code error = ", end=" ")
                if hasattr(data, "status") : print(data.status)
                else: print(data.bozo_exception)
        
        try: 
            shutil.rmtree("../pages")
        except OSError:
            if not os.path.isdir("../pages"):
                raise
        
        es_manager.disconnect()