import streamlit as st
from database_config import get_connection_string
from sql_execution import run_query

# App Title
st.set_page_config(page_title="QueryCraft", layout="centered", initial_sidebar_state="expanded")
st.title("🔍 QueryCraft")
st.subheader("Craft SQL Queries from Natural Language Questions")

# Sidebar for database credentials
connection_string = get_connection_string()

# Main input for the user query
query = st.text_area("Type your question to generate SQL Query and retrieve results:", height=150)

# Submit button
if st.button("Run Query"):
    run_query(query, connection_string)
