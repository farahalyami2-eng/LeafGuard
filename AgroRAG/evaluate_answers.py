import pandas as pd
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

load_dotenv()

df = pd.read_csv("rag_dataset.csv")

# Test set
test_df = df.sample(n=20, random_state=7)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectordb = Chroma(
    persist_directory="./agri_db",
    embedding_function=embeddings
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

results = []

for _, row in test_df.iterrows():
    question = row["question"]
    ground_truth = row["answer"]

    docs = vectordb.similarity_search(question, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])

    answer_prompt = f"""
You are an agricultural customer support assistant.

Use the retrieved context to answer the user's question.
If the context does not contain relevant information, say that information is unavailable.
Do not invent information.

Context:
{context}

Question:
{question}

Answer:
"""

    generated_answer = llm.invoke(answer_prompt).content

    eval_prompt = f"""
You are evaluating a RAG system.

Question:
{question}

Ground truth answer:
{ground_truth}

Generated answer:
{generated_answer}

Retrieved context:
{context}

Score the generated answer from 1 to 5 for:

Faithfulness: Is the answer supported by the retrieved context?
Answer Relevancy: Does the answer answer the question?
Grounded Accuracy: Is the answer close to the ground truth?

Return only this format:
Faithfulness: X
Answer Relevancy: X
Grounded Accuracy: X
Notes: short explanation
"""

    evaluation = llm.invoke(eval_prompt).content

    results.append({
        "question": question,
        "ground_truth": ground_truth,
        "generated_answer": generated_answer,
        "evaluation": evaluation
    })

results_df = pd.DataFrame(results)
results_df.to_csv("answer_evaluation_results.csv", index=False)

print("Answer evaluation saved to answer_evaluation_results.csv")
print(results_df.head())