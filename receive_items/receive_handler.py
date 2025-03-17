from db_handler import DatabaseManager

class ReceiveHandler(DatabaseManager):
    """Handles database interactions for receiving items and item locations."""

    def get_received_pos(self):
        """Fetch all POs with status 'Received' but not yet 'Completed'."""
        query = """
        SELECT po.POID, po.ExpectedDelivery, s.SupplierName
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        WHERE po.Status = 'Received'
        """
        return self.fetch_data(query)

    def get_po_items(self, poid):
        """Fetch items details for a specific PO."""
        query = """
        SELECT poi.ItemID, i.ItemNameEnglish, poi.OrderedQuantity, poi.ReceivedQuantity
        FROM PurchaseOrderItems poi
        JOIN Item i ON poi.ItemID = i.ItemID
        WHERE poi.POID = %s
        """
        return self.fetch_data(query, (poid,))

    def add_items_to_inventory(self, inventory_items):
        """Insert received items into Inventory."""
        query = """
        INSERT INTO Inventory (ItemID, Quantity, ExpirationDate, StorageLocation, DateReceived)
        VALUES (%s, %s, %s, %s, CURRENT_DATE)
        """
        for item in inventory_items:
            self.execute_command(query, (
                item["item_id"],
                item["quantity"],
                item["expiration_date"],
                item["storage_location"]
            ))

    def mark_po_completed(self, poid):
        """Update PO status to Completed after items added to inventory."""
        query = """
        UPDATE PurchaseOrders
        SET Status = 'Completed'
        WHERE POID = %s
        """
        self.execute_command(query, (poid,))

    def update_received_quantity(self, poid, item_id, received_quantity):
        """Update the actual received quantity in PurchaseOrderItems."""
        query = """
        UPDATE PurchaseOrderItems
        SET ReceivedQuantity = %s
        WHERE POID = %s AND ItemID = %s
        """
        self.execute_command(query, (received_quantity, poid, item_id))

    def get_items_with_locations_and_expirations(self):
        """Fetch items with their storage locations and expiration dates, grouped properly."""
        query = """
        SELECT 
            i.ItemID AS itemid,
            i.ItemNameEnglish AS itemnameenglish,
            i.Barcode AS barcode,
            inv.StorageLocation AS storelocation,
            inv.ExpirationDate AS expirationdate,
            SUM(inv.Quantity) AS currentquantity
        FROM Item i
        JOIN Inventory inv ON i.ItemID = inv.ItemID
        GROUP BY i.ItemID, i.ItemNameEnglish, i.Barcode, inv.StorageLocation, inv.ExpirationDate
        HAVING SUM(inv.Quantity) > 0
        """
        return self.fetch_data(query)

    def get_items_without_location(self):
        """Fetch items currently in inventory but without an assigned location."""
        query = """
        SELECT 
            i.ItemID AS itemid, 
            i.ItemNameEnglish AS itemnameenglish, 
            i.Barcode AS barcode,
            COALESCE(inv.Quantity, 0) AS currentquantity
        FROM Item i
        JOIN Inventory inv ON i.ItemID = inv.ItemID
        WHERE inv.StorageLocation IS NULL OR inv.StorageLocation = ''
        """
        return self.fetch_data(query)

    def update_item_location(self, item_id, new_location):
        """Updates the store location for an item (without considering expiration date)."""
        query = """
        UPDATE Inventory
        SET StorageLocation = %s
        WHERE ItemID = %s AND (StorageLocation IS NULL OR StorageLocation = '')
        """
        self.execute_command(query, (new_location, item_id))

    def update_item_location_specific(self, item_id, expiration_date, new_location):
        """Updates the store location for a specific item with a specific expiration date."""
        query = """
        UPDATE Inventory
        SET StorageLocation = %s
        WHERE ItemID = %s AND ExpirationDate = %s
        """
        self.execute_command(query, (new_location, item_id, expiration_date))
