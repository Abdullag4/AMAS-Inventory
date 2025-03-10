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

        query_poid = """
        INSERT INTO PurchaseOrderItems (POID, ItemID, Quantity)
        VALUES (%s, %s, %s)
        """
        for item in items:
            self.execute_command(query_poi, (po_id, item["item_id"], item["quantity"]))

        return po_id
