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

## 한계와 돌려 보지 않은 것

- 지휘자가 계획을 알고 12절 초안을 직접 따랐다. 라우터(v-mode)가 맡기기를 고르고 delegate-omp.md만 보고 끝까지 가는지는 보지 않았다.
- 지휘자의 판단(맡기기 거부: 진행 중 작업, 레시피 없음, 위험)은 보지 않았다.
- 비정상 경로: 지휘자 재시작 뒤 이어받기, 중단, 보고 없이 끝난 작업자, 시작 실패, 닫힌 작업자에게 보내기.
- `feature`·`refactoring`, 간헐 버그, 준비·정리가 필요한 프로젝트.
- 한 번 돌린 결과다. omp가 `reviewer`를 고르는 것, 서브에이전트가 쓰지 않는 것이 늘 그런지는 모른다.

## 시범 저장소 밖에 남은 것

- Orca 등록 `vstack-pilot-omp`(repo `94015eb4-17e6-4ddd-bf4c-1867c151d62c`), worktree와 브랜치 `fix/done-invalid-id`(`763399e`), Run `run_ba1501382a22`. 정리는 사용자 확인 뒤에 한다.
- omp 전역 설정 `skills.customDirectories`(vstack 스킬 폴더, 이 시범 전에 더함. 백업 `config.yml.bak-vstack-host-neutral`).
- omp 세션 기록(위 경로)과 사전 점검 기록(`…-scratchpad-omp-probe`).
