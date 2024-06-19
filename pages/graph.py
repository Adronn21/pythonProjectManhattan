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

def setup():
    st.set_page_config(layout="wide", page_title="Graph", page_icon='📈')
    st.header("📈Graph")
    return "Initialization done."

def main():
    # Execute setup function
    setup_result = setup()
    Navbar()

if __name__ == "__main__":
    main()



