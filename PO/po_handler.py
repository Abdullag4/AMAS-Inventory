from db_handler import DatabaseManager
import pandas as pd

class POHandler(DatabaseManager):
    def get_low_stock_items_with_supplier(self):
        query = """
        SELECT i.ItemID, i.ItemNameEnglish, i.ItemPicture, s.SupplierName, 
               (i.AverageRequired - SUM(inv.Quantity)) AS required_quantity
        FROM Item i
        JOIN Inventory inv ON i.ItemID = inv.ItemID
        JOIN ItemSupplier isup ON i.ItemID = isup.ItemID
        JOIN Supplier s ON isup.SupplierID = s.SupplierID
        GROUP BY i.ItemID, i.ItemNameEnglish, i.ItemPicture, s.SupplierName, i.Threshold, i.AverageRequired
        HAVING SUM(inv.Quantity) < i.Threshold
        """
        return self.fetch_data(query)

    def send_auto_po(self, low_stock_items):
        for _, row in low_stock_items.iterrows():
            query = """
            INSERT INTO PurchaseOrders (ItemID, SupplierID, Quantity, Status, OrderDate)
            VALUES (%s, (SELECT SupplierID FROM Supplier WHERE SupplierName = %s), %s, 'Pending', CURRENT_TIMESTAMP)
            """
            params = (row["itemid"], row["suppliername"], int(row["required_quantity"]))
            self.execute_command(query, params)

    def get_all_purchase_orders(self):
        query = """
        SELECT po.POID, po.ItemID, i.ItemNameEnglish, i.ItemPicture, po.Quantity, po.Status, po.OrderDate, po.ExpectedDelivery, s.SupplierName
        FROM PurchaseOrders po
        JOIN Item i ON po.ItemID = i.ItemID
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        ORDER BY po.OrderDate DESC
        """
        return self.fetch_data(query)
