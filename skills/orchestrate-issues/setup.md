# 프로젝트 설정 만들기

프로젝트 설정은 지휘(이 스킬)와 v-mode 맡기기([delegate.md](../v-mode/delegate.md) "프로젝트 설정")가 함께 읽는다. 메인 저장소에 프로젝트 설정이 없을 때 한 번 한다. 훑기는 짧게 끝내고(몇 초 안의 파일·`gh` 조회만) 바로 설정 창을 띄운다. 끝나면 SKILL.md로 돌아가 사용자가 원래 요청한 일을 이어 간다.

`configure` 스킬로 이미 있는 설정을 고칠 때도 이 문서를 쓴다. 그때는 사용자가 고른 창만 띄우고, 선택지는 2단계의 "선택지 표시"대로 단다.

## 설정 위치

두 곳 중 한 곳에 둔다. 스킬은 앞쪽부터 찾는다.

| 위치 | 언제 |
| --- | --- |
| `docs/agents/orchestration.md`, `docs/agents/common-findings.md` | 저장소에 커밋해 팀과 다른 컴퓨터에서 같이 쓸 때 |
| `.local/orchestration/settings.md`, `.local/orchestration/common-findings.md` | 회사 저장소처럼 개인 도구 설정을 커밋하지 않을 때 |

어느 쪽인지는 2단계 첫 창에서 묻는다. 이 문서와 SKILL.md에서 "프로젝트 설정", `common-findings.md`는 고른 위치의 파일이다.

`.local/orchestration/`은 agent-orchestra 때의 폴더 이름이다. 이미 있는 프로젝트의 설정을 옮기지 않으려고 설정 위치로는 그대로 쓴다. vstack의 작업 파일은 `.local/vstack/`에 둔다.

## 절이 빠졌을 때

플러그인이 커지면서 양식(3단계)에 절이 늘었다. 예전에 만든 설정에는 절이 빠져 있을 수 있고, 그때 스킬은 아래 값으로 움직인다. `(선택)` 절은 빠져도 알리지 않는다.

| 절 | 빠졌을 때 | 채우는 창(2단계) | 맡기기도 읽음 |
| --- | --- | --- | --- |
| 이슈 저장소 | GitHub 이슈, [trackers.md](trackers.md)의 GitHub 기본값 | 기본, 이슈 | 아니오 |
| 병합 | 기본 브랜치 `main`, `자동`, `merge` | 기본 | 아니오 |
| 작성 규칙 | `AGENTS.md`의 작성 규칙, 그것도 없으면 한국어·서명 줄 넣음 | 작성 규칙 | 예 |
| 스펙과 먼저 읽을 문서 | `README`와 `AGENTS.md`만 | 훑기 | 예 |
| 구현 제약 | 없음. 명세에 구현 제약이 빠진다 | 훑기 | 예 |
| 환경 준비 | 없음. 작업자가 저장소 문서에서 찾는다 | 명령 | 예 |
| 테스트 | 없음. 작업자가 저장소 문서에서 찾는다 | 명령 | 예 |
| UI 작업 | 없음. UI도 등급 목록으로 맡긴다 | 작업 나누기 | 아니오 |
| 간단한 구현에서 뺄 영역 | 없음. 등급 기준만으로 정한다 | 작업 나누기 | 아니오 |
| 등급별 배치 | [tiers.md](tiers.md)의 기본 배치. 표에 검토 목록 열, `UI` 줄, 2차 의견 줄이 없으면 그 부분만 기본값 | 등급별 배치, 검토 배치 | 아니오 |
| 명세 점검 (선택) | `claude`(관리자와 같은 모델). Codex는 쓰지 않는다([spec-check.md](spec-check.md) "누구에게") | 명세 점검 | 아니오 |
| 추가 완료 조건 | 없음 | 명령 | 예 |
| 실창 검사 (선택) | 실창 잠금을 명세에 넣지 않는다 | 작업 나누기 | 예 |
| 확인 자료 (선택) | 없음 | 훑기 | 예 |

"맡기기도 읽음"이 "예"인 절은 맡기기가 빠졌을 때 저장소를 훑어 정한다(delegate.md "프로젝트 설정"). "아니오"인 절과 `Codex fast`는 지휘에서만 쓴다.

"훑기"는 창으로 묻지 않고 1단계에서 찾은 내용으로 채운다는 뜻이다. 채운 내용은 마지막 확인 창의 초안에서 보여 준다.

## 1. 훑기

사용자에게 묻기 전에 저장소로 알 수 있는 것을 먼저 모은다: `README`, `AGENTS.md`/`CLAUDE.md`, `docs/`, 용어집이나 ADR이 있으면 그것, 패키지·빌드 설정, 테스트 폴더, CI 설정, 기본 브랜치(`git symbolic-ref refs/remotes/origin/HEAD`), PR 규칙(브랜치 보호, CODEOWNERS, PR 양식), 이슈 흔적(`gh label list`, `gh issue list --limit 10 --json number,title,labels,milestone,body`, `.scratch/`나 `docs/`의 이슈 같은 md 파일).

## 2. 설정 창으로 묻기

`AskUserQuestion` 창으로 묻는다. 훑어서 알아낸 값은 첫 선택지에 "(추천)"을 붙여 넣고, 근거(찾은 파일·라벨)를 설명에 적는다. 사용자는 고르기만 하거나 "Other"로 직접 쓴다. 한 창에 질문 4개까지이므로 아래 차례로 나눠 띄우고, 앞 답에 따라 다음 질문을 고른다.

**선택지 표시**: 처음 만들 때는 위처럼 추천 값에 "(추천)"을 붙인다. 이미 있는 설정을 고칠 때는 다음을 따른다.
- 지금 값과 추천 값이 같으면 선택지 하나로 내고, "(현재·추천)"을 붙여 맨 앞에 둔다.
- 다르면 지금 값 "(현재)"를 맨 앞에, 추천 값 "(추천)"을 그다음에 둔다. 추천 근거는 설명에 적는다.
- 절이 빠져 지금 값이 없으면 "(현재)" 선택지를 내지 않는다. 대신 질문에 "지금은 기본값 <값>을 쓰는 중"이라고 적는다(위 "절이 빠졌을 때").

1. **기본**: 설정 위치(`docs/agents/` / `.local/`), 이슈 저장소 종류(GitHub 이슈 / 로컬 md / 아티팩트), 병합 방식(`자동`: 관리자가 PR·병합까지 / `지시`: 검토 통과 뒤 내 지시를 기다림), 기본 브랜치.
   - `자동`이면 병합 방법(`merge`/`squash`/`rebase`)을 다음 창에 더한다. 저장소 설정(`gh repo view --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed`)에서 허용된 것만 낸다.
2. **이슈**: 종류에 맞춰 맡길 이슈 표시(찾은 라벨·마일스톤·상태 값), 선행 관계, 완료 기준 위치. 로컬 md면 이슈 파일 위치와 상태 표시를, 아티팩트면 URL을 묻는다(URL은 "Other"로 받는다).
3. **작업 나누기**: UI 작업 범위(찾은 프런트엔드 폴더, 여러 개 고름), 간단한 구현에서 뺄 영역(여러 개 고름), 실창 검사가 필요한 앱인지.
4. **등급별 배치**([tiers.md](tiers.md)): 질문 3개. `light`·`standard`·`hard` 구현 목록을 하나씩 묻는다. `max`는 관리자 몫이라 묻지 않는다.
   - 선택지는 목록 묶음이다. 첫 선택지는 [tiers.md](tiers.md)의 기본 배치에 "(추천)"을 붙인다. 나머지는 강도를 한 단계 올리거나 내린 묶음, 순서를 바꾼 묶음으로 채운다. 예: `light`면 "codex@medium → claude (추천)", "codex@low → claude", "claude → codex@medium".
   - 설명에 지금 기본 모델을 적는다: Codex는 `$CODEX_HOME/config.toml`(없으면 `~/.codex/config.toml`. Orca는 계정마다 `CODEX_HOME`을 따로 둔다)의 `model`·`model_reasoning_effort`.
   - 다른 모델이나 강도는 "Other"로 `에이전트[:모델][@강도]` 표기를 받는다.
   - 답을 받으면 세 목록의 표기를 모두 `python -I <스킬 폴더>/scripts/check_tiers.py <표기...>`로 본다. 경고가 나오면 막지 않고, 경고와 가까운 이름을 질문에 적어 그 등급만 다시 묻는다. 첫 선택지는 가까운 이름으로 고친 표기 "(추천)", 둘째는 입력한 그대로다.
5. **검토 배치**([tiers.md](tiers.md) "검토자 고르기"): 질문 4개. `light`·`standard`·`hard` 검토 목록을 하나씩 묻고, 마지막으로 2차 의견을 묻는다. `UI` 검토 목록은 "UI 작업" 절이 있을 때만 묻고, 그때는 질문이 5개가 되므로 2차 의견을 다음 창으로 넘긴다.
   - 첫 선택지는 [tiers.md](tiers.md)의 기본 검토 목록에 "(추천)"을 붙인다. 나머지는 Codex를 앞에 둔 묶음(Claude 몫을 줄임), 강도를 한 단계 올린 묶음으로 채운다. 예: `standard`면 "claude → codex (추천)", "codex@high → claude", "claude@high → codex@high".
   - 설명에 바로 앞 창에서 고른 구현 목록을 적고, 구현자와 같은 계열은 건너뛴다는 규칙을 한 줄로 적는다.
   - 2차 의견 선택지: "같은 계열 검토일 때만 (추천)", "standard 이상", "모든 검토".
   - 답을 받으면 검토 목록 표기도 `check_tiers.py`로 본다(`관리자`는 통과).
6. **명세 점검**([spec-check.md](spec-check.md)): 질문 2개. 점검자 목록 `codex[:모델][@강도]` → `claude[:모델][@강도]`의 두 항목을 하나씩 묻는다. 순서는 이대로이고, 바꾸려면 "Other"나 마지막 확인 창에서 목록을 직접 쓴다.
   - Codex 점검 모델: "쓰지 않음 (추천)"(기본값과 같다), "`codex@medium`", "`codex@low`". 설명에 `$CODEX_HOME/config.toml`(없으면 `~/.codex/config.toml`)의 `model`·`model_reasoning_effort`를 적는다. 다른 모델은 "Other"로 `모델[@강도]`(예: `gpt-6-astra@medium`)를 받는다. `codex` 명령이 없으면 이 질문을 빼고 "쓰지 않음"으로 둔다.
   - Claude 점검 모델(앞 점검자를 쓰지 않거나 못 쓸 때): "관리자와 같은 모델 (추천)", "sonnet", "haiku", "opus". 강도는 "Other"로 `모델@강도`(예: `sonnet@high`)를 받는다.
   - 답으로 목록을 만든다. 쓰지 않는 항목은 뺀다. 예: `codex@medium → claude:sonnet`, Codex를 쓰지 않으면 `claude:sonnet`. 모델을 설정·관리자 그대로 두면 모델을 뺀다(`claude`). Codex 표기는 `check_tiers.py`로 본다(4와 같이 처리).
7. **명령**: 환경 준비 명령, 관련 테스트 명령, 추가 완료 조건. 찾은 명령(`package.json` scripts, `Makefile`, 설정 스크립트)을 선택지로 낸다.
8. **작성 규칙**: 메시지 언어(최근 커밋 메시지·PR에서 찾은 언어를 추천), PR 서명 줄("🤖 Generated with Claude Code")을 넣을지. `AGENTS.md`에 이미 정해져 있으면 이 창은 건너뛴다.

아티팩트는 URL을 받은 뒤 `Artifact` `read`와 `ArtifactData` `list`로 컬렉션·필드를 보고(권한 확인은 [trackers.md](trackers.md) "아티팩트"), 필드 대응과 상태 값을 한 창 더 띄워 확인한다. 데이터베이스가 없거나 편집 권한이 없으면 그 사실을 알리고 읽기 전용으로 할지 같은 창에서 묻는다. 로컬 md도 파일 몇 개를 열어 본 뒤 같은 식으로 확인하고, 파일이 Git에서 제외됐는지 `git check-ignore`로 본다([trackers.md](trackers.md) "로컬 md").

초안을 다 채우면 마지막 창을 띄운다. 질문은 "이대로 저장할까요?", 선택지는 "저장" / "고칠 곳 있음"이다. "저장" 선택지의 `preview`에 초안 전체를 넣는다. "고칠 곳 있음"이면 어느 절인지 묻고 그 절의 창만 다시 띄운다.

## 3. 쓰기

먼저 `.local/`을 Git에서 뺀다. 설정을 커밋하는 프로젝트면 `.gitignore`에, 아니면 `.git/info/exclude`에 더한다(저장소 파일을 바꾸지 않는다). 이미 빠져 있으면(`git check-ignore .local/x`) 건너뛴다.

아래 양식으로 프로젝트 설정을 쓴다. 절 이름은 SKILL.md와 양식들이 그대로 가리키므로 바꾸지 않는다. 해당 없는 선택 절은 지운다. 각 절은 명세에 그대로 옮겨질 문장으로 쓴다.

```markdown
# 프로젝트 설정

vstack 플러그인의 맡기기와 지휘(`orchestrate-issues`)가 읽는 이 프로젝트의 설정이다. 이슈 저장소, 병합, UI 작업, 간단한 구현에서 뺄 영역, 등급별 배치, Codex fast, 명세 점검은 지휘만 읽는다.

## 이슈 저장소

- 종류: <GitHub 이슈 / 로컬 md / 아티팩트>
- <GitHub면 선택: 진행 중 라벨 `<이름>`>
- 맡길 이슈: <GitHub: 라벨 `<이름>` / 마일스톤 `<이름>` / 열린 이슈 전부(제외 라벨). 로컬 md·아티팩트: 상태 값 `<값>`>
- 선행 관계: <GitHub 이슈 의존 관계 / 본문의 `Blocked by` 줄 / 필드 `<이름>` / 없음>
- 완료 기준: <본문의 체크리스트 / 본문의 "<절 이름>" 절 / 필드 `<이름>` / 따로 없음(관리자가 명세에 뽑아 적음)>
- <로컬 md면: 위치, 작업 이름 규칙, 상태 표시와 값(맡길·진행 중·끝), 댓글 위치>
- <아티팩트면: URL, 컬렉션, 필드 대응(ID·제목·본문·상태·선행 관계·완료 기준·댓글), 상태 값, 작업 이름 접두어>

## 병합

- 기본 브랜치: <main / develop 등>
- 병합 방식: <자동 / 지시>
- 병합 방법: <merge / squash / rebase. 자동일 때만>
- <PR 규칙: 필요한 리뷰어, PR 양식, 제목 규칙 등. 프로젝트 양식이 있으면 pr-template.md보다 그것을 따른다.>
- <자동인 프로젝트에서도 사용자 승인을 받을 이슈나 조건이 있으면>

## 작성 규칙

- 메시지 언어: <한국어 / 영어 등. 명세·커밋·PR·이슈 댓글 모두>
- PR 서명 줄: <넣음 / 뺌>

## 스펙과 먼저 읽을 문서

<전체 스펙이 있으면 그 위치, 작업 전 반드시 읽을 문서 목록과 각 문서가 무엇인지. 없으면 README와 AGENTS.md만 적는다.>

## 구현 제약

<기술 스택(ADR), 아키텍처 규칙(어디에 도메인 규칙을 두는지 등), 용어 규칙, 테스트 작성 원칙>

## 환경 준비

<새 worktree에서 의존성을 준비하는 명령>

## 테스트

<관련 테스트만 돌리는 명령과 예시. 병렬 실행 옵션이 있으면 함께. 전체 테스트 명령(관리자가 Release 직전에 돌림)>

## UI 작업

<이 프로젝트에서 Claude가 구현할 UI 작업의 범위: 폴더, 화면, 대화상자, 문구 등>

## 간단한 구현에서 뺄 영역

<`light`·`standard`로 맡기지 않을 위험한 영역: 공용 계약, DB 버전, 플랫폼별 코드 등. 이 영역을 건드리는 일은 `hard`다.>

## 등급별 배치

| 등급 | 구현 목록(앞부터) | 검토 목록(앞부터) |
| --- | --- | --- |
| `light` | <예: codex@medium → claude> | <예: 관리자 → claude → codex> |
| `standard` | <예: codex@medium → claude> | <예: claude → codex> |
| `hard` | <예: codex@high → claude@high> | <예: claude → codex> |
| `UI` | claude | <예: codex → claude. "UI 작업" 절이 없으면 줄을 지운다> |

- 2차 의견: <같은 계열 검토일 때만 / standard 이상 / 모든 검토>

## Codex fast (선택)

<Codex fast를 켜고 끄는 기준. 비우면 codex-fast.md의 기본값(짧은 창 문턱 60%, 긴 창 상한 75%, 긴 창 속도 하한 40%·여유 15%p(초기화 24시간 전부터는 보지 않음), 동시 상한 3명, 검토·병합 직전·임계 경로·묶음의 마지막·사용자가 기다림이면 켬)을 쓴다. 바꿀 항목만 적는다.>

## 명세 점검 (선택)

- 점검자(앞부터): <예: codex@medium → claude:sonnet. 쓸 수 있는 에이전트는 codex, claude. 모델을 빼면 Codex는 config.toml의 모델, Claude는 관리자와 같은 모델>

## 추가 완료 조건

<특정 종류의 이슈에 붙는 완료 조건. 예: 프런트엔드 변경은 lint·typecheck·build 통과, 기본 창 크기 스크린샷, 데이터 개수별 배치 확인. 어느 이슈에 붙는지 함께 적는다.>

## 실창 검사 (선택)

<앱이 실제 창을 띄우는 경우만. 데스크톱 없이 스크린샷 찍는 방법, 실창이 꼭 필요한 검사 목록>

## 확인 자료 (선택)

<사람·검토자가 실제 동작을 재현할 때 쓸 자료의 위치와 내용>
```

`common-findings.md`도 같은 위치에 만든다. 처음에는 제목과 다음 문단만 둔다: "교차 검토 보고서(`.local/vstack/*/review*.md`)에서 반복해 나온 지적을 유형별로 모은다. 구현자는 제출 전에 이 목록으로 스스로 점검하고, 검토자는 이 목록을 먼저 확인한다. 새 유형이 두 번 이상 나오면 관리자가 먼저 lint·테스트로 막을 수 있는지 보고, 못 막는 것만 여기에 더한다. 유형마다 예시(이슈 표시)와 '점검' 한 줄을 둔다."

## 4. 연결하기

설정을 `docs/agents/`에 둔 프로젝트만 한다. `AGENTS.md`(없으면 `CLAUDE.md`)에 다음 한 줄을 더한다. 둘 다 없으면 건너뛴다(스킬은 설정 파일을 직접 읽는다).

```markdown
### Issue orchestration

Settings for the vstack plugin (delegation and the `orchestrate-issues` skill). See `docs/agents/orchestration.md` and `docs/agents/common-findings.md`.
```

## 5. 전제 확인

설정을 저장한 뒤에 한다(`configure`로 점검만 요청받았으면 이것만 한다). 설정 창이 먼저 뜨도록, 시간이 걸리거나 비용이 드는 확인(Codex 한도 측정)은 여기로 미뤘다. 맡기기와 지휘가 처음 쓰기 전에 필요한 것을 여기서 한데 본다. 항목마다 갖춤 / 빠짐(고치는 방법)을 한 줄로 사용자에게 알린다. 고치는 일은 하지 않는다. 설정은 그대로 둔다.

**지휘의 첫 실행으로 들어왔으면**([SKILL.md](SKILL.md) "가장 먼저") 아래에서 "지휘 전제"라고 적은 항목이 모두 갖춰진 뒤에 원래 요청한 지휘를 시작한다. 빠졌으면 알리고 기다린다. 나머지 항목과, `configure`로 들어왔거나 점검만 요청받은 경우는 알리기만 한다.

- **Orca**: `orca orchestration run-current`가 답한다(Orca 안에서 실행 중). 맡기기와 지휘 모두 Orca가 있어야 한다(명령은 실행 환경 문서 [backends/orca.md](backends/orca.md)).
- **GitHub**(지휘 전제): 코드 저장소가 GitHub(회사 GitHub Enterprise 포함)이면 `gh`가 그 호스트에 로그인돼 있다(`gh auth status`).
- **작업자 도구**(지휘 전제): 실행 환경 문서([SKILL.md](SKILL.md) "실행 환경")가 요구하는 명령과 `codex` 명령이 있다. 맡기기는 `claude`, `codex`만 쓴다.
- **한도**(지휘 전제): [check-limits](../check-limits/SKILL.md)로 잰 Codex와 Claude가 둘 다 `unknown`이 아니다. `unknown`이면 그 스킬이 알려 주는 원인을 사용자에게 전한다.
- **작업 파일 무시**: `git check-ignore -q .local/x`가 0이다(`.local/vstack/`, `.local/vstack-delegate/`가 커밋되지 않는다). 아니면 3단계 "쓰기"의 첫 문단("`.local/`을 Git에서 뺀다")대로 하라고 알린다.
- **mattpocock 설정**: `docs/agents/issue-tracker.md`가 있거나 `AGENTS.md`/`CLAUDE.md`에 `## Agent skills` 절이 있다. 없으면 지휘의 정렬 단계(`to-spec`, `to-tickets`)가 이슈 저장소를 모르므로, 사용자에게 `/mattpocock-skills:setup-matt-pocock-skills`를 실행하라고 안내한다. vstack이 그 일을 대신하지 않는다.
- **검증 수단**: "테스트" 절의 명령(없으면 1단계에서 찾은 테스트 명령)이 저장소에 있다. 없으면 맡기기와 지휘의 수용 기준을 정하기 어렵다고 알린다(v-mode 고정 규칙 7이 그때 검증 수단부터 만든다).
- **실창 잠금**: "실창 검사" 절이 있으면 `~/.agent-orchestra/bin/desktop_lock.py`가 있다. 없으면 `python -I <이 스킬 폴더>/scripts/desktop_lock.py install`을 안내한다([desktop.md](desktop.md) "고정 경로").


**완료 기준**: 설정과 `common-findings.md`가 고른 위치에 있고, 사용자가 마지막 창에서 "저장"을 골랐고, 전제 확인 결과를 항목마다 알렸다. 저장소 파일을 바꿨다면 커밋은 사용자가 원할 때 한다.
