import streamlit as st
import Helpers.Data_Helpers as hlp
import Helpers.Data_Functions as hlf
import pandas as pd
import plotly.express as px


def dashboard():
    st.header("**Faktoren**")
    col1, col2 = st.columns([2, 1])

    #Gebäudefaktoren
    with col1:
        ge_ele = hlp.Geschossfläche.get_instances()
        buildings_gf = [obj.building for obj in ge_ele]
        areas_gf = [f"{obj.floor_area} m²" for obj in ge_ele]

        buildings_ur = [instanz.building for instanz in hlp.Umbauter_Raum.all_instances.values()]
        volumes_ur = [f"{instanz.volume} m³" for instanz in hlp.Umbauter_Raum.all_instances.values()]

        data_ur = pd.DataFrame({'Gebäude': buildings_ur, 'Umbauter Raum': volumes_ur})
        datagf = pd.DataFrame({'Gebäude': buildings_gf, 'Geschossfläche': areas_gf})
        datagf = datagf.merge(data_ur, on='Gebäude')

        st.write(datagf.to_html(index=False), unsafe_allow_html=True)

    with col2:
        #ÜZ    
        ziffer = hlp.Überbauungsziffer.get_uez()
        st.metric(label="Überbauungsziffer ganze Parzelle", value=ziffer)
    
    st.write("")
    st.write("")


    #SIA 416
    st.header("Flächen nach SIA-416")
    st.write("**Auswertung der Flächen nach SIA 416 pro Gebäude in m\u00B2**")

    data = []
    for building in hlp.SIA_416.get_all_instances():
        data.append({
            'Gebäude': building.building,
            'HNF': building.hnf,
            'NNF': building.nnf,
            'VF': building.vf,
            'FF': building.ff,
            'AGF': building.agf,
            'KF': building.kf
        })

    df = pd.DataFrame(data)
    df_long = df.melt(id_vars=['Gebäude'], var_name='Flächentyp', value_name='Fläche in m\u00B2')
    df_long.sort_values(by='Gebäude', inplace=True)
    color_map = {
        'HNF': '#FF9688',
        'NNF': '#F5D073',
        'VF': '#F3F678',
        'FF': '#74D1F5',
        'AGF': '#9DD983',
        'KF': '#BA9E57'
    }

    fig = px.bar(df_long, x='Gebäude', y='Fläche in m\u00B2', color='Flächentyp', barmode='group', color_discrete_map=color_map)
    st.plotly_chart(fig, use_container_width=True)


    #Wohnungsanzahl
    st.header("Wohnungsspiegel")

    all_flats = hlp.Wohnungsmix.get_gesamtzahl_aller_wohnungen()
    st.metric(label="Anzahl der Wohnungen", value=all_flats)


    #Wohnungsmix
    data = []
    for building in hlp.Wohnungsmix.get_all_instances():
        data.extend([
            {'Gebäude': building.building, 'Wohnungstyp': '1.5 Zi-Whg.', 'Anzahl Wohnungen': building._ty15},
            {'Gebäude': building.building, 'Wohnungstyp': '2.5 Zi-Whg.', 'Anzahl Wohnungen': building._ty25},
            {'Gebäude': building.building, 'Wohnungstyp': '3.5 Zi-Whg.', 'Anzahl Wohnungen': building._ty35},
            {'Gebäude': building.building, 'Wohnungstyp': '4.5 Zi-Whg.', 'Anzahl Wohnungen': building._ty45},
            {'Gebäude': building.building, 'Wohnungstyp': '5.5 Zi-Whg.', 'Anzahl Wohnungen': building._ty55},
        ])

    df = pd.DataFrame(data)
    df.sort_values(by=['Gebäude', 'Wohnungstyp'], inplace=True)
    fig = px.bar(df, x='Wohnungstyp', y='Anzahl Wohnungen', color='Gebäude', barmode='group')
    st.plotly_chart(fig, use_container_width=True)


    #Zimmeranzahl
    st.header("Parkplätze")

    #Parkplätze
    ppa_ist = hlp.Parkplatz._instance.ppa_ist
    ppa_soll = hlp.Parkplatz._instance.ppa_soll
    ppv_ist = hlp.Parkplatz._instance.ppv_ist
    ppv_soll = hlp.Parkplatz._instance.ppv_soll

    data = [
        {'Typ': 'Auto', 'Kategorie': 'Ist', 'Anzahl Parkplätze': ppa_ist},
        {'Typ': 'Auto', 'Kategorie': 'Soll', 'Anzahl Parkplätze': ppa_soll},
        {'Typ': 'Velo', 'Kategorie': 'Ist', 'Anzahl Parkplätze': ppv_ist},
        {'Typ': 'Velo', 'Kategorie': 'Soll', 'Anzahl Parkplätze': ppv_soll},
    ]

    df = pd.DataFrame(data)

    fig = px.bar(df, x='Typ', y='Anzahl Parkplätze', color='Kategorie', barmode='group')

    st.plotly_chart(fig, use_container_width=True)


    #Fensterfläche
    st.header("Wohnraumvorschriften")

    fen_ele = hlp.Fensteranteil.get_instances()
    st.write("**Folgende Elemente unterschreiten die geltenden mindestanforderungen für Fensterflächen:**")
    st.write("*Die Baurechtsregelung sieht in Wohnräumen 10% der Raumfläche vor.*")
    st.text(fen_ele)

    #Raumhöhe
    raum_ele = hlp.Raumhöhe.get_instances()
    st.write("**Folgende Elemente unterschreiten die geltenden mindestanforderungen für Raumhöhen:**")
    st.write("*Die Baurechtsregelung sieht in Wohnräumen eine mindest Raumhöhe von 210 cm vor.*")
    st.text(raum_ele)


    #Grenzabstand
    st.header("Bauvorschriften (BETA)")

    gren_ele = hlp.Grenzabstand.get_instances()
    st.write("**Folgende Elemente unterschreiten die geltenden Grenzabstände:**")
    st.text(gren_ele)

    #Höhenbegrenzung
    hoh_ele = hlp.Höhenbegrenzung.get_instances()
    st.write("**Folgende Elemente überschreiten die geltenden Höhenbegrenzungen:**")
    st.text(hoh_ele)

    #3D-Grafik
    data = hlp.Höhenbegrenzung_geom.get_all_instances()
    if data:
        first_instance = data[0]
        vom_data = first_instance.vom
        bam_data = first_instance.bam

        fig = hlf.plot_from_two_dic(vom_data, additional_faces_with_coords=bam_data, additional_color='red')
        st.plotly_chart(fig, use_container_width=True)

    return None