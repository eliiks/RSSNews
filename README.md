# RSSNews
Auteurs : Louis-Xavier Godet & Sylvain Buche

## Principe
Notre programme permet de collecter, d'indexer et de classifier des items RSS en provenance d'une multitude de sources francophones et anglophones. 
Ces items sont des articles de presse appartenant aux catégories suivantes : art, economie, politique, santé, science et sport.

## Pré-requis
+ Python 3
+ pip avec une version inférieure à 24.1
+ Un serveur local ou distant ElasticSearch avec une clé d'API

## Installation
La librairie [textract](https://github.com/deanmalmgren/textract) nécessite que le logiciel "pip" possède une version inférieure à 24.1.
Si ce n'est pas le cas, notez la version actuelle de "pip" et lancez cette commande : `python -m pip install --upgrade pip<24.1`
\
\
Votre logiciel pip est désormais avec une version inférieure à 24.1., vous pouvez installer les paquets nécessaires au fonctionnement de **RSSNews** avec la commande suivante : `python install.py`
\
\
Pour l'accès à votre propre serveur ElasticSearch, le programme d'installation va vous demander vos informations de connexion :
+ "host" : l'adresse du serveur ElasticSearch
+ "api_key" : la clé API associée à ce serveur
+ "index_name" : le nom de l'index dans lequel seront stockés les données

**RSSNews** est prêt à être lancé !\
N'oubliez pas de remettre à jour votre logiciel pip si besoin après la réussite de l'installation : `python -m pip install --upgrade pip[==VERSION_SOUHAITEE]`

## Exécution
Pour exécuter le programme, placez-vous tout d'abord dans le répertoire src avec un terminal.
Utilisez ensuite la commande `python main.py`. N'oubliez pas de lancer votre serveur ElasticSearch.

## Utilisation
Le programme va régulièrement vous demander de choisir parmis plusieurs options.
Il faudra saisir le chiffre correspondant à l'option de votre choix pour y accéder.

L'arborescence des choix est la suivante:
1. **Collecter des items RSS** : Démarre la collecte de posts RSS à partir de flux sources
	
2. **Effectuer une recherche** : Lance la saisie d'une recherche. Il faut saisir tout d'abord la catégorie voulue et ensuite rentrer la requête.
	
3. **Gérer la classification** : Lance un sous-menu pour gérer le composant classification.
\
	3.1 **Effectuer les cross-validate de chaque modèle testé** :
  Calcule les cross-validate de plusieurs modèles et affiche les meilleurs hyper-paramètres de chacun des modèles
	
	3.2 **Afficher les métriques de chaque modèle entrainé avec les meilleurs hyper-paramètres** :
	Calcule et affiche les métriques de chaque modèle avec les meilleurs combinaisons d'hyper-paramètres 
	Permet de comparer et de trouver le classifieur le plus adapté à la classification d'items RSS
	
	3.3 **Afficher la configuration des classifieurs des articles** :
	Affiche en détail les classifieurs qui ont été choisis pour classifier les items RSS.
	Plus précisement, les noms des modèles et les hyper-paramètres sont affichés.
		
	3.4 **Refaire la vectorisation des données** :
	Recalcule les vecteurs à partir des articles collectés.
	ATTENTION: Cela supprime les données précédentes. Assurez-vous qu'il y a assez de données sur votre serveur ElasticSearch.
		
	3.5 **Refaire l'entrainement des modèles** :
	Réentraîne les classifieurs choisis avec les données vectorielles sauvegardées lors de la vectorisation.
	
	3.6 : **Retour au menu principal**

5. **Afficher les statistiques de la base de données**

6. **Quitter l'application**

## Détails techniques
### Collecte d'items RSS
Le programme peut tout d'abord collecter des items RSS à partir de flux sources (la liste est renseignée dans le fichier « liste_RSS.txt » dans le dossier « config »). 
\
\
La collecte est gérée par la classe « RSSParser » qui, grâce à la librairie
« feedparser », va requêter les flux RSS et obtenir des posts pour chacun d’entre eux.
Un item RSS est représenté par la classe « Item ». Cette classe possède des attributs
tels que le titre, la description, la langue ou encore la date de l’article. Ces attributs sont
complétés à partir du post XML envoyé par le flux RSS. La classe « Item » stocke aussi le
contenu de l’article, téléchargé et lu par la librairie « urllib » et nettoyé grâce à la librairie
« BeautifulSoup ». Certains attributs doivent être obligatoirement renseignés et valides,
notamment le lien vers la publication, la langue qui doit être française ou anglaise, le contenu
qui ne doit pas être vide, etc.

### Indexation d'items RSS
La deuxième fonctionnalité importante de l’application est l’indexation d’items RSS. Lors
de la collecte, si un item RSS est valide, le programme va le stocker/l’indexer sous forme de
dictionnaire dans une base de données ElasticSearch. C’est la classe « ElasticSearchManager »
qui gère les connexions, les insertions et recherches grâce à l’API Python d’ElasticSearch.
Lors de l’exécution de l’application, il est possible de retrouver les items RSS indexés
précédemment : il suffit de taper « 2 » dans le menu principal et de suivre les instructions. Il
faut tout d’abord entrer le nom de la catégorie dans laquelle on souhaite effectuer une
recherche, et ensuite une chaîne de caractère qui précise la requête.

### Classification d'articles
Enfin, la dernière fonctionnalité principale de **RSSNews** est la classification d’articles.
C’est le rôle de la classe « Classifiers » qui prédira les probabilités des catégories selon le
contenu d’un nouvel article collecté.
\
\
Cette classe possède deux modèles de vectorisations, un pour chaque langue. Ils sont
chargés à partir du fichier « vectorizations » dans le dossier « config ». Ils ont été entraînés
grâce à la classe « Dataset » qui gère notamment l’entraînement de vectorisation de texte
d’articles. Il est possible, avec cette classe, de créer une vectorisation des données à partir de
tous les articles français et anglais grâce à la fonction « fit_transform_from_corpus ». Les
données des articles sous forme de vecteurs et les modèles de vectorisations sont alors
sauvegardés dans le fichier « vectorizations ». Cela permet d’éviter de recalculer à chaque fois
ces données et de les charger directement pour les réutiliser.
\
\
La classe “Classifiers” possède également deux modèles de classification, un pour
chaque langue. Ces modèles sont chargés à partir du fichier « classifiers » dans le dossier
« config ». Grâce aux fonctions du fichier « evaluation.py », les configurations de ces
classifieurs ont été trouvées à la suite de cross validate imbriqués, de calculs de métriques
numériques et graphiques. Ces résultats sont visibles dans le dossier « metrics ».
\
\
Après une comparaison des modèles testés et des hyper-paramètres, nous avons
choisi un Random Forest pour le modèle français, mais aussi pour le modèle anglais. Ces
modèles ont été ensuite entraînés et sauvegardés dans le fichier « classifiers ». La fonction
« predict » de la classe Classifiers retourne le tableau de probabilités de chaque catégorie
selon le contenu d’un article. Ce tableau sera ensuite analysé par la classe Item qui regardera
la probabilité la plus haute et associera la catégorie de cette probabilité au nouvel article
collecté.

## Évolutions possibles
L'affichage se fait uniquement via la console, rendant la lecture des actualités peu confortable.
Une application web pourrait permettre d'afficher les actualités collectées sur une interface visuelle agréable, 
en s'appuyant sur un serveur Python chargé d'exécuter les fonctionnalités de **RSSNews**.
\
\
De plus, les textes extraits des pages HTML de certains flux RSS peuvent contenir du code JavaScript ou d'autres éléments indésirables.
Un traitement plus poussé du texte permettrait d'éliminer ces informations superflues.

## Codes externes utilisés
[feedparser](https://github.com/kurtmckee/feedparser)\
[hashlib](https://github.com/python/cpython/blob/3.12/Lib/hashlib.py)\
[langdetect](https://github.com/Mimino666/langdetect)\
[urllib](https://github.com/python/cpython/tree/3.12/Lib/urllib/)\
[textract](https://github.com/deanmalmgren/textract)\
[beautifulsoup](https://git.launchpad.net/beautifulsoup/tree/)\
[elasticsearch-py](https://github.com/elastic/elasticsearch-py)\
[scikit-learn](https://github.com/scikit-learn/scikit-learn)\
[snowballstemmer](https://github.com/snowballstem/snowball)\
[stop-words](https://github.com/Alir3z4/python-stop-words)



