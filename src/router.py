from src.portfolio_health import run as run_portfolio_health
from src.schemas import ClassificationResult

#dispatch is the main function that takes a ClassificationResult, which includes the intent, agent, entities, and any other relevant information about the user's query, and routes it to the appropriate agent for handling.
def dispatch(classification: ClassificationResult, user_context: dict | None = None, llm=None) -> dict:
    if classification.agent == "portfolio_health":
        return run_portfolio_health(user_context or {}, llm=llm)

    return {
        "intent": classification.intent,
        "agent": classification.agent,
        "entities": classification.entities,
        "message": (
            f"The {classification.agent} agent is not implemented in this MVP. "
            "The router still classified and dispatched the request successfully."
        ),
    }
