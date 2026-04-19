from dataclasses import dataclass

from persistent_memory_recsys.interaction.adapters.outbound.in_memory import (
    InMemoryUserEventRecorder,
)
from persistent_memory_recsys.interaction.application.ports import UserEventRecorder
from persistent_memory_recsys.shared.domain.module_status import (
    ModuleReadiness,
    ModuleStatus,
)


@dataclass(slots=True)
class InteractionModule:
    event_recorder: UserEventRecorder
    status: ModuleStatus


def build_interaction_module() -> InteractionModule:
    return InteractionModule(
        event_recorder=InMemoryUserEventRecorder(),
        status=ModuleStatus(
            bounded_context="interaction",
            description="사용자 이벤트 적재, 노출 로그, 멱등 처리 경계.",
            readiness=ModuleReadiness.SKELETON,
            next_step="정규화된 사용자 이벤트 명령과 영속성 어댑터를 추가한다.",
        ),
    )
