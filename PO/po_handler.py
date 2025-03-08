import streamlit as st
import pandas as pd
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    """Handles all Purchase Order related database interactions."""

    # ✅ Fetch low stock items along with their suppliers
    def get_low_stock_items_with_supplier(self):
        query = """
        SELECT i.ItemID, i.ItemNameEnglish, i.ItemPicture, i.Threshold, 
               i.AverageRequired, inv.Quantity, s.SupplierID, s.SupplierName
        FROM Inventory inv
        JOIN Item i ON inv.ItemID = i.ItemID
        JOIN ItemSupplier isup ON i.ItemID = isup.ItemID
        JOIN Supplier s ON isup.SupplierID = s.SupplierID
        WHERE inv.Quantity < i.Threshold
        """
        return self.fetch_data(query)

    # ✅ Insert a new purchase order
    def create_purchase_order(self, supplier_id, expected_delivery, items):
        """Creates a new purchase order and links it to multiple items."""
        query = """
        INSERT INTO PurchaseOrders (SupplierID, OrderDate, ExpectedDelivery, Status, CreatedAt)
        VALUES (%s, CURRENT_TIMESTAMP, %s, 'Pending', CURRENT_TIMESTAMP)
        RETURNING POID
        """
        po_id = self.execute_command_returning(query, (supplier_id, expected_delivery))

        if po_id:
            po_id = po_id[0]  # Extract POID
            self.add_items_to_purchase_order(po_id, items)
            return po_id
        return None

    # ✅ Add items to a purchase order
    def add_items_to_purchase_order(self, po_id, items):
        """Links multiple items to a purchase order in the PurchaseOrderItems table."""
        query = """
        INSERT INTO PurchaseOrderItems (POID, ItemID, Quantity)
        VALUES (%s, %s, %s)
        """
        for item in items:
            self.execute_command(query, (po_id, item["ItemID"], item["Quantity"]))

    # ✅ Fetch all purchase orders with item details
    def get_all_purchase_orders(self):
        query = """
        SELECT po.POID, poi.ItemID, i.ItemNameEnglish, i.ItemPicture, poi.Quantity, 
               po.Status, po.OrderDate, po.ExpectedDelivery, s.SupplierName
        FROM PurchaseOrders po
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)

    # ✅ Fetch purchase orders for a specific supplier
    def get_supplier_purchase_orders(self, supplier_id):
        query = """
        SELECT po.POID, poi.ItemID, i.ItemNameEnglish, i.ItemPicture, poi.Quantity, 
               po.Status, po.OrderDate, po.ExpectedDelivery
        FROM PurchaseOrders po
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        WHERE po.SupplierID = %s
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query, (supplier_id,))

    # ✅ Update purchase order status
    def update_purchase_order_status(self, po_id, status, actual_delivery=None):
        """Updates the status of a purchase order and sets delivery date if received."""
        query = "UPDATE PurchaseOrders SET Status = %s"
        params = [status]

        if status == "Received" and actual_delivery:
            query += ", ActualDelivery = %s"
            params.append(actual_delivery)

        query += " WHERE POID = %s"
        params.append(po_id)

        self.execute_command(query, tuple(params))
