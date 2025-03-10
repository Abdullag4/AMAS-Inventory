import streamlit as st
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    """Handles all database interactions related to purchase orders."""

    def get_all_purchase_orders(self):
        """Fetch all purchase orders with item details, supplier name, and status."""
        query = """
        SELECT 
            po.POID, po.OrderDate, po.ExpectedDelivery, po.Status,
            s.SupplierName, 
            poi.ItemID, i.ItemNameEnglish, poi.Quantity, poi.EstimatedPrice,
            i.ItemPicture
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)
