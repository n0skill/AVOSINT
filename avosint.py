#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf8
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
from libs.registers import *

# Data sources
flightradar = 'http://data.flightradar24.com/zones/fcgi/feed.js?bounds='
planefinder = 'https://planefinder.net/endpoints/update.php?callback=planeDataCallback&faa=1&routetype=iata&cfCache=true&bounds=37%2C-80%2C40%2C-74&_=1452535140'
flight_data_src = 'http://data-live.flightradar24.com/clickhandler/?version=1.5&flight='


# News source
AP = 'Associated Press'
AFP = 'Agence France Presse'
AP_KEY = 'API KEY HERE'

# Hard-coded areas

CH_AREA = [Coordinates(45,4.5), Coordinates(48.5 , 10)]
IS_AREA = [Coordinates(62.76,-32.18), Coordinates(66.92, -3.5)]
US_AREA = [Coordinates(0,0), Coordinates(0,0)]


# Determines if you should use a proxy or not.
# Examples:
#proxies = {'http': '127.0.0.1:9150'}
proxies = {}

# Fake using a regular browser to avoid HTTP 401/501 errors
user_agent = {'User-agent': 'Mozilla/5.0'}

# GLOBAL VARIABLES
FLG_DEBUG = False

# Text colors using ANSI escaping. Surely theres a better way to do this
class bcolors:
    ERRO = '\033[31m'
    WARN = '\033[91m'
    OKAY = '\033[32m'
    STOP = '\033[0m'


def test_connection_f24():
    req = requests.get('')

def getjson(jsonurl):
    req = requests.get(jsonurl, headers=user_agent, proxies=proxies)
    if FLG_DEBUG:
        print(req.url)
    if req.status_code == 200:
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
    print(coords_1, coords_2)
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

def intel_from_ICAO():
    print("TODO GET ICAO INFO")

def intel_from_tail_n(tail_number):
    """
    Gather intel from tail number
    1) Owner information
    2) Last changes of ownership
    3) Last known position
    """
    print("[*] Getting intel for tail number {}".format(tail_number))

    tail_number = tail_number.upper()
    # Step 1 - Gather ownership information

    if tail_number.startswith('HB-'):
        owner_infos = CH(tail_number)
    elif tail_number.startswith('F-'):
        owner_infos = FR(tail_number)
    elif tail_number.startswith('TF'):
        owner_infos = IS(tail_number)
    elif tail_number.startswith('N'):
        owner_infos = US(tail_number)
    elif tail_number.startswith('OO-'):
        owner_infos = BE(tail_number)
    elif tail_number.startswith('OE-'):
        owner_infos = AT(tail_number)
    elif tail_number.startswith('SE-'):
        owner_infos = SW(tail_number)
    elif tail_number.startswith('OK-'):
        owner_infos = CZ(tail_number)
    elif tail_number.startswith('G-'):
        owner_infos = UK(tail_number)
    elif tail_number.startswith('EI-'):
         owner_infos = IE(tail_number)
    elif tail_number.startswith('M-'):
         owner_infos = IM(tail_number)
    elif tail_number.startswith('I-'):
         owner_infos = IT(tail_number)
    elif tail_number.startswith('C-'):
         owner_infos = CA(tail_number)
    elif tail_number.startswith('YR-'):
         owner_infos = RO(tail_number)
    elif tail_number.startswith('YU-'):
         owner_infos = RS(tail_number)
    elif tail_number.startswith('VH-'):
         owner_infos = AU(tail_number)
    elif tail_number.startswith('9A-'):
         owner_infos = HR(tail_number)
    elif tail_number.startswith('9V-'):
         owner_infos = SG(tail_number)
    elif tail_number.startswith('ZK-'):
         owner_infos = NZ(tail_number)
    elif tail_number.startswith('PP-') or tail_number.startswith('PR-') or tail_number.startswith('PS-') or tail_number.startswith('PT-') or tail_number.startswith('PU-'):
         owner_infos = BR(tail_number)
    elif tail_number.startswith('D-'):
         owner_infos = DE(tail_number)
    elif tail_number.startswith('UR-'):
         owner_infos = UA(tail_number)
    elif tail_number.startswith('HS-') or tail_number.startswith('U-'):
         owner_infos = TH(tail_number)
    elif tail_number.startswith('OY-'):
         owner_infos = DK(tail_number)
    elif tail_number.startswith('YL-'):
         owner_infos = LV(tail_number)
    elif tail_number.startswith('E7-'):
         owner_infos = BA(tail_number)
    else:
        if tail_number != '':
            raise Exception('[!] Tail number unknown or country not implemented')

    # Display information
    print("[*] Infos from registry\n", owner_infos)

def main():
    # 1 - Check OSINT from ICAO
    # 2 - Check OSINT from tail number
    # 3 - Tool to convert icao to tail number

    parser  = argparse.ArgumentParser()

    parser.add_argument("--action", help="Action to perform ('ICAO', 'tail', 'convert'", type=str)
    parser.add_argument('--tail-numbers', nargs='+', help='Tail numbers to lookup', required=True)
    parser.add_argument("--icao", help="ICAO code to retrieve OSINT for")
    parser.add_argument("--proxy", help="Use proxy address", type=str)
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--debug", action="store_true")
    require_group = parser.add_mutually_exclusive_group(required=False)
    require_group.add_argument("--country", help="country code", type=str)
    require_group.add_argument(
            "--coords", 
            help="longitude coord in decimal format",
            nargs=4,
            type=float)
    args    = parser.parse_args()
    corner_1 = None
    corner_2 = None

    if not args.action:
        print("[*] No action was specified. Quit.")
        return
    else:
        if args.action == "ICAO":
            intel_from_ICAO(args.ICAO)
        elif args.action == "tail":
            for tail_number in args.tail_numbers:
                intel_from_tail_n(tail_number)
        elif args.action == "convert":
            convert_US_ICAO_to_tail()
        else:
            print("[!] Unknown action. Quit.")
            return

if __name__ == "__main__":
        main()
