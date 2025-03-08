import streamlit as st
from item.item_handler import ItemHandler

item_handler = ItemHandler()

def add_item_tab():
    st.header("➕ Add New Item")

    dropdown_fields = [
        "Class Category", "Department Category", "Section Category", 
        "Family Category", "Sub-Family Category", 
        "Unit Type", "Packaging", "Origin Country", "Manufacturer", "Brand"
    ]

    dropdown_values = {
        field: item_handler.db.get_dropdown_values(field) for field in dropdown_fields
    }

    # Input fields
    item_name_en = st.text_input("Item Name (English) *")
    item_name_ku = st.text_input("Item Name (Kurdish)")
    class_cat = st.selectbox("Class Category *", dropdown_values["Class Category"])
    department_cat = st.selectbox("Department Category *", dropdown_values["Department Category"])
    section_cat = st.selectbox("Section Category", dropdown_values["Section Category"])
    family_cat = st.selectbox("Family Category", dropdown_values["Family Category"])
    subfamily_cat = st.selectbox("Sub-Family Category", dropdown_values["Sub-Family Category"])
    shelf_life = st.number_input("Shelf Life (days) *", min_value=0, step=1)
    threshold = st.number_input("Threshold *", min_value=0, step=1)
    avg_required = st.number_input("Average Required *", min_value=0, step=1)
    unit_type = st.selectbox("Unit Type", dropdown_values["Unit Type"])
    packaging = st.selectbox("Packaging", dropdown_values["Packaging"])
    origin_country = st.selectbox("Origin Country", dropdown_values["Origin Country"])
    manufacturer = st.selectbox("Manufacturer", dropdown_values["Manufacturer"])
    brand = st.selectbox("Brand", dropdown_values["Brand"])
    barcode = st.text_input("Barcode")
    item_picture = st.text_input("Item Picture URL")

    # Supplier selection
    suppliers_df = item_handler.get_suppliers()
    if not suppliers_df.empty:
        supplier_names = suppliers_df["suppliername"].tolist()
        selected_sup_names = st.multiselect("Select Supplier(s)", supplier_names)
        selected_sup_ids = suppliers_df[suppliers_df["suppliername"].isin(selected_sup_names)]["supplierid"].tolist()
    else:
        st.warning("⚠️ No suppliers available.")
        selected_sup_ids = []

    if st.button("Add Item"):
        required_fields = [
            item_name_en, class_cat, department_cat, shelf_life, threshold, avg_required
        ]

        if not all(required_fields):
            st.error("❌ Please fill in all required fields before adding the item.")
            return

        if item_handler.item_exists(item_name_en):
            st.error(f"❌ Item '{item_name_en}' already exists!")
            return

        item_data = {
            "ItemNameEnglish": item_name_en,
            "ItemNameKurdish": item_name_ku,
            "ClassCat": class_cat,
            "DepartmentCat": department_cat,
            "SectionCat": section_cat,
            "FamilyCat": family_cat,
            "SubFamilyCat": subfamily_cat,
            "ShelfLife": shelf_life,
            "Threshold": threshold,
            "AverageRequired": avg_required,
            "UnitType": unit_type,
            "Packaging": packaging,
            "OriginCountry": origin_country,
            "Manufacturer": manufacturer,
            "Brand": brand,
            "Barcode": barcode,
            "ItemPicture": item_picture
        }

        item_id = item_handler.add_item(item_data, selected_sup_ids)
        if item_id:
            st.success(f"✅ Item '{item_name_en}' added successfully!")
        else:
            st.error("❌ Failed to add item. Check logs.")
