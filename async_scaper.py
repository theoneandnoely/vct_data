import asyncio
import aiohttp
from bs4 import BeautifulSoup
from extract_kaggle_data import get_match_ids

# async def fetch(url:str, session:aiohttp.ClientSession) -> str:
#     async with session.get(url) as resp:
#         assert resp.status == 200
#         return await resp.text

async def get_match_data(match_id:int, session:aiohttp.ClientSession, semaphore:asyncio.Semphore) -> list:
    async with semaphore:
        try:
            async with session.get(f'https://vlr.gg/{str(match_id)}', timeout=30) as resp:
                if resp.status == 200:
                    soup = BeautifulSoup(await resp.text(), 'html.parser')
        except asyncio.TimeoutError:
            pass

async def main():
    ids = get_match_ids()
    sem = asyncio.Sempahore(25)

    async with aiohttp.ClientSession() as session:
        tasks = [get_match_data(i, session, sem) for i in ids]
        results = await asyncio.gather(*tasks)