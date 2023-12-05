import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.placement
import ifcopenshell.util.element
import Helpers.Data_Helpers as hlp
import Helpers.Data_Functions as hlf
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

def r3(model_paths):
    #Überbauungsziffer
    ifc_file = model_paths.VOM
    ifc_file_policy = model_paths.BAM
    all_spaces = ifc_file.by_type("IfcSpace")
    site = ifc_file_policy.by_type("IfcSpace")

    storeys = [ifc_storey.Name for ifc_storey in ifc_file.by_type("IfcBuildingStorey")]
    building_list = hlp.Umbauter_Raum.get_all_buildings()
    settings = ifcopenshell.geom.settings()

    spaces_by_building_id = {building_id: [] for building_id in building_list}
    
    #UG Räume wegfiltern
    spaces_per_storey = {}
    spaces_in_099 = set()
    if "099" in storeys:
        for storey in ifc_file.by_type('IfcBuildingStorey'):
            spaces = hlf.getChildrenOfType(storey, 'IfcSpace')
            spaces_per_storey[storey] = spaces
            
            if storey.Name == "099":
                spaces_in_099.update(spaces)

            relev_spaces = list(set(all_spaces) - set(spaces_in_099))
    else:
        relev_spaces = all_spaces

    #Aussengeschossflächen wegfiltern
    filtered_spaces = []
    for space in relev_spaces:
        has_geschossflaeche_true = False
        for pset in space.IsDefinedBy:
            if pset.is_a('IfcRelDefinesByProperties'):
                property_set = pset.RelatingPropertyDefinition
                if property_set.is_a('IfcPropertySet') and property_set.Name == '_Baueingabe':
                    for property in property_set.HasProperties:
                        if property.Name == 'Geschossfläche' and str(property.NominalValue.wrappedValue).upper() == "TRUE":
                            has_geschossflaeche_true = True
                            break
            if has_geschossflaeche_true:
                break
        
        if has_geschossflaeche_true:
            filtered_spaces.append(space)
    
    relev_spaces = filtered_spaces

    # Zuordnen der gefilterten Räume zu den entsprechenden Gebäuden
    for space in relev_spaces:
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

    #Entfernen der nicht horizontalen Flächen
    for building_id, building_faces in faces_with_coords_by_building_id.items():
        for space_idx, space_faces in enumerate(building_faces):
            horizontal_faces = [face for face in space_faces if all(v[2] == face[0][2] for v in face)]
            faces_with_coords_by_building_id[building_id][space_idx] = horizontal_faces

    #Elemente auf Z Achse 0 setzen
    faces_with_z_zero_by_building_id = {}
    for building_id, building_faces in faces_with_coords_by_building_id.items():
        building_faces_with_z_zero = []
        for space_faces in building_faces:
            space_faces_with_z_zero = []
            for face in space_faces:
                face_with_z_zero = [[v[0], v[1], 0] for v in face]
                space_faces_with_z_zero.append(face_with_z_zero)
            building_faces_with_z_zero.append(space_faces_with_z_zero)
        faces_with_z_zero_by_building_id[building_id] = building_faces_with_z_zero

    #Mergen der Faces
    unified_area_by_building_id = {}
    for building_id, building_faces in faces_with_z_zero_by_building_id.items():
        polygons = []
        for space_faces in building_faces:
            for face in space_faces:
                polygon = Polygon(face)
                polygons.append(polygon)

        unified_polygon = unary_union(polygons)
        unified_area_by_building_id[building_id] = unified_polygon

    #for building_id, area in unified_area_by_building_id.items():
        #print(f" {building_id}: {area.area}")
   
    total_area = 0
    for building_id, area in unified_area_by_building_id.items():
        total_area += area.area
    total_area_of_buildings = total_area

    for space in site:
        psets = ifcopenshell.util.element.get_psets(space, psets_only= False)
        _gfa = psets["Qto_SpaceBaseQuantities"]["GrossFloorArea"]

    uez_ber = round(total_area_of_buildings / _gfa, 2)
    uez = hlp.Überbauungsziffer(uez_ber)
    print("Rule 3: Es wurden folgende Überbauungsziffer ermittelt:")
    print(uez_ber)

    #################################################################

    #Vertex der anrechenbaren Grundstücksfläche
    site_vertices = []
    for space in site:
        shape = ifcopenshell.geom.create_shape(settings, space)
        verts = shape.geometry.verts
        matrix = ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement)
        transformed_verts = [np.dot(matrix, np.array(list(verts[i:i+3]) + [1]))[:3] for i in range(0, len(verts), 3)]
        site_vertices.extend(transformed_verts)

    #Face der anrechenbaren Grundstücksfläche
    all_faces = []
    for space in site:
        shape = ifcopenshell.geom.create_shape(settings, space)
        faces = shape.geometry.faces
        grouped_faces = [faces[i:i+3] for i in range(0, len(faces), 3)]
        all_faces.extend(grouped_faces)

    #übertragen der Vertex-Koordinaten an die Idexes bei den Faces und Z-Achse auf 0 setzten
    faces_with_z_zero_coords = []
    for face in all_faces:
        face_with_z_zero_coords = [[vertex[0], vertex[1], 0] for vertex in (site_vertices[idx] for idx in face)]
        faces_with_z_zero_coords.append(face_with_z_zero_coords)

    return None