
import json

class Database:
    def __init__(self, path: str) -> None:
        with open(path, 'r', encoding = 'utf8') as file:
            self.db = json.load(file)
            
    def get(self, key: str, column: str):
        return self.db.get(column, {}).get(key, None)
    
    def getAll(self, column: str, key: str | None = "", value: str | None = ""):
        dicts = self.db.get(column, None)
        if key and value:
            return [ { "id": k, **val } for k, val in dicts.items() if val.get(key, None) == value ]
        else:
            return [ { "id": k, **val } for k, val in dicts.items() ]