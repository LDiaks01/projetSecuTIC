#!/usr/bin/python3
from bottle import route, run, template, request, response
import subprocess, base64, qrcode
from utilities import signer_donnees, verifier_signature, qrcode_maker, get_timestamp_from_tsa, build_hidden_content, retrieve_from_hidden_contents, build_certificate, extract_hidden_data

private_key_file = './authorityCert/certauthority.key.pem'
public_key_file = './authorityCert/certauthority.publickey.pem'
signature_file = './temp/signature.bin'
data_file = './temp/infos.txt'
tsr_file = './temp/timestamp.tsr'
tsq_file = './temp/timestamp.tsq'
finalAttestationPath = "./temp/attestation_final.png"

@route('/creation', method='POST')
def création_attestation():
    contenu_identité = request.forms.get('identite')
    contenu_intitulé_certification = request.forms.get('intitule_certif')

    #test verification signature
    fichier_infos = open(data_file, 'w')
    fichier_infos.write(contenu_identité + contenu_intitulé_certification)
    fichier_infos.close()
    #creation de la signature
    signature = signer_donnees(contenu_identité, contenu_intitulé_certification)
    fichier_signature = open(signature_file, 'wb')
    fichier_signature.write(signature)
    fichier_signature.close()
    b64_signature = base64.b64encode(signature)
    print(f"Signature : {b64_signature}")

    #generation du qr code contenant la signature
    qrcode_maker(b64_signature)
    #this function will generate a timestamp and save it in the temp folder
    get_timestamp_from_tsa()

    #generating hidden content
    hidden_data = build_hidden_content(data_file, tsr_file, tsq_file)

    
    # test de verification de la signature
    verified = verifier_signature(public_key_file, signature_file, data_file)

    response_image = build_certificate(contenu_identité, contenu_intitulé_certification, hidden_data)

    retieved_datas = extract_hidden_data(finalAttestationPath)
    retrieve_from_hidden_contents(retieved_datas)

    # renvoyer l'image en reponse
    response.set_header('Content-type', 'image/png')
    return response_image
    
    print('nom prénom :', contenu_identité, ' intitulé de la certification :',
            contenu_intitulé_certification)


@route('/verification', method='POST')
def vérification_attestation():
    contenu_image = request.files.get('image')
    contenu_image.save('attestation_a_verifier.png',overwrite=True)
    response.set_header('Content-type', 'text/plain')
    return "ok!"

@route('/fond', method='GET')
def récupérer_fond():
    response.set_header('Content-type', 'image/png')
    descripteur_fichier = open('fond_attestation.png','rb')
    contenu_fichier = descripteur_fichier.read()
    descripteur_fichier.close()
    return contenu_fichier
run(host='0.0.0.0',port=8080,debug=True)

