import streamlit as st
import geemap.foliumap as geemap
import pandas as pd

st.title("Bekzhan's Interactive Map")

a=['1','2','3','4']
st.selectbox('test', a)

col1, col2 = st.columns([4, 1])
options = list(geemap.basemaps.keys())
index = options.index("OpenTopoMap")

with col2:

    basemap = st.selectbox("Select a basemap:", options, index)


with col1:

    m = geemap.Map()
    m.add_basemap(basemap)
    m.to_streamlit(height=700)

# Add a file uploader to import files
uploaded_file = st.file_uploader("Choose a file", type=["xlsx"])

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.read()
    st.write("File content as bytes:")
    st.write(bytes_data)

    # For Excel files
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
        st.write("File content as a DataFrame:")
        st.write(df)