
import pandas as pd
from db_operator import db_manager
import streamlit as st
from werkzeug.security import generate_password_hash
import altair as alt
from utils import utils_
from configs import *

def expense_views():
    st.title("Expense Tracker App")
    data_col1, data_col2, data_col3 = st.columns(3)
    categories = utils_.get_categories()
    category_options = {name: id for id, name in categories}
    selected_category = data_col1.selectbox("Select Category for Expense", list(category_options.keys()))
    session_usr = st.session_state.get('username', 'guest')
    
    subcategory_options = {}
    if selected_category:
        subcategories = utils_.get_subcategories(category_options[selected_category])
        subcategory_options = {name: id for id, name in subcategories}
    selected_subcategory = data_col2.selectbox("Select Subcategory", list(subcategory_options.keys()))
    expense_date = data_col3.date_input("Date", format="YYYY-MM-DD")

    expense_description = data_col1.text_input("Expense Description")
    expense_amount = data_col2.number_input("Expense Amount", min_value=0.0, format="%.2f")
    data_col3.text("")
    data_col3.text("")
    if data_col3.button("Add Expense", use_container_width=True):
        if selected_category and selected_subcategory and expense_description and expense_amount > 0:
            utils_.add_expense(expense_date, category_options[selected_category], subcategory_options[selected_subcategory], expense_description, expense_amount, session_usr)
            st.success("Expense added successfully!")
        else:
            st.error("Please fill in all fields to add an expense.")

    st.write("")
    st.subheader("Expense Records")
    rec_col1, rec_col2 = st.columns([3, 2])
    data = utils_.fetch_expenses()
    df = data.reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    selected_month = rec_col2.selectbox("Select Month", options=df['month'].unique())

    # Filter the dataframe based on the selected month
    df_filtered = df[df['month'] == selected_month]
    df_show = df_filtered.copy()
    df_show['date'] = df_filtered['date'].dt.strftime('%Y-%m-%d')
    rec_col1.dataframe(df_show.drop(['id'], axis=1), use_container_width=True)
    
    if not df_filtered.empty:
        category_expenses = df_filtered.groupby('category')['amount'].sum().reset_index()
        
        # Create the Altair donut chart
        chart = alt.Chart(category_expenses).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="amount", type="quantitative"),
            color=alt.Color(field="category", type="nominal",legend=alt.Legend(orient='bottom'),scale=alt.Scale(range=colors)),
            tooltip=["category", "amount"]
        ).properties(
            width=500,
            height=500,
            title='Expenses by Category for ' + str(selected_month)
        )
        
        rec_col2.altair_chart(chart, use_container_width=True)

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
                    db_manager.insert_user(new_username, hashed_password, int(is_admin))
                    st.success("User registered successfully!")
                else:
                    st.error("Please fill in all fields.")
        
        with col2: 
            st.subheader("Update User Password")
            st.write("")  # Adding some space
            users = [user[0] for user in db_manager.fetch_users()]
            selected_user = st.selectbox("Select User", users)
            new_password_for_user = st.text_input("New Password for Selected User", type="password")
            
            st.write("") 
             # Adding some space
            update_password_button = st.button("Update Password")
            
            if update_password_button:
                if selected_user and new_password_for_user:
                    db_manager.update_user_password(selected_user, new_password_for_user)
                    st.success("Password updated successfully!")
                else:
                    st.error("Please select a user and enter a new password.")
        
        with col3:
            st.subheader("Delete User")
            all_users = [user[0] for user in db_manager.fetch_users(include_deleted=True)]
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
                        db_manager.soft_delete_user(delete_user)
                        st.success(f"User {delete_user} soft deleted successfully!")
                    elif delete_type == "Hard Delete":
                        db_manager.hard_delete_user(delete_user)
                        st.success(f"User {delete_user} hard deleted successfully!")
                else:
                    st.error("Please select a user to delete.")
        
        st.write("")  # Adding some space
        users_data = db_manager.fetch_users(include_deleted=True)
        
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
            utils_.add_category(category_name)
            st.success(f"Category '{category_name}' added successfully!")
        st.header("Add Subcategory")
        categories = utils_.get_categories()
        category_options = {name: id for id, name in categories}
        selected_category = st.selectbox("Select Category", list(category_options.keys()))
        subcategory_name = st.text_input("Subcategory Name")
        if st.button("Add Subcategory"):
            utils_.add_subcategory(subcategory_name, category_options[selected_category])
            st.success(f"Subcategory '{subcategory_name}' added successfully!")
            
def annual_summary():
    
    st.header("Annual Summary")
    st.sidebar.subheader("Filters")
    
    # Sidebar date inputs
    from_date = st.sidebar.date_input("From", value=None)
    end_date = st.sidebar.date_input("End", value=None)
    
    # Convert date inputs to pandas Timestamp
    from_date, end_date = pd.Timestamp(from_date), pd.Timestamp(end_date)
    
    # Fetch expense data
    expense_data = utils_.fetch_expenses()
    # df_unfiltered = expense_data.copy()
    expense_data['date'] = pd.to_datetime(expense_data['date'])
    
    # Apply date filter if dates are selected
    if not pd.isna(from_date) and not pd.isna(end_date):
        expense_data = expense_data[(expense_data['date'] >= from_date) & (expense_data['date'] <= end_date)]
    
    # Get unique categories and usernames for multi-select filters
    categories = expense_data['category'].unique()
    usernames = expense_data['usr_name'].unique()
    
    # Create multi-select filters in the sidebar
    selected_categories = st.sidebar.multiselect("Category", options=categories, default=categories.tolist())
    selected_usernames = st.sidebar.multiselect("Username", options=usernames, default=usernames.tolist())
    
    # Apply category and username filters independently
    if selected_categories:
        expense_data = expense_data[expense_data['category'].isin(selected_categories)]
    if selected_usernames:
        expense_data = expense_data[expense_data['usr_name'].isin(selected_usernames)]
    
    # Extract month from the 'date' column and sort by month order
    expense_data['Month'] = expense_data['date'].dt.month_name()
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Group data by Month and Category to get the total amount
    monthly_summary = expense_data.groupby(['Month', 'category'], as_index=False)['amount'].sum()
    monthly_summary['Month'] = pd.Categorical(monthly_summary['Month'], categories=month_order, ordered=True)
    monthly_summary = monthly_summary.sort_values('Month')
    
    # Display the data in a Streamlit dataframe with formatted date
    expense_data['date'] = expense_data['date'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(expense_data.drop(columns=['id']),use_container_width=True)
    graph_col1,graph_col2 = st.columns(2)
    category_expenses = expense_data.groupby('category')['amount'].sum().reset_index()
    # Create a bar chart with rounded edges for each month with multiple categories
    # colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    bar_chart = alt.Chart(monthly_summary).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
        x=alt.X('Month:N', sort=month_order),
        y='amount:Q',
        color=alt.Color(field="category", type="nominal", scale=alt.Scale(range=colors)),
        tooltip=['Month', 'category', 'amount']
    ).properties(
        width=800,
        height=400,
        title='Monthly Expense Summary'
    ).configure_axis(
        labelAngle=0
    )
    
    # Display the chart in Streamlit
    graph_col1.altair_chart(bar_chart, use_container_width=True)
    chart = alt.Chart(category_expenses).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="amount", type="quantitative"),
            color=alt.Color(field="category", type="nominal", scale=alt.Scale(range=colors)),
            tooltip=["category", "amount"]
        ).properties(
            width=400,
            height=400,
            title='Annual Expenses by Category'
        )
        
    graph_col2.altair_chart(chart, use_container_width=True)
    
    if not expense_data.empty:
        
        st.subheader("Total Summary")
        total_expense = category_expenses['amount'].sum()
        
        # Create 4 columns
        col1, col2, col3 = st.columns(3)
        
        # Display the overall total expense in the first column
        
        
        # Display each category's total expense in the remaining columns
        for idx, row in category_expenses.iterrows():
            if idx % 4 == 0:
                col1.metric(row['category'], f"{row['amount']:.2f}")
            elif idx % 4 == 1:
                col1.metric(row['category'], f"{row['amount']:.2f}")
            elif idx % 4 == 2:
                col2.metric(row['category'], f"{row['amount']:.2f}")
            else:
                col2.metric(row['category'], f"{row['amount']:.2f}")
        
        col3.metric("Overall Total Expense:", f"{total_expense:.2f}")
        

        