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
        return "%s\n\t\t\t\t\t%s\t%s\n\t\t\t\t\t%s\n\t\t\t\t\t%s" % (self.name, self.street, self.street_n, self.zip_code, self.country)

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

        elif self.numb.startswith('TF'):
            req = requests.get(self.agency.data_url+self.numb)
            if req.status_code is 200:
                soup = BeautifulSoup(req.text, 'html.parser')
                own = soup.find(own = soup.find('li', {'class':'owner'}))
                if own is not None:
                    return None
            return None

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
            data = '{"page_result_limit":10,"current_page_number":1,"sort_list":"registration","totalItems":3337,"query":{"registration":"' +self.numb[3:]+'"},"language":"fr","tab":"basic"}'

            response = requests.post('https://www.bazlwork.admin.ch/bazl-backend/lfr', headers=headers, data=data)
            text = response.text
            jsonobj = json.loads(text)
            leng = len(jsonobj[0].get('ownerOperators'))
            name = str(jsonobj[0].get('ownerOperators')[leng-1].get('ownerOperator'))
            street = str(jsonobj[0].get('ownerOperators')[leng-1].get('address').get('street').encode())
            street_n = str(jsonobj[0].get('ownerOperators')[leng-1].get('address').get('streetNo').encode())
            zipcode = str(jsonobj[0].get('ownerOperators')[leng-1].get('address').get('zipCode').encode())
            own = Owner(name, street, street_n, zipcode, "Switzerland")
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
