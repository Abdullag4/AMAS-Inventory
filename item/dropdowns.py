import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def manage_dropdowns_tab():
    st.header("🔽 Manage Dropdowns")

    existing_sections = db.get_all_sections()
    selected_section = st.selectbox("Select a Section", [""] + existing_sections)

    new_section = st.text_input("Or Add New Section (if not in list)").strip()
    final_section = new_section if new_section else selected_section

    if not final_section:
        st.warning("⚠️ Please select or enter a section name.")
        return

    dropdown_values = db.get_dropdown_values(final_section)
    st.subheader(f"📋 Values in {final_section}")
    if dropdown_values:
        st.write(dropdown_values)
    else:
        st.info("No values available for this section.")

    # Add a new value
    new_value = st.text_input(f"Add new value to {final_section}").strip()
    if st.button("➕ Add Value"):
        if new_value:
            db.add_dropdown_value(final_section, new_value)
            st.success(f"✅ '{new_value}' added to '{final_section}'")
            # ❌ Removed st.experimental_rerun()
            st.info("Please refresh or switch tabs to see updated values.")
        else:
            st.error("❌ Value cannot be empty!")

    # Delete an existing value
    if dropdown_values:
        value_to_delete = st.selectbox("Select a value to delete", [""] + dropdown_values)
        if st.button("🗑️ Delete Selected Value"):
            if value_to_delete:
                db.delete_dropdown_value(final_section, value_to_delete)
                st.success(f"✅ '{value_to_delete}' deleted from '{final_section}'")
                st.info("Please refresh or switch tabs to see updated values.")
            else:
                st.error("❌ Please select a value to delete!")
