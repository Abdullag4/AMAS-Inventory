import streamlit as st
from item.item_handler import ItemHandler

item_handler = ItemHandler()

def add_item_tab():
    st.header("➕ Add New Item")

    dropdown_fields = [
        "ClassCat", "DepartmentCat", "SectionCat", "FamilyCat", "SubFamilyCat",
        "UnitType", "Packaging", "OriginCountry", "Manufacturer", "Brand"
    ]

    dropdown_values = {
        field: item_handler.get_dropdown_values(field) for field in dropdown_fields
    }

    suppliers_df = item_handler.get_suppliers()
    supplier_names = suppliers_df["suppliername"].tolist() if not suppliers_df.empty else []

    item_name_en = st.text_input("Item Name (English) *")
    item_name_ku = st.text_input("Item Name (Kurdish)")

    class_cat = st.selectbox("Class Category *", dropdown_values["ClassCat"], index=None)
    department_cat = st.selectbox("Department Category", dropdown_values["DepartmentCat"], index=None)
    section_cat = st.selectbox("Section Category", dropdown_values["SectionCat"], index=None)
    family_cat = st.selectbox("Family Category", dropdown_values["FamilyCat"], index=None)
    subfamily_cat = st.selectbox("Sub-Family Category", dropdown_values["SubFamilyCat"], index=None)

    shelf_life = st.number_input("Shelf Life (days) *", min_value=0, value=0)
    threshold = st.number_input("Threshold *", min_value=0, value=0)
    average_required = st.number_input("Average Required *", min_value=0, value=0)

    origin_country = st.selectbox("Origin Country", dropdown_values["OriginCountry"], index=None)
    manufacturer = st.selectbox("Manufacturer", dropdown_values["Manufacturer"], index=None)
    brand = st.selectbox("Brand", dropdown_values["Brand"], index=None)

    barcode = st.text_input("Barcode")
    unit_type = st.selectbox("Unit Type", dropdown_values["UnitType"], index=None)
    packaging = st.selectbox("Packaging", dropdown_values["Packaging"], index=None)

    item_picture = st.file_uploader("Upload Item Picture", type=["jpg", "jpeg", "png"])

    selected_sup_names = st.multiselect("Select Supplier(s) *", supplier_names)
    selected_sup_ids = []
    if selected_sup_names:
        selected_sup_ids = [
            int(suppliers_df[suppliers_df["suppliername"] == name]["supplierid"].iloc[0])
            for name in selected_sup_names
        ]

    if st.button("➕ Add Item"):
        required_fields = [item_name_en, class_cat, shelf_life, threshold, average_required, selected_sup_ids]

        if not all(required_fields):
            st.error("❌ Please fill in all required fields, including 'Class Category', before adding the item.")
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
            "averagerequired": int(average_required),
            "origincountry": origin_country,
            "manufacturer": manufacturer,
            "brand": brand,
            "barcode": barcode,
            "unittype": unit_type,
            "packaging": packaging,
            "itempicture": item_picture.getvalue() if item_picture else None,
        }

        item_id = item_handler.add_item(item_data, selected_sup_ids)
        if item_id:
            st.success("✅ Item added successfully!")
        else:
            st.error("❌ Failed to add item.")
