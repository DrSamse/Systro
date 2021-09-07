import matplotlib.pyplot as plt
from typing import List
from modules.Simbad import DataBank, SpaceObject

db = DataBank()
db.LoadDB("./db.sdb")
print("[DB] Loaded " + str(len(db.objsObjs)) + " entries")

STAR_COUNT = 0
STEP = 1

newStars = 0

for i in range(1, STAR_COUNT * STEP + 1, STEP):
    id = "HD " + str(i)
    if not db.HasObj(id):
        db.IDRequest(id)
        newStars += 1
        if (newStars % 100) == 0: 
            print(str(newStars) + " new Stars added!")
            db.SaveDB()
            print("[DB] Saved " + str(len(db.objs)) + " points")

# Plotlib-Config
plt.axis([40000, 2000, 15, -10])
# plt.xscale("log", basex=2)
plt.xlabel("Temperature [K]") 
plt.ylabel("Magnitude")

plotPoints = db.GetPlotData()
plt.plot(plotPoints[0], plotPoints[1], "o", markersize=1)
print("Plotted " + str(len(plotPoints[0])) + " points")
plt.title("Star-Plotting of " + str(len(plotPoints[0])) + " objss") 

db.SaveDB()
print("[DB] Saved " + str(len(db.objsObjs)) + " points")

plt.show()