import streamlit as st
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    """Handles all database interactions related to purchase orders."""

    def get_all_purchase_orders(self):
        """Fetch all *active* purchase orders (excluding completed/rejected ones)."""
        query = """
        SELECT 
            po.POID, po.OrderDate, po.ExpectedDelivery, po.Status, po.RespondedAt,
            s.SupplierName, 
            poi.ItemID, i.ItemNameEnglish, poi.OrderedQuantity, poi.EstimatedPrice,
            i.ItemPicture
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        WHERE po.Status NOT IN ('Completed', 'Rejected')  -- ✅ Exclude Completed & Rejected
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)

    def get_archived_purchase_orders(self):
        """Fetch completed and rejected purchase orders separately."""
        query_completed = """
        SELECT POID, SupplierID, OrderDate, ExpectedDelivery, Status 
        FROM PurchaseOrders 
        WHERE Status = 'Completed'
        ORDER BY OrderDate DESC
        """

        query_rejected = """
        SELECT POID, SupplierID, OrderDate, ExpectedDelivery, Status 
        FROM PurchaseOrders 
        WHERE Status = 'Rejected'
        ORDER BY OrderDate DESC
        """

        completed_orders = self.fetch_data(query_completed)
        rejected_orders = self.fetch_data(query_rejected)

        return completed_orders, rejected_orders
