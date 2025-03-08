import streamlit as st
from db_handler import DatabaseManager

class ItemHandler(DatabaseManager):
    """Handles all item-related database interactions separately."""

    def get_items(self):
        """Retrieve all items for editing."""
        query = """
        SELECT itemid, itemnameenglish, itemnamekurdish, classcat, departmentcat, sectioncat, 
               familycat, subfamilycat, shelflife, origincountry, manufacturer, 
               brand, barcode, unittype, packaging, threshold, averagerequired, 
               itempicture, createdat, updatedat 
        FROM item
        """
        return self.fetch_data(query)

    def update_item(self, item_id, updated_data):
        """Update item details in the database."""
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
        st.success("✅ Item updated successfully!")

    def add_item(self, item_data, supplier_ids):
        """Insert a new item and link it to suppliers."""
        columns = ", ".join(item_data.keys())  
        values_placeholders = ", ".join(["%s"] * len(item_data))

        query = f"""
        INSERT INTO item ({columns}, createdat, updatedat)
        VALUES ({values_placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING itemid
        """

        item_id = self.execute_command_returning(query, list(item_data.values()))

        if item_id:
            self.link_item_suppliers(item_id[0], supplier_ids)
            return item_id[0]
        return None

    def link_item_suppliers(self, item_id, supplier_ids):
        """Link item to multiple suppliers in the ItemSupplier table."""
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

    def get_suppliers(self):
        """Retrieve all suppliers."""
        query = "SELECT supplierid, suppliername FROM supplier"
        return self.fetch_data(query)

    def get_item_suppliers(self, item_id):
        """Retrieve supplier names linked to a specific item."""
        query = """
        SELECT s.suppliername FROM itemsupplier isup
        JOIN supplier s ON isup.supplierid = s.supplierid
        WHERE isup.itemid = %s
        """
        df = self.fetch_data(query, (item_id,))
        return df["suppliername"].tolist() if not df.empty else []

    # ✅ ADDING THIS MISSING METHOD
    def get_dropdown_values(self, section):
        """Retrieve dropdown values for a specific section."""
        query = "SELECT value FROM dropdowns WHERE section = %s"
        df = self.fetch_data(query, (section,))
        return df["value"].tolist() if not df.empty else []

    def add_dropdown_value(self, section, value):
        """Add a new value to dropdown."""
        query = """
        INSERT INTO dropdowns (section, value)
        VALUES (%s, %s)
        ON CONFLICT (section, value) DO NOTHING
        """
        self.execute_command(query, (section, value))

    def delete_dropdown_value(self, section, value):
        """Delete a value from dropdown."""
        query = "DELETE FROM dropdowns WHERE section = %s AND value = %s"
        self.execute_command(query, (section, value))
