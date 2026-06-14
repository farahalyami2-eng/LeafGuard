import pandas as pd
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Load dataset
df = pd.read_csv("rag_dataset.csv")

# Use a small test set
test_df = df.sample(n=30, random_state=42)

# Load vector database
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectordb = Chroma(
    persist_directory="./agri_db",
    embedding_function=embeddings
)

recall_at_1 = 0
recall_at_3 = 0
recall_at_5 = 0

results = []

for _, row in test_df.iterrows():
    question = row["question"]
    true_category = row["category"]

    docs = vectordb.similarity_search(
        question,
        k=5
    )

    retrieved_categories = [
        doc.metadata.get("category") for doc in docs
    ]

    hit_at_1 = true_category in retrieved_categories[:1]
    hit_at_3 = true_category in retrieved_categories[:3]
    hit_at_5 = true_category in retrieved_categories[:5]

    recall_at_1 += int(hit_at_1)
    recall_at_3 += int(hit_at_3)
    recall_at_5 += int(hit_at_5)

    results.append({
        "question": question,
        "true_category": true_category,
        "retrieved_categories": retrieved_categories,
        "hit@1": hit_at_1,
        "hit@3": hit_at_3,
        "hit@5": hit_at_5
    })

total = len(test_df)

print("===== Retrieval Evaluation =====")
print("Total test questions:", total)
print("Recall@1:", recall_at_1 / total)
print("Recall@3:", recall_at_3 / total)
print("Recall@5:", recall_at_5 / total)

results_df = pd.DataFrame(results)
test_df = df.sample(n=30, random_state=42)
test_df.to_csv("test_data.csv", index=False)
print("\nSaved results to retrieval_evaluation_results.csv")