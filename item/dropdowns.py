import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

# Fixed sections to manage
SECTIONS = [
    "ClassCat",
    "DepartmentCat",
    "SectionCat",
    "FamilyCat",
    "SubFamilyCat",
    "UnitType",
    "Packaging",
    "OriginCountry",
    "Manufacturer",
    "Brand"
]

def manage_dropdowns_tab():
    """Tab to manage dropdown values for specific, fixed sections."""
    st.header("🔽 Manage Dropdowns")

    selected_section = st.selectbox("Select a Section to manage", [""] + SECTIONS)

    if not selected_section:
        st.warning("⚠️ Please choose a section from the list.")
        return

    # Fetch existing values from the Dropdowns table
    dropdown_values = db.get_dropdown_values(selected_section)
    st.subheader(f"📋 Values in '{selected_section}'")

    if dropdown_values:
        st.write(dropdown_values)
    else:
        st.info("No values available for this section.")

    # Add a new value
    new_value = st.text_input(f"Add new value to '{selected_section}'").strip()
    if st.button("➕ Add Value"):
        if new_value:
            db.add_dropdown_value(selected_section, new_value)
            st.success(f"✅ '{new_value}' added to '{selected_section}'")
            st.info("Refresh or switch tabs to see the updated values.")
        else:
            st.error("❌ Value cannot be empty!")

    # Delete an existing value
    if dropdown_values:
        value_to_delete = st.selectbox("Select a value to delete", [""] + dropdown_values)
        if st.button("🗑️ Delete Selected Value"):
            if value_to_delete:
                db.delete_dropdown_value(selected_section, value_to_delete)
                st.success(f"✅ '{value_to_delete}' deleted from '{selected_section}'")
                st.info("Refresh or switch tabs to see the updated values.")
            else:
                st.error("❌ Please select a value to delete!")
