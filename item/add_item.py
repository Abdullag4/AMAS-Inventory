import streamlit as st
from item.item_handler import ItemHandler

item_handler = ItemHandler()

def add_item_tab():
    st.header("➕ Add New Item")

    required_fields = ["Item Name (English)", "Class Category", "Shelf Life", "Threshold", "Average Required"]

    dropdown_fields = [
        "Class Category", "Department Category", "Section Category", "Family Category", 
        "Sub-Family Category", "Unit Type", "Packaging", "Origin Country", 
        "Manufacturer", "Brand"
    ]

    dropdown_values = {
        field: item_handler.get_dropdown_values(field) for field in dropdown_fields
    }

    # Input fields
    item_name_en = st.text_input("Item Name (English) *")
    item_name_ku = st.text_input("Item Name (Kurdish)")
    
    class_cat = st.selectbox("Class Category *", dropdown_values["Class Category"])
    department_cat = st.selectbox("Department Category", [""] + dropdown_values["Department Category"])
    section_cat = st.selectbox("Section Category", [""] + dropdown_values["Section Category"])
    family_cat = st.selectbox("Family Category", [""] + dropdown_values["Family Category"])
    subfamily_cat = st.selectbox("Sub-Family Category", [""] + dropdown_values["Sub-Family Category"])

    shelf_life = st.number_input("Shelf Life (days) *", min_value=0)
    threshold = st.number_input("Threshold *", min_value=0)
    average_required = st.number_input("Average Required *", min_value=0)

    origin_country = st.selectbox("Origin Country", [""] + dropdown_values["Origin Country"])
    manufacturer = st.selectbox("Manufacturer", [""] + dropdown_values["Manufacturer"])
    brand = st.selectbox("Brand", [""] + dropdown_values["Brand"])

    barcode = st.text_input("Barcode")
    unit_type = st.selectbox("Unit Type", [""] + dropdown_values["Unit Type"])
    packaging = st.selectbox("Packaging", [""] + dropdown_values["Packaging"])

    item_picture = st.file_uploader("Item Picture", type=["jpg", "jpeg", "png"])

    # Supplier selection
    suppliers_df = item_handler.get_suppliers()
    supplier_names = suppliers_df["suppliername"].tolist()
    selected_sup_names = st.multiselect("Select Supplier(s)", supplier_names)
    selected_sup_ids = suppliers_df[suppliers_df["suppliername"].isin(selected_sup_names)]["supplierid"].tolist()

    if st.button("Add Item"):
        # Validate required fields
        if not all([item_name_en, class_cat, shelf_life, threshold, average_required]):
            st.error("❌ Please fill in all required fields.")
            return

        # Check for duplicate item name (English)
        existing_items = item_handler.get_items()
        if item_name_en.strip().lower() in existing_items["itemnameenglish"].str.strip().str.lower().values:
            st.error("❌ An item with this English name already exists!")
            return

        # Process uploaded image
        item_picture_data = item_picture.getvalue() if item_picture else None

        # Construct item data
        item_data = {
            "itemnameenglish": item_name_en.strip(),
            "itemnamekurdish": item_name_ku.strip(),
            "classcat": class_cat,
            "departmentcat": department_cat or None,
            "sectioncat": section_cat or None,
            "familycat": family_cat or None,
            "subfamilycat": subfamily_cat or None,
            "shelflife": int(shelf_life),
            "threshold": int(threshold),
            "averagerequired": int(average_required),
            "origincountry": origin_country or None,
            "manufacturer": manufacturer or None,
            "brand": brand or None,
            "barcode": barcode.strip() or None,
            "unittype": unit_type or None,
            "packaging": packaging or None,
            "itempicture": item_picture_data
        }

        # Add the item and link to suppliers
        item_id = item_handler.add_item(item_data, selected_sup_ids)
        if item_id:
            st.success("✅ Item added successfully!")
        else:
            st.error("❌ Error adding item. Please try again.")
