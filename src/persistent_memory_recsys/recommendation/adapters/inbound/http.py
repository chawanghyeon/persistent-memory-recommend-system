from dataclasses import asdict

from fastapi import APIRouter

from persistent_memory_recsys.recommendation.application.use_cases import (
    GenerateHomeRecommendationPreviewUseCase,
)


def build_recommendation_router(
    home_preview_use_case: GenerateHomeRecommendationPreviewUseCase,
) -> APIRouter:
    router = APIRouter(tags=["recommendation"])

    @router.get("/recommendations/home/{user_id}")
    def home_recommendation_preview(user_id: str) -> dict[str, object]:
        return asdict(home_preview_use_case.execute(user_id))

    return router
