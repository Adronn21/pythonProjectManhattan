import ee
import streamlit as st
import geemap.foliumap as geemap
import geopandas as gpd
import matplotlib.pyplot as plt
from io import BytesIO
import zipfile
import tempfile
import os
from app import Navbar
from app import datasets
from app import indexes
from app import mask_clouds
from app import get_filtered_images
from app import add_rgb_layer_to_map
from app import calc_index

def setup():
    st.set_page_config(layout="wide", page_title="Graph", page_icon='📈')
    st.header("📈Graph")
    return "Initialization done."

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



