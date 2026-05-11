from bs4 import BeautifulSoup
from time import sleep
import requests


def get_match_data(match_id:int) -> list:
    url = f'https://www.vlr.gg/{str(match_id)}/'

    with requests.get(url) as page:
        if page.status_code != 200:
            raise RuntimeError(f'{url} returned code {page.status_code}')
        soup = BeautifulSoup(page.text, 'html.parser')
    
    # Tournament ID
    match_header_event = soup.find_all('a',{'class':'match-header-event'})[0]
    tournament = match_header_event['href'].split('/')[2]
    # print(event, type(event))

    # Match Date
    match_date_div = soup.find_all('div', {'class':'match-header-date'})[0]
    match_date = match_date_div.div['data-utc-ts']
    # print(match_date, type(match_date))

    # Teams
    match_vs_header = soup.find_all('a', {'class':'match-header-link'})
    team_a = match_vs_header[0]['href'].split('/')[2]
    team_b = match_vs_header[1]['href'].split('/')[2]
    # print(team_a, team_b)

    # Patch
    match_header_note = soup.find_all('')

    return [tournament, match_date, team_a, team_b]


if __name__ == '__main__':
    get_match_data(660389)