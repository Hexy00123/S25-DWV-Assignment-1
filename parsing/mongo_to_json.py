import pymongo
from dotenv import dotenv_values
import json 


if __name__ == '__main__': 
    config = dotenv_values(".env")   
    
    films = []    
    with pymongo.MongoClient(f"mongodb://{config['LOGIN']}:{config['PASSWORD']}@127.0.0.1") as  mongo_connection: 
        db = mongo_connection['films']
        collection = db.films
        
        for film in collection.find():
            del film['_id'] 
            films.append(film)
            
    with open('../public/films.json', 'w') as file: 
        json.dump(films, file, indent=2)
        
    