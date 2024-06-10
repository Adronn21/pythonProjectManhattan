import streamlit as st
import geemap.foliumap as geemap
import pandas as pd

# Title of the Streamlit app
st.title("Bekzhan's Interactive Map")

# A simple select box with test values
a = ['1', '2', '3', '4']
st.selectbox('Select a value', a)

# Creating two columns with a 4:1 ratio
col1, col2 = st.columns([4, 1])

# Getting the list of available basemaps and finding the index for OpenTopoMap
options = list(geemap.basemaps.keys())
index = options.index("OpenTopoMap")

# Select box for choosing a basemap, placed in the smaller column (col2)
with col2:
    basemap = st.selectbox("Select a basemap:", options, index)

# Map display in the larger column (col1)
with col1:
    m = geemap.Map()
    m.add_basemap(basemap)
    m.to_streamlit(height=700)

# File uploader for Excel files
uploaded_file = st.file_uploader("Choose a file", type=["xlsx"])

if uploaded_file is not None:
    # Reading the file as bytes
    bytes_data = uploaded_file.read()
    st.write("File content as bytes:")
    st.write(bytes_data)

    # Reading the file into a DataFrame if it's an Excel file
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
        st.write("File content as a DataFrame:")
        st.write(df)
