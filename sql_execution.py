from typing import Annotated, Sequence, TypedDict
import streamlit as st
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import  MemorySaver
from langgraph.graph import START, END
from langgraph.graph.message import add_messages
from prompt_setup import get_prompt_template
from IPython.display import Image

def run_query(query, connection_string):
    if not query:
        st.warning("⚠️ Please enter a valid question.")
    elif not connection_string:
        st.warning("⚠️ Please ensure all database credentials are filled in.")
    else:
        try:
            llm = ChatOpenAI(model="gpt-4o-mini")
            prompt_template, output_parser = get_prompt_template()

            url = f"mysql+mysqlconnector://{connection_string}"
            sql = SQLDatabase.from_uri(url)

            class State(TypedDict):
                schema: str
                messages: Annotated[Sequence[BaseMessage], add_messages]
                format_instructions: str

            def get_schema(state):
                table_info = sql.get_table_info()
                print(table_info)
                return {"schema": str(table_info)}

            def call_model(state):
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
                {"messages": [HumanMessage(query)], "format_instructions": output_parser.get_format_instructions()}, 
                config
            )
            query_to_execute = output_parser.parse(result["messages"][-1].content)
            output = sql.run(query_to_execute["sql_query"])

            st.success("✅ Query executed successfully!")
            st.markdown("### Generated SQL Query:")
            st.code(query_to_execute["sql_query"], language="sql")

            st.markdown("### Query Result:")
            st.code(output)
            st.image(Image(
                sql_graph.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API,
                )
            ).data, caption="Mermaid Diagram", width=300)
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
