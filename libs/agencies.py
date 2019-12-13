# -*- coding: utf-8 -*-
import json
import requests
import ssl
from bs4 import BeautifulSoup

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

class TLSv1Adapter(HTTPAdapter):
    """"Transport adapter" that allows us to use TLSv1."""

    def init_poolmanager(self, connections, maxsize, block=False):
    	self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

class NODHAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
    	self.poolmanager = PoolManager(num_pools=connections,
						   context = create_urllib3_context(ciphers='DEFAULT:!DH'),
						   maxsize=maxsize,
						   block=block,
						   ssl_version=ssl.PROTOCOL_TLSv1)


# Gather data from various agencies depending on country code of tail number

class Owner:
    def __init__(self):
        self.name = 'TBD'
        self.country = 'TBD'

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


def CH(tail_n):
	"""
	Get information on aircraft from tail number
	"""

	url = 'https://app02.bazl.admin.ch/web/bazl-backend/lfr'	
	headers = {
                'Pragma': 'no-cache',
                'Origin': 'https://app02.bazl.admin.ch/web/bazl/fr/',
                'Content-Type': 'application/json',
                'Referer': 'https://app02.bazl.admin.ch/web/bazl/fr/'
            }
	data = '{"page_result_limit":10,"current_page_number":1,"sort_list":"registration","language":"fr","queryProperties":{"registration":"'+tail_n[3:] + '","aircraftStatus":["Registered","Reserved","Reservation Expired","Registration in Progress"]}}}'
    
	response = requests.post(url, headers=headers, data=data)
    
	if response.status_code == 200:
		jsonobj     = json.loads(response.text)
		infoarray   = jsonobj[0]
		own_ops     = infoarray.get('ownerOperators')
		leng        = len(own_ops)
		name        = own_ops[leng-1].get('ownerOperator')
		addr        = own_ops[leng-1].get('address')
		street      = addr.get('street')
		street_n    = addr.get('streetNo')
		zipcode     = addr.get('zipCode')
		city		= addr.get('city')
		own         = Owner(name, street + ' ' + street_n, city ,zipcode, "Switzerland")
		return own
	else:
		return Owner('Unknown', 'Unknown','Unknown','Unknown','Unknown')


def FR(tail_n):
	# WARNING 
	# French service communicates over TLSV1, which is outdated
	print('WARNING: The french agency uses TLSV1. Security is not guaranteed')
	s = requests.session()
	headers = {
		'Origin': 'https://immat.aviation-civile.gouv.fr',
		'Referer': 'https://immat.aviation-civile.gouv.fr/immat/servlet/aeronef_liste.html'
	}

	data = [
	  ('FORM_DTO_ID', 'DTO_RECHERCHE_AER'),
	  ('FORM_ACTION', 'SEARCH'),
	  ('FORM_CHECK', 'true'),
	  ('FORM_ROW', ''),
	  ('CTRL_ID', '1010'),
	  ('SUBFORM_DTC_ID', 'DTC_1'),
	  ('$DTO_RECHERCHE_AER$PER_ID', ''),
	  ('$DTO_RECHERCHE_AER$PER_VERSION', ''),
	  ('$DTO_RECHERCHE_AER$PERSONNE', ''),
	  ('$DTO_RECHERCHE_AER$MRQ_CD', tail_n),
	  ('$DTO_RECHERCHE_AER$CNT_LIBELLE', ''),
	  ('$DTO_RECHERCHE_AER$SI_RADIE', '1'),
	  ('$DTO_RECHERCHE_AER$SI_RADIEcheckbox', '1'),
	  ('$DTO_RECHERCHE_AER$SI_INSCRIT', '1'),
	  ('$DTO_RECHERCHE_AER$SI_INSCRITcheckbox', '1'),
	  ('$DTO_RECHERCHE_AER$CRE_NUM_SERIE', ''),
	]
	s.mount("https://", TLSv1Adapter())
	response = s.post('https://immat.aviation-civile.gouv.fr/immat/servlet/aeronef_liste.html', headers=headers, data=data)
	if response.status_code == 200:
		soup = BeautifulSoup(response.text, 'html.parser')
		bls = soup.find('a', string=tail_n)
		if bls is None:
			print(f'Could not find {tail_n} in agency registers')
		if bls is not None:
			response = s.get('https://immat.aviation-civile.gouv.fr/immat/servlet/' + bls['href'], headers=headers, data=data)
			soup = BeautifulSoup(response.text, 'html.parser')
			bls = soup.find('a', string="Données juridiques")
			response = s.get('https://immat.aviation-civile.gouv.fr/immat/servlet/' + bls['href'], headers=headers, data=data)
			soup = BeautifulSoup(response.text, 'html.parser')
			bls = soup.find_all('td', {'class':"tdLigneListe"})
			if len(bls) > 0:
				name = bls[0].text
				addr = bls[1].text
				city = bls[2].text
				return Owner(name, addr, city, '', 'France')
			

def US(tail_n):
	resp = requests.get("https://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?nNumberTxt="+tail_n)
	if resp.status_code == 200:
		soup = BeautifulSoup(resp.text, 'html.parser')
		name = soup.find('span', {'id':'ctl00_content_lbMfrName'}).text.strip()
		city = soup.find('span', {'id':'ctl00_content_lbOwnerCity'}).text.strip()
		addr = soup.find('span', {'id':'ctl00_content_lbOwnerStreet'}).text.strip()
		return Owner(name, addr, city, '', 'USA')
	raise Exception('Error while retrieving from US')

def IS(tail_n):
	name = ''
	street = ''
	city = ''
	s = requests.session()
	s.mount("https://", TLSv1Adapter())
	req = s.get('https://www.icetra.is/aviation/aircraft/register?aq='+tail_n)
	if req.status_code is 200:
		soup = BeautifulSoup(req.text, 'html.parser')
		own = soup.find('li', {'class':'owner'})
		if own is not None:
			won = own.stripped_strings
			for i,j in enumerate(won):
				if i == 1:
					name = j
				if i == 2:
					street = j
				if i == 3:
					city = j
			if own is not None:
				return Owner(name, street, city, '', 'Iceland')

def BE(tail_n):
	rep = requests.get('https://es.mobilit.fgov.be/aircraft-registry/rest/aircrafts?aircraftStates=REGISTERED&registrationMark=' + tail_n + '&page=0&pageSize=10&sort=REGISTRATIONMARK&sortDirection=ascending')
	if rep.status_code == 200:
		j = json.loads(rep.text)
		if len(j) > 0:
			if j[0].get('id') != '':
				rep = requests.get('https://es.mobilit.fgov.be/aircraft-registry/rest/aircrafts/'+str(j[0].get('id')))
				if rep.status_code == 200:
					#print(rep.text)
					j 		= json.loads(rep.text)
					name 	= j.get('stakeHolderRoleList')[0].get('name') 
					street 	= j.get('stakeHolderRoleList')[0].get('addresses').get('street')
					city 	= j.get('stakeHolderRoleList')[0].get('addresses').get('city')
					return Owner(name, street, city, '', 'Belgium')

		return None

def SW(tail_n):
	data = {
		'selection':'regno',
		'regno': tail_n,
		'part':'',
		'owner':'',
		'item':'',
		'X-Requested-With':'XMLHttpRequest'
	}
	s = requests.session()
	rep = s.post('https://sle-p.transportstyrelsen.se/extweb/en-gb/sokluftfartyg', data = data)
	if rep.status_code == 200:
		soup = BeautifulSoup(rep.content, features="html.parser")
		results_element = soup.find_all('label', {'class':'owner-headline'})[0]
		name = results_element.parent.find('a', {'class':'open-owner-page'}).text
		street = results_element.parent.text.split('\r\n')[1].strip()
		city = results_element.parent.text.split('\r\n')[2].strip()
		country= results_element.parent.text.split('\r\n')[3].strip()
		return Owner(name, street, city, '', country)
	else:
		raise Exception('Error retrieving from SW')

# FIXME
def AT(tail_n):
	tail_n = tail_n.strip('OE-')
	s = requests.session()
	data = [
			("txtKennzeichen", tail_n),
			("radStartgewicht", 1),
			('txtOrdnungszahl', ''),
            ('txtHersteller', ''),
            ('txtBaumuster', ''),
            ('cmbLfzart', ''),
            ('txtSeriennummer', ''),
            ('txtStartgewicht', ''),
            ('txtHalter', ''),
            ('p::submit', ''),
		]
	headers = {	
		'Origin': 'https://www.austrocontrol.at/',
		'Referer': 'https://www.austrocontrol.at/'
	}
	rep = s.get('https://www.austrocontrol.at/ta/OenflSucheEn')
	if rep.status_code == 200:
		soup = BeautifulSoup(rep.text, features="html.parser") 
		form_submit = soup.find_all('form')[0]
		url = form_submit.get('action')[2:]
		rep = s.post("https://www.austrocontrol.at/ta/" + url, data=data, headers=headers)
		if rep.status_code == 200:
			soup = BeautifulSoup(rep.text, features="html.parser")
			table = soup.find('table', {'id': 'resultTable'})
			columns = table.find_all('td')
			texts = [column.p for column in columns]	
			name = texts[4].contents[0]
			address_values = texts[4].contents[1].text.split(',')
			street = str(address_values[1]) + ' ' + str(address_values[2])
			city = address_values[0]
			return Owner(name, street, city, '', 'Austria')

	else:
		print(vars(rep))


def CZ(tail_n):
	raise NotImplementedError('Czech registry not yet implemented.\nRegistry url is http://portal.caa.cz/letecky-rejstrik')
