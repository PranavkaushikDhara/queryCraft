from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def get_prompt_template():
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
    return prompt_template, output_parser
