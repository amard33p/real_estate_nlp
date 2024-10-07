import os
import json
from typing import Dict, Any

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase


load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def extract_location_from_query(user_query: str) -> Dict[str, Any]:
    _EXTRACTION_TEMPLATE = """Given an input question about real estate projects, extract the location information (if any) and the main query.
    Only consider locations within Bangalore, Karnataka, India.
    If a location outside Bangalore is mentioned, set the location to Bangalore.
    If the query does not contain any location information, set the location value to null.

    You must return the result as a JSON object with 'location' and 'query' keys.

    Input: {input}

    Output format:
    {{
        "location": "extracted Bangalore location or null",
        "query": "main query without location information"
    }}

    Examples:
    1. Input: "All projects in Whitefield"
       Output: {{"location": "Whitefield", "query": "All projects"}}
    
    2. Input: "Projects launched in 2022 near Electronic City"
       Output: {{"location": "Electronic City", "query": "Projects launched in 2022"}}
    
    3. Input: "projects launched by prestige after 2023 around varthur"
       Output: {{"location": "Varthur", "query": "Projects launched by prestige after 2023"}}
    
    4. Input: "launched projects in 2022"
       Output: {{"location": null, "query": "launched projects in 2022"}}
    
    5. Input: "projects with bwssb water source in Mumbai"
       Output: {{"location": "Bangalore", "query": "projects with bwssb water source"}}

    6. Input: "projects by prestige"
       Output: {{"location": null, "query": "projects by prestige"}}
    """

    EXTRACTION_PROMPT = PromptTemplate(
        input_variables=["input"], template=_EXTRACTION_TEMPLATE
    )

    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    json_parser = JsonOutputParser()
    
    extraction_chain = EXTRACTION_PROMPT | llm | json_parser
    
    return extraction_chain.invoke({"input": user_query})


def transform_query(user_query: str, db: SQLDatabase) -> str:
    _SQL_TEMPLATE = """Given an input question, return the syntactically correct {dialect} query to run for that question.
    - Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist.
    - Use 'LIKE' instead of '=' for matching the following columns after converting them to uppercase: 'promoter_name', 'district', 'source_of_water', 'approving_authority'.
    - Always include the following filters: land_under_litigation = 'NO', rera_project_approval_status = 'APPROVED', 'project_name' is not NULL, 'latitude' is not NULL, 'longitude' is not NULL.
    - Only include these columns in the SELECT statement: 'project_id' as 'id', 'project_name' as 'name', 'latitude', 'longitude'.
    - Do not include any geographical filtering in the SQL query.
    - For date comparisons, use the SQLite date functions. For example, to get the year from a date column, use: CAST(substr(date_column, 1, 4) AS INTEGER)
    - To compare dates, use the comparison operators directly on the date strings (e.g., plan_approval_date > '2022-01-01')
    - Only return the SQL query itself, without using any delimiters or comments.

    Only use the following tables:
    {table_info}

    Question: {input}"""

    SQL_PROMPT = PromptTemplate(
        input_variables=["input", "table_info", "dialect"], template=_SQL_TEMPLATE
    )

    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    
    sql_chain = SQL_PROMPT | llm
    
    response = sql_chain.invoke(
        {"input": user_query, "table_info": db.get_table_info(), "dialect": db.dialect}
    )
    return response.content
