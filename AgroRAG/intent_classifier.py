import pandas as pd
import joblib
import numpy as np

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

df = pd.read_csv("rag_dataset_full_430.csv")
print(df["category"].value_counts())

# Combine question, answer, and source info for better features
df["combined_text"] = (
    df["question"] + " " + 
    df["answer"].fillna("") + " " +
    df["source_file"].str.replace(".jsonl", "").fillna("")
)

X = df["combined_text"]
y = df["category"]

le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=600,
        min_df=1,
        max_df=0.9,
        sublinear_tf=True,
        lowercase=True,
        stop_words="english"
    )),
    ("classifier", LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
        solver='lbfgs'
    ))
])

# Hyperparameter tuning
param_grid = {
    'tfidf__ngram_range': [(1, 2), (1, 3)],
    'tfidf__max_features': [400, 600, 800],
    'classifier__C': [0.01, 0.1, 1, 10],
}

grid_search = GridSearchCV(model, param_grid, cv=5, n_jobs=-1, scoring='accuracy', verbose=1)
grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best CV Accuracy: {grid_search.best_score_:.4f}")

model = grid_search.best_estimator_
predictions = model.predict(X_test)

errors = pd.DataFrame({
    "question": X_test,
    "true_category": le.inverse_transform(y_test),
    "predicted_category": le.inverse_transform(predictions)
})

errors = errors[errors["true_category"] != errors["predicted_category"]]
errors.to_csv("wrong_predictions.csv", index=False)
print("\nWrong Predictions:")
print(errors.head(20))

print("Accuracy:", accuracy_score(y_test, predictions))

print("\nClassification Report:")
print(classification_report(y_test, predictions, target_names=le.classes_))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))


joblib.dump(model, "intent_classifier.joblib")
print("\nModel saved as intent_classifier.joblib")