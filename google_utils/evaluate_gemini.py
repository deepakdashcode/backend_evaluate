import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


def evaluate_quiz(formatted_string: str):
    st = 'I want to evaluate the quiz of my student. It has several questions and each'\
        ' question has some marks which is written in [] after it. In the next line the answer starts and' \
        ' it ends with two newlines before next question. you need to evaluate each question and mark accordingly. also state where they could have improved'\
        'in each question in case they dont get full marks in that question. Comment only if marks are not full also find the total marks in quiz out of maximum marks.Be professional.The quiz starts from next line\n'
    
    st += formatted_string
    response = model.generate_content(st)
    return response.text


# quiz = '''
# Capital of India [2]
# Delhi

# Capital of Odisha [2]
# BBSR

# Capital of Bihar [3]
# Patna
# '''
# print(evaluate_quiz(quiz))