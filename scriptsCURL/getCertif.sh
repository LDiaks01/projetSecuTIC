#!/bin/bash
# Message de bienvenue
echo "Bienvenue dans le programme de création de certificats."
# Demander à l'utilisateur d'entrer le nom et le prénom
read -p "Entrez votre nom et prénom : " nom_prenom
read -p "Entrez l'intitulé du certificat : " intitule_certif

# Extraire le nom et le prénom de la variable
nom=$(echo "$nom_prenom" | cut -d' ' -f1)
prenom=$(echo "$nom_prenom" | cut -d' ' -f2-)
echo "Generation en cours.."
# Envoi de la requête POST avec curl
curl -X POST -d "identite=$prenom $nom" -d "intitule_certif=$intitule_certif" --cacert ./authorityCert/certauthority.cert.pem https://localhost:9000/creation --output certificat.png
# Vérification du statut de la requête
if [ $? -ne 0 ]; then
    echo "La requête curl a échoué."
    exit 1
fi

echo "Generation terminée avec succès : Le certificat a été téléchargé dans certificat.png "
