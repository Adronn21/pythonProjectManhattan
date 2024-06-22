import ee
import streamlit as st
import geemap.foliumap as geemap
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import zipfile
import tempfile
import os

test = st.multiselect('Test', ['1', '2', '3'])

st.write(test)

