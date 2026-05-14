from bs4 import BeautifulSoup
from time import sleep
import requests

# def get_map_data(match_id:int, game_id: int) -> dict:
#     url = f'https://vlr.gg/{str(match_id)}/?game={str(game_id)}&tab=overview/'
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0'}

#     with requests.get(url, headers=headers) as page:
#         if page.status_code != 200:
#             raise RuntimeError(f'{url} returned code {page.status_code}')
#         soup = BeautifulSoup(page.content, 'html.parser')
    
#     stats = soup.find('div',{'class':'vm-stats'})
#     print(stats)
#     header = soup.find('div',{'class':'vm-stats-game'})
#     print(header)
#     teams_divs = header.find_all('div',{'class':'team'})
#     team_a_score = int(teams_divs[0].find('div', {'class','score'}).text)
#     team_b_score = int(teams_div[1].find('div',{'class','score'}).text)
#     map = header.find('div',{'class':'map'}).div.span.text
#     print(f'{map} ({game_id}): {team_a_score} - {team_b_score}')
#     return {}

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
        'decider':None
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

    maps_divs = soup.find_all('div',{'class':'vm-stats-game'})
    maps = {}
    for m in maps_divs:
        data = {
            'map_name':None,
            'team_a_score':None,
            'team_a_att':None,
            'team_a_def':None,
            'team_a_ot':None,
            'team_b_score':None,
            'team_b_att':None,
            'team_b_def':None,
            'team_b_ot':None,
            'a_player_1':None,
            'a_player_2':None,
            'a_player_3':None,
            'a_player_4':None,
            'a_player_5':None,
            'b_player_1':None,
            'b_player_2':None,
            'b_player_3':None,
            'b_player_4':None,
            'b_player_5':None
        }

        player_stats = []
        
        if m['data-game-id'] != 'all':
            game_id = m['data-game-id']
            data['map_name'] = m.find('div',{'class':'map'}).div.span.text.strip().split('\t')[0]

            team_divs = m.find_all('div',{'class','team'})
            data['team_a_score'] = int(team_divs[0].find('div',{'class':'score'}).text)
            data['team_a_att'] = int(team_divs[0].find('span',{'class':'mod-t'}).text)
            data['team_a_def'] = int(team_divs[0].find('span',{'class':'mod-ct'}).text)
            data['team_a_ot'] = None if team_divs[0].find('span',{'class':'mod-ot'}) is None else int(team_divs[0].find('span',{'class':'mod-ot'}).text)
            data['team_b_score'] = int(team_divs[1].find('div',{'class':'score'}).text)
            data['team_b_att'] = int(team_divs[1].find('span',{'class':'mod-t'}).text)
            data['team_b_def'] = int(team_divs[1].find('span',{'class':'mod-ct'}).text)
            data['team_b_ot'] = None if team_divs[1].find('span',{'class':'mod-ot'}) is None else int(team_divs[1].find('span',{'class':'mod-ot'}).text)
            
            tables = m.find_all('table', {'class':'mod-overview'})
            a_players = tables[0].tbody.find_all('tr')
            b_players = tables[1].tbody.find_all('tr')
            for i in range(len(a_players)):
                data[f'a_player_{str(i+1)}'] = int(a_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2])
                data[f'b_player_{str(i+1)}'] = int(b_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2])
                a_player_stat = {
                    'player_id':int(a_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2]),
                    'game_id':game_id,
                    'agent':a_players[i].find('td',{'class':'mod-agents'}).div.span.img['title'],
                    'kills_tot':int(a_players[i].find('td',{'class':'mod-vlr-kills'}).span.find('span',{'class':'mod-both'}).text),
                    'kills_att':int(a_players[i].find('td',{'class':'mod-vlr-kills'}).span.find('span',{'class':'mod-t'}).text),
                    'kills_def':int(a_players[i].find('td',{'class':'mod-vlr-kills'}).span.find('span',{'class':'mod-ct'}).text),
                    'deaths_tot':int(a_players[i].find('td',{'class':'mod-vlr-deaths'}).span.find('span',{'class':'mod-both'}).text),
                    'deaths_att':int(a_players[i].find('td',{'class':'mod-vlr-deaths'}).span.find('span',{'class':'mod-t'}).text),
                    'deaths_def':int(a_players[i].find('td',{'class':'mod-vlr-deaths'}).span.find('span',{'class':'mod-ct'}).text),
                    'assists_tot':int(a_players[i].find('td',{'class':'mod-vlr-assists'}).span.find('span',{'class':'mod-both'}).text),
                    'assists_att':int(a_players[i].find('td',{'class':'mod-vlr-assists'}).span.find('span',{'class':'mod-t'}).text),
                    'assists_def':int(a_players[i].find('td',{'class':'mod-vlr-assists'}).span.find('span',{'class':'mod-ct'}).text),
                    'first_kills':int(a_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-both'}).text),
                    'fk_att':int(a_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-t'}).text),
                    'fk_def':int(a_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-ct'}).text),
                    'first_deaths':int(a_players[i].find('td',{'class':'mod-fd'}).span.find('span',{'class':'mod-both'}).text),
                    'fd_att':int(a_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-t'}).text),
                    'fd_def':int(a_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-ct'}).text),
                    'vlr_rating_tot':float(a_players[i].find_all('td',{'class':'mod-stat'})[0].span.find('span',{'class':'mod-both'}).text),
                    'vlr_rating_att':float(a_players[i].find_all('td',{'class':'mod-stat'})[0].span.find('span',{'class':'mod-t'}).text),
                    'vlr_rating_def':float(a_players[i].find_all('td',{'class':'mod-stat'})[0].span.find('span',{'class':'mod-ct'}).text),
                    'acs_tot':int(a_players[i].find_all('td',{'class':'mod-stat'})[1].span.find('span',{'class':'mod-both'}).text),
                    'acs_att':int(a_players[i].find_all('td',{'class':'mod-stat'})[1].span.find('span',{'class':'mod-t'}).text),
                    'acs_def':int(a_players[i].find_all('td',{'class':'mod-stat'})[1].span.find('span',{'class':'mod-ct'}).text)
                }
                b_player_stat = {
                    'player_id':int(b_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2]),
                    'game_id':game_id,
                    'agent':b_players[i].find('td',{'class':'mod-agents'}).div.span.img['title'],
                    'kills_tot':int(b_players[i].find('td',{'class':'mod-vlr-kills'}).span.find('span',{'class':'mod-both'}).text),
                    'kills_att':int(b_players[i].find('td',{'class':'mod-vlr-kills'}).span.find('span',{'class':'mod-t'}).text),
                    'kills_def':int(b_players[i].find('td',{'class':'mod-vlr-kills'}).span.find('span',{'class':'mod-ct'}).text),
                    'deaths_tot':int(b_players[i].find('td',{'class':'mod-vlr-deaths'}).span.find('span',{'class':'mod-both'}).text),
                    'deaths_att':int(b_players[i].find('td',{'class':'mod-vlr-deaths'}).span.find('span',{'class':'mod-t'}).text),
                    'deaths_def':int(b_players[i].find('td',{'class':'mod-vlr-deaths'}).span.find('span',{'class':'mod-ct'}).text),
                    'assists_tot':int(b_players[i].find('td',{'class':'mod-vlr-assists'}).span.find('span',{'class':'mod-both'}).text),
                    'assists_att':int(b_players[i].find('td',{'class':'mod-vlr-assists'}).span.find('span',{'class':'mod-t'}).text),
                    'assists_def':int(b_players[i].find('td',{'class':'mod-vlr-assists'}).span.find('span',{'class':'mod-ct'}).text),
                    'first_kills':int(b_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-both'}).text),
                    'fk_att':int(b_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-t'}).text),
                    'fk_def':int(b_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-ct'}).text),
                    'first_deaths':int(b_players[i].find('td',{'class':'mod-fd'}).span.find('span',{'class':'mod-both'}).text),
                    'fd_att':int(b_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-t'}).text),
                    'fd_def':int(b_players[i].find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-ct'}).text),
                    'vlr_rating_tot':float(b_players[i].find_all('td',{'class':'mod-stat'})[0].span.find('span',{'class':'mod-both'}).text),
                    'vlr_rating_att':float(b_players[i].find_all('td',{'class':'mod-stat'})[0].span.find('span',{'class':'mod-t'}).text),
                    'vlr_rating_def':float(b_players[i].find_all('td',{'class':'mod-stat'})[0].span.find('span',{'class':'mod-ct'}).text),
                    'acs_tot':int(b_players[i].find_all('td',{'class':'mod-stat'})[1].span.find('span',{'class':'mod-both'}).text),
                    'acs_att':int(b_players[i].find_all('td',{'class':'mod-stat'})[1].span.find('span',{'class':'mod-t'}).text),
                    'acs_def':int(b_players[i].find_all('td',{'class':'mod-stat'})[1].span.find('span',{'class':'mod-ct'}).text)
                }
                player_stats.append(a_player_stat)
                player_stats.append(b_player_stat)
            maps[game_id] = data

    return [tournament, match_date, team_a, team_b, patch, best_of, map_veto, maps, player_stats]


if __name__ == '__main__':
    # get_map_data(660389, 265488)
    
    fnc_th = get_match_data(660389) # FNC 1 - 2 TH
    print('660389: FNC 1 - 2 TH')
    for i in fnc_th:
        print(i)
    sleep(1)

    # navi_fnc = get_match_data(594757) # NAVI 1 - 2 FNC
    # print('\n594757: NAVI 1 - 2 FNC')
    # for i in navi_fnc:
    #     print(i)
    # sleep(1)

    # prx_fnc = get_match_data(498628) # PRX 3 - 1 FNC
    # print('\n498628: PRX 3 - 1 FNC')
    # for i in prx_fnc:
    #     print(i)