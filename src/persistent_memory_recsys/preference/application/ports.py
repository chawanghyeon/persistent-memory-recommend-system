from typing import Protocol

from persistent_memory_recsys.preference.domain.models import PreferenceState


class PreferenceStateReader(Protocol):
    def get_active_state(self, user_id: str) -> PreferenceState:
        """Load the active preference state for a user."""
