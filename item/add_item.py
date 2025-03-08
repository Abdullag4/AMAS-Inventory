import streamlit as st
from item.item_handler import ItemHandler

item_handler = ItemHandler()

def add_item_tab():
    st.header("➕ Add New Item")

    # Define dropdown fields exactly matching database values
    dropdown_fields = [
        "ClassCat", "DepartmentCat", "SectionCat",
        "FamilyCat", "SubFamilyCat", "UnitType",
        "Packaging", "OriginCountry", "Manufacturer", "Brand"
    ]

    # Fetch dropdown values
    dropdown_values = {
        field: item_handler.get_dropdown_values(field)
        for field in dropdown_fields
    }

    # Debugging line (remove after confirming working state)
    st.write("Dropdown Values Debug:", dropdown_values)

    # Input fields
    item_name_en = st.text_input("Item Name (English) *")
    item_name_ku = st.text_input("Item Name (Kurdish)")
    
    # Dropdown inputs
    class_cat = st.selectbox("Class Category", dropdown_values.get("ClassCat", []))
    department_cat = st.selectbox("Department Category", dropdown_values.get("DepartmentCat", []))
    section_cat = st.selectbox("Section Category", dropdown_values.get("SectionCat", []))
    family_cat = st.selectbox("Family Category", dropdown_values.get("FamilyCat", []))
    subfamily_cat = st.selectbox("Sub-Family Category", dropdown_values.get("SubFamilyCat", []))
    unit_type = st.selectbox("Unit Type", dropdown_values.get("UnitType", []))
    packaging = st.selectbox("Packaging", dropdown_values.get("Packaging", []))
    origin_country = st.selectbox("Origin Country", dropdown_values.get("OriginCountry", []))
    manufacturer = st.selectbox("Manufacturer", dropdown_values.get("Manufacturer", []))
    brand = st.selectbox("Brand", dropdown_values.get("Brand", []))

    shelf_life = st.number_input("Shelf Life (days)", min_value=1, step=1)
    threshold = st.number_input("Threshold", min_value=0, step=1)
    avg_required = st.number_input("Average Required", min_value=0, step=1)
    barcode = st.text_input("Barcode")

    # Suppliers selection
    suppliers_df = item_handler.get_suppliers()
    if not suppliers_df.empty:
        supplier_names = suppliers_df["suppliername"].tolist()
        selected_sup_names = st.multiselect("Select Supplier(s)", supplier_names)
        selected_sup_ids = [
            suppliers_df[suppliers_df["suppliername"] == name]["supplierid"].iloc[0]
            for name in selected_sup_names
        ]
    else:
        selected_sup_ids = []
        st.warning("⚠️ No suppliers available in database.")

    if st.button("Add Item"):
        if not item_name_en or not class_cat or not department_cat or not shelf_life or not selected_sup_ids:
            st.error("❌ Please fill in all required fields.")
            return

        item_data = {
            "itemnameenglish": item_name_en,
            "itemnamekurdish": item_name_ku,
            "classcat": class_cat,
            "departmentcat": department_cat,
            "sectioncat": section_cat,
            "familycat": family_cat,
            "subfamilycat": subfamily_cat,
            "shelflife": shelf_life,
            "threshold": threshold,
            "averagerequired": avg_required,
            "origincountry": origin_country,
            "manufacturer": manufacturer,
            "brand": brand,
            "barcode": barcode,
            "unittype": unit_type,
            "packaging": packaging,
        }

        item_id = item_handler.add_item(item_data, selected_sup_ids)
        if item_id:
            st.success("✅ Item added successfully!")
        else:
            st.error("❌ Failed to add item.")
