import streamlit as st
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    """Handles all database interactions related to purchase orders."""

    def get_all_purchase_orders(self):
        query = """
        SELECT 
            po.POID, po.OrderDate, po.ExpectedDelivery, po.Status, po.RespondedAt, po.ActualDelivery,
            po.CreatedBy, po.SupProposedDeliver, po.ProposedStatus, po.OriginalPOID, po.SupplierNote,
            s.SupplierName, 
            poi.ItemID, i.ItemNameEnglish, poi.OrderedQuantity, poi.EstimatedPrice,
            poi.SupProposedQuantity, poi.SupProposedPrice,
            poi.ReceivedQuantity, i.ItemPicture
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        WHERE po.Status NOT IN ('Completed', 'Declined')
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)

    def get_proposed_pos(self):
        query = """
        SELECT DISTINCT
            po.POID, po.OrderDate, po.ExpectedDelivery, po.SupProposedDeliver, po.SupplierNote,
            po.ProposedStatus, po.OriginalPOID, po.CreatedBy, s.SupplierName
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        WHERE po.ProposedStatus = 'Proposed'
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)

    def accept_proposed_po(self, proposed_po_id):
        query_po = """
        INSERT INTO PurchaseOrders (SupplierID, ExpectedDelivery, Status, OriginalPOID, CreatedBy)
        SELECT SupplierID, SupProposedDeliver, 'Pending', POID, CreatedBy
        FROM PurchaseOrders WHERE POID = %s
        RETURNING POID
        """
        new_po_id = self.execute_command_returning(query_po, (proposed_po_id,))[0]

        query_items = """
        INSERT INTO PurchaseOrderItems (POID, ItemID, OrderedQuantity, EstimatedPrice, ReceivedQuantity)
        SELECT %s, ItemID, SupProposedQuantity, SupProposedPrice, 0
        FROM PurchaseOrderItems WHERE POID = %s
        """
        self.execute_command(query_items, (new_po_id, proposed_po_id))

        query_update_status = """
        UPDATE PurchaseOrders SET ProposedStatus = 'Accepted' WHERE POID = %s
        """
        self.execute_command(query_update_status, (proposed_po_id,))

    def decline_proposed_po(self, proposed_po_id):
        query = """
        UPDATE PurchaseOrders SET ProposedStatus = 'Declined' WHERE POID = %s
        """
        self.execute_command(query, (proposed_po_id,))

    def update_po_status_to_received(self, poid):
        query = """
        UPDATE PurchaseOrders
        SET Status = 'Received', ActualDelivery = CURRENT_TIMESTAMP
        WHERE POID = %s
        """
        self.execute_command(query, (poid,))

    def update_received_quantity(self, poid, item_id, received_quantity):
        query = """
        UPDATE PurchaseOrderItems
        SET ReceivedQuantity = %s
        WHERE POID = %s AND ItemID = %s
        """
        self.execute_command(query, (received_quantity, poid, item_id))
