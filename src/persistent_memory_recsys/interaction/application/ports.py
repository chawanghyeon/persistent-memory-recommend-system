from collections.abc import Sequence
from typing import Protocol

from persistent_memory_recsys.interaction.domain.models import UserEvent


class UserEventRecorder(Protocol):
    def record(self, event: UserEvent) -> None:
        """Persist a normalized user event."""

    def list_recent(self, user_id: str) -> Sequence[UserEvent]:
        """Return recent events for a user."""
