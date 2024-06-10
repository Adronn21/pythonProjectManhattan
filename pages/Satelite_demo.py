import ee
import streamlit as st
import geemap.foliumap as geemap

def getSatelite(satelite, year, geometry):
    # Import the image collection.
    sat_filtered = ee.ImageCollection(sat_names[satelite][0]) \
                    .filter(ee.Filter.calendarRange(f'{year}-01-01', f'{year}-12-31')) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                    .filterBounds(geometry) \
                    .median()

    return sat_filtered.select(sat_names[satelite][1])

st.header("Satelite Imagery")

sat_names = {"Landsat-8":["LANDSAT/LC08/C02/T1_L2", ['SR_B4', 'SR_B3', 'SR_B2'], [2014, 2023]],
            "Sentinel-2":["COPERNICUS/S2_SR_HARMONIZED", ['B4', 'B3', 'B2'], [2018, 2023]]
}

# Create an interactive map
Map = geemap.Map()

# Create a layout containing two columns, one for the map and one for the layer dropdown list.
row1_col1, row1_col2 = st.columns([3, 1])





# Create a geometry object for the city of Astana
astana_geometry = ee.Geometry.Point(71.4306, 51.1694)  # Coordinates of the center of Astana

# Set the map center and zoom level to Astana
Map.centerObject(astana_geometry, zoom=12)  # Center the map on Astana with zoom level 12



# Add a dropdown list and checkbox to the second column.
with row1_col2:
    sat = st.selectbox("Select a satelite", sat_names.keys())
    # Select the available years.
    years = list(range(sat_names[sat][2][0], sat_names[sat][2][1]))
    selected_year = st.selectbox("Select a year", years)



if selected_year:
    Map.addLayer(getSatelite(sat, selected_year, astana_geometry), {'bands': sat_names[sat][1], 'min': 0, 'max': 3000}, sat + str(selected_year))

    with row1_col1:
        Map.to_streamlit(height=600)
else:
    with row1_col1:
        Map.to_streamlit(height=600)
