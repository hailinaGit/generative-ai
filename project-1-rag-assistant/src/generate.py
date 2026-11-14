"""Grounded Local LLM Generation module for Cambodia HR RAG Assistant (FR-03 & FR-04).

Uses LangChain + local Ollama model to ensure:
- 100% offline / local execution (no OpenAI required).
- Strict grounding against retrieved Cambodia labor law chunks.
- Explicit citations linking answers to source documents and sections.
- Fallback message when facts are absent from the approved policy.

Usage:
    python src/generate.py "How many days of annual leave do employees get in Cambodia?"
    python src/generate.py "What is the overtime rate on public holidays?" --model llama3.2
"""
import argparse
import re
import sys
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

try:
    from src.retrieve import DEFAULT_DB_DIR, retrieve_relevant_chunks
except ModuleNotFoundError:
    from retrieve import DEFAULT_DB_DIR, retrieve_relevant_chunks

# Strict RAG system prompt enforcing grounding & citations (FR-03, FR-04)
RAG_SYSTEM_PROMPT = """You are a specialized HR Compliance Assistant for Cambodian Labor Law and internal regulations.

SCOPE CONSTRAINT:
You are AUTHORIZED to answer questions related to HR, employment, labor law, working conditions, wages, leave, overtime, seniority pay, disciplinary actions, and staff policies in Cambodia.

RULES:
1. Approved Scope: If the question is about HR, labor regulations, or employee policies in Cambodia (including broad questions like "tell me about HR policy" or "what are the policies?"), answer thoroughly using the provided context blocks. Summarize all relevant sections and cite their source document and section headers (e.g. "[cambodia_hr_regulations.md - Section: 2. Leave & Time-Off Policies]").
2. Strictly Out-of-Scope: If the user's question is NOT about HR or Cambodian labor regulations (such as coding, general knowledge, other countries' laws like US 401k/tax, sports, weather, unrelated company operations, or topics completely absent from the context), you MUST refuse to answer and reply with this EXACT sentence and nothing else:
   "I cannot find this information in the approved policy documents."
3. Zero Hallucination: Never invent rules, provisions, or percentages not explicitly stated in the context.

Context:
{context}
"""


def format_context_for_llm(chunks: list[dict[str, Any]]) -> str:
    """Format chunks into clear labeled context blocks."""
    if not chunks:
        return "No relevant context available."

    blocks = []
    for i, c in enumerate(chunks, 1):
        block = (
            f"[Source {i}: {c['source']} | Section: {c['section']}]\n"
            f"{c['content']}"
        )
        blocks.append(block)
    return "\n\n".join(blocks)


def generate_answer(
    query: str,
    model_name: str = "llama3.2",
    top_k: int = 3,
    temperature: float = 0.0,
    db_dir: str = DEFAULT_DB_DIR,
) -> dict[str, Any]:
    """Retrieve chunks and synthesize a grounded answer using a local LangChain LLM."""
    chunks = retrieve_relevant_chunks(query=query, top_k=top_k, db_dir=db_dir)

    if not chunks:
        return {
            "query": query,
            "answer": "I cannot find this information in the approved policy documents.",
            "citations": [],
            "chunks": [],
        }

    context_text = format_context_for_llm(chunks)

    # Initialize local LLM via LangChain Ollama
    llm = ChatOllama(
        model=model_name,
        temperature=temperature,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", RAG_SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    chain = prompt | llm

    response = chain.invoke({
        "context": context_text,
        "question": query,
    })

    citations = [
        {"source": c["source"], "section": c["section"], "distance": c["distance"]}
        for c in chunks
    ]

    # Clean out markdown bold asterisks (**) for clean reading
    clean_answer = re.sub(r"\*\*(.*?)\*\*", r"\1", str(response.content))
    clean_answer = clean_answer.replace("**", "")

    return {
        "query": query,
        "answer": clean_answer,
        "citations": citations,
        "chunks": chunks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query_pos", nargs="?", help="Question to ask the HR assistant")
    parser.add_argument("--query", "-q", help="Question to ask")
    parser.add_argument("--model", "-m", default="llama3.2", help="Ollama local model name (default: llama3.2)")
    parser.add_argument("--top-k", "-k", type=int, default=3, help="Number of retrieved chunks")
    parser.add_argument("--temperature", "-t", type=float, default=0.0, help="LLM temperature")
    args = parser.parse_args()

    query = args.query or args.query_pos
    if not query:
        print("Please provide a question to query.")
        print("Example: python src/generate.py 'What is the maternity leave duration and pay?'")
        sys.exit(1)

    print(f"\nUser Query: {query}")
    print(f"Using Local Model: {args.model}")
    print("=" * 60)

    try:
        result = generate_answer(
            query=query,
            model_name=args.model,
            top_k=args.top_k,
            temperature=args.temperature,
        )
    except Exception as e:
        print(f"\nError running local LLM generation: {e}", file=sys.stderr)
        print("\nTip: Make sure Ollama is running (`ollama serve`) and the model is downloaded (`ollama pull llama3.2`).", file=sys.stderr)
        sys.exit(1)

    print("\n--- Response ---")
    print(result["answer"])
    print("\n--- Verified Citations ---")
    for i, cite in enumerate(result["citations"], 1):
        print(f"[{i}] {cite['source']} -> Section: \"{cite['section']}\" (Distance: {cite['distance']})")


if __name__ == "__main__":
    main()

