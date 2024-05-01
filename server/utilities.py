import subprocess
import subprocess
import base64, qrcode, datetime, stegano, zbarlight
from PIL import Image, UnidentifiedImageError

def signer_donnees(nom_prenom, formation):

    # Concaténer les données
    donnees = nom_prenom + "_" +formation

    # Appeler OpenSSL pour signer les données
    # openssl dgst -sha256 -sign certauthority.key.pem -out signature.bin infos.txt
    openssl_command = [
        'openssl', 'dgst', '-sha256', '-sign', './authorityCert/certauthority.key.pem'
    ]
    openssl_process = subprocess.Popen(openssl_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    signature, openssl_error = openssl_process.communicate(input=donnees.encode())

    # Vérifier s'il y a eu une erreur
    if openssl_error:
        print("Erreur OpenSSL :", openssl_error.decode())
        return None

    # Retourner la signature encodée en base64 (ASCII)
    return signature

# public_key_file: chemin du fichier de clé publique de Certifplus
# signature_file: chemin du fichier de signature (données du qrcode)
# data_file: chemin du fichier de données (nom_prenom_formation)
def verifier_signature(public_key_file, signature_file, data_file):
    try:
        # Commande openssl pour vérifier la signature
        openssl_cmd = [
            'openssl',
            'dgst',
            '-sha256',
            '-verify', public_key_file,
            '-signature', signature_file,
            data_file
        ]
        openssl_process = subprocess.Popen(openssl_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        openssl_output, openssl_error = openssl_process.communicate()
        #print(openssl_output.decode())
        if openssl_error:
            print("Erreur OpenSSL :", openssl_error.decode())
            return False
    
        # Vérifier si la signature est valide
        return openssl_output == b'Verified OK\n'

    except subprocess.CalledProcessError as e:
        print("Erreur lors de la vérification de la signature avec OpenSSL:", e)
        return False

def qrcode_maker(b64_signature):
    #generation du qr code contenant la signature
    qr = qrcode.make(b64_signature)
    qr.save("./temp/qrcode.png", scale=2)
    print("QR Code géneré et enregistré dans le repertoire temp")


# Fonction pour générer un timestamp à partir d'un serveur TSA
def get_timestamp_from_tsa():

    time = datetime.datetime.now()
    try:
        time_file = open('./temp/time.txt', 'w')
        time_file.write(str(time))
        time_file.close()

        #generer le timestamp request
        subprocess.run(['openssl', 'ts', '-query', '-data', './temp/time.txt', '-no_nonce', '-sha512',  '-out',  './temp/timestamp.tsq'])
        #envoyer la requete au serveur TSA
        #getCert= ['curl', '-H', 'Content-Type: application/timestamp-query', '--data-binary', '@./temp/timestamp.tsq', 'https://freetsa.org/tsr', '>', './temp/timestamp.tsr']
        getCert= ['curl','-H','Content-Type: application/timestamp-query','--data-binary','@./temp/timestamp.tsq','https://freetsa.org/tsr','-o','./temp/timestamp.tsr']
        subprocess.run(getCert)

    except Exception as e:
        print("Erreur lors de la génération du timestamp request:", e)
    
    print("Timestamp généré et enregistré dans le repertoire temp")


def build_hidden_content(data_etudiant, timestamp_response, timestamp_query):
    # Lire les fichiers
    contenu_concatene = ''
    with open(data_etudiant, 'r') as file:
        data = file.read()
        # on fait le bourrage
        if len(data) < 64:
            data = '*' * (64 - len(data)) + data

        contenu_concatene += data + '|'
    
    with open(timestamp_response, 'rb') as file:
        tsr = file.read()
        tsr = base64.b64encode(tsr)
        tsr = tsr.decode('utf-8')
        contenu_concatene += tsr + '|'
    
    with open(timestamp_query, 'rb') as file:
        tsq = file.read()
        tsq = base64.b64encode(tsq)
        tsq = tsq.decode('utf-8')
        contenu_concatene += tsq
    #print(contenu_concatene)
    print(len(contenu_concatene))
    return contenu_concatene

def retrieve_from_hidden_contents(data):
    # Lire les fichiers
    data = data.split('|')
    if len(data) != 3:
        return None
    
    #eliminer les caracteres de bourrage
    infosEtu = data[0].replace('*', '')
    #save infosEtu to file
    with open('./temp/infos_retrieved.txt', 'w') as file:
        file.write(infosEtu)

    tsr_data = bytes(data[1],"utf-8")
    tsr_data = base64.b64decode(tsr_data)
    #save tsr_data to file
    with open('./temp/timestamp_retrieved.tsr', 'wb') as file:
        file.write(tsr_data)

    tsq_data = bytes(data[2],"utf-8")
    tsq_data = base64.b64decode(tsq_data)
    #save tsq_data to file
    with open('./temp/timestamp_retrieved.tsq', 'wb') as file:
        file.write(tsq_data)

    #print(len(data))
    #print("Voici les données cachées dans l'image :")
    #print("Informations de l'étudiant :", infosEtu)
    #print("Timestamp Response :", tsr_data)
    #print("Timestamp Query :", tsq_data)
    
    return (infosEtu, tsr_data, tsq_data)

def build_certificate(nom_prenom, formation, data_to_hide):
    #chemin du label à générer
    labelAttestationPath = "./temp/label.png"
    fondAttestationPath = "./assets/fond_attestation.png"
    combinaisonPath = "./temp/combinaison.png"
    qrcodePath = "./temp/qrcode.png"
    attestationPath = "./temp/attestation.png"
    finalAttestationPath = "./temp/attestation_final.png"

    #Génération du texte à 
    texte_ligne = formation+" \ndélivré\nà\n" + nom_prenom
    #Generation du label au format png
    subprocess.run("convert -size 1000x600 -gravity center -pointsize 56 label:" + "\""+ texte_ligne + "\"" +" -transparent white " +labelAttestationPath,shell=True)
    #Redimensionnement avec ImageMagick
    subprocess.run("mogrify -resize 1000x600 "+labelAttestationPath,shell=True)

    #Combinaison des images en l'image finale avec ImageMagick
    subprocess.run("composite -gravity center "+labelAttestationPath+" " + fondAttestationPath +" " +combinaisonPath,shell=True)

    #Ajout du QR Code dans l'image finale
    #on resize le qrcode 210x210
    subprocess.run("mogrify -resize 210x210 "+qrcodePath,shell=True)
    subprocess.run("composite -geometry +1418+934 "+qrcodePath+" "+combinaisonPath+" "+attestationPath, shell=True)

    imageAttestation = Image.open(attestationPath)
    #cacher les données dans l'image
    stegano.cacher(imageAttestation, data_to_hide)
    #sauvegarder l'image
    imageAttestation.save(finalAttestationPath)
    print("Attestation générée avec succès")

    #renvoyer l'attestation, pas le chemin
    with open(finalAttestationPath, 'rb') as file:
        return file.read()

# Fonction pour extraire les données cachées dans une image
# la taille est la taille du message caché, fixe de 2034
def extract_hidden_data(image_path, taille=2034):
    image = Image.open(image_path)
    return stegano.recuperer(image, taille)

# Fonction pour créer un répertoire temporaire
def make_temp_dir():
    # Créer le répertoire temporaire s'il ne existe pas
    subprocess.run("mkdir ./temp", shell=True)

# Fonction pour vider les fichiers temporaires
def clear_temp_files():
    # Supprimer les fichiers temporaires
    subprocess.run("rm -f ./temp/*", shell=True)
    
    
# Fonction pour recuperer le qrcode à partir de l'image
def retrieve_qrcode(image_path):
    image = Image.open(image_path)
    qrImage = image.crop((1418,934,1418+210,934+210))
    data = zbarlight.scan_codes(['qrcode'], qrImage)
    #b64 decode from data
    #print(base64.b64decode(data[0]))
    return base64.b64decode(data[0])
    

# Fonction pour verifier le timestamp
def verify_timestamp(tsaCAfile, tsaCRTfile, tsr_file, tsq_file):
    # Avec cette commande: openssl ts -verify -in file.tsr -queryfile file.tsq -CAfile cacert.pem -untrusted tsa.crt
    try:
        # Commande openssl pour vérifier la signature
        openssl_cmd = ['openssl', 'ts', '-verify', '-in', tsr_file, '-queryfile', tsq_file, '-CAfile', tsaCAfile, '-untrusted', tsaCRTfile]
        openssl_process = subprocess.Popen(openssl_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        openssl_output, openssl_error = openssl_process.communicate()

        #print(openssl_output.decode())
        if openssl_error:
            # Ignorer le message "Using configuration from /usr/lib/ssl/openssl.cnf"
            if b"Using configuration from /usr/lib/ssl/openssl.cnf" not in openssl_error:
                # Afficher d'autres erreurs éventuelles
                print("Erreur OpenSSL :", openssl_error.decode())
                return False
    
        # Vérifier si la signature est valide
        return b'Verification: OK' in openssl_output
    except subprocess.CalledProcessError as e:
        print("Erreur lors de la vérification de la signature avec OpenSSL:", e)
        return False

