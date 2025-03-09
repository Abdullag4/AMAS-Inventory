import streamlit as st
import pandas as pd
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    """Handles all purchase order-related database operations."""

    def get_suppliers(self):
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    def get_items(self):
        query = "SELECT ItemID, ItemNameEnglish, ItemPicture FROM Item"
        return self.fetch_data(query)

    def create_manual_po(self, supplier_id, po_items):
        try:
            po_query = """
            INSERT INTO PurchaseOrders (SupplierID)
            VALUES (%s)
            RETURNING POID
            """
            po_id_result = self.execute_command_returning(po_query, (supplier_id,))
            if not po_id_result:
                return None

            po_id = po_id_result[0]

            for item in po_items:
                query = """
                INSERT INTO PurchaseOrderItems (POID, ItemID, Quantity, EstimatedPrice)
                VALUES (%s, %s, %s, %s)
                """
                self.execute_command(query, (po_id, item["item_id"], item["quantity"], item["estimated_price"]))

            return po_id
        except Exception as e:
            st.error(f"❌ Error creating PO: {e}")
            return None
