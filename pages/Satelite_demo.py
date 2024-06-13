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
        'cloud_mask_value': 1 << 5 | 1 << 3,  # Cloud confidence & cloud
        'rgb_bands': ['SR_B3', 'SR_B2', 'SR_B1'],  # Corrected RGB bands
        'year_range': [2000, 2023]
    },
    'Landsat-8': {
        'collection': 'LANDSAT/LC08/C02/T1_L2',
        'cloud_mask_band': 'QA_PIXEL',
        'cloud_mask_value': 1 << 5 | 1 << 3,  # Cloud confidence & cloud
        'rgb_bands': ['SR_B4', 'SR_B3', 'SR_B2'],  # Corrected RGB bands
        'year_range': [2014, 2023]
    },
    'Sentinel-2': {
        'collection': 'COPERNICUS/S2_SR_HARMONIZED',
        'rgb_bands': ['B4', 'B3', 'B2'],
        'year_range': [2019, 2023]
    },
    'MODIS': {
        'collection': 'MODIS/006/MOD09GA',
        'cloud_mask_band': 'state_1km',
        'cloud_mask_value': 1 << 10 | 1 << 11,  # Cloud state bits
        'rgb_bands': ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'],
        'year_range': [2001, 2022]
    }
}


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


def add_rgb_layer_to_map(m, satellite, year, region, brightness):
    filtered_images = get_filtered_images(satellite, year, region)
    median_image = filtered_images.median()
    rgb_bands = datasets[satellite]['rgb_bands']

    vis_params = {
        'bands': rgb_bands,
        'min': 0,
        'max': int(brightness)*1000,
        'gamma': 1.4
    }

    m.addLayer(median_image, vis_params, f'{satellite} {year} RGB')
    m.centerObject(region, 10)


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
    region = ee.geometry.geemap.geopandas_to_ee(gdf)

    Map.centerObject(region, zoom=12)

with row1_col2:
    brightness = st.text_input("Set brightness")
    sat = st.selectbox("Select a satelite", list(datasets.keys()))
    years = list(range(datasets[sat]['year_range'][0], datasets[sat]['year_range'][1]))
    selected_year = st.selectbox("Select a year", years)

if selected_year and sat and brightness and region:
    add_rgb_layer_to_map(Map, sat, selected_year, region, brightness)
    st.text(brightness)
    with row1_col1:
        Map.to_streamlit(height=600)
else:
    with row1_col1:
        Map.to_streamlit(height=600)
