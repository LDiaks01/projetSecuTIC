import subprocess
import subprocess
import base64

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
