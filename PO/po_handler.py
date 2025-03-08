import streamlit as st
from db_handler import DatabaseManager
import pandas as pd

class POHandler(DatabaseManager):

    def get_items_below_threshold(self):
        query = """
        SELECT i.ItemID, i.ItemNameEnglish, i.ItemPicture, 
               (i.AverageRequired - SUM(inv.Quantity)) AS required_quantity,
               s.SupplierName, s.SupplierID
        FROM Item i
        JOIN Inventory inv ON i.ItemID = inv.ItemID
        JOIN ItemSupplier isup ON i.ItemID = isup.ItemID
        JOIN Supplier s ON isup.SupplierID = s.SupplierID
        GROUP BY i.ItemID, i.ItemNameEnglish, i.ItemPicture, s.SupplierName, s.SupplierID, i.Threshold, i.AverageRequired
        HAVING SUM(inv.Quantity) < i.Threshold
        """
        return self.fetch_data(query)

    def create_auto_purchase_orders(self, items_df):
        for _, row in items_df.iterrows():
            supplier_id = row['supplierid']
            item_id = row['itemid']
            required_qty = int(row['required_quantity'])

            # Create PO
            po_query = """
            INSERT INTO PurchaseOrder (SupplierID, OrderDate, Status)
            VALUES (%s, CURRENT_TIMESTAMP, 'Pending') RETURNING POID
            """
            po_id = self.execute_command_returning(po_query, [supplier_id])[0]

            # Insert PO Detail
            po_detail_query = """
            INSERT INTO PurchaseOrderDetail (POID, ItemID, Quantity, ItemName, ItemPicture)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.execute_command(po_detail_query, [
                po_id, item_id, required_qty, row['itemnameenglish'], row['itempicture']
            ])

    def get_all_purchase_orders(self):
        query = """
        SELECT po.POID, pod.ItemName, pod.Quantity, po.Status, po.ExpectedDelivery, po.ActualDelivery
        FROM PurchaseOrder po
        JOIN PurchaseOrderDetail pod ON po.POID = pod.POID
        ORDER BY po.POID DESC
        """
        return self.fetch_data(query)

    def create_manual_po(self, supplier_id, item_id, quantity):
        po_query = """
        INSERT INTO PurchaseOrder (SupplierID, OrderDate, Status)
        VALUES (%s, CURRENT_TIMESTAMP, 'Pending') RETURNING POID
        """
        po_id = self.execute_command_returning(po_query, [supplier_id])[0]

        item_details = self.fetch_data("SELECT ItemNameEnglish, ItemPicture FROM Item WHERE ItemID = %s", [item_id]).iloc[0]

        po_detail_query = """
        INSERT INTO PurchaseOrderDetail (POID, ItemID, Quantity, ItemName, ItemPicture)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_command(po_detail_query, [
            po_id, item_id, quantity, item_details['itemnameenglish'], item_details['itempicture']
        ])

