import streamlit as st
import pandas as pd
from reports.report_handler import ReportHandler

report_handler = ReportHandler()

def near_expiry_tab():
    """Tab displaying items that are close to expiration."""
    st.header("⏳ Items Near Expiry")

    # ✅ Allow user to set expiry threshold (Default: 30 days)
    days_threshold = st.slider("⚠️ Show items expiring in the next X days:", min_value=7, max_value=90, value=30)

    # ✅ Fetch data
    expiry_data = report_handler.get_items_near_expiry(days_threshold)

    if expiry_data.empty:
        st.success("✅ No items are nearing expiry! Inventory is in good condition.")
        return

    # ✅ Format the table
    expiry_data["DaysToExpiry"] = expiry_data["daystoexpiry"].apply(lambda x: f"{x} days" if x > 0 else "Expiring Today! ⚠️")

    # ✅ Display the data
    st.subheader(f"📋 Items Expiring in the Next {days_threshold} Days")
    st.dataframe(
        expiry_data[["itemnameenglish", "currentstock", "expirationdate", "DaysToExpiry", "storagelocation"]].rename(columns={
            "itemnameenglish": "Item Name",
            "currentstock": "Stock",
            "expirationdate": "Expiry Date",
            "storagelocation": "Location"
        }),
        use_container_width=True
    )

    # ✅ Highlight Critical Items
    expiring_soon = expiry_data[expiry_data["daystoexpiry"] <= 7]
    if not expiring_soon.empty:
        st.warning("⚠️ **Critical Expiry Warning!** Some items expire in the next 7 days.")
        st.dataframe(expiring_soon[["itemnameenglish", "expirationdate", "storagelocation"]])

    st.success("✅ Report generated successfully!")
