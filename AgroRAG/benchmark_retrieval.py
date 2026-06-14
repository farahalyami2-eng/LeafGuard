import pandas as pd
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

test_df = pd.read_csv("rag_dataset_cleaned.csv")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectordb = Chroma(
    persist_directory="./agri_db",
    embedding_function=embeddings
)

results = []

for _, row in test_df.iterrows():
    question = row["question"]
    expected_category = row["category"]

    docs = vectordb.similarity_search(question, k=5)

    retrieved_categories = [
        doc.metadata.get("category") for doc in docs
    ]

    hit_at_1 = retrieved_categories[0] == expected_category if retrieved_categories else False
    hit_at_5 = expected_category in retrieved_categories

    results.append({
        "question": question,
        "expected_category": expected_category,
        "top1_category": retrieved_categories[0] if retrieved_categories else None,
        "retrieved_categories": retrieved_categories,
        "hit_at_1": hit_at_1,
        "hit_at_5": hit_at_5
    })

results_df = pd.DataFrame(results)

print("Retrieval Benchmark")
print("Hit@1:", results_df["hit_at_1"].mean())
print("Hit@5:", results_df["hit_at_5"].mean())

results_df.to_csv("retrieval_benchmark_results.csv", index=False)
print("\nSaved: retrieval_benchmark_results.csv")