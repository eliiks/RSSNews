"""
La classe Item contient les informations d'un item provenant d'un flux RSS
"""

import numpy as np
import os, re, datetime
import hashlib, langdetect, urllib, textract, bs4
from urllib.error import URLError, HTTPError
from utils.globals import CATEGORIES

class Item:
    def __init__ (self):
        """
        Crée une instance Item d'un post RSS (vide)
        """
        self.source_page = ""
        self.id = ""
        self.source_feed = ""
        self.title = ""
        self.feed_category = ""
        self.predicted_category = ""
        self.predicted_score = 0.0
        self.article_date = ""
        self.collection_date = ""
        self.doc_type = ""
        self.description = ""
        self.lang = ""
        self.content = ""
    
    def load_from_RSS_post(self, post, category, source_feed):
        """
        Charge une instance Item à partir d'un post RSS

        :param post: L'item RSS collecté
        :type post: FeedParserDict
        :param category: La catégorie de l'article
        :type category: str
        :param source_feed: Le flux source de l'item RSS
        :type source_feed: str
        :return: si l'item est valide ou non
        :rtype: bool:
        """
        self.source_page = post.link
        self.id = self.id_init()
        self.source_feed = source_feed
        self.title = post.title
        self.feed_category = category
        self.article_date = self.date_finder(post)
        self.collection_date = str(datetime.datetime.today())
        self.doc_type = self.type_finder(post)
        self.description = self.description_finder(post)
        self.content = self.extract_content()
        if self.content == "": return False
        self.lang = self.language_finder()
        if self.lang == "": return False
        return True

    def load_from_dictionnary(self, dict):
        """
        Charge une instance Item à partir d'un dictionnaire

        :param dict: l'objet à convertir
        :type dict: dict
        """
        self.source_page = dict["source_page"]
        self.id = dict["id"]
        self.source_feed = dict["source_feed"]
        self.title = dict["title"]
        self.feed_category = dict["feed_category"]
        self.predicted_category = dict["predicted_category"]
        self.predicted_score = dict["predicted_score"]
        self.article_date = dict["article_date"]
        self.collection_date = dict["collection_date"]
        self.doc_type = dict["doc_type"]
        self.description = dict["description"]
        self.lang = dict["lang"]
        self.content = dict["content"]
        
    def id_init(self):
        """
        Génère un id à partir d'un hashage du lien de la page source de l'item
        
        :return: L'id hashé de l'item
        :rtype: str
        """
        cleanUrl = urllib.parse.urlparse(self.source_page)
        return hashlib.md5(((cleanUrl.hostname+cleanUrl.path).lower()).encode()).hexdigest()
        
    def type_finder(self, post):
        """
        Détecte le type d'un document (html, pdf, png, ...)

        :param post: l'item RSS collecté
        :type post: FeedParserDict
        :return: Le type du document
        :rtype: str
        """
        if hasattr(post, "links") and len(post.links) > 0 and hasattr(post.links[0], "type"):
            doc_type=(re.findall("/.*",post.links[0].type)[0])[1:]
        else: doc_type=""
        return doc_type
        
    def date_finder(self, post):
        """
        Récupère la date de l'article. 
        Si elle n'est pas renseigné, la date de collecte est prise en compte

        :param post: L'item RSS collecté
        :type post: FeedParserDict
        :return: La date de l'article, ou la date de collecte si non renseignée
        :rtype: str
        """
        if hasattr(post, "published") and post.published != "": date=post.published
        else: date=str(datetime.datetime.today())
        return date
    
    def language_finder(self):
        """
        Détecte la langue de l'article

        :return: La langue de l'article de l'item ("fr" ou "en" en majeur partie)
        :rtype: str
        """
        if self.description != "": lang = langdetect.detect(self.description)
        elif self.title != "": lang = langdetect.detect(self.title)
        else: lang = ""
        return lang
    
    def description_finder(self, post):
        """
        Récupère la description du post. Si elle n'est pas renseigné, la description est vide.

        :param post: L'item RSS collecté
        :type post: FeedParserDict
        :return: La description de l'article
        :rtype: str
        """
        if hasattr(post, "description") and post.description != "": description=post.description
        elif hasattr(post, "summary") and post.summary != "": description=post.summary
        else: description=""
        cleaner = re.compile("<.*?>")
        cleanDescription = re.sub(cleaner, "", description)
        return cleanDescription
    
    def extract_content(self):
        """
        Extrait le contenu de l'article via la page source renseignée.
        
        :return: Le contenu de la page de l'article
        :rtype: str
        """
        # Téléchargement de la page
        try:
            pageDoc = urllib.request.urlopen(self.source_page)
        except HTTPError as h:
            print("Item http error /", h,"\nIgnored:", self.source_page)
            return ""
        except URLError as u:
            print("Item url error /", u.reason,"\nIgnored:", self.source_page)
            return ""
        except UnicodeEncodeError as u:
            print("Item unicode error /", u.reason,"\nIgnored:", self.source_page)
            return ""
        
        # Extraction contenu et stockage local
        pageContent = pageDoc.read()
    
        pageName = "../pages/"+self.id + "." + self.doc_type
        with open(pageName, 'wb') as f:
            f.write(pageContent)

        # Extraction contenu à partir du fichier local de la page
        pageText = textract.process(pageName, encoding='ascii').decode("utf-8")
        os.remove(pageName)

        # Toilettage contenu extrait
        soup = bs4.BeautifulSoup(pageContent, 'html.parser')
        articleText=""

        # beautifulsoup
        if soup.find("article") is not None : 
            #Si balise article trouvé dans l'HTML page => extraction des p dans cette balise
            for pg in soup.find("article").find_all("p"):
                articleText+=pg.get_text()+"\n\n"
        else:
            #Sinon prendre tous les p avec nbCaractères > 100
            for pg in soup.find_all("p"):
                if len(pg.get_text()) > 100:
                    articleText+=pg.get_text()+"\n\n"

        # textract
        if articleText == "" : 
            #Si contenue extrait encore vide => prendre texte extrait à partir de textract
            articleText += pageText
        return articleText
    
    def set_predictions(self, predictions):
        """
        Analyse le tableau de prédictions et associe la catégorie avec la plus forte probabilité

        :param predictions: la tableau des probabilités de chaque catégorie
        :type predictions: list
        """
        if predictions is not None:
            c = np.argmax(predictions)
            self.predicted_category, self.predicted_score = CATEGORIES[c], predictions[c]

    def to_dictionnary(self): 
        """
        Convertit l'item en format dictionnaire
        :return: Le post RSS en format dictionnaire
        :rtype: dict
        """       
        return  {
            'id': self.id,
            'source_feed': self.source_feed,
            'source_page': self.source_page,
            'title': self.title,
            'feed_category' : self.feed_category,
            'predicted_category' : self.predicted_category,
            'predicted_score': self.predicted_score,
            'article_date': self.article_date,
            'collection_date': self.collection_date,
            'doc_type': self.doc_type,
            'lang': self.lang,
            'description': self.description,
            'content': self.content,
        }

    def __str__(self):
        """
        Imprime les informations de l'item

        :return: les informations d'un item
        :rtype: str
        """
        post = "\n-----------------------------------------\n"
        post += "\nId: " + self.id + "\n"
        post += "\nURL flux source: " + self.source_feed + "\n"
        post += "\nURL page source: " + self.source_page + "\n"
        post += "\nTitre: \"" + self.title + "\"\n"
        post += "\nCatégorie: " + self.feed_category + "\n"
        post += "\nCatégorie prédite: " + self.predicted_category + " | Score proba. = " + str(self.predicted_score) + "\n"
        post += "\nDate: " + self.article_date + "\n"
        post += "\nType: " + self.doc_type + "\n"
        post += "\nLangue: " + self.lang + "\n"
        post += "\nDescription: \n" + self.description + "\n"
        post += "\nContenu: \n" + self.content + "\n"
        post += "\n-----------------------------------------\n"
        return post