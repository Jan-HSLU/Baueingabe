import numpy as np
import plotly.graph_objects as go
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.placement

def getChildrenOfType(ifcParentElement, ifcType):
    items = []
    if type(ifcType) != list:
        #Abpacken des Types in eine Liste
        ifcType = [ifcType]
    _getChildrenOfType(items, ifcParentElement, ifcType, 0)
    return items


def _getChildrenOfType(targetList, element, ifcTypes, level):
    if element.is_a('IfcSpatialStructureElement'):
        for rel in element.ContainsElements or []:
            relatedElements = rel.RelatedElements
            for child in relatedElements:
                _getChildrenOfType(targetList, child, ifcTypes, level + 1)
    
    if element.is_a('IfcObjectDefinition'):
        for rel in element.IsDecomposedBy or []:
            relatedObjects = rel.RelatedObjects
            for child in relatedObjects:
                _getChildrenOfType(targetList, child, ifcTypes, level + 1)

    for typ in ifcTypes:
        if element.is_a(typ):
            targetList.append(element)


def plot_from_one_dic(faces_with_coords_by_building_id):
    min_coords, max_coords = None, None
    fig = go.Figure()

    for building_id, faces_list in faces_with_coords_by_building_id.items():
        for faces in faces_list:
            for face in faces:
                x = [vertex[0] for vertex in face]
                y = [vertex[1] for vertex in face]
                z = [vertex[2] for vertex in face]

                min_coords = np.minimum(min_coords, [min(x), min(y), min(z)]) if min_coords is not None else [min(x), min(y), min(z)]
                max_coords = np.maximum(max_coords, [max(x), max(y), max(z)]) if max_coords is not None else [max(x), max(y), max(z)]

                fig.add_trace(go.Mesh3d(
                    x=x, y=y, z=z,
                    color='black',
                    opacity=0.5
                ))

    spans = np.array(max_coords) - np.array(min_coords)
    if spans[2] == 0:
        spans[2] = max(spans[0], spans[1]) * 0.1
    ratio = spans / np.max(spans)

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='', showbackground=False, showticklabels=False, showgrid=False),
            yaxis=dict(title='', showbackground=False, showticklabels=False, showgrid=False),
            zaxis=dict(title='', showbackground=False, showticklabels=False, showgrid=False),
            aspectmode='manual', aspectratio=dict(x=ratio[0], y=ratio[1], z=ratio[2])
        ),
        title='',
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=0)
    )
    return fig


def plot_from_one_dic_one_list(faces_with_coords_by_building_id, additional_faces=None, additional_color='red'):
    min_coords, max_coords = None, None
    fig = go.Figure()

    for building_id, faces_list in faces_with_coords_by_building_id.items():
        for faces in faces_list:
            for face in faces:
                if not all(len(vertex) == 3 for vertex in face):
                    print(f"Fehlerhaftes Face gefunden in Gebäude {building_id}: {face}")
                    continue

                x = [vertex[0] for vertex in face]
                y = [vertex[1] for vertex in face]
                z = [vertex[2] for vertex in face]

                min_coords = np.minimum(min_coords, [min(x), min(y), min(z)]) if min_coords is not None else [min(x), min(y), min(z)]
                max_coords = np.maximum(max_coords, [max(x), max(y), max(z)]) if max_coords is not None else [max(x), max(y), max(z)]

                fig.add_trace(go.Mesh3d(x=x, y=y, z=z, color='black', opacity=1))

    if additional_faces is not None:
        for face in additional_faces:
            if not all(len(vertex) == 3 for vertex in face):
                print(f"Fehlerhaftes zusätzliches Face gefunden: {face}")
                continue

            x = [vertex[0] for vertex in face]
            y = [vertex[1] for vertex in face]
            z = [vertex[2] for vertex in face]

            fig.add_trace(go.Mesh3d(x=x, y=y, z=z, color=additional_color, opacity=0.1))

    spans = np.array(max_coords) - np.array(min_coords)
    if spans[2] == 0:
        spans[2] = max(spans[0], spans[1]) * 0.1
    ratio = spans / np.max(spans)

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='', showbackground=False, showticklabels=False, showgrid=False),
            yaxis=dict(title='', showbackground=False, showticklabels=False, showgrid=False),
            zaxis=dict(title='', showbackground=False, showticklabels=False, showgrid=False),
            aspectmode='manual', aspectratio=dict(x=ratio[0], y=ratio[1], z=ratio[2])
        ),
        title='',
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=0)
    )
    return fig


def plot_from_two_dic(faces_with_coords_by_building_id, additional_faces_with_coords=None, additional_color='red'):
    min_coords, max_coords = None, None
    fig = go.Figure()

    for building_id, faces_list in faces_with_coords_by_building_id.items():
        for faces in faces_list:
            for face in faces:
                if not all(len(vertex) == 3 for vertex in face):
                    print(f"Fehlerhaftes Face gefunden in Gebäude {building_id}: {face}")
                    continue

                x, y, z = zip(*face)
                min_coords, max_coords = update_min_max_coords(x, y, z, min_coords, max_coords)
                fig.add_trace(go.Mesh3d(x=x, y=y, z=z, color='black', opacity=0.8))

    if additional_faces_with_coords is not None:
        for building_id, faces_list in additional_faces_with_coords.items():
            for faces in faces_list:
                for face in faces:
                    if not all(len(vertex) == 3 for vertex in face):
                        print(f"Fehlerhaftes zusätzliches Face gefunden in Gebäude {building_id}: {face}")
                        continue

                    x, y, z = zip(*face)
                    min_coords, max_coords = update_min_max_coords(x, y, z, min_coords, max_coords)
                    fig.add_trace(go.Mesh3d(x=x, y=y, z=z, color=additional_color, opacity=1))

    spans = np.array(max_coords) - np.array(min_coords)
    if spans[2] == 0:
        spans[2] = max(spans[0], spans[1]) * 0.1
    ratio = spans / np.max(spans)

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='', showbackground=False, showticklabels=False, showgrid=False),
            yaxis=dict(title='', showbackground=False, showticklabels=False, showgrid=False),
            zaxis=dict(title='', showbackground=False, showticklabels=False, showgrid=False),
            aspectmode='manual', aspectratio=dict(x=ratio[0], y=ratio[1], z=ratio[2])
        ),
        title='',
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=0)
    )
    return fig

def update_min_max_coords(x, y, z, min_coords, max_coords):
    min_coords = np.minimum(min_coords, [min(x), min(y), min(z)]) if min_coords is not None else [min(x), min(y), min(z)]
    max_coords = np.maximum(max_coords, [max(x), max(y), max(z)]) if max_coords is not None else [max(x), max(y), max(z)]
    return min_coords, max_coords
