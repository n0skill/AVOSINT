# -*- coding: utf-8 -*-
from .geoloc import *
import requests
from bs4 import BeautifulSoup
import json

# Decoders for countries here
from .agencies import CH, FR, IS, US, BE

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
        self.get_owner()


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s\t%s\t%s\t%s\t%s" % (self.numb, self.call, self.coords, self.altitude, str(self.owner))

    def get_owner(self):
        if self.numb.startswith('HB-'):
            self.owner = CH(self.numb)
        elif self.numb.startswith('F-'):
            self.owner = FR(self.numb)
        elif self.numb.startswith('TF'):
            self.owner = IS(self.numb)
        elif self.numb.startswith('N'):
            self.owner = US(self.numb)
        elif self.numb.startswith('OO-'):
            self.owner = BE(self.numb)
        else:
            self.owner = None

    def get_path(self):
        return []
        #j = getjson(flight_data_src+self.name)

class RT_craft(Craft):
	pass
