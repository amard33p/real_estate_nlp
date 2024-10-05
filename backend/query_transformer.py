import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase


load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def transform_query(user_query: str, db: SQLDatabase) -> str:
    _DEFAULT_TEMPLATE = """Given an input question, return the syntactically correct {dialect} query to run for that question.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist.
    Remember to use 'LIKE' instead of '=' for matching the following columns after converting them to uppercase: 'promoter_name', 'district', 'source_of_water', 'approving_authority'.
    Remember to always include the following filters: land_under_litigation = 'NO', rera_project_approval_status = 'APPROVED', 'project_name' is not NULL, 'latitude' is not NULL, 'longitude' is not NULL.
    Remember to only include these columns in the SELECT statement: 'project_id' as 'id', 'project_name', 'latitude', 'longitude'.
    Remember to only return the SQL query itself, without using delimiters.

    Only use the following tables:
    {table_info}

    Question: {input}"""

    PROMPT = PromptTemplate(
        input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
    )

    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    chain = LLMChain(llm=llm, prompt=PROMPT)
    response = chain.invoke(
        dict(input=user_query, table_info=db.get_table_info(), dialect=db.dialect)
    )
    return response["text"]
