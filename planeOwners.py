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
import argparse
from bs4 import BeautifulSoup
from threading import Thread
import time

from libs.planes import *
from libs.display import *

# Data sources
flightradar = 'http://data.flightradar24.com/zones/fcgi/feed.js?bounds='
planefinder = 'https://planefinder.net/endpoints/update.php?callback=planeDataCallback&faa=1&routetype=iata&cfCache=true&bounds=37%2C-80%2C40%2C-74&_=1452535140'
flight_data_src = 'http://data-live.flightradar24.com/clickhandler/?version=1.5&flight='
# News source
AP = 'Associated Press'
AFP = 'Agence France Presse'
AP_KEY = 'API KEY HERE'

# Define areas to lookup.
CH_AREA = Area(Coordinates(48.5 , 4.5), Coordinates(45,10))


# Determines if you should use a proxy or not.
# Examples:
#proxies = {'http': '127.0.0.1:9150'}
proxies = {}

# Fake using a regular browser to avoid HTTP 401/501 errors
user_agent = {'User-agent': 'Mozilla/5.0'}


# Text colors using ANSI escaping. Surely theres a better way to do this
class bcolors:
    ERRO = '\033[31m'
    WARN = '\033[91m'
    OKAY = '\033[32m'
    STOP = '\033[0m'

def getjson(jsonurl):
    req = requests.get(jsonurl, headers=user_agent, proxies=proxies)
    print(req.url)
    if req.status_code is 200:
        try:
            json = req.json()
        except:
            print('Error while decoding json')
        return json
    else:
        print(bcolors.ERRO)
        print('ERROR '+str(req.status_code) + ' ' + jsonurl)
        print(bcolors.STOP)
        raise ConnectionError


# This method gets plane from an area and puts them in a list
def fetch_planes_from_area(coords_1, coords_2):
    planelist = []
    location = str(coords_2.latitude)+'.00,'+str(coords_1.latitude)+'.00,'+str(coords_1.longitude)+'.00,'+str(coords_2.longitude)+'.00'
    try:
        j = getjson(flightradar+location)
    except Exception as e:
        raise e

    if j is not None:
        for planeID in j:
            # Filter out non-plane results
            if planeID == 'full_count' or planeID == 'version' or planeID == 'stats':
                pass
            else:
                 p = Plane(planeID, j[planeID][9], j[planeID][16], j[planeID][1], j[planeID][2], j[planeID][11], j[planeID][12], j[planeID][4])
                 planelist.append(p)
    return planelist

def getInterestingPlaces():
    # Get news feed about things that could require a plane flyover
    # Wildfire, traffic accidents, police intervention, natural disasters, etc.
    return None

def main():
    parser  = argparse.ArgumentParser()
    parser.add_argument("--proxy", help="Use proxy address", type=str)
    parser.add_argument("--interactive", action="store_true")
    require_group = parser.add_mutually_exclusive_group(required=True)
    require_group.add_argument("--country", help="country code", type=str)
    require_group.add_argument("--coords", help="longitude coord in decimal format", nargs=4, type=float)
    args    = parser.parse_args()

    # List of places to visit
    areas = []
    corner_1 = None
    corner_2 = None
    # Convert coords to coords objects
    if args.coords:
        corner_1 = Coordinates(args.coords[0], args.coords[1])
        corner_2 = Coordinates(args.coords[2], args.coords[3])
    elif args.country:
        if args.country == 'CH':
            areas.append(CH_AREA)
        if args.country == 'IS':
            areas.append(LAT_LON_IS)
        if args.country == 'US':
            areas.append(LAT_LON_US)
    else:
        print('Nothing has really been specified, wtf dude ?')

    while True:
        if args.interactive:
            disp = Display()
            plane_list = fetch_planes_from_area(corner_1, corner_2)
            disp.update(planelist)
        else:
            plane_list = fetch_planes_from_area(corner_1, corner_2)
            for plane in plane_list:
                if plane.owner is not None:
                    print(plane.numb)
                    print(plane.owner)

if __name__ == "__main__":
        main()
