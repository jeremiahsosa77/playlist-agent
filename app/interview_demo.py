"""Interactive command-line demo for the AI playlist interview."""

from app.conversation import (
    ConfiguredInterviewProvider,
    ConversationService,
    ConversationStatus,
)


def main() -> None:
    """
    Run an adaptive playlist interview in the terminal.
    """
    provider = ConfiguredInterviewProvider()

    service = ConversationService(
        decision_provider=provider
    )

    session = service.start_session()

    print()
    print("Playlist Agent Interview")
    print("------------------------")
    print()
    print(
        f"AI: {session.messages[-1].content}"
    )

    while (
        session.status
        == ConversationStatus.ACTIVE
    ):
        print()

        user_response = input(
            "You: "
        ).strip()

        if not user_response:
            print(
                "Please enter a response."
            )
            continue

        if user_response.lower() in {
            "quit",
            "exit",
            "cancel",
        }:
            session = service.cancel_session(
                session.id
            )

            print()
            print("Interview cancelled.")
            return

        session, action = service.respond_to_user(
            session.id,
            user_response,
        )

        print()

        if (
            session.status
            == ConversationStatus.READY_TO_GENERATE
        ):
            print(
                "AI: I have enough information "
                "to create your playlist."
            )
            print()
            print(
                "Decision summary: "
                f"{action.reasoning_summary}"
            )
            print()
            print(
                f"Questions asked: "
                f"{session.question_count}"
            )
            print(
                f"Clarifications: "
                f"{session.clarification_count}"
            )
            print(
                f"User responses: "
                f"{session.user_message_count}"
            )
            return

        print(
            f"AI: {action.question}"
        )


if __name__ == "__main__":
    main()