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
        """Fetch all items with their storage locations and expiration dates."""
        query = """
        SELECT 
            i.ItemID as itemid,
            i.ItemNameEnglish as itemnameenglish,
            i.Barcode as barcode,
            inv.StorageLocation as storelocation,
            inv.ExpirationDate as expirationdate,
            SUM(inv.Quantity) AS currentquantity
        FROM Item i
        LEFT JOIN Inventory inv ON i.ItemID = inv.ItemID
        GROUP BY i.ItemID, i.ItemNameEnglish, i.Barcode, inv.StorageLocation, inv.ExpirationDate
        """
        return self.fetch_data(query)

    def update_item_location_specific(self, item_id, expiration_date, new_location):
        """Update an item's storage location for a specific expiration date."""
        query = """
        UPDATE Inventory
        SET StorageLocation = %s
        WHERE ItemID = %s AND ExpirationDate = %s
        """
        self.execute_command(query, (new_location, item_id, expiration_date))

### ✅ **How to Properly Add New Methods:**
When adding new methods to a Python class (like `ReceiveHandler`):

1. **Define the method clearly** within your class using the syntax:
    ```python
    def method_name(self, parameter1, parameter2):
        # method logic
    ```
2. **Ensure correct indentation**: All methods must be indented consistently within the class.
3. **Save the file** after adding the new methods.

### 🚩 **Final Note:**
Make sure to update your database queries and ensure that your database structure matches the query logic in these new methods. Specifically, verify the existence of columns (`StorageLocation`, `ExpirationDate`, etc.) in your `Inventory` table.
