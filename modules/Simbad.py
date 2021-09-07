import requests, re, json

class Angle:
    def __init__(self, deg : int, min : int, sec : float):
        self.deg = deg
        self.min = min
        self.sec = sec

class AnglePair:
    def __init__(self, dec : Angle, asc : Angle):
        self.dec = dec
        self.asc = asc


SPEC_TYPE_REGEX = r"Spectral type:[ ]*?<\/SPAN>\n[ ]*?<\/TD>\n[ ]*?<TD>\n[ ]*?<B>\n[ ]*?<TT>\n(.*?)\n[ ]*?<\/TT>"
NAME_REGEX = r"<A HREF=\".*?\">NAME<\/A>(.*?)\n"
MAG_REGEX = r"V[ ]{1,}([\d\.]*?)[ ]"

KELVINS = {
    "M": lambda x: 2400 + 130*x,
    "K": lambda x: 3700 + 150*x,
    "G": lambda x: 5200 + 80*x,
    "F": lambda x: 6000 + 150*x,
    "A": lambda x: 7500 + 250*x,
    "B": lambda x: 10000 + 2000*x,
    "O": lambda x: 30000
}

class SpaceObject:
    """A space object gathered by the simbad databank"""
    def __init__(self, name : str = "", id : str = "", spec : str = "", magn : float = None) -> None:
        """
        Args:
            name (str): The name of the space-object
            id (str): The id of the space-object, e.g. HD xxxxxx for stars
            spec (str): The spectral type if the object is a star
            magn (float): [description]
        """
        self.name = name
        self.id = id
        self.spec = spec
        self.shortSpec = spec[0:2]
        self.magn = magn
        if ((re.search(r"\d", self.shortSpec) == None) & (len(self.shortSpec) != 0)):
            self.shortSpec = self.shortSpec[0] + "0"

    @staticmethod
    def ParseCSV(string : str):
        """Parses a starobject from a csv-string

        Args:
            string (str): The csv-string

        Returns:
            SpaceObject: The parsed spaceobejct
        """
        lineSplit = string.split(",")
        return SpaceObject(
            lineSplit[0],
            lineSplit[1],
            lineSplit[2],
            float(lineSplit[3])
        )

    def ParseHTML(id : str, string : str):
        nameReg = re.search(NAME_REGEX, string)
        specReg = re.search(SPEC_TYPE_REGEX, string)
        magReg = re.search(MAG_REGEX, string)
        name = ""
        spec = ""
        mag = None
        if nameReg != None:
            name = nameReg.groups()[0].strip()
        if specReg != None:
            spec = specReg.groups()[0].strip()
        if magReg != None:
            mag = float(magReg.groups()[0].strip())
        return SpaceObject(name, id, spec, mag)

    def ParseDict(pDict : dict):
        return SpaceObject(
            pDict["name"],
            pDict["id"],
            pDict["spec"],
            pDict["magn"]
        )

    def GetCSV(self) -> str:
        return f"${self.name},${self.id},${self.shortSpec},${self.magn}\n"

    def GetDict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "spec": self.spec,
            "magn": self.magn
        }

    def GetKelvin(self):
        return KELVINS[self.shortSpec[0]](int(self.shortSpec[1]))


class DataBank:
    def __init__(self) -> None:
        self.starObjs = { }
        self.path = ""

    def Append(self, star : SpaceObject):
        self.starObjs[star.id] = star

    def HasStar(self, id : str) -> bool:
        return (id in self.starObjs)

    def LoadDB(self, path : str):
        self.path = path
        try:
            jsonObjs = json.loads(open(path, "r").read())
            for obj in jsonObjs:
                self.starObjs[obj["id"]] = SpaceObject.ParseDict(obj)
        except FileNotFoundError:
            jFile = open(path, "w")
            jFile.write("[ ]")
            jFile.close()

    def SaveDB(self, path : str = ""):
        if path == "":
            if self.path != "":
                path = self.path
            else:
                raise Exception("No path specified")

        jsonItems = [ ]
        for key, value in self.starObjs.items():
            jsonItems.append(value.GetDict())
            
        jFile = open(path, "w")
        jFile.write(json.dumps(jsonItems))
        jFile.close()

    def IDRequest(self, id : str) -> SpaceObject:
        if self.HasStar(id): return self.starObjs[id]
        req = requests.get("http://simbad.u-strasbg.fr/simbad/sim-id?Ident=" + id.replace(" ", "+") + "&NbIdent=1&Radius=2&Radius.unit=arcmin&submit=submit+id")
        starObj = None
        if req.status_code == 200:
            starObj = SpaceObject.ParseHTML(id, req.text)
            self.Append(starObj)
        req.close()
        return starObj

    def GetPlotData(self):
        plotPoints = [ [ ], [ ] ]
        for key, star in self.starObjs.items():
            try:
                if star.magn != None:
                    plotPoints[0].append(star.GetKelvin())
                    plotPoints[1].append(star.magn) 
            except:
                pass
        return plotPoints
  
