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
            poi.ReceivedQuantity, poi.SupProposedQuantity, poi.SupProposedPrice, i.ItemPicture
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        WHERE po.Status NOT IN ('Completed', 'Declined')
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)

    def get_archived_purchase_orders(self):
        query = """
        SELECT 
            po.POID, po.OrderDate, po.ExpectedDelivery, po.Status, po.RespondedAt, po.ActualDelivery, po.CreatedBy,
            s.SupplierName, 
            poi.ItemID, i.ItemNameEnglish, poi.OrderedQuantity, poi.EstimatedPrice,
            poi.ReceivedQuantity, i.ItemPicture
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        JOIN Item i ON poi.ItemID = i.ItemID
        WHERE po.Status IN ('Completed', 'Declined')
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)

    def create_manual_po(self, supplier_id, expected_delivery, items, created_by, original_poid=None):
        """Creates a manual PO, optionally linking it to an OriginalPOID (for acceptance of proposals)."""
        query_po = """
        INSERT INTO PurchaseOrders (SupplierID, ExpectedDelivery, CreatedBy, OriginalPOID)
        VALUES (%s, %s, %s, %s)
        RETURNING POID
        """
        po_id_result = self.execute_command_returning(query_po, (supplier_id, expected_delivery, created_by, original_poid))
        
        if not po_id_result:
            return None
        
        po_id = po_id_result[0]

        query_poi = """
        INSERT INTO PurchaseOrderItems (POID, ItemID, OrderedQuantity, EstimatedPrice, ReceivedQuantity)
        VALUES (%s, %s, %s, %s, 0)
        """
        for item in items:
            self.execute_command(query_poi, (
                po_id,
                item["item_id"],
                item["quantity"],
                item.get("estimated_price", None)
            ))

        return po_id

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

    # --- NEW/RE-ADDED: for autopo.py logic ---
    def get_item_supplier_mapping(self):
        """Fetches item-supplier relationships to filter items per supplier (autopo usage)."""
        query = "SELECT ItemID, SupplierID FROM ItemSupplier"
        return self.fetch_data(query)

    def get_proposed_pos(self):
        """Fetch all POs with ProposedStatus = 'Proposed'."""
        query = """
        SELECT *
        FROM PurchaseOrders
        WHERE ProposedStatus = 'Proposed'
        """
        return self.fetch_data(query)

    def accept_proposed_po(self, proposed_po_id):
        """Accept a proposed PO, create a new normal PO from the proposed data, mark original as Accepted."""
        # 1) fetch existing PO info
        po_info = self.fetch_data("SELECT * FROM PurchaseOrders WHERE POID = %s", (proposed_po_id,)).iloc[0]
        # 2) fetch items
        items_info = self.fetch_data("SELECT * FROM PurchaseOrderItems WHERE POID = %s", (proposed_po_id,))

        # 3) create new normal PO from the proposed fields
        new_poid = self.create_manual_po(
            po_info['supplierid'],
            po_info['supproposeddeliver'],  # Proposed date
            [
                {
                    "item_id": item["itemid"],
                    "quantity": item["supproposedquantity"],
                    "estimated_price": item["supproposedprice"]
                } for _, item in items_info.iterrows()
            ],
            po_info['createdby'],
            original_poid=proposed_po_id
        )

        # 4) mark original PO as Accepted
        self.execute_command(
            "UPDATE PurchaseOrders SET ProposedStatus = 'Accepted' WHERE POID = %s",
            (proposed_po_id,)
        )
        return new_poid

    def decline_proposed_po(self, proposed_po_id):
        """Decline a proposed PO, set ProposedStatus = 'Declined'."""
        self.execute_command(
            "UPDATE PurchaseOrders SET ProposedStatus = 'Declined' WHERE POID = %s",
            (proposed_po_id,)
        )
