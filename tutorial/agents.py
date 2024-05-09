import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
from data_formatting import get_csv_data
# from utils import get_csv_data

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_MODEL = "openai/gpt-4-turbo"


class Message:
    def __init__(self, content):
        self.content = content
    
    def __str__(self):
        return self.content

class SystemMessage(Message):
    def __init__(self, content):
        super().__init__(content)
        self.role = "system"

class UserMessage(Message):
    def __init__(self, content):
        super().__init__(content)
        self.role = "user"


def send_request(messages, MODEL = BASE_MODEL):
    payload = {
        "model": MODEL,
        "messages": [vars(message) for message in messages]
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )

    return response

class Call:
    def __init__(self, query):
        self.query = UserMessage(query)
        self.system_promt = ""
    
    def respond(self):
        response = send_request([SystemMessage(self.system_promt), self.query])
        return response.json()

class FormatQuestionCall(Call):
    def __init__(self, query):
        super().__init__(query)
        self.system_promt = '''User will ask you a question about the data in a cap table.

                            Cap table contains only financial data.

                            Their question might be vague and might have has some tonality.
                            Identify the key values and features the user asks about that might be present in the table.
                            
                            If there are multiple different values, give them in the form 
                            "[Value1, Value2, Value3]", and nothing else.

                            If there is a term with different notations, you may include them
                            with a slash: "Value1.1/Value1.2/Value1.3" instead of "Value1".

                            You should not try to answer the question, but identify the key terms
                            specific to the user's query.

                            If the question is already in financial terms and clear, you may leave it as it is.

                            If the query is vague, you might specify it. For example, "Revenue" to "Total Revenue".
                            Or, "Side Expenses" to "Other Expenses".

                            Try to keep it short, at most 2 words per value. Mostly 1 key word.

                            For instance, the user asks "What are the major categories of our operating expenses?"
                            Your response might be "[Operating Expenses, Categories]"

                            The user asks, "How much stakeholders' equity do we have?"
                            Your response might be "[Stakeholders, Equity]"
                            
                            For example, the user asks "How much money I made in April of 2023?"
                            Your response might be "[Total Revenue, Income/Profit, Apr 2023]"

                            Because the user might be asking about the revenue or the profit (which is the same as income).
                            And the date is important.
                            
                            Do not include anything else. If there is nothing to answer, respond with an empty list "[]"
                            '''
    def respond(self):
        response = super().respond()
        # print(f'{response =}')
        content = response['choices'][0]['message']['content']
        content = content.strip("'[]")
        queries = [query.strip() for query in content.split(',')]
        self.queries = queries
        
        return response
    
class AnswerCall(Call):
    def __init__(self, query):
        super().__init__(query)
        self.table = ""
        self.system_promt = '''
                            You are a data analyst for a financial company.

                            You will be given some financial metric/indicator to look for.

                            You will be given the CSV data for the company's financial data 
                            with most unnecessary cells filtrer (removed).

                            You should highlight the most relevant CSV cells used to answer the query.

                            Assume that the CSV cells are labelled in the format 'A1', 'B2', etc.

                            Do not provide any explanation on how you calculated the data.

                            Your answer should consist only of values from cells. Do not create any metadata.
                            
                            The answer should be specific to the query.
                            If the query asks about total revenue, you should provide the total revenue value from the table.
                            If it asks about other income soures, you should provide the values of other income sources, not the total revenue.

                            For each of the queries, find the value of that metric, assosiated period, the sheet name,
                            and cell number in excel notation, where this `value` is located.

                            The answer should be of the form:

                            ""metric_name": [
                            {
                            "period": "period from the table",
                            "value": value,
                            "sheet": "sheet name",
                            "cell": "cell in excel notation"
                            },
                            {
                            "period": "period from the table",
                            "value": value,
                            "sheet": "sheet name",
                            "cell": "cell in excel notation"
                            },
                            ...
                            ]"

                            Metric name in most cases will be the same as the query.
                            If there is nothing relevant to answer, respond with an empty list:
                            ""metric_name": [
                                ]"

                            For example, if the user asks for "Expense", you should highlight cells with the numeric
                            value of expenses, date for the specific expense, the sheet name and the cell in the excel
                            sheet with those value.
                            '''
    def load_table(self, file_path):
        self.table = "table = " + get_csv_data(file_path)
    
    def respond(self):
        response = send_request([SystemMessage(self.system_promt), 
                                 self.query,
                                 UserMessage(self.table)])
        # print(f'{response.json() =}')
        content = response.json()['choices'][0]['message']['content']
        self.highlighted_json = content
        return response.json()
                    