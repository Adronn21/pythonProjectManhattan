import ee
import streamlit as st
import geemap.foliumap as geemap
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from io import BytesIO
import zipfile
import tempfile
import os

st.set_page_config(layout="wide")
st.header("Satelite Imagery")
row1_col1, row1_col2 = st.columns([4, 1])
row2_col1, row2_col2 = st.columns([4, 1])

Map = geemap.Map()

# Dictionary of datasets
datasets = {
    'Landsat-7': {
        'collection': 'LANDSAT/LE07/C02/T1_L2',
        'cloud_mask_band': 'QA_PIXEL',
        'cloud_mask_value': 1 << 5 | 1 << 3,
        'bands': ['SR_B3', 'SR_B2', 'SR_B1', ],# bands: 1-Red, 2-Blue, 3- Green, 4-NIR
        'year_range': [2000, 2023]
    },
    'Landsat-8': {
        'collection': 'LANDSAT/LC08/C02/T1_L2',
        'cloud_mask_band': 'QA_PIXEL',
        'cloud_mask_value': 1 << 5 | 1 << 3,
        'bands': ['SR_B4', 'SR_B3', 'SR_B2', "SR_B5"],# bands: 1-Red, 2-Blue, 3- Green, 4-NIR
        'year_range': [2014, 2023]
    },
    'Sentinel-2': {
        'collection': 'COPERNICUS/S2_SR_HARMONIZED',
        'bands': ['B4', 'B3', 'B2', 'B8'],# bands: 1-Red, 2-Blue, 3- Green, 4-NIR
        'year_range': [2019, 2023]
    },
    'MODIS': {
        'collection': 'MODIS/006/MOD09GA',
        'cloud_mask_band': 'state_1km',
        'cloud_mask_value': 1 << 10 | 1 << 11,
        'bands': ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'],# bands: 1-Red, 2-Blue, 3- Green, 4-NIR
        'year_range': [2001, 2022]
    }
}

indexes = ["NDVI", "EVI","SAVI", "NDWI", "GNDVI", "NDRE", "MSAVI2", "ARVI", "PRI", "WBI"]

def mask_clouds(image, dataset):
    cloud_mask_band = datasets[dataset]['cloud_mask_band']
    cloud_mask_value = datasets[dataset]['cloud_mask_value']
    cloud_mask = image.select(cloud_mask_band).bitwiseAnd(cloud_mask_value).eq(0)
    return image.updateMask(cloud_mask)


def get_filtered_images(satellite, year, region):
    dataset = datasets[satellite]
    collection = ee.ImageCollection(dataset['collection'])

    filtered_images = collection.filterBounds(region) \
        .filterDate(f'{year}-01-01', f'{year}-12-31')
    if satellite == 'Sentinel-2':
        return filtered_images.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                            .filter(ee.Filter.lt('SNOW_ICE_PERCENTAGE', 20))
    else:
        return filtered_images.map(lambda image: mask_clouds(image, satellite))


def add_rgb_layer_to_map(m, satellite, year, region, brightness, clip, gamma):
    filtered_images = get_filtered_images(satellite, year, region)
    median_image = filtered_images.median()
    if clip:
        median_image = median_image.clip(region)
    rgb_bands = [datasets[satellite]['bands'][i] for i in range(0, 3)]

    vis_params = {
        'bands': rgb_bands,
        'min': 0,
        'max': int(brightness)*1000,
        'gamma': gamma
    }

    m.addLayer(median_image, vis_params, f'{satellite} {year} RGB')
    m.centerObject(region, 10)

def calcIndex(satellite, index_name, year, region, clip):
    filtered_images = get_filtered_images(satellite, year, region)
    image = filtered_images.median()
    if clip:
        image = image.clip(region)
    if index_name == "NDVI":
        return image.normalizedDifference([datasets[satellite]['bands'][3], datasets[satellite]['bands'][0]]).rename('NDVI')
    else:
        return 0




roi = False
# Upload a zipped shapefile
uploaded_shp_file = st.sidebar.file_uploader("Upload a Zipped Shapefile", type=["zip"])

if uploaded_shp_file is not None:
    # Extract the zip file
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(uploaded_shp_file, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        # Find the shapefile within the extracted files
        shapefile_path = None
        for root, dirs, files in os.walk(tmpdir):
            for file in files:
                if file.endswith(".shp"):
                    shapefile_path = os.path.join(root, file)
                    break

        if shapefile_path:
            # Read the shapefile into a GeoDataFrame
            gdf = gpd.read_file(shapefile_path)

            # Create the plot
            fig, ax = plt.subplots()
            gdf.plot(ax=ax)

            # Save the plot to a BytesIO object
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            # Display the plot in Streamlit
            st.image(buf, caption='Geopandas Plot')
        else:
            st.error("Shapefile (.shp) not found in the uploaded zip file.")


        if not gdf.empty:
            roi = geemap.geopandas_to_ee(gdf)


check_index = False
with row1_col2:
    clip = st.checkbox("Clip image")
    brightness = st.text_input("Set brightness", value = 3)
    gamma = st.text_input("Set gamma", value = 1.4)
    sat = st.selectbox("Select a satelite", list(datasets.keys()))
    years = list(range(datasets[sat]['year_range'][0], datasets[sat]['year_range'][1]))
    selected_year = st.selectbox("Select a year", years)

    index_name = st.selectbox("Select an index", indexes, value=None)
    if st.button("Add Index"):
        calculated_index = calcIndex(sat, index_name, selected_year, roi, clip)
        Map.addLayer(calculated_index, {'min': -1, 'max': 1, 'palette': ['blue', 'white', 'green']}, 'Index')

if selected_year and sat and roi:
    Map.centerObject(roi, zoom=12)
    add_rgb_layer_to_map(Map, sat, selected_year, roi, brightness, clip, gamma)
    Map.add_gdf(gdf, 'poligon')
    with row1_col1:
        Map.to_streamlit(height=600)
else:
    with row1_col1:
        Map.to_streamlit(height=600)

