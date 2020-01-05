# -*- coding: utf-8 -*-
from .geoloc import *
import requests
from bs4 import BeautifulSoup
import json

# Decoders for countries here
from .agencies import * 

class Owner:
    def __init__(self, name, street, city, zip_code, country):
        self.name = name
        self.street = street
        self.city = city
        self.zip_code = zip_code
        self.country = country

    def __repr__(self):
        return "%s %s %s %s %s" % (self.name, self.street, self.city, self.zip_code, self.country)

    def __str__(self):
        return self.__repr__()

# TODO: move location stuff to another class "realtime plane"
class Craft:
    def __init__(self, webi, numb, call, latitude, longitude, craft_type=None, origin=None, destination=None, altitude=None):
        self.coords = Coordinates(latitude, longitude)
        self.webi = webi
        self.numb = numb
        self.call = call
        self.origin = origin
        self.destination = destination
        self.altitude = altitude	
        self.owner = self.get_owner()
		

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s\t%s\t%s\t%s\t%s" % (self.numb, self.call, self.coords, self.altitude, str(self.owner))

    def get_owner(self):
        if self.numb.startswith('HB-'):
            return CH(self.numb)
        elif self.numb.startswith('F-'):
            return FR(self.numb)
        elif self.numb.startswith('TF'):
            return IS(self.numb)
        elif self.numb.startswith('N'):
            return US(self.numb)
        elif self.numb.startswith('OO-'):
            return BE(self.numb)
        elif self.numb.startswith('OE-'):
            return AT(self.numb)
        elif self.numb.startswith('SE-'):
            return SW(self.numb)
        elif self.numb.startswith('OK-'):
            return CZ(self.numb)
        elif self.numb.startswith('G-'):
            return UK(self.numb)
        elif self.numb.startswith('EI-'):
            return IE(self.numb)
        elif self.numb.startswith('M-'):
            return IM(self.numb)
        elif self.numb.startswith('I-'):
            return IT(self.numb)
        elif self.numb.startswith('C-'):
            return CA(self.numb)
        elif self.numb.startswith('YR-'):
            return RO(self.numb)
        elif self.numb.startswith('VH-'):
            return AU(self.numb)
        elif self.numb.startswith('9A-'):
            return HR(self.numb)
        else:
            if self.numb != '':
               # r = requests.get(f'https://commons.wikimedia.org/wiki/Category:{self.numb}_(aircraft)')
               # if r.status_code == 200:
               # 	raise NotImplementedError(f'Agency not implemented. Try wikimedia commons: https://commons.wikimedia.org/wiki/Category:{self.numb}_(aircraft)')
               # else:
               raise NotImplementedError(f'Agency not implemented for {self.numb}')
            raise Exception('No tail number found')


    def get_path(self):
        return []
        #j = getjson(flight_data_src+self.name)

class RT_craft(Craft):
	pass
