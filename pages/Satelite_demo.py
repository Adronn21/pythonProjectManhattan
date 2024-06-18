import ee
import streamlit as st
import geemap.foliumap as geemap
import geopandas as gpd
import matplotlib.pyplot as plt
from io import BytesIO
import zipfile
import tempfile
import os

# Function to run once when page loads
def setup():
    st.set_page_config(layout="wide")
    st.header("Satellite Imagery")
    return "Initialization done."

# Main Streamlit app
def main():
    # Execute setup function
    setup_result = setup()
    row0_col1, row0_col2, row0_col3, row0_col4, row0_col5 = st.columns([1, 1, 1, 1, 1])
    row1_col1, row1_col2 = st.columns([4, 1])


    Map = geemap.Map()

    # Dictionary of datasets
    datasets = {
        'Sentinel-2': {
            'collection': 'COPERNICUS/S2_SR_HARMONIZED',
            'bands': ['B4', 'B3', 'B2', 'B8', 'B5'],  # bands: 0-Red, 1-Blue, 2-Green, 3-NIR, 4-Red Edge(or red)
            'year_range': [2019, 2023]
        },
        'Landsat-7': {
            'collection': 'LANDSAT/LE07/C02/T1_L2',
            'cloud_mask_band': 'QA_PIXEL',
            'cloud_mask_value': 1 << 1 | 1 << 3 | 1 << 4 | 1 << 5,
            'bands': ['SR_B3', 'SR_B2', 'SR_B1', 'SR_B4', "SR_B3"],  # bands: 0-Red, 1-Blue, 2-Green, 3-NIR, 4-Red Edge(or red)
            'year_range': [2000, 2023]
        },
        'Landsat-8': {
            'collection': 'LANDSAT/LC08/C02/T1_L2',
            'cloud_mask_band': 'QA_PIXEL',
            'cloud_mask_value': 1 << 1 | 1 << 2 | 1 << 3 | 1 << 4 | 1 << 5,
            'bands': ['SR_B4', 'SR_B3', 'SR_B2', "SR_B5", "SR_B4"],  # bands: 0-Red, 1-Blue, 2-Green, 3-NIR, 4-Red Edge(or red)
            'year_range': [2014, 2023]
        },
        'MODIS': {
            'collection': 'MODIS/006/MOD09GA',
            'cloud_mask_band': 'state_1km',
            'cloud_mask_value': 1 << 10 | 1 << 11,
            'bands': ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03', 'sur_refl_b02', 'sur_refl_b01'],  # 0-Red, 1-Blue, 2-Green, 3-NIR, 4-Red Edge(or red)
            'year_range': [2001, 2022]
        }
    }

    # Index definitions
    indexes = {
        "NDVI": "(NIR - RED) / (NIR + RED)",
        "EVI": "2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))",
        "SAVI": "((NIR - RED) / (NIR + RED + L)) * (1 + L)",
        "NDWI": "(GREEN - NIR) / (GREEN + NIR)",
        "GNDVI": "(NIR - GREEN) / (NIR + GREEN)",
        "NDRE": "(NIR - RED_EDGE) / (NIR + RED_EDGE)",
        "MSAVI2": "(2 * NIR + 1 - sqrt(pow((2 * NIR + 1), 2) - 8 * (NIR - RED)) ) / 2",
        "ARVI": "(NIR - (2 * RED - BLUE)) / (NIR + (2 * RED - BLUE))",
        "PRI": "(RED - BLUE) / (RED + BLUE)",
        "WBI": "NIR / GREEN"
    }

    # Function to mask clouds
    def mask_clouds(image, dataset):
        cloud_mask_band = datasets[dataset]['cloud_mask_band']
        cloud_mask_value = datasets[dataset]['cloud_mask_value']
        cloud_mask = image.select(cloud_mask_band).bitwiseAnd(cloud_mask_value).eq(0)
        return image.updateMask(cloud_mask)

    # Function to get filtered images
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

    # Function to add RGB layer to map
    def add_rgb_layer_to_map(m, satellite, year, region, brightness, clip, gamma):
        filtered_images = get_filtered_images(satellite, year, region)
        median_image = filtered_images.median()
        if clip:
            median_image = median_image.clip(region)
        rgb_bands = [datasets[satellite]['bands'][i] for i in range(0, 3)]

        vis_params = {
            'bands': rgb_bands,
            'min': 0,
            'max': int(brightness) * 1000,
            'gamma': gamma
        }

        layer = m.addLayer(median_image, vis_params, f'{satellite} {year} RGB')
        m.centerObject(region, 10)
        return layer

    # Function to calculate index
    def calc_index(satellite, index_name, year, region, clip):
        filtered_images = get_filtered_images(satellite, year, region)
        image = filtered_images.median()
        red_band = datasets[satellite]['bands'][0]
        blue_band = datasets[satellite]['bands'][1]
        green_band = datasets[satellite]['bands'][2]
        nir_band = datasets[satellite]['bands'][3]
        red_edge_band = datasets[satellite]['bands'][4]

        if clip:
            image = image.clip(region)

        index = image.expression(indexes[index_name], {
            'RED': image.select(red_band),
            'BLUE': image.select(blue_band),
            'GREEN': image.select(green_band),
            'NIR': image.select(nir_band),
            'RED_EDGE': image.select(red_edge_band),
            'L': 0.5
        })
        return index

    roi = None

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

    with row0_col1:
        sat = st.selectbox("Select a satellite", list(datasets.keys()), index=0)
    with row0_col2:
        years = list(range(datasets[sat]['year_range'][0], datasets[sat]['year_range'][1] + 1))
        selected_year = st.selectbox("Select a year", years, index=len(years) - 1)
    with row0_col3:
        brightness = st.text_input("Set brightness", value='3')
    with row0_col4:
        gamma = st.text_input("Set gamma", value='1.4')
    with row0_col5:
        clip = st.checkbox("Clip image")
    with row1_col2:
        check_index = st.checkbox("Add Index")
        if check_index:
            index_name = st.selectbox("Select an index", list(indexes.keys()), index=0)
            main_color = st.color_picker('Main color', value='#00ff00')
            mid_color = st.color_picker('Mid color', value='#ffff00')
            secondary_color = st.color_picker("Secondary color", value='#ff0000')

    if selected_year is not None and sat is not None and roi is not None:
        Map.centerObject(roi, zoom=10)
        # Add RGB layer
        add_rgb_layer_to_map(Map, sat, selected_year, roi, brightness, clip, gamma)
        # Add GeoDataFrame layer
        Map.add_gdf(gdf, 'polygon')
        # Add index layer if checked
        if check_index:
            Map.addLayer(calc_index(sat, index_name, selected_year, roi, clip),
                                       {'min': -1, 'max': 1, 'palette': [secondary_color, mid_color, main_color]},
                                       f'{index_name},{sat} {selected_year}')

    with row1_col1:
        Map.to_streamlit(height=600)

if __name__ == "__main__":
    main()
