import pandas as pd
from db_handler import DatabaseManager

class POHandler(DatabaseManager):
    def get_low_stock_items_with_supplier(self):
        query = """
        SELECT 
            i.ItemID,
            i.ItemNameEnglish,
            i.ItemPicture,
            (i.averagerequired - COALESCE(SUM(inv.Quantity), 0)) AS required_quantity,
            s.SupplierName
        FROM Item i
        LEFT JOIN Inventory inv ON i.ItemID = inv.ItemID
        LEFT JOIN ItemSupplier isup ON i.ItemID = isup.ItemID
        LEFT JOIN Supplier s ON isup.SupplierID = s.SupplierID
        GROUP BY i.ItemID, i.ItemNameEnglish, i.ItemPicture, s.SupplierName, i.threshold, i.averagerequired
        HAVING COALESCE(SUM(inv.Quantity), 0) < i.threshold
        """
        return self.fetch_data(query)

    def send_auto_po(self, po_data_df):
        # Placeholder implementation
        for _, row in po_data_df.iterrows():
            # Insert into PurchaseOrder table, send email, etc.
            print(f"Sending PO: Item {row['ItemNameEnglish']} to {row['SupplierName']} for {row['required_quantity']} units.")
