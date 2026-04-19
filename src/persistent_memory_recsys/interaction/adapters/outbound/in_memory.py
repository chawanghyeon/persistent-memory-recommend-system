from collections.abc import Sequence

from persistent_memory_recsys.interaction.application.ports import UserEventRecorder
from persistent_memory_recsys.interaction.domain.models import UserEvent


class InMemoryUserEventRecorder(UserEventRecorder):
    def __init__(self) -> None:
        self._events: list[UserEvent] = []

    def record(self, event: UserEvent) -> None:
        self._events.append(event)

    def list_recent(self, user_id: str) -> Sequence[UserEvent]:
        return tuple(event for event in self._events if event.user_id == user_id)
