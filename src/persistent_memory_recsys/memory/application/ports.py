from typing import Protocol

from persistent_memory_recsys.memory.domain.models import MemorySnapshot


class MemorySnapshotReader(Protocol):
    def get_snapshot(self, user_id: str) -> MemorySnapshot:
        """Load the latest active memory snapshot for a user."""
