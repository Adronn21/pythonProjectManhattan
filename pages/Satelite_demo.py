import ee
import streamlit as st
import geemap.foliumap as geemap
import pandas as pd
import geopandas as gpd


st.set_page_config(layout="wide")
st.header("Satelite Imagery")
row1_col1, row1_col2 = st.columns([4, 1])

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
        'year_range': [2018, 2023]
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
    if satellite == 'Sentinel2':
        return filtered_images.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    else:
        return filtered_images.map(lambda image: mask_clouds(image, satellite))


def add_rgb_layer_to_map(m, satellite, year, region, brightness):
    filtered_images = get_filtered_images(satellite, year, region)
    median_image = filtered_images.median()
    rgb_bands = datasets[satellite]['rgb_bands']

    vis_params = {
        'bands': rgb_bands,
        'min': 0,
        'max': brightness,
        'gamma': 1.4
    }

    m.addLayer(median_image, vis_params, f'{satellite} {year} RGB')
    m.centerObject(region, 10)



region = ee.Geometry.Point([71.4306, 51.1694])

Map.centerObject(region, zoom=12)



with row1_col2:
    brightness = st.text_input("Set brightness")
    sat = st.selectbox("Select a satelite", list(datasets.keys()))
    years = list(range(datasets[sat]['year_range'][0], datasets[sat]['year_range'][1]))
    selected_year = st.selectbox("Select a year", years)

if selected_year and sat and brightness:
    add_rgb_layer_to_map(Map, sat, selected_year, region, brightness)

    with row1_col1:
        map_state = Map.to_streamlit(height=600)
else:
    with row1_col1:
        map_state = Map.to_streamlit(height=600)


uploaded_shp_file = st.sidebar.file_uploader("Shapefile", type=["shp"])

# Создание вкладки "Загрузка Shapefile"
if uploaded_shp_file is not None:

    # Загрузка Shapefile в GeoDataFrame
    gdf = gpd.read_file(uploaded_shp_file)

    # Просмотр загруженных данных (опционально)
    st.write("Пример первых строк данных:")
    st.write(gdf.head())
