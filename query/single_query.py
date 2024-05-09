import os
import os
import pandas as pd
from pinecone import Pinecone
from openpyxl import Workbook, load_workbook
from openai import OpenAI
from utils.data_formatting import create_filtered_meta_excel
from utils.agents import AnswerCall


from dotenv import load_dotenv
# Get the current working directory
current_dir = os.getcwd()
# Construct the path to the .env file relative to the current directory
env_path = os.path.join(current_dir, '..', '.env')
# Load environment variables from .env file
load_dotenv(env_path)

SECRET_KEY = os.environ.get('SECRET_KEY')
EMBED_API_KEY = os.environ.get('EMBED_API_KEY')
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
EMBED_MODEL = os.environ.get('EMBED_MODEL')
BASE_MODEL = os.environ.get('BASE_MODEL')
INDEX_NAME = os.environ.get('INDEX_NAME')

pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX = pc.Index(INDEX_NAME)
INDEX_DIMENSION = 1536


def get_similarities(query, namespace, filters, top_k = 100):
    temp_client = OpenAI(
    api_key=os.environ.get('EMBED_API_KEY'),
    )

    description_response = temp_client.embeddings.create(
            input=query,
            model=EMBED_MODEL,
        )
    query_embed_vec = description_response.data[0].embedding
    similar_vectors = []

    for filter in filters:
        result = INDEX.query(
            namespace=namespace,
            vector=query_embed_vec,
            filter={"type": filter},
            top_k=top_k,
            include_metadata=True
        )
        similar_vectors.extend(result['matches'])

    return similar_vectors


def answer_single_query(query, namespace, table_path, filtered_table_name):
        similarities = get_similarities(query, namespace, ["value", "term"])
        
        # print(f'{len(similarities)} similar cells found')
        # create filtered table
        # cell_set = create_similar_cell_set(similarities, threshold=0.2)
        filtered_path = f"{filtered_table_name}.xlsx"
        print(f'filtered excel for {table_path} is being created at {filtered_path}')

        create_filtered_meta_excel(table_path, filtered_path, similarities)
        # create_filtered_excel(table_path, filtered_path, cell_set)
        print()
        answer_call = AnswerCall(query)
        answer_call.load_table(filtered_path)
        answer_call.respond()

        query_result = answer_call.highlighted_json
        return query_result
