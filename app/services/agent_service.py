from app.services.llm_service import query_llm

def decide_action(question):
    prompt = f"""
You are an AI assistant that decides how to handle a user request.

Decide the best action:

- "rag" → if the question requires company documents
- "general" → if it's a general knowledge question
- "clarify" → if the question is unclear

Only return one word: rag, general, or clarify.

Question:
{question}

Decision:
"""

    decision = query_llm(prompt).strip().lower()

    if "rag" in decision:
        return "rag"
    elif "clarify" in decision:
        return "clarify"
    else:
        return "general"