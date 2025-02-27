import streamlit as st
import psycopg2
import pandas as pd

def get_connection():
    """Establish connection using DSN stored in Streamlit secrets."""
    try:
        dsn = st.secrets["dsn"]
        return psycopg2.connect(dsn)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def fetch_inventory():
    """Retrieve inventory batches from the database."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM InventoryBatch")
            df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
        conn.close()
        return df
    return pd.DataFrame()

def add_inventory(item_name_en, item_name_ku, class_cat, department_cat, section_cat, family_cat, sub_family_cat, shelf_life, origin_country, manufacturer, brand, barcode, unit_type, packaging, item_picture):
    """Add new inventory item to the database."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            query = """
            INSERT INTO Item (ItemNameEnglish, ItemNameKurdish, ClassCat, DepartmentCat, SectionCat, FamilyCat, SubFamilyCat, ShelfLife, OriginCountry, Manufacturer, Brand, Barcode, UnitType, Packaging, ItemPicture, CreatedAt, UpdatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            cursor.execute(query, (item_name_en, item_name_ku, class_cat, department_cat, section_cat, family_cat, sub_family_cat, shelf_life, origin_country, manufacturer, brand, barcode, unit_type, packaging, item_picture))
        conn.commit()
        conn.close()
        st.success("Item added successfully!")
