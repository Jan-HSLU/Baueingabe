import ifcopenshell
import ifcopenshell.util.element 
import Helpers.Data_Helpers as hlp

def r7(model_paths):
    #Parkplätze
    ifc_file = model_paths.NUM

    spaces = ifc_file.by_type("IfcSpace")

    auto_PPB = []
    velo_PPV = []
    pp_all = []

    for space in spaces:
        for pset in space.IsDefinedBy:
            if pset.is_a('IfcRelDefinesByProperties'):
                property_set = pset.RelatingPropertyDefinition
                if property_set.is_a('IfcPropertySet'):
                    if property_set.Name == '_Baueingabe':
                        for property in property_set.HasProperties:
                            if property.Name == 'Nutzungstyp' and str(property.NominalValue.wrappedValue).upper() == "PPB":
                                auto_PPB.append(space)

    for space in spaces:
        for pset in space.IsDefinedBy:
            if pset.is_a('IfcRelDefinesByProperties'):
                property_set = pset.RelatingPropertyDefinition
                if property_set.is_a('IfcPropertySet'):
                    if property_set.Name == '_Baueingabe':
                        for property in property_set.HasProperties:
                            if property.Name == 'Nutzungstyp' and str(property.NominalValue.wrappedValue).upper() == "PPV":
                                velo_PPV.append(space)

    auto_PPB_gesm = len(auto_PPB)
    velo_PPV_gesm = len(velo_PPV)

    #Soll-PP_auto
    all_flats = hlp.Wohnungsmix.get_gesamtzahl_aller_wohnungen()
    soll_PPB = all_flats * 1.1

    #Soll-PP_velo
    soll_PPV = hlp.Wohnungsmix.get_gesamtzahl_aller_zimmer()

    pp = hlp.Parkplatz(auto_PPB_gesm, soll_PPB, velo_PPV_gesm, soll_PPV)
    pp_all.append(pp)
    print("Rule 7: Es wurden folgende Parkplätze ermittelt:")
    print(pp)

    return pp_all