import streamlit as st
import pandas as pd
from reports.report_handler import ReportHandler

report_handler = ReportHandler()

def sup_performance_tab():
    """Tab for Supplier Performance Analysis."""
    st.header("📊 Supplier Performance Report")

    # ✅ Fetch supplier performance data
    data = report_handler.get_supplier_performance()

    if data.empty:
        st.warning("⚠️ No supplier performance data available.")
        return

    # ✅ Calculate performance metrics
    data["On-Time Delivery Rate"] = (data["ontimedeliveries"] / data["totalorders"]).fillna(0) * 100
    data["Quantity Accuracy Rate"] = (data["correctquantityorders"] / data["totalorders"]).fillna(0) * 100

    # ✅ Format displayed table
    display_data = data[[
        "suppliername",
        "totalorders",
        "ontimedeliveries",
        "latedeliveries",
        "avglatedays",
        "quantitymismatchorders",
        "On-Time Delivery Rate",
        "Quantity Accuracy Rate"
    ]].rename(columns={
        "suppliername": "Supplier",
        "totalorders": "Total Orders",
        "ontimedeliveries": "On-Time Deliveries",
        "latedeliveries": "Late Deliveries",
        "avglatedays": "Avg Late Days",
        "quantitymismatchorders": "Qty Mismatch Orders"
    })

    # ✅ Display summary table
    st.subheader("📋 Supplier Performance Overview")
    st.dataframe(display_data.style.format({
        "Avg Late Days": "{:.1f}",
        "On-Time Delivery Rate": "{:.1f}%",
        "Quantity Accuracy Rate": "{:.1f}%"
    }), use_container_width=True)

    # ✅ Highlight underperforming suppliers
    low_performance = data[(data["On-Time Delivery Rate"] < 80) | (data["Quantity Accuracy Rate"] < 80)]
    if not low_performance.empty:
        st.subheader("⚠️ Underperforming Suppliers")
        st.error("These suppliers have low reliability scores:")
        st.dataframe(low_performance[["suppliername", "On-Time Delivery Rate", "Quantity Accuracy Rate"]])

    # ✅ Success Message
    st.success("✅ Report generated successfully!")
