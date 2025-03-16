import streamlit as st

def authenticate_user():
    """Handles user authentication via Google login."""
    if not st.experimental_user.is_logged_in:
        st.title("🔐 Login Required")
        st.warning("Please log in with your Google account to access the app.")

        # ✅ Login button
        st.button("Log in with Google", on_click=st.login, args=["google"])
        st.stop()  # Stops execution until login is completed

    # ✅ If user is logged in, display user details
    user_info = st.experimental_user
    st.sidebar.write(f"👤 Logged in as: **{user_info.name}** ({user_info.email})")
    
    return user_info  # Returns user info for further use

def logout():
    """Logs out the current user."""
    st.logout()
    st.success("✅ Logged out successfully!")
    st.experimental_rerun()
