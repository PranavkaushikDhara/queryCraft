import streamlit as st

def get_connection_string():
    st.sidebar.header("Database Configuration")
    database_name = st.sidebar.text_input("Database Name", placeholder="Enter your database name")
    database_username = st.sidebar.text_input("Database Username", placeholder="Enter your database username")
    database_password = st.sidebar.text_input(
        "Database Password", type="password", placeholder="Enter your database password"
    )
    port = st.sidebar.text_input("Port", placeholder="Enter your database port")
    host = "localhost"  # Fixed host value
    st.sidebar.text(f"Host: {host}")

    if database_name and database_username and database_password and port:
        connection_string = f"{database_username}:{database_password}@{host}:{port}/{database_name}"
        st.sidebar.markdown("**Connection String:**")
        st.sidebar.code(connection_string, language="text")
        return connection_string
    else:
        st.sidebar.warning("⚠️ Please fill in all the fields to establish the database connection.")
        return None
