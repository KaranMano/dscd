from pathlib import Path
import json
import copy

class RaftLog():
    raw = []
    _index = 0

    def __init__(self, logFilePath):
        self.logFilePath = logFilePath
        if Path(self.logFilePath).exists():
            with open(self.logFilePath, "r") as log:
                self.raw = json.load(log)
        else:
            with open(self.logFilePath, "w") as log:
                json.dump(self.raw, log)
        
    def __len__(self):
        return len(self.raw)
    
    def __iter__(self):
        return self

    def __next__(self):
        _index = 0 
        try:
            result = copy.copy(self.raw[self._index])
        except IndexError:
            self._index = 0
            raise StopIteration
        self._index += 1
        return result
    
    def __getitem__(self, key):
        return copy.copy(self.raw[key])

    def __set_attr__(self, name, value):
        raise KeyError
    
    def appendAt(self, msg, term, index):
        raw = raw[:index]
        raw.append({"msg": msg, "term": term})

        with open(self.logFilePath, "w") as log:
            json.dump(self.raw, log)