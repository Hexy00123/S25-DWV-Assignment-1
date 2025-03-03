import requests 
from bs4 import BeautifulSoup
import pymongo
import asyncio
from dotenv import dotenv_values
import logging
import aiohttp
import re
from time import sleep
from random import choice

class Parser:
    def __init__(self):
        logging.basicConfig(filename='logs/parser.log', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info('Parser started.') 
        self.config = dotenv_values(".env")        
        
        self.listing_url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films" 
        self.mongo_connection = pymongo.AsyncMongoClient(f"mongodb://{self.config['LOGIN']}:{self.config['PASSWORD']}@127.0.0.1")
    
    async def extract_film_urls(self, url: str):  
        self.logger.info('JOB: extract_film_urls') 
        
        db = self.mongo_connection['films']
        collection = db.films
        
        request = requests.get(url)
        
        if request.status_code != 200: 
            self.logger.error('Could not get page.')   
            return
        
        content = BeautifulSoup(request.content, 'html.parser')
        tables = content.find_all('table', class_='wikitable plainrowheaders')
        table = tables[max(enumerate(tables), key=lambda x: len(x[1].find_all('tr')))[0]]

        film_urls = [] 
        for film_data_raw in table.find_all('tr')[1:]:
            url = 'https://en.wikipedia.org' + film_data_raw.find('i').find('a').get('href')
            
            box_office = next(filter(lambda tag: "$" in tag.text, film_data_raw.find_all('td'))).text.replace(',', '')             
            box_office = ''.join(char if char.isnumeric() else ' ' for char in box_office[1:]).split()[0]

            contains = await collection.find_one({"url": url})
            if contains is None:
                film_urls.append({'url': url, 'box_office': box_office})
                
        self.logger.info(f'Found {len(film_urls)} new films.')   
        if len(film_urls) == 0: 
            return
        
        self.logger.info('Inserting new films to database...') 
        await collection.insert_many(film_urls)
        self.logger.info('Successfully inserted.') 
        
    async def parse_films_data(self): 
        self.logger.info('JOB: parse_films_data') 
        
        db = self.mongo_connection['films']
        collection = db.films
        
        films = await collection.find({"url": {"$exists": True}, "title": {"$exists": False}}).to_list(length=None)
        
        film_promises = []
        for film in films:
            film_promises.append(self.parse_film_data(film['url']))

        write_promises = []
        for film, data in zip(films, await asyncio.gather(*film_promises)):
            write_promises.append(collection.update_one({"_id": film['_id']}, {"$set": data}))
            
        await asyncio.gather(*write_promises)
            
    async def parse_film_data(self, url: str):
        self.logger.info(f'JOB:      parse_film_data {url}') 
        sleep(choice([0, 0.15, 0.4, 0.5, 0.7]))
        
        page_content = await self.fetch_page(url)
        content = BeautifulSoup(page_content, 'html.parser')

        # title, release_year, director, country
        table = content.find('table', class_='infobox vevent').find('tbody')
        rows = table.find_all('tr')

        fields = {row.find('th').text: row.find('td') for row in rows[1:] if row.find('th') is not None}
                
        film = dict()
        # title processing 
        film['title'] = rows[0].find('th').text 
        
        # release_year processing
        pattern = r'\b(1[7-9]\d{2}|2[0-1]\d{2})\b'
        
        field = (fields.get('Release dates') or fields.get('Release date')).text
        film['release_year'] = int(re.findall(pattern, field)[0])
        
        # director processing
        if fields['Directed by'].find('li') is not None:
            film['director'] = [(name.text[:name.text.find(' (')]  if '(' in name.text else name.text)
                                for name in fields['Directed by'].find_all('li') if ':' not in name.text]
        else: 
            film['director'] = [fields.get('Directed by').find('a').text]
        
        # country processing
        if 'Country' in fields:
            film['country'] = fields.get('Country').text    
        else:
            if fields.get('Countries').find('li') is not None:
                film['country'] = fields.get('Countries').find('li').text
            else:
                field = str(fields.get('Countries')) 
                film['country'] = field[field.find('>') + 1:field[1:].find('<') + 1] 
                
        if '[' in film['country']:
            film['country'] = film['country'][:film['country'].find('[')]
            
        self.logger.info(f'JOB DONE: parse_film_data {url}') 
        return film
        
            
    async def fetch_page(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

        
    
if __name__ == '__main__': 
    parser = Parser() 
    asyncio.run(parser.extract_film_urls(parser.listing_url))
    asyncio.run(parser.parse_films_data())
    