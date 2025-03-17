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
    missing_location_df = items_df[items_df["storelocation"].isna()]

    if not missing_location_df.empty:
        st.write("These items have no assigned store location:")
        st.dataframe(missing_location_df[["itemnameenglish", "barcode", "currentquantity", "expirationdate"]], use_container_width=True)

        # ✅ Assign location
        st.write("### 📍 Assign Store Locations")
        selected_items = st.multiselect("Select items to assign location", missing_location_df["itemnameenglish"].tolist())

        if selected_items:
            location_input = st.text_input("Enter new location:")
            if st.button("Assign Location"):
                if location_input:
                    for item_name in selected_items:
                        item_rows = missing_location_df[missing_location_df["itemnameenglish"] == item_name]
                        for _, item_row in item_rows.iterrows():
                            receive_handler.update_item_location_specific(
                                item_row["itemid"],
                                item_row["expirationdate"],
                                location_input
                            )
                    st.success(f"✅ Location '{location_input}' assigned to selected items!")
                    st.rerun()
                else:
                    st.error("❌ Please enter a location before assigning.")

    else:
        st.success("✅ No items without store location.")

    # ✅ Section 2: Edit Existing Locations
    st.subheader("📝 Update Store Locations")
    assigned_location_df = items_df[~items_df["storelocation"].isna()]

    if not assigned_location_df.empty:
        st.write("Modify existing store locations:")
        item_options = dict(zip(assigned_location_df["itemnameenglish"], assigned_location_df["itemid"]))
        selected_item_name = st.selectbox("Select item to edit location", list(item_options.keys()))
        selected_item_id = item_options[selected_item_name]

        item_expirations_df = assigned_location_df[assigned_location_df["itemid"] == selected_item_id].copy()
        item_expirations_df["expirationdate"] = pd.to_datetime(item_expirations_df["expirationdate"]).dt.strftime('%Y-%m-%d')

        st.write("**Available quantities and expiration dates:**")
        st.dataframe(item_expirations_df, use_container_width=True)

        # Select specific expiration dates to update
        expiration_dates = item_expirations_df["expirationdate"].tolist()
        selected_expirations = st.multiselect("Select expiration dates to update", expiration_dates)

        new_location = st.text_input("Enter new store location:")

        if st.button("Update Location"):
            if new_location and selected_expirations:
                for exp_date in selected_expirations:
                    receive_handler.update_item_location_specific(selected_item_id, exp_date, new_location)
                st.success(f"✅ Store location updated for '{selected_item_name}'!")
                st.rerun()
            else:
                st.error("❌ Please select expiration dates and enter a valid location.")
    else:
        st.info("ℹ️ No items currently have store locations.")
