import streamlit as st
import ifcopenshell
import Helpers.Data_Helpers as hlp

def read_data():
    st.set_page_config()
    st.sidebar.title("Willkommen zur Baueingabevorprüfung!")

    uploaded_files = st.sidebar.file_uploader("Dateien hochladen", accept_multiple_files=True, type=['ifc'])
    VOM_data, NUM_data, BAM_data = None, None, None
    ifcpaths = None 

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith("_VOM.ifc"):
                VOM_data = ifcopenshell.file.from_string(uploaded_file.getvalue().decode("utf-8"))
            elif uploaded_file.name.endswith("_NUM.ifc"):
                NUM_data = ifcopenshell.file.from_string(uploaded_file.getvalue().decode("utf-8"))
            elif uploaded_file.name.endswith("_BAM.ifc"):
                BAM_data = ifcopenshell.file.from_string(uploaded_file.getvalue().decode("utf-8"))

        if None not in [VOM_data, NUM_data, BAM_data]:
            ifcpaths = hlp.IfcPaths(VOM_data, NUM_data, BAM_data)
        else:
            st.sidebar.error("Es müssen genau drei Modelle eingelesen werden! Achte auf Schreibfehler.")

    return ifcpaths


if __name__ == "__main__":
    paths_list = read_data()