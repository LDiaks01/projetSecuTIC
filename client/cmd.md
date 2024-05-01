#== Commandes pour utiliser le serveur

1 - Dans un terminal,positionnez vous à la RACINE du projet
2 - Créez un dossier nommé temp $mkdir temp
3 - Dans un nouveau terminal, positionnez vous à la racine du projet et lancer le serveur python
$python3 server/server.py

4 - Dans un nouveau terminal, positionnez vous à la racine du projet et lancer le serveur frontal

socat openssl-listen:9000,fork,cert=bundle_server.pem,cafile=certauthority.cert.pem,verify=0 tcp:127.0.0.1:8080

5 - Finalement dans un nouveau terminal, positionnez vous à la racine du projet et réaliser une requete sur le serveur frontal pour créer une attestation par exemple.

curl -v -X POST -d identite=toto -d intitule_certif=SecuTIC --cacert certauthority.cert.pem https://localhost:9000/creation
