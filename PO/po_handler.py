import streamlit as st
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    """Handles all database interactions related to purchase orders."""

    def get_all_purchase_orders(self):
        """Fetch all active purchase orders (Pending, Accepted, Shipping, Received)."""
        query = """
        SELECT 
            po.POID, po.OrderDate, po.ExpectedDelivery, po.Status, po.RespondedAt,
            s.SupplierName, 
            poi.ItemID, i.ItemNameEnglish, poi.OrderedQuantity, poi.EstimatedPrice,
            poi.ReceivedQuantity, i.ItemPicture
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        WHERE po.Status IN ('Pending', 'Accepted', 'Shipping', 'Received')
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)

    def get_archived_purchase_orders(self):
        """Fetch all archived (Completed, Rejected) purchase orders."""
        query = """
        SELECT 
            po.POID, po.OrderDate, po.ExpectedDelivery, po.ActualDelivery, po.Status, po.RespondedAt,
            s.SupplierName,
            poi.ItemID, i.ItemNameEnglish, poi.OrderedQuantity, poi.ReceivedQuantity, poi.EstimatedPrice,
            i.ItemPicture
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        WHERE po.Status IN ('Completed', 'Rejected')
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

    def create_manual_po(self, supplier_id, expected_delivery, items):
        """Creates a manual purchase order and links selected items to it."""
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
        INSERT INTO PurchaseOrderItems (POID, ItemID, OrderedQuantity, EstimatedPrice, ReceivedQuantity)
        VALUES (%s, %s, %s, %s, %s)
        """
        for item in items:
            estimated_price = item.get("estimated_price", None)
            self.execute_command(query_poi, (po_id, item["item_id"], item["quantity"], estimated_price, 0))

        return po_id

    def update_po_status_to_received(self, poid):
        """Marks a purchase order as Received."""
        query = """
        UPDATE PurchaseOrders
        SET Status = 'Received', ActualDelivery = CURRENT_TIMESTAMP
        WHERE POID = %s
        """
        self.execute_command(query, (poid,))

    def update_received_quantity(self, poid, item_id, received_quantity):
        """Update received quantity for specific item in a PO."""
        query = """
        UPDATE PurchaseOrderItems
        SET ReceivedQuantity = %s
        WHERE POID = %s AND ItemID = %s
        """
        self.execute_command(query, (received_quantity, poid, item_id))

    def mark_po_as_completed(self, poid):
        """Marks a purchase order as Completed."""
        query = """
        UPDATE PurchaseOrders
        SET Status = 'Completed'
        WHERE POID = %s
        """
        self.execute_command(query, (poid,))

    def mark_po_as_rejected(self, poid):
        """Marks a purchase order as Rejected."""
        query = """
        UPDATE PurchaseOrders
        SET Status = 'Rejected', RespondedAt = CURRENT_TIMESTAMP
        WHERE POID = %s
        """
        self.execute_command(query, (poid,))
