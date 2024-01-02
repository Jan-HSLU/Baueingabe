class IfcPaths:
    def __init__(self, VOM, NUM, BAM):
        self.VOM = VOM
        self.NUM = NUM
        self.BAM = BAM

    def __str__(self):
        return f"VOM: {self.VOM}\nNUM: {self.NUM}\nBAM: {self.BAM}"


class Geschossfläche:
    instances = {}

    def __init__(self, building, floor_area):
        self.building = building
        self.floor_area = floor_area
        Geschossfläche.instances[building] = self

    def __str__(self):
        return f"Gebäude: {self.building}, Geschossfläche: {self.floor_area}m\u00B2"

    @classmethod
    def get_instances(cls):
        return cls.instances.values()


class Umbauter_Raum:
    all_buildings = set()
    all_instances = {}

    def __init__(self, building, volume):
        self.building = building
        self.volume = volume
        Umbauter_Raum.all_buildings.add(building)
        Umbauter_Raum.all_instances[building] = self

    def __str__(self):
        return f"Gebäude: {self.building}, Volumen: {self.volume}m\u00B3"

    @classmethod
    def get_all_buildings(cls):
        return list(cls.all_buildings)


class Überbauungsziffer:
    ueberbauungsziffer= []

    def __init__(self, uez):
        self.uez = uez
        Überbauungsziffer.ueberbauungsziffer.append(uez)

    @classmethod
    def get_uez(cls):
        if cls.ueberbauungsziffer:
            return cls.ueberbauungsziffer[0]
        return None

    def __str__(self):
        return f"Überbauungsziffer Parzelle: {self.uez}"


class SIA_416:
    instances = {}

    def __init__(self, building, hnf, nnf, vf, ff, agf, kf):
        self.building = building
        self.hnf = hnf
        self.nnf = nnf
        self.vf = vf
        self.ff = ff
        self.agf = agf
        self.kf = kf
        SIA_416.instances[building] = self

    def __str__(self):
        return f"Gebäude: {self.building}, HNF: {self.hnf}m\u00B2, NNF: {self.nnf}m\u00B2, VF: {self.vf}m\u00B2, FF: {self.ff}m\u00B2, AGF: {self.agf}m\u00B2, KF: {self.kf}m\u00B2"

    @classmethod
    def get_all_instances(cls):
        return cls.instances.values()
    

class Wohnungsmix:
    instances = {}

    def __init__(self, building, _ty15, _ty25, _ty35, _ty45, _ty55):
        self.building = building
        self._ty15 = _ty15
        self._ty25 = _ty25
        self._ty35 = _ty35
        self._ty45 = _ty45
        self._ty55 = _ty55
        Wohnungsmix.instances[building] = self
    
    def __str__(self):
        return f"Gebäude: {self.building}, 1.5 Zi-Whg.: {self._ty15}, 2.5 Zi-Whg.: {self._ty25}, 3.5 Zi-Whg.: {self._ty35}, 4.5 Zi-Whg.: {self._ty45}, 5.5 Zi-Whg.: {self._ty55}"

    @classmethod
    def get_gesamtzahl_aller_wohnungen(cls):
        return sum(sum([inst._ty15, inst._ty25, inst._ty35, inst._ty45, inst._ty55]) for inst in cls.instances.values())
    
    @classmethod
    def get_gesamtzahl_aller_zimmer(cls):
        return sum(inst.berechne_zimmer() for inst in cls.instances.values())
    
    def berechne_zimmer(self):
        zimmer = (self._ty15 * 1.5) + (self._ty25 * 2.5) + (self._ty35 * 3.5) + (self._ty45 * 4.5) + (self._ty55 * 5.5)
        return zimmer

    @classmethod
    def get_all_instances(cls):
        return cls.instances.values()

    
class Parkplatz:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Parkplatz, cls).__new__(cls)
        return cls._instance

    def __init__(self, ppa_ist, ppa_soll, ppv_ist, ppv_soll):
        self.ppa_ist = ppa_ist
        self.ppa_soll = ppa_soll
        self.ppv_ist = ppv_ist
        self.ppv_soll = ppv_soll

    def __str__(self):
        return f"Auto: Es gibt {self.ppa_ist} von {self.ppa_soll} geforderten. Velo: Es gibt {self.ppv_ist} von {self.ppv_soll} geforderten."


class Fensteranteil:
    instances = []

    def __init__(self, guid):
        self.guid = guid
        if not self._instance_exists(guid):
            Fensteranteil.instances.append(self)

    def __str__(self):
        return f"{self.guid}"

    @classmethod
    def get_instances(cls):
        if not cls.instances:
            return "Es gibt keine."
        else:
            return "\n".join(str(instance) for instance in cls.instances)

    @classmethod
    def _instance_exists(cls, guid):
        return any(instance.guid == guid for instance in cls.instances)


class Raumhöhe: 
    instances = []

    def __init__(self, guid):
        self.guid = guid
        if not self._instance_exists(guid):
            Raumhöhe.instances.append(self)

    def __str__(self):
        return f"{self.guid}"

    @classmethod
    def get_instances(cls):
        if not cls.instances:
            return "Es gibt keine."
        else:
            return "\n".join(str(instance) for instance in cls.instances)  
    
    @classmethod
    def _instance_exists(cls, guid):
        return any(instance.guid == guid for instance in cls.instances)


class Grenzabstand:
    instances = []

    def __init__(self, guid):
        self.guid = guid
        if not self._instance_exists(guid):
            Grenzabstand.instances.append(self)

    def __str__(self):
        return f"{self.guid}"

    @classmethod
    def get_instances(cls):
        if not cls.instances:
            return "Es gibt keine."
        else:
            return "\n".join(str(instance) for instance in cls.instances)
    
    @classmethod
    def _instance_exists(cls, guid):
        return any(instance.guid == guid for instance in cls.instances)
    

class Höhenbegrenzung:
    instances = []

    def __init__(self, guid):
        self.guid = guid
        if not self._instance_exists(guid):
            Höhenbegrenzung.instances.append(self)

    def __str__(self):
        return f"{self.guid}"
    
    @classmethod
    def get_instances(cls):
        if not cls.instances:
            return "Es gibt keine."
        else:
            return "\n".join(str(instance) for instance in cls.instances)
    
    @classmethod
    def _instance_exists(cls, guid):
        return any(instance.guid == guid for instance in cls.instances)

    
class Höhenbegrenzung_geom:
    instances = []

    def __init__(self, vom, bam):
        self.vom = vom
        self.bam = bam
        Höhenbegrenzung_geom.instances.append(self)

    def __str__(self):
        return " "
    
    @classmethod
    def get_all_instances(cls):
        return cls.instances
