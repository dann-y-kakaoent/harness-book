---
name: book-writer
description: "책 집필 오케스트레이터. 에이전트 팀을 조율하여 책 한 권을 완성합니다. '책 집필', '책 쓰기', 'write book' 요청 시 트리거."
---

# Book Writer — 집필 오케스트레이터

에이전트 팀(book-planner, chapter-writer, book-editor, infographic-creator, book-publisher)을 조율하여 책 한 권을 완성하는 오케스트레이터 스킬.

## 에이전트 팀 구성

| 에이전트 | 역할 | 모델 | Phase |
|---------|------|------|-------|
| `book-planner` | 목차/구조 설계 | sonnet | 1 |
| `chapter-writer` | 챕터 집필 | opus | 2, 3 |
| `book-editor` | 원고 리뷰/편집 | sonnet | 3 |
| `infographic-creator` | SVG 인포그래픽 | sonnet | 4 |
| `book-publisher` | PDF + 웹 뷰어 | sonnet | 5 |

## 디렉토리 구조

```
book/
├── chapters/           # 챕터 마크다운
│   ├── ch01-intro.md
│   ├── ch02-first-agent.md
│   └── ...
├── assets/             # SVG 인포그래픽
│   ├── infographic-ch01-overview.svg
│   └── ...
├── output/
│   ├── pdf/            # PDF 결과물
│   └── web/            # 웹 뷰어
└── outline.md          # 목차/명세 (book-planner 산출물)
```

## 워크플로우

### Phase 1: 목차 설계
- **에이전트**: `book-planner`
- **입력**: 책 주제, 대상 독자, 요구사항
- **출력**: `book/outline.md` (목차 + 챕터별 명세)
- **검증**: 사용자가 목차를 확인하고 승인

### Phase 2: 챕터 집필
- **에이전트**: `chapter-writer`
- **입력**: `book/outline.md`의 챕터별 명세
- **출력**: `book/chapters/ch{NN}-{slug}.md`
- **방식**: 한 챕터씩 순차 집필
- **검증**: 각 챕터 파일이 챕터 구조를 따르는지 확인

### Phase 3: 리뷰 루프 (생성-검증)
- **에이전트**: `book-editor` → `chapter-writer`
- **입력**: 완성된 챕터
- **프로세스**:
  1. `book-editor`가 챕터 리뷰
  2. CRITICAL 이슈가 있으면 `chapter-writer`에게 수정 요청
  3. 수정본을 `book-editor`가 재리뷰
  4. CRITICAL 이슈 0개일 때 승인
- **검증**: 모든 챕터가 편집자 승인을 받음

### Phase 4: 인포그래픽 생성
- **에이전트**: `infographic-creator`
- **입력**: 각 챕터에서 시각화가 필요한 개념
- **출력**: `book/assets/infographic-ch{NN}-{slug}.svg`
- **방식**: 챕터별 병렬 생성 가능
- **검증**: SVG 파일이 유효하고 챕터에서 참조됨

### Phase 5: 출판
- **에이전트**: `book-publisher`
- **입력**: 완성된 챕터들 + SVG 에셋
- **출력**:
  - `book/output/pdf/harness-engineering-guide.pdf`
  - `book/output/web/index.html`
- **검증**: PDF가 정상 생성되고 웹 뷰어에서 페이지 넘김 동작

## 실행 방법

오케스트레이터(사용자 또는 메인 Claude)가 각 Phase를 순서대로 실행:

```
Phase 1: Agent tool → book-planner → outline.md 생성 → 사용자 승인
Phase 2: Agent tool → chapter-writer → 챕터 1개씩 순차 집필
Phase 3: Agent tool → book-editor → 리뷰 → chapter-writer → 수정 (반복)
Phase 4: Agent tool → infographic-creator → SVG 생성
Phase 5: Agent tool → book-publisher → PDF + 웹 뷰어
```

각 Phase 완료 후 사용자 확인을 받고 다음 Phase로 진행.
