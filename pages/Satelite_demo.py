import ee
import streamlit as st
import geemap.foliumap as geemap

# Function to get Sentinel-2 images by year.
def getSentinel2(year):
    # Import the Sentinel-2 collection.
    dataset = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")

    # Filter the collection by year and region.
    sentinel = dataset.filter(ee.Filter.calendarRange(year, year, 'year')) \
                      .filterBounds(astana_geometry) \
                      .median()  # Take the median to reduce cloud cover and other anomalies

    # Select the RGB bands.
    rgb = sentinel.select(['B4', 'B3', 'B2'])
    return rgb

st.header("Sentinel-2 Imagery")

# Create a layout containing two columns, one for the map and one for the layer dropdown list.
row1_col1, row1_col2 = st.columns([3, 1])

# Create an interactive map
Map = geemap.Map()

# Create a geometry object for the city of Astana
astana_geometry = ee.Geometry.Point(71.4306, 51.1694)  # Coordinates of the center of Astana

# Set the map center and zoom level to Astana
Map.centerObject(astana_geometry, zoom=12)  # Center the map on Astana with zoom level 12

# Select the available years for Sentinel-2 data.
years = list(range(2015, 2023))  # Sentinel-2 data is available from 2015 to the present

# Add a dropdown list and checkbox to the second column.
with row1_col2:
    selected_year = st.selectbox("Select a year", years)
    add_legend = st.checkbox("Show legend")

# Add selected Sentinel-2 image to the map based on the selected year.
if selected_year:
    Map.addLayer(getSentinel2(selected_year), {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}, "Sentinel-2 " + str(selected_year))

    if add_legend:
        Map.add_legend(
            title="Sentinel-2 RGB Composite",
            legend_dict={
                'Band B4 (Red)': 'red',
                'Band B3 (Green)': 'green',
                'Band B2 (Blue)': 'blue'
            }
        )
    with row1_col1:
        Map.to_streamlit(height=600)
else:
    with row1_col1:
        Map.to_streamlit(height=600)
