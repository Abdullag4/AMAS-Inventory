import streamlit as st
import home
import itemadd

st.set_page_config(page_title="Inventory Management System", layout="wide")

def main():
    """Main entry point for the Inventory Management app."""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Add Item"])

    if page == "Home":
        home.home()
    elif page == "Add Item":
        itemadd.itemadd()

if __name__ == "__main__":
    main()
