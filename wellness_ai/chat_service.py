
from contextlib import closing
import logging
import sqlite3

from django.conf import settings
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from .agent import build_wellness_agent


logger = logging.getLogger(__name__)

DATABASE_PATH = str(
    settings.DATABASES["default"]["NAME"]
)

ERROR_MESSAGE = (
    "I'm having trouble responding right now. "
    "Please try again."
)


def get_thread_id(user):
    """
    Each Django user has one persistent
    LangGraph conversation thread.
    """
    return f"mindwell-user-{user.pk}"


def get_config(user):
    """
    LangGraph uses the thread ID to locate
    the latest saved conversation state.
    """
    return {
        "configurable": {
            "thread_id": get_thread_id(user)
        },
        "recursion_limit": 8,
    }


def get_agent(checkpointer, user):
    return build_wellness_agent(
        user_id=user.pk,
        checkpointer=checkpointer
    )


def send_chat_message(user, message):
    """
    Send a new message to the agent.

    LangGraph loads the previous conversation
    and saves the new state automatically.
    """

    config = get_config(user)

    try:
        with closing(sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False,
            timeout=30
        )) as conn:

            checkpointer = SqliteSaver(conn)

            agent = get_agent(
                checkpointer,
                user
            )

            result = agent.invoke(
                {
                    "messages": [
                        HumanMessage(content=message)
                    ]
                },
                config=config
            )

            last_message = result["messages"][-1]

            response = last_message.content

            if not isinstance(response, str):
                return ERROR_MESSAGE

            if not response.strip():
                return ERROR_MESSAGE

            return response.strip()

    except Exception:
        logger.exception(
            "LangGraph chat request failed"
        )
        return ERROR_MESSAGE


def get_chat_history(user):
    """
    Retrieve the most recent visible messages
    from the user's LangGraph thread.
    """

    config = get_config(user)

    with closing(sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False,
        timeout=30
    )) as conn:

        checkpointer = SqliteSaver(conn)

        agent = get_agent(
            checkpointer,
            user
        )

        state = agent.get_state(config)

        messages = state.values.get(
            "messages", []
        )

        history = []

        for msg in messages:

            if msg.type not in ("human", "ai"):
                continue

            # Hide internal tool-calling messages
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
                "content": msg.content
            })

        return history[-30:]
