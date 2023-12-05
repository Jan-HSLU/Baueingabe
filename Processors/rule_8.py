import ifcopenshell
import ifcopenshell.util.element
import Helpers.Data_Helpers as hlp


def r8(model_paths):
    #Fensterflächenanteil
    ifc_file = model_paths.NUM

    rel_spaces = []
    data_dict = {}
    data_dict_factor = {}
    false_data = []

    for space in ifc_file:
        if hasattr(space, 'IsDefinedBy'):
            for pset in space.IsDefinedBy:
                if pset.is_a('IfcRelDefinesByProperties'):
                    property_set = pset.RelatingPropertyDefinition
                    if property_set.is_a('IfcPropertySet'):
                        if property_set.Name == '_Baueingabe':
                            for property in property_set.HasProperties:
                                if property.Name == 'Zimmer' and str(property.NominalValue.wrappedValue).upper() == "TRUE":
                                    rel_spaces.append(space)

    for space in rel_spaces:
        infos = space.get_info()
        psets = ifcopenshell.util.element.get_psets(space, psets_only= False)

        _gid = infos.get("GlobalId")
        _nfa = psets["Qto_SpaceBaseQuantities"]["NetFloorArea"]
        _fan = float(psets["_Baueingabe"]["Fensteranteil"])

        data_dict[_gid] = [_nfa, _fan]

        nfa_factor = _nfa * 0.1
        data_dict_factor[_gid] = nfa_factor < _fan

    false_data = [id for id, value in data_dict_factor.items() if not value]
    print("Rule 8: Folgende Elemente unterschreiten die geltenden mindestanforderungen für Fensterflächen:")
    obj = [hlp.Fensteranteil(id) for id in false_data]

    object = hlp.Fensteranteil.get_instances()
    print(object)

    return false_data