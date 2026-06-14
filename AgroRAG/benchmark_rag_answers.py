import pandas as pd
import joblib
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

test_df = pd.read_csv("rag_dataset_cleaned.csv").sample(30, random_state=42)

intent_model = joblib.load("intent_classifier.joblib")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectordb = Chroma(
    persist_directory="./agri_db",
    embedding_function=embeddings
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

judge_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

results = []

for _, row in test_df.iterrows():
    question = row["question"]
    expected_answer = row["answer"]
    expected_category = row["category"]

    predicted_intent = intent_model.predict([question])[0]

    docs = vectordb.similarity_search(
        question,
        k=5,
        filter={"category": predicted_intent}
    )

    context = "\n\n".join([doc.page_content for doc in docs])

    rag_prompt = f"""
You are an agricultural customer support assistant.

Use the retrieved context to answer the question.

Context:
{context}

Question:
{question}

Answer:
"""

    generated_answer = llm.invoke(rag_prompt).content

    judge_prompt = f"""
Evaluate the generated answer compared to the expected answer.

Question:
{question}

Expected Answer:
{expected_answer}

Generated Answer:
{generated_answer}

Give scores from 1 to 5 for:
Correctness
Relevance
Completeness
Groundedness

Return only this format:
Correctness: number
Relevance: number
Completeness: number
Groundedness: number
"""

    evaluation = judge_llm.invoke(judge_prompt).content

    results.append({
        "question": question,
        "expected_category": expected_category,
        "predicted_intent": predicted_intent,
        "expected_answer": expected_answer,
        "generated_answer": generated_answer,
        "evaluation": evaluation
    })

results_df = pd.DataFrame(results)

results_df.to_csv("rag_answer_benchmark_results.csv", index=False)

print("RAG Answer Benchmark completed.")
print("Saved: rag_answer_benchmark_results.csv")