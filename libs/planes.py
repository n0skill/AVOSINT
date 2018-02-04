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

class Owner:
    def __init__(self, name, street, city, zip_code, country):
        self.name = name
        self.street = street
        self.city = city
        self.zip_code = zip_code
        self.country = country

    def __repr__(self):
        return "%s %s %s %s %s" % (self.name, self.street, self.city, self.zip_code, self.country)

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

            return Owner(own[0], own[4], own[6], own[8], 'Great Britain')

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
                'Origin': 'http://www.immat.aviation-civile.gouv.fr',
                'Referer': 'http://www.immat.aviation-civile.gouv.fr/immat/servlet/aeronef_liste.html'
            }

            data = [
              ('FORM_DTO_ID', 'DTO_RECHERCHE_AER'),
              ('FORM_ACTION', 'SEARCH'),
              ('FORM_CHECK', 'true'),
              ('FORM_ROW', ''),
              ('CTRL_ID', '1010'),
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

            if bls is not None:
                response = requests.get('http://www.immat.aviation-civile.gouv.fr/immat/servlet/' + bls['href'], headers=headers, data=data)
                soup = BeautifulSoup(response.text, 'html.parser')
                bls = soup.find('a', string="Données juridiques")

                response = requests.get('http://www.immat.aviation-civile.gouv.fr/immat/servlet/' + bls['href'], headers=headers, data=data)
                soup = BeautifulSoup(response.text, 'html.parser')
                bls = soup.find_all('td', {'class':"tdLigneListe"})

                name = bls[0].text
                addr = bls[1].text
                city = bls[2].text
                return Owner(name, addr, city, '', 'France')

            else:
                return None

        elif self.numb.startswith('HB-'):
            url=URL_CH
            headers = {
                'Pragma': 'no-cache',
                'Origin': 'https://www.bazlwork.admin.ch',
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://www.bazlwork.admin.ch/bazl/'
            }
            data = '{"page_result_limit":10,"current_page_number":1,"sort_list":"registration","totalItems":0,"query":{"registration":"' +self.numb[3:]+'"},"language":"fr","tab":"basic"}'

            response = requests.post('https://www.bazlwork.admin.ch/bazl-backend/lfr', headers=headers, data=data)

            jsonobj     = json.loads(response.text)
            infoarray   = jsonobj[0]
            own_ops     = infoarray.get('ownerOperators')
            leng        = len(own_ops)
            name        = own_ops[leng-1].get('ownerOperator').encode().decode()
            addr        = own_ops[leng-1].get('address')
            street      = str(addr.get('street').encode())
            street_n    = str(addr.get('streetNo').encode())
            zipcode     = addr.get('zipCode').encode().decode()

            own         = Owner(name, street + ' ' + street_n, 'CITY TODO',zipcode, "Switzerland")
            return own

        elif self.numb.startswith('OE'):
            # Austria
            # FIXME: Needs new cookies to function proprely
            s = requests.session()
            response = s.get('https://www.austrocontrol.at/en/aviation_agency/aircraft/aircraft_register/search_online')
            #print(s.cookies)
            params = (
                ('1-2.IFormSubmitListener-form', ''),
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

            headers = {
                'Origin': 'https://www.austrocontrol.at',
                'Referer': 'https://www.austrocontrol.at/ta/OenflSucheEn?1',
            }
            response = s.post('https://www.austrocontrol.at/ta/OenflSucheEn?0-1.IFormSubmitListener-form', data=data, headers=headers)
            if response.status_code is not 200:
                print(response.status_code)
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find('table', {'id':'resultTable'})

            if table is None:
                return None

            tds = table.find_all('td')
            ownerinfos = tds[4] # Owner infos contained in 5th column
            parag = ownerinfos.find('p')
            infos = parag.encode().decode().split('<br>')
            name = infos[0].replace('<p>', '').encode()
            addr_street = infos[1].split(',')[1].encode()
            addr_city = infos[1].split(',')[0].encode()
            return Owner(name, addr_street, addr_city, '', 'Austria')
        elif self.numb.startswith('VH-'):
            response = requests.get('https://www.casa.gov.au/aircraft-register?search_api_views_fulltext=&vh='+ self.numb[2:] +'&field_ar_serial=')
            soup = BeautifulSoup(response.text, 'html.parser')
            infos = soup.find('div', {'class':'field-name-field-ar-registration-holder'})
            onlyinfo = infos.text.replace('Registration holder:', '')
            return Owner(onlyinfo[4:], '', '', '', '')
        elif self.numb.startswith('OO-'):
            s = requests.session()

            response = s.get('http://www.mobilit.fgov.be:7081/bcaa/aircraft/search.jsf')


            data = [
              ('javax.faces.partial.ajax', 'true'),
              ('javax.faces.source', 'form:j_idt104'),
              ('javax.faces.partial.execute', 'form:j_idt104'),
              ('javax.faces.partial.render', 'form'),
              ('javax.faces.behavior.event', 'rowSelect'),
              ('javax.faces.partial.event', 'rowSelect'),
              ('form:j_idt104_instantSelectedRowKey', '3479'),
              ('form', 'form'),
              ('form:j_idt38:j_idt41:inputText', 'OO-LEL'),
              ('form:j_idt38:j_idt52:inputText', ''),
              ('form:j_idt38:j_idt53:selectManyCheckbox', 'REGISTERED'),
              ('form:j_idt38:j_idt53:selectManyCheckbox', 'CANCELLED'),
              ('form:j_idt38:j_idt60:inputText', ''),
              ('form:j_idt38:j_idt61:inputText', ''),
              ('form:j_idt38:j_idt63:inputText', ''),
              ('form:j_idt38:j_idt64:selectOneMenu', ''),
              ('form:j_idt38:j_idt73:selectOneMenu', ''),
              ('form:j_idt38:j_idt74:selectOneMenu', ''),
              ('form:j_idt104_selection', '3479'),
              ('form:j_idt104_scrollState', '0,0'),
              ('javax.faces.ViewState', '8392740435488277566:1147169290838077729'),
            ]

            response = s.post('http://www.mobilit.fgov.be:7081/bcaa/aircraft/search.jsf;', data=data)
            #print(response.text.encode())
            soup = BeautifulSoup(response.text, 'html.parser')
            found = soup.find('div', {'id':'form:results'})
            print(found)

        elif self.numb.startswith('C-'):
            response = requests.get('         http://wwwapps.tc.gc.ca/saf-sec-sur/2/ccarcs-riacc/RchSimpRes.aspx?cn=%7c%7c&mn=%7c%7c&sn=%7c%7c&on=%7c%7c&m=%7c' + self.numb[2:] + '%7c', allow_redirects=True)
            soup = BeautifulSoup(response.text, 'html.parser')
            div = soup.find('div', {'id':'dvOwnerName'})

            if div is None:
                return None 
            name = div.find()

            name = div.select('div')[1].get_text(strip=True)

            div = soup.find('div', {'id':'divOwnerAddress'})
            street = div.select('div')[1].get_text(strip=True)

            div = soup.find('div', {'id':'divOwnerCity'})
            city = div.select('div')[1].get_text(strip=True)
            code = div.select('div')[3].get_text(strip=True)

            div = soup.find('div', {'id':'divOwnerProvince'})
            prov = div.select('div')[1].get_text(strip=True)

            return Owner(name, street, city + ' ' + code, prov, 'Canada')

        else:
            return None

    def get_path(self):
        return []
        #j = getjson(flight_data_src+self.name)
