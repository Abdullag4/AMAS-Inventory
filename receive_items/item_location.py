import streamlit as st
import pandas as pd
from receive_items.receive_handler import ReceiveHandler

receive_handler = ReceiveHandler()

def item_location_tab():
    """Tab for managing item store locations."""
    st.header("📍 Item Store Locations")

    # Fetch items currently in inventory with locations
    items_df = receive_handler.get_items_with_locations()

    if items_df.empty:
        st.success("✅ All items have assigned store locations!")
        return

    # ✅ Section 1: Items without a location
    st.subheader("⚠️ Items Without Store Location")
    missing_location_df = items_df[items_df["storelocation"].isna()]

    if not missing_location_df.empty:
        st.write("These items have no assigned store location:")
        st.dataframe(missing_location_df[["itemnameenglish", "barcode", "currentquantity"]], use_container_width=True)

        selected_items = st.multiselect("Select items to assign location", missing_location_df["itemnameenglish"].tolist())
        new_location = st.text_input("Enter store location:", key="new_loc")

        if st.button("Assign Location"):
            if new_location:
                for item_name in selected_items:
                    item_id = missing_location_df.loc[missing_location_df["itemnameenglish"] == item_name, "itemid"].values[0]
                    receive_handler.update_item_location(item_id, new_location)
                st.success("✅ Locations assigned successfully!")
                st.experimental_rerun()
            else:
                st.warning("❌ Please enter a location.")

    else:
        st.success("✅ All items currently have store locations!")

    # Section for editing locations
    st.subheader("📝 Update Store Locations")

    inventory_items_df = items_df[~items_df["storelocation"].isna()]

    if not inventory_items_df.empty:
        item_to_edit = st.selectbox("Select item to edit location", inventory_items_df["itemnameenglish"].unique())

        # Show current locations clearly before editing
        current_locations_df = inventory_items_df[inventory_items_df["itemnameenglish"] == item_to_edit]

        st.write("**Current store locations:**")
        st.dataframe(current_locations_df[["expirationdate", "storelocation", "currentquantity"]], use_container_width=True)

        selected_expiration = st.multiselect("Select expiration dates to update", current_locations_df["expirationdate"].astype(str).tolist())

        new_location = st.text_input("Enter new location")

        if st.button("Update Location"):
            if new_location and selected_expirations:
                for exp_date in selected_expirations:
                    exp_date = pd.to_datetime(exp_date)
                    receive_handler.update_item_location_by_expiration(item_to_edit, exp_date, new_location)
                st.success("✅ Store locations updated successfully!")
                st.experimental_rerun()
            else:
                st.warning("❌ Please select expiration dates and enter a new location.")
    else:
        st.info("ℹ️ No items available in inventory for editing locations.")
