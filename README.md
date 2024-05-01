# Projet Sécurité des usages TIC

## Dépendances du projet:
Avant d'exécuter ce serveur, veuillez d'abord installer les différentes dépendances via :
```python
pip install -r requirements.txt
```
## Commandes pour utiliser le serveur

1. Dans un terminal, positionnez-vous à la **racine du projet**.

2. Créez un dossier nommé `temp` s'il n'existe pas déjà :
```bash
   mkdir temp
```

** Ensuite on a le choix entre utiliser les scripts déjà préparés ou executer si même les commandes : toujours se positionner à la racine du projet **

___________________________COMMANDES DIRECTES_____________________________
1. - Dans un nouveau terminal, positionnez vous à la racine du projet et lancer le serveur applicatif python
```
    $python3 server/server.py
```
2. - Dans un nouveau terminal, positionnez vous à la racine du projet et lancer le serveur frontal

```bash
    socat openssl-listen:9000,fork,cert=./authorityCert/bundle_server.pem,cafile=./authorityCert/certauthority.cert.pem,verify=0 tcp:127.0.0.1:8080
```

3. - Finalement dans un nouveau terminal, positionnez vous à la racine du projet et réaliser une requete sur le serveur frontal pour créer une attestation par exemple.
```bash
    curl -v -X POST -d identite=Lansana DIAKITE -d intitule_certif=ETH --cacert ./authorityCert/certauthority.cert.pem https://localhost:9000/creation --output certificat.png
```

4. - POur verifier une attestation
```bash
    curl -v -F "image=@certificat.png" --cacert ./authorityCert/certauthority.cert.pem https://localhost:9000/verification
```

________________________________________________________________________________
** Utiliser les scripts fournis **


1. Terminal 1:
Se positionner à la racine du projet et lancer le script:
```bash
    ./client/applicatif_serv.sh
```
2. Terminal 2:
Se positionner à la racine du projet et lancer le script: 
```bash
    ./client/frontal_serv.sh
```

3. Terminal 3: Se positionner à la racine du projet et lancer soit :
```bash
./scriptsCURL/getCertif.sh pour generer un certificat
```
ou

```bash
./scriptsCURL/verifCertif.sh pour vérifier un certificat
```


