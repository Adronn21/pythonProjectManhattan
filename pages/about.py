import streamlit as st
from app import Navbar


def setup():
    st.set_page_config(layout="wide", page_title="Yearly index delta Graph", page_icon='ⓘ')
    st.header("ⓘAbout")
    return "Initialization done."

def main():
    # Execute setup function
    setup()
    Navbar()
if __name__ == "__main__":
    main()