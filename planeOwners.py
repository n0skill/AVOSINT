#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import sys

# Data sources
flightradar = 'http://data.flightradar24.com/zones/fcgi/feed.js?bounds='
planefinder = 'https://planefinder.net/endpoints/update.php?callback=planeDataCallback&faa=1&routetype=iata&cfCache=true&bounds=37%2C-80%2C40%2C-74&_=1452535140'

# News source
AP = 'Associated Press'
AFP = 'Agence France Presse'
AP_KEY = 'API KEY HERE'


# Aviation agencies
AT = 'hhttps://www.austrocontrol.at/ta/OenflSucheEn?1-7.IFormSubmitListener-form'
US = 'http://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?MailProcess=1&nNumberTxt='
UK = 'http://publicapps.caa.co.uk/modalapplication.aspx?catid=1&pagetype=65&appid=1&mode=detailnosummary&fullregmark='
IS = 'http://www.icetra.is/aviation/aircraft/register?aq='
NL = 'http://www.newfoundland.nl/luchtvaartregister/user/en/luchtvaartuig.php?registratie='
BE = 'http://www.mobilit.fgov.be/bcaa/aircraft/search.jsf'
CA = 'http://wwwapps.tc.gc.ca/saf-sec-sur/2/ccarcs-riacc/RchSimpRes.aspx?cn=||&mn=||&sn=||&on=||&m=|'
CH = 'https://www.bazlwork.admin.ch/bazl-backend/lfr'

# Defines areas to lookup.
# Format:
# AREA = [maxlat, minlat, maxlon, minlon]

LAT_LON_LA = (35, 32, -115, -120)
LAT_LON_TX = (37, 25, -92, -106)
LAT_LON_NY = (41, 39, -72, -75)
LAT_LON_CH = [48.5 , 45, 4.5,12]
LAT_LON_IS = (66, 63, -27, -19)


# Determines if you should use a proxy or not.
# Examples:
#proxies = {'http': '127.0.0.1:9150'}
proxies = {}

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
class Owner:
    def __init__(self, name, street, streetn, zipCode, country):
        self.name = name
        self.street = street
        self.streetn= streetn
        self.zipCode = zipCode
        self.country = country

class Plane:
    interestOwners = ['DELTA AIR LINES INC'] # Example

    def __init__(self, webi, numb, call, latt, lonn, orig, dest, alti):
        self.webi = webi
        self.numb = numb
        self.call = call
        self.latt = latt
        self.lonn = lonn
        self.orig = orig
        self.dest = dest
        self.alti = alti
        self.owner = self.getowner()

    # Gets the owner of a plane
    def getowner(self):
        if self.numb is not '':

            #Select country


            # Afghanistan
            if self.numb.startswith('YA-'):
                pass
            # Albania
            if self.numb.startswith('ZA-'):
                pass

            # Algeria
            if self.numb.startswith('7T-'):
                pass

            # Andorra
            if self.numb.startswith('C3-'):
                pass

            # Angola
            if self.numb.startswith('D2-'):
                pass

            # Anguilla
            if self.numb.startswith('VP-A'):
                pass

            # Antigua and Barbuda
            if self.numb.startswith('V2-'):
                pass

            # Argentina
            if self.numb.startswith('LV-'):
                pass
            if self.numb.startswith('LQ-'):
                pass
            # Armenia
            if self.numb.startswith('EK-'):
                pass

            # Aruba
            if self.numb.startswith('P4-'):
                pass

            # Australia
            if self.numb.startswith('VH-'):
                pass

            # Austria
            if self.numb.startswith('OE-'):

                headers = {
                        'Host': 'www.austrocontrol.at',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Referer': 'https://www.austrocontrol.at/ta/OenflSucheEn?1',
                        'Connection': 'keep-alive',
                        }

                data = {
                        'id3_hf_0': '',
                        'txtKennzeichen': 'aae',
                        'txtOrdnungszahl': '',
                        'txtHersteller': '',
                        'txtBaumuster': '',
                        'cmbLfzart': '',
                        'txtSeriennummer': '',
                        'radStartgewicht': '1',
                        'txtStartgewicht': '',
                        'txtHalter': '',
                        'p::submit': ''
                        }

                req = requests.post('https://www.austrocontrol.at/ta/OenflSucheEn?1-7.IFormSubmitListener-form', headers=headers, data=data)
                print(req.status_code)
                soup = BeautifulSoup(req.text, 'html.parser')
                table = soup.find('table', {'id':'resultTable'})
                tds = table.findAll('td')
                t = None
                for t in tds:
                    pass
                t = t.stripped_strings
                l = list(t)
                addr = l[1].split(',')
                zip = addr[0].split()[0]
                return Owner(l[0], addr[1], addr[1], zip, l[2])

            # Azerbaijan
            if self.numb.startswith('4K--'):
                pass

            # Bahamas
            if self.numb.startswith('C6-'):
                pass

            # Bahrain
            if self.numb.startswith('A9C-'):
                pass

            # Bangladesh
            if self.numb.startswith('S2'):
                pass

            # Barbaros
            if self.numb.startswith('8P-'):
                pass

            # Belarus
            if self.numb.startswith('EW-'):
                pass


            #Netherlands
            if self.numb.startswith('PH-'):
                req = requests.get(NL+self.numb)
                soup = BeautifulSoup(req.text, 'html.parser')

            # Canada
            if self.numb.startswith('G-C'):
                url = CA+self.numb

            # Switzerland
            if self.numb.startswith('HB-'):
                headers = {
                            'Origin': 'https://www.bazlwork.admin.ch',
                            'Content-Type': 'application/json;charset=UTF-8',
                            'Accept': 'application/json, text/plain, */*',
                            'Referer': 'https://www.bazlwork.admin.ch/bazl/',
                            'Connection': 'keep-alive',
                            }

                data = '{"page_result_limit":10,"current_page_number":1,"sort_list":"registration","totalItems":1,"query":{"registration":"'+str(self.numb)+'"},"language":"en","tab":"basic"}'

                req = requests.post(CH, headers=headers, data=data)

                if req.status_code is 200:
                    print(u'\u2713 ' + req.url)
                    json_obj = req.json()
                    for i in json_obj:
                        own_operator = str(i['ownerOperators'][0]['ownerOperator'].encode('utf-8'))
                        own_bil_addr = str(i['ownerOperators'][0]['billingAddress'])
                        own_addr     = i['ownerOperators'][0]['address']
                        print(own_addr)
                        return Owner(own_operator, own_addr['street'], own_addr['streetNo'], own_addr['zipCode'], own_addr['country'])

            # USA
            if self.numb.startswith('N'):
                url = US+self.numb
                req = requests.get(url)
                if req.status_code is 200:
                    print(u'\u2713 ' + req.url)
                    with open('./html/'+self.numb, 'w') as fil:
                        txt =req.text.encode('utf8')
                        fil.write(txt)
                        soup = BeautifulSoup(req.text, 'html.parser')
                        name = soup.find('span', {'id':'content_lbOwnerName'}).text
                        street = soup.find('span', {'id':'content_lbOwnerStreet'}).text
                        street2= soup.find('span', {'id':'content_lbOwnerStreet'}).text
                        city   = soup.find('span', {'id':'content_lbOwnerCity'}).text
                        state  = soup.find('span', {'id':'content_lbOwnerState'}).text
                        zip    = soup.find('span', {'id':'content_lbOwnerZip'}).text
                        return Owner(name, street, str(city + ', ' + state), zip, 'United States')
                else:
                    print(u'\u274C ' + str(req.status_code) + " " + url)

            # UK
            elif self.numb.startswith('G-E'):
                url = UK+self.numb[2:]
                req = requests.get(url)
                if req.status_code is 200:
                    print(u'\u2713 ' + req.url)
                    soup = BeautifulSoup(req.text, 'html.parser')
                    own = soup.find('span', {'id':'currentModule_currentModule_RegisteredOwners'}).contents
                    return Owner(own[0], own[4], own[6], own[8], 'Great Britain')
                else:
                    print(u'\u274C ' + str(req.status_code) + " " + req.url)

            # Iceland
            elif self.numb.startswith('TF'):
                url = IS+self.numb
                req = requests.get(url)
                if req.status_code is 200:
                    print(u'\u2713 ' + req.url)
                    soup = BeautifulSoup(req.text, 'html.parser')
                    own = soup.find('li', {'class':'owner'})
                    if own is not None:
                        print(own.contents[2].strip())
                        return None
                else:
                    print(u'\u274C ' + str(req.status_code) + " " + url)
                print(self.numb)

            # Germany
            elif self.numb.startswith('D-'):
                pass
            else:
                print(self.numb)
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


def main(argv):
    coords = [] # List of places to look up
    while True:
        if argv[1] == 'CH':
            coords.append(LAT_LON_CH)
        if argv[1] == 'IS':
            coords.append(LAT_LON_IS)
        for place in coords:
            getareaplanes(place[1], place[0], place[3], place[2])
            for plane in planelist:
                if plane.owner is not None:
                    print(plane.numb)
                    print(plane.owner.name)
                    print(plane.owner.street)
                    print(plane.owner.streetn)
                    print(plane.owner.zipCode)
                    print(plane.owner.country)
                    print('\r')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv)
    else:
        main()
