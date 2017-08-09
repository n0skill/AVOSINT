from .geoloc import *
import requests
from bs4 import BeautifulSoup

# Aviation agencies sources
AT = 'https://www.austrocontrol.at/ta/OenflSucheEn?1-7.IFormSubmitListener-form'
US = 'http://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?MailProcess=1&nNumberTxt='
UK = 'http://publicapps.caa.co.uk/modalapplication.aspx?catid=1&pagetype=65&appid=1&mode=detailnosummary&fullregmark='
IS = 'http://www.icetra.is/aviation/aircraft/register?aq='
NL = 'http://www.newfoundland.nl/luchtvaartregister/user/en/luchtvaartuig.php?registratie='
BE = 'http://www.mobilit.fgov.be/bcaa/aircraft/search.jsf'
CA = 'http://wwwapps.tc.gc.ca/saf-sec-sur/2/ccarcs-riacc/RchSimpRes.aspx?cn=||&mn=||&sn=||&on=||&m=|'
CH = 'https://www.bazlwork.admin.ch/bazl-backend/lfr'

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
        return "%s\r%s\r%s\r%s\r%s" % (self.name, self.street, self.street_n, self.zip_code, self.country)

    def __str__():
        return self.__repr__()

class Plane:
    def __init__(self, webi, numb, call, latitude, longitude, origin=None, destination=None, altitude=None):
        self.coordinates = Coordinates(latitude, longitude)
        self.webi = webi
        self.numb = numb
        self.call = call
        self.origin = origin
        self.destination = destination
        self.altitude = altitude
        self.agency = self.get_agency()
        #self.owner = self.get_owner()
        self.path = self.get_path()
        self.heading = None
        pass

    def __repr__(self):
        return "%s\t%s\t%s\t%s" % (self.numb, self.call, self.coordinates, self.altitude)

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
                return Owner(name, street, str(city + ', ' + state), zip, 'United States')

        elif self.numb.startswith('G-E'):
            req = requests.get(self.agency.data_url + self.numb[2:])
            soup = BeautifulSoup(req.text, 'html.parser')
            own = soup.find('span', {'id':'currentModule_currentModule_RegisteredOwners'}).contents
            return Owner(own[0], own[4], own[6], own[8], 'Great Britain')
        elif self.numb.startswith('TF'):
            req = requests.get(self.agency.data_url+self.numb)
            if req.status_code is 200:
                soup = BeautifulSoup(req.text, 'html.parser')
                own = soup.find(own = soup.find('li', {'class':'owner'}))
                if own is not None:
                    return None
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
