import streamlit as st

# Import all the pages as modules
import home
import itemadd

# Streamlit page configuration
st.set_page_config(page_title="Inventory Management System", layout="wide")

def main():
    """
    Main entry point for the Inventory Management app.
    Handles navigation and rendering of different pages.
    """

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Add Item"])

    if page == "Home":
        home.home()  # Call the function inside home.py
    elif page == "Add Item":
        itemadd.itemadd()  # Call the function inside itemadd.py

if __name__ == "__main__":
    main()
