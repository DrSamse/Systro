from typing import Tuple
from modules.Simbad import DataBank

db = DataBank()
db.LoadDB("./db.sdb")

print(" Systro-Shell   (c) Samuel Nösslböck 2021 ")
print("==========================================")

while True:
    id = input("ID:// ")
    print(db.IDRequest(id).GetDict())
    db.SaveDB()