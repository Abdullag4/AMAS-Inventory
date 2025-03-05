import streamlit as st
import pandas as pd
import io
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Database instance

def generate_example_excel():
    """Generate an example Excel file with all required columns for bulk item addition."""
    sample_data = {
        "ItemNameEnglish": ["Paracetamol 500mg", "Ibuprofen 200mg"],
        "ItemNameKurdish": ["پاراستامۆل ٥٠٠مگ", "ئەيبۆپڕۆفێن ٢٠٠مگ"],  # ✅ Kurdish name added
        "ClassCat": ["Pain Reliever", "Anti-Inflammatory"],
        "DepartmentCat": ["Pharmacy", "Pharmacy"],
        "SectionCat": ["OTC", "OTC"],
        "FamilyCat": ["Analgesics", "Analgesics"],
        "SubFamilyCat": ["Tablets", "Tablets"],
        "ShelfLife": [730, 365],  # Days
        "Threshold": [100, 50],  # Minimum stock before reorder
        "AverageRequired": [500, 300],  # Expected stock level
        "OriginCountry": ["USA", "Germany"],
        "Manufacturer": ["Company A", "Company B"],
        "Brand": ["Brand X", "Brand Y"],
        "Barcode": ["1234567890123", "9876543210987"],
        "UnitType": ["Box", "Pack"],
        "Packaging": ["Blister", "Bottle"],
        "SupplierName": ["Supplier A", "Supplier B"]  # ✅ Supplier Name for mapping
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

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)

            # ✅ Ensure all required columns exist
            required_columns = [
                "ItemNameEnglish", "ItemNameKurdish", "ClassCat", "DepartmentCat", "ShelfLife", 
                "Threshold", "AverageRequired", "SupplierName"
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                return

            # ✅ Convert numeric fields to integers
            df["ShelfLife"] = df["ShelfLife"].astype(int)
            df["Threshold"] = df["Threshold"].astype(int)
            df["AverageRequired"] = df["AverageRequired"].astype(int)

            # ✅ Fetch supplier data & debug
            supplier_df = db.get_suppliers()
            st.write("🔍 Supplier Table Data:", supplier_df)

            if supplier_df.empty or "SupplierName" not in supplier_df.columns:
                st.error("❌ 'SupplierName' column not found in database. Please check table structure.")
                return

            # ✅ Insert items into the database
            for _, row in df.iterrows():
                item_data = row.drop("SupplierName").to_dict()  # ✅ Exclude supplier temporarily
                supplier_name = row["SupplierName"]

                # ✅ Get Supplier ID from name
                supplier_id = supplier_df.loc[supplier_df["SupplierName"] == supplier_name, "SupplierID"]
                
                if not supplier_id.empty:
                    supplier_id = supplier_id.iloc[0]
                    db.add_item(item_data, [supplier_id])  # ✅ Link item to supplier
                else:
                    st.warning(f"⚠️ Supplier '{supplier_name}' not found. Item '{row['ItemNameEnglish']}' was not added.")

            st.success("✅ Items added successfully!")

        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
