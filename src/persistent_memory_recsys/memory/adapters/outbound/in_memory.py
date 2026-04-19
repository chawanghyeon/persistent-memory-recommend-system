from persistent_memory_recsys.memory.application.ports import MemorySnapshotReader
from persistent_memory_recsys.memory.domain.models import MemorySnapshot


class InMemoryMemorySnapshotReader(MemorySnapshotReader):
    def get_snapshot(self, user_id: str) -> MemorySnapshot:
        return MemorySnapshot(
            user_id=user_id,
            hard_blocks={
                "brands": ("BrandX",),
                "categories": ("formal_shoes",),
            },
        )
