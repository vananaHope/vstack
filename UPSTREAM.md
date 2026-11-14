# 출처

vstack은 세 곳에서 파일을 가져온다. 무엇을 어떻게 가져오는지의 정본은 [`upstream.json`](upstream.json)이다. 이 문서는 사람이 읽는 설명과 고친 내용의 기록이다.

## 출처 목록

| 출처 | 버전 | 커밋 | 라이선스 |
| --- | --- | --- | --- |
| [pstack](https://github.com/cursor/plugins/tree/main/pstack) | 0.15.36 | `6b0300214a09fd6029cfb7077043125758cd1fd2` | MIT, Copyright (c) 2026 Lauren Tan. [`licenses/pstack-LICENSE`](licenses/pstack-LICENSE) |
| mattpocock-skills(claude-plugins-official) | 1.3.1 | `49dd158d1076134a641b33efb035946536778336` | MIT, Copyright (c) 2026 Matt Pocock. [`licenses/mattpocock-skills-LICENSE`](licenses/mattpocock-skills-LICENSE) |
| [agent-orchestra](https://github.com/vananaHope/agent-orchestra)(아카이브된 원본, 2026-11-14) | 0.20.0 | `c62be33381a546fb7127088795a83378cfe35371` | MIT, Copyright (c) 2026 vananaHope. [`licenses/agent-orchestra-LICENSE`](licenses/agent-orchestra-LICENSE) |

- pstack 커밋은 가져올 때 받은 `cursor/plugins` 저장소의 HEAD다.
- mattpocock-skills와 agent-orchestra 커밋은 설치 기록(`installed_plugins.json`의 `gitCommitSha`)에서 읽었다. 설치 캐시 내용이 그 커밋과 같은지는 해시로 검증하지 않았다.
- agent-orchestra는 아카이브된 원본이다(2026-11-14, vstack 0.20.0). 옮겨 온 파일은 vstack이 소유하고, 원본과 다시 대조하지 않는다. 그래서 `check-links`의 closure 검사는 `moved` 항목을 보지 않고, `--source agent-orchestra`가 필요 없다.

## 가져오는 방식

| 방식 | 뜻 |
| --- | --- |
| `verbatim` | 원문 그대로. 고치지 않는다. 안의 다른 스킬·원칙 언급과 링크는 가리키는 곳이 vstack 안이든 밖이든 출처 참조이며, 작업자는 따라가지 않는다([reference-policy.md](skills/v-mode/contracts/reference-policy.md)) |
| `adapted` | 복사한 뒤 고친다. 고친 내용은 아래 "고친 내용"에 적는다. 실행 경로라서 검사 대상이다: 경로는 표준 형태로 바꾸고(링크 또는 `<vstack>/` 경로, [FORMAT.md](skills/v-mode/recipes/FORMAT.md) "실행 경로 표기"), 남는 스킬 이름은 vstack 스킬이어야 하며, 특정 런타임의 스킬 도구 문장은 없앤다. 원본이 가리키던 파일은 가져오거나 `dropped`에 이유와 함께 적는다 |
| `extracted` | 원문의 일부만 떼어 새 파일로 만든다. 원본이 가리키던 파일 가운데 가져오지 않는 것은 `dropped`에 적는다 |
| `moved` | vstack이 이어받아 소유한다. 원본 저장소는 아카이브한다. 원본과 대조하지 않으므로 closure 검사 대상이 아니다 |

**pstack에서 가져오기 전에 mattpocock-skills와 겹치는지 본다.** vstack은 mattpocock-skills를 의존성으로 함께 설치한다. 같은 역할의 스킬이 두 벌 생기면 무엇을 써야 할지 헷갈리고, pstack 사본은 원본이 바뀔 때마다 다시 맞춰야 한다. 그래서 pstack에서 가져오는 것(스킬, 플레이북을 바탕으로 만드는 레시피)마다 먼저 한다.

1. 설치된 mattpocock-skills의 스킬 목록에서 역할이 맞닿는 것을 고른다.
2. 그 스킬의 원문을 끝까지 읽어 비교한다. 설명 한 줄로 판단하지 않는다.
3. 아래 "mattpocock-skills와의 겹침" 표에 판정을 적는다.

| 판정 | 뜻 | 하는 일 |
| --- | --- | --- |
| 겹치지 않음 | 묻는 것이나 방법이 다르다 | 가져온다 |
| 겹침 | 같은 일을 한다 | 가져오지 않는다. mattpocock 것을 쓰고, 라우터가 그 명령을 안내한다(`upstream.json`의 `user_commands`) |
| 일부 겹침 | 맞닿는 부분이 있다 | 무엇이 겹치고 무엇이 다른지, 그래도 가져오는 이유를 적는다. 겹치는 부분은 mattpocock 것을 가리킬 수 있는지 먼저 본다 |

## 단계별 가져올 것

| 단계 | 출처 | 원본 | vstack | 방식 |
| --- | --- | --- | --- | --- |
| 2 | pstack | `skills/principle-*`(24개) | `skills/principle-*` | verbatim |
| 2 | pstack | `skills/create-verification-skill` | 같음 | adapted |
| 2 | mattpocock-skills | `skills/engineering/diagnosing-bugs` | `skills/diagnosing-bugs` | adapted(`agents/openai.yaml` 제외) |
| 2 | mattpocock-skills | `skills/engineering/tdd` | `skills/tdd` | adapted(`agents/openai.yaml` 제외) |
| 2 | mattpocock-skills | `skills/engineering/codebase-design/SKILL.md`의 용어 부분 | `skills/tdd/references/codebase-vocabulary.md` | extracted(`DEEPENING.md`, `DESIGN-IT-TWICE.md`는 dropped) |
| 3 | agent-orchestra | `skills/orchestrate-issues`, `skills/check-limits`, `skills/configure` | 같음 | moved |
| 7 | pstack | `skills/blast-radius` | 같음 | adapted |
| 7 | pstack | `skills/maintain-verification-skill` | 같음 | adapted |
| 7 | pstack | `skills/benchmark-checklist` | 같음 | adapted |
| 7 | pstack | `skills/ketchup` | 같음 | adapted |

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
| 42~44 | "5. Offer the maintenance loop"(`/maintain-verification-skill` 안내) → "5. Report the map's coverage"(지도 범위를 보고, 지도가 낡으면 관리자에게 알림). 7단계(2026-11-14)에 maintain-verification-skill을 가져오면서 "첫 버전에는 없다" 문장을 그 사본을 가리키는 링크로 바꿨다. 지도를 지나가며 고치지 말고 관리자에게 알리는 문장은 그대로다 | 고치는 일은 따로 맡긴다(`delegate.md` "검증 스킬 점검") |

`references/feature-map-example/`은 원문 그대로.

### `skills/maintain-verification-skill/SKILL.md`(pstack 0.15.36, 7단계)

원본에는 딸린 파일이 없다. 맡기기의 구현자가 경로로 읽는다(`skills/v-mode/delegate.md` "검증 스킬 점검"). 원본의 판정(clean / changed / blocked), 편집 범위, 단계 0~6과 실행 확인의 세 불변식은 그대로 두었다.

| 원본 줄 | 바꾼 것 | 이유 |
| --- | --- | --- |
| 3 | "at most one PR" → "at most one branch", `/vstack:maintain-verification-skill` 추가 | 작업자는 PR을 만들지 않는다. Claude Code의 플러그인 명령 접두사 |
| 6 뒤 | "vstack copy of pstack …"과 "the manager"가 누구인지 한 줄 | 다른 adapted 사본과 같다 |
| 9, 25 | `/create-verification-skill` → vstack 사본 링크 | vstack 안의 실행 경로로 |
| 15~16 | clean의 "No branch, no PR" → "No commits", changed의 "one PR ships" → 작업 브랜치의 커밋, 반영은 관리자가 정하고 push·PR을 하지 않는다 | 맡기기의 권한(작업 브랜치에서 커밋까지) |
| 25 | `.cursor/skills/verify-*/` → `.claude/skills/verify-*/`, "ask which one" → "ask the manager which one" | Claude Code 경로, 작업자는 관리자에게 묻는다 |
| 29 | "launched concurrently" → 한 번에 셋까지, `vstack:explorer`, 없으면 직접 읽음 | `skills/v-mode/subagents.md` |
| 33 | "The coordinator owns all driving" → "You own all driving" | 이 스킬을 따르는 것은 구현자 한 명이다 |
| 37 | changed의 "one PR of proven corrections" → 작업 브랜치에 커밋. clean의 "no PR" → 커밋 없음. blocked의 "no PR" → 증명한 수정만 커밋하고 증명하지 못한 수정은 되돌려 diff로 보고(작업 트리를 깨끗하게). 어느 결과든 다룬 기능, `verified-unreachable` 전제, 확인된 어긋남, 고친 실행 수단, 찾은 제품 고장을 보고 | 맡기기의 권한과 관리자의 수용 기준(`delegate.md` "검증 스킬 점검"). blocked에서 이미 증명한 수정을 버리지 않으면서 관리자의 확인(깨끗한 작업 트리)과 사용자의 선택(이어 가기, 증명된 것만 받기, 그만두기)으로 이어지게 했다 |
| 39 | scratch → 저장소 밖(OS 임시 폴더) | 작업 트리를 깨끗하게 둔다 |

### `skills/ketchup/SKILL.md`(pstack 0.15.36, 7단계)

원본에는 딸린 파일이 없다. v-mode "그 밖의 요청"이 경로로 읽고, 바로 갈래에서 관리자가 따른다(읽기 전용). 모으기·답 쓰기·그림 규칙과 낱말 수는 그대로다.

| 원본 줄 | 바꾼 것 | 이유 |
| --- | --- | --- |
| 3 | `/vstack:ketchup` 추가 | Claude Code의 플러그인 명령 접두사 |
| 6 뒤 | "vstack copy of pstack …"과 바로 갈래에서 관리자가 따른다는 한 줄 | 다른 adapted 사본과 같다 |
| 11 | "Use `/bro`'s voice, not its task" → "Use a plain voice"(뒤의 말투 설명은 그대로), 그리고 v-mode "답 쓰기"(맥락 먼저, 용어집, 고정 규칙 2의 표시)를 따른다는 문장 | `bro`는 vstack에 없다. v-mode의 답 규칙과 어긋나지 않게 |
| 15 | 모으는 곳에 vstack의 맡기기 기록, 지휘 작업 상태, Orca 받은 편지함을 더함. 기록은 메인 저장소([main-repo.md](skills/v-mode/main-repo.md))에서 읽음 | 관리자가 작업자의 결과와 기록이 기다리는 것을 따라잡게. `/vstack:ketchup`을 홈 레포에서 바로 불러도 제품 저장소의 기록을 읽게 |
| 37, 43 | `/visualize` 언급 → "a chart" | `visualize`는 vstack에 없다 |

### `skills/benchmark-checklist/SKILL.md`(pstack 0.15.36, 7단계)

원본에는 딸린 파일이 없다. 성능 레시피(`skills/v-mode/recipes/perf.md`)와 그 검토 명세가 경로로 읽는다. 질문 1~7과 "Report"의 앞 세 항목은 그대로다(마지막 항목은 아래 34줄).

| 원본 줄 | 바꾼 것 | 이유 |
| --- | --- | --- |
| 3 | description 끝에 "vstack recipes (perf) read this file by path" | 다른 adapted 사본과 같다 |
| 6 뒤 | "vstack copy of pstack …"과 "the manager"가 누구인지 한 줄 | 같다 |
| 17 | `uptime`·`nproc`에 Windows에서 쓸 명령을 괄호로 더함 | 사용자의 환경이 Windows다 |
| 34 | "Keep a PR body to one primary number, per the **Opening a PR** playbook" → 머리 숫자는 하나, 실행 기록과 범위와 한계 요인은 작업이 정한 곳(맡기기면 완료 보고) | vstack에 그 플레이북이 없고, 작업자는 PR을 쓰지 않는다 |
| 38~39 | Perf issue·Hillclimb 플레이북 언급 → vstack 성능 레시피 링크 하나 | Hillclimb는 가져오지 않았다 |

### `skills/v-mode/recipes/perf.md`(vstack이 씀, pstack 0.15.36 `poteto-mode/playbooks/perf-issue.md`에서, 7단계)

성능 개선 레시피다. 맡기기 갈래에서만 쓴다. 원문 `playbooks/perf-issue.md`(26줄)를 읽었다. 전체 검수(#20)의 확정대로 vstack의 `diagnosing-bugs` 사본(Phase 4 "Perf branch")과 `benchmark-checklist` 위에 성능 주문 목록을 얹었다.

| 원본 | vstack에서 |
| --- | --- |
| 고치는 일마다 측정을 붙이고 소스 읽기로 측정을 대신하지 않는다 | 가져옴. 머리말과 단계 2 |
| 기준 추적을 control skill로 잡고 benchmark-checklist로 검증한다 | 가져옴. 단계 1. 측정 명령은 맡기기 전에 정하고, 없으면 고정 규칙 7(검증 수단 먼저) |
| `how`로 가설을 세우고, 돌려 보기 전에 한계를 주장하지 않는다 | 일부 가져옴. 한계 요인은 프로파일로 찾는다(단계 2). `how`는 vstack에서 조사 레시피라 작업자가 부르지 않는다 |
| 성능 주문 일곱(하지 않는다 … 싸게 한다), 앞의 것이 목표를 채우면 멈춘다 | 가져옴. 단계 3 |
| 함수 경계를 넘으면 `architect` 먼저, 구현을 하위 에이전트에게 위임, 모델 지정, diff 검토 | 가져오지 않음. 구현은 맡기기의 구현자가 하고 검토는 Codex 검토자가 한다. 공용 인터페이스나 예정 쓰기 영역 밖에 닿으면 묻는다 |
| `sequence-verifiable-units`로 시도마다 검증 | 가져옴. 단계 4와 후보 원칙 |
| 산출물을 파싱해 비교하고, "판단 못 함"이나 엉뚱한 경로는 통과가 아니다 | 가져옴. 단계 5(결론 넷, 목표를 못 채우면 그대로 보고) |
| PR에 측정을 인용, Opening a PR | 가져오지 않음. 측정은 완료 보고에 싣고 반영은 관리자가 사용자에게 묻는다 |
| 지속 개선은 Hillclimb | 가져오지 않음. "쓰지 않을 때"에 여러 번에 걸친 지표 올리기를 적었다 |
| Reply: 기준, 수정 뒤 숫자, 차이, 산출물 경로 | 가져옴. "완료 보고"에 두 중앙값의 차이와 실행마다의 원시 출력(하네스가 파일을 남기면 그 경로)을 적게 했다 |
| (원문에 없음) 판정 절차 | vstack이 더함. 원문의 "흔들림보다 큰가"(benchmark-checklist 5)를 맡길 때 고정하는 판정식으로 만들었다(입력 7: 비교 기준 `C`, 횟수, 하네스 통계 또는 범위가 겹치지 않음, 다시 재기 한 번). 관리자와 검토자가 같은 판정을 다시 하고, 기준이 움직이면 다른 변경의 효과를 이 변경의 개선으로 치지 않게 하려는 것이다. 목표 미달은 `--outcome failed`와 사용자 선택(더 시도, 목표 바꾸기, 그만두기)으로 잇는다 |

분류는 `own`이다(원문 문장을 복사하지 않았다).

### `skills/blast-radius/SKILL.md`(pstack 0.15.36, 7단계)

원본에는 딸린 파일이 없다. 원본이 이름으로 가리키던 스킬(`how`, `why`, `arena`, `unslop`)은 vstack에 없어서, 그 문장을 지우거나 같은 뜻의 문장으로 바꿨다.

| 원본 줄 | 바꾼 것 | 이유 |
| --- | --- | --- |
| 3 | description에 `/vstack:blast-radius` 추가 | Claude Code의 플러그인 명령 접두사 |
| 6 뒤 | "vstack copy of pstack …" 한 줄 | 다른 adapted 사본과 같다 |
| 11 | "Companion to `how` and `why` …" → 두 스킬의 이름 없이 "코드가 무엇을 하는지, 왜 그런 모양인지와는 다른 질문이다" | `how`·`why`는 vstack에 없다 |
| 33 | "Use `why` step 2 to pull the PR and commits." → 그 단계의 명령(`git log`, `gh pr view`)을 직접 적고, vstack 작업이면 대상이 `git diff <B>...<H>`라고 적음 | `why`는 vstack에 없다 |
| 36 | "Same rules as `why`." 삭제(뒤의 규칙 문장은 그대로) | 같음 |
| 37 | 끝에 "스크립트는 아래 'Where the proof lives'가 말한 곳에 두고 제품 트리에 두지 않는다" | 검토자는 제품 소스·테스트를 고치지 않는다(작업자 계약) |
| 38 | "run it as an `arena`. Ask more than one model …" → "한 번 읽은 것으로는 부족하다고 보고하고 가장 자신 없는 부분을 적는다. 다른 계열의 두 번째 읽기는 관리자가 정한다. 스스로 다른 에이전트를 띄우지 않는다" | `arena`는 vstack에 없고, 작업자는 다른 작업자를 띄우지 않는다 |
| 43 | "If you couldn't prove it, write unproven." 뒤에 "돌려 보니 사실이 거짓이면(일부 조건에서만 거짓이어도) disproven이라고 쓰고 조건을 적고, 깨지는 것을 Risks에 적는다" | 평가에서 검토자가 "증명됨/증명 못 함" 둘뿐이라 반증된 경우의 표기를 스스로 만들었다 |
| 48 | "Write it through `unslop`" → "Write it plainly" | `unslop`은 vstack에 없다 |
| 48 뒤 | "Where the proof lives" 절 추가: vstack 작업이면 스크립트는 명세의 scratch, 명령과 출력은 증거 폴더 `process/`, 결과는 검토 보고서의 지적(증명 못 한 사실은 지적이나 사람이 확인할 항목). 5단계(실행 중인 앱)는 명세가 준 verify 스킬이나 준비 절차로만 띄우고, 실창이 뜨면 명세의 잠금 명령 안에서만. 작업 밖에서는 스크립트를 요청한 쪽이 정한 폴더(없으면 OS 임시 폴더)에 두고 앱 실행은 그 프로젝트의 안내를 따름 | 증거 계약과 역할별 권한에 맞춤 |
| 50 | Reply의 "either proven or marked unproven" → "proven, disproven, or unproven"으로, unproven은 증명도 반증도 못 한 경우라고 적음 | 43줄에 더한 disproven과 맞춤 |

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

`backends/herdr.md`, 나머지 문서, `scripts/*.py`는 그대로 옮겼다. herdr는 vstack 첫 버전에서 검증하지 않았고, 2026-11-14(0.20.1)에 `backends/herdr.md`를 지웠다(사용자가 herdr를 쓰지 않는다).

### agent-orchestra 은퇴(2026-11-14, vstack 0.20.0, #22)

agent-orchestra 플러그인을 지우고 원래 저장소를 아카이브하기로 하면서 옮긴 파일을 다시 고쳤다. 위 표의 일부를 되돌린다.

| 파일 | 바꾼 것 | 이유 |
| --- | --- | --- |
| `orchestrate-issues/SKILL.md`, `check-limits/SKILL.md` | description 앞의 "vstack 사본"과 "옮겨 온 사본" 머리말을 뺐다. `orchestrate-issues`의 머리말은 계약 문장만 남겼다 | 이름이 겹치는 플러그인이 없다 |
| `check-limits/SKILL.md` | `disable-model-invocation: true`를 뺐다 | 읽기 전용 측정이라 모델이 불러도 된다. "한도 확인해 줘"처럼 이름으로 부르던 습관을 받는다. 지휘(`orchestrate-issues`)와 설정(`configure`)은 그대로 사용자가 실행한다 |
| `orchestrate-issues/setup.md` | AGENTS.md 한 줄을 "of the vstack plugin"으로 | 설정을 쓰는 플러그인이 vstack 하나다 |
| `orchestrate-issues/SKILL.md` 1단계 | "기존 agent-orchestra의" → "agent-orchestra 때의 작업 파일" | 옛 작업을 이어받지 않는 규칙은 남긴다 |
| `orchestrate-issues/vstack.md`, `ui-polish.md`, `backends/orca.md` | agent-orchestra로 돌아가라는 안내를 뺐다. 출처 문장은 "(아카이브됨)"을 붙여 기록으로 남겼다 | 돌아갈 곳이 없다. 레시피가 없는 일은 맡기기로 하거나 레시피를 먼저 만든다 |

`upstream.json`: `user_commands`에서 `agent-orchestra:configure`를 뺐다(실행 경로에서 그 명령을 안내하는 곳이 없다). agent-orchestra 출처에 `status: archived`와 날짜를 적었다. `check-links`의 closure 검사에서 `moved` 항목을 뺐다.

옛 경로 이름(`.local/orchestration/`, `~/.agent-orchestra/`, `check-limits/scripts/claude_limit.py`의 캐시 폴더 이름)은 그대로 둔다(ADR 0007).

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

### `skills/v-mode/subagents.md`(pstack 0.15.36 `skills/poteto-mode/SKILL.md`의 "Subagents" 절에서 일부, 7단계)

vstack이 새로 쓴 파일이고, 아래 문장의 뜻을 pstack에서 가져왔다. 원문은 고정 커밋의 `https://raw.githubusercontent.com/cursor/plugins/6b0300214a09fd6029cfb7077043125758cd1fd2/pstack/skills/poteto-mode/SKILL.md`에서 2026-11-13에 받아 읽었다.

| 원본 줄 | 원본의 문장 | vstack에서 |
| --- | --- | --- |
| 100 | 서브에이전트의 일은 부른 쪽이 책임진다. diff를 직접 보고 자기 요약을 쓴다 | 가져옴. 읽기 전용 조사에 맞춰 "해당 파일과 줄을 직접 다시 읽는다"로 바꿈 |
| 96 | 내용을 붙여넣지 않고 파일 경로를 준다 | 가져옴 |
| 19 | 요청문마다 사용자의 목표를 다시 적는다 | 가져옴("Subagents" 절 밖의 줄이다) |
| 102 | 새 일은 새 서브에이전트에게 범위를 모아서 준다. 옮기기 비싼 상태가 있을 때만 이어 쓴다 | 앞 문장만 가져옴. 이어 쓰기 예외는 가져오지 않음(읽기 전용 조사에는 그런 상태가 없다) |
| 94 | 정해진 스킬(`how`, `why` 등)이 자기 서브에이전트 종류를 정하면 그것을 따른다 | 넓혀서 가져옴: 사용자가 실행한 스킬이 서브에이전트를 정하면 그 스킬을 따른다. 맡긴 작업자가 이것으로 제한을 풀지는 않는다 |
| 94 | 종류 `poteto-agent` | 가져오지 않음. vstack의 조사 에이전트 `vstack:explorer`를 쓴다(아래 `agents/explorer.md`) |
| 96, 98 | 역할별 모델과 `/setup-pstack`, 일에 맞춘 모델 강도 조절, 다른 계열 모델 | 가져오지 않음. Claude Code의 서브에이전트는 Claude 모델만 쓴다. 모델은 `sonnet` 하나이고, 다른 계열은 맡기기의 Codex 검토자로 얻는다 |
| 94 | 서브에이전트가 코드를 쓴다(code-writing delegates) | 가져오지 않음. 같은 worktree를 나눠 쓰므로 읽기 전용 조사만 맡긴다 |
| 96 | 백그라운드로 띄운다 | 가져오지 않음. Claude Code의 기본 동작이다 |

vstack이 더한 것: 누구에게 적용하는가(바로와 맡기기 갈래의 Claude. 2026-11-14 전에는 "한 세션 갈래"라고 불렀다. 계약 작업자와 Codex 검토자는 아님), 쓰는 때와 쓰지 않는 때, 맡기지 않는 일, 한 번에 셋까지, Orca 작업자를 띄우지 않는다.

분류: `upstream.json`에서는 레시피와 같은 `own`이다. 원문의 문장을 복사하지 않고 뜻만 가져와 한국어로 새로 썼기 때문이다(`extracted`는 원문의 일부를 떼어 파일로 만드는 방식이다). 계획(`docs/delegate-claude-plan.md`)은 `extracted`라고 적었는데 실행하면서 이렇게 바꿨다. 그래서 이 파일은 closure 검사와 import 갱신의 대상이 아니다. pstack 버전을 올릴 때는 `poteto-mode/SKILL.md`의 "Subagents" 절과 19줄이 바뀌었는지 위 표의 줄 번호로 손으로 비교한다.

### vstack 자체 레시피의 변경(`own`, 7단계)

레시피는 vstack이 쓴 것(`own`)이라 출처와 대조하지 않는다. 버전을 올린 변경만 적는다.

- `bug-fix@7`, `feature@3`, `refactoring@4`, `investigation@3`, `correct@2`, `perf@3`, `ui-polish@5`(2026-11-14, #22): 머리말의 `contract`를 `vstack-contract@4`로 올렸다. `ui-polish@5`는 출처 문장에 "agent-orchestra(아카이브됨)"도 적었다. 절차는 그대로다.
- `perf@2`(2026-11-14, #21, 처음 싣는 버전): 반영 전 초안 `perf@1`(시범에서 그 사본을 씀)에서 Codex 검토로 바꿨다. 비교 기준을 현재 확인 기준 `C`로, 판정 절차(횟수, 개선 판정식, 다시 재기)를 맡길 때 고정하게, 목표 미달과 판단 못 함은 누가 쟀든 사용자 선택으로 잇게 했다.
- `bug-fix@6`(2026-11-14, #21): "쓰지 않을 때"의 "성능 레시피(첫 버전 미포함)"를 `perf` 레시피로 바꿨다.
- `investigation@2`(2026-11-14, #21): "쓰지 않을 때"의 "성능은 레시피가 없다"를 `perf` 레시피로 바꿨다.
- `bug-fix@5`(2026-11-14): "쓰지 않을 때"의 "원인과 수정 위치가 이미 정해진 한 줄 수정: v-mode가 바로 처리한다"를 지웠다. 동작이 바뀌는 수정은 한 줄이어도 맡긴다(ADR 0010).
- `ui-polish@4`(2026-11-14, 전체 검수): 문구만 고쳤다(가져온 곳의 수, "새 다듬기" 6에서 7의 끝 이름을 가리키는 말).
- `ui-polish@3`(2026-11-14): 한 세션에서 이 대화가 직접 하던 레시피를 맡기기 갈래에서 작업자에게 맡기게 바꿨다. 묻는 것과 알리는 것, 항목 확정("새 다듬기" 0), 기준 인계, 사진 폴더(기록 폴더의 `shots/`). 바탕이 된 pstack `visual-parity`·`hillclimb`의 규칙(기준을 고치지 않음, 허용 오차 없음, 하나 바꾸고 전·후를 봄)은 그대로다.

### `skills/v-mode/recipes/investigation.md`(vstack이 씀, pstack 0.15.36 `poteto-mode/playbooks/investigation.md`·`how`·`why`에서, 7단계)

조사 레시피다. 바로 갈래에서 관리자가 따른다(읽기 전용, ADR 0010). 고정 커밋의 원문 `playbooks/investigation.md`(14줄), `how/SKILL.md`(36줄)와 `references/explainer-prompt.md`·`explorer-prompt.md`, `why/SKILL.md`(98줄)와 `references/epistemics.md`·`synthesizer-prompt.md`·`source-playbook.md`를 읽었다.

| 원본 | vstack에서 |
| --- | --- |
| 플레이북: 조사는 읽기 전용이고 근거가 붙은 설명이나 추천을 낸다. PR과 코드 변경이 없다. 변경으로 이어지면 사용자에게 돌려 갈래를 다시 고른다 | 가져옴. "바로 갈래에서 관리자가 따른다"와 단계 6 |
| 플레이북: 처리량 확인 줄(`throughput checkpoint`), `unslop` 스킬 적용 | 가져오지 않음. vstack에 없는 절차와 스킬이다. 답 쓰기는 v-mode "답 쓰기"를 따른다 |
| 플레이북: "확실해?"에는 근거와 자기 판단, 전제가 틀리면 반박 | 가져옴. 단계 5와 후보 원칙 `attack-the-premise` |
| `how`: 단순·복잡 나누기(애매하면 단순), 복잡하면 2~4 각도로 나눠 탐색자를 동시에 띄움 | 가져옴. 탐색자는 `vstack:explorer`(한 번에 셋까지, `subagents.md`). 받은 답은 관리자가 원본을 다시 읽어 확인한다 |
| `how`: 설명자(explainer) 에이전트가 쓰고 부르는 쪽은 거의 고치지 않고 내놓음, 역할마다 모델 지정 | 가져오지 않음. 설명은 관리자가 직접 쓴다. 조사 에이전트는 쓰기와 판단을 하지 않는다(`agents/explorer.md`) |
| `how`: 답의 절(개요, 핵심 개념, 동작, 위치, 함정), 맞지 않는 절은 뺌 | 가져옴. "답의 형식" |
| `why`: 대상이 모호하면 맥락으로 추측하고 해석을 밝힌 뒤 진행 | 가져옴. "입력" |
| `why`: 코드 기준점(`git blame -L`, `git log --follow`, PR 번호, `gh pr view`)을 먼저 만든다 | 가져옴. 단계 3.1. `-p`와 `--json` 필드 목록은 뺐다 |
| `why`: MCP를 찾아 근거 범주 일곱에 대응시키고, 범주마다 조사 에이전트를 하나씩 띄우고, 종합 에이전트가 씀 | 가져오지 않음. `vstack:explorer`는 셸과 MCP가 없다. 범주 목록만 가져와 관리자가 차례로 본다. 소스 이력과 이슈 저장소는 늘 보고, 나머지는 도구가 있을 때만 보고 없으면 "찾지 못함"으로 적는다(원본의 "건너뛰면 이유를 적는다") |
| `why`: 방어 코드면 사건 기록(`incident-postmortem`)을 더 찾는다 | 가져옴. 단계 3.2. 범주별 플레이북 파일(`sources/*.md`)은 가져오지 않았다 |
| `why` `epistemics.md`: 신뢰 단계 다섯(Direct, Supported, Inferred, Speculative, Unknown)과 말투, 코드를 의도의 근거로 쓰지 않음, 깔끔한 이유를 덧씌우지 않음, 근거 없음을 없음의 근거로 쓰지 않음, 사용자 가설을 후보로 봄, 끝내기 전 점검 | 가져옴. 단계 4. v-mode 고정 규칙 2의 (측정)/(추론)/(추측)과 대응시켰다. 원본은 이유를 찾는 조사의 틀이라 이유와 의도에 대한 주장에만 붙이고, 직접 읽은 동작 사실에는 고정 규칙 2만 쓴다 |
| `why` `epistemics.md`·`synthesizer-prompt.md`: 근거끼리 어긋나면 둘 다 인용해 보이고 한쪽을 고르지 않는다 | 가져옴. 단계 4와 "답의 형식" |
| `why`: 답의 절(질문 … 신뢰 요약), 찾아본 곳은 범주마다 한 줄 | 가져옴. "답의 형식" |
| `why`: 변경의 전 단계면 Preserve / Change / Avoid / Risk | 가져옴. 단계 6. 원본은 `why`에만 있지만 `how`로 끝난 조사에도 쓴다 |
| `why`: 최근 커밋 편향 | 가져옴. 단계 3.3 |
| `disable-model-invocation`, Cursor의 `readonly`·`generalPurpose`·`mcps/` | 가져오지 않음. Cursor 설정이다 |

분류는 `own`이다(원문 문장을 복사하지 않고 뜻만 한국어로 새로 썼다). 그래서 closure 검사와 import 갱신의 대상이 아니다. pstack 버전을 올릴 때는 위 원본 파일들이 바뀌었는지 손으로 비교한다.

### `skills/v-mode/recipes/correct.md`(vstack이 씀, pstack 0.15.36 `skills/correct/SKILL.md`에서, 7단계)

반복 실수 막기 레시피다. 맡기기 갈래에서만 쓴다(지휘에는 연결하지 않았다). 고정 커밋의 원문 `correct/SKILL.md`(32줄, 참조 파일 없음)를 읽었다.

| 원본 | vstack에서 |
| --- | --- |
| 에이전트는 연 파일만 보고, 가까운 예를 베끼고, 컴파일되는 가장 짧은 길을 간다고 가정한다 | 가져옴. 머리말 |
| 실수 유형 찾기: 최근 커밋, 되돌림, 검토 지적, 에이전트 지침 파일, 우회 주석을 읽고 묶는다. 두 번 나와야 유형이다 | 가져옴. 읽기 전용이라 관리자가 맡기기 전에 한다("입력" 1). vstack의 검토 보고서 위치와 `common-findings.md`, 대화에서 바로잡은 것을 더했다. 막을 유형은 사용자가 고른다 |
| 높은 층부터: 구조 → 타입(안 되면 고칠 곳을 말하는 lint·검사, 이미 흔하면 늘어날 때만 실패) → 동작 테스트(깨져도 통과하거나 내부에 묶인 테스트는 고치거나 지움) → 문서·규칙은 마지막에 판단만 | 가져옴. 단계 2. 구조 층은 예정 쓰기 영역 안에서만 하고, 여러 모듈의 소유를 옮기거나 공용 인터페이스를 바꾸면 묻고 멈춘다(맡기기는 한 단위의 일이다). 테스트를 지우는 것은 이 유형에 걸린 것만, 이유를 보고에 |
| 빈도 높은 유형부터 지금 고치고 유형마다 커밋 하나 | 가져옴. 한 맡기기에 셋까지 권한다(vstack이 정한 값) |
| 새 검사가 실제 과거 실수에서 실패함을 보인다 | 가져옴. 단계 7. 방법(유형을 커밋한 뒤 그 커밋을 OS 임시 폴더에 `git archive`로 풀고 재현점을 넣어 검사 명령을 돌림, 이력 검사는 범위로, 끝에 `H`로 한 번 더)은 vstack이 정했다. 관리자와 검토자가 같은 증명을 다시 한다(`delegate-review-spec.md` 6) |
| 로컬과 CI가 같은 명령을 돌린다 | 가져옴. 단계 3. CI 설정이 없으면 새로 만들지 않고 보고한다 |
| 예외는 그 줄에 이유, 만료일, 사람의 승인 | 가져옴. 단계 4. 승인은 관리자를 거쳐 사용자에게 묻는다 |
| 에이전트 지침 파일에 규칙과 막는 장치의 표를 둔다 | 일부 가져옴. 단계 5. 위치는 Git이 추적하는 파일이어야 하고, `common-findings.md`가 추적되면 그 파일, 아니면 사용자가 정한다("입력" 4). 원문과 달리 표를 두지 않는 선택을 허용했다: 회사 저장소처럼 지침 파일을 커밋하지 않는 곳이 있다. 그때 문서 층 유형은 쓰지 않고 보고만 한다 |
| 운영자가 바로잡을 때마다 그 실수를 고치고 규칙을 더한다. 이미 있던 규칙인데 막는 것이 없으면 반복이므로 같은 변경에서 높은 층으로 막는다. 일어날 수 없게 된 규칙은 지운다 | 일부 가져옴. 표를 고치는 규칙(단계 5)은 가져왔다. "바로잡힐 때마다" 이 일을 하는 것은 관리자가 스스로 시작하지 않는다. "언제"에 사용자가 같은 실수를 두 번 바로잡은 경우를 넣어 사용자가 이 레시피를 고르게 했다. 지휘에서는 기존 "반복 지적"이 이 일을 한다 |
| 답: 유형마다 근거, 고른 층, 더 높은 층이 안 된 이유 | 가져옴. "완료 보고" |
| `disable-model-invocation`, `/correct` 명령 | 가져오지 않음. v-mode의 레시피 표로 고른다 |

분류는 `own`이다(원문 문장을 복사하지 않고 뜻만 한국어로 새로 썼다). 지휘의 "반복 지적"(`skills/orchestrate-issues/SKILL.md`)에는 막는 층의 순서와 이 레시피를 가리키는 문장만 더했다. 지휘 절차는 바꾸지 않았다.

### `agents/explorer.md`(vstack이 새로 씀, 방식만 pstack 0.15.36 `agents/poteto-agent.md`에서, 7단계)

플러그인의 조사 에이전트 정의다. Claude Code에서 `vstack:explorer`로 부른다. 모델 기본값 `sonnet`, 도구는 `Read`·`Grep`·`Glob`만 준다(허용 목록이라 셸과 MCP 도구가 빠진다). 본문 규칙은 `skills/v-mode/subagents.md`의 "요청문"과 "답을 다루는 법"에서 에이전트 쪽 의무만 옮겼다. 부르는 쪽의 의무(원본을 직접 다시 읽기, 요청문에 목표와 볼 곳)는 `subagents.md`에 남겼다.

원문은 고정 커밋의 `pstack/agents/poteto-agent.md`(3줄 설명, 9줄 본문)를 읽었다.

| 원본 | vstack에서 |
| --- | --- |
| 설명에 쓸 때와 쓰지 않을 때를 적는다("Use for delegates, not as the runner") | 가져옴. 쓸 때(넓게 훑기, 독립 조사 여러 개, 긴 출력 요약)와 쓰지 않을 때(볼 곳을 앎, 몇 번이면 끝남, 코드 쓰기·검토·판단)를 설명에 적었다 |
| 새 일마다 새로 띄운다("Spawn a fresh ... for each new task") | 가져옴. 이어 쓰기 예외는 가져오지 않음(`subagents.md`와 같은 이유) |
| 코드를 쓰는 위임(code-writing and helper tasks) | 가져오지 않음. 읽기 전용 조사만 한다(ADR 0009) |
| 일하기 전에 `poteto-mode` `SKILL.md`를 끝까지 읽는다, 플러그인 폴더에서 그 파일을 찾는 절차 | 가져오지 않음. 조사 에이전트는 vstack의 절차를 따르지 않고, 지킬 규칙을 정의 본문에 둔다 |
| `is_background: true` | 가져오지 않음. Cursor의 필드다. Claude Code에서는 부르는 쪽이 정한다 |

mattpocock-skills 1.3.1에는 에이전트 정의가 없다(설치본에서 확인). 겹치지 않는다. 분류는 `own`이다(원문 문장을 복사하지 않았다).

## mattpocock-skills와의 겹침

pstack에서 가져온 것마다 "가져오는 방식"의 확인 결과를 적는다. 비교한 mattpocock-skills는 1.3.1(`49dd158`)이다.

| 가져온 것 | 비교한 mattpocock 스킬 | 판정 | 근거 |
| --- | --- | --- | --- |
| `skills/blast-radius` | `code-review` | 겹치지 않음 | `code-review`는 변경이 저장소의 코딩 규칙을 지켰는지와 명세대로 만들었는지를 하위 에이전트 둘이 읽어서 판정한다. 변경이 diff 밖에서 깨뜨리는 것을 찾거나 코드를 돌려 증명하는 단계가 없다. 이 확인은 가져온 뒤(2026-11-13)에 했다 |
| `skills/v-mode/recipes/ui-polish.md`(pstack `visual-parity`·`hillclimb`를 조합) | `prototype` | 겹치지 않음 | 스킬 38개의 원문에서 화면·스크린샷·다듬기를 다루는 것을 찾았고, 맞닿는 것은 `prototype`의 UI 갈래뿐이다. 그것은 버릴 시안 여러 개로 "어떤 모양이어야 하나"를 정하는 일이다. `ui-polish`는 이미 정해진 모양의 화면을 다듬고, 모양을 새로 정하는 일은 시작하지 않는다. 그 일이 `prototype`의 몫이다. 이 확인도 만든 뒤(2026-11-13)에 했다. `ui-polish@2`부터 v-mode가 그런 요청에 `prototype` 명령을 안내한다(`upstream.json`의 `user_commands`) |
| `skills/v-mode/recipes/investigation.md`(pstack 조사 플레이북·`how`·`why`) | `research`, `wayfinder`, `codebase-design`, `teach`, `diagnosing-bugs` | 일부 겹침 | `research`는 1차 자료(공식 문서, 소스 코드, 명세, 직접 API)에서 주장마다 출처를 따라가 백그라운드 에이전트가 Markdown 파일 하나로 남긴다. 대화에서 답하지 않는다. 소스 코드도 1차 자료라서 이 저장소의 코드를 출처를 달아 조사하는 일 자체는 겹친다. 다른 점은 셋이다: 조사 레시피는 대화에서 답하고 파일을 남기지 않는다, 어떻게 질문에 정해진 설명 절(개요 … 함정)이 있다, 왜 질문에 이력 조사(코드 기준점, 근거 범주, 신뢰 단계, 경쟁 가설)가 있다. 바깥 자료(라이브러리 문서, 명세)를 모아 남기는 일을 `research` 명령으로 안내하는 것은 vstack이 정한 나눔이다(원본 `research`에 그런 제한은 없다. `upstream.json`의 `user_commands`). `wayfinder`의 `research` 티켓은 작업 폴더 밖의 지식이 필요할 때 같은 스킬을 부른다. `codebase-design`은 모듈의 인터페이스와 seam을 설계하거나 고치는 어휘와 원칙이다. 조사 레시피의 "어디에 둘까"는 지금 구조를 읽어 대안을 비교해 추천하는 데서 멈추고, 새 인터페이스나 seam을 설계하는 일은 하지 않는다(그 일은 변경이라 갈래를 다시 고른다). `teach`는 여러 세션에 걸쳐 주제를 가르치는 작업 폴더를 만든다. 코드 설명과 겹치지 않는다. `diagnosing-bugs`는 결함의 원인을 찾는 진단이라 "쓰지 않을 때"로 보냈다. 코드가 왜 이렇게 됐는지를 이력에서 찾는 스킬과 신뢰 단계는 mattpocock에 없다(2026-11-14, 스킬 38개의 설명과 위 다섯의 원문을 읽음) |
| `skills/v-mode/recipes/correct.md`(pstack `correct`) | `retro`, `code-review`, `writing-for-agents`, `setup-ts-deep-modules` | 일부 겹침 | `retro`는 한 세션을 돌아보고 에이전트 환경의 개선 후보(길 찾기, 자동 검사, 코딩 규칙, 지침 파일, 도구 비용, 효과 없는 지시, 정보 접근)를 사용자에게 심각도순으로 보인다. 고치지 않는다. 기계적인 위반은 글 규칙보다 검사로 막고, 판단만 `CODING_STANDARDS.md`에 둔다는 생각이 `correct`와 같다. `correct`는 한 세션이 아니라 저장소의 이력에서 두 번 이상 나온 실수를 묶고, 높은 층부터 직접 막고, 과거 실수에서 검사가 실패함을 보인다. 그래서 "찾아서 제안"과 "막고 증명"으로 나뉜다. 사용자가 mattpocock-skills를 쓰면 `retro`로 후보를 찾고 이 레시피로 막을 수 있다. `code-review`는 변경이 코딩 규칙을 지켰는지 판정할 뿐 규칙을 장치로 바꾸지 않는다. `writing-for-agents`는 지침 문서를 쓰는 법이라 문서 층에서만 맞닿는다`setup-ts-deep-modules`(`in-progress` 폴더, 사용자 실행 전용)는 TypeScript 저장소에 dependency-cruiser로 패키지 경계 규칙을 설치하고, 저장소의 검사 명령에 연결하고, 일부러 넣은 잘못된 import에서 실패함을 보인 뒤 지침 파일에 포인터를 남긴다. 이 레시피의 구조·검사 층과 "실패를 보인다"가 겹친다. 다른 점: 그 스킬은 정해진 한 규칙(패키지 경계)을 정해진 도구로 설치하고 예제 위반으로 증명한다. 이 레시피는 저장소 이력에서 되풀이된 실수를 골라 그에 맞는 층을 정하고 실제 과거 실수로 증명한다. 막을 유형이 TypeScript 패키지 경계면 구현자가 그 스킬의 방식을 참고할 수 있지만 레시피가 부르지는 않는다(2026-11-14, 스킬 38개의 설명과 위 넷의 원문을 읽음) |
| `skills/ketchup` | `handoff`, `wait-what`, `chief-of-staff` | 겹치지 않음 | `handoff`는 다음 에이전트가 이어 받을 문서를 OS 임시 폴더에 쓴다. `wait-what`은 직전 메시지 하나를 맥락과 쉬운 말로 다시 쓴다(v-mode가 "다시 설명 요청"으로 안내한다). `chief-of-staff`는 하위 에이전트로 오래 가는 목표를 쫓는 운영 방식이다. 사용자의 마지막 메시지 뒤로 바뀐 것과 사용자만 정할 것(그 결정에 필요한 근거, 위험, 추천)을 한 답에 모으는 스킬은 mattpocock에 없다(2026-11-14, 위 셋의 원문을 읽음) |
| `skills/v-mode/recipes/perf.md`, `skills/benchmark-checklist` | `diagnosing-bugs` | 일부 겹침 | mattpocock `diagnosing-bugs`는 성능 회귀도 다룬다("Perf branch": 기준 측정 뒤 이분 탐색, 측정 먼저). vstack은 그 사본을 레시피가 경로로 읽고, 그 위에 측정 검증(benchmark-checklist의 질문 일곱, 교차 반복, 결론 넷)과 성능 주문 목록을 얹었다. 측정이 믿을 만한지 따지는 스킬과 회귀가 아닌 느림을 줄이는 절차는 mattpocock에 없다(스킬 38개의 원문에서 "benchmark", "profil"을 찾았고 `diagnosing-bugs`만 나옴, 2026-11-14) |
| `skills/maintain-verification-skill` | `retro`, `setup-pre-commit`, `diagnosing-bugs` | 겹치지 않음 | 프로젝트의 검증 스킬과 기능 지도를 앱에 맞춰 관리하는 스킬은 mattpocock-skills에 없다(스킬 38개의 원문에서 "feature map", "verification skill", "verify-"를 찾았고 나오지 않음). `retro`는 자동 검사가 연결되지 않았거나 깨진 것을 개선 후보로 보일 뿐이다. `setup-pre-commit`은 Husky·lint-staged 훅을 설치한다. `diagnosing-bugs`의 되먹임 고리는 버그 하나를 위한 것이다(2026-11-14, 위 셋의 원문을 읽음) |
| `skills/v-mode/subagents.md`(pstack `poteto-mode`의 "Subagents" 절에서 일부) | `code-review`, `codebase-design`(DESIGN-IT-TWICE), `implement-spec`, `ask-matt`(PHASE-BOUNDARIES), `research` | 일부 겹침 | 서브에이전트를 어떻게 쓸지 정하는 같은 역할의 스킬은 없다. 스킬마다 자기 서브에이전트를 따로 정할 뿐이다(두 검토 서브에이전트, 설계안 서브에이전트, 구현 서브에이전트, 혼자 돌릴 수 있는 일의 위임, 조사 맡기기). 같은 생각은 둘 있다: `implement-spec`의 "내용을 복제하지 말고 가리킨다", `code-review` 설명서(`docs/engineering/code-review.md`)의 "서브에이전트의 출력은 가설이지 증거가 아니다". 그래도 따로 두는 이유는, 맡긴 작업자가 레시피를 따르는 동안 지킬 규칙이 어디에도 없기 때문이다. 사용자가 mattpocock 스킬을 실행하면 그 스킬이 정한 서브에이전트를 따른다 |

이 규칙을 두기 전에 pstack에서 가져온 것(원칙 24개, `create-verification-skill`, 레시피 `bug-fix`·`feature`·`refactoring`의 바탕이 된 플레이북)은 이 표에 없다. 다시 손댈 때 확인해 채운다. 이와 따로, `tdd`와 `diagnosing-bugs`는 pstack이 아니라 mattpocock-skills에서 고쳐 가져온 사본이고 레시피가 그 사본을 쓴다.

앞으로 가져올 후보와 먼저 비교할 스킬: 프로토타입 ↔ `prototype`.

## 출처 참조

verbatim 원문 안에서 vstack에 없는 스킬을 가리키는 곳은 [`skills/v-mode/contracts/reference-policy.md`](skills/v-mode/contracts/reference-policy.md)에 있다. 이 파일은 스크립트가 만든다.

## 갱신 절차

0. pstack에서 새로 가져오는 것이면 "가져오는 방식"의 mattpocock-skills 겹침 확인을 먼저 하고 판정을 적는다.
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
