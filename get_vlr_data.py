from bs4 import BeautifulSoup
from time import sleep
import requests

BASE_URL = 'https://www.vlr.gg/'
EVENTS_ENDING = 'events/?tier=60'

with requests.get(BASE_URL+EVENTS_ENDING) as page:
    soup = BeautifulSoup(page.text, 'html.parser')

