import streamlit as st
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    """Handles all database interactions related to purchase orders."""

    def get_all_purchase_orders(self):
        """Fetch all purchase orders with item details, supplier name, and status."""
        query = """
        SELECT 
            po.POID, po.OrderDate, po.ExpectedDelivery, po.Status,
            po.RespondedAt,
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

    def get_suppliers(self):
        """Fetch supplier list with SupplierID and SupplierName."""
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    def get_items(self):
        """Fetch all items available for purchase order selection."""
        query = """
        SELECT ItemID, ItemNameEnglish, ItemPicture, AverageRequired
        FROM Item
        """
        return self.fetch_data(query)

    def create_manual_purchase_order(self, supplier_id, expected_delivery, items):
        """Create a manual purchase order and link items to it."""
        query_po = """
        INSERT INTO PurchaseOrders (SupplierID, ExpectedDelivery)
        VALUES (%s, %s)
        RETURNING POID
        """
        po_id_result = self.execute_command_returning(query_po, (supplier_id, expected_delivery))
        
        if not po_id_result:
            return None
        
        po_id = po_id_result[0]

        query_poi = """
        INSERT INTO PurchaseOrderItems (POID, ItemID, Quantity)
        VALUES (%s, %s, %s)
        """
        for item in items:
            self.execute_command(query_poi, (po_id, item["item_id"], item["quantity"]))

        return po_id
