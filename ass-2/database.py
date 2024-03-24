from pathlib import Path
import json
import copy

class Database():
    record = {}

    # node - current Node. Used to resolve path to db file
    def __init__(self, ID):
        Path(f"./logs_node_{ID}").mkdir(parents=True, exist_ok=True)
        self.filePath = f"./logs_node_{ID}/db.txt"
        if Path(self.filePath).exists():
            with open(self.filePath, "r") as db:
                self.record = json.load(db)
    
    def __getitem__(self, key):
        return copy.copy(self.record[key])

    def commit(self, key, value):
        self.record[key] = value
        with open(self.filePath, "w") as db:
            json.dump(self.record, db)