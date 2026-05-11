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
    tournament = int(match_header_event['href'].split('/')[2])

    # Match Date
    match_date_div = soup.find_all('div', {'class':'match-header-date'})[0]
    match_date = match_date_div.div['data-utc-ts']

    # Teams
    match_vs_header = soup.find_all('a', {'class':'match-header-link'})
    team_a = int(match_vs_header[0]['href'].split('/')[2])
    team_b = int(match_vs_header[1]['href'].split('/')[2])

    # Patch
    patch_div = match_date_div.find_all('div', {'style':'font-style: italic;'})
    if len(patch_div) == 0:
        patch = None
    else:
        patch = patch_div[0].text.split(' ')[1]

    # Best Of
    match_header_vs_note = soup.find_all('div',{'class': 'match-header-vs-note'})
    for i in range(len(match_header_vs_note)):
        if match_header_vs_note[i].text.strip()[:2].upper() == 'BO':
            best_of = int(match_header_vs_note[i].text.strip()[-1])
            break

    # Map Veto
    match_header_note = soup.find_all('div',{'class':'match-header-note'})[0].text.strip()
    map_veto = {
        'first_pick_short_name':match_header_note.split(' ')[0],
        'first_pick':{'bans':[], 'picks':[]},
        'second_pick':{'bans':[], 'picks':[]},
        'decider':''
    }
    for s in match_header_note.split('; '):
        if s.split(' ')[0] == map_veto['first_pick_short_name']:
            if s.split(' ')[1] == 'ban':
                map_veto['first_pick']['bans'].append(s.split(' ')[2])
            else:
                map_veto['first_pick']['picks'].append(s.split(' ')[2])
        elif len(s.split(' ')) == 3:
            if s.split(' ')[1] == 'ban':
                map_veto['second_pick']['bans'].append(s.split(' ')[2])
            else:
                map_veto['second_pick']['picks'].append(s.split(' ')[2])
        else:
            map_veto['decider'] = s.split(' ')[0]

    return [tournament, match_date, team_a, team_b, patch, best_of, map_veto]


if __name__ == '__main__':
    fnc_th = get_match_data(660389) # FNC 1 - 2 TH
    print('660389: FNC 1 - 2 TH')
    for i in fnc_th:
        print(i)
    sleep(1)

    navi_fnc = get_match_data(594757) # NAVI 1 - 2 FNC
    print('\n594757: NAVI 1 - 2 FNC')
    for i in navi_fnc:
        print(i)
    sleep(1)

    prx_fnc = get_match_data(498628) # PRX 3 - 1 FNC
    print('\n498628: PRX 3 - 1 FNC')
    for i in prx_fnc:
        print(i)