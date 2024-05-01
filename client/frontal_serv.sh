#!/bin/bash

# Serveur frontal : le client ne verra pas le serveur applicatif situé sur le port 8080
# Le serveur frontal est un serveur HTTPS qui va recevoir les requêtes du client et les rediriger vers le serveur applicatif
echo "Lancement du serveur frontal..."
socat openssl-listen:9000,fork,cert=./authorityCert/bundle_server.pem,cafile=./authorityCert/certauthority.cert.pem,verify=0 tcp:127.0.0.1:8080

#Se positionner à la racine du projet et lancer le script: ./client/frontal_serv.sh