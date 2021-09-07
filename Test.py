from typing import Tuple
from modules.Simbad import DataBank

db = DataBank()
db.LoadDB("./db.sdb")

while True:
    id = input("ID:// ")
    print(db.IDRequest(id).GetDict())
    db.SaveDB()