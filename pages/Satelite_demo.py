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
datasets = {
    'Landsat7': {
        'collection': 'LANDSAT/LE07/C02/T1_L2',
        'cloud_mask': lambda image: image.updateMask(image.select('QA_PIXEL').bitwiseAnd(1 << 3).eq(0))
    },
    'Landsat8': {
        'collection': 'LANDSAT/LC08/C02/T1_L2',
        'cloud_mask': lambda image: image.updateMask(image.select('QA_PIXEL').bitwiseAnd(1 << 3).eq(0))
    },
    'Sentinel2': {
        'collection': 'COPERNICUS/S2_SR_HARMONIZED',
        'cloud_mask': lambda image: image.updateMask(image.select('QA60').bitwiseAnd(1 << 10).eq(0).And(image.select('QA60').bitwiseAnd(1 << 11).eq(0)))
    },
    'MODIS': {
        'collection': 'MODIS/006/MOD09GA',
        'cloud_mask': lambda image: image.updateMask(image.select('state_1km').bitwiseAnd(1 << 10).eq(0))
    }
}
astana_geometry = ee.Geometry.Point(71.4306, 51.1694)


Map.centerObject(astana_geometry, zoom=12)



with row1_col2:
    sat = st.selectbox("Select a satelite", list(sat_names.keys()))

    years = list(range(sat_names[sat][2][0], sat_names[sat][2][1]))
    selected_year = st.selectbox("Select a year", years)

if selected_year:

    Map.addLayer(getSatelite(sat, selected_year, astana_geometry), {'bands': sat_names[sat][1], 'min': 0, 'max': 3000}, sat + str(selected_year))

    with row1_col1:
        map_state = Map.to_streamlit(height=600)
else:
    with row1_col1:
        map_state = Map.to_streamlit(height=600)

if st.button("Clear"):
    st.text('TEST')


# def filter_clouds(dataset_name, start_date, end_date):
#     dataset = datasets[dataset_name]
#     collection = ee.ImageCollection(dataset['collection']).filterDate(start_date, end_date)
#     masked_collection = collection.map(dataset['cloud_mask'])
#     return masked_collection
# Example usage
# landsat7_filtered = filter_clouds('Landsat7', '2023-01-01', '2023-12-31')
# landsat8_filtered = filter_clouds('Landsat8', '2023-01-01', '2023-12-31')
# sentinel2_filtered = filter_clouds('Sentinel2', '2023-01-01', '2023-12-31')
# modis_filtered = filter_clouds('MODIS', '2023-01-01', '2023-12-31')
