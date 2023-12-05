import ifcopenshell
import ifcopenshell.util.element
import Helpers.Data_Helpers as hlp


def r9(model_paths):
    #Raumhöhen
    ifc_file = model_paths.NUM
    
    rel_spaces = []
    data_dict = {}
    data_dict_eval = {}
    false_data = []

    for space in ifc_file:
        if hasattr(space, 'IsDefinedBy'):
            for pset in space.IsDefinedBy:
                if pset.is_a('IfcRelDefinesByProperties'):
                    property_set = pset.RelatingPropertyDefinition
                    if property_set.is_a('IfcPropertySet'):
                        if property_set.Name == '_Baueingabe':
                            for property in property_set.HasProperties:
                                if property.Name == 'Nutzungstyp' and str(property.NominalValue.wrappedValue).upper() == "WOH":
                                    rel_spaces.append(space)

    for space in rel_spaces:
        infos = space.get_info()
        psets = ifcopenshell.util.element.get_psets(space, psets_only= False)

        _gid = infos.get("GlobalId")
        _hei = psets["Qto_SpaceBaseQuantities"]["Height"]

        data_dict[_gid] = [_hei]

        min_height = 2.10
        data_dict_eval[_gid] = min_height < _hei

    false_data = [id for id, value in data_dict_eval.items() if not value]
    print("Rule 9: Folgende Elemente unterschreiten die geltenden mindestanforderungen für Raumhöhen:")
    obj = [hlp.Raumhöhe(id) for id in false_data]

    object = hlp.Raumhöhe.get_instances()
    print(object)

    return false_data
