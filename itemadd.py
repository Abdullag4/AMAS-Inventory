import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def itemadd():
    """Page for adding new items to the inventory."""
    st.title("➕ Add New Item")

    item_name_en = st.text_input("Item Name (English)")
    item_name_ku = st.text_input("Item Name (Kurdish)")
    class_cat = st.text_input("Class Category")
    department_cat = st.text_input("Department Category")
    section_cat = st.text_input("Section Category")
    family_cat = st.text_input("Family Category")
    sub_family_cat = st.text_input("Sub-Family Category")
    shelf_life = st.number_input("Shelf Life (days)", min_value=0, step=1)
    origin_country = st.text_input("Origin Country")
    manufacturer = st.text_input("Manufacturer")
    brand = st.text_input("Brand")
    barcode = st.text_input("Barcode")
    unit_type = st.text_input("Unit Type")
    packaging = st.text_input("Packaging")
    item_picture = st.text_area("Item Picture URL")

    if st.button("Add Item"):
        item_data = (item_name_en, item_name_ku, class_cat, department_cat, section_cat, 
                     family_cat, sub_family_cat, shelf_life, origin_country, manufacturer, 
                     brand, barcode, unit_type, packaging, item_picture)
        
        db.add_item(item_data)
        st.success("Item added successfully!")

