import requests
import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup

def serial_requests(ids:list, session: requests.Session) -> list:
    urls = [f'https://www.vlr.gg/{str(i)}' for i in ids]
    output = []
    for u in urls:
        extracted_data = {'matches':[], 'games':[], 'player_game_history':[]}

        with session.get(u) as page:
            assert page.status_code == 200
            print(u)
            soup = BeautifulSoup(page.text, 'html.parser')
        
        match_id = int(u.split('/')[-1])
        tournament = int(soup.find_all('a',{'class':'match-header-event'})[0]['href'].split('/')[2])
        match_date = soup.find_all('div',{'class':'match-header-date'})[0].div['data-utc-ts']
        match_vs_header = soup.find_all('a',{'class':'match-header-link'})
        team_a = int(match_vs_header[0]['href'].split('/')[2])
        team_b = int(match_vs_header[1]['href'].split('/')[2])
        patch_div = soup.find_all('div',{'class':'match-header-date'})[0].find_all('div',{'style':'font-style: italic;'})
        patch = None if len(patch_div) == 0 else patch_div[0].text.split(' ')[1]
        match_header_vs_note = soup.find_all('div',{'class': 'match-header-vs-note'})
        for i in range(len(match_header_vs_note)):
            if match_header_vs_note[i].text.strip()[:2].upper() == 'BO':
                best_of = int(match_header_vs_note[i].text.strip()[-1])
                break
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
        
        extracted_data['matches'].append({
            'id':match_id,
            'tournament':tournament,
            'match_date':match_date,
            'team_a':team_a,
            'team_b':team_b,
            'patch':patch,
            'best_of':best_of,
            'map_veto':map_veto
        })

        maps_div = soup.find_all('div',{'class':'vm-stats-game'})
        for m in maps_div:
            if m['data-game-id'] != 'all':
                team_divs = m.find_all('div',{'class':'team'})
                map_data = {
                    'id': int(m['data-game-id']),
                    'match_id':match_id,
                    'map_name':m.find('div',{'class':'map'}).div.span.text.strip().split('\t')[0],
                    'team_a_score':int(team_divs[0].find('div',{'class':'score'}).text),
                    'team_a_att':int(team_divs[0].find('span',{'class':'mod-t'}).text),
                    'team_a_def':int(team_divs[0].find('span',{'class':'mod-ct'}).text),
                    'team_a_ot':None if team_divs[0].find('span',{'class':'mod-ot'}) is None else int(team_divs[0].find('span',{'class':'mod-ot'}).text),
                    'team_b_score':int(team_divs[1].find('div',{'class':'score'}).text),
                    'team_b_att':int(team_divs[1].find('span',{'class':'mod-t'}).text),
                    'team_b_def':int(team_divs[1].find('span',{'class':'mod-ct'}).text),
                    'team_b_ot':None if team_divs[1].find('span',{'class':'mod-ot'}) is None else int(team_divs[1].find('span',{'class':'mod-ot'}).text),
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
                
                tables = m.find_all('table', {'class':'mod-overview'})
                a_players = tables[0].tbody.find_all('tr')
                b_players = tables[1].tbody.find_all('tr')
                for i in range(len(a_players)):
                    map_data[f'a_player_{str(i+1)}'] = int(a_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2])
                    map_data[f'b_player_{str(i+1)}'] = int(b_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2])
                    a_player_stat = {
                        'player_id':int(a_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2]),
                        'game_id':int(m['data-game-id']),
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
                        'game_id':int(m['data-game-id']),
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
                    extracted_data['player_game_history'].append(a_player_stat)
                    extracted_data['player_game_history'].append(b_player_stat)
                extracted_data['games'].append(map_data)
        output.append(extracted_data)
        time.sleep(1)
    return output

async def fetch(url:str, session:aiohttp.ClientSession) -> str:
    async with session.get(url) as resp:
        assert resp.status == 200
        return {'id':int(url.split('/')[-1]),'page': await resp.text()}

async def fetch_all_first(ids:list, session:aiohttp.ClientSession) -> list:
    urls = [f'https://www.vlr.gg/{str(i)}' for i in ids]
    tasks = [fetch(u, session) for u in urls]
    pages = await asyncio.gather(*tasks)
    output = []
    for p in pages:
        extracted_data = {'matches':[], 'games':[], 'player_game_history':[]}
        soup = BeautifulSoup(p['page'], 'html.parser')
        match_id = p['id']
        tournament = int(soup.find_all('a',{'class':'match-header-event'})[0]['href'].split('/')[2])
        match_date = soup.find_all('div',{'class':'match-header-date'})[0].div['data-utc-ts']
        match_vs_header = soup.find_all('a',{'class':'match-header-link'})
        team_a = int(match_vs_header[0]['href'].split('/')[2])
        team_b = int(match_vs_header[1]['href'].split('/')[2])
        patch_div = soup.find_all('div',{'class':'match-header-date'})[0].find_all('div',{'style':'font-style: italic;'})
        patch = None if len(patch_div) == 0 else patch_div[0].text.split(' ')[1]
        match_header_vs_note = soup.find_all('div',{'class': 'match-header-vs-note'})
        for i in range(len(match_header_vs_note)):
            if match_header_vs_note[i].text.strip()[:2].upper() == 'BO':
                best_of = int(match_header_vs_note[i].text.strip()[-1])
                break
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
        
        extracted_data['matches'].append({
            'id':match_id,
            'tournament':tournament,
            'match_date':match_date,
            'team_a':team_a,
            'team_b':team_b,
            'patch':patch,
            'best_of':best_of,
            'map_veto':map_veto
        })

        maps_div = soup.find_all('div',{'class':'vm-stats-game'})
        for m in maps_div:
            if m['data-game-id'] != 'all':
                team_divs = m.find_all('div',{'class':'team'})
                map_data = {
                    'id': int(m['data-game-id']),
                    'match_id':match_id,
                    'map_name':m.find('div',{'class':'map'}).div.span.text.strip().split('\t')[0],
                    'team_a_score':int(team_divs[0].find('div',{'class':'score'}).text),
                    'team_a_att':int(team_divs[0].find('span',{'class':'mod-t'}).text),
                    'team_a_def':int(team_divs[0].find('span',{'class':'mod-ct'}).text),
                    'team_a_ot':None if team_divs[0].find('span',{'class':'mod-ot'}) is None else int(team_divs[0].find('span',{'class':'mod-ot'}).text),
                    'team_b_score':int(team_divs[1].find('div',{'class':'score'}).text),
                    'team_b_att':int(team_divs[1].find('span',{'class':'mod-t'}).text),
                    'team_b_def':int(team_divs[1].find('span',{'class':'mod-ct'}).text),
                    'team_b_ot':None if team_divs[1].find('span',{'class':'mod-ot'}) is None else int(team_divs[1].find('span',{'class':'mod-ot'}).text),
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
                
                tables = m.find_all('table', {'class':'mod-overview'})
                a_players = tables[0].tbody.find_all('tr')
                b_players = tables[1].tbody.find_all('tr')
                for i in range(len(a_players)):
                    map_data[f'a_player_{str(i+1)}'] = int(a_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2])
                    map_data[f'b_player_{str(i+1)}'] = int(b_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2])
                    a_player_stat = {
                        'player_id':int(a_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2]),
                        'game_id':int(m['data-game-id']),
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
                        'game_id':int(m['data-game-id']),
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
                    extracted_data['player_game_history'].append(a_player_stat)
                    extracted_data['player_game_history'].append(b_player_stat)
                extracted_data['games'].append(map_data)
        output.append(extracted_data)
    return output

async def fetch_and_extract(url:str, session:aiohttp.ClientSession) -> dict:
    extracted_data = {'matches':[], 'games':[], 'player_game_history':[]}
    async with session.get(url) as resp:
        assert resp.status == 200
        soup = BeautifulSoup(await resp.text(), 'html.parser')
    match_id = int(url.split('/')[-1])
    tournament = int(soup.find_all('a',{'class':'match-header-event'})[0]['href'].split('/')[2])
    match_date = soup.find_all('div',{'class':'match-header-date'})[0].div['data-utc-ts']
    match_vs_header = soup.find_all('a',{'class':'match-header-link'})
    team_a = int(match_vs_header[0]['href'].split('/')[2])
    team_b = int(match_vs_header[1]['href'].split('/')[2])
    patch_div = soup.find_all('div',{'class':'match-header-date'})[0].find_all('div',{'style':'font-style: italic;'})
    patch = None if len(patch_div) == 0 else patch_div[0].text.split(' ')[1]
    match_header_vs_note = soup.find_all('div',{'class': 'match-header-vs-note'})
    for i in range(len(match_header_vs_note)):
        if match_header_vs_note[i].text.strip()[:2].upper() == 'BO':
            best_of = int(match_header_vs_note[i].text.strip()[-1])
            break
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
    
    extracted_data['matches'].append({
        'id':match_id,
        'tournament':tournament,
        'match_date':match_date,
        'team_a':team_a,
        'team_b':team_b,
        'patch':patch,
        'best_of':best_of,
        'map_veto':map_veto
    })

    maps_div = soup.find_all('div',{'class':'vm-stats-game'})
    for m in maps_div:
        if m['data-game-id'] != 'all':
            team_divs = m.find_all('div',{'class':'team'})
            map_data = {
                'id': int(m['data-game-id']),
                'match_id':match_id,
                'map_name':m.find('div',{'class':'map'}).div.span.text.strip().split('\t')[0],
                'team_a_score':int(team_divs[0].find('div',{'class':'score'}).text),
                'team_a_att':int(team_divs[0].find('span',{'class':'mod-t'}).text),
                'team_a_def':int(team_divs[0].find('span',{'class':'mod-ct'}).text),
                'team_a_ot':None if team_divs[0].find('span',{'class':'mod-ot'}) is None else int(team_divs[0].find('span',{'class':'mod-ot'}).text),
                'team_b_score':int(team_divs[1].find('div',{'class':'score'}).text),
                'team_b_att':int(team_divs[1].find('span',{'class':'mod-t'}).text),
                'team_b_def':int(team_divs[1].find('span',{'class':'mod-ct'}).text),
                'team_b_ot':None if team_divs[1].find('span',{'class':'mod-ot'}) is None else int(team_divs[1].find('span',{'class':'mod-ot'}).text),
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
            
            tables = m.find_all('table', {'class':'mod-overview'})
            a_players = tables[0].tbody.find_all('tr')
            b_players = tables[1].tbody.find_all('tr')
            for i in range(len(a_players)):
                map_data[f'a_player_{str(i+1)}'] = int(a_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2])
                map_data[f'b_player_{str(i+1)}'] = int(b_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2])
                a_player_stat = {
                    'player_id':int(a_players[i].find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2]),
                    'game_id':int(m['data-game-id']),
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
                    'game_id':int(m['data-game-id']),
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
                extracted_data['player_game_history'].append(a_player_stat)
                extracted_data['player_game_history'].append(b_player_stat)
            extracted_data['games'].append(map_data)
    return extracted_data

async def async_extract(ids:list, session:aiohttp.ClientSession) -> list:
    urls = [f'https://www.vlr.gg/{str(i)}' for i in ids]
    tasks = [fetch_and_extract(u, session) for u in urls]
    output = await asyncio.gather(*tasks)
    return output

async def main():
    ids = [660389, 594757, 498628, 660383, 666490, 659481, 626549, 498632, 378829, 167393]
    start = time.time()
    with requests.session() as s:
        serial_results = serial_requests(ids, s)
    serial_time = time.time() - start
    start = time.time()
    async with aiohttp.ClientSession() as s:
        fetch_first_results = await fetch_all_first(ids, s)
    fetch_first_time = time.time() - start
    start = time.time()
    async with aiohttp.ClientSession() as s:
        async_results = await async_extract(ids, s)
    async_time = time.time() - start

    if serial_results == fetch_first_results and fetch_first_results == async_results:
        print('All Results returned the same')
    else:
        print(f'Serial:\n{serial_results}\n\nFetch First:\n{fetch_first_results}\n\nAsync:\n{async_results}\n')
    
    print(f'Serial: {serial_time} seconds\nFetch First: {fetch_first_time} seconds\nAsync: {async_time} seconds')

if __name__ == '__main__':
    asyncio.run(main())