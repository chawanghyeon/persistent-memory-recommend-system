from dataclasses import dataclass

from persistent_memory_recsys.memory.adapters.outbound.in_memory import (
    InMemoryMemorySnapshotReader,
)
from persistent_memory_recsys.memory.application.ports import MemorySnapshotReader
from persistent_memory_recsys.shared.domain.module_status import (
    ModuleReadiness,
    ModuleStatus,
)


@dataclass(slots=True)
class MemoryModule:
    memory_snapshot_reader: MemorySnapshotReader
    status: ModuleStatus


def build_memory_module() -> MemoryModule:
    return MemoryModule(
        memory_snapshot_reader=InMemoryMemorySnapshotReader(),
        status=ModuleStatus(
            bounded_context="memory",
            description="장기기억 저장, 통합, 스냅샷 조회 경계.",
            readiness=ModuleReadiness.SKELETON,
            next_step="사용자 기억 집계와 스냅샷 조립을 구현한다.",
        ),
    )
