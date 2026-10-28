
import logging
from contextlib import closing

from django.conf import settings

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver

from .agent import build_wellness_agent


logger = logging.getLogger(__name__)

ERROR_MESSAGE = (
    "I'm having trouble responding right now. "
    "Please try again."
)


def get_thread_id(user):
    """Give each user a persistent conversation thread."""
    return f"mindwell-user-{user.pk}"


def get_config(user):
    """Configuration used to load and save conversation state."""
    return {
        "configurable": {
            "thread_id": get_thread_id(user),
        },
        "recursion_limit": 8,
    }


def get_agent(checkpointer, user):
    return build_wellness_agent(
        user_id=user.pk,
        checkpointer=checkpointer,
    )


def get_database_url():
    database_url = getattr(
        settings, "DATABASE_URL", None
    )

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    return database_url


def send_chat_message(user, message):
    """Invoke the agent with persistent PostgreSQL checkpoints."""
    try:
        with PostgresSaver.from_conn_string(
            get_database_url()
        ) as checkpointer:

            # Ensure LangGraph checkpoint tables exist.
            checkpointer.setup()

            agent = get_agent(checkpointer, user)

            result = agent.invoke(
                {
                    "messages": [
                        HumanMessage(content=message)
                    ]
                },
                config=get_config(user),
            )

            response = result["messages"][-1].content

            if isinstance(response, str) and response.strip():
                return response.strip()

            logger.error("Chat agent returned an empty response.")
            return ERROR_MESSAGE

    except Exception:
        logger.exception("LangGraph chat request failed")
        return ERROR_MESSAGE


def get_chat_history(user):
    """Load the latest visible messages from PostgreSQL."""
    try:
        with PostgresSaver.from_conn_string(
            get_database_url()
        ) as checkpointer:

            checkpointer.setup()

            agent = get_agent(checkpointer, user)

            state = agent.get_state(get_config(user))

            if not state.values:
                return []

            messages = state.values.get("messages", [])
            history = []

            for msg in messages:
                if msg.type not in ("human", "ai"):
                    continue

                # Don't display internal tool-call messages.
                if getattr(msg, "tool_calls", None):
                    continue

                if not isinstance(msg.content, str):
                    continue

                if not msg.content.strip():
                    continue

                history.append({
                    "role": (
                        "user"
                        if msg.type == "human"
                        else "assistant"
                    ),
                    "content": msg.content,
                })

            return history[-30:]

    except Exception:
        logger.exception(
            "Failed to load LangGraph chat history"
        )
        raise
