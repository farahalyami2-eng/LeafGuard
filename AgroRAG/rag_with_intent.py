"""
RAGChatbot — importable wrapper around the AgroRAG knowledge-base Q&A system.

Usage:
    from rag_with_intent import RAGChatbot

    bot = RAGChatbot()
    result = bot.ask("How do I mix Bacteria Clear?")
    # {"answer": "...", "intent": "cat1_usage_product", "sources": [...]}

    # With context from upstream image analysis
    result = bot.ask(
        "What should I do about it?",
        context={"crop": "citrus", "disease": "Downy_Mildew"},
    )
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Resolve paths relative to this file so the module works from any cwd
_HERE = Path(__file__).parent
load_dotenv(_HERE / ".env")

import joblib
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic

# ── Constants ──────────────────────────────────────────────────────────────

# Maps LabelEncoder integer → category string (alphabetical order matches fit order)
INTENT_LABELS: dict[int, str] = {
    0: "cat1_usage_product",
    1: "cat2_diagnosis",
    2: "cat3_aftersales_logistics",
    3: "cat4_safety_sensitive",
}

_INTENT_DESCRIPTIONS: dict[str, str] = {
    "cat1_usage_product":        "product usage, dosage, mixing ratio, application, spraying",
    "cat2_diagnosis":            "plant disease, pests, weeds, symptoms, treatment effectiveness",
    "cat3_aftersales_logistics": "orders, delivery, shipping, refunds, price, store link",
    "cat4_safety_sensitive":     "safety, toxicity, children, pets, chemicals, protective gear",
}


# ── RAGChatbot ─────────────────────────────────────────────────────────────

class RAGChatbot:
    """
    Agricultural Q&A chatbot backed by:
      - TF-IDF + LogisticRegression intent classifier (intent_classifier.joblib)
      - Chroma vector DB with 430 Q&A embeddings (agri_db/)
      - GPT-4o-mini for answer synthesis

    All file paths are resolved relative to this module, so the class is safe
    to import and use from any working directory.
    """

    def __init__(self) -> None:
        print("[RAG] Loading intent classifier …")
        self._intent_model = joblib.load(_HERE / "intent_classifier.joblib")

        print("[RAG] Loading vector database …")
        self._embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-base"
        )
        self._vectordb = Chroma(
            persist_directory=str(_HERE / "agri_db"),
            embedding_function=self._embeddings,
        )

        self._llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0)
        print("[RAG] Ready.")

    # ── Public API ─────────────────────────────────────────────────────────

    def ask(
        self,
        question: str,
        context: Optional[dict] = None,
    ) -> dict:
        """
        Answer an agricultural question using intent classification + retrieval + GPT.

        Args:
            question: The user's question in natural language.
            context:  Optional dict with 'crop' and/or 'disease' keys coming from
                      upstream image analysis. Enriches the retrieval query and
                      is injected into the generation prompt.

        Returns:
            {
              "answer":  str,        # GPT-generated answer
              "intent":  str,        # Detected intent category
              "sources": list[str],  # Short previews of retrieved documents
            }
        """
        retrieval_query = self._build_retrieval_query(question, context)
        intent          = self._predict_intent(retrieval_query)
        docs            = self._retrieve(retrieval_query, intent)
        knowledge_text  = "\n\n---\n\n".join(d.page_content for d in docs)

        # Build context block for the prompt
        ctx_lines: list[str] = []
        if context:
            if context.get("crop"):
                ctx_lines.append(f"Crop identified: {context['crop']}")
            if context.get("disease"):
                ctx_lines.append(f"Disease detected: {context['disease']}")
        ctx_block = (
            "Additional context from image analysis:\n" + "\n".join(ctx_lines) + "\n\n"
            if ctx_lines else ""
        )

        prompt = f"""You are an agricultural customer support assistant for LeafGuard.

Detected user intent: {intent} ({_INTENT_DESCRIPTIONS.get(intent, '')})

{ctx_block}Retrieved knowledge:
{knowledge_text}

User question: {question}

Instructions:
- Answer using the retrieved knowledge. Be concise and accurate.
- Include dosage, mixing ratios, or usage steps if the knowledge contains them.
- For safety questions, recommend checking the product label and consulting an expert.
- Only say information is unavailable if nothing in the retrieved documents is relevant.

Answer format:
Direct Answer:
<your answer>

Evidence:
<key facts used from retrieved context>

Source Category:
{intent}"""

        answer = self._llm.invoke(prompt).content.strip()

        sources = [
            doc.page_content[:120].replace("\n", " ").strip() + "…"
            for doc in docs
        ]

        return {"answer": answer, "intent": intent, "sources": sources}

    # ── Internal helpers ───────────────────────────────────────────────────

    def _build_retrieval_query(self, question: str, context: Optional[dict]) -> str:
        """Append crop/disease context to the query for better embedding match."""
        if not context:
            return question
        extras = [question]
        if context.get("crop"):
            extras.append(f"crop: {context['crop']}")
        if context.get("disease"):
            extras.append(f"disease: {context['disease']}")
        return " ".join(extras)

    def _predict_intent(self, query: str) -> str:
        """
        TF-IDF + LR prediction; GPT fallback when confidence < 0.65.
        Returns one of the four INTENT_LABELS strings.
        """
        probs     = self._intent_model.predict_proba([query])[0]
        classes   = self._intent_model.classes_
        best_idx  = int(probs.argmax())
        confidence = float(probs[best_idx])
        ml_intent  = INTENT_LABELS.get(int(classes[best_idx]), str(classes[best_idx]))

        if confidence >= 0.65:
            return ml_intent

        # Low confidence — ask GPT
        fallback_prompt = (
            "Classify this agricultural question into exactly one category name:\n\n"
            + "\n".join(
                f"{k}  —  {v}" for k, v in _INTENT_DESCRIPTIONS.items()
            )
            + f"\n\nReturn ONLY the category name.\n\nQuestion: {query}"
        )
        gpt_intent = self._llm.invoke(fallback_prompt).content.strip()
        return gpt_intent if gpt_intent in INTENT_LABELS.values() else ml_intent

    def _retrieve(self, query: str, intent: str, k: int = 5) -> list:
        """
        Semantic search filtered by the predicted intent category.
        Falls back to unfiltered search if fewer than 3 documents are returned
        (guards against a wrong intent prediction).
        """
        docs = self._vectordb.similarity_search(
            query, k=k, filter={"category": intent}
        )
        if len(docs) < 3:
            docs = self._vectordb.similarity_search(query, k=k)
        return docs
