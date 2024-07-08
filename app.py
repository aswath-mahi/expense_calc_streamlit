import streamlit as st
import base64
from db_operator import db_manager
from views import admin_entry, annual_summary, expense_views
from werkzeug.security import check_password_hash







def main():
    
    st.set_page_config(layout="wide")

    
    
    # Initialize the database and create default collections and admin user
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.session_state.username = None

    if not st.session_state.authenticated:
        st.title("_Fin_ :red[HUB] :v:")
        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            user = db_manager.get_user(username=username)
            print(user)
            if user and check_password_hash(user[2], password):
                st.session_state.authenticated = True
                st.session_state.is_admin = bool(user[3])
                st.session_state.username = username
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")
    else:
        st.sidebar.title("_Fin_ :red[HUB]")
        
        selected_tab = st.sidebar.selectbox("Menu", ["Expense Tracker","Admin Entry","Annual Summary"])
        
        if selected_tab == "Expense Tracker":
            expense_views()
        elif selected_tab == "Admin Entry":
            admin_entry()
        elif selected_tab == 'Annual Summary':
            annual_summary()
        
        logout_button = st.sidebar.button("Logout")   
        st.sidebar.caption(f"Logged in as :red[{st.session_state.username}]")
        if logout_button:
            st.session_state.authenticated = False
            st.session_state.is_admin = False
            st.session_state.username = None
            st.rerun()
    

if __name__ == "__main__":
    db_manager.init_db()
    main()