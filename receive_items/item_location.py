import streamlit as st
import pandas as pd
from receive_items.receive_handler import ReceiveHandler

receive_handler = ReceiveHandler()

def item_location_tab():
    """Tab for managing item store locations with expiration-date specificity."""
    st.header("📍 Item Store Locations")

    items_df = receive_handler.get_items_with_locations_and_expirations()

    if items_df.empty:
        st.success("✅ All items have assigned store locations!")
        return

    # ✅ **Fix: Identify missing store locations properly (Empty OR Null)**
    items_df["storelocation"] = items_df["storelocation"].replace("", pd.NA)  # Convert empty strings to NaN
    missing_location_df = items_df[items_df["storelocation"].isna()]  # Detect missing locations

    # ✅ Section 1: Items Without Store Location
    st.subheader("⚠️ Items Without Store Location")

    if not missing_location_df.empty:
        st.write("These items have no assigned store location:")
        st.dataframe(
            missing_location_df[["itemnameenglish", "barcode", "expirationdate", "currentquantity"]],
            use_container_width=True
        )

        selected_items = st.multiselect(
            "Select items to assign location", 
            missing_location_df["itemnameenglish"].tolist()
        )

        if selected_items:
            location_input = st.text_input("Enter new location:")
            if st.button("Assign Location"):
                if location_input:
                    for item_name in selected_items:
                        item_id = missing_location_df.loc[
                            missing_location_df["itemnameenglish"] == item_name, "itemid"
                        ].values[0]
                        receive_handler.update_item_location(item_id, location_input)
                    st.success(f"✅ Location '{location_input}' assigned successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please enter a location before assigning.")
    else:
        st.success("✅ No items without store location.")

    # ✅ Section 2: Update Store Locations by Expiration Date
    st.subheader("📝 Update Store Locations")
    existing_location_df = items_df.dropna(subset=["storelocation"])

    if existing_location_df.empty:
        st.info("ℹ️ No items currently have store locations.")
        return

    item_options = existing_location_df.set_index("itemnameenglish")["itemid"].to_dict()
    selected_item_name = st.selectbox("Select item to edit location", list(item_options.keys()))
    selected_item_id = item_options[selected_item_name]

    item_expirations_df = existing_location_df[existing_location_df["itemid"] == selected_item_id].copy()

    # ✅ Ensure ExpirationDate is formatted as YYYY-MM-DD
    item_expirations_df["expirationdate"] = pd.to_datetime(
        item_expirations_df["expirationdate"], errors='coerce'
    ).dt.strftime('%Y-%m-%d')

    # ✅ Display current locations and expiration dates clearly
    st.write(f"**Current locations for '{selected_item_name}':**")
    st.dataframe(
        item_expirations_df[["expirationdate", "storelocation", "currentquantity"]]
        .rename(columns={
            "expirationdate": "Expiration Date",
            "storelocation": "Store Location",
            "currentquantity": "Quantity"
        }),
        use_container_width=True
    )

    expiration_dates = item_expirations_df["expirationdate"].unique().tolist()
    selected_expirations = st.multiselect("Select expiration dates to update", expiration_dates)

    new_location = st.text_input("Enter new store location:", value="")

    if st.button("Update Location"):
        if new_location and selected_expirations:
            for exp_date in selected_expirations:
                receive_handler.update_item_location_specific(
                    selected_item_id, exp_date, new_location
                )
            st.success(f"✅ Location updated for '{selected_item_name}'!")
            st.rerun()
        else:
            st.error("❌ Please enter a valid location and select at least one expiration date.")
