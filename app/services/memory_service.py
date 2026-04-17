from app.services.llm_service import query_llm

def update_summary(previous_summary, question, answer):
    prompt = f"""
You are managing a conversation summary.

Update the summary based on the new interaction.

Previous summary:
{previous_summary}

New interaction:
User: {question}
Assistant: {answer}

Updated summary:
"""

    return query_llm(prompt).strip()