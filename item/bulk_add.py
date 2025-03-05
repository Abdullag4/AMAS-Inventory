import streamlit as st
import pandas as pd
import io
from db_handler import DatabaseManager

db = DatabaseManager()  # ✅ Database instance

def generate_example_excel():
    """Generate an example Excel file for bulk item addition."""
    sample_data = {
        "ItemNameEnglish": ["Item 1", "Item 2"],
        "ClassCat": ["Category A", "Category B"],
        "DepartmentCat": ["Department X", "Department Y"],
        "ShelfLife": [365, 180],
        "Threshold": [50, 30],
        "AverageRequired": [200, 150],
        "Manufacturer": ["Brand A", "Brand B"],
        "Barcode": ["123456789", "987654321"],
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

            # ✅ Ensure required columns exist
            required_columns = ["ItemNameEnglish", "ClassCat", "DepartmentCat", "ShelfLife", "Threshold", "AverageRequired"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                return

            # ✅ Convert shelf life & numeric columns to integers
            df["ShelfLife"] = df["ShelfLife"].astype(int)
            df["Threshold"] = df["Threshold"].astype(int)
            df["AverageRequired"] = df["AverageRequired"].astype(int)

            # ✅ Insert items one by one
            for _, row in df.iterrows():
                item_data = row.to_dict()
                db.add_item(item_data, [])  # No supplier linking in bulk upload

            st.success("✅ Items added successfully!")

        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
