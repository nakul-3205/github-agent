import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def ask_llm(question, code_chunks):
    context = "\n\n".join(
        f"File: {c['file']}\nFunction: {c['function']}\nCode:\n{c['code']}"
        for c in code_chunks
    )

    prompt = f"""You are a code assistant. Use ONLY the code context below to answer the question.

Code context:
{context}

Question: {question}

Answer clearly and concisely, referencing the specific function(s) involved.
"""

    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    dummy_chunk = {
        "file": "sample.py",
        "function": "login",
        "code": '''def login(self, username, password):
    if username == "admin":
        return True
    return False''',
    }

    answer = ask_llm("how does login work", [dummy_chunk])
    print(answer)