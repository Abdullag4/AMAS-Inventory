import streamlit as st
from db_handler import DatabaseManager

class ItemHandler:
    """Item-specific database interactions."""

    def __init__(self):
        self.db = DatabaseManager()

    def get_items(self):
        query = """
        SELECT itemid, itemnameenglish, classcat, departmentcat, sectioncat, 
               familycat, subfamilycat, shelflife, origincountry, manufacturer, 
               brand, barcode, unittype, packaging, threshold, averagerequired, 
               itempicture, createdat, updatedat 
        FROM item
        """
        return self.db.fetch_data(query)

    def get_suppliers(self):
        query = "SELECT supplierid, suppliername FROM supplier"
        return self.db.fetch_data(query)

    def get_item_suppliers(self, item_id):
        query = """
        SELECT s.suppliername 
        FROM itemsupplier isup
        JOIN supplier s ON isup.supplierid = s.supplierid
        WHERE isup.itemid = %s
        """
        df = self.db.fetch_data(query, (item_id,))
        return df["suppliername"].tolist() if not df.empty else []

    def add_item(self, item_data, supplier_ids):
        columns = ", ".join(item_data.keys())
        placeholders = ", ".join(["%s"] * len(item_data))

        query = f"""
        INSERT INTO item ({columns}, createdat, updatedat)
        VALUES ({placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING itemid
        """

        item_id = self.db.execute_command_returning(query, list(item_data.values()))

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

        self.db.execute_command(query, params)

    def update_item(self, item_id, updated_data):
        if not updated_data:
            st.warning("⚠️ No changes detected.")
            return

        set_clause = ", ".join(f"{col} = %s" for col in updated_data.keys())
        params = list(updated_data.values()) + [item_id]

        query = f"""
        UPDATE item
        SET {set_clause}, updatedat = CURRENT_TIMESTAMP
        WHERE itemid = %s
        """

        self.db.execute_command(query, params)
        st.success("✅ Item updated successfully!")

    def update_item_suppliers(self, item_id, supplier_ids):
        delete_query = "DELETE FROM itemsupplier WHERE itemid = %s"
        self.db.execute_command(delete_query, (item_id,))

        if supplier_ids:
            self.link_item_suppliers(item_id, supplier_ids)

    def item_exists(self, item_name_english):
        query = "SELECT 1 FROM item WHERE itemnameenglish = %s LIMIT 1"
        df = self.db.fetch_data(query, (item_name_english,))
        return not df.empty
