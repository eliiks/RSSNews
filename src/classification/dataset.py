from utils.globals import CATEGORIES
from stop_words import get_stop_words
import pickle
import snowballstemmer
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

class StemmedCountVectorizer(CountVectorizer):
    """
    Classe fille de CountVectorizer avec une étape intermédiaire de stemmer
    """
    def defineStemmer(self, stemmer):
        self.doc_stemmer = stemmer

    def build_analyzer(self):
        analyzer = super(StemmedCountVectorizer, self).build_analyzer()
        return lambda doc: self.doc_stemmer.stemWords(analyzer(doc))

class Dataset:
    """
    La classe gére les données des articles RSS pour l'entrainement des modèles
    Il gère aussi les vectorisation (entrainement, sauvegarde et chargement)
    """
    def __init__(self):
        """
        Crée une instance Dataset
        """   
        # french data
        self.corpus_fr = []
        self.X_fr = []
        self.y_fr = []
        
        # english data
        self.corpus_en = []
        self.X_en = []
        self.y_en = []

        #stemmer 
        stemmer_fr = snowballstemmer.stemmer("french")
        stemmer_en = snowballstemmer.stemmer("english")

        # vectorizers
        SCV_fr = StemmedCountVectorizer(stop_words=get_stop_words("fr"))
        SCV_fr.defineStemmer(stemmer_fr)
        self.vectorizer_fr = make_pipeline(SCV_fr, TfidfTransformer())

        SCV_en = StemmedCountVectorizer(stop_words=get_stop_words("en"))
        SCV_en.defineStemmer(stemmer_en)
        self.vectorizer_en = make_pipeline(SCV_en, TfidfTransformer())
    
    def fit_transform_from_corpus(self, es_manager):
        """
        Entraine le vectoriseur en français et anglais à partir des articles
        Retourne les données (articles X et labels y) vectorisées par le vectoriseur

        :param es_manager: le manager de l'API ElasticSearch 
        :type es_manager: ElasticSearchManager
        """
        cpt_fr = 0
        cpt_en = 0

        self.X_fr = []
        self.y_fr = []
        self.X_en = []
        self.y_en = []

        try:
            es_manager.connect()
        except ValueError as v:
            print("")
            print(v, end="")
            return
        
        docs_fr = es_manager.get_all_articles("fr")
        docs_en = es_manager.get_all_articles("en")
        for d in docs_fr:
            cpt_fr += 1
            self.corpus_fr.append(d["_source"]["content"])
            self.y_fr.append(CATEGORIES.index(d["_source"]["feed_category"]))
        for d in docs_en:
            cpt_en += 1
            self.corpus_en.append(d["_source"]["content"])
            self.y_en.append(CATEGORIES.index(d["_source"]["feed_category"]))
        es_manager.disconnect()

        print("Nombre de documents français extraits = " + str(cpt_fr))
        print("Nombre de documents anglais extraits = "+ str(cpt_en))
        self.X_fr, self.X_en = self.fit_transform()
        print("Nombre de documents français vectorisés  = " + str(len(self.X_fr)))
        print("Nombre de documents anglais vectorisés = "+ str(len(self.X_en)))

        self.save_vectorization()
    
    def save_vectorization(self):
        """
        Sauvegarde les données vectorisées et les vectoriseurs dans un fichier pickle
        """
        data = {}
        data["vectorizer_fr"] = self.vectorizer_fr
        data["vectorizer_en"] = self.vectorizer_en
        data["X_fr"] = self.X_fr
        data["X_en"] = self.X_en
        data["y_fr"] = self.y_fr
        data["y_en"] = self.y_en

        with open("../config/vectorizations", "wb") as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    def load_vectorization(self):
        """
        Charge les données vectorisées et les vectoriseurs dans un fichier pickle

        :return: les données vectorisées X et leurs labels y pour chaque langue
        :rtype: tuple(list, list)
        """
        shelve_file = open("../config/vectorizations", "rb")
        data = pickle.load(shelve_file)

        if "vectorizer_fr" in data:
            self.vectorizer_fr = data["vectorizer_fr"]
        if "vectorizer_en" in data:
            self.vectorizer_en = data["vectorizer_en"]
        if "X_fr" in data:
            self.X_fr = data["X_fr"]
        if "X_en" in data:
            self.X_en = data["X_en"]
        if "y_fr" in data:
            self.y_fr = data["y_fr"]
        if "y_en" in data:
            self.y_en = data ["y_en"]

        shelve_file.close()
        return self.X_fr, self.X_en, self.y_fr, self.y_en
    
    def fit_transform(self):
        """
        Vectorise le corpus d'articles en français et en anglais en affinant les vectoriseurs

        :return: les données vectorisées des articles français et anglais
        :rtype: tuple(list, list)
        """
        return self.vectorizer_fr.fit_transform(self.corpus_fr).toarray(), self.vectorizer_en.fit_transform(self.corpus_en).toarray()
    
    def transform(self, doc, lang):
        """
        Vectorise un document en français ou en anglais

        :return: le document vectorisé
        :rtype: list
        """
        if lang == "fr":
            return self.vectorizer_fr.transform(doc).toarray()
        elif lang == "en":
            return self.vectorizer_en.transform(doc).toarray()