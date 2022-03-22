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
from bs4 import BeautifulSoup
from threading import Thread
import time
import socket
from wiki_api import search_wiki_commons

from registers import *
from tail_to_register import *
from investigation_authorities import *
from monitor import monitor


# Data sources
flightradar = 'http://data.flightradar24.com/zones/fcgi/feed.js?bounds='
planefinder = 'https://planefinder.net/endpoints/update.php?callback=planeDataCallback&faa=1&routetype=iata&cfCache=true&bounds=37%2C-80%2C40%2C-74&_=1452535140'
flight_data_src = 'http://data-live.flightradar24.com/clickhandler/?version=1.5&flight='


# News source
AP      = 'Associated Press'
AFP     = 'Agence France Presse'
AP_KEY  = 'API KEY HERE'


# Docker
DOCKER_HOST = '127.0.0.1'
DOCKER_PORT = 3001


# Files 


# Hard-coded areas
#CH_AREA = [Coordinates(45,4.5), Coordinates(48.5 , 10)]
#IS_AREA = [Coordinates(62.76,-32.18), Coordinates(66.92, -3.5)]
#US_AREA = [Coordinates(0,0), Coordinates(0,0)]


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

   # if check_config_file_coherence \
   #         and check_docker_connectivity \
   #         and additional_check:
   #             return True


def getInterestingPlaces():
    # Get news feed about things that could require a plane flyover
    # Wildfire, traffic accidents, police intervention, natural disasters, etc.
    return None

def intel_from_ICAO():
    print("TODO GET ICAO INFO")
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
    print("[*] Getting intel for tail number {}".format(tail_number))

    # Step 1 - Gather ownership information

    # Cleaning up tail for register lookup according to config file
    tail_number = tail_number.upper()
    if '-' in tail_number:
        tail_prefix = tail_number.split('-')[0]+'-'
    else:
        tail_prefix = tail_number[0]

    if tail_prefix not in tail_to_register_function:
        raise NotImplementedError

    owner_infos, aircraft_infos = tail_to_register_function[tail_prefix](tail_number)


    # Wikipedia infos
    wiki_infos = search_wiki_commons(tail_number)
    # Last changes of ownership

    # Last known position

    # Detailled info (pictures etc)
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

    args    = parser.parse_args()

    # For storing intel recieved
    owner_infos         = None
    aicraft_infos       = None
    incident_reports    = None
    wiki_infos          = None
    status              = None
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

        while action != 'quit':
                if action == "ICAO":
                    try:
                        intel_from_ICAO(icao)
                    except Exception as e:
                        status = 'ActionICAOException'
                elif action == "tail":
                    try:
                        if tail_number == None:
                            tail_number = input("Enter tail number to lookup: ")
                        owner_infos, aircraft_infos, wiki_infos = intel_from_tail_n(tail_number)
                    except Exception as e:
                        status = 'ActionTailException'

                    try:
                        print("[*] Searching for incident reports ....")
                        incident_reports = \
                                search_incidents(tail_number, args.verbose)
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
                    print("Wikipedia informations")
                    print("\t{}".format(wiki_infos))

                tail_number     = None
                owner_infos     = None
                aircraft_infos  = None
                action = input('New Action [ICAO, tail, convert, monitor, exit, quit] ({}):'.format(tail_number))

            

if __name__ == "__main__":
    main()
