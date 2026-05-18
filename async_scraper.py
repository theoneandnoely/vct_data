import asyncio
import aiohttp
from bs4 import BeautifulSoup
from extract_kaggle_data import get_match_ids
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

async def extract_player_game_data(row:str, game_id:int) -> dict:
    output = {
        'player_id':int(row.find('td',{'class':'mod-player'}).find('a')['href'].split('/')[2]),
        'game_id':game_id,
        'agent':row.find('td',{'class','mod-agents'}).div.span.img['title'],
        'kills_tot':int(row.find('td',{'class':'mod-vlr-kills'}).span.find('span',{'class':'mod-both'}).text),
        'kills_att':int(row.find('td',{'class':'mod-vlr-kills'}).span.find('span',{'class':'mod-t'}).text),
        'kills_def':int(row.find('td',{'class':'mod-vlr-kills'}).span.find('span',{'class':'mod-ct'}).text),
        'deaths_tot':int(row.find('td',{'class':'mod-vlr-deaths'}).span.find('span',{'class':'mod-both'}).text),
        'deaths_att':int(row.find('td',{'class':'mod-vlr-deaths'}).span.find('span',{'class':'mod-t'}).text),
        'deaths_def':int(row.find('td',{'class':'mod-vlr-deaths'}).span.find('span',{'class':'mod-ct'}).text),
        'assists_tot':int(row.find('td',{'class':'mod-vlr-assists'}).span.find('span',{'class':'mod-both'}).text),
        'assists_att':int(row.find('td',{'class':'mod-vlr-assists'}).span.find('span',{'class':'mod-t'}).text),
        'assists_def':int(row.find('td',{'class':'mod-vlr-assists'}).span.find('span',{'class':'mod-ct'}).text),
        'first_kills':int(row.find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-both'}).text),
        'fk_att':int(row.find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-t'}).text),
        'fk_def':int(row.find('td',{'class':'mod-fb'}).span.find('span',{'class':'mod-ct'}).text),
        'first_deaths':int(row.find('td',{'class':'mod-fd'}).span.find('span',{'class':'mod-both'}).text),
        'fd_att':int(row.find('td',{'class':'mod-fd'}).span.find('span',{'class':'mod-t'}).text),
        'fd_def':int(row.find('td',{'class':'mod-fd'}).span.find('span',{'class':'mod-ct'}).text),
        'vlr_rating_tot':float(row.find_all('td',{'class':'mod-stat'})[0].span.find('span',{'class':'mod-both'}).text),
        'vlr_rating_att':float(row.find_all('td',{'class':'mod-stat'})[0].span.find('span',{'class':'mod-t'}).text),
        'vlr_rating_def':float(row.find_all('td',{'class':'mod-stat'})[0].span.find('span',{'class':'mod-ct'}).text),
        'acs_tot':int(row.find_all('td',{'class':'mod-stat'})[1].span.find('span',{'class':'mod-both'}).text),
        'acs_att':int(row.find_all('td',{'class':'mod-stat'})[1].span.find('span',{'class':'mod-t'}).text),
        'acs_def':int(row.find_all('td',{'class':'mod-stat'})[1].span.find('span',{'class':'mod-ct'}).text)
    }
    return output

async def get_match_data(match_id:int, session:aiohttp.ClientSession, semaphore:asyncio.Semaphore) -> dict:
    async with semaphore:
        logger.info(f'Getting data for {match_id}')
        max_attempts = 2
        for a in range(max_attempts):
            try:
                async with session.get(f'https://vlr.gg/{str(match_id)}', timeout=10) as resp:
                    if resp.status == 200:
                        logging.info(f'https://vlr.gg/{str(match_id)} request returned successfully')
                        soup = BeautifulSoup(await resp.text(), 'html.parser')
                        break
                    else:
                        logger.error(f'https://vlr.gg/{str(match_id)} returned status code {resp.status}')
                        raise aiohttp.ClientError(f'https://vlr.gg/{str(match_id)} returned status code {resp.status}.\n{resp}')
            except asyncio.TimeoutError:
                logger.warning(f'https://vlr.gg/{str(match_id)} timed out. Retrying attempt {a+1}...')
                asyncio.sleep(2 ** a)
        else:
            logger.error(f'Request to https://vlr.gg/{str(match_id)} timed out {max_attempts + 1} times.')
            raise asyncio.TimeoutError(f'Request to https://vlr.gg/{str(match_id)} timed out {max_attempts + 1} times')
        
        # Set up dictionary for returned values
        data = {'matches':[], 'games':[], 'player_game_history':[]}
        
        # Get data for `matches` table
        tournament = int(soup.find_all('a',{'class':'match-header-event'})[0]['href'].split('/')[2])
        logger.debug(f'tournament value extracted for {match_id}')
        match_date = soup.find_all('div',{'class':'match-header-date'})[0].div['data-utc-ts']
        logger.debug(f'match_date value extracted for {match_id}')
        match_vs_header = soup.find_all('a',{'class':'match-header-link'})
        team_a = int(match_vs_header[0]['href'].split('/')[2])
        team_b = int(match_vs_header[1]['href'].split('/')[2])
        logger.debug(f'team IDs extracted for {match_id}')
        patch_div = soup.find_all('div',{'class':'match-header-date'})[0].find_all('div',{'style':'font-style: italic;'})
        patch = None if len(patch_div) == 0 else patch_div[0].text.split(' ')[1].strip()
        logger.debug(f'patch value extracted for {match_id}')
        match_header_vs_note = soup.find_all('div',{'class':'match-header-vs-note'})
        for i in range(len(match_header_vs_note)):
            if match_header_vs_note[i].text.strip()[:2].upper() == 'BO':
                best_of = int(match_header_vs_note[i].text.strip()[-1])
                break
        logger.debug(f'best_of value extracted for {match_id}')
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
        logger.debug(f'map_veto extracted for {match_id}')
        data['matches'].append({
            'id':match_id,
            'tournament':tournament,
            'match_date':match_date,
            'team_a':team_a,
            'team_b':team_b,
            'patch':patch,
            'best_of':best_of,
            'map_veto':map_veto
        })

        # Get data for `games` and `player_game_history` tables
        maps_div = soup.find_all('div',{'class':'vm-stats-game'})
        for m in maps_div:
            if m['data-game-id'] != 'all':
                team_divs = m.find_all('div',{'class':'team'})
                map_data = {
                    'id':int(m['data-game-id']),
                    'match_id':match_id,
                    'map':m.find('div',{'class':'map'}).div.span.text.strip().split('\t')[0],
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
                    map_data[f'a_player_{str(i+1)}'] = int(a_players[i].find('td', {'class':'mod-player'}).find('a')['href'].split('/')[2])
                    map_data[f'b_player_{str(i+1)}'] = int(b_players[i].find('td', {'class':'mod-player'}).find('a')['href'].split('/')[2])
                    data['player_game_history'].append(await extract_player_game_data(a_players[i], int(m['data-game-id'])))
                    logger.debug(f'player_game_history record extracted for game {m['data-game-id']} of match {match_id}')
                    data['player_game_history'].append(await extract_player_game_data(b_players[i], int(m['data-game-id'])))
                    logger.debug(f'player_game_history record extracted for game {m['data-game-id']} of match {match_id}')
                logger.debug(f'games data extracted for game {m['data-game-id']} of match {match_id}')
                data['games'].append(map_data)
    return data

        

async def main():
    ids = [660389, 594757, 498628, 660383, 666490, 659481, 626549, 498632, 378829, 167393]
    sem = asyncio.Semaphore(10)

    async with aiohttp.ClientSession() as session:
        tasks = [get_match_data(i, session, sem) for i in ids]
        results = await asyncio.gather(*tasks)
    
    for r in results:
        print(f'\n{r['matches'][0]['id']}\n')
        print(f'Matches:\n{r['matches'][0]}\n')
        # print(f'Games:')
        # for g in r['games']:
        #     print(g)
        # print(f'Player Game History:')
        # for g in r['player_game_history']:
        #     print(g)

if __name__ == '__main__':
    asyncio.run(main())