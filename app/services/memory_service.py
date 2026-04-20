from app.services.session_service import get_session, update_session
from app.services.llm_service import query_llm

def update_summary_async(session_id, old_summary, question, answer):
    try:
        new_summary = update_summary(old_summary, question, answer)

        session = get_session(session_id)

        # ⚠️ importante: no perder historial
        session["summary"] = new_summary

        # guardar TODO
        update_session(
            session_id,
            new_summary,
            question=None,
            answer=None
        )

    except Exception as e:
        print("Summary update failed:", e)

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