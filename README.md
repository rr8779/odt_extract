# odt_extract

Permet d'extraire les données utiles à la vérification de la signature électronique d'un fichier odt (open document text) : contenu texte brut, contenu xml au format "canonical xml", empreinte signée du contenu, certificat de signature utilisé.

Testé sous RHEL 6.3 64 bits / python 2.6.6 release 29.el6_2.2 (rpm par défaut)
- Nécessite la lib lxml, sous RHEL 6.3 faire "yum install python-lxml"
- Nécessite la lib argparse qui n'est en standard qu'à partir de python 2.7 : https://pypi.python.org/pypi/argparse

Quelques exemples d'utilisations sur un fichier "test_signed.odt" :

Affichage du certificat de signature :

./odt_extract.py --file test_signed.odt --x509 | base64 --decode | openssl x509 -inform DER -text -noout

TODO : parsing d'un "formulaire" dans le document signé / pouvoir extraire des champs précis

Références :
- Spec. odf : http://docs.oasis-open.org/office/v1.2/cs01/OpenDocument-v1.2-cs01.html
- Spec. odt : http://docs.oasis-open.org/office/v1.2/cs01/OpenDocument-v1.2-cs01-part1.html#__RefHeading__1415004_253892949
- Signature : http://docs.oasis-open.org/office/v1.2/cs01/OpenDocument-v1.2-cs01-part3.html#Digital_Signature_File
- Spec. signature xml : https://www.w3.org/TR/2008/REC-xmldsig-core-20080610/
-  Spec. canonical xml : https://www.w3.org/TR/xml-c14n
