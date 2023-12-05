import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.placement
import numpy as np
import Helpers.Data_Helpers as hlp


def r10(model_paths):
    #Grenzabstand
    ifc_file_VOM = model_paths.VOM
    ifc_file_BAM = model_paths.BAM

    baulinien = []
    settings = ifcopenshell.geom.settings()
    aabbs_VOM = {}
    aabbs_BAM = {}
    baulinien_verletzung = []

    for element in ifc_file_VOM.by_type('IfcSpace'):
        shape = ifcopenshell.geom.create_shape(settings, element)
        verts = shape.geometry.verts
        matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)

        transformed_verts = [np.dot(matrix, np.array(list(verts[i:i+3]) + [1]))[:3] for i in range(0, len(verts), 3)]
        min_coords = [min(v[i] for v in transformed_verts) for i in range(3)]
        max_coords = [max(v[i] for v in transformed_verts) for i in range(3)]
        aabbs_VOM[element.GlobalId] = (min_coords, max_coords)

    for element in ifc_file_BAM:
        if element.is_a('IfcSlab'):
            for pset in element.IsDefinedBy:
                if pset.is_a('IfcRelDefinesByProperties'):
                    property_set = pset.RelatingPropertyDefinition
                    if property_set.is_a('IfcPropertySet'):
                        if property_set.Name == '_Baueingabe':
                            for property in property_set.HasProperties:
                                if property.Name == 'Baurecht' and str(property.NominalValue.wrappedValue).upper() == "BL":
                                    baulinien.append(element)

    for element in baulinien:
        shape = ifcopenshell.geom.create_shape(settings, element)
        verts = shape.geometry.verts
        matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)

        transformed_verts = [np.dot(matrix, np.array(list(verts[i:i+3]) + [1]))[:3] for i in range(0, len(verts), 3)]
        min_coords = [min(v[i] for v in transformed_verts) for i in range(3)]
        max_coords = [max(v[i] for v in transformed_verts) for i in range(3)]
        aabbs_BAM[element.GlobalId] = (min_coords, max_coords)

    for id1, aabb1 in aabbs_VOM.items():
        for id2, aabb2 in aabbs_BAM.items():
            collision = not any(aabb1[0][i] > aabb2[1][i] or aabb2[0][i] > aabb1[1][i] for i in range(3))
            if collision:
                #print(f"Kollision zwischen IfcSpace {id1} aus VOM und IfcSlab {id2} aus BAM")
                baulinien_verletzung.append(id1)

    print("Rule 10: Folgende Elemente unterschreiten die geltenden Grenzabstände:")
    obj = [hlp.Grenzabstand(id) for id in baulinien_verletzung]

    object = hlp.Grenzabstand.get_instances()
    print(object)

    return baulinien_verletzung
