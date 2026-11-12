# omp 맡기기 시범 기록

- 날짜: 2026-11-10 · 실행 환경: Orca 1.4.255 · omp 18.18.6 · 레시피 `bug-fix@4`(한 세션 절차 범위, 계약 밖) · 플러그인 vstack 0.8.0 설치본의 레시피를 작업자가 읽음
- 목적: Claude Code 지휘자가 한 세션 크기의 버그 수정을 omp 작업자에게 새 worktree로 맡기는 경로([design.md](design.md) 12절 초안)가 실제로 도는지 본다([pilot-omp-plan.md](pilot-omp-plan.md)).
- 지휘자: Claude Code 세션 `claude_c7c5aeab_077d_4e9a_8b20_7091f680a49a`. 12절 초안을 직접 읽고 따랐다(라우터를 거치지 않았다).
- 저장소: 로컬 전용 `C:/Users/gusdn/orca/projects/vstack-pilot-omp`(`vstack-pilot-todo` `main` `99168cf`의 복제, 원격 없음). 준비 커밋 `afc0b85`(`B`). worktree `C:/Users/gusdn/orca/workspaces/vstack-pilot-omp/done-invalid-id`, 브랜치 `fix/done-invalid-id`.
- Run `run_ba1501382a22`. 작업 기록은 시범 저장소의 `.local/vstack-delegate/done-invalid-id.md`와 명세 `done-invalid-id.spec.md`.
- 시각은 UTC다(한국 시간은 9시간을 더한다).
- 근거: Orca 명령 출력(지휘자 대화 기록), omp 세션 기록 `~/.omp/agent/sessions/-orca-workspaces-vstack-pilot-omp-done-invalid-id/`(부모 `2026-11-10T14-37-27-782Z_01a1c5e4-….jsonl`, 자식 `…/ReviewDoneInvalidId.jsonl`), 시범 저장소의 git 기록. 이 PC에만 있다.

## 결과 요약

정상 경로가 끝까지 갔다. 띄우기(14:37:25)부터 정리(14:44)까지 약 7분.

| 12.4 단계 | 기대 | 실제 |
| --- | --- | --- |
| 2 예약 | 기록 `예약` | 그대로 |
| 3 Run | 전용 Run | `run-create`로 새로 만들고 `run-current`로 확인. 그 전에는 이전 scratch 시범의 자식 세션이 만든 Run(`run_94c9647db78e`)에 묶여 있었다 |
| 4 worktree | 띄우기 전 HEAD=`B`, clean | 그대로. `--no-parent`를 더했다(계획에 없음) |
| 5 띄우기 | `--agent omp`, 모델 없음 | 결과의 `launch.effective`가 `model: null, effort: null` |
| 6 제출 확인 | Task·Dispatch 기록 | `task_4c424a958e0e`·`ctx_bc3904d96a63`, `state: ready`. `turnStart: unsupported`라 `worker-show`·`worker-read`로 시작을 봤다 |
| 7 질문 | `ask` → 답 → 이어 감 | 성립(아래) |
| 8 확인 | 통과 | 통과. AC-1 종료 0, AC-2 종료 0(13/13) |
| 9 후속 지시 | 새 Dispatch, 새 커밋, 다시 확인 | 성립(아래). AC-2 14/14 |
| 10 끝내기 | 모든 Dispatch 해제 | 마지막 Dispatch `released`. 앞선 Dispatch는 `retained`·`ownership_transferred`(아래 "어긋난 곳" 2) |

결과물: `B..763399e` 커밋 4개(실패 테스트 → 수정 → 실패 테스트 → 수정). `bin/todo.mjs` 2줄, `test/cli.test.mjs` 새 파일 44줄. 건드리지 말 곳(`src/store.mjs`, `scripts/verify.mjs`, `.claude/skills/`)은 바뀌지 않았다.

## 일부러 넣은 경로

### 질문(앞에 0이 붙은 id) — 성립

- 14:38:00 작업자 `ask`(`msg_e94f496220b4`). 재현을 먼저 하고, 선택지 둘과 추천((A) 거부), 지금 `01`·`0x1`·`1e0`·`' 1'`이 모두 1번으로 처리된다는 사실을 붙여 물었다.
- 질문이 온 시점의 worktree: HEAD=`B`, status 빔.
- 14:38:19 지휘자 `reply --id msg_e94f496220b4`(`msg_244d364e656a`): 정해 둔 답 "(A) 거부, `invalid id 01`, 종료 코드 1". 계획에 없던 "회귀 테스트에도 넣어라" 한 문장을 지휘자가 덧붙였다.
- 14:38:22 작업자 `orca orchestration check`로 답을 받음 → 14:38:34 첫 구현 쓰기(`test/cli.test.mjs`). 답 뒤에 썼다.
- 한계: 명세가 물으라고 시켰다. 질문이 필요한지 omp가 스스로 판단하는 능력은 보지 않았다.

### 후속 지시(사용법 줄) — 성립(시험용 요구, 실제 확인 실패 아님)

- 1차 확인이 통과해 계획이 승인한 시험용 요구를 보냈다: 사용법 줄을 `todo done <id(양의 정수)>`로, 그 줄을 보는 테스트 추가.
- 14:42:10 `send --to dispatch:ctx_bc3904d96a63` → `delivery: follow_up`, 새 `ctx_1c32fc77937c`·`task_36a955f0b7e3`, 같은 터미널. omp 세션 기록도 같은 파일에서 이어졌다(세션 줄 하나).
- 14:42:49 `worker_done`. 새 커밋 `08c46cc`(실패 테스트), `763399e`(수정). 다시 확인 통과.
- 작업자가 닫히기 전(자동 해제 예정 14:42:49)에 보냈다. 이미 닫힌 작업자가 `send`로 다시 열리는지는 보지 못했다.

## 관측

- **O1 시작**: 기록·Run·Task·Dispatch·worktree가 맞았다. 시작 HEAD=`B`.
- **O2 보고 경로**: 작업자는 `orca orchestration ask --from <터미널>`, `check`, `send --type worker_done`을 썼다. 지휘자는 Orca가 깨웠다(질문 1회, 완료 보고 2회). 끝난 뒤 `terminalState: reclaimable`, 자동 해제는 약 2분 뒤로 잡혔다(backends/orca.md대로).
- **O3 메인 모델**: `anthropic/claude-opus-5-5`, `resolvedModelIsFallback: false`. `modelRoles.default`와 같다. assistant 메시지 33개(1차 24, 후속 9) 모두 같은 모델.
- **O4 서브에이전트**: `task` 호출 1회. omp가 고른 에이전트는 `reviewer`(명세는 "서브에이전트에게 읽기 전용 검토"만 시켰다). 자식 세션의 모델은 `openai-codex/gpt-6-astra`, fallback 아님. `modelRoles.slow`와 같다. 자식의 도구 호출은 read 10, bash 3(`git diff`, `git log`, `git show`)이고 쓰기가 없다. 결과는 지적 없음. 후속 턴에서는 서브에이전트를 쓰지 않았다(후속 지시가 요구하지 않았다).
- **O5 경계**: omp와 자식의 기록에 작업자 생성 명령(`worker-start`, `worktree create`)이 없다. Run의 작업자는 맡긴 Dispatch 둘뿐이고, 시범 5 Run(`run_368dd5ac3393`)은 시작 전 기준 목록 그대로다. 지휘자는 worktree에서 읽기 전용 git과 검증 명령만 돌렸다(산출물은 OS 임시 폴더). 커밋은 `fix/done-invalid-id`에만 있고 `main`은 `B`다.
- **O6 확인 시점**: 1차는 메인 턴이 끝난(14:40:51) 뒤 14:40:57부터, 2차는 후속 턴이 끝난(14:43:02) 뒤 14:43:08부터 확인했다. 두 번 모두 확인 뒤 HEAD·status가 그대로였다. 지휘자는 각 실패 테스트 커밋을 OS 임시 폴더에 풀어 실제로 실패하는 것도 봤다.

사전 점검(버려도 되는 저장소)에서 알게 된 것: omp 세션 기록에서 메인 모델, `task` 호출과 에이전트 종류, 자식 기록(`session.parentSession`, `model_change`의 `subagent:<이름>` 역할과 모델), 자식의 도구 호출, 종료를 모두 읽을 수 있다. 서브에이전트의 모델은 에이전트 종류별 역할이 정한다(번들 정의: `scout`→`smol`, `reviewer`→`slow`, `task`→`task`, `sonic`→`smol`). 점검에서는 `scout`가 불려 Claude Sonnet으로 돌았다. 계획의 "서브에이전트는 `task` 역할" 가설은 틀렸다.

## 어긋난 곳과 원인

1. **omp 전역 설정이 준비 기록 뒤에 바뀌었다(기록 시점이 일렀다).** 지휘자가 설정을 기록한 것은 14:05, 설정 파일이 바뀐 것은 14:32:18, 띄운 것은 14:37:25다. 지휘자가 바꾸지 않았다. 사용자가 그 사이에 직접 바꾼 것이다(사용자 확인). 바뀐 값: `plan`·`tiny` 역할, `task` 대체 모델, `usageAwareFallback`, `task.eager: preferred` 등. 이번에 쓰인 `default`·`slow` 값은 같아 O3·O4의 모델 대조는 성립한다. `task.eager`가 서브에이전트 사용에 준 영향은 확인하지 못했다. 고칠 것: 설정 기록은 띄우기 직전에 한다(시범 절차). 실제 운용에서는 설정을 기록하지 않는다(모델은 omp가 정한다).
2. **후속 Dispatch 뒤 앞선 Dispatch가 `released`가 되지 않는다(Orca 동작, 문서 빠짐).** `worker-release ctx_bc3904d96a63` → `retained`, `reason: ownership_transferred`. 터미널은 후속 Dispatch 쪽에서 `released`됐다. backends/orca.md "정리"의 "모든 dispatch가 `released`"와 맞지 않았다. → backends/orca.md와 delegate-omp.md에 적었다.
3. **Orca가 omp의 턴 시작을 관측하지 못한다(Orca 동작).** `turnStart: unsupported`, `stage`는 `input_accepted`에 머문다. → delegate-omp.md "제출 확인"에 `worker-show`·`worker-read` 확인을 넣었다.
4. **`worker_done` 직후 `worker-show`의 `activity`는 `working`이다(Orca 동작).** 메인 턴이 끝난 뒤에도 잠깐 그렇게 보였다. 작업자가 정말 멈췄는지는 이 값으로 알 수 없다. → 확인 전후 HEAD·status 대조로 잡는다(delegate-omp.md 8).
5. **계획과 다르게 한 것(실행 판단)**: 준비 커밋을 `cherry-pick --no-commit` 대신 `git diff … | git apply --index`로 얹었다(정답이 든 수정 커밋 객체를 시범 저장소에 들이지 않으려고). `worktree create`에 `--no-parent`. 답에 한 문장 추가.

## 반영

- 절차의 정본을 `skills/v-mode/delegate-omp.md`와 `delegate-omp-spec.md`(이번 명세를 양식으로)로 옮기고 12절은 요약으로 줄였다.
- v-mode: 고르기 0에 진행 중인 맡기기, "한 세션"에 "직접 할지, omp에 맡길지"(`bug-fix`는 조건이 맞으면 맡기기가 기본), "실행 도구"에 omp에서 다른 모델 쓰기.
- orchestrate-issues "새 작업 시작 조건"에 진행 중인 맡기기 없음. backends/orca.md "정리"에 위 2.
- 반영을 Codex가 검토하며 나온 것(시범에서는 드러나지 않았다): 기록을 `<이름>/state.md`·`spec.md`로 나눔(시범의 `<이름>.md`·`<이름>.spec.md` 배치는 명세 파일이 "진행 중"으로 잡힌다), 맡기기 전에 지휘자 작업 트리의 미커밋 변경과 기준 커밋의 검증 기반 확인, 맡기지 않는 이유에 따라 직접/지휘를 나눔, 명세에 원칙 원문의 참조를 따라가지 않는다는 문장.

## 라우터를 거친 실행(2026-11-11)

위 시범은 지휘자가 계획을 알고 절차 초안을 직접 따랐다. PR #9를 병합하고 플러그인 0.9.0을 설치한 뒤, 사용자가 Orca에서 시범 저장소 `main`에 새 Claude Code 세션을 열어 `/vstack:v-mode`로 버그 하나를 줬다. 그 세션은 이 시범을 모른다. 이 기록을 쓰는 세션은 읽기만 했다.

- 요청: "데이터 파일에 `items`가 없으면(`{}`, `{"version":2}`) `todo list`·`todo add`가 `오류: Cannot read properties of undefined (reading 'map')`로 끝난다. 기대: 빈 목록으로 읽는다."
- 지휘자: `claude_3ef6708b_c5e1_4a36_b23f_66afe89865b8`. 근거는 그 세션의 대화 기록(`<Claude 설정 폴더>/projects/C--Users-gusdn-orca-projects-vstack-pilot-omp/55f23fb7-cca3-4a8d-9b06-97b180507415.jsonl`), 시범 저장소의 `.local/vstack-delegate/missing-items/state.md`·`spec.md`, omp 세션 기록(`~/.omp/agent/sessions/-orca-workspaces-vstack-pilot-omp-missing-items/`), git 기록이다.

| 시각(UTC) | 일어난 일 |
| --- | --- |
| 04:44 | 고르기 0(끝난 기록 `done-invalid-id` 확인), Orca·omp 확인, 버그 재현. 갈래: 한 세션 · `bug-fix` · omp에 맡기기 |
| 04:45:44 | "맡기기 전에" 7: 사용자 경로를 검증할 verify 시나리오가 `main`에 없다. 선택지 셋(`main`에 시나리오 커밋 후 맡김 / 시나리오 브랜치를 기준으로 / 맡기지 않고 직접)으로 물음 → 사용자가 첫째를 고름 |
| ~04:52 | verify 시나리오 `missing-items`를 `main`에 로컬 커밋(`dae1c59` = `B`, 지금 코드에서 실패 확인). 예약, Run을 새로 만듦(`run_a888d2921607`), worktree `fix/missing-items`(띄우기 전 HEAD=`B`·clean 확인) |
| 04:52:30 | `worker-start --agent omp`, 모델 옵션 없음. `worker-show`·`worker-read`로 시작 확인, 기록 `배정됨` |
| 04:54:44 | `worker_done`(`H`=`88143cb`). 작업자 질문은 없었다(명세가 범위를 정했다) |
| 04:54:50~04:55:03 | 지휘자 확인: Dispatch 끝남, clean, `H`=실제 HEAD, `B..H` 커밋 2개(실패 테스트 `15e8fee` → 수정 `88143cb`), AC-1·AC-2 재실행, 원래 재현 경로, `15e8fee` 임시 사본에서 새 테스트만 실패, 다른 verify 시나리오 5개. `확인 통과`. 작업자 터미널 해제(`released`) |
| ~05:00 | 사용자 지시(로컬에서 `main`에 fast-forward 병합, push·PR 없음, worktree 삭제): `git merge --ff-only` → `main`=`88143cb`, `main`에서 AC 재실행, `orca worktree rm --delete-branch` → 기록 `끝`(05:00:59) |

- omp: 메인 `anthropic/claude-opus-5-5`(fallback 아님). `task` 1회, 에이전트 `reviewer`, 자식 `openai-codex/gpt-6-astra`(fallback 아님). 자식 도구는 read 9, bash 4(`git diff`·`log`·`show`), grep 1이고 쓰기가 없다. 메인의 쓰기는 `test/store.test.mjs`와 `src/store.mjs` 한 줄(`(raw.items ?? []).map(normalize)`). Run의 작업자는 하나다.
- 관찰자 재확인(05:01): `main`=`88143cb`·clean, `node scripts/verify.mjs missing-items` 종료 0, `node --test test/` 13/13, worktree와 브랜치 없음, 기록 `끝`.
- 명세는 양식(`delegate-omp-spec.md`)의 절을 모두 갖췄다. 기록은 새 배치(`<이름>/state.md`, `spec.md`)다.
- 문서에 없던 것: 결과 반영 방법으로 지휘자가 로컬 병합을 선택지로 냈고, 병합 뒤 기준 브랜치에서 수용 기준을 다시 돌렸다. → delegate-omp.md 10에 적었다.
- 이 실행으로 처음 돌려 본 것: 라우터의 맡기기 선택, 새 세션이 delegate-omp.md만 보고 끝까지 감, "맡기기 전에" 7의 질문, 새 기록 배치, 끝내기의 병합과 worktree 지우기. Run은 첫 시범처럼 새로 만들었다(이번에는 그 판단을 새 세션이 delegate-omp.md 3을 보고 했다). 이 실행에는 작업자 질문과 후속 지시가 없었다.

## 기능 레시피 맡기기와 시작 실패 뒤 다시 띄우기(2026-11-12)

플러그인 0.9.2를 설치한 뒤, 사용자가 Orca에서 시범 저장소 `main`에 새 Claude Code 세션을 열어 `/vstack:v-mode`로 기능 하나(`todo undo <id>`: 완료 취소)를 줬다. 이 기록을 쓰는 세션은 읽기만 했다(끝난 뒤 `main`에서 수용 기준을 다시 돌린 것 말고는).

- 지휘자: `claude_82e79011_590f_4789_a262_df7fb0c5c0b4`. 근거는 그 세션의 대화 기록(`<Claude 설정 폴더>/projects/C--Users-gusdn-orca-projects-vstack-pilot-omp/142c76ae-a147-4e88-ba82-d1b29b974bb8.jsonl`), 시범 저장소의 `.local/vstack-delegate/undo/state.md`·`spec.md`, omp 세션 기록(`~/.omp/agent/sessions/-orca-workspaces-vstack-pilot-omp-undo/`), git 기록, Windows CodeIntegrity 이벤트 로그다.
- 라우터의 고르기: 첫 요청에는 맡기라는 말이 없어 라우터가 문서대로 이 대화에서 직접 구현했다(`feature`는 직접 하는 것이 기본). 사용자가 그 브랜치를 병합 없이 지우게 하고 "omp에 맡겨서 진행해"로 다시 요청했다. 라우터는 돌려 보지 않은 경로라는 것을 기록에 적고 맡겼다. 같은 세션이 그 기능을 한 번 구현해 본 뒤라, 명세(범위 밖, 수용 기준 5개)는 그 경험이 든 상태에서 쓰였다.

| 시각(UTC) | 일어난 일 |
| --- | --- |
| ~02:00 | 맡기기 전 조건 확인(`omp --version` 답함), 예약, Run 새로 만듦(`run_c1e524a81b1e`), worktree `feature/undo`(띄우기 전 HEAD=`B` `88143cb`·clean 확인). `B`에서 undo 시나리오 4개가 실패하는 것을 확인 |
| ~02:06 | `worker-start --agent omp` 실패: `failedStage: agent_readiness`, `lastError: timeout`. 명세는 전달되지 않았다. 같은 명령을 되풀이하지 않았다 |
| ~02:08 | `worker-read`로 원인을 읽음(아래). 에이전트 종료를 확인하고 `worker-release` → `released`. worktree는 HEAD=`B`·clean 그대로. 기록 `확인 필요`, 사용자에게 알리고 멈춤. 지휘자는 OS 보안 설정과 omp 설치를 바꾸지 않았다 |
| (사용자) | 사용자가 Smart App Control을 끄고 omp를 18.19.0으로 올린 뒤 "다시 맡겨"라고 함 |
| 13:38:06 | 다시 띄우기 전 확인(`omp sh -c 'echo natives-ok'` 종료 0, worktree HEAD=`B`·clean). 같은 Task로 `worker-start --task task_2ba1db58cd8c --retry-of ctx_2991d92d3589 --worktree path:<worktree> --agent omp --run <run>` → 새 Dispatch `ctx_34576c9c0ecb`, `state: ready`. 명세는 고치지 않았다. `worker-show`·`worker-read`로 시작 확인, 기록 `배정됨` |
| 13:41~13:42 | `worker_done`(`H`=`96edf70`). 작업자 질문은 없었다 |
| 13:42:03~13:42:22 | 지휘자 확인: Dispatch 끝남, clean, `H`=실제 HEAD, `B..H` 커밋 4개, AC-1~4(verify 시나리오 4개) 각각 종료 0, AC-5 `node --test test/` 20/20, 다른 시나리오 6개 종료 0, 건드리지 말 곳 변경 0. `B` 소스에 새 테스트를 얹은 임시 사본에서 새 테스트가 실패하는 것, 틀린 구현의 임시 사본에서 미완료 undo 테스트만 실패하는 것도 확인. `확인 통과` |
| ~13:50 | 사용자 지시("병합하고 지워줘"): `git merge --ff-only` → `main`=`96edf70`, `main`에서 AC-1~5 재실행, `orca worktree rm --delete-branch`(13:52:10) → 기록 `끝`. 원격이 없어 push·PR은 없다 |

- **시작 실패의 원인**: omp가 시작 직후 `Failed to load pi_natives native addon`으로 죽었다. Windows Smart App Control이 서명 없는 네이티브 모듈(`~/.omp/natives/18.18.6/pi_natives.win32-x64-baseline.node`)을 막았다(CodeIntegrity 이벤트 3077, 레지스트리 `VerifiedAndReputablePolicyState`=1). 이 PC의 설정 문제이고 vstack·Orca의 결함이 아니다. 앞선 두 실행(11-10, 11-11)에서는 같은 omp 18.18.6이 떴다. 그 사이에 무엇이 바뀌었는지는 확인하지 못했다(이벤트 로그가 11-12 08:54 KST부터만 남아 있다).
- **`omp --version`은 이 실패를 잡지 못했다.** 네이티브 모듈 없이도 버전을 답한다. 같은 상태에서 `omp --help`는 실패했고(관찰자 측정), 막힘이 풀린 뒤에는 종료 코드 0으로 사용법을 냈다. → delegate-omp.md "맡기기 전에" 4를 `omp --help`로 바꿨다.
- **같은 Task 다시 띄우기**: `--retry-of`로 띄운 새 Dispatch가 같은 Task의 명세를 받았다(`--spec-file`을 다시 주지 않았다). 실패한 Dispatch는 그 전에 `released`였다. → delegate-omp.md에 "시작 실패" 절을 더했다.
- omp(18.19.0): 메인 `anthropic/claude-opus-5-5`(fallback 아님), assistant 메시지 37개 모두 같은 모델. `task` 1회, 에이전트 `reviewer`(이름 `UndoReview`), 자식 `openai-codex/gpt-6-astra`(fallback 아님). 자식 도구는 read 9, bash 1(`git diff`)이고 쓰기가 없다. 결과는 지적 없음. 메인 세션은 13:38:08~13:43:19.
- 결과물: `B..96edf70` 커밋 4개(undo 명령 → 미완료 undo 테스트 → 없는 id 오류 → 사용법 줄·README). `bin/todo.mjs`, `src/todo.mjs`, `test/cli.test.mjs`(새 파일 66줄), `test/todo.test.mjs`, `README.md` 1줄. 동작 2(미완료에 undo)의 테스트는 앞선 구현 때문에 처음부터 통과했고, 작업자는 틀린 구현의 임시 사본으로 그 테스트가 실패할 수 있음을 확인했다고 보고했다(명세가 그렇게 시켰다).
- 관찰자 재확인(11-12 밤): `main`=`96edf70`·clean, verify 시나리오 `undo-persist`·`undo-idempotent`·`undo-missing`·`usage-undo` 각각 종료 0, `node --test test/` 20/20, worktree와 브랜치 `feature/undo` 없음, 기록 `끝`.
- 이 실행으로 처음 돌려 본 것: `feature` 레시피 맡기기(사용자 지시로), 시작 실패 뒤 `확인 필요`로 멈추기, 같은 Task 다시 띄우기. 작업자 질문과 후속 지시는 없었다.
- 한계: 맡긴 기능은 데이터 모양이 정해진 작은 것이다(기존 `done` 불리언). 지휘자가 같은 기능을 먼저 직접 구현해 봤다. 라우터가 `feature`를 스스로 맡기는 경우는 보지 않았다(기본값은 직접 하기 그대로다).

## 한계와 돌려 보지 않은 것

- 첫 시범은 지휘자가 계획을 알고 12절 초안을 직접 따랐다. 라우터를 거친 실행은 위 두 번이다(`bug-fix` 한 번, `feature` 한 번).
- 지휘자의 판단(맡기기 거부: 진행 중 작업, 레시피 없음, 위험)은 보지 않았다.
- 비정상 경로: 지휘자 재시작 뒤 이어받기, 중단, 보고 없이 끝난 작업자, 닫힌 작업자에게 보내기. 시작 실패는 "다시 띄우기"만 한 번 돌려 봤고, 맡기지 않고 닫는 길과 작업자가 무엇인가 쓴 뒤 죽은 경우는 보지 않았다.
- `refactoring`, 데이터 모양을 정해야 하는 `feature`, 간헐 버그, 준비·정리가 필요한 프로젝트.
- 세 번 돌린 결과다. 세 번 모두 omp가 `reviewer`를 골랐고 서브에이전트가 쓰지 않았지만, 늘 그런지는 모른다.

## 시범 저장소 밖에 남은 것

- Orca 등록 `vstack-pilot-omp`(repo `94015eb4-17e6-4ddd-bf4c-1867c151d62c`), 첫 시범의 worktree와 브랜치 `fix/done-invalid-id`(`763399e`, `main`에 병합하지 않음), Run `run_ba1501382a22`·`run_a888d2921607`·`run_c1e524a81b1e`. 시범 저장소 `main`은 `96edf70`이다. 정리는 사용자 확인 뒤에 한다.
- omp 전역 설정 `skills.customDirectories`(vstack 스킬 폴더, 이 시범 전에 더함. 백업 `config.yml.bak-vstack-host-neutral`).
- omp 세션 기록(위 경로)과 사전 점검 기록(`…-scratchpad-omp-probe`).
- 이 PC의 설정: 사용자가 2026-11-12에 Smart App Control을 껐고 omp를 18.19.0으로 올렸다.
