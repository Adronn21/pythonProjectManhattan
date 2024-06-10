import streamlit as st
import geemap.foliumap as geemap

st.title("Bekzhan's Interactive Map")
a=['1','2','3','4']
st.selectbox('test', a)
col1, col2 = st.columns([4, 1])
options = list(geemap.basemaps.keys())
index = options.index("OpenTopoMap")
a=['1','2','3','4']
st.selectbox('test', a)

with col2:

    basemap = st.selectbox("Select a basemap:", options, index)


with col1:

    m = geemap.Map()
    m.add_basemap(basemap)
    m.to_streamlit(height=700)
