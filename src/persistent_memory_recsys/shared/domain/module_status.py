from dataclasses import dataclass
from enum import StrEnum


class ModuleReadiness(StrEnum):
    SKELETON = "골격"
    FOUNDATIONAL = "기반구현"
    IMPLEMENTING = "구현중"


@dataclass(frozen=True, slots=True)
class ModuleStatus:
    bounded_context: str
    description: str
    readiness: ModuleReadiness
    next_step: str

    def as_dict(self) -> dict[str, str]:
        return {
            "bounded_context": self.bounded_context,
            "description": self.description,
            "readiness": self.readiness.value,
            "next_step": self.next_step,
        }


@dataclass(frozen=True, slots=True)
class SystemStatus:
    app_name: str
    architecture: str
    package_name: str
    module_statuses: tuple[ModuleStatus, ...]
    current_phase: str
    next_milestone: str

    def as_dict(self) -> dict[str, object]:
        return {
            "app_name": self.app_name,
            "architecture": self.architecture,
            "package_name": self.package_name,
            "current_phase": self.current_phase,
            "next_milestone": self.next_milestone,
            "bounded_contexts": [module.as_dict() for module in self.module_statuses],
        }
