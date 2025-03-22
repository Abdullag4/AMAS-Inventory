import streamlit as st
import pandas as pd
from db_handler import DatabaseManager
from datetime import datetime

class POHandler(DatabaseManager):
    """Handles all database interactions related to purchase orders."""

    def get_all_purchase_orders(self):
        query = """
        SELECT 
            po.POID, po.OrderDate, po.ExpectedDelivery, po.Status, po.RespondedAt, 
            po.ActualDelivery, po.CreatedBy, po.SupProposedDeliver, po.ProposedStatus, 
            po.OriginalPOID, po.SupplierNote,
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
            po.POID, po.OrderDate, po.ExpectedDelivery, po.Status, po.RespondedAt, 
            po.ActualDelivery, po.CreatedBy,
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

    def get_items(self):
        """Fetch basic item info for manual PO creation."""
        query = """
        SELECT ItemID, ItemNameEnglish, ItemPicture, AverageRequired
        FROM Item
        """
        return self.fetch_data(query)

    def create_manual_po(self, supplier_id, expected_delivery, items, created_by, original_poid=None):
        """
        Creates a manual PO, optionally linking it to an OriginalPOID (for acceptance of proposals).
        We convert any potential numpy types to native Python int/datetime to avoid 'can't adapt' errors.
        """
        # Ensure supplier_id is a native int
        if supplier_id is not None:
            supplier_id = int(supplier_id)

        # Convert original_poid to int if not None
        if original_poid is not None:
            original_poid = int(original_poid)

        # If expected_delivery is a NumPy datetime64, convert it:
        if pd.notnull(expected_delivery) and not isinstance(expected_delivery, datetime):
            # Use .to_pydatetime() if it's a Timestamp
            expected_delivery = pd.to_datetime(expected_delivery).to_pydatetime()

        query_po = """
        INSERT INTO PurchaseOrders (SupplierID, ExpectedDelivery, CreatedBy, OriginalPOID)
        VALUES (%s, %s, %s, %s)
        RETURNING POID
        """
        po_id_result = self.execute_command_returning(
            query_po, (supplier_id, expected_delivery, created_by, original_poid)
        )
        
        if not po_id_result:
            return None
        
        po_id = po_id_result[0]

        query_poi = """
        INSERT INTO PurchaseOrderItems 
            (POID, ItemID, OrderedQuantity, EstimatedPrice, ReceivedQuantity)
        VALUES 
            (%s, %s, %s, %s, 0)
        """
        for item in items:
            # item["item_id"] may also be numpy type
            item_id = int(item["item_id"])
            quantity = int(item["quantity"])  # convert to Python int
            estimated_price = item.get("estimated_price", None)

            self.execute_command(query_poi, (
                po_id,
                item_id,
                quantity,
                estimated_price
            ))

        return po_id

    def update_po_status_to_received(self, poid):
        # Make sure poid is a python int
        poid = int(poid)
        query = """
        UPDATE PurchaseOrders
        SET Status = 'Received', ActualDelivery = CURRENT_TIMESTAMP
        WHERE POID = %s
        """
        self.execute_command(query, (poid,))

    def update_received_quantity(self, poid, item_id, received_quantity):
        poid = int(poid)
        item_id = int(item_id)
        received_quantity = int(received_quantity)

        query = """
        UPDATE PurchaseOrderItems
        SET ReceivedQuantity = %s
        WHERE POID = %s AND ItemID = %s
        """
        self.execute_command(query, (received_quantity, poid, item_id))

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
        """
        Accept a proposed PO, create a new normal PO from the proposed data,
        mark original as 'Accepted'.
        """
        # Convert to int to avoid 'numpy.int64' issues
        proposed_po_id = int(proposed_po_id)

        # 1) fetch existing PO info
        po_info = self.fetch_data(
            "SELECT * FROM PurchaseOrders WHERE POID = %s", (proposed_po_id,)
        ).iloc[0]

        # 2) fetch items
        items_info = self.fetch_data(
            "SELECT * FROM PurchaseOrderItems WHERE POID = %s", (proposed_po_id,)
        )

        # Convert SupplierID to int
        supplier_id = int(po_info['supplierid']) if pd.notnull(po_info['supplierid']) else None
        # Convert supProposedDeliver to python datetime if it's not null
        sup_proposed_date = None
        if pd.notnull(po_info['supproposeddeliver']):
            sup_proposed_date = pd.to_datetime(po_info['supproposeddeliver']).to_pydatetime()

        # 3) create new normal PO from the proposed fields
        new_poid = self.create_manual_po(
            supplier_id,
            sup_proposed_date,  # Proposed date
            [
                {
                    "item_id": int(item["itemid"]),
                    "quantity": int(item["supproposedquantity"]),
                    "estimated_price": item["supproposedprice"]
                } 
                for _, item in items_info.iterrows()
            ],
            created_by=po_info['createdby'],
            original_poid=proposed_po_id
        )

        # 4) mark original PO as 'Accepted'
        self.execute_command(
            "UPDATE PurchaseOrders SET ProposedStatus = 'Accepted' WHERE POID = %s",
            (proposed_po_id,)
        )
        return new_poid

    def decline_proposed_po(self, proposed_po_id):
        """Decline a proposed PO, set ProposedStatus = 'Declined'."""
        proposed_po_id = int(proposed_po_id)  # also ensure python int
        self.execute_command(
            "UPDATE PurchaseOrders SET ProposedStatus = 'Declined' WHERE POID = %s",
            (proposed_po_id,)
        )
