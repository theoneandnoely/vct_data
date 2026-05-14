import asyncio
import aiohttp
from bs4 import BeautifulSoup
from extract_kaggle_data import get_match_ids

async def fetch(url:str, session:aiohttp.ClientSession) -> str:
    async with session.get(url) as resp:
        assert resp.status == 200
        return await resp.text

async def get_match_data(match_id:int, session:aiohttp.ClientSession) -> list:
    pass

async def main():
    ids = get_match_ids()

    async with aiohttp.ClientSession() as session:
        page = await fetch()