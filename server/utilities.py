import subprocess
import subprocess
import base64, qrcode, datetime

def signer_donnees(nom_prenom, formation):

    # Concaténer les données
    donnees = nom_prenom + formation

    # Appeler OpenSSL pour signer les données
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
        print(openssl_output.decode())
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
    qr.save("./temp/qrcode.png", scale=5)
    print("QR Code enregistré dans le repertoire temp")

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

    

