import pandas as pd
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

df = pd.read_csv("rag_dataset_full_430.csv")

documents = []

for _, row in df.iterrows():
    text = f"""
Category: {row['category']}

Question:
{row['question']}

Answer:
{row['answer']}
"""

    documents.append(
        Document(
            page_content=text,
            metadata={
                "category": row["category"],
                "source_file": row["source_file"]
            }
        )
    )

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base"
)

vectordb = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./agri_db"
)

print("Vector DB created successfully!")
print("Documents:", len(documents))