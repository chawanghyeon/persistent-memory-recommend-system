from dataclasses import dataclass

from persistent_memory_recsys.preference.adapters.outbound.in_memory import (
    InMemoryPreferenceStateReader,
)
from persistent_memory_recsys.preference.application.ports import PreferenceStateReader
from persistent_memory_recsys.shared.domain.module_status import (
    ModuleReadiness,
    ModuleStatus,
)


@dataclass(slots=True)
class PreferenceModule:
    preference_state_reader: PreferenceStateReader
    status: ModuleStatus


def build_preference_module() -> PreferenceModule:
    return PreferenceModule(
        preference_state_reader=InMemoryPreferenceStateReader(),
        status=ModuleStatus(
            bounded_context="preference",
            description="선호 상태 판별과 활성 선호 상태 경계.",
            readiness=ModuleReadiness.SKELETON,
            next_step="선호 상태 생성 서비스와 검증 규칙을 추가한다.",
        ),
    )
