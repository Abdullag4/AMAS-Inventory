import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def itemadd():
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
