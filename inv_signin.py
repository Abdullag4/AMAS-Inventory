import streamlit as st
from db_handler import DatabaseManager

# Initialize the DatabaseManager
db = DatabaseManager()

def authenticate():
    """Handles user authentication and retrieves access permissions."""
    if not st.experimental_user.is_logged_in:
        google_icon_url = "https://img.icons8.com/color/48/000000/google-logo.png"
        st.markdown("<h2 style='text-align: center;'>Inventory Management System</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns([1, 3, 1])
        with cols[1]:
            st.image(google_icon_url, width=30)
            st.button("Sign in with Google", on_click=st.login, use_container_width=True)
        st.stop()

    user_email = st.experimental_user.email
    user_name = st.experimental_user.name

    # Save user details clearly in session_state
    st.session_state["user_email"] = user_email
    st.session_state["user_name"] = user_name

    # Check if user exists in the database
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
            "CanAccessHome": True,
            "CanAccessItems": False,
            "CanAccessReceive": False,
            "CanAccessPO": False,
            "CanAccessReports": False
        }
        st.session_state["user_role"] = "User"
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
        st.session_state["user_role"] = user_info["role"]

def logout():
    """Handles user logout."""
    st.logout()
