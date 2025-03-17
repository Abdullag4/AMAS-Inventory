import streamlit as st
import pandas as pd
from receive_items.receive_handler import ReceiveHandler

receive_handler = ReceiveHandler()

def item_location_tab():
    """Tab for managing item store locations."""
    st.header("📍 Item Store Locations")

    # ✅ Fetch all items and their locations
    items_df = receive_handler.get_items_with_locations_and_expirations()

    if items_df.empty:
        st.success("✅ All items have assigned store locations!")
        return

    # ✅ Section 1: Items without a location
    st.subheader("⚠️ Items Without Store Location")
    missing_location_df = items_df[items_df["storelocation"].isna() | (items_df["storelocation"] == '')]

    if not missing_location_df.empty:
        st.write("These items have no assigned store location:")
        st.dataframe(
            missing_location_df[["itemnameenglish", "expirationdate", "barcode", "currentquantity"]],
            use_container_width=True
        )

        # ✅ Assign location
        st.write("### 📍 Assign Store Locations")
        selected_items = st.multiselect(
            "Select items to assign location",
            missing_location_df["itemnameenglish"].tolist()
        )

        if selected_items:
            location_input = st.text_input("Enter new location:")
            if st.button("Assign Location"):
                if location_input:
                    for item_name in selected_items:
                        item_row = missing_location_df.loc[missing_location_df["itemnameenglish"] == item_name]

                        # ✅ Convert item_id to standard int
                        item_id = int(item_row["itemid"].values[0])  
                        expiration_date = item_row["expirationdate"].values[0]  

                        receive_handler.update_item_location_specific(item_id, expiration_date, location_input)
                    
                    st.success(f"✅ Location '{location_input}' assigned to selected items!")
                    st.rerun()
                else:
                    st.error("❌ Please enter a location before assigning.")

    else:
        st.success("✅ No items without store location.")

    # ✅ Section 2: Edit Existing Locations
    st.subheader("📝 Update Store Locations")
    assigned_location_df = items_df[~items_df["storelocation"].isna() & (items_df["storelocation"] != '')]

    if not assigned_location_df.empty:
        st.write("Modify existing store locations:")
        
        # ✅ Select Item
        item_options = dict(zip(assigned_location_df["itemnameenglish"], assigned_location_df["itemid"]))
        selected_item_name = st.selectbox("Select item to edit location", list(item_options.keys()))
        selected_item_id = int(item_options[selected_item_name])  # ✅ Convert to standard int

        # ✅ Filter expiration dates
        item_expirations_df = assigned_location_df[assigned_location_df["itemid"] == selected_item_id]
        st.write("### 🏷️ Current Locations")
        st.dataframe(
            item_expirations_df[["expirationdate", "storelocation", "currentquantity"]],
            use_container_width=True
        )

        expiration_dates = item_expirations_df["expirationdate"].dt.strftime("%Y-%m-%d").tolist()
        selected_expirations = st.multiselect("Select expiration dates to update:", expiration_dates)

        new_location = st.text_input("Enter new store location:")

        if st.button("Update Location"):
            if new_location and selected_expirations:
                for exp_date in selected_expirations:
                    receive_handler.update_item_location_specific(selected_item_id, exp_date, new_location)
                
                st.success(f"✅ Store location updated for '{selected_item_name}'!")
                st.rerun()
            else:
                st.error("❌ Please enter a valid location and select expiration dates.")
    else:
        st.info("ℹ️ No items currently have store locations.")
