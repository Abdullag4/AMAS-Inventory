import streamlit as st
from db_handler import DatabaseManager

class ItemHandler(DatabaseManager):
    """Handles all item-related database interactions separately."""

    # Item methods
    def get_items(self):
        query = """
        SELECT ItemID, ItemNameEnglish, ItemNameKurdish, ClassCat, DepartmentCat, SectionCat,
               FamilyCat, SubFamilyCat, ShelfLife, Threshold, AverageRequired, OriginCountry,
               Manufacturer, Brand, Barcode, UnitType, Packaging, ItemPicture, CreatedAt, UpdatedAt
        FROM item
        """
        return self.fetch_data(query)

    def get_suppliers(self):
        query = "SELECT SupplierID, SupplierName FROM Supplier"
        return self.fetch_data(query)

    def get_item_suppliers(self, item_id):
        query = """
        SELECT s.SupplierName FROM ItemSupplier isup
        JOIN Supplier s ON isup.SupplierID = s.SupplierID
        WHERE isup.ItemID = %s
        """
        df = self.fetch_data(query, (item_id,))
        return df["suppliername"].tolist() if not df.empty else []

    def add_item(self, item_data, supplier_ids):
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
        if not supplier_ids:
            return
        values = ", ".join(["(%s, %s)"] * len(supplier_ids))
        params = []
        for supplier_id in supplier_ids:
            params.extend([item_id, supplier_id])
        query = f"""
        INSERT INTO itemsupplier (itemid, supplierid) 
        VALUES {values}
        ON CONFLICT DO NOTHING
        """
        self.execute_command(query, params)

    def update_item(self, item_id, updated_data):
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
        delete_query = "DELETE FROM ItemSupplier WHERE ItemID = %s"
        self.execute_command(delete_query, (item_id,))
        for supplier_id in supplier_ids:
            insert_query = "INSERT INTO ItemSupplier (ItemID, SupplierID) VALUES (%s, %s)"
            self.execute_command(insert_query, (item_id, supplier_id))

    # Dropdown methods explicitly added here:
    def get_dropdown_values(self, section):
        query = "SELECT value FROM Dropdowns WHERE section = %s"
        df = self.fetch_data(query, (section,))
        return df["value"].tolist() if not df.empty else []

    def add_dropdown_value(self, section, value):
        query = """
        INSERT INTO Dropdowns (section, value)
        VALUES (%s, %s)
        ON CONFLICT (section, value) DO NOTHING
        """
        self.execute_command(query, (section, value))

    def delete_dropdown_value(self, section, value):
        query = "DELETE FROM Dropdowns WHERE section = %s AND value = %s"
        self.execute_command(query, (section, value))
