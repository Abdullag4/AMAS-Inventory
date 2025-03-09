import streamlit as st
import pandas as pd
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    """Handles all purchase order-related database operations."""

    # ✅ Fetch all suppliers
    def get_suppliers(self):
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    # ✅ Fetch all items (Including item pictures)
    def get_items(self):
        query = """
        SELECT ItemID, ItemNameEnglish, ItemPicture 
        FROM Item
        """
        return self.fetch_data(query)

    # ✅ Create Manual PO
    def create_manual_po(self, supplier_id, po_items):
        """Creates a manual purchase order and links items to it."""
        try:
            # ✅ Step 1: Insert new PO
            po_query = """
            INSERT INTO PurchaseOrders (SupplierID)
            VALUES (%s)
            RETURNING POID
            """
            po_id_result = self.execute_command_returning(po_query, (supplier_id,))
            if not po_id_result:
                return None

            po_id = po_id_result[0]

            # ✅ Step 2: Link Items to PO
            for item in po_items:
                query = """
                INSERT INTO PurchaseOrderItems (POID, ItemID, Quantity, EstimatedPrice)
                VALUES (%s, %s, %s, %s)
                """
                self.execute_command(query, (po_id, item["item_id"], item["quantity"], item["estimated_price"] or None))

            return po_id
        except Exception as e:
            st.error(f"❌ Error creating PO: {e}")
            return None

    # ✅ Fetch All Purchase Orders for Tracking
    def get_all_purchase_orders(self):
        query = """
        SELECT po.POID, po.SupplierID, s.SupplierName, po.Status, po.RespondedAt, po.ExpectedDelivery,
               poi.ItemID, i.ItemNameEnglish, poi.Quantity, poi.EstimatedPrice, i.ItemPicture
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)
