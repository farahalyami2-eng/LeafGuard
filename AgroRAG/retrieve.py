from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectordb = Chroma(
    persist_directory="./agri_db",
    embedding_function=embeddings
)

query = "What fertilizer is good for tomato plants?"


results = vectordb.similarity_search(
    query,
    k=3
)

for i, doc in enumerate(results, 1):
    print(f"\n===== Result {i} =====")
    print(doc.page_content)
    