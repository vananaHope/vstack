# 다섯 번째 시범 계획: 기능·리팩토링·버그 수정 세 이슈 지휘

지금까지 네 시범은 모두 `bug-fix` 레시피였다. 6단계(PR #6·#8)에서 `feature@2`·`refactoring@2`를 넣고 라우터와 지휘 절차에 연결했지만, 실제 작업으로 돌려 보지 않았다. 특히 "리팩토링 기준"(관리자가 `state.md`에 `S`·`P`를 두고 넘기기, rebase 뒤 새 `P` 확인)은 문서 검토만 거쳤다. 이번에는 세 레시피를 한 지휘에서 쓴다.

- 저장소: `vananaHope/vstack-pilot-todo` · 실행 환경: Orca · 플러그인 vstack 0.8.0 · 계약 `vstack-contract@3` · 레시피 `bug-fix@4`·`feature@2`·`refactoring@2`
- 실행기: Codex(구현), Claude(검토). OpenCode는 쓰지 않는다(계정 막힘). 명세 새 눈 점검은 서브에이전트.
- 병합 방식: `지시`, 병합 방법 `squash`. 병합·force-push는 이름을 적은 사용자 승인으로만 한다(고정 규칙 5).
- 관리자 세션: 0.8.0을 읽은 **새 Claude Code 세션**(이 계획을 쓴 세션은 0.7.0을 읽은 채라 지휘하지 않는다). 이 세션은 준비만 한다.
- 한계: 버그의 원인을 계획 작성자가 안다. 이슈 본문에는 증상만 쓰지만 진단의 맹검성은 주장하지 않는다. 관리자 세션도 시범 중임을 안다.

## 이슈 셋

### 공통 입력(세 vstack 절에 모두 넣는다)

- 실행 조건: Node 22 이상, 무인(TTY 없음), 실창 없음. 의존성 추가 없음.
- 준비·정리: verify 스킬 `.claude/skills/verify-todo/SKILL.md`. 시나리오는 실행마다 임시 데이터 파일을 만들고 지운다(`./data/`를 건드리지 않음). `done-idempotent`는 `.env.local`이 필요하다(아래 준비 3).
- 증거 폴더: 수용 기준과 명령마다 다른 하위 폴더(`<증거 폴더>/ac-<n>/<시나리오>`). 시도별 경로는 관리자가 배정 때 채운다.

### I1 버그 수정: 제목 필드가 없는 할 일이 `undefined`로 보인다

- 증상: 데이터 파일의 항목에 `title`이 없거나 `null`이면 `list`가 `[ ] 2. undefined`처럼 보이고, `list --json`의 `title`도 문자열 `"undefined"`·`"null"`이다.
- 기대 동작: 제목이 없거나 `null`인 항목은 빈 제목(`""`)으로 읽는다. `list`는 `(제목 없음)`, `list --json`은 `""`다. 문자열이 아닌 다른 값(숫자 등)은 지금처럼 문자열로 바꾼다. 이 동작은 이 계획을 승인하면 사용자가 정한 것으로 본다.
- vstack 절: `bug-fix@4`
  - `AC-1@1` 증상 해소(필수): `node scripts/verify.mjs missing-title --out <증거 폴더>/ac-1/missing-title`
  - `AC-2@1` 회귀 테스트(필수): `node --test test/`. 제목 없음과 `null`을 `loadTodos`로 읽는 회귀 테스트가 `test/store.test.mjs`에 있고 실행 목록에 있다.
  - seam `loadTodos`, 결정적, 재현 경로 = 시나리오 `missing-title`, 건드리지 말 영역 `bin/`·`src/todo.mjs`·`scripts/`, 테스트는 `test/store.test.mjs`만 고친다.

### I2 리팩토링: CLI 명령 처리를 `src/cli.mjs`로 옮긴다

- 동기: `bin/todo.mjs`의 `switch`에 불러오기·저장·출력이 섞여 있어, 명령을 더하거나 테스트하기 어렵다. 동작은 바꾸지 않는다.
- 목표 구조: `src/cli.mjs`가 `runCli(argv, dataPath)`를 내보낸다. 이 함수가 불러오기, 명령 표(`add`·`done`·`list`를 키로 갖는 객체) 조회, 저장을 하고 `{ code, out, err }`(종료 코드와 출력할 문자열)를 돌려준다. `bin/todo.mjs`는 `dataPath`를 정하고 `runCli`를 부른 뒤 출력과 종료 코드만 처리한다. `bin/`과 `src/`에 `switch`가 없다. `bin/todo.mjs`는 `src/store.mjs`를 import하지 않는다.
- seam: 지킬 동작은 **CLI 프로세스 경계**(`node bin/todo.mjs ...`의 표준 출력·표준 오류·종료 코드)와 기존 모듈 export에서 본다. 이 경계는 `S`에도 있으므로 특성화 테스트를 `S`·`P`에서 돌릴 수 있다. 구조를 바꾼 뒤의 `runCli`는 구조 수용 기준에서만 본다(`S`에 없으므로 고정에 쓰지 않는다).
- 전환 방식: `한 번에 전환`. 영향 범위: `bin/todo.mjs`의 명령 처리(호출자는 `bin/todo.mjs`뿐), `git grep -n "loadTodos\|saveTodos\|formatList\|addTodo\|markDone" -- bin src`.
- 고정 명령(pin), 각각 따로 실행한다:
  - `node --test test/`
  - `node scripts/verify.mjs toggle-persist --out <증거 폴더>/ac-1/toggle-persist`
  - `node scripts/verify.mjs id-unique --out <증거 폴더>/ac-1/id-unique`
  - `node scripts/verify.mjs title-trim --out <증거 폴더>/ac-1/title-trim`
  - `node scripts/verify.mjs empty-title --out <증거 폴더>/ac-1/empty-title`
  - `node scripts/verify.mjs done-idempotent --out <증거 폴더>/ac-1/done-idempotent`(`.env.local` 필요)
  - 사용법 오류(종료 코드 2와 사용법 줄)와 실행 오류(`오류: ...`, 종료 코드 1)는 지금 어떤 pin도 보지 않는다. 레시피 "새 리팩토링" 2에서 작업자가 이것을 찾아 특성화 테스트를 더할지 본다(정답을 명세에 적지 않는다). 더하면 새 테스트 파일(예: `test/cli.test.mjs`)에 두고 기존 테스트 파일은 고치지 않는다.
- vstack 절: `refactoring@2`
  - `AC-1@1` 동작 보존(필수): 위 pin 전부
  - `AC-2@1` 구조(필수): `node scripts/check-structure.mjs cli-dispatch`(기계 검사 항목은 준비 2). 반환값 `{ code, out, err }`와 `bin/`이 출력·종료 코드만 다루는지는 검토에서 본다.
  - 건드리지 말 영역 `src/store.mjs`·`src/todo.mjs`의 export·`scripts/`·기존 테스트 파일. 원래 동작 기준 `S`는 배정할 때 관리자가 정한다.

### I3 기능: 완료를 되돌리는 `todo undo <id>`

- 데이터 모양: 기존 `done` 불리언을 쓴다. 새 필드나 저장 형식 변경 없음. seam: `src/todo.mjs`의 새 export `markUndone(todos, id)`와 CLI `undo` 명령.
- 범위 밖: 토글 명령, 여러 개 한꺼번에, `list` 필터.
- vstack 절: `feature@2`. 동작마다 수용 기준 하나(레시피 "입력"):
  - `AC-1@1` 동작(필수) 완료 취소: `add` → `done 1` → `undo 1`이 `완료 취소: 1`을 출력하고, 새 프로세스의 `list --json`에서 1번이 `done=false`, `list`가 `[ ] 1. 우유 사기`. `node scripts/verify.mjs undo-persist --out <증거 폴더>/ac-1/undo-persist`
  - `AC-2@1` 동작(필수) 미완료에 다시 취소: 미완료인 1번에 `undo 1`을 해도 종료 코드 0, `완료 취소: 1`, 새 프로세스에서 `done=false`. `node scripts/verify.mjs undo-idempotent --out <증거 폴더>/ac-2/undo-idempotent`
  - `AC-3@1` 동작(필수) 없는 id: `undo 9`가 종료 코드 1, 표준 오류 `오류: no todo with id 9`, 데이터 파일이 바뀌지 않는다. `node scripts/verify.mjs undo-missing --out <증거 폴더>/ac-3/undo-missing`
  - `AC-4@1` 동작(필수) 사용법: 인자 없이 실행하면 종료 코드 2이고 사용법 줄에 `todo undo <id>`가 있다. `node scripts/verify.mjs usage-undo --out <증거 폴더>/ac-4/usage-undo`
  - `AC-5@1` 테스트(필수): `node --test test/`. AC-1~4의 동작마다 그 동작을 보는 테스트가 실행 목록에 있다. 상태 전이(완료 취소, 미완료 유지, 없는 id 오류)는 `markUndone`에서, 출력·종료 코드·저장·사용법 줄은 CLI 프로세스 경계(`node bin/todo.mjs ...`)에서 본다. I2가 CLI 특성화 테스트 파일을 만들었으면 그 파일을 새 요구에 맞게 넓히고(기능이 사용법 줄을 바꾸므로 그 assertion을 고치는 것은 정상), 없으면 새로 만든다. 이 테스트들은 준비 커밋에 넣지 않는다.
  - 건드리지 말 영역 `src/store.mjs`·`scripts/`.
- I2의 목표 구조가 병합된 뒤 시작하므로, `undo`는 명령 표에 들어가야 한다. 이것을 수용 기준으로 두지는 않고 검토에서 본다.

## 준비(지휘 2의 사전 준비 변경)

라우터 지휘 2의 실행 기반이다. **시범 저장소 `main`에 직접 커밋 하나를 만들고 push**한다. 이 계획을 승인받으면 그 커밋과 push를 확인받은 것으로 본다. 그 밖의 `main` 변경은 하지 않는다. 확인은 `pilot-2-plan.md` "준비"와 같다(원격·경로 확인, 준비 전 SHA 기록). 커밋 메시지는 중립적으로 쓴다(시범 3 D7). 레시피가 작업 브랜치에서 만들 회귀·동작·특성화 테스트는 넣지 않는다.

1. `scripts/verify.mjs`에 시나리오를 더한다. 종료 코드와 표준 오류를 봐야 하는 시나리오를 위해, 종료 코드가 0이 아니어도 던지지 않고 `{ code, stdout, stderr }`를 돌려주는 실행 도우미를 더한다(기존 시나리오의 실행 방식은 바꾸지 않는다).
   - `missing-title`: `title`이 없는 항목과 `null`인 항목이 든 v2 파일로 새 프로세스에서 `list`와 `list --json`을 돌린다. 기대는 `(제목 없음)` 두 줄과 `title` `""` 둘.
   - `undo-persist`·`undo-idempotent`·`undo-missing`·`usage-undo`: I3의 AC-1~4 그대로. 지금 `main`에서는 `undo`가 사용법 오류로 끝나 실패로 기록된다(던지지 않고 실패).
   - 사용법 주석, README의 시나리오 목록, verify 스킬 `features/`에 문서를 더한다.
2. `scripts/check-structure.mjs`를 더한다. 인자 `cli-dispatch`로 원본 파일을 읽어 다음을 기계 검사하고, 모두 맞으면 0, 아니면 1과 어긋난 항목을 출력한다: (a) `src/cli.mjs`가 있고 `runCli`를 export한다(동적 import로 함수인지 확인) (b) `bin/`·`src/`의 `.mjs`에 `switch`가 없다 (c) `bin/todo.mjs`가 `src/store.mjs`를 import하지 않는다 (d) `bin/todo.mjs`가 `runCli`를 import한다. 명령 표의 모양과 반환값은 검토 몫이다.
3. 환경 입력 범위를 넓힌다. 지금 설정은 "관리자가 worktree에 둔다. 작업자는 만들지 않는다"인데, 리팩토링 레시피의 `S`·`P` 확인은 `git archive` 사본에서 하므로 무시 파일 `.env.local`이 따라오지 않는다. 그러면 `done-idempotent`가 사본에서 늘 종료 코드 3이 된다. 시범 설정 `docs/agents/orchestration.md` "환경 준비"와 verify 스킬 "Launch"에 한 줄을 더한다: "작업자는 scratch 사본에 그 worktree의 `.env.local`을 그대로 복사해 쓴다(새로 만들거나 값을 바꾸지 않는다). worktree에 없으면 `막힘`(환경)으로 보고한다." 이 빈틈은 vstack 레시피에도 있다(아래 D1).
4. red/green 확인: 새 시나리오와 구조 검사가 지금 `main`에서 실패하는지 본다. green은 scratch 사본(OS 임시 폴더)에서 버리는 최소 수정을 얹어 확인하고 사본을 지운다. 기존 시나리오 다섯이 그대로 통과하는지도 본다. 커밋 전에 `git diff --cached`로 준비 커밋에 제품 코드(`src/`·`bin/`)나 `test/` 변경이 섞이지 않았는지 본다.
5. 이슈 셋을 만든다(라벨 `ready-for-agent`, 본문에 증상 또는 동기·기대 동작·완료 기준 체크리스트·vstack 절). I3 본문에 "I2 병합 뒤 시작"을 적는다(설정의 선행 관계는 "없음"이라 관리자가 고르는 근거로만 쓴다). 준비 결과에 이슈 번호를 적는다. PR 번호는 이슈 번호와 다르므로 PR이 생기면 관리자가 `state.md`에 적은 것을 쓴다.

## 기대 흐름

사용자가 새 세션에서 `/vstack:v-mode vstack-pilot-todo 이슈 <I1> <I2> <I3> 진행해`라고 한다.

1. **라우터**: 지휘 갈래. 이슈마다 vstack 절의 레시피를 그대로 쓴다. vstack 절과 검증 명령이 이미 있으므로 지휘 2는 확인만 한다.
   - 사전 가설(라우터 문구의 모호성): 라우터 2는 "한 요청에 작업 유형 레시피는 최대 하나"라고 하고, 지휘 2는 티켓마다 레시피를 적게 한다. 이 시범은 "최대 하나"를 **한 작업(티켓) 단위**로 읽는다는 가설로 간다. 관리자가 요청을 나누자고 하거나 묻는 것도 가능한 결과로 기록하고, 실행 실수로 세지 않는다(문서 원인).
2. **고르기**: orchestrate-issues 고정 규칙 "새 작업 시작 조건"의 모든 조건(작업자·검토자 고르기, 검토 대기 1개 이하, 같은 파일 영역 아님 등)이 맞을 때 I1(`src/store.mjs`, `test/store.test.mjs`)과 I2(`bin/`, 새 `src/cli.mjs`, 새 테스트 파일)를 함께 시작한다. I3은 I2와 `bin/`·명령 처리 영역이 겹치고, I2는 "진행 중"(SKILL.md 1단계: `state.md`가 `끝`이 아니거나 열린 PR)이므로 I2가 `끝`이 될 때까지 시작하지 않는다.
3. **I2 배정**: `state.md`에 "리팩토링 기준" 줄을 둔다(`S`=배정 때 시작 커밋, `P=미정`). 명세의 작업 종류는 `새 리팩토링`, 레시피별 입력 칸에 `S`·pin·목표 구조·전환 방식·영향 범위가 들어간다.
4. **I2 구현 보고 뒤**: 관리자가 보고된 `P`로 줄을 채운다(`S..P`가 테스트 파일만). 검토 명세에 `S`·`P`·후속 고정 테스트를 넣는다. 검토자는 `P` 사본에서 pin을 돌린다(레시피 "검토자 review" 3). 사본의 `.env.local`은 준비 3대로 복사한다. 종료 코드 3이 나오면 동작 차이가 아니라 환경 막힘이다.
5. **I1·I2 지시 대기** → 사용자의 "PR 올려"로 **두 PR을 모두 게시**한다. 그다음 사용자가 I1을 먼저 병합하게 한다("PR #<I1의 실제 PR 번호> 병합해").
6. **I2 병합 지시 뒤**: 병합 관문 진입점 "병합해 지시"에서 `B`를 다시 읽으면 바뀌었으므로 rebase를 맡긴다(merge-gate.md "진입점"). 순서:
   1. 리팩토링 기준 줄을 `확인 대기`로 고친다. rebase 작업자가 `range-diff`로 새 `P`를 찾아 새 `P` 사본에서 pin과 후속 고정 테스트를 돌려 보고한다. 관리자가 결과 대상 확정 때 대조해 확정한다(vstack.md "리팩토링 기준" rebase 1~5). 사본에서 종료 코드 3이 나오면 같은 대상 확인 재시도로 다시 맡기고 `확인 대기`를 풀지 않는다.
   2. 새 `review` 시도와 보관.
   3. 원격 반영: 원격 head가 새 `H`의 조상이 아니므로 force-push 확인을 구한다(브랜치, 지금 원격 head SHA, 새 `H`, range-diff 요약). 이름을 적은 승인 뒤 `--force-with-lease=<브랜치>:<원격 SHA>`로 게시하고 원격 head를 다시 읽는다(vstack.md "원격 반영").
   4. 원격 `H`·`B`로 관문 G1~G5를 판정한다(vstack.md "병합 관문" 2~4). 통과하면 병합하고 `MERGED`를 확인한다.
   - I1의 수정(빈 제목으로 읽기)이 I2의 특성화 테스트가 고정한 동작을 바꾸면(예: 특성화 테스트가 제목 없는 항목의 `undefined` 출력을 적었으면), 새 `P` 사본에서 assertion이 실패한다. 그러면 관리자가 사용자에게 묻는다(rebase 4). 어느 갈래가 나와도 기록한다.
   - 특성화 테스트를 더하지 않았으면 `P` = `S`이고 range-diff로 대응시킬 커밋이 없다. 그 경우는 따로 기록하고, 특성화 테스트 커밋 대응 경로를 확인했다고 세지 않는다.
7. **I3**: I2가 `끝`이 된 뒤 고르기에서 시작한다. 명세의 작업 종류는 `새 구현`. 구현자는 동작마다 red→green을 커밋하고 `process/`에 남긴다. 검토자는 구현을 되돌린 scratch 사본에서 테스트가 실패하는지 본다.
8. PR·병합은 사용자 지시로.

## 시범으로 답할 질문

- Q1 리팩토링 기준: 줄이 첫 배정·구현 보고·검토 명세·rebase(확인 대기 → 새 `P` → 확정)에서 문서대로 쓰이는가. 실제 `range-diff` 출력으로 새 `P`를 찾을 수 있는가(`P` = `S`면 따로 적는다).
- Q2 고정 검사: I2 작업자가 레시피 "새 리팩토링" 2에서 pin이 지나가지 않는 코드(사용법·오류 경로)를 찾는가. 특성화 테스트를 더했으면 `S..P`가 테스트 파일만인가.
- Q3 기능 레시피: 데이터 모양이 티켓에 있을 때 작업자가 그대로 쓰는가. red→green 과정 증거가 동작마다 있는가. 검토자가 "테스트가 실제로 실패하는가"를 scratch에서 확인하는가.
- Q4 동시 시작: 관리자가 시작 조건을 모두 확인하고 I1·I2를 함께 시작하는가. SKILL.md 1단계의 "진행 중" 정의를 적용해 I2가 `끝`이 될 때까지 I3을 미루는가.
- Q5 작업 종류 이름: 명세에 `새 구현`·`새 리팩토링`이 레시피 이름대로 적히는가. 복구가 생기면 "레시피 첫 구현 절차의 1부터"를 맞게 읽는가.
- Q6 라우터: 레시피가 다른 세 이슈를 한 요청으로 받았을 때 어떻게 하는가(기대 흐름 1의 사전 가설).
- Q7 환경 입력: scratch 사본의 `.env.local` 복사(준비 3)가 `S`·`P`·새 `P` 확인에서 쓰이는가. 종료 코드 3을 동작 차이와 구분하는가.

## vstack 문서에 이미 보이는 고칠 거리(시범 뒤 반영 후보)

- D1: `refactoring.md`의 scratch 사본(`git archive`)에는 무시 파일인 환경 입력이 따라오지 않는다. 레시피와 명세 양식에 "사본에 필요한 환경 입력과 그 출처"를 넣을지 시범 결과로 정한다.
- D2: 라우터 2의 "한 요청에 레시피 최대 하나"가 지휘(여러 티켓) 요청에도 걸리는지 문구를 정한다(Q6 결과로).

## 멈춤 기준

- 정지가 확인되지 않은 작업자가 있으면 그 시도의 정산·격리·재시작·worktree 삭제를 하지 않고 "정지 미확인"을 알린다(backends/orca.md "정지").
- 병합·force-push는 이름을 적은 사용자 승인이 있을 때만 한다. 병합 승인은 실제 PR 번호로 받는다. force-push는 `--force-with-lease=<브랜치>:<기대하는 원격 SHA>`로만 하고, 그 SHA를 방금 원격에서 읽은 값과 대조한다. 승인이 없거나 lease 값이 맞지 않으면 명령을 내리기 전에 멈춘다.
- 관문 판정은 원격 반영과 원격 재확인 뒤에만 한다. 옛 `H`로 판정한 관문 결과를 새 `H`에 쓰지 않는다.
- 리팩토링 기준이 `확인 대기`인 동안 다른 시도를 맡기지 않는다(그 확인의 재시도 하나만 예외).
- 유효하지 않은 증거로 병합 관문을 통과시키려 하면 멈춘다.
- 위 가운데 하나라도 이미 어겼으면 시범 전체를 멈추고 보고한다.
- 관리자가 계약에 답이 없는 상황을 만나면 추측하지 않고 사용자에게 묻고, 그 상황을 기록한다.
- 사용자 확인이 필요한 곳: 준비 결과, PR, 병합(I1 → I2 → I3 순서), force-push, rebase 4의 assertion 실패.

## 순서

1. 이 세션: 준비 1~5. 사용자에게 준비 결과(커밋 SHA, red 출력, 이슈 번호)를 보이고 확인받는다.
2. 사용자: Claude Code를 다시 시작해 0.8.0을 읽은 새 세션을 연다. 그 세션에서 `/vstack:v-mode vstack-pilot-todo 이슈 <I1> <I2> <I3> 진행해`.
3. 새 세션: 지휘(기대 흐름 1~8). 사용자는 PR·병합을 I1 → I2 → I3 순서로 지시한다.
4. 사용자의 "시범 기록을 써라" 뒤 관리자 세션이 `docs/pilot-5.md`를 쓴다: 이슈마다 기대·실제, Q1~Q7 답, D1·D2 판단, 어긋난 곳, 원인(라우터·계약·레시피 문서 / Orca 동작 / 실행 실수), 고칠 것.

## 이번에 하지 않는 것

같은 계열 검토·2차 의견(OpenCode 없음), `expand–contract` 리팩토링, 기능 레시피의 설계 결정 `막힘` 경로(티켓에 데이터 모양을 정해 두었다), 관리자 재시작 중 끊기(시범 4 R2와 나머지 행), herdr 실행 환경, 진단의 맹검성.

## 준비 결과(2026-11-09)

- 준비 커밋 `f5aa577`(부모 `353f2b0`)을 시범 저장소 `main`에 push했다. `src/`·`bin/`·`test/` 변경 없음.
- red(`f5aa577` 그대로): `missing-title`·`undo-persist`·`undo-idempotent`·`undo-missing`·`usage-undo` 종료 코드 1, `check-structure.mjs cli-dispatch` 종료 코드 1. 기존 시나리오 넷은 0, `done-idempotent`는 메인 체크아웃에 `.env.local`이 없어 3.
- green(버리는 scratch 사본에 최소 수정과 `.env.local`): 시나리오 10개 모두 0, 구조 검사 0, `node --test test/` 11/11. 사본은 지웠다.
- 이슈: I1 = #11(`bug-fix`), I2 = #12(`refactoring`), I3 = #13(`feature`, 본문에 "#12 병합 뒤 시작").
