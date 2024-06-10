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

# Button to process the file
if st.button("Process File"):
    # Check if a file is uploaded
    if uploaded_file is not None:
        # For CSV files
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.write("CSV file contents:")
            st.dataframe(df)

        # For Excel files
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
            st.write("Excel file contents:")
            st.dataframe(df)

        # For text files
        elif uploaded_file.name.endswith('.txt'):
            content = uploaded_file.read().decode('utf-8')
            st.write("Text file contents:")
            st.text(content)
    else:
        st.warning("Please upload a file before clicking the button.")
