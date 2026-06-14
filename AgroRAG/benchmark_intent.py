import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

df = pd.read_csv("rag_dataset_cleaned.csv")

df["question"] = df["question"].astype(str)
df["answer"] = df["answer"].astype(str)
df["source_file"] = df["source_file"].astype(str)
df["category"] = df["category"].astype(str).str.strip()

# Combine question, answer, and source for better features
df["combined_text"] = (
    df["question"] + " " + 
    df["answer"].fillna("") + " " +
    df["source_file"].str.replace(".jsonl", "")
)

X = df["combined_text"]
y = df["category"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced"))
])

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("Intent Classification Benchmark")
print("Accuracy:", accuracy_score(y_test, predictions))

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

results = pd.DataFrame({
    "question": X_test,
    "true_category": y_test,
    "predicted_category": predictions
})

results.to_csv("intent_benchmark_results.csv", index=False)
print("\nSaved: intent_benchmark_results.csv")