
import os
from openai import OpenAI
from pinecone import Pinecone
import openpyxl
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
INDEX = pc.Index(os.environ.get('INDEX_NAME'))


def get_window_snapshot(r, c, window_width, window_height, namespace, sheet_name):
    print("row", r, "col", c)
    file_path = f'uploads/{namespace}'
    workbook = openpyxl.load_workbook(file_path, data_only=True)

    sheet = workbook[sheet_name]
    window_data = []

    # Iterate over the rows within the window's height
    for row in range(r, r + window_height):
        row_data = []
        for col in range(c, c + window_width):
            cell_value = sheet.cell(row=row, column=col).value
            row_data.append(cell_value)
        window_data.append(row_data)
    print(window_data)

    return window_data


def get_top_k_chunks(query, namespace, index=INDEX):
    temp_client = OpenAI(
        api_key=os.environ.get('EMBED_API_KEY'),
    )

    description_response = temp_client.embeddings.create(
        input=query,
        model="text-embedding-3-small",
    )

    query_embed_vec = description_response.data[0].embedding
    # creating part of the context to LLM formed from our relevant embeds
    chunks_context = ""
    table_snapshot_num = 1

    # getting top 3 of each type (value, term, window)
    for filter_type in ["value", "term", "window"]:
        relevant_embeds = index.query(
            namespace=namespace,
            vector=query_embed_vec,
            filter={"type": filter_type},
            top_k=3,
            include_metadata=True)

        for single_embed in relevant_embeds['matches']:

            data, table_content = single_embed['metadata'], ""
            row, col, sheet = int(data['row']), int(data['col']), data['sheet']
            window_height, window_width = int(
                data['window_height']), int(data['window_width'])
            if filter_type == "window":
                table_content = get_window_snapshot(row, col, window_width,
                                                    window_height, namespace, sheet)
                print(table_content)
            chunks_context += f"\n\nTable snapshot # {table_snapshot_num}."
            chunks_context += f"Location in the original table row:"
            chunks_context += f" {row}, col: {col}."
            chunks_context += f"Content of the table: {table_content}\n\n"

    return chunks_context


def send_message_to_llm(query, namespace):
    # getting relevant embeddings first
    chunks_context = get_top_k_chunks(query, namespace)

    return f"{chunks_context}"
