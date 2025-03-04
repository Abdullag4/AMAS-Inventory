import streamlit as st
import pandas as pd
from db_handler import DatabaseManager

db = DatabaseManager()

def bulk_add_tab():
    """Tab for adding multiple items via Excel upload."""
    st.subheader("📂 Bulk Upload Items")

    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith("xlsx") else pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:", df.head())

            if st.button("Add Items"):
                for _, row in df.iterrows():
                    item_data = row.to_dict()
                    db.add_item(item_data)
                st.success("✅ Bulk items added successfully!")

        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
