# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
from geoloc import Coordinates

# Decoders for countries here

class Aircraft:
    def __init__(self, tail_n, msn=None, call=None, \
            latitude=None, longitude=None, craft_type=None, \
            origin=None, destination=None, altitude=None, manufacturer=None, icao=None,notes=None):

        self.tail_n         = tail_n
        self.msn            = msn
        self.call           = call
        self.origin         = origin
        self.manufacturer   = manufacturer
        self.destination    = destination
        self.altitude       = altitude	
        self.latitude       = latitude
        self.longitude      = longitude
        self.icao           = icao  
        self.notes          = notes


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return """
        Manufacturer/Type: %s
        Manufacturer Serial Number: %s
        Tail Number: %s
        Call Sign: %s
        Last known position: %s
        Last known altitude: %s
        
        Notes: 
        %s
        """ % (self.manufacturer, self.msn, self.tail_n, self.call, (self.latitude, self.longitude), self.altitude, self.notes)

    def get_path(self):
        return []
        #j = getjson(flight_data_src+self.name)

class RT_craft(Aircraft):
	pass
