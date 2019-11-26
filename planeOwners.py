#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AVOSINT - Aviation Open Source Intelligence Tool
# A complete tool to search Aviation-related OSINT from sources such as
# 1) Online live aviation maps
# 2) Radio signals (ADSB via SDR)
# 3) Official aircraft registeries

# As of now, this tools supports registeries from
# The United States of America
# The United Kingdom
# Switzerland
# France
# Iceland
# Austria

# Python script to lookup plane owner's in a particular geographic area using public data from planefinder.net and the federal aviation agency.


# TODO
# Implement ADS-B
# Add support for multiple countries registeries

import requests
import random as rand
import json
import logging
import argparse
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing.pool import ThreadPool
import time
from subprocess import Popen
from libs.planes import *
from libs.display import *
from libs.geoloc import *

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
	if req.status_code is 200:
		try:
			json = req.json()
			return json
		except:
			print('Error while decoding json')
	else:
		print(bcolors.ERRO)
		print('ERROR '+str(req.status_code) + ' ' + jsonurl)
		print(bcolors.STOP)
		raise ConnectionError


# This method gets plane from an area and puts them in a list
def fetch_planes_from_area(coords_1, coords_2):
	planelist = []
	if coords_2 is not None and coords_1 is not None:
		location = str(coords_2.latitude)+','+str(coords_1.latitude)+','+str(coords_1.longitude)+','+str(coords_2.longitude)
		try:
			j = getjson(flightradar+location)
			if len(j) > 0:
				for planeID in j:
					# Filter out non-plane results
					if planeID == 'full_count' or planeID == 'version' or planeID == 'stats':
						pass
					else:
						p = Plane(planeID, 
								j[planeID][9],
								j[planeID][16],
								j[planeID][1], 
								j[planeID][2],	
								j[planeID][11],
								j[planeID][12],
								j[planeID][4])
						planelist.append(p)
		except Exception as e:
			raise e
	else:
		location = None
		print("Location is none")
		return []
	return planelist

def getInterestingPlaces():
# Get news feed about things that could require a plane flyover
# Wildfire, traffic accidents, police intervention, natural disasters, etc.
		return None

def main():
	plane_list = []
	parser  = argparse.ArgumentParser()
	pool = ThreadPool(processes=1)
	parser.add_argument("--proxy", help="Use proxy address", type=str)
	parser.add_argument("--interactive", action="store_true")
	parser.add_argument("--debug", action="store_true")
	
	require_group = parser.add_mutually_exclusive_group(required=True)
	require_group.add_argument("--country", help="country code", type=str)
	require_group.add_argument("--coords", help="longitude coord in decimal format", nargs=4, type=float)
	require_group.add_argument("--number", help="Specify plane number")
	require_group.add_argument("--sdr", help="Use sdr source instead", action="store_true")

	args    = parser.parse_args()
	corner_1 = None
	corner_2 = None

	if args.debug:
		FLG_DEBUG = True
		flg_lookup = False

	if args.number is not None:
		p = Plane(None, args.number, None, None, None)
		print(p.owner)

	elif args.coords:
		corner_1 = Coordinates(args.coords[0], args.coords[1])
		corner_2 = Coordinates(args.coords[2], args.coords[3])
		flg_lookup = True
	elif args.country:
		flg_lookup = True
		if args.country.upper() == 'CH':
			corner_1 = CH_AREA[0]
			corner_2 = CH_AREA[1]
		if args.country == 'IS':
			corner_1 = IS_AREA[0]
			corner_2 = IS_AREA[1]
		if args.country == 'US':
			corner_1 = US_AREA[0]
			corner_2 = US_AREA[1]

	elif args.sdr:
		Popen(["dump1090", "--net", "--quiet"])
		while True:
			time.sleep(2)
			j = getjson('http://127.0.0.1:8080/dump1090/data.json')
			for i in j:
				hexn = int(i['hex'], 16)
				if hexn > 0xA00001 and hexn < 0xADF669: # If american, we know how to convert back to tail number
					print(icao_to_tail(hexn))

# get json

	if flg_lookup:
		disp = Display()
		while True:
			if args.interactive:
				async_result = pool.apply_async(fetch_planes_from_area, (corner_1, corner_2))
				disp.loading()
				plane_list = async_result.get()
				disp.update(plane_list)
			else:
				plane_list = fetch_planes_from_area(corner_1, corner_2)
				print(plane_list)
				for plane in plane_list:
					if plane.owner is not None:
						print(plane.numb)
						print(plane.owner)
			time.sleep(0.2)

if __name__ == "__main__":
	main()
