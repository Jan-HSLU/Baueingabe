import ifcopenshell
import ifcopenshell.util.element 
import Helpers.Data_Helpers as hlp

def r5(model_paths):
    # Wohnungsmix
    ifc_file = model_paths.NUM
    
    spaces = ifc_file.by_type("IfcSpace")

    building_list = hlp.Umbauter_Raum.get_all_buildings()
    flat_type_list = ["1.5", "2.5", "3.5", "4.5", "5.5"]

    # Arbeitsschritt Listen
    fil_spaces = []
    flats_per_building = {}
    flats_per_building_anz = {}
    mix_objects = []

    for space in spaces:
        for pset in space.IsDefinedBy:
            if pset.is_a('IfcRelDefinesByProperties'):
                property_set = pset.RelatingPropertyDefinition
                if property_set.is_a('IfcPropertySet'):
                    if property_set.Name == '_Baueingabe':
                        for property in property_set.HasProperties:
                            if property.Name == 'Nutzungstyp' and str(property.NominalValue.wrappedValue).upper() == "WOH":
                                fil_spaces.append(space)

    for space in fil_spaces:
        psets = ifcopenshell.util.element.get_psets(space)
        baueingabe_pset = psets.get("_Baueingabe")

        if baueingabe_pset:
            building_id = baueingabe_pset.get("Gebäude_ID")
            flat_type = baueingabe_pset.get("Wohnungstyp")
            flat_id = baueingabe_pset.get("Einheit_ID")

            if building_id not in flats_per_building:
                flats_per_building[building_id] = {ftype: [] for ftype in flat_type_list}

            if flat_type not in flats_per_building[building_id]:
                flats_per_building[building_id][flat_type] = []

            if flat_id not in flats_per_building[building_id][flat_type]:
                flats_per_building[building_id][flat_type].append(flat_id)

    for building_id, types_dict in flats_per_building.items():
        flats_per_building_anz[building_id] = {flat_type: len(flat_ids) for flat_type, flat_ids in types_dict.items()}

    print("Rule 5: Es wurden folgender Wohnungsmix ermittelt:")
    for building, whg in flats_per_building_anz.items():
        _15 = whg["1.5"]
        _25 = whg["2.5"]
        _35 = whg["3.5"]
        _45 = whg["4.5"]
        _55 = whg["5.5"]

        mix_obj = hlp.Wohnungsmix(building, _15, _25, _35, _45, _55)
        mix_objects.append(mix_obj)
        print(mix_obj)
        setattr(hlp.Wohnungsmix, building, mix_obj)    


    return mix_objects