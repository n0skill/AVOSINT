# Python script to lookup plane owner's in a particular geographic area using public data from planefinder.net and the federal aviation agency.
# If a particular owner is found, the plane infos are shown


# TODO
# Implement ADS-B
# Implement news source, location API, and search based on location name  

import requests
import random as rand
import json
import logging
from bs4 import BeautifulSoup

# Data sources
flightradar = 'http://data.flightradar24.com/zones/fcgi/feed.js?bounds='
planefinder = 'https://planefinder.net/endpoints/update.php?callback=planeDataCallback&faa=1&routetype=iata&cfCache=true&bounds=37%2C-80%2C40%2C-74&_=1452535140'

# News source
AP = 'Associated Press'
AFP = 'Agence France Presse'
AP_KEY = 'API KEY HERE'


# Aviation agencies
US = 'http://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?MailProcess=1&nNumberTxt='
UK = 'http://publicapps.caa.co.uk/modalapplication.aspx?catid=1&pagetype=65&appid=1&mode=detailnosummary&fullregmark='
IS = 'http://www.icetra.is/aviation/aircraft/register?aq='
NL = 'http://www.newfoundland.nl/luchtvaartregister/user/en/luchtvaartuig.php?registratie=PH-'
BE = 'http://www.mobilit.fgov.be/bcaa/aircraft/search.jsf'
CA = 'http://wwwapps.tc.gc.ca/saf-sec-sur/2/ccarcs-riacc/RchSimpRes.aspx?cn=||&mn=||&sn=||&on=||&m=|'

# Defines areas to lookup.
# Format:
# AREA = [maxlat, minlat, maxlon, minlon]

#LA = [35, 32, -115, -120]
#TX = [37, 25, -92, -106]
#NY = [41, 39, -72, -75]
#CH = [42 , 40, -87, -89]
ICELAND = [65, 63, -20, -22]
rand_lat = rand.randrange(24, 49)
rand_long = rand.randrange(-124, -67)

# Defines a list of areas to lookup.
LOCS = [ICELAND]


# Determines if you should use a proxy or not.
# Examples:
proxies = {'http': '127.0.0.1:9150'}
#proxies = {}

# Fake using a regular browser to avoid HTTP 401/501 errors
user_agent = {'User-agent': 'Mozilla/5.0'}

# Plane list of area
planelist = []

# Text colors using ANSI escaping. Surely theres a better way to do this
class bcolors:
    ERRO = '\033[31m'
    WARN = '\033[91m'
    OKAY = '\033[32m'
    STOP = '\033[0m'

class Plane:
    interestOwners = ['DELTA AIR LINES INC']

    def __init__(self, webi, numb, call, latt, lonn, orig, dest, alti):
        self.webi = webi
        self.numb = numb
        self.call = call
        self.latt = latt
        self.lonn = lonn
        self.orig = orig
        self.dest = dest
        self.alti = alti
        self.owne = self.getowner()

    # Gets the owner of a plane
    def getowner(self):
        if self.numb is not '':

        #Select country
            if self.numb.startswith('C'):
                url = CA+self.numb

            if self.numb.startswith('N'):
                url = US+self.numb
                req = requests.get(url)
                if req.status_code is 200:
                    print(u'\u2713 ' + url)
                    with open('./html/'+self.numb, 'w') as fil:
                        fil.write(req.text)
                        soup = BeautifulSoup(req.text, 'html.parser')
                        own = soup.find('span', {'id':'content_lbOwnerName'})
                        if own is not None:
                            return own.text
                        else:
                            pass
                else:
                    print(u'\u274C ' + str(req.status_code) + " " + url)

            elif self.numb.startswith('G'):
                url = UK+self.numb[2:]
                req = requests.get(url)
                if req.status_code is 200:
                    print(u'\u2713 ' + url)
                    soup = BeautifulSoup(req.text, 'html.parser')
                    own = soup.find('span', {'id':'currentModule_currentModule_RegisteredOwners'}).contents[0].strip()
                    return own
                else:
                    print(u'\u274C ' + str(req.status_code) + " " + url)

            elif self.numb.startswith('TF'):
                url = IS+self.numb
                req = requests.get(url)
                if req.status_code is 200:
                    print(u'\u2713 ' + url)
                    soup = BeautifulSoup(req.text, 'html.parser')
                    own = soup.find('li', {'class':'owner'})
                    if own is not None:
                        print(own.contents[2].strip())
                        return own.text
                else:
                    print(u'\u274C ' + str(req.status_code) + " " + url)

        return None


    def isInteresting(self):
        if self.owne in plane.interestOwners:
            return True
        else:
            return False


def getjson(jsonurl):
    req = requests.get(jsonurl, headers=user_agent, proxies=proxies)
    if req.status_code is 200:
        print(bcolors.OKAY)
        print('✓ ' + str(req.status_code) + ' ' + jsonurl)
        print(bcolors.STOP)
        try:
            json = req.json()
        except:
            print('Error while decoding json')
        return json
    else:
        print(bcolors.ERRO)
        print('✖'+str(req.status_code) + ' ' + jsonurl)
        print(bcolors.STOP)
        return None


# This method gets plane from an area and puts them in a list
def getareaplanes(latmin, latmax, lonmin, lonmax):
    location = str(latmax)+'.00,'+str(latmin)+'.00,'+str(lonmax)+".00,"+str(lonmin)+".00"
    j = getjson(flightradar+location)
    if j is not None:
        print(len(j))
        for planeID in j:
             # Filter out non-plane results
             if planeID == 'full_count' or planeID == 'version' or planeID == 'stats':
                 pass
             else:
                 planelist.append(Plane(planeID, j[planeID][9], j[planeID][16], j[planeID][1], j[planeID][2], j[planeID][11], j[planeID][12], j[planeID][4]))

def getpath(plane):
    j = getjson('http://data-live.flightradar24.com/clickhandler/?version=1.5&flight='+plane)
    if j is not None:
        path = j['trail']

def getInterestingPlaces():

    # Get news feed about things that could require a plane flyover
    # Wildfire, traffic accidents, police intervention, natural disasters, etc.
    return None



while True:
    RANDLOC = [rand_lat, rand_lat - 2, rand_long, rand_long - 2 ]
    LOCS.append(RANDLOC)
    for place in LOCS:
        getareaplanes(place[1], place[0], place[3], place[2])

    for plane in planelist:
        if plane.owne is not None:
            print(plane.owne)
