import streamlit as st
from db_handler import DatabaseManager

db = DatabaseManager()

def authenticate():
    """Handles user authentication and retrieves access permissions."""
    if not st.experimental_user.is_logged_in:
        st.button("🔑 Log in with Google", on_click=st.login)
        st.stop()

    # Get user info
    user_email = st.experimental_user.email
    user_name = st.experimental_user.name

    # Check if user exists
    query = "SELECT * FROM Users WHERE Email = %s"
    user_df = db.fetch_data(query, (user_email,))

    if user_df.empty:
        # New user → Add them with default permissions
        insert_query = """
        INSERT INTO Users (Name, Email, Role)
        VALUES (%s, %s, 'User')
        """
        db.execute_command(insert_query, (user_name, user_email))
        st.session_state["permissions"] = {
            "CanAccessHome": True, "CanAccessItems": False,
            "CanAccessReceive": False, "CanAccessPO": False,
            "CanAccessReports": False
        }
    else:
        # Existing user → Fetch permissions
        user_info = user_df.iloc[0]
        st.session_state["permissions"] = {
            "CanAccessHome": user_info["canaccesshome"],
            "CanAccessItems": user_info["canaccessitems"],
            "CanAccessReceive": user_info["canaccessreceive"],
            "CanAccessPO": user_info["canaccesspo"],
            "CanAccessReports": user_info["canaccessreports"]
        }
