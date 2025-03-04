import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def manage_dropdowns_tab():
    """Tab for managing dropdown values for item fields."""
    st.subheader("⚙️ Manage Dropdowns")

    dropdown_fields = ["ClassCat", "DepartmentCat", "SectionCat", "FamilyCat", "SubFamilyCat", "UnitType", "Packaging"]
    selected_field = st.selectbox("Select a field to manage", dropdown_fields)

    existing_values = db.fetch_data(f"SELECT DISTINCT {selected_field} FROM Item")

    st.write("Current values:", existing_values)

    new_value = st.text_input(f"Add new value to {selected_field}")
    if st.button("Add Value"):
        db.execute_command(f"INSERT INTO Item ({selected_field}) VALUES (%s)", (new_value,))
        st.success(f"✅ Value '{new_value}' added to {selected_field}!")
