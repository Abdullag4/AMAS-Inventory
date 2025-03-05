import streamlit as st
import psycopg2
import pandas as pd
from db_handler import DatabaseManager

class ItemHandler(DatabaseManager):
    """Handles all item-related database interactions separately."""

    def get_items(self):
        """Retrieve all items for editing."""
        query = """
        SELECT itemid, itemnameenglish, classcat, departmentcat, sectioncat, 
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
            self.link_item_suppliers(item_id[0][0], supplier_ids)
            return item_id[0][0]
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
