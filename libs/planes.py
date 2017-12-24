# -*- coding: utf-8 -*-
from .geoloc import *
import requests
from bs4 import BeautifulSoup
import json

# Aviation agencies sources
AT = 'https://www.austrocontrol.at/ta/OenflSucheEn?1-7.IFormSubmitListener-form'
US = 'http://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?MailProcess=1&nNumberTxt='
UK = 'http://publicapps.caa.co.uk/modalapplication.aspx?catid=1&pagetype=65&appid=1&mode=detailnosummary&fullregmark='
IS = 'http://www.icetra.is/aviation/aircraft/register?aq='
NL = 'http://www.newfoundland.nl/luchtvaartregister/user/en/luchtvaartuig.php?registratie='
BE = 'http://www.mobilit.fgov.be/bcaa/aircraft/search.jsf'
CA = 'http://wwwapps.tc.gc.ca/saf-sec-sur/2/ccarcs-riacc/RchSimpRes.aspx?cn=||&mn=||&sn=||&on=||&m=|'
URL_CH = 'https://www.bazlwork.admin.ch/bazl-backend/lfr'

# TODO
class OwnerGetter:
    def __init__(self, agency, **specs):
        # Specs are specifics methods for retrieving the owner data
        pass

class Agency:
    def __init__(self, country, main_url, data_url):
        self.country = country
        self.data_url = data_url
        self.main_url = main_url
    pass
    def get_owner(self):
        pass
        # parent ?

class Owner:
    def __init__(self, name, street, street_n, zip_code, country):
        self.name = name
        self.street = street
        self.street_n = street_n
        self.zip_code = zip_code
        self.country = country

    def __repr__(self):
        return "%s\n%s %s\n%s\n%s" % (self.name, self.street, self.street_n, self.zip_code, self.country)

    def __str__(self):
        return self.__repr__()

class Plane:
    def __init__(self, webi, numb, call, latitude, longitude, origin=None, destination=None, altitude=None):
        self.coords = Coordinates(latitude, longitude)
        self.webi = webi
        self.numb = numb
        self.call = call
        self.origin = origin
        self.destination = destination
        self.altitude = altitude
        self.agency = self.get_agency()
        self.owner = self.get_owner()
        #self.path = self.get_path()
        self.heading = None
        pass

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return "%s\t%s\t%s\t%s\t%s" % (self.numb, self.call, self.coords, self.altitude, str(self.owner))

    def get_owner(self):
        if self.numb.startswith('N'):
            req = requests.get(self.agency.data_url + self.numb)
            if req.status_code is 200:
                soup = BeautifulSoup(req.text, 'html.parser')
                name = soup.find('span', {'id':'content_lbOwnerName'}).text
                street = soup.find('span', {'id':'content_lbOwnerStreet'}).text
                street2= soup.find('span', {'id':'content_lbOwnerStreet'}).text
                city   = soup.find('span', {'id':'content_lbOwnerCity'}).text
                state  = soup.find('span', {'id':'content_lbOwnerState'}).text
                zip    = soup.find('span', {'id':'content_lbOwnerZip'}).text
                own = Owner(name, street, str(city + ', ' + state), zip, 'United States')
                return own

        elif self.numb.startswith('G-E'):

            req = requests.get(self.agency.data_url + self.numb[2:])
            soup = BeautifulSoup(req.text, 'html.parser')
            own = soup.find('span', {'id':'currentModule_currentModule_RegisteredOwners'}).contents

            return Owner(own[0], own[4],   own[6],   own[8],  'Great Britain')

        # ICELAND
        elif self.numb.startswith('TF'):
            req = requests.get(self.agency.data_url+self.numb)
            if req.status_code is 200:
                soup = BeautifulSoup(req.text, 'html.parser')
                own = soup.find(own = soup.find('li', {'class':'owner'}))
                if own is not None:
                    return None
            return None

        # FRANCE
        elif self.numb.startswith('F-'):
            headers = {
                'Pragma': 'no-cache',
                'Origin': 'http://www.immat.aviation-civile.gouv.fr',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Cache-Control': 'no-cache',
                'Referer': 'http://www.immat.aviation-civile.gouv.fr/immat/servlet/aeronef_liste.html',
                'Connection': 'keep-alive',
            }

            data = [
              ('FORM_DTO_ID', 'DTO_RECHERCHE_AER'),
              ('FORM_ACTION', 'SEARCH'),
              ('FORM_CHECK', 'true'),
              ('FORM_ROW', ''),
              ('CTRL_ID', '145814_ad541de4'),
              ('SUBFORM_DTC_ID', 'DTC_1'),
              ('$DTO_RECHERCHE_AER$PER_ID', ''),
              ('$DTO_RECHERCHE_AER$PER_VERSION', ''),
              ('$DTO_RECHERCHE_AER$PERSONNE', ''),
              ('$DTO_RECHERCHE_AER$MRQ_CD', self.numb),
              ('$DTO_RECHERCHE_AER$CNT_LIBELLE', ''),
              ('$DTO_RECHERCHE_AER$SI_RADIE', '1'),
              ('$DTO_RECHERCHE_AER$SI_RADIEcheckbox', '1'),
              ('$DTO_RECHERCHE_AER$SI_INSCRIT', '1'),
              ('$DTO_RECHERCHE_AER$SI_INSCRITcheckbox', '1'),
              ('$DTO_RECHERCHE_AER$CRE_NUM_SERIE', ''),
            ]

            response = requests.post('http://www.immat.aviation-civile.gouv.fr/immat/servlet/aeronef_liste.html', headers=headers, data=data)
            print(response.text).decode()

        elif self.numb.startswith('HB-'):
            url=URL_CH
            headers = {
                'Pragma': 'no-cache',
                'Origin': 'https://www.bazlwork.admin.ch',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json, text/plain, */*',
                'Cache-Control': 'no-cache',
                'Referer': 'https://www.bazlwork.admin.ch/bazl/',
                'Connection': 'keep-alive',
            }
            data = '{"page_result_limit":10,"current_page_number":1,"sort_list":"registration","totalItems":0,"query":{"registration":"' +self.numb[3:]+'"},"language":"fr","tab":"basic"}'

            response = requests.post('https://www.bazlwork.admin.ch/bazl-backend/lfr', headers=headers, data=data)

            jsonobj     = json.loads(response.text)
            infoarray   = jsonobj[0]
            own_ops     = infoarray.get('ownerOperators')
            leng        = len(own_ops)
            name        = own_ops[leng-1].get('ownerOperator').encode().decode()
            addr        = own_ops[leng-1].get('address')
            street      = addr.get('street').encode().decode()
            street_n    = addr.get('streetNo').encode().decode()
            zipcode     = addr.get('zipCode').encode().decode()
            own         = Owner(name, street, street_n, zipcode, "Switzerland")
            return own

        else:
            return None

    def get_agency(self):
        if self.numb.startswith('OE-'):
            return Agency('Austria', 'austrocontrol.at', 'https://www.austrocontrol.at/ta/OenflSucheEn?1-7.IFormSubmitListener-form')
        if self.numb.startswith('N'):
            return Agency('USA', 'faa.gov', 'http://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?MailProcess=1&nNumberTxt=')
            # UK
        elif self.numb.startswith('G-E'):
            return Agency('UK', 'caa.co.uk', 'http://publicapps.caa.co.uk/modalapplication.aspx?catid=1&pagetype=65&appid=1&mode=detailnosummary&fullregmark=')

         # Iceland
        elif self.numb.startswith('TF'):
            return Agency('Iceland', 'icetra.is', 'http://www.icetra.is/aviation/aircraft/register?aq=')

    def get_path(self):
        return []
        #j = getjson(flight_data_src+self.name)
