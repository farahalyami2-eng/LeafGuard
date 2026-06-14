import pandas as pd

df = pd.read_csv("rag_dataset.csv")

def fix_category(question, old_category):
    q = str(question).lower()

    # Safety first
    if any(word in q for word in [
        "safe", "children", "pets", "toxic", "poison",
        "gloves", "mask", "chemical", "chemicals"
    ]):
        return "cat4_safety_sensitive"

    # Product usage
    if any(word in q for word in [
        "how do i use", "how is this used", "how is it used",
        "mix with water", "water for one bag", "ml to use",
        "how many ml", "dosage", "dose", "apply", "spray",
        "use it", "used", "watering", "watered in"
    ]):
        return "cat1_usage_product"

    # Diagnosis
    if any(word in q for word in [
        "yellow", "leaves", "spots", "wilting", "disease",
        "thrips", "weeds", "pest", "infection", "remove"
    ]):
        return "cat2_diagnosis"

    # After-sales / logistics
    if any(word in q for word in [
        "send", "shipping", "delivery", "refund", "return",
        "price", "order", "pinduoduo", "selling", "bottle"
    ]):
        return "cat3_aftersales_logistics"

    return old_category


df["old_category"] = df["category"]
df["category"] = df.apply(
    lambda row: fix_category(row["question"], row["category"]),
    axis=1
)

changed = df[df["old_category"] != df["category"]]

print("Changed rows:", len(changed))
print(changed[["question", "old_category", "category"]].head(30))

df.to_csv("rag_dataset_fixed.csv", index=False)
print("Saved fixed dataset as rag_dataset_fixed.csv")