import streamlit as st
from db_handler import DatabaseManager

class ItemHandler(DatabaseManager):
    """Handles all item-related database interactions in a concise way."""

    # 1) Fetch items with automatic column lowercase
    def get_items(self):
        query = """
        SELECT 
            ItemID,
            ItemNameEnglish,
            ItemNameKurdish,
            ClassCat,
            DepartmentCat,
            SectionCat,
            FamilyCat,
            SubFamilyCat,
            ShelfLife,
            Threshold,
            AverageRequired,
            OriginCountry,
            Manufacturer,
            Brand,
            Barcode,
            UnitType,
            Packaging,
            ItemPicture,
            CreatedAt,
            UpdatedAt
        FROM item
        """
        df = self.fetch_data(query)
        if not df.empty:
            # ✅ Lowercase all column names automatically
            df.columns = df.columns.str.lower()
        return df

    def get_suppliers(self):
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        df = self.fetch_data(query)
        if not df.empty:
            df.columns = df.columns.str.lower()
        return df

    def get_item_suppliers(self, item_id):
        query = """
        SELECT s.SupplierName 
        FROM ItemSupplier isup
        JOIN Supplier s ON isup.SupplierID = s.SupplierID
        WHERE isup.ItemID = %s
        """
        df = self.fetch_data(query, (item_id,))
        if not df.empty:
            df.columns = df.columns.str.lower()
            return df["suppliername"].tolist()
        return []

    def add_item(self, item_data, supplier_ids):
        """
        Inserts a new item into 'item' table and links it to suppliers in 'ItemSupplier'.
        item_data keys should match columns in 'item' table (all lowercase).
        """
        columns = ", ".join(item_data.keys())
        placeholders = ", ".join(["%s"] * len(item_data))

        query = f"""
        INSERT INTO item ({columns}, createdat, updatedat)
        VALUES ({placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING itemid
        """
        item_id = self.execute_command_returning(query, list(item_data.values()))
        if item_id:
            self.link_item_suppliers(item_id[0], supplier_ids)
            return item_id[0]
        return None

    def link_item_suppliers(self, item_id, supplier_ids):
        """
        Links an item to multiple suppliers in the ItemSupplier table.
        Avoids duplication by using ON CONFLICT DO NOTHING.
        """
        if not supplier_ids:
            return
        # Build placeholder string like "(%s, %s),(%s, %s),..."
        values = ", ".join(["(%s, %s)"] * len(supplier_ids))
        params = []
        for supplier_id in supplier_ids:
            params.extend([item_id, supplier_id])

        query = f"""
        INSERT INTO ItemSupplier (ItemID, SupplierID)
        VALUES {values}
        ON CONFLICT DO NOTHING
        """
        self.execute_command(query, params)

    def update_item(self, item_id, updated_data):
        """
        Updates an item’s details in 'item' table.
        updated_data = {col: val, col2: val2, ...} (all lowercase).
        """
        if not updated_data:
            st.warning("⚠️ No changes made.")
            return

        set_clause = ", ".join(f"{col} = %s" for col in updated_data.keys())
        query = f"""
        UPDATE item
        SET {set_clause}, updatedat = CURRENT_TIMESTAMP
        WHERE itemid = %s
        """
        params = list(updated_data.values()) + [item_id]
        self.execute_command(query, params)

    def update_item_suppliers(self, item_id, supplier_ids):
        """
        Replaces item-supplier links with new set of supplier_ids.
        """
        # Remove old links
        delete_query = "DELETE FROM ItemSupplier WHERE ItemID = %s"
        self.execute_command(delete_query, (item_id,))

        # Insert new links
        for supplier_id in supplier_ids:
            insert_query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
            self.execute_command(insert_query, (item_id, supplier_id))

    # 2) Dropdown / Category mgmt
    def get_dropdown_values(self, section):
        """
        Returns list of dropdown values for a given section in 'Dropdowns' table.
        """
        query = "SELECT value FROM Dropdowns WHERE section = %s"
        df = self.fetch_data(query, (section,))
        if not df.empty:
            df.columns = df.columns.str.lower()
            return df["value"].tolist()
        return []

    def add_dropdown_value(self, section, value):
        """
        Adds a new value to 'Dropdowns' for the given section. Avoid duplication with ON CONFLICT DO NOTHING.
        """
        query = """
        INSERT INTO Dropdowns (section, value)
        VALUES (%s, %s)
        ON CONFLICT (section, value) DO NOTHING
        """
        self.execute_command(query, (section, value))

    def delete_dropdown_value(self, section, value):
        """
        Deletes a value from 'Dropdowns' given a section and value.
        """
        query = "DELETE FROM Dropdowns WHERE section = %s AND value = %s"
        self.execute_command(query, (section, value))
