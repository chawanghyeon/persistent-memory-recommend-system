from persistent_memory_recsys.preference.application.ports import PreferenceStateReader
from persistent_memory_recsys.preference.domain.models import PreferenceState


class InMemoryPreferenceStateReader(PreferenceStateReader):
    def get_active_state(self, user_id: str) -> PreferenceState:
        return PreferenceState(
            user_id=user_id,
            likes=("minimal", "black"),
            preferred_categories=("outerwear",),
            blocked_brands=("BrandX",),
            blocked_categories=("formal_shoes",),
            price_sensitivity="medium",
            exploration_tolerance=20,
            state_confidence=0.82,
            text_summary="미니멀한 블랙 계열의 아우터를 선호한다.",
        )
