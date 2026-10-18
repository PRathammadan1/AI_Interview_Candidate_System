from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="gemma3:1b",
    temperature=0
)

def generate_answer(prompt):
    response = llm.invoke(prompt)

    return response.content