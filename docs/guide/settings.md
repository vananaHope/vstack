# 프로젝트 설정

맡기기와 지휘가 함께 읽는 프로젝트마다의 설정이다. `/vstack:configure`로 만들고 고친다. 양식과 각 절의 뜻은 [setup.md](../../skills/orchestrate-issues/setup.md)가 정본이고, 여기서는 어디에 두는지, 어떤 절이 있는지, 빠졌을 때 무엇을 쓰는지만 모은다.

## 위치

두 곳 가운데 한 곳에 둔다. 앞쪽부터 찾는다.

| 위치 | 언제 |
| --- | --- |
| `docs/agents/orchestration.md`, `docs/agents/common-findings.md` | 저장소에 커밋해 다른 컴퓨터에서도 같이 쓸 때 |
| `.local/orchestration/settings.md`, `.local/orchestration/common-findings.md` | 회사 저장소처럼 개인 도구 설정을 커밋하지 않을 때 |

`.local/orchestration/`은 agent-orchestra 때의 이름이다. 경로를 바꾸지 않았다([ADR 0007](../adr/0007-keep-agent-orchestra-legacy-paths.md)). vstack의 작업 파일은 `.local/vstack/`(지휘)과 `.local/vstack-delegate/`(맡기기)에 따로 둔다.

## 절과 기본값

예전에 만든 설정에는 절이 빠져 있을 수 있다. 빠진 절은 아래 값으로 움직인다. "맡기기도 읽음"이 "예"인 절은 맡기기가 빠졌을 때 저장소를 훑어 정한다.

| 절 | 빠졌을 때 | 맡기기도 읽음 |
| --- | --- | --- |
| 이슈 저장소 | GitHub 이슈 | 아니오 |
| 병합 | 기본 브랜치 `main`, `자동`, `merge`, 병합 위치 `원격` | 아니오 |
| 작성 규칙 | `AGENTS.md`의 작성 규칙, 그것도 없으면 한국어·서명 줄 넣음 | 예 |
| 스펙과 먼저 읽을 문서 | `README`와 `AGENTS.md`만 | 예 |
| 구현 제약 | 없음 | 예 |
| 환경 준비 | 없음. 작업자가 저장소 문서에서 찾는다 | 예 |
| 테스트 | 없음. 작업자가 저장소 문서에서 찾는다 | 예 |
| UI 작업 | 없음. UI도 등급 목록으로 맡긴다 | 아니오 |
| 간단한 구현에서 뺄 영역 | 없음. 등급 기준만으로 정한다 | 아니오 |
| 등급별 배치 | [tiers.md](../../skills/orchestrate-issues/tiers.md)의 기본 배치 | 아니오 |
| Codex fast (선택) | [codex-fast.md](../../skills/orchestrate-issues/codex-fast.md)의 기본값 | 아니오 |
| 명세 점검 (선택) | `claude`(관리자와 같은 모델) | 아니오 |
| 추가 완료 조건 | 없음 | 예 |
| 실창 검사 (선택) | 실창 잠금을 명세에 넣지 않는다 | 예 |
| 확인 자료 (선택) | 없음 | 예 |

## 병합 절 예시

```
## 병합

- 기본 브랜치: main
- 병합 방식: 자동
- 병합 방법: squash
- 병합 위치: 로컬
```

병합 방식·방법·위치의 뜻은 [orchestrate.md](orchestrate.md) "병합 설정"에 있다.

## 전제 확인

`/vstack:configure`는 저장한 뒤 다음을 점검해 항목마다 알린다. 고치는 일은 하지 않는다. "지휘 전제" 항목이 빠졌으면 지휘는 시작하지 않는다.

- Orca 안에서 실행 중인가(맡기기와 지휘 모두).
- `gh`가 로그인돼 있는가(지휘 전제).
- `claude`, `codex` 명령이 있는가(지휘 전제).
- Codex와 Claude의 한도를 잴 수 있는가(지휘 전제).
- `.local/`이 Git에서 빠졌는가.
- mattpocock 설정(`docs/agents/issue-tracker.md` 또는 `AGENTS.md`의 `## Agent skills` 절)이 있는가. 없으면 `/mattpocock-skills:setup-matt-pocock-skills`를 안내한다.
- 테스트 명령 같은 검증 수단이 있는가.
- "실창 검사" 절이 있으면 실창 잠금 스크립트가 있는가.

설정을 고치지 않고 점검만 하려면 `/vstack:configure`에 "점검만 해 줘"라고 말한다.
