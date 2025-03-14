import streamlit as st
import pandas as pd
from reports.report_handler import ReportHandler

report_handler = ReportHandler()

def sup_performance_tab():
    """Supplier Performance Report."""
    st.header("📊 Supplier Performance Report")

    # ✅ Fetch purchase order data to analyze supplier performance
    po_data = report_handler.get_supplier_performance_data()

    if po_data.empty:
        st.info("ℹ️ No purchase orders available for analysis.")
        return

    # ✅ Calculate Supplier Performance Metrics
    po_data["DelayDays"] = (po_data["ActualDelivery"] - po_data["ExpectedDelivery"]).dt.days
    po_data["OnTime"] = po_data["DelayDays"] <= 0
    po_data["QuantityMatch"] = po_data["OrderedQuantity"] == po_data["ReceivedQuantity"]

    # ✅ Aggregate Supplier Performance
    supplier_performance = po_data.groupby("SupplierName").agg(
        TotalOrders=("POID", "count"),
        OnTimeDeliveries=("OnTime", "sum"),
        AccurateOrders=("QuantityMatch", "sum"),
        AvgDelayDays=("DelayDays", "mean"),
    ).reset_index()

    # ✅ Calculate Rates
    supplier_performance["OnTimeRate"] = (supplier_performance["OnTimeDeliveries"] / supplier_performance["TotalOrders"]) * 100
    supplier_performance["AccuracyRate"] = (supplier_performance["AccurateOrders"] / supplier_performance["TotalOrders"]) * 100
    supplier_performance["AvgDelayDays"] = supplier_performance["AvgDelayDays"].fillna(0).round(2)

    # ✅ Display the Report
    st.subheader("📋 Supplier Performance Overview")
    st.write("This report evaluates suppliers based on their **on-time delivery and accuracy**.")

    # ✅ Show summary table
    st.dataframe(
        supplier_performance[["SupplierName", "TotalOrders", "OnTimeRate", "AccuracyRate", "AvgDelayDays"]],
        use_container_width=True
    )

    # ✅ Highlight worst-performing suppliers
    st.subheader("⚠️ Suppliers with Low Performance")
    low_performance = supplier_performance[
        (supplier_performance["OnTimeRate"] < 80) | (supplier_performance["AccuracyRate"] < 80)
    ]

    if not low_performance.empty:
        st.warning("🚨 The following suppliers have **low performance**:")
        st.dataframe(
            low_performance[["SupplierName", "OnTimeRate", "AccuracyRate", "AvgDelayDays"]],
            use_container_width=True
        )
    else:
        st.success("✅ All suppliers are performing well!")
