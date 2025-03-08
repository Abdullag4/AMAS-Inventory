import streamlit as st
from item.item_handler import ItemHandler

item_handler = ItemHandler()


def add_item_tab():
    st.header("➕ Add New Item")

    # Dropdown fields to populate from the database
    dropdown_fields = [
        "ClassCat", "DepartmentCat", "SectionCat", "FamilyCat", "SubFamilyCat",
        "UnitType", "Packaging", "OriginCountry", "Manufacturer", "Brand"
    ]

    # Fetch dropdown values
    dropdown_values = {
        field: item_handler.get_dropdown_values(field) for field in dropdown_fields
    }

    # Fetch suppliers
    suppliers_df = item_handler.get_suppliers()
    if not suppliers_df.empty:
        supplier_names = suppliers_df["suppliername"].tolist()
        selected_sup_names = st.multiselect("Select Supplier(s) *", supplier_names)
        selected_sup_ids = [
            int(suppliers_df[suppliers_df["suppliername"] == name]["supplierid"].iloc[0])
            for name in selected_sup_names
        ]
    else:
        selected_sup_ids = []
        st.warning("⚠️ No suppliers available in database.")

    # Input fields
    item_name_en = st.text_input("Item Name (English) *")
    item_name_ku = st.text_input("Item Name (Kurdish)")
    class_cat = st.selectbox("Class Category", dropdown_values["ClassCat"])
    department_cat = st.selectbox("Department Category", dropdown_values["DepartmentCat"])
    section_cat = st.selectbox("Section Category", dropdown_values["SectionCat"])
    family_cat = st.selectbox("Family Category", dropdown_values["FamilyCat"])
    subfamily_cat = st.selectbox("Sub-Family Category", dropdown_values["SubFamilyCat"])
    shelf_life = st.number_input("Shelf Life (days) *", min_value=0, step=1)
    threshold = st.number_input("Threshold *", min_value=0, step=1)
    avg_required = st.number_input("Average Required *", min_value=0, step=1)
    origin_country = st.selectbox("Origin Country", dropdown_values["OriginCountry"])
    manufacturer = st.selectbox("Manufacturer", dropdown_values["Manufacturer"])
    brand = st.selectbox("Brand", dropdown_values["Brand"])
    barcode = st.text_input("Barcode")
    unit_type = st.selectbox("Unit Type", dropdown_values["UnitType"])
    packaging = st.selectbox("Packaging", dropdown_values["Packaging"])

    # Add item button
    if st.button("Add Item"):
        if not item_name_en or not shelf_life or not threshold or not avg_required or not selected_sup_ids:
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
            "shelflife": int(shelf_life),
            "threshold": int(threshold),
            "averagerequired": int(avg_required),
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
            st.error("❌ Failed to add item. Please check the details and try again.")
