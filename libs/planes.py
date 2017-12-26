# -*- coding: utf-8 -*-
from .geoloc import *
import requests
from bs4 import BeautifulSoup
import json

# Aviation agencies sources
AT = 'https://www.austrocontrol.at/ta/OenflSucheEn?1-7.IFormSubmitListener-form'
NL = 'http://www.newfoundland.nl/luchtvaartregister/user/en/luchtvaartuig.php?registratie='
BE = 'http://www.mobilit.fgov.be/bcaa/aircraft/search.jsf'

CA = 'http://wwwapps.tc.gc.ca/saf-sec-sur/2/ccarcs-riacc/RchSimpRes.aspx?cn=||&mn=||&sn=||&on=||&m=|'


# Implemented
URL_DE = ''
URL_IS = 'http://www.icetra.is/aviation/aircraft/register?aq='
URL_CH = 'https://www.bazlwork.admin.ch/bazl-backend/lfr'
URL_UK = 'http://publicapps.caa.co.uk/modalapplication.aspx?catid=1&pagetype=65&appid=1&mode=detailnosummary&fullregmark='
URL_US = 'http://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?MailProcess=1&nNumberTxt='

# TODO
class OwnerGetter:
    def __init__(self, agency, **specs):
        # Specs are specifics methods for retrieving the owner data
        pass

class Owner:
    def __init__(self, name, street, city, zip_code, country):
        self.name = name
        self.street = street
        self.city = city
        self.zip_code = zip_code
        self.country = country

    def __repr__(self):
        return "%s\n%s\n%s\n%s\n%s" % (self.name, self.street, self.city, self.zip_code, self.country)

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
            req = requests.get(URL_US + self.numb)
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
            req = requests.get(URL_UK + self.numb[2:])
            soup = BeautifulSoup(req.text, 'html.parser')
            own = soup.find('span', {'id':'currentModule_currentModule_RegisteredOwners'}).contents

            return Owner(own[0], own[4],   own[6],   own[8],  'Great Britain')

        # ICELAND
        elif self.numb.startswith('TF'):
            name = ''
            street = ''
            city = ''
            req = requests.get(URL_IS+self.numb)
            if req.status_code is 200:
                soup = BeautifulSoup(req.text, 'html.parser')
                own = soup.find('li', {'class':'owner'})
                won = own.stripped_strings

                for i,j in enumerate(won):
                    if i == 1:
                        name = j
                    if i == 2:
                        street = j
                    if i == 3:
                        city = j
                if own is not None:
                    return Owner(name, street, city, '', 'Iceland')
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
            soup = BeautifulSoup(response.text, 'html.parser')
            bls = soup.find('a', string=self.numb)

            response = requests.get('http://www.immat.aviation-civile.gouv.fr/immat/servlet/' + bls['href'], headers=headers, data=data)
            soup = BeautifulPSoup(response.text, 'html.parser')
            bls = soup.find('a', string="Données juridiques")

            response = requests.get('http://www.immat.aviation-civile.gouv.fr/immat/servlet/' + bls['href'], headers=headers, data=data)
            soup = BeautifulSoup(response.text, 'html.parser')
            bls = soup.find_all('td', {'class':"tdLigneListe"})

            name = bls[0].text
            addr = bls[1].text
            city = bls[2].text
            return Owner(name, addr, city, '', 'France')


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
            own         = Owner(name, street + ' ' + street_n, 'CITY TODO',zipcode, "Switzerland")
            return own

        elif self.numb.startswith('OE'):
            cookies = {
                'JSESSIONID': '5FBDACF3598077D88445BF60A6741886',
                'TS01efbd85': '01f60c9e4f1ea3e8a93276490ec04ebcb3eb255a85b97d8425918ae1d7b64e53fbc1f81377d2d68acc1c60ec4afc4673babca57c0a638ba77560cbaac9f438ef173ad6ca85',
            }

            headers = {
                'Pragma': 'no-cache',
                'Origin': 'https://www.austrocontrol.at',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Cache-Control': 'no-cache',
                'Referer': 'https://www.austrocontrol.at/ta/OenflSucheEn?4',
                'Connection': 'keep-alive',
            }

            params = (
                ('4-5.IFormSubmitListener-form', ''),
            )

            data = [
              ('id3_hf_0', ''),
              ('txtKennzeichen', self.numb[3:]),
              ('txtOrdnungszahl', ''),
              ('txtHersteller', ''),
              ('txtBaumuster', ''),
              ('cmbLfzart', ''),
              ('txtSeriennummer', ''),
              ('radStartgewicht', '1'),
              ('txtStartgewicht', ''),
              ('txtHalter', ''),
              ('p::submit', ''),
            ]

            response = requests.post('https://www.austrocontrol.at/ta/OenflSucheEn', headers=headers, params=params, cookies=cookies, data=data)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id':'resultTable'})
            tds = table.find_all('td')
            ownerinfos = tds[4] # Owner infos contained in 5th column
            parag = ownerinfos.find('p')
            infos = parag.decode().split('<br>')
            name = infos[0].replace('<p>', '').encode()
            addr_city = infos[1].split(',')[0].encode()
            addr_street = infos[1].split(',')[1].encode()
            country = infos[2]
            return Owner(name, addr_street, addr_city, 'N/A', 'Austria')
        else:
            return None

    def get_path(self):
        return []
        #j = getjson(flight_data_src+self.name)
