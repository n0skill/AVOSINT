import requests
import time
from bs4 import BeautifulSoup

def search_incidents(tail_n, is_verbose):
    r = requests.get('https://aviation-safety.net/database/registration/regsearch.php?regi={}'.format(tail_n))
    
    if r.status_code == 200:
        soup= BeautifulSoup(r.content, 'html.parser')
        td  = soup.find('span', {'class': 'nobr'})
        if td:
            r   = requests.get('https://aviation-safety.net'+td.find('a')['href'])
            return r.url
            if r.status_code == 403:
                return 'HTTP 403 while retriving incidents'
    return None
