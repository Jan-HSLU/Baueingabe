import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.placement
import numpy as np
import Helpers.Data_Helpers as hlp
import Helpers.Data_Functions as hlf
import streamlit as st

def r11(model_paths):
    #Höhenbegrenzung
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
                                if property.Name == 'Baurecht' and str(property.NominalValue.wrappedValue).upper() == "HB":
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

    print("Rule 11: Folgende Elemente überschreiten die geltenden Höhenbegrenzungen:")
    obj = [hlp.Höhenbegrenzung(id) for id in baulinien_verletzung]

    object = hlp.Höhenbegrenzung.get_instances()
    print(object)
    

    #Datenextraktion für spätere Darstellung 
    Modell = ifc_file_VOM.by_type("IfcSpace")
    baurecht = ifc_file_BAM.by_type("IfcSlab")
    building_list = hlp.Umbauter_Raum.get_all_buildings()
    spaces_by_building_id = {building_id: [] for building_id in building_list}
    settings = ifcopenshell.geom.settings()
    

    # Zuordnen der Räume zu den entsprechenden Gebäuden
    for space in Modell:
        for prop_set in space.IsDefinedBy:
            if prop_set.is_a('IfcRelDefinesByProperties'):
                properties = prop_set.RelatingPropertyDefinition
                if properties.is_a('IfcPropertySet'):
                    for prop in properties.HasProperties:
                        if prop.Name == 'Gebäude_ID':
                            building_id = prop.NominalValue.wrappedValue
                            if building_id in building_list:
                                spaces_by_building_id[building_id].append(space)

    #Vertex pro Space und Gebäude als koordinate xyz
    vertices_by_building_id = {}
    for building_id, spaces in spaces_by_building_id.items():
        building_vertices = []
        for space in spaces:
            shape = ifcopenshell.geom.create_shape(settings, space)
            verts = shape.geometry.verts
            matrix = ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement)
            transformed_verts = [np.dot(matrix, np.array(list(verts[i:i+3]) + [1]))[:3] for i in range(0, len(verts), 3)]
            building_vertices.append(transformed_verts)
        vertices_by_building_id[building_id] = building_vertices

    #Faces pro Space und Gebäude als Triangulierung
    faces_by_building_id = {}
    for building_id, spaces in spaces_by_building_id.items():
        building_faces = []
        for space in spaces:
            shape = ifcopenshell.geom.create_shape(settings, space)
            faces = shape.geometry.faces
            grouped_faces = [faces[i:i+3] for i in range(0, len(faces), 3)]
            building_faces.append(grouped_faces)
        faces_by_building_id[building_id] = building_faces

    #Übertragen der Vertex-Koordinaten an die Idexes bei den Faces
    faces_with_coords_by_building_id = {}
    for building_id in faces_by_building_id:
        building_faces_with_coords = []
        for space_idx, space_faces in enumerate(faces_by_building_id[building_id]):
            space_faces_with_coords = []
            for face in space_faces:
                face_coords = [vertices_by_building_id[building_id][space_idx][idx] for idx in face]
                space_faces_with_coords.append(face_coords)
            building_faces_with_coords.append(space_faces_with_coords)
        faces_with_coords_by_building_id[building_id] = building_faces_with_coords


    #Zuordnen der Elemente zu den Baurechten
    baurecht_dict = {}
    for element in baurecht:
        if element.is_a('IfcSlab'):
            for pset in element.IsDefinedBy:
                if pset.is_a('IfcRelDefinesByProperties'):
                    property_set = pset.RelatingPropertyDefinition
                    if property_set.is_a('IfcPropertySet'):
                        if property_set.Name == '_Baueingabe':
                            for property in property_set.HasProperties:
                                if property.Name == 'Baurecht':
                                    baurecht_value = str(property.NominalValue.wrappedValue)
                                    if baurecht_value not in baurecht_dict:
                                        baurecht_dict[baurecht_value] = []
                                    baurecht_dict[baurecht_value].append(element)

    #Erhalten der Vertex der Baurechtelemente
    bre_vertices_by_building_id = {}
    for baurecht_value, slabs in baurecht_dict.items():
        building_vertices = []
        for slab in slabs:
            shape = ifcopenshell.geom.create_shape(settings, slab)
            verts = shape.geometry.verts
            matrix = ifcopenshell.util.placement.get_local_placement(slab.ObjectPlacement)
            transformed_verts = [np.dot(matrix, np.array(list(verts[i:i+3]) + [1]))[:3] for i in range(0, len(verts), 3)]
            building_vertices.append(transformed_verts)
        bre_vertices_by_building_id[baurecht_value] = building_vertices

    #Erhaltne der Faces als Triangulierung
    bre_faces_by_building_id = {}
    for building_id, spaces in baurecht_dict.items():
        building_faces = []
        for space in spaces:
            shape = ifcopenshell.geom.create_shape(settings, space)
            faces = shape.geometry.faces
            grouped_faces = [faces[i:i+3] for i in range(0, len(faces), 3)]
            building_faces.append(grouped_faces)
        bre_faces_by_building_id[building_id] = building_faces

    #Übertragen der Vertex-Koordinaten an die Idexes bei den Faces
    bre_faces_with_coords_by_building_id = {}
    for building_id in bre_faces_by_building_id:
        building_faces_with_coords = []
        for space_idx, space_faces in enumerate(bre_faces_by_building_id[building_id]):
            space_faces_with_coords = []
            for face in space_faces:
                face_coords = [bre_vertices_by_building_id[building_id][space_idx][idx] for idx in face]
                space_faces_with_coords.append(face_coords)
            building_faces_with_coords.append(space_faces_with_coords)
        bre_faces_with_coords_by_building_id[building_id] = building_faces_with_coords


    data = hlp.Höhenbegrenzung_geom(faces_with_coords_by_building_id,bre_faces_with_coords_by_building_id)

    return baulinien_verletzung