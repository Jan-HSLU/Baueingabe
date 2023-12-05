import ifcopenshell
import ifcopenshell.util.element
import Helpers.Data_Helpers as hlp

def r1(model_paths):
    #Umbauter Raum
    ifc_file = model_paths.VOM

    spaces = ifc_file.by_type("IfcSpace")
    temp_set = {}
    temp_set_fil_pro_geb = {}
    umbauter_raum = []

    for space in spaces:
        infos = space.get_info()
        psets = ifcopenshell.util.element.get_psets(space, psets_only= False)

        _gid = infos.get("GlobalId")
        _geb = psets["_Baueingabe"]["Gebäude_ID"]
        _gf = psets["_Baueingabe"]["Geschossfläche"]
        _gv = psets["Qto_SpaceBaseQuantities"]["GrossVolume"]

        temp_set[_gid] = [_geb, _gf, _gv]
    
    temp_set_fil = {key: value for key, value in temp_set.items() if value[1] == "TRUE"}

    #Erinnerung key = GUI / value = Liste der Eckdaten    
    for key, value in temp_set_fil.items():
        _geb_num = value[0]
    
        if _geb_num not in temp_set_fil_pro_geb:
            #Generieren von leeren Dicts mit Gebäudenummer
            temp_set_fil_pro_geb[_geb_num] = {}
        
        #Eintrag direkt ins subdict speichern. Dicts haben keine doppelten schlüssel.
        temp_set_fil_pro_geb[_geb_num][key] = value

    print("Rule 1: Es wurden folgende Faktoren für den umbauten Raum ermittelt:")
    for _geb_num, element in temp_set_fil_pro_geb.items():
        total_volume = round(sum([value[2] for value in element.values()]), 2)
    
        volume = hlp.Umbauter_Raum(_geb_num, total_volume)
        umbauter_raum.append(volume)
        print(volume)

        setattr(hlp.Umbauter_Raum, _geb_num, volume)
    #print(hlp.Umbauter_Raum.U)

    return umbauter_raum