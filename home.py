import streamlit as st
from neon_handler import fetch_inventory

st.title("🏠 Inventory Home Page")

st.subheader("📊 Inventory Overview")

# Fetch inventory data
df = fetch_inventory()

if not df.empty:
    st.metric(label="Total Inventory Items", value=len(df))
    total_quantity = df["Quantity"].sum()
    st.metric(label="Total Stock Quantity", value=total_quantity)
    
    # Show upcoming expired items
    st.subheader("⚠️ Items Near Expiry")
    expired_items = df[df["ExpirationDate"] <= pd.to_datetime("today") + pd.Timedelta(days=30)]
    if not expired_items.empty:
        st.dataframe(expired_items)
    else:
        st.success("No items are near expiry in the next 30 days.")
else:
    st.info("No inventory data available.")
