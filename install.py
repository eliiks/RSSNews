import subprocess
import sys
import json

# Installation librairie
print("\nInstallation des librairies en cours...\n")
subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "langdetect"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "textract"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "elasticsearch"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn==1.3.2"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "snowballstemmer"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "stop-words"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "six==1.17.0"])
print("\nInstallation des librairies finie!\n")

# création fichier es_config
host = input("Entrez l'adresse hôte de votre serveur ElasticSearch : ")
api_key = input("Entrez la clé API associée à votre serveur ElasticSearch : ")
index_name = input("Entrez le nom de l'index dans lequel les items RSS seront stockés : ")
config = {
    "host":host,
    "api_key": api_key,
    "index_name":index_name
}
config_json = json.dumps(config, indent=4)
with open("./config/es_config.json", "w") as f:
    f.write(config_json)
print("Fichier de configuration serveur \"es_config.json\" créé! Il est disponible dans le dossier config. Modifiez-le si besoin")