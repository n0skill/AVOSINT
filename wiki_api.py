import requests
import json

def search_wiki_commons(tail_n):
    r = requests.get('https://commons.wikimedia.org/wiki/Category:{}_(aircraft)'.format(tail_n))
    
    if r.status_code == 200:
        return r.url
    else:
        return None
