# 출처

vstack은 세 곳에서 파일을 가져온다. 무엇을 어떻게 가져오는지의 정본은 [`upstream.json`](upstream.json)이다. 이 문서는 사람이 읽는 설명과 고친 내용의 기록이다.

## 출처 목록

| 출처 | 버전 | 커밋 | 라이선스 |
| --- | --- | --- | --- |
| [pstack](https://github.com/cursor/plugins/tree/main/pstack) | 0.15.36 | `6b0300214a09fd6029cfb7077043125758cd1fd2` | MIT, Copyright (c) 2026 Lauren Tan. [`licenses/pstack-LICENSE`](licenses/pstack-LICENSE) |
| mattpocock-skills(claude-plugins-official) | 1.3.1 | `49dd158d1076134a641b33efb035946536778336` | MIT, Copyright (c) 2026 Matt Pocock. [`licenses/mattpocock-skills-LICENSE`](licenses/mattpocock-skills-LICENSE) |
| [agent-orchestra](https://github.com/vananaHope/agent-orchestra) | 0.20.0 | `c62be33381a546fb7127088795a83378cfe35371` | MIT, Copyright (c) 2026 vananaHope. [`licenses/agent-orchestra-LICENSE`](licenses/agent-orchestra-LICENSE) |

- pstack 커밋은 가져올 때 받은 `cursor/plugins` 저장소의 HEAD다.
- mattpocock-skills와 agent-orchestra 커밋은 설치 기록(`installed_plugins.json`의 `gitCommitSha`)에서 읽었다. 설치 캐시 내용이 그 커밋과 같은지는 해시로 검증하지 않았다.

## 가져오는 방식

| 방식 | 뜻 |
| --- | --- |
| `verbatim` | 원문 그대로. 고치지 않는다. 안의 다른 스킬·원칙 언급과 링크는 가리키는 곳이 vstack 안이든 밖이든 출처 참조이며, 작업자는 따라가지 않는다([reference-policy.md](skills/v-mode/contracts/reference-policy.md)) |
| `adapted` | 복사한 뒤 고친다. 고친 내용은 아래 "고친 내용"에 적는다. 실행 경로라서 검사 대상이다: 경로는 표준 형태로 바꾸고(링크 또는 `<vstack>/` 경로, [FORMAT.md](skills/v-mode/recipes/FORMAT.md) "실행 경로 표기"), 남는 스킬 이름은 vstack 스킬이어야 하며, 특정 런타임의 스킬 도구 문장은 없앤다. 원본이 가리키던 파일은 가져오거나 `dropped`에 이유와 함께 적는다 |
| `extracted` | 원문의 일부만 떼어 새 파일로 만든다. 원본이 가리키던 파일 가운데 가져오지 않는 것은 `dropped`에 적는다 |
| `moved` | vstack이 이어받는다. 원본 저장소는 아카이브한다 |

## 단계별 가져올 것

| 단계 | 출처 | 원본 | vstack | 방식 |
| --- | --- | --- | --- | --- |
| 2 | pstack | `skills/principle-*`(24개) | `skills/principle-*` | verbatim |
| 2 | pstack | `skills/create-verification-skill` | 같음 | adapted |
| 2 | mattpocock-skills | `skills/engineering/diagnosing-bugs` | `skills/diagnosing-bugs` | adapted(`agents/openai.yaml` 제외) |
| 2 | mattpocock-skills | `skills/engineering/tdd` | `skills/tdd` | adapted(`agents/openai.yaml` 제외) |
| 2 | mattpocock-skills | `skills/engineering/codebase-design/SKILL.md`의 용어 부분 | `skills/tdd/references/codebase-vocabulary.md` | extracted(`DEEPENING.md`, `DESIGN-IT-TWICE.md`는 dropped) |
| 3 | agent-orchestra | `skills/orchestrate-issues`, `skills/check-limits`, `skills/configure` | 같음 | moved |

## 고친 내용

`adapted`·`extracted`·`moved` 파일을 고칠 때마다 여기에 적는다. 원본과의 차이는 `diff --strip-trailing-cr <원본> <vstack 파일>`로 다시 볼 수 있다. 아래 줄 번호는 원본 기준이다.

### 공통(2단계 adapted 3개)

- frontmatter에 `disable-model-invocation: true`(create-verification-skill은 원래 있음). 기존 mattpocock-skills 플러그인이 설치된 동안 같은 이름의 스킬이 두 벌 생겨 모델이 어느 쪽을 부를지 알 수 없기 때문이다. vstack에서는 레시피가 경로로 읽는다.
- 본문 첫머리에 "vstack 사본이며 고친 내용은 UPSTREAM.md에 있다"는 한 줄과, "관리자"가 누구인지 적은 한 줄.

### `skills/diagnosing-bugs/SKILL.md`(mattpocock-skills 1.3.1 `engineering/diagnosing-bugs`)

| 원본 줄 | 바꾼 것 | 이유 |
| --- | --- | --- |
| 3 | description을 "vstack 레시피가 경로로 읽는다"로 | 모델이 스스로 부르지 않는다 |
| 16, 55 | "ask the user" → "ask the manager" | 작업자는 사용자에게 직접 묻지 않는다(worker-contract) |
| 35 | HITL 스크립트를 링크로, 무인 작업자는 직접 돌려 기다리지 않고 사본을 준비해 `막힘`으로 관리자에게 요청 | 실행 경로 표기, 스크립트가 `read`로 입력을 기다려 무인 실행에서 멈춘다 |
| 64 | HITL 스크립트를 링크로, "관리자를 통해" | 실행 경로 표기 |
| 74 | "the **user** described" → "the **ticket** describes" | 증상의 출처는 티켓이다 |
| 98 | 가설 목록을 "사용자에게 보여 주기" → "적어 두고 답을 기다리지 않기" | 작업자는 사용자와 대화하지 않는다. 원문도 "막지 말라"고 했다 |
| 138 | "commit / PR message" → "commit message and the completion report" | 작업자는 PR을 만들지 않는다 |

`scripts/hitl-loop.template.sh`는 원문 그대로. `agents/openai.yaml`은 제외.

### `skills/tdd/SKILL.md`(mattpocock-skills 1.3.1 `engineering/tdd`)

| 원본 줄 | 바꾼 것 | 이유 |
| --- | --- | --- |
| 3 | description을 "vstack 레시피가 경로로 읽는다"로 | 모델이 스스로 부르지 않는다 |
| 22 | seam을 "사용자와 확인" → "작업과 함께 온다(배정 전에 사용자와 합의됨)" | seam은 정렬 단계에서 정한다(priority.md 충돌표) |
| 24 | "Ask: …" → "명명된 seam이 동작에 닿지 않으면 관리자에게 묻고 기다린다. 스스로 새 seam을 고르지 않는다" | 같은 이유 |
| 26 | "call the Skill tool with codebase-design" → `references/codebase-vocabulary.md` 링크 | 특정 런타임의 도구 문장 제거, 용어 부분만 추출해 둠 |
| 38 | "`code-review` skill" → "vstack's cross-review" | vstack에 없는 스킬. 검토는 orchestra 교차 검토가 맡는다 |

`tests.md`, `mocking.md`는 원문 그대로. `agents/openai.yaml`은 제외.

### `skills/tdd/references/codebase-vocabulary.md`(mattpocock-skills 1.3.1 `engineering/codebase-design/SKILL.md`에서 추출)

- 가져온 절: Glossary, Principles, Relationships, Rejected framings(원문 그대로)와 첫 문단의 목표 문장.
- 뺀 절: Deep vs shallow 그림, Designing for testability(`mocking.md`와 겹침), Going deeper.
- `dropped`: `DEEPENING.md`(용어 참고 범위 밖), `DESIGN-IT-TWICE.md`(하위 에이전트 3개 이상을 띄우는 절차라 작업자 계약과 맞지 않음).

### `skills/create-verification-skill/SKILL.md`(pstack 0.15.36)

| 원본 줄 | 바꾼 것 | 이유 |
| --- | --- | --- |
| 3 | `/create-verification-skill` → `/vstack:create-verification-skill` | Claude Code의 플러그인 명령 접두사 |
| 9, 25, 36 | `.cursor/skills/` → `.claude/skills/` | Claude Code 경로(pstack `docs/harness/claude-code.md` "Paths") |
| 13 | "ask the user" → "ask the manager" | 작업자 계약 |
| 30 | Evidence 끝에 "산출물 폴더를 호출하는 쪽이 정할 수 있게(인자나 환경 변수), 기본값을 명시. vstack 작업자는 명세의 증거 폴더를 넘긴다" | 생성되는 verify 스킬이 vstack 증거 폴더(evidence.md)에 쓸 수 있어야 한다 |
| 42~44 | "5. Offer the maintenance loop"(`/maintain-verification-skill` 안내) → "5. Report the map's coverage"(지도 범위를 보고, 지도가 낡으면 관리자에게 알림) | maintain-verification-skill은 첫 버전에서 뺐다(하위 에이전트 병렬 실행, PR 생성) |

`references/feature-map-example/`은 원문 그대로.

### agent-orchestra 옮기기(3-1단계, 0.20.0 `c62be33`)

`skills/orchestrate-issues`, `skills/check-limits`, `skills/configure`를 옮겼다. 원본은 `plugins/marketplaces/agent-orchestra` 클론(깨끗한 체크아웃)이다. 여기서부터 vstack이 소유한다.

| 파일 | 바꾼 것 | 이유 |
| --- | --- | --- |
| `orchestrate-issues/SKILL.md`, `check-limits/SKILL.md` | frontmatter에 `disable-model-invocation: true`, description 앞에 "vstack 사본", 머리말 한 줄 | 기존 agent-orchestra가 설치된 동안 이름이 겹친다. 사용자가 `/vstack:...`로 실행한다 |
| 모든 md | `/agent-orchestra:configure` → `/vstack:configure` | 플러그인 이름 |
| `orchestrate-issues/SKILL.md`, `limits.md`, `codex-fast.md`, `setup.md` | "`check-limits` 스킬로" → `[check-limits](../check-limits/SKILL.md)` 링크 | 스킬 이름 호출 대신 경로 |
| `orchestrate-issues/SKILL.md`, `check-limits/SKILL.md` | "스킬 폴더"를 `Base directory`만으로 정하지 않고, 경로로 읽는 경우 "이 SKILL.md가 있는 폴더" | v-mode·레시피가 파일을 경로로 읽어 따를 수 있다 |
| `configure/SKILL.md` | 인라인 경로 → `[setup.md](../orchestrate-issues/setup.md)` | 실행 경로 표기 |
| 작업 파일 경로 전부 | `.local/orchestration/<작업 이름>/`, `assign-log.md`, `*/review*.md`, `tracker-state.md` → `.local/vstack/...` | state-and-rollback.md "위치": 기존 관리자가 자동으로 읽지 않게. 설정 파일(`settings.md`)과 `common-findings.md`는 두 쪽이 함께 쓰므로 그대로 |
| `orchestrate-issues/SKILL.md` 1단계 | 기존 `.local/orchestration/*/state.md`에 끝나지 않은 작업이 있으면 이어받지 않고 알린다 | state-and-rollback.md "소유권" |
| `orchestrate-issues/SKILL.md`, `spec-check.md` | 결과 파일 `spec-check.md`를 `.local/vstack/<작업 이름>/spec-check.md` 전체 경로로 | 절차 문서 `spec-check.md`와 이름이 같아 구분이 안 됐다 |
| `orchestrate-issues/backends/orca.md` | 다시 씀. Orca 1.4.253 안내와 `--help` 기준: `check --wait` 대기·터미널 키 입력·`--terminal` 재사용 대신 턴 끝내기·`send`·`reply --id`, `worker-retain` → `worker-keep-open`, 명세는 `--spec-file`, 정지 확인(종료 코드 0 + `stop_unknown` 없음 + `worker-show`에서 settled, `processAction`만으로 판정하지 않음), 정리(시도별 터미널 상태표, 새 worktree 작업자는 기본으로 열린 채 남음, `released` 전에는 worktree 삭제 금지), `worktree create --branch`, `worktree rm --delete-branch`(지금은 기본으로 브랜치를 남김, squash·rebase 병합 브랜치는 `-D`로 강제 삭제하지 않고 보고), `.codex/` 제외는 `--git-path info/exclude` | 옛 방식은 지금 Orca 안내가 금지하거나 동작이 바뀌었다 |
| `orchestrate-issues/SKILL.md` 6단계 6 | 터미널 확인을 실행 환경 문서의 **정리** 완료로, 브랜치를 지울 수 없으면 남기고 알림 | Orca 정리 의미가 바뀌었다 |
| `orchestrate-issues/setup.md` | AGENTS.md 한 줄의 "agent-orchestra plugin" → "shared by the vstack and agent-orchestra plugins" | 설정을 두 플러그인이 함께 쓴다 |

`backends/herdr.md`, 나머지 문서, `scripts/*.py`는 그대로 옮겼다. herdr는 vstack 첫 버전에서 검증하지 않았다.

### vstack 계약 연결(3-2단계)

| 파일 | 바꾼 것 |
| --- | --- |
| `orchestrate-issues/vstack.md`(새 파일) | 단계별 계약 적용을 한곳에 모음: 레시피 없는 작업, 배정 전(입력 검사·시도·역할 자격·보관 준비·명세), 완료 보고 보관, 보고 없이 멈춤, 검토 보고 처리(실패·막힘·무효 증거), 교차 검토 배정, 대상이 바뀌면 재검증, 병합 관문, 사람이 병합, 그만둘 때, UI 다듬기 제외, worktree 지우기 전 정산, PR 본문 |
| `orchestrate-issues/SKILL.md` | 단계마다 vstack.md를 가리키는 연결, 실행 환경 표에 **정지**, `state.md`에 `병합 대기`와 계약 형식, 4단계 `관리자` 검토 제외, 6단계 병합 명령에 관문과 `--match-head-commit`, worktree 지우기 전 확인 넷(정산 추가), "그만둬"·UI 다듬기 경로 |
| `orchestrate-issues/task-template.md` | "vstack 계약" 절(역할·작업 종류·시도 ID·대상·계약·레시피·후보 원칙·맡은 수용 기준·seam·준비·증거 폴더·권한), 증거는 커밋하지 않고 증거 폴더에, 완료 보고 항목 |
| `orchestrate-issues/review-template.md` | "vstack 계약" 절(scope review, 대상 확인, 검토 범위, scratch, 권한), "파일 수정 금지·흔적 금지·화면은 사람 몫" → 역할별 권한과 실창 잠금·막힘, 수용 기준 판정표, 재검토를 새 대상의 `review` 시도로, "재실행 전용(rerun-only)" 양식 |
| `orchestrate-issues/tiers.md` | 검토 목록의 `관리자` 건너뜀, "구현자"를 변경 작성자로 읽고 역할 자격 확인, 관리자 확인은 검토 결론이 아님 |
| `orchestrate-issues/fixes.md` | 수정 명세에 계약 절과 필수 수용 기준 전부, 수정 뒤 항상 rev `review` 시도(사소 수정 포함), 완료 기준 |
| `orchestrate-issues/opencode.md` | rebase 검증에 재검증(range-diff가 같아도) |
| `orchestrate-issues/pr-template.md` | "검증"에 수용 기준별 판정과 증거 위치 |
| `orchestrate-issues/ui-polish.md` | 첫 버전에서 하지 않는다는 머리말 |

계약 쪽: 시도 ID의 가운데 8자를 dispatch ID에서 관리자가 띄우기 전에 정하는 세션 키로 바꿈(dispatch ID는 띄운 뒤에야 생겨 명세의 증거 폴더에 넣을 수 없었다). evidence.md·archive.md·state-and-rollback.md.

## 출처 참조

verbatim 원문 안에서 vstack에 없는 스킬을 가리키는 곳은 [`skills/v-mode/contracts/reference-policy.md`](skills/v-mode/contracts/reference-policy.md)에 있다. 이 파일은 스크립트가 만든다.

## 갱신 절차

1. 출처의 새 버전을 받는다(pstack은 `cursor/plugins` 저장소, 나머지는 플러그인 캐시나 원격 저장소). 처음 가져올 때와 verbatim 갱신은 `node scripts/import.mjs --stage <n> --source …`로 한다. verbatim은 덮어쓰고, adapted는 파일이 없을 때만 원본으로 깔아 둔다(있으면 손대지 않는다). `--check`는 verbatim이 원본과 다른지만 본다.
2. 받은 체크아웃이 깨끗한지(`git status --short`가 빈 출력) 확인한다.
3. `upstream.json`의 각 항목을 이전 커밋과 비교한다. 경로는 출처의 `path`와 항목의 `from`을 이은 것이다. 예: pstack은 `git diff <이전 커밋> <새 커밋> -- pstack/skills/principle-prove-it-works`.
4. `verbatim`은 원문을 그대로 덮는다. `adapted`·`extracted`는 바뀐 부분을 보고 "고친 내용"을 다시 적용한다.
5. `upstream.json`과 이 문서의 버전·커밋을 고친다.
6. 출처 참조를 다시 만들고 검사한다. `--source` 경로는 각 출처의 저장소 루트다(pstack은 `cursor/plugins` 체크아웃, mattpocock-skills는 플러그인 캐시의 버전 폴더).

   ```
   node scripts/collect-references.mjs --source pstack=<cursor/plugins>
   node scripts/check-links.mjs --stage <현재 단계> --source pstack=<cursor/plugins> --source mattpocock-skills=<mattpocock-skills>
   ```

   `check-links`는 `--source`를 받으면 `adapted`·`extracted` 항목의 원본이 가리키던 파일이 모두 들어왔는지(`NOT CARRIED`)도 본다.

7. vstack 버전(`.claude-plugin/plugin.json`)을 올린다.
