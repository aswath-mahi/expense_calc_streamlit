import pandas as pd
from db_operator import fetch_users, hard_delete_user, insert_user, soft_delete_user, update_user_password
import streamlit as st
from werkzeug.security import generate_password_hash
from utils import add_category, fetch_expenses
from utils import add_category, add_expense, add_subcategory, get_categories, get_subcategories
import altair as alt

colors = [
    "#aa423a",
    "#f6b404",
    "#327a88",
    "#303e55",
    "#c7ab84",
    "#b1dbaa",
    "#feeea5",
    "#3e9a14",
    "#6e4e92",
    "#c98149",
    "#d1b844",
    "#8db6d8",
]
def expense_views():
    st.title("Expense Tracker App")
    categories = get_categories()
    category_options = {name: id for id, name in categories}
    selected_category = st.selectbox("Select Category for Expense", list(category_options.keys()))
    session_usr = st.session_state.username
    st.caption("Username")
    usr_name = st.code(session_usr,language='markdown')
    subcategory_options = {}
    if selected_category:
        subcategories = get_subcategories(category_options[selected_category])
        subcategory_options = {name: id for id, name in subcategories}
    selected_subcategory = st.selectbox("Select Subcategory", list(subcategory_options.keys()))
    expense_date = st.date_input("Date")
    expense_description = st.text_input("Expense Description")
    expense_amount = st.number_input("Expense Amount", min_value=0.0, format="%.2f")
    if st.button("Add Expense"):
        if selected_category and selected_subcategory and expense_description and expense_amount > 0:
            add_expense(expense_date,category_options[selected_category], subcategory_options[selected_subcategory], expense_description, expense_amount,session_usr)
            st.success("Expense added successfully!")
        else:
            st.error("Please fill in all fields to add an expense.")

    st.write("")
    st.subheader("Expense Records")
    data = fetch_expenses(session_usr)
    df = data.reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    selected_month = st.selectbox("Select Month", options=df['month'].unique())

    # Filter the dataframe based on the selected month
    df_filtered = df[df['month'] == selected_month]
    st.dataframe(df_filtered)
    if not df_filtered.empty:
        category_expenses = df_filtered.groupby('category')['amount'].sum().reset_index()
        
        # Create the Altair donut chart
        chart = alt.Chart(category_expenses).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="amount", type="quantitative"),
            color=alt.Color(field="category", type="nominal",scale=alt.Scale(range=colors)),
            tooltip=["category", "amount"]
        ).properties(
            width=400,
            height=400,
            title='Expenses by Category for ' + str(selected_month)
        )
        
        st.altair_chart(chart, use_container_width=True)

def admin_entry():
    st.title("User Management System")
    
    if st.session_state.is_admin:
        st.write("")  # Adding some space
        
        col1, col2, col3 = st.columns(3, gap="large")  # Adding gap between columns

        with col1:
            st.subheader("New User Register")
            st.write("")  # Adding some space
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            
            sub_col1,sub_col2 = st.columns(2)
            with sub_col1:
                st.write("")  # Adding some space
                is_admin = st.checkbox("Admin")
            with sub_col2:
                st.write("")  # Adding some space
                register_button = st.button("Register User")
            
            if register_button:
                if new_username and new_password:
                    hashed_password = generate_password_hash(new_password)
                    insert_user(new_username, hashed_password, int(is_admin))
                    st.success("User registered successfully!")
                else:
                    st.error("Please fill in all fields.")
        
        with col2: 
            st.subheader("Update User Password")
            st.write("")  # Adding some space
            users = [user[0] for user in fetch_users()]
            selected_user = st.selectbox("Select User", users)
            new_password_for_user = st.text_input("New Password for Selected User", type="password")
            
            st.write("") 
             # Adding some space
            update_password_button = st.button("Update Password")
            
            if update_password_button:
                if selected_user and new_password_for_user:
                    update_user_password(selected_user, new_password_for_user)
                    st.success("Password updated successfully!")
                else:
                    st.error("Please select a user and enter a new password.")
        
        with col3:
            st.subheader("Delete User")
            all_users = [user[0] for user in fetch_users(include_deleted=True)]
            st.write("") 
            st.write("") 
            st.write("")  # Adding some space
            delete_user = st.selectbox("Select User to Delete", all_users)
            delete_type = st.radio("Delete Type", ("Soft Delete", "Hard Delete"))
            
            st.write("")  # Adding some space
            delete_button = st.button("Delete User")
            
            if delete_button:
                if delete_user:
                    if delete_type == "Soft Delete":
                        soft_delete_user(delete_user)
                        st.success(f"User {delete_user} soft deleted successfully!")
                    elif delete_type == "Hard Delete":
                        hard_delete_user(delete_user)
                        st.success(f"User {delete_user} hard deleted successfully!")
                else:
                    st.error("Please select a user to delete.")
        
        st.write("")  # Adding some space
        users_data = fetch_users(include_deleted=True)
        
        # Prepare user data for display
        user_data = [
            {
                "Username": user[0], 
                "Password": user[1] if st.session_state.is_admin else "****", 
                "Admin": "Yes" if user[2] else "No", 
                "Deleted": "Yes" if user[3] else "No"
            } 
            for user in users_data
        ]
        
        # Create DataFrame
        df = pd.DataFrame(user_data)
        
        # Display DataFrame
        st.subheader("Registered Users")
        st.write("")  # Adding some space
        st.dataframe(df)

    st.title("Category Management")
    if st.session_state.is_admin:
        st.header("Add Category")
        category_name = st.text_input("Category Name")
        if st.button("Add Category"):
            add_category(category_name)
            st.success(f"Category '{category_name}' added successfully!")
        st.header("Add Subcategory")
        categories = get_categories()
        category_options = {name: id for id, name in categories}
        selected_category = st.selectbox("Select Category", list(category_options.keys()))
        subcategory_name = st.text_input("Subcategory Name")
        if st.button("Add Subcategory"):
            add_subcategory(subcategory_name, category_options[selected_category])
            st.success(f"Subcategory '{subcategory_name}' added successfully!")