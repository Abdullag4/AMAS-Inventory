import streamlit as st
import pandas as pd
from receive_items.receive_handler import ReceiveHandler

receive_handler = ReceiveHandler()

def item_location_tab():
    """Tab for managing item store locations."""
    st.header("📍 Item Store Locations")

    # ✅ Fetch items with their locations and expiration dates
    items_df = receive_handler.get_items_with_locations_and_expirations()

    if items_df.empty:
        st.success("✅ All items have assigned store locations!")
        return

    # ✅ Section 1: Items without a location
    st.subheader("⚠️ Items Without Store Location")
    missing_location_df = items_df[
        items_df["storelocation"].isna() & (items_df["currentquantity"] > 0)
    ]

    if not missing_location_df.empty:
        st.write("These items have no assigned store location:")
        st.dataframe(missing_location_df[["itemnameenglish", "barcode", "expirationdate", "currentquantity"]], 
                     use_container_width=True)

        # ✅ Assign location
        st.write("### 📍 Assign Store Locations")
        selected_items = st.multiselect(
            "Select items to assign location",
            missing_location_df["itemnameenglish"].unique()
        )

        if selected_items:
            location_input = st.text_input("Enter new location:")
            if st.button("Assign Location"):
                if location_input:
                    for item_name in selected_items:
                        item_entries = missing_location_df[
                            missing_location_df["itemnameenglish"] == item_name
                        ]
                        for _, row in item_entries.iterrows():
                            receive_handler.update_item_location_specific(
                                item_id=row["itemid"],
                                expiration_date=row["expirationdate"],
                                new_location=location_input
                            )
                    st.success(f"✅ Location '{location_input}' assigned to selected items!")
                    st.rerun()
                else:
                    st.error("❌ Please enter a location before assigning.")
    else:
        st.success("✅ No items without store location.")

    # ✅ Section 2: Edit Existing Locations (with specific expiration dates)
    st.subheader("📝 Update Store Locations")

    # ✅ Filter for items with assigned locations and quantity > 0
    assigned_location_df = items_df[
        (~items_df["storelocation"].isna()) & (items_df["currentquantity"] > 0)
    ]

    if not assigned_location_df.empty:
        st.write("Modify existing store locations:")

        # Select item
        item_options = assigned_location_df["itemnameenglish"].unique()
        selected_item_name = st.selectbox("Select item to edit location", item_options)

        # Filter item expiration dates
        item_expirations_df = assigned_location_df[
            assigned_location_df["itemnameenglish"] == selected_item_name
        ][["expirationdate", "storelocation", "currentquantity"]]

        st.write(f"### 📅 Expiration dates for '{selected_item_name}'")
        st.dataframe(item_expirations_df, use_container_width=True)

        # Select specific expiration dates to update
        expiration_dates = item_expirations_df["expirationdate"].dt.strftime("%Y-%m-%d").tolist()
        selected_expirations = st.multiselect("Select expiration dates to update location", expiration_dates)

        new_location = st.text_input("Enter new store location:", value="")

        if st.button("Update Selected Expirations Location"):
            if selected_expirations and new_location:
                for exp_date in selected_expirations:
                    receive_handler.update_item_location_specific(
                        item_id=assigned_location_df.loc[
                            (assigned_location_df["itemnameenglish"] == selected_item_name) &
                            (assigned_location_df["expirationdate"] == pd.to_datetime(exp_date)),
                            "itemid"
                        ].values[0],
                        expiration_date=exp_date,
                        new_location=new_location
                    )
                st.success(f"✅ Store location updated for selected expirations of '{selected_item_name}'!")
                st.rerun()
            else:
                st.error("❌ Please select expiration dates and enter a valid location.")
    else:
        st.info("ℹ️ No items currently available for location updates.")
