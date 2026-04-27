# Personal Shopping Recommender

개인화 상품 추천을 위한 FastAPI 백엔드입니다.

사용자 행동을 선호 프로필로 정리하고, 작은 PyTorch Transformer 모델이 상품의 `semantic_id`를 생성합니다. 생성 과정에는 STATIC 방식의 prefix 제약을 적용해 카탈로그에 존재하는 상품만 추천되도록 합니다.

## Overview

```text
User Events
    ↓
Preference Profile
    ↓
Transformer Recommender
    ↓
STATIC Constrained Decoding
    ↓
Recommended Items
```

상품은 일반적인 `item_id`와 별도로 모델이 생성할 수 있는 `semantic_id`를 가집니다.

```text
item_id     = item-10001
semantic_id = [12, 7, 3, 21]
```

추천 모델은 사용자의 선호 프로필과 현재까지 생성된 prefix를 보고 다음 token logits를 만듭니다. STATIC index는 현재 prefix에서 이어질 수 있는 token만 남깁니다.

```text
prefix            = [12, 7]
valid next tokens = [3, 9, 21]
```

완성된 `semantic_id`는 다시 `item_id`로 복원되고, 추천 trace와 함께 응답됩니다.

## Why This Project

일반적인 포트폴리오용 추천 API는 상품 점수를 계산하고 정렬하는 수준에서 끝나는 경우가 많습니다. 이 프로젝트는 추천 결과를 생성 모델이 token 단위로 만들고, 그 결과를 백엔드 제약 인덱스로 통제하는 구조를 다룹니다.

중점은 아래 세 가지입니다.

- 실제 Transformer 모델을 추천 생성 경로에 포함합니다.
- STATIC 제약으로 존재하지 않는 상품 ID 생성을 막습니다.
- DDD 기반 modular monolith 구조로 추천 도메인을 분리합니다.

## Features

| Area | Description |
| --- | --- |
| Catalog | 상품 정보와 `semantic_id` 매핑을 관리합니다. |
| Interaction | 조회, 클릭, 찜, 구매, 숨김 이벤트를 저장합니다. |
| Profile | 사용자 이벤트를 선호 프로필로 요약합니다. |
| Recommender | PyTorch Transformer로 다음 `semantic_id` token을 예측합니다. |
| Constraint | STATIC index로 prefix별 valid token을 계산합니다. |
| Analytics | 추천 결과와 생성 과정을 trace로 남깁니다. |

## Architecture

하나의 FastAPI 애플리케이션으로 배포하되, 내부는 모듈 단위로 나눕니다. 초기 단계에서 마이크로서비스로 나누기보다, 모듈 경계를 분명히 둔 modular monolith로 시작합니다.

```text
src/persistent_memory_recsys/
  bootstrap/
  shared/
  catalog/
  interaction/
  profile/
  constraint/
  recommendation/
  analytics/
```

각 모듈은 가능한 한 같은 계층 구조를 사용합니다.

```text
domain/
  도메인 모델과 규칙

application/
  유스케이스와 포트

adapters/
  HTTP, DB, model runtime 등 외부 입출력 구현
```

도메인 계층은 FastAPI, SQLAlchemy, PyTorch에 직접 의존하지 않도록 둡니다.

## Recommendation Flow

1. 사용자의 최근 이벤트를 조회합니다.
2. 이벤트를 선호 프로필로 변환합니다.
3. 선호 프로필을 model input으로 인코딩합니다.
4. Transformer 모델이 다음 `semantic_id` token logits를 계산합니다.
5. STATIC index가 현재 prefix에서 가능한 token만 남깁니다.
6. token을 반복 생성해 `semantic_id`를 완성합니다.
7. `semantic_id`를 실제 상품으로 복원합니다.
8. 추천 결과와 trace id를 반환합니다.

## Model

추천 모델은 작은 Transformer로 시작합니다. 외부 LLM API에 의존하지 않고, 서버 내부에서 추론 가능한 크기로 유지합니다.

```text
profile embedding
+ semantic token embedding
+ positional embedding
→ TransformerEncoder
→ vocab projection
→ next-token logits
```

초기 모델은 작은 seed dataset으로 학습하거나 재현 가능한 weight 초기화로 시작합니다. 이후 사용자 이벤트와 상품 카탈로그를 기반으로 next-token prediction 학습 루프를 추가합니다.

## STATIC Constraint

STATIC은 생성 가능한 token sequence를 제한하기 위한 인덱스입니다. 공식 구현은 trie를 dense lookup table과 CSR sparse matrix로 변환해 accelerator-friendly constrained decoding을 수행합니다.

이 프로젝트는 다음 순서로 구현합니다.

1. 상품의 `semantic_id` 목록으로 trie index를 만듭니다.
2. prefix를 입력받아 가능한 다음 token을 반환합니다.
3. 모델 logits에서 invalid token을 선택하지 못하게 masking합니다.
4. 완성된 `semantic_id`가 실제 상품으로 복원되는지 검증합니다.
5. 이후 dense/CSR 기반 index로 교체할 수 있게 인터페이스를 분리합니다.

## API

초기 API 범위입니다.

```text
GET  /api/v1/health

GET  /api/v1/catalog/items
POST /api/v1/catalog/items

GET  /api/v1/constraints/static-index
POST /api/v1/constraints/static-index/rebuild
GET  /api/v1/constraints/next-tokens

POST /api/v1/events
GET  /api/v1/users/{user_id}/events

GET  /api/v1/profiles/{user_id}
POST /api/v1/profiles/{user_id}/refresh

GET  /api/v1/recommendations/home/{user_id}
GET  /api/v1/recommendations/traces/{trace_id}
```

추천 응답 예시는 아래 형태를 기준으로 합니다.

```json
{
  "user_id": "user-1",
  "items": [
    {
      "item_id": "item-10001",
      "semantic_id": [12, 7, 3, 21],
      "reason": "minimal outerwear preference"
    }
  ],
  "trace_id": "rec-trace-01",
  "model_version": "transformer-small-v1",
  "static_index_version": "static-2026-04-28"
}
```

## Tech Stack

| Layer | Stack |
| --- | --- |
| API | FastAPI |
| Language | Python 3.12 |
| Model | PyTorch |
| Database | PostgreSQL |
| ORM / Migration | SQLAlchemy, Alembic |
| Test | pytest |
| Package / Env | uv |

## Getting Started

```bash
uv sync
```

```bash
uv run uvicorn persistent_memory_recsys.main:app --reload
```

```bash
uv run pytest -q
```

## Project Status

현재 저장소는 백엔드 구조를 새 방향에 맞춰 다시 작성하는 단계입니다.

| Step | Status |
| --- | --- |
| README 방향 정리 | Done |
| 카탈로그와 semantic_id 매핑 | Planned |
| STATIC trie index | Planned |
| 사용자 이벤트와 선호 프로필 | Planned |
| Transformer 추천 모델 | Planned |
| 추천 API와 trace | Planned |
| PostgreSQL 저장소 | Planned |
| 모델 학습 스크립트 | Planned |

## Completion Criteria

포트폴리오 완성 기준은 아래와 같습니다.

- 로컬에서 실행 가능한 FastAPI 서버
- PostgreSQL 기반 영속성
- Alembic 마이그레이션
- seed 데이터
- PyTorch Transformer 추천 모델
- STATIC constrained decoding
- 추천 trace
- API 테스트
- 도메인 테스트
- 모델 초기화 또는 학습 스크립트

## Out of Scope

- 쇼핑 챗봇
- RAG
- Elasticsearch 검색
- 실시간 학습 파이프라인
- 마이크로서비스 분리
- 프론트엔드 화면

## References

- STATIC: https://github.com/youtube/static-constraint-decoding
- Paper: https://arxiv.org/abs/2602.22647
