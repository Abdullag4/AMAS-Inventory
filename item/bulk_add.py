import streamlit as st
import pandas as pd
import numpy as np
import io
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Database instance

def generate_example_excel():
    """Generate an example Excel file with all required columns for bulk item addition."""
    sample_data = {
        "ItemNameEnglish": ["Paracetamol 500mg", "Ibuprofen 200mg"],
        "ItemNameKurdish": ["پاراستامۆل ٥٠٠مگ", "ئەيبۆپڕۆفێن ٢٠٠مگ"],
        "ClassCat": ["Pain Reliever", "Anti-Inflammatory"],
        "DepartmentCat": ["Pharmacy", "Pharmacy"],
        "SectionCat": ["OTC", "OTC"],
        "FamilyCat": ["Analgesics", "Analgesics"],
        "SubFamilyCat": ["Tablets", "Tablets"],
        "ShelfLife": [730, 365],  
        "Threshold": [100, 50],  
        "AverageRequired": [500, 300],  
        "OriginCountry": ["USA", "Germany"],
        "Manufacturer": ["Company A", "Company B"],
        "Brand": ["Brand X", "Brand Y"],
        "Barcode": ["1234567890123", "9876543210987"],
        "UnitType": ["Box", "Pack"],
        "Packaging": ["Blister", "Bottle"],
        "SupplierName": ["Supplier A", "Supplier B"]  
    }

    df = pd.DataFrame(sample_data)

    # Create an in-memory Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Items")
    processed_data = output.getvalue()
    
    return processed_data


def bulk_add_tab():
    """Handles bulk item addition via Excel file upload."""
    st.header("📂 Bulk Add Items")

    # ✅ Provide downloadable example file
    example_file = generate_example_excel()
    st.download_button(
        label="📥 Download Example Excel File",
        data=example_file,
        file_name="Bulk_Item_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ Upload section
    uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

    # ✅ Add "Upload File" button
    if uploaded_file and st.button("📤 Upload File"):
        try:
            df = pd.read_excel(uploaded_file)

            # ✅ Debug Step: Show uploaded file columns
            st.write("📂 Uploaded File Columns:", df.columns.tolist())

            # ✅ Normalize column names to lowercase
            df.columns = df.columns.str.lower()

            # ✅ Required columns
            required_columns = [
                "itemnameenglish", "itemnamekurdish", "classcat", "departmentcat", "shelflife", 
                "threshold", "averagerequired", "suppliername"
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                return

            # ✅ Convert numeric fields to Python integers
            for col in ["shelflife", "threshold", "averagerequired"]:
                df[col] = df[col].astype(int)

            # ✅ Fetch supplier data & debug
            supplier_df = db.get_suppliers()
            st.write("🔍 Supplier Table Data:", supplier_df)

            if supplier_df.empty or "suppliername" not in supplier_df.columns:
                st.error("❌ 'SupplierName' column not found in supplier table. Check database structure.")
                return

            # ✅ Create a set of available supplier names (for fast lookup)
            existing_suppliers = set(supplier_df["suppliername"].str.lower())

            # ✅ Insert items into the database
            items_added = 0
            missing_suppliers = set()  # ✅ Track missing suppliers

            for _, row in df.iterrows():
                supplier_name = row["suppliername"].strip().lower()  # ✅ Normalize case & spaces

                # ✅ Check if supplier exists
                if supplier_name not in existing_suppliers:
                    missing_suppliers.add(row["suppliername"])  # ✅ Track missing supplier
                    continue  # ✅ Skip this item (DO NOT ADD)

                # ✅ Convert item data (skip "suppliername" column)
                item_data = {
                    key: int(value) if isinstance(value, (np.int64, float)) else value
                    for key, value in row.items() if key != "suppliername"
                }

                # ✅ Get Supplier ID from name
                supplier_match = supplier_df[supplier_df["suppliername"].str.lower() == supplier_name]
                supplier_id = int(supplier_match.iloc[0]["supplierid"])  # ✅ Convert supplier_id to int

                # ✅ Add the item & link to supplier
                db.add_item(item_data, [supplier_id])
                items_added += 1

            # ✅ Success Message
            if items_added > 0:
                st.success(f"✅ {items_added} items added successfully!")

            # ✅ Warning for missing suppliers
            if missing_suppliers:
                st.warning(f"⚠️ The following suppliers were not found in the database, so their items were not added: {', '.join(missing_suppliers)}")

        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
