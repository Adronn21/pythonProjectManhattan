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

    st.header("Authors:")
    st.write("Baigabulov Adil")
    st.write("Bekenov Bekzhan")
    st.write("Ospanov Akhmet")
    st.markdown("<p style='text-align: right'>Group 05-057-21-05 \
                <br>The Department of Computer Science \
                <br>Kazakh Agro-Technical Research University\
                <br>Astana</p>",
                unsafe_allow_html=True)
    st.markdown("""Group 05-057-21-05""")
    st.markdown("""The Department of Computer Science""")
    st.markdown("""Kazakh Agro-Technical Research University""")
    st.markdown("""Astana""")
if __name__ == "__main__":
    main()
