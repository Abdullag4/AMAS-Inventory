import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Create a single DB instance

def itemadd():
    """Page for adding new items to the inventory."""
    st.title("➕ Add New Item")

    # Define item fields dynamically
    item_fields = {
        "ItemNameEnglish": "Item Name (English)",
        "ItemNameKurdish": "Item Name (Kurdish)",
        "ClassCat": "Class Category",
        "DepartmentCat": "Department Category",
        "SectionCat": "Section Category",
        "FamilyCat": "Family Category",
        "SubFamilyCat": "Sub-Family Category",
        "ShelfLife": "Shelf Life (days)",
        "OriginCountry": "Origin Country",
        "Manufacturer": "Manufacturer",
        "Brand": "Brand",
        "Barcode": "Barcode",
        "UnitType": "Unit Type",
        "Packaging": "Packaging",
        "ItemPicture": "Item Picture URL"
    }

    # Generate input fields dynamically
    item_data = {}
    for key, label in item_fields.items():
        if key == "ShelfLife":
            item_data[key] = st.number_input(label, min_value=0, step=1)
        else:
            item_data[key] = st.text_input(label)

    if st.button("Add Item"):
        db.add_item(item_data)  # ✅ Prevents duplicate items now
