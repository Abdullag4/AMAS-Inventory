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
        item_data = {
            "ItemNameEnglish": item_name_en,
            "ItemNameKurdish": item_name_ku,
            "ClassCat": class_cat,
            "DepartmentCat": department_cat,
            "SectionCat": section_cat,
            "FamilyCat": family_cat,
            "SubFamilyCat": sub_family_cat,
            "ShelfLife": shelf_life,
            "OriginCountry": origin_country,
            "Manufacturer": manufacturer,
            "Brand": brand,
            "Barcode": barcode,
            "UnitType": unit_type,
            "Packaging": packaging,
            "ItemPicture": item_picture
        }
        
        db.add_item(item_data)  # ✅ Now works dynamically
        st.success("Item added successfully!")
