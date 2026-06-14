from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectordb = Chroma(
    persist_directory="./agri_db",
    embedding_function=embeddings
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

query = input("Ask your agricultural question: ")

docs = vectordb.similarity_search(query, k=5)

context = "\n\n".join([doc.page_content for doc in docs])

prompt = f"""
You are an agricultural customer support assistant.

Answer the user's question using ONLY the provided context.

If the context is not enough, say:
"I don't have enough information from the available data."

For safety-sensitive questions, be cautious and recommend checking the product label or consulting an agricultural expert.

Context:
{context}

User question:
{query}

Answer:
"""

response = llm.invoke(prompt)

print("\n===== Retrieved Context =====")
for i, doc in enumerate(docs, 1):
    print(f"\n--- Document {i} ---")
    print(doc.page_content)

print("\n===== Final Answer =====")
print(response.content)