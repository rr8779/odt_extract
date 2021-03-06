# odt_extract

Permet d'extraire les données utiles à la vérification de la signature électronique d'un fichier odt (open document text) : contenu texte brut, contenu xml au format "canonical xml", empreinte signée du contenu, certificat de signature utilisé.

Testé sous RHEL 6.3 64 bits / python 2.6.6 release 29.el6_2.2 (rpm par défaut)
- Nécessite la lib lxml, sous RHEL 6.3 faire "yum install python-lxml"
- Nécessite la lib argparse qui n'est en standard qu'à partir de python 2.7 : https://pypi.python.org/pypi/argparse

__Quelques exemples d'utilisations sur un fichier "test_signed.odt" :__

_Options de la ligne de commande:_

`./odt_extract.py --help`

_Affichage du certificat de signature :_

`./odt_extract.py --file test_signed.odt --x509 | base64 --decode | openssl x509 -inform DER -text -noout`

_Calcul de l'empreinte du contenu :_

`./odt_extract.py --file test_signed.odt --content | openssl dgst -binary -sha1 | base64`

_Affichage de l'empreinte du contenu signée dans le bloc "SignedInfo" :_

`./odt_extract.py --file test_signed.odt --digest`

_Calcul de l'empreinte du bloc signé "SignedInfo" :_

`/odt_extract.py --file test_signed.odt --signedinfo | openssl dgst -binary -sha1 | base64`

_Déchiffrement (avec la clé publique) de la signature du bloc "SignedInfo" :_

`./odt_extract.py --file test_signed.odt --x509 | base64 --decode | openssl x509 -inform DER > cert.txt`

`./odt_extract.py --file test_signed.odt --dsig | base64 --decode > signaturevalue.txt`

`openssl rsautl -inkey cert.txt -certin -in signaturevalue.txt | base64`

TODO :
- parsing d'un "formulaire" dans le document signé / pouvoir extraire des champs précis
- Vérifier l'attribut `<CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>`
- Vérifier l'attribut `<SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>`
- Vérifier l'attribut `<Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>`
- Vérifier l'attribut `<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>`

Références :
- Spec. odf : http://docs.oasis-open.org/office/v1.2/cs01/OpenDocument-v1.2-cs01.html
- Spec. odt : http://docs.oasis-open.org/office/v1.2/cs01/OpenDocument-v1.2-cs01-part1.html#__RefHeading__1415004_253892949
- Signature : http://docs.oasis-open.org/office/v1.2/cs01/OpenDocument-v1.2-cs01-part3.html#Digital_Signature_File
- Spec. signature xml : https://www.w3.org/TR/2008/REC-xmldsig-core-20080610/
-  Spec. canonical xml : https://www.w3.org/TR/xml-c14n
