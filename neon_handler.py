import streamlit as st
import psycopg2
import pandas as pd

def get_connection():
    """Establish connection using DSN stored in Streamlit secrets."""
    try:
        conn = psycopg2.connect(st.secrets["neon"]["dsn"])
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def run_query(sql, params=None):
    """For SELECT statements (no auto-commit). Returns fetched rows."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
        conn.close()
        return rows
    return []

def run_command(sql, params=None):
    """For non-returning commands like UPDATE/DELETE. Commits changes automatically."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            conn.commit()
        conn.close()

def run_command_returning(sql, params=None):
    """For INSERT ... RETURNING or similar statements that both write data and return newly generated rows."""
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            conn.commit()
        conn.close()
        return rows
    return []

def fetch_inventory():
    """Fetch inventory data and return as a pandas DataFrame."""
    query = "SELECT * FROM InventoryBatch"
    rows = run_query(query)
    if rows:
        columns = ["BatchID", "ItemID", "Quantity", "ExpirationDate", "StorageLocation", "DateReceived", "LastUpdated"]
        return pd.DataFrame(rows, columns=columns)
    return pd.DataFrame()  # Return empty DataFrame if no data

def add_inventory(item_name_en, item_name_ku, class_cat, department_cat, section_cat, family_cat, sub_family_cat, shelf_life, origin_country, manufacturer, brand, barcode, unit_type, packaging, item_picture):
    """Add new inventory item to the database."""
    query = """
    INSERT INTO Item (ItemNameEnglish, ItemNameKurdish, ClassCat, DepartmentCat, SectionCat, FamilyCat, SubFamilyCat, ShelfLife, OriginCountry, Manufacturer, Brand, Barcode, UnitType, Packaging, ItemPicture, CreatedAt, UpdatedAt)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """
    run_command(query, (item_name_en, item_name_ku, class_cat, department_cat, section_cat, family_cat, sub_family_cat, shelf_life, origin_country, manufacturer, brand, barcode, unit_type, packaging, item_picture))
