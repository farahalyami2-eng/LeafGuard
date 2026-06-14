import pandas as pd

# Original dataset
df = pd.read_csv("rag_dataset.csv")

# Your corrected file
corrections = pd.read_excel("wrong_predictions_corrected.xlsx")

# clean spaces
df["question"] = df["question"].astype(str).str.strip()
df["category"] = df["category"].astype(str).str.strip()

corrections["question"] = corrections["question"].astype(str).str.strip()
corrections["predicted_category"] = corrections["predicted_category"].astype(str).str.strip()

# remove empty rows
corrections = corrections.dropna(subset=["question", "predicted_category"])

# create mapping: question -> corrected label
correction_map = dict(
    zip(corrections["question"], corrections["predicted_category"])
)

# backup old category
df["old_category"] = df["category"]

# apply corrections
df["category"] = df.apply(
    lambda row: correction_map.get(row["question"], row["category"]),
    axis=1
)

changed = df[df["old_category"] != df["category"]]

print("Changed rows:", len(changed))
print(changed[["question", "old_category", "category"]])

# save new clean dataset
df.drop(columns=["old_category"]).to_csv("rag_dataset_cleaned.csv", index=False)

print("Saved: rag_dataset_cleaned.csv")
df = pd.read_csv("rag_dataset_cleaned.csv")
print(len(df))