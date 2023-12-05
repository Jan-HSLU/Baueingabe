import ifcopenshell
import ifcopenshell.util.element 
import Helpers.Data_Helpers as hlp

def r4(model_paths):
    # SIA416 Flächen
    ifc_file = model_paths.NUM
    
    spaces = ifc_file.by_type("IfcSpace")

    building_list = hlp.Umbauter_Raum.get_all_buildings()

    room_categories = {
        "hnf": ["WOH", "GEW", "DIL"],
        "nnf": ["PPA", "VEL", "KEL"],
        "vf": ["ERS"],
        "ff": ["RED", "TEC"],
        "agf": ["LOG", "AUS", " ", "None"]
    }

    #Arbeitsschirtt Listen
    guid_rooms = {}
    area_rooms = {}
    summed_areas = {}
    sia_objects = []

    for space in spaces:
        psets = ifcopenshell.util.element.get_psets(space)
        baueingabe_pset = psets.get("_Baueingabe")

        if baueingabe_pset:
            nutzungstyp = baueingabe_pset.get("Nutzungstyp")
            gebaeude_id = baueingabe_pset.get("Gebäude_ID")
            net_floor_area = psets.get("Qto_SpaceBaseQuantities").get("NetFloorArea") if psets.get("Qto_SpaceBaseQuantities") else None
            #Prüfen der Values, zum dazugehörenden Key - Filtert Räume weg wie PP die die Props nicht haben
            category = None
            for cat, types in room_categories.items():
                if nutzungstyp in types:
                    category = cat
                    break

            if category:
                if gebaeude_id not in guid_rooms:
                    guid_rooms[gebaeude_id] = {cat: [] for cat in room_categories}
                guid_rooms[gebaeude_id][category].append(space.GlobalId)
                #Zuweisen der Flächen über dict.comp
                if net_floor_area is not None:
                    if gebaeude_id not in area_rooms:
                        area_rooms[gebaeude_id] = {cat: [] for cat in room_categories}
                        summed_areas[gebaeude_id] = {cat: 0 for cat in room_categories}

                    area_rooms[gebaeude_id][category].append(net_floor_area)
                    summed_areas[gebaeude_id][category] += net_floor_area

    #Einlesen der GF ins dict zur später ermittlung der Konstruktionsfläche
    for building in building_list:
        geschossflaeche_obj = getattr(hlp.Geschossfläche, building, None)
        if geschossflaeche_obj is not None:
            geschossflaeche_value = geschossflaeche_obj.floor_area
            if building in summed_areas:
                summed_areas[building]["gf"] = geschossflaeche_value
    #print(summed_areas)

    print("Rule 4: Es wurden folgende SIA-416 Flächen ermittelt:")
    for building, areas in summed_areas.items():
        hnf = round(areas["hnf"], 2)
        nnf = round(areas["nnf"], 2)
        vf = round(areas["vf"], 2)
        ff = round(areas["ff"], 2)
        agf = round(areas["agf"], 2)
        gf = round(areas["gf"], 2)

        kf = round(gf - (hnf + nnf + vf + ff), 2)

        sia_obj = hlp.SIA_416(building, hnf, nnf, vf, ff, agf, kf)
        sia_objects.append(sia_obj)
        print(sia_obj)
        setattr(hlp.SIA_416, building, sia_obj)

    return sia_objects



