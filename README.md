# 장기기억 기반 추천 시스템

커머스 도메인을 대상으로 하는 장기기억 기반 생성형 추천 백엔드다.  
사용자 행동을 장기기억과 선호 상태로 정리한 뒤, `semantic_id`를 생성하고 `STATIC`으로 유효한 추천만 남기는 구조를 기준으로 한다.

현재 저장소는 서비스 완성본이 아니라 구조와 핵심 경로를 검증하는 단계다.  
지금 포함된 범위는 아래와 같다.

- 카탈로그 기준 `semantic_id` 생성
- 활성 `STATIC` 인덱스 생성과 재생성
- 홈 추천 미리보기
- 활성 semantic 매핑 조회
- 활성 `STATIC` 인덱스 조회

## 구조

코드는 `DDD + modular monolith + hexagonal architecture` 기준으로 나눈다.

```text
src/persistent_memory_recsys/
  bootstrap/
  shared/
  interaction/
  memory/
  preference/
  catalog/
  recommendation/
  constraint/
```

각 모듈은 공통적으로 아래 구조를 따른다.

- `domain`
- `application`
- `adapters`
- `module.py`

## 실행

의존성 설치:

```bash
uv sync
```

개발 서버 실행:

```bash
uv run uvicorn persistent_memory_recsys.main:app --reload
```

테스트 실행:

```bash
uv run pytest -q
```

## 주요 API

상태 확인:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/system/status
```

semantic mapping:

```bash
curl http://127.0.0.1:8000/api/v1/catalog/semantic-mappings
curl -X POST http://127.0.0.1:8000/api/v1/catalog/semantic-mappings/regenerate
```

STATIC 인덱스:

```bash
curl http://127.0.0.1:8000/api/v1/constraints/static-index
curl -X POST http://127.0.0.1:8000/api/v1/constraints/static-index/rebuild
```

추천 미리보기:

```bash
curl http://127.0.0.1:8000/api/v1/recommendations/home/test-user
```

## 문서

상세 설계와 계약 문서는 [docs/README.md](./docs/README.md)에서 시작하면 된다.
