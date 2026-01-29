#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf8
# Python script to lookup plane owner's in a particular geographic area using public data from planefinder.net and the federal aviation agency.
# If a particular owner is found, the plane infos are shown


# TODO
# Implement ADS-B
# Implement news source, location API, and search based on location name
import os
import sys
import requests
import random as rand
import json
import logging
import argparse
import time
import socket
import csv

from registers import *
from tail_to_register import *
from investigation_authorities import *
from monitor import monitor
from wiki_api import search_wiki_commons
from opensky_api import OpenSkyApi
from bs4 import BeautifulSoup
from threading import Thread


# Data sources
flightradar = 'http://data.flightradar24.com/zones/fcgi/feed.js?bounds='
planefinder = 'https://planefinder.net/endpoints/update.php'\
                    '?callback=planeDataCallback&faa=1&routetype=iata&cfCache=true'\
                    '&bounds=37%2C-80%2C40%2C-74&_=1452535140'
flight_data_src = 'http://data-live.flightradar24.com/clickhandler/?version=1.5&flight='


# News source
AP = 'Associated Press'
AFP = 'Agence France Presse'
AP_KEY  = 'API KEY HERE'


# Docker
DOCKER_HOST = '127.0.0.1'
DOCKER_PORT = 3001


# GLOBAL VARIABLES
verbose = False


# Text colors using ANSI escaping. Surely theres a better way to do this
class bcolors:
    ERRO = '\033[31m'
    WARN = '\033[93m'
    OKAY = '\033[32m'
    STOP = '\033[0m'


class NoIntelException(Exception):
    """ Raised when no information has been found in registers"""
    pass 


def printok(str):
    return print(bcolors.OKAY+'[OK]'+bcolors.STOP+' {}'.format(str))


def printko(str):
    return print(bcolors.ERRO+'[KO]'+bcolors.STOP+' {}'.format(str))


def printwarn(str):
    return print(bcolors.WARN+'[WRN]'+bcolors.STOP+' {}'.format(str))


def printverbose(str):
    if verbose:
        print(str)
    else:
        pass


def quit():
    print('bye then !\nIf you wish, you can buy me a coffee at https://ko-fi.com/arctos')
    return 0


def check_config():
    check_config_file_coherence = False
    check_docker_connectivity = False

    print("[*] Checking config")

    # Tests connectivity to the docker container
    timeout_seconds=1
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout_seconds)
    result = sock.connect_ex((DOCKER_HOST, DOCKER_PORT))
    sock.close()
    docker_result = result

    if result == 0:
        printok("Parsr docker container is reachable")
        return True
    else:
        printwarn("Could not contact docker container. PDF registery lookup will not work.")
        return False



def getInterestingPlaces():
    # Get news feed about things that could require a plane flyover
    # Wildfire, traffic accidents, police intervention, natural disasters, etc.
    return None

def intel_from_ICAO(icao):
    """
    Gather intel starting with icao number
    """
    return None


def opensky(tail_n):
    print("[*] Gathering infos from opensky network database. This can take some time")
    headers = {
            'User-Agent': 'AVOSINT - CLI tool to gather aviation OSINT.'\
                    'Infos and contact: https://github.com/n0skill/AVOSINT'
    }

    if os.path.exists('/tmp/opensky.cache') \
            and os.stat("/tmp/opensky.cache").st_size != 0:
        print('[*] Opensky cache exists. Do not download again')
    else:
        r = requests.get(
                'https://opensky-network.org/datasets/metadata/aircraftDatabase.csv',
                stream=True,
                headers=headers)

        if r.status_code == 200:
            with open('/tmp/opensky.cache', 'wb') as f: 
                total_l = int(r.headers.get('content-length'))
                dl = 0
                for data in r.iter_content(chunk_size=8192*4):
                    dl += len(data)
                    f.write(data)
                    print('\r[*] Downloading {:2f}'.format((dl/total_l)*100), end='')
                print('\r[*] Done loading !')
        else:
            printwarn(r.status_code)

    with open('/tmp/opensky.cache', 'r') as f:
        parsed_content = csv.reader(f)
        for line in parsed_content:
            if tail_n in line:
                # Aircraft infos
                icao = line[0]
                manufacturer = line[3]
                msn = line[6] if line[6] else ''
                # Owner infos
                owner = line[13]
                return Aircraft(
                    tail_n,
                    icao=icao,
                    manufacturer=manufacturer,
                    msn=msn), Owner(owner)
        return None


def intel_from_tail_n(tail_number):
    """
    Gather intel from tail number
    1) Owner information
    2) Last changes of ownership
    3) Last known position
    """

    wiki_infos = None
    owner_infos = None
    aircraft_infos = None
    os_aircraft = None
    os_owner = None

    print("[*] Getting intel for tail number {}".format(tail_number))

    # Step 1 - Gather ownership information
    # Cleaning up tail for register lookup according to config file
    tail_number = tail_number.upper()
    if '-' in tail_number:
        tail_prefix = tail_number.split('-')[0]+'-'
    else:
        tail_prefix = tail_number[0]

    # Gather all information together

    # First, from official registers
    try:
        owner_infos, aircraft_infos = tail_to_register_function[tail_prefix](tail_number)    
    except Exception as e:
        printverbose("[!] Exception while calling tail_to_register: {}".format(e))

    # Opensky network
    try:
        results_os = opensky(tail_number)
        if results_os is not None:
            os_aircraft, os_owner = results_os
            icao = os_aircraft.icao.lower()
            api = OpenSkyApi()
            s = api.get_states(icao24=icao)
            try:
                if s is not None and len(s.states) > 0:
                    last_lat = (s.states)[0].latitude
                    last_lon = (s.states)[0].longitude
                    os_aircraft.latitude = last_lat
                    os_aircraft.longitude = last_lon
            except Exception as e:
                printko(e)
        else:
            printverbose("[!] Aircraft not found in opensky. returns None")
    except Exception as e:
        printko("[!] Exception while calling opensky: {}".format(e))


    # Wikipedia infos
    try:
        wiki_infos = search_wiki_commons(tail_number)
    except Exception as e:
        printwarn(e)
    # Last changes of ownership
    # TODO

    # Detailled info (pictures etc)
    # TODO

    # Merge infos and return them
    try:
        if aircraft_infos is not None and os_aircraft is not None:
            for attr, value in aircraft_infos.__dict__.items():
                if value is None and getattr(os_aircraft, attr) is not None:
                    setattr(aircraft_infos, attr, getattr(os_aircraft, attr))
        else:
            aircraft_infos = os_aircraft

    except Exception as e:
        printko(e)

    return owner_infos, aircraft_infos, wiki_infos


def main():
    # 1 - Check OSINT from ICAO
    # 2 - Check OSINT from tail number
    # 3 - Tool to convert icao to tail number
    parser  = argparse.ArgumentParser()
    parser.add_argument("--action", 
            help="Action to perform ('ICAO', 'tail', 'convert')",
            type=str, required=True)
    parser.add_argument('--tail-number',
            help='Tail number to lookup')
    # Optional arguments
    parser.add_argument("--icao",
            help="ICAO code to retrieve OSINT for", required=False)
    parser.add_argument("--config", 
            help="Config file", type=str)
    parser.add_argument("--proxy", 
            help="Use proxy address", type=str)
    parser.add_argument("--interactive", 
            action="store_true")
    parser.add_argument("--verbose",
            action="store_true")

    require_group = parser.add_mutually_exclusive_group(required=False)
    require_group.add_argument("--country", help="country code", type=str)
    require_group.add_argument(
            "--coords", 
            help="longitude coord in decimal format",
            nargs=4,
            type=float)

    args = parser.parse_args()

    # For storing intel recieved
    owner_infos = None
    aircraft_infos = None
    incident_reports = None
    wiki_infos = None
    status = None
    if not args.action:
        print("[*] No action was specified. Quit.")
        return
    else:
        if check_config() == False:
            printwarn("Not all check passed. Usage may be degraded")
        else:
            printok("All checks passed")
        
        action      = args.action
        tail_number = args.tail_number
        icao        = args.icao
        verbose     = args.verbose

        while action != 'quit':
            if action == "ICAO":
                try:
                    intel_from_ICAO(icao)
                except Exception as e:
                    status = 'ActionICAOException'
            elif action == "tail":
                try:
                    while tail_number == None:
                        tail_number = input("Enter tail number to lookup: ")
                    owner_infos, aircraft_infos, wiki_infos = intel_from_tail_n(tail_number)
                    incident_reports                        = search_incidents(tail_number, args.verbose)
                except Exception as e:
                    status = 'IncidentSearchException'

                status = 'Done'
            elif action == "convert":
                convert_US_ICAO_to_tail()
                status = 'Done'
            elif action == "monitor":
                if args.verbose == False:
                    os.system('clear')
                print("[*] Monitor aircraft mode")
                if icao is None:
                    icao = input("Enter icao number: ")
                monitor(icao)



            # Exits context (deselection of tail_numer or ICAO etc)
            elif action == 'exit':
                tail_number     = None
                owner_infos     = None
                aircraft_infos  = None
                status          = 'Waiting for action'
            else:
                print("[!] Unknown action. Try again")
                action = input("Enter valid action [ICAO, tail, convert, monitor, exit, quit]")

            # Print retrieved intel
            if args.verbose == False:
                os.system('clear')
            print("==========================================")
            print("Current Status: "+bcolors.OKAY+"[{}]".format(status)+bcolors.STOP)
            print("Last action: {}".format(action))
            print("Current tail: {}".format(tail_number))
            print("==========================================")
            print("✈️ Aircraft infos:")
            print(aircraft_infos)
            print("🧍 Owner infos")
            print(owner_infos)

            if incident_reports is not None:
                print("💥 Incident reports")
                print("\t{}".format(incident_reports))

            if wiki_infos:
                print("📖 Wikipedia informations")
                print("\t{}".format(wiki_infos))

            tail_number     = None
            owner_infos     = None
            aircraft_infos  = None
            action          = input('New Action [ICAO, tail,'\
                    'convert, monitor, exit, quit] ({}):'\
                    .format(tail_number))

        quit() 

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        quit()
