from dataclasses import asdict, dataclass

from persistent_memory_recsys.constraint.application.ports import StaticIndexManager


@dataclass(slots=True)
class GetActiveStaticIndexUseCase:
    static_index_manager: StaticIndexManager

    def execute(self) -> dict[str, object]:
        return asdict(self.static_index_manager.describe_active_index())


@dataclass(slots=True)
class RebuildActiveStaticIndexUseCase:
    static_index_manager: StaticIndexManager

    def execute(self) -> dict[str, object]:
        return asdict(self.static_index_manager.rebuild_active_index())
