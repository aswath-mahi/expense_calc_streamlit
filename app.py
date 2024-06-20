import streamlit as st
from db_operator import get_user, init_db
from views import admin_entry, expense_views
from werkzeug.security import check_password_hash


def main():
    init_db()
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.session_state.username = None

    if not st.session_state.authenticated:
        st.title("_aswath_mahi_ :red[HUB] :v:")
        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            user = get_user(username)
            if user and check_password_hash(user[2], password):
                st.session_state.authenticated = True
                st.session_state.is_admin = bool(user[3])
                st.session_state.username = username
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")
    else:
        st.sidebar.title("_aswath_mahi_ :red[HUB]")

        selected_tab = st.sidebar.selectbox("Menu", ["Expense Tracker","Admin Entry"])
        
        if selected_tab == "Expense Tracker":
            expense_views()
        elif selected_tab == "Admin Entry":
            admin_entry()
        
        logout_button = st.sidebar.button("Logout")   
        st.sidebar.caption(f"Logged in as :red[{st.session_state.username}]")
        if logout_button:
            st.session_state.authenticated = False
            st.session_state.is_admin = False
            st.session_state.username = None
            st.rerun()
    

if __name__ == "__main__":
    main()