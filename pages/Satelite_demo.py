import ee
import streamlit as st
import geemap.foliumap as geemap
import pandas as pd
import geopandas as gpd


st.set_page_config(layout="wide")
st.header("Satelite Imagery")
row1_col1, row1_col2 = st.columns([4, 1])

Map = geemap.Map()



def getSatelite(satelite, year, geometry):
    sat_filtered = ee.ImageCollection(sat_names[satelite][0]) \
                    .filterDate(f'{year}-01-01', f'{year}-12-31') \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                    .filterBounds(geometry) \
                    .median()

    return sat_filtered

sat_names = {"Sentinel-2":["COPERNICUS/S2_SR_HARMONIZED", ['B4', 'B3', 'B2'], [2018, 2024]],
            "Landsat-9":["LANDSAT/LC08/C02/T1_L2", ['SR_B4', 'SR_B3', 'SR_B2'], [2014, 2024]]
}

astana_geometry = ee.Geometry.Point(71.4306, 51.1694)


Map.centerObject(astana_geometry, zoom=12)

if st.button('Add layer'):

    Map.addLayer(getSatelite(sat, selected_year, astana_geometry), {'bands': sat_names[sat][1], 'min': 0, 'max': 3000}, sat + str(selected_year))
    with row1_col1:
        map_state = Map.to_streamlit(height=600)
else:
    with row1_col1:
        map_state = Map.to_streamlit(height=600)

with row1_col2:
    sat = st.selectbox("Select a satelite", list(sat_names.keys()))

    years = list(range(sat_names[sat][2][0], sat_names[sat][2][1]))
    selected_year = st.selectbox("Select a year", years)



# Function to clear selected layers
def clear_layers(map_object):
    layers_to_keep = ['OpenStreetMap']
    layers_to_remove = [layer for layer in map_object.get_layer_names() if layer not in layers_to_keep]
    for layer_name in layers_to_remove:
        map_object.remove_layer(map_object.find_layer(layer_name))

# Create a button to clear selected layers
if st.button('Clear Selected Layers'):
    # Preserve the current location and zoom level
    current_location = map_state['center']
    current_zoom = map_state['zoom']

    # Clear the selected layers
    clear_layers(Map)

    # Reinitialize the map with preserved location and zoom level
    Map = geemap.Map(center=current_location, zoom=current_zoom)
    st.write("Selected layers cleared.")

    # Display the map again
    Map.to_streamlit(height=600)


