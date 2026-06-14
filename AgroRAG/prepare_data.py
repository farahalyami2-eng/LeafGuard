import json
import glob
import pandas as pd

rows = []

for file in glob.glob("*.jsonl"):
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            messages = item.get("messages", [])

            user_msg = None
            assistant_msg = None

            for msg in messages:
                if msg["role"] == "user":
                    user_msg = msg["content"]
                elif msg["role"] == "assistant":
                    assistant_msg = msg["content"]

            if user_msg and assistant_msg:
                rows.append({
                    "category": file.split("_real")[0],
                    "question": user_msg,
                    "answer": assistant_msg,
                    "source_file": file
                })

df = pd.DataFrame(rows)
df.to_csv("rag_dataset.csv", index=False)

print(df.head())
print("Total rows:", len(df))