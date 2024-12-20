
# QueryCraft

**QueryCraft** converts natural language into SQL queries, simplifying database interaction. Built with Streamlit and LangChain, it allows users to configure databases, ask questions, and retrieve results in real-time.

## Features
- Generate SQL queries from natural language.
- Dynamic database configuration.
- Real-time query execution and results display.

## Usage
1. Install the requirements using:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. Enter database credentials (name, username, password, port).
5. Ask a question (e.g., "How many users are there?").
6. View the generated SQL query and its result.

## Example
- **Question**: "How many users joined last month?"
- **Query**:
  ```sql
  SELECT COUNT(*) AS user_count FROM users WHERE created_at >= NOW() - INTERVAL 1 MONTH;
  ```
- **Result**:
  ```json
  {"user_count": 120}
  ```

## Contributions
Feel free to contribute via issues or pull requests.
