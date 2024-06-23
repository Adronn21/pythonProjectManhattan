import streamlit as st
from app import Navbar


def setup():
    st.set_page_config(layout="wide", page_title="Yearly index delta Graph", page_icon='📖')
    st.header("📖About")
    return "Initialization done."

def main():
    # Execute setup function
    setup()
    Navbar()

    st.markdown("<H1>Authors:</H1>")
    st.markdown("""Baigabulov Adil""")
    st.markdown("""Bekenov Bekzhan""")
    st.markdown("""Ospan Akhmet""")
    st.markdown("""Group 05-057-21-05""")
    st.markdown("""The Department of Computer Science""")
    st.markdown("""Kazakh Agro-Technical Research University""")
    st.markdown("""Astana""")
if __name__ == "__main__":
    main()