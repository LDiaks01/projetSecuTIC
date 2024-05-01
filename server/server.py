#!/usr/bin/python3
from bottle import route, run, template, request, response, abort
import subprocess, base64, qrcode, zbarlight
from utilities import signer_donnees, verifier_signature, qrcode_maker, get_timestamp_from_tsa, build_hidden_content, retrieve_from_hidden_contents, build_certificate, extract_hidden_data, retrieve_qrcode, verify_timestamp
from PIL import UnidentifiedImageError

private_key_file = './authorityCert/certauthority.key.pem'
public_key_file = './authorityCert/certauthority.publickey.pem'
signature_file = './temp/signature.bin'
data_file = './temp/infos.txt'
tsr_file = './temp/timestamp.tsr'
tsq_file = './temp/timestamp.tsq'
finalAttestationPath = "./temp/attestation_final.png"

#Partie pour la vérification de la signature
attestationToVerify = "./temp/attestation_a_verifier.png"
tsr_retrieved = "./temp/timestamp_retrieved.tsr"
tsq_retrieved = "./temp/timestamp_retrieved.tsq"
signature_retrieved = "./temp/signature_retrieved.bin"
infos_retrieved = "./temp/infos_retrieved.txt"
tsa_crt = "./freeTSACert/tsa.crt"
tsa_CA = "./freeTSACert/cacert.pem"



@route('/creation', method='POST')
def création_attestation():
    print("____________________________________________________________")
    print("Création d'une nouvelle attestation")
    contenu_identité = request.forms.get('identite')
    contenu_intitulé_certification = request.forms.get('intitule_certif')

    #creation des fichiers infos.txt et signature.bin
    fichier_infos = open(data_file, 'w')
    fichier_infos.write(contenu_identité + "_" + contenu_intitulé_certification)
    fichier_infos.close()
    #creation de la signature
    signature = signer_donnees(contenu_identité, contenu_intitulé_certification)
    fichier_signature = open(signature_file, 'wb')
    fichier_signature.write(signature)
    fichier_signature.close()
    b64_signature = base64.b64encode(signature)
    #print(f"Signature : {b64_signature}")

    #generation du qr code contenant la signature
    qrcode_maker(b64_signature)
    #this function will generate a timestamp and save it in the temp folder
    get_timestamp_from_tsa()

    #generating hidden content
    hidden_data = build_hidden_content(data_file, tsr_file, tsq_file)

    #creation de l'attestation
    response_image = build_certificate(contenu_identité, contenu_intitulé_certification, hidden_data)

    # renvoyer l'image en reponse
    print('Certificat délivré à \n Nom Prénom :', contenu_identité, ' Intitulé de la certification :',
            contenu_intitulé_certification)
    print("____________________________________________________________")
    response.set_header('Content-type', 'image/png')
    retrieve_qrcode(finalAttestationPath)
    return response_image



@route('/verification', method='POST')
def vérification_attestation():
    print("____________________________________________________________")
    print("Vérification d'une attestation")
    response.set_header('Content-type', 'text/plain')
    try:
        contenu_image = request.files.get('image')
        contenu_image.save('./temp/attestation_a_verifier.png',overwrite=True)

        #On recupere le code qr et la signature à l'interieur
        signature_bin = retrieve_qrcode(attestationToVerify)
        #on enregistre la signature
        signature_file = open(signature_retrieved, 'wb')
        signature_file.write(signature_bin)
        signature_file.close()

        #on extrait les données cachées
        retrieved_datas = extract_hidden_data(attestationToVerify)
        #ecriture des donneés dans infos_retrieved.txt, timestamp_retrieved.tsr et timestamp_retrieved.tsq
        retrieve_from_hidden_contents(retrieved_datas)

        #on verifie la signature
        verified = verifier_signature(public_key_file, signature_retrieved, infos_retrieved)
        return_string = ''
        if verified:
            return_string = "Signature vérifiée"
        else:
            return_string = "Signature non vérifiée"
        #On verifie avec le serveur TSA
        verified2 = verify_timestamp(tsa_CA, tsa_crt, tsr_retrieved, tsq_retrieved)
        if verified2:
            return_string += " et Timestamp vérifié"
        else:
            return_string += " Timestamp non vérifié"

        #read the infos_retrieved.txt file
        nom_prenom = ''
        intitule_certif = ''
        with open(infos_retrieved, 'r') as file:
            data = file.read()
            data = data.split('_')
            print(data)
            nom_prenom = data[0]
            intitule_certif = data[1]


        # verified (signature) and verified2 (timestamp) are booleans
        if verified and verified2:
            print(f"Nom et prénom : {nom_prenom} \n Intitulé de la certification : {intitule_certif}\n Attestation valide")
            print("____________________________________________________________")
            return f"Nom et prénom : {nom_prenom} \n Intitulé de la certification : {intitule_certif}\n Attestation valide\n"
            pr
        else:
            print(f"Nom et prénom : {nom_prenom} \n Intitulé de la certification : {intitule_certif}\n Attestation invalide")
            print("____________________________________________________________")
            return f"Nom et prénom : {nom_prenom} \n Intitulé de la certification : {intitule_certif}\n" + return_string + "\n"

    except UnidentifiedImageError as e:
        print("Erreur lors de la vérification de l'attestation : ", e)
        #return "Erreur : " + str(e) + "\nImpossible d'identifier le fichier image.\n"
        abort(500, "\nImpossible d'identifier le fichier image.\n")
    except ValueError as e:
        print("Erreur lors de la vérification de l'attestation : ", e)
        #return "Erreur : " + str(e) + "\nCette image ne ressemble pas à un certificat généré par CertifPlus.\n"
        abort(500, "Cette image ne ressemble pas à un certificat généré par CertifPlus.")
    except Exception as e:
        print("Erreur lors de la vérification de l'attestation : ", e)
        #return "Une erreur est survenue lors de la vérification de l'attestation : " + str(e) + "\n"
        abort(500, "Une erreur est survenue lors de la vérification de l'attestation")
        
    

@route('/fond', method='GET')
def récupérer_fond():
    response.set_header('Content-type', 'image/png')
    descripteur_fichier = open('fond_attestation.png','rb')
    contenu_fichier = descripteur_fichier.read()
    descripteur_fichier.close()
    return contenu_fichier


run(host='0.0.0.0',port=8080,debug=True)

