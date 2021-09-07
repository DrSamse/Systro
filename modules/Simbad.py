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
            id (str): The id of the space-object, e.g. HD xxxxxx for objs
            spec (str): The spectral type if the object is a obj
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
        """Parses a objobject from a csv-string

        Args:
            string (str): The csv-string

        Returns:
            SpaceObject: The parsed space object
        """
        lineSplit = string.split(",")
        return SpaceObject(
            lineSplit[0],
            lineSplit[1],
            lineSplit[2],
            float(lineSplit[3])
        )

    def ParseHTML(id : str, string : str):
        """Parses a space-object from a HTML-Files responded by the simbad-databank

        Args:
            id (str): The id of the object
            string (str): The HTML-File

        Returns:
            SpaceObject: The parsed space-object
        """
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
        """Parse a space-object by a dict

        Args:
            pDict (dict): The dict to parse the obj from

        Returns:
            SpaceObject: The parsed space-object
        """
        return SpaceObject(
            pDict["name"],
            pDict["id"],
            pDict["spec"],
            pDict["magn"]
        )

    def GetCSV(self) -> str:
        """Get the CSV-string

        Returns:
            str: The CSV-String
        """
        return f"${self.name},${self.id},${self.shortSpec},${self.magn}\n"

    def GetDict(self) -> dict:
        """Get the Dict-value of the object

        Returns:
            dict: The dict
        """
        return {
            "name": self.name,
            "id": self.id,
            "spec": self.spec,
            "magn": self.magn
        }

    def GetKelvin(self) -> float:
        """Get the kelvin surface temperature of the space-object by the spectral-class

        Returns:
            float: The Kelvins
        """
        return KELVINS[self.shortSpec[0]](int(self.shortSpec[1]))


class DataBank:
    """A space-object data. It enables communication with the SIMBAD-databank online
    """
    def __init__(self) -> None:
        self.objs = { }
        self.path = ""

    def Append(self, obj : SpaceObject):
        """Append a spaceobject

        Args:
            obj (SpaceObject): The obj to append
        """
        self.objs[obj.id] = obj

    def HasObj(self, id : str) -> bool:
        """Check if the databank has a object with the given id

        Args:
            id (str): The id to check

        Returns:
            bool: Whether the data bank has a star with the given id or not
        """
        return (id in self.objs)

    def LoadDB(self, path : str):
        """Loads the data-bank from a .sdb-file, the given path is saved and used for saving if not specified otherwise 

        Args:
            path (str): The path to the .sdb-file
        """
        self.path = path
        try:
            jsonObjs = json.loads(open(path, "r").read())
            for obj in jsonObjs:
                self.objs[obj["id"]] = SpaceObject.ParseDict(obj)
        except FileNotFoundError:
            jFile = open(path, "w")
            jFile.write("[ ]")
            jFile.close()
        return self

    def SaveDB(self, path : str = ""):
        """Saves the data bank to the given .sdb-file

        Args:
            path (str, optional): The path to save the data bank to, . Defaults to "".

        Raises:
            Exception: [description]
        """
        if path == "":
            if self.path != "":
                path = self.path
            else:
                raise Exception("No path specified")

        jsonItems = [ ]
        for key, value in self.objs.items():
            jsonItems.append(value.GetDict())
            
        jFile = open(path, "w")
        jFile.write(json.dumps(jsonItems))
        jFile.close()

    def IDRequest(self, id : str) -> SpaceObject:
        """

        Args:
            id (str): [description]

        Returns:
            SpaceObject: [description]
        """
        if self.HasObj(id): return self.objs[id]
        req = requests.get("http://simbad.u-strasbg.fr/simbad/sim-id?Ident=" + id.replace(" ", "+") + "&NbIdent=1&Radius=2&Radius.unit=arcmin&submit=submit+id")
        objObj = None
        if req.status_code == 200:
            objObj = SpaceObject.ParseHTML(id, req.text)
            self.Append(objObj)
        req.close()
        return objObj

    def GetPlotData(self):
        plotPoints = [ [ ], [ ] ]
        for key, obj in self.objs.items():
            try:
                if obj.magn != None:
                    plotPoints[0].append(obj.GetKelvin())
                    plotPoints[1].append(obj.magn) 
            except:
                pass
        return plotPoints
  
