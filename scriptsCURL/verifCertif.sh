#!/bin/bash

# Message de bienvenue
echo "Bienvenue dans le programme de vérification de certificats."

# Demander à l'utilisateur de spécifier le chemin vers le certificat
read -p "Entrez le chemin vers le certificat à vérifier : " certificat_path

#verifier si le fichier existe

if [ ! -f $certificat_path ]; then
    echo "Le fichier spécifié n'existe pas."
    exit 1
fi

# Envoi de la requête POST pour la vérification du certificat avec curl et affichage de la réponse
echo "Envoi de la requête de vérification du certificat... En attente de la réponse du serveur."
response=$(curl -v -F "image=@$certificat_path" http://localhost:8080/verification 2>&1)

# Affichage de la réponse de la requête curl
echo "$response"
