import ee
import streamlit as st
import geemap.foliumap as geemap
import geopandas as gpd
import matplotlib.pyplot as plt
from io import BytesIO
import zipfile
import tempfile
import os
from app import Navbar, mask_clouds


def setup():
    st.set_page_config(layout="wide", page_title="Graph", page_icon='📈')
    st.header("📈Graph")
    return "Initialization done."
# Datasets
datasets = {
    'Sentinel-2': {
        'collection': 'COPERNICUS/S2_SR_HARMONIZED',
        'bands': ['B4', 'B3', 'B2', 'B8', 'B5'],  # bands: 0-Red, 1-Blue, 2-Green, 3-NIR, 4-Red Edge(or red)
        'year_range': [2019, 2023]
    },
    'Landsat-5': {
        'collection': 'LANDSAT/LT05/C02/T1_L2',
        'cloud_mask_band': 'QA_PIXEL',
        'cloud_mask_value': 1 << 1 | 1 << 3 | 1 << 4,
        'bands': ['SR_B3', 'SR_B2', 'SR_B1', 'SR_B4', "SR_B3"],
        # bands: 0-Red, 1-Blue, 2-Green, 3-NIR, 4-Red Edge(or red)
        'year_range': [1985, 2011]
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

# Indexes
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

def main():
    # Execute setup function
    setup()
    Navbar()
    row0_col1, row0_col2, row0_col3, row0_col4, row0_col5 = st.columns([1, 1, 1, 1, 1])
    row1_col1, row1_col2 = st.columns([5, 1])
    row2_col1, row2_col2, row2_col3 = st.columns([1, 1, 1])
    roi = None


    st.sidebar.markdown("""---""")
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
                plt.xticks(rotation=90, fontsize=7)
                plt.yticks(fontsize=7)

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

if __name__ == "__main__":
    main()



