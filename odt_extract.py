#! /usr/bin/python
# -*- coding: utf-8 -*-

# Script permettant d'extraire le texte brut et la signature électronique d'un fichier odt (opendocument text file)

# Testé sous RHEL 6.3 64 bits / python 2.6.6 release 29.el6_2.2 (rpm par défaut)

# Spec. odf : http://docs.oasis-open.org/office/v1.2/cs01/OpenDocument-v1.2-cs01.html
# Spec. odt : http://docs.oasis-open.org/office/v1.2/cs01/OpenDocument-v1.2-cs01-part1.html#__RefHeading__1415004_253892949
# Signature : http://docs.oasis-open.org/office/v1.2/cs01/OpenDocument-v1.2-cs01-part3.html#Digital_Signature_File
# Spec. signature xml : https://www.w3.org/TR/2008/REC-xmldsig-core-20080610/
# Spec. canonical xml : https://www.w3.org/TR/xml-c14n

# argparse n'est en standard qu'à partir de python 2.7
import argparse

from zipfile import ZipFile
#from xml.etree import ElementTree
import lxml.etree as ElementTree
from StringIO import StringIO
from sys import exit

# Represente un fichier au format OASIS "ODF" Open Document Format
class ODTFile:

    def __init__(self, archive=''):

        # Namespace xml déclaré par l'OASIS pour le format opendocument (ODF)
        self._ODF_NS = {
                'office':'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
                'text':'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
                'dsig':'urn:oasis:names:tc:opendocument:xmlns:digitalsignature:1.0',
                'ds':'http://www.w3.org/2000/09/xmldsig#'}

        self._MIME_FILE = 'mimetype'
        self._MIMETYPE = 'application/vnd.oasis.opendocument.text'
        self._CONTENT_FILE = 'content.xml'
        self._DSIG_FILE = 'META-INF/documentsignatures.xml'

        self.xmlroot = None
        self.dsigroot = None

        mimedata = None
        xmldata = None
        dsigdata = None
        try: fichier_zip = ZipFile(archive, 'r')
        except: pass
        else:
            try: mimedata = fichier_zip.read(self._MIME_FILE)
            except: mimedata = None
            try: xmldata = fichier_zip.read(self._CONTENT_FILE)
            except: xmldata = None
            try: dsigdata = fichier_zip.read(self._DSIG_FILE)
            except: dsigdata = None
        try: fichier_zip.close()
        except: pass

        if (mimedata == self._MIMETYPE) and xmldata:
            self.xmlroot = ElementTree.fromstring(xmldata)
        if dsigdata: self.dsigroot = ElementTree.fromstring(dsigdata)

    def get_odf_version(self):
        # Version ODF
        return self.xmlroot.get('{%s}version' % self._ODF_NS['office'])

    def get_raw_text(self):
        # Contenu texte brut
        raw_text = ''
        # Voir les specifications OASIS correspondantes
        body_element = self.xmlroot.find('{%s}body' % self._ODF_NS['office'])
        text_element = body_element.find('{%s}text' % self._ODF_NS['office'])
        for p_element in text_element.findall('{%s}p' % self._ODF_NS['text']):
            if p_element.text is not None: raw_text += '%s\n' % p_element.text
        return raw_text

    def get_content(self):
        # Contenu xml au format canonical xml (xml-c14n)
        temp_ET = ElementTree.ElementTree(self.xmlroot)
        temp_file_object = StringIO()
        # Transformation en xml canonique : write_c14n(self, file, exclusive=False, with_comments=True, compression=0, inclusive_ns_prefixes=None)
        # Canonical XML 1.0 (omits comments) : http://www.w3.org/TR/2001/REC-xml-c14n-20010315
        temp_ET.write_c14n(temp_file_object, exclusive=False, with_comments=False)
        return temp_file_object.getvalue()

    def get_dsig_algo(self):
        # Algorithme utilisée pour la signature électronique
        dsig_algo = ''
        # Voir les specifications OASIS correspondantes et les specs W3C xmldsig-core
        # On ne prend en compte que le premier element <ds:Signature> trouvé
        ds_element = self.dsigroot.find('{%s}Signature' % self._ODF_NS['ds'])
        signedinfo_element = ds_element.find('{%s}SignedInfo' % self._ODF_NS['ds'])
        signature_method_element = signedinfo_element.find('{%s}SignatureMethod' % self._ODF_NS['ds'])
        dsig_algo = signature_method_element.get('Algorithm')
        return dsig_algo

    def get_dsig_digest(self):
        # Empreinte (condensat) du contenu
        dsig_digest = ''
        # Voir les specifications OASIS correspondantes et les specs W3C xmldsig-core
        # On ne prend en compte que le premier element <ds:Signature> trouvé
        ds_element = self.dsigroot.find('{%s}Signature' % self._ODF_NS['ds'])
        signedinfo_element = ds_element.find('{%s}SignedInfo' % self._ODF_NS['ds'])
        reference_elements = signedinfo_element.findall('{%s}Reference' % self._ODF_NS['ds'])
        for reference_element in reference_elements:
            if reference_element.get('URI') == self._CONTENT_FILE:
                digest_value_element = reference_element.find('{%s}DigestValue' % self._ODF_NS['ds'])
                dsig_digest = digest_value_element.text
                break
        return dsig_digest

    def get_dsig_value(self):
        # Signature (empreinte du contenu signé avec la clé privée du certificat)
        # Le résultat est en base64
        dsig_value = ''
        # Voir les specifications OASIS correspondantes et les specs W3C xmldsig-core
        # On ne prend en compte que le premier element <ds:Signature> trouvé
        ds_element = self.dsigroot.find('{%s}Signature' % self._ODF_NS['ds'])
        signaturevalue_element = ds_element.find('{%s}SignatureValue' % self._ODF_NS['ds'])
        dsig_value = signaturevalue_element.text
        return dsig_value

    def get_dsig_issuer(self):
        # Emetteur du certificat de signature
        dsig_issuer = ''
        return dsig_issuer

    def get_dsig_x509(self):
        # Le certificat de signature utilisé
        # Le résultat est en base64
        dsig_x509 = ''
        # Voir les specifications OASIS correspondantes et les specs W3C xmldsig-core
        # On ne prend en compte que le premier element <ds:Signature> trouvé
        ds_element = self.dsigroot.find('{%s}Signature' % self._ODF_NS['ds'])
        keyinfo_element = ds_element.find('{%s}KeyInfo' % self._ODF_NS['ds'])
        x509data_element = keyinfo_element.find('{%s}X509Data' % self._ODF_NS['ds'])
        x509cert_element = x509data_element.find('{%s}X509Certificate' % self._ODF_NS['ds'])
        dsig_x509 = x509cert_element.text
        return dsig_x509

    def get_dsig_date(self):
        # Date de la signature
        dsig_date = ''
        return dsig_date

    def __repr__(self):
        # Permet d'afficher les elements de l'arbre xml
        repr = ''
        if self.xmlroot:
            # xml.etree.ElementTree.Element.itertext() n'est pas dispo avant python 2.7
            for element in self.xmlroot.getiterator():
                repr += 'Tag: %s\n' % element.tag
                repr += 'Attrib: %s\n' % element.attrib
                repr += 'Text: %s\n' % element.text
        return repr.encode('utf8')

if __name__ == '__main__':

    code_retour = 0

    # Analyse des arguments de la ligne de commande
    parser = argparse.ArgumentParser(description='Permet d\'extraire le texte brut et la signature électronique d\'un fichier odt (opendocument text file)')
    parser.add_argument('--file', required=True, help='Fichier à traiter')
    parser.add_argument('--text', action='store_true', help='Affichage du texte brut du contenu')
    parser.add_argument('--content', action='store_true', help='Affichage du contenu xml au format canonical xml (xml-c14n)')
    parser.add_argument('--digest', action='store_true', help='Affichage de l\'empreinte (condensat) du contenu')
    parser.add_argument('--dsig', action='store_true', help='Affichage de la signature (empreinte signée) au format base64')
    parser.add_argument('--issuer', action='store_true', help='Affichage de l\'emetteur du certificat')
    parser.add_argument('--x509', action='store_true', help='Affichage du certificat de signature utilisé au format base64')
    parser.add_argument('--date', action='store_true', help='Affichage de la date de signature du contenu')
    parser.add_argument('--verbose', action='store_true', help='Affichage des étapes successives')
    args = parser.parse_args()

    # args contient les arguments de la ligne de commande
    if args.verbose: print 'Lecture du fichier %s' % args.file
    odtfile = ODTFile(args.file)
    if odtfile.xmlroot is None:
        print 'Erreur de lecture du contenu xml'
        code_retour = 1
    else:
        if args.verbose: print 'Contenu xml au format ODF version %s' % odtfile.get_odf_version()
        if args.text: print odtfile.get_raw_text()
        if args.content: print odtfile.get_content()
        if odtfile.dsigroot is None:
            print 'Erreur de lecture de la signature électronique'
            code_retour = 1
        else:
            if args.verbose: print 'Algorithme de la signature électronique %s' % odtfile.get_dsig_algo()
            if args.digest: print odtfile.get_dsig_digest()
            if args.dsig: print odtfile.get_dsig_value()
            if args.issuer: print odtfile.get_dsig_issuer()
            if args.x509: print odtfile.get_dsig_x509()
            if args.date: print odtfile.get_dsig_date()

    exit(code_retour)
