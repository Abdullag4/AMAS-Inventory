import streamlit as st
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    """Handles all database interactions related to purchase orders."""

    def get_all_purchase_orders(self):
        """Fetch all purchase orders with item details, supplier name, and status."""
        query = """
        SELECT 
            po.poid,  -- ✅ Ensure POID is correctly retrieved
            po.orderdate, 
            po.expecteddelivery, 
            po.status,
            po.respondedat,
            s.suppliername, 
            poi.itemid, 
            i.itemnameenglish, 
            poi.quantity, 
            poi.estimatedprice,
            i.itempicture
        FROM purchaseorders po
        JOIN supplier s ON po.supplierid = s.supplierid
        JOIN purchaseorderitems poi ON po.poid = poi.poid
        JOIN item i ON poi.itemid = i.itemid
        ORDER BY po.orderdate DESC
        """
        return self.fetch_data(query)
