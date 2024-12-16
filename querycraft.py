import streamlit as st
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Sequence
from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

# App Title
st.set_page_config(page_title="QueryCraft", layout="centered", initial_sidebar_state="expanded")
st.title("🔍 QueryCraft")
st.subheader("Craft SQL Queries from Natural Language Questions")

# Sidebar for database credentials
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
else:
    st.sidebar.warning("⚠️ Please fill in all the fields to establish the database connection.")

# Main input for the user query
query = st.text_area("Type your question to generate SQL Query and retrieve results:", height=150)

# Submit button
if st.button("Run Query"):
    if not query:
        st.warning("⚠️ Please enter a valid question.")
    elif not (database_name and database_username and database_password and port):
        st.warning("⚠️ Please ensure all database credentials are filled in.")
    else:
        try:
            # Initialize database and LLM
            llm = ChatOpenAI(model="gpt-4o-mini")

            sql_query = ResponseSchema(name="sql_query", description="This is the query for your question")
            response_schemas = [sql_query]

            output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
            format_instructions = output_parser.get_format_instructions()

            system_template = """
            As an SQL expert, your task is to answer user queries by generating MYSQL statements based on a database schema:\n 
            {schema}

            ### Guidelines:
            - Follow the given database schema and question provided meticulously, focusing on each word to derive the appropriate SQL query.
            - Always use table aliases for clarity and to avoid ambiguity in your queries.
            - When calculating ratios, ensure to cast the numerator as a float for accurate results.

            ### Prompt:
            Given the MySQL database schema and user questions, craft SQL queries that precisely address each query by referencing the schema 
            and following the SQL best practices mentioned above. Remember, attention to detail and accuracy are key in translating questions into 
            effective SQL statements.

            {format_instructions}
            """
            prompt_template = ChatPromptTemplate.from_messages(
                [
                    ("system", system_template),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            )

            url = f"mysql+mysqlconnector://{database_username}:{database_password}@{host}:{port}/{database_name}"
            sql = SQLDatabase.from_uri(url)

            class State(TypedDict):
                schema: str
                messages: Annotated[Sequence[BaseMessage], add_messages]
                format_instructions: str

            def get_schema(state: State):
                table_info = sql.get_table_info()
                return {"schema": str(table_info)}

            def call_model(state: State):
                prompt = prompt_template.invoke(state)
                result = llm.invoke(prompt)
                return {"messages": result}

            sql_graph_outline = StateGraph(state_schema=State)

            sql_graph_outline.add_node("model", call_model)
            sql_graph_outline.add_node("getschema", get_schema)

            sql_graph_outline.add_edge(START, "getschema")
            sql_graph_outline.add_edge("getschema", "model")
            sql_graph_outline.add_edge("model", END)

            memory = MemorySaver()
            sql_graph = sql_graph_outline.compile(checkpointer=memory)

            config = {"configurable": {"thread_id": "user1"}}
            result = sql_graph.invoke(
                {"messages": [HumanMessage(query)], "format_instructions": format_instructions}, config
            )
            query_to_execute = output_parser.parse(result["messages"][-1].content)
            output = sql.run(query_to_execute["sql_query"])

            data = {
                "query": query_to_execute["sql_query"],
                "result": output,
            }

            # Display the output
            st.success("✅ Query executed successfully!")
            st.markdown("### Generated SQL Query:")
            st.code(data["query"], language="sql")

            st.markdown("### Query Result:")
            st.code(data["result"])
            st.image(Image(
                            sql_graph.get_graph().draw_mermaid_png(
                                draw_method=MermaidDrawMethod.API,
                            )
                        ).data,caption="Mermaid Diagram", width=300)
        
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

