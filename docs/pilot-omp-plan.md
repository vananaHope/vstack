# omp 맡기기 시범 계획

[design.md](design.md) 12절 "omp에 맡기기"(제안·미검증)를 처음 돌려 본다. Claude Code 지휘자가 한 세션 크기의 버그 수정 하나를 omp 작업자에게 새 worktree로 맡기고, omp가 자기 설정대로 서브에이전트를 쓰는지, 지휘자가 기존 Orca 절차(`skills/orchestrate-issues/backends/orca.md`)로 끝까지 다룰 수 있는지 본다. 결과로 12절을 고친 뒤 v-mode에 넣는다.

- 지휘자: 이 Claude Code 세션. 12절은 아직 v-mode에 없으므로 지휘자는 **12절을 직접 읽고 따른다**. 라우터의 고르기는 이 시범의 대상이 아니다.
- 작업자: omp 18.18.6, `--agent omp`, `--model`·`--effort` 없음.
- 레시피: `bug-fix@4`, 한 세션 절차 범위(12.3). 계약 밖이다. 증거 보관·교차 검토·병합 관문은 없다.
- 실행 환경: Orca. 시범 5(`vstack-pilot-todo`, 다른 세션 진행 중)와 저장소·Run을 나눈다.
- 한계: 지휘자가 이 계획을 안다. 지휘자의 판단(거부·고르기)은 스스로 채점하게 되므로 이번 결과로 세지 않는다. 보는 것은 작업자와 Orca의 실제 동작이다. 질문과 후속 지시는 일부러 넣은 것이라, 질문이 필요한지 omp가 스스로 판단하는 능력은 보지 않는다.

## 준비

1. **시범 저장소**: `C:\Users\gusdn\orca\projects\vstack-pilot-omp`에 `vstack-pilot-todo`의 `main`(`99168cf`)을 로컬 복제한다. `origin`을 지우고 `git remote -v`가 빈지 본다. 기본 push 경로를 없애고 명세로 push·PR을 금지하는 것이다(명시적 URL push까지 기술적으로 막지는 않는다). GitHub에는 만들지 않는다.
2. **실행 기반(준비 커밋)**: 이번 세션 scratch 시범의 verify 시나리오 커밋 `f5fc068`(`done-invalid-id` 시나리오, 기능 문서, README 줄. 수정 코드 없음. 앞 0(`01`) 입력은 다루지 않음을 확인함)을 `git cherry-pick --no-commit f5fc068`로 얹는다. `git diff --cached --stat`에 `bin/`·`src/`·`test/`가 없는지 보고 커밋한다. 원본 SHA와 새 커밋 SHA `B`를 적는다. `node scripts/verify.mjs done-invalid-id --out <임시>`가 종료 코드 1이고 결과에 `오류: no todo with id NaN`이 나오는지(기대한 실패인지) 본다.
3. **Orca 등록**: `orca repo add`로 등록하고 `orca repo show`로 확인한다.
4. **`.local/` 무시**: 메인 저장소에서 `git check-ignore .local/x`. 아니면 `.git/info/exclude`에 `/.local/`을 더한다.
5. **omp 설정 기록**: `omp --version`, `omp config get modelRoles`, `omp config get retry.fallbackChains`를 기록한다. **이번 시범은 전역 omp 설정을 바꾸지 않는다.** 시범이 끝나면 같은 값을 다시 읽어 비교한다. 기대(가설): omp 메인은 `modelRoles.default`, 서브에이전트(`task`)는 `modelRoles.task`.
6. **omp 기록 형식 확인(사전 점검)**: scratch 폴더의 버려도 되는 저장소에서 `omp -p --no-tools`가 아닌 기본 도구로 "서브에이전트에게 README를 읽기 전용으로 한 줄 요약시키고 그 결과를 답하라"를 한 번 돌린다. 생긴 세션 기록에서 다음을 찾을 수 있는지 본다: 세션 ID·cwd·시각, 메인 모델(provider·model), 서브에이전트 호출 ID와 그 자식 기록의 위치, 자식의 모델, 자식의 도구 호출과 결과(셸 포함), 자식 종료. 찾은 형식을 시범 기록에 적는다. 못 찾는 항목은 시범에서 그 관측을 `미확인`으로 판정한다.
7. **Run**: `orca orchestration run-create --objective "vstack-pilot-omp omp 맡기기 시범"`. 결과의 Run ID를 기록하고 `run-current`로 이 지휘자에 묶였는지 본다. 이후 Run을 받는 orchestration 명령에만 `--run <그 ID>`를 붙인다(`worktree create`에는 없다).
8. **기준 목록**: 맡기기 전에 `orca orchestration worker-list --json`(Run 지정 없이, 그리고 시범 5 Run `run_368dd5ac3393`), 결과에 `nextCursor`가 있으면 끝까지 읽어 지금 있는 Dispatch 목록을 남긴다. 시범 5는 진행 중이라 새 작업자가 정상으로 생길 수 있다. 이번 시범의 잘못 배정인지는 그 Dispatch의 Run·Task·worktree·생성 시각으로 판정한다. 시범 5 작업자는 정지하지 않는다.

준비 결과(1~8)를 사용자에게 보이고 확인받은 뒤 맡긴다.

## 맡길 일

- 이름: `done-invalid-id`. 작업 브랜치: `fix/done-invalid-id`.
- 증상: `todo done abc`처럼 숫자가 아닌 id를 주면 `오류: no todo with id NaN`이 나온다.
- 기대 동작: id가 양의 정수가 아니면 표준 오류에 `오류: invalid id <입력값>`, 종료 코드 1, 데이터 파일은 그대로다.
- 수용 기준:
  - `AC-1` 증상 해소(필수): `node scripts/verify.mjs done-invalid-id --out <OS 임시 폴더>` 종료 코드 0.
  - `AC-2` 회귀 테스트(필수): `node --test test/` 종료 코드 0, 증상을 잡는 테스트가 실행 목록에 있다.
- seam: CLI 프로세스 경계(`node bin/todo.mjs done <id>`).
- 재현 경로: `TODO_DATA=<임시 파일> node bin/todo.mjs add 우유` 뒤 `... done abc`. 결정적.
- 준비·정리: 없음(임시 데이터 파일만).
- 건드리지 말 곳: `src/store.mjs`, `scripts/verify.mjs`, `.claude/skills/`.
- **시험용 예외(질문)**: 12.4의 1은 입력을 맡기기 전에 확정하라고 한다. 이번에는 `ask → reply → 이어 감` 전달 경로를 보려고 하나를 일부러 열어 둔다. 명세: "`01`처럼 앞에 0이 붙은 id를 받을지는 정하지 않았다. 구현 전에 `ask`로 지휘자에게 물어라." 정해 둔 답: "받지 않는다(`오류: invalid id 01`, 종료 코드 1)."

명세는 12.4의 5에 적힌 항목을 모두 넣어 `.local/vstack-delegate/done-invalid-id.spec.md`로 쓰고 `--spec-file`로 넘긴다.

## 순서와 기대 동작

12.4의 단계 번호를 쓴다.

1. **입력**: 위 "맡길 일".
2. **예약**: `.local/vstack-delegate/done-invalid-id.md`를 `예약`으로 쓴다(지휘자, `B`, 브랜치, Run).
3. **Run**: 준비 7의 Run.
4. **worktree**: `orca worktree create --name done-invalid-id --branch fix/done-invalid-id --repo path:<시범 저장소> --base-branch main --setup run --json`. 띄우기 전에 그 worktree의 HEAD가 `B`, status가 빈지 본다. 아니면 멈춘다.
5. **띄우기**: `orca orchestration worker-start --spec-file <명세> --worktree path:<worktree> --agent omp --task-title "done-invalid-id: 숫자가 아닌 id 오류" --run <run>`. 모델 옵션 없음.
6. **제출 확인**: Task·Dispatch·터미널을 기록하고 `배정됨`.
7. **질문**: 작업자의 `ask`가 오면 그 메시지 ID를 기록하고 정해 둔 답을 `reply --id <그 ID>`로 보낸다. 성립 조건: 답이 그 질문 ID에 연결됐고, 답을 받은 뒤에 첫 구현 쓰기(`bin/`·`test/` 파일 쓰기)가 있었다(세션 기록·`worker-read`). 구현 쓰기가 질문보다 먼저였으면 "전달 경로는 성립, 순서는 어김"으로 나눠 적는다. 질문 없이 구현했으면 미성립으로 적고 계속한다.
8. **확인**: `worker_done`을 받으면 12.4의 8대로 확인한다(Dispatch 끝남, 서브에이전트 끝남, clean, 보고한 `H` = 실제 HEAD, `B..H` diff, AC-1·AC-2 직접 재실행, 재실행 뒤 HEAD·status 그대로). 질문의 답(`01` 거부)이 동작에 반영됐는지도 본다.
9. **후속 지시**: 확인이 처음부터 실패하면 그 실패를 보낸다. 통과하면 **시험용 후속 요구 하나를 보낸다**(이 계획을 승인하면 이 요구 변경도 승인한 것으로 본다): "사용법 줄의 `todo done <id>`를 `todo done <id(양의 정수)>`로 바꾸고, 인자 없이 실행했을 때 그 줄이 나오는지 보는 테스트를 더하라." `send`로 보내고 새 Dispatch를 기록한다. 성립 조건: 새 Dispatch의 `worker_done`, 새 커밋, 새 HEAD `H2`에서 8을 다시 해 통과. 첫 구현이 이미 이 요구를 채웠으면 후속 시험은 미성립으로 적는다(다른 요구를 즉석에서 만들지 않는다). 결과에는 실제 확인 실패였는지 시험용 요구였는지 나눠 적는다.
10. **끝내기**: push·PR은 없다. "정리"로 모든 Dispatch가 `released`인지 확인한다. worktree는 시범 기록을 쓸 때까지 남긴다. 기록을 `끝`으로. 준비 5의 omp 설정을 다시 읽어 비교한다.

## 관측할 것

Orca 상태(`worker-show`, `worker-list`, `inbox --full`)와 준비 6에서 확인한 omp 세션 기록 형식으로 본다. 기록이 없거나 불완전한 항목은 `미확인`으로 판정한다(통과로 치지 않는다).

- **O1 시작**: 기록·Run·Task·Dispatch·worktree가 맞는가. 시작 HEAD가 `B`인가. 작업이 실제로 시작됐는가(`worker-read`).
- **O2 보고 경로**: `ask`·`worker_done`이 Orca 절차대로 오는가(7·9의 성립 조건). 후속 지시를 같은 터미널에서 받고 새 Dispatch로 보고하는가. 기존 worktree 작업자의 자동 닫힘과 `send`로 다시 열림이 backends/orca.md대로인가.
- **O3 모델**: 세션 기록의 메인 provider·model이 준비 5의 `modelRoles.default`와 같은가. 다르면 fallback(`retry.fallbackChains`), 역할 선택, 설정 변경(전후 비교) 가운데 무엇인지 구분해 적는다.
- **O4 서브에이전트**: 서브에이전트 호출 ID와 자식 기록, 자식의 모델(기대 `modelRoles.task`), 자식의 도구 호출(셸 포함)에 쓰기가 있었는가, 자식이 끝났는가. 판정: 호출 없음 = "다른 모델 검토 미관측", 자식의 쓰기 = 명세 위반, 기록으로 판정 불가 = `미확인`. 최종 clean만으로 "쓰기 없음"이라 하지 않는다.
- **O5 경계**: omp·자식의 도구 기록에 `orca` 작업자 생성 명령이 없는가, 준비 8의 기준 목록 대비 이번 Run·worktree에서 새로 생긴 Dispatch가 맡긴 것뿐인가. 지휘자 쪽은 이 세션의 도구 기록에 그 worktree를 고친 명령이 없는가. 커밋이 작업 브랜치에만 있는가. 관측 범위 밖의 실행은 `미확인`.
- **O6 확인**: 모든 하위 작업(서브에이전트 포함)이 끝난 뒤의 HEAD에서 확인했고, 그 뒤 HEAD·status가 그대로인가.

## 비정상 경로(이번에는 시험하지 않음)

12.6의 "비정상"(지휘자 재시작, 중단 요청, 보고 없이 끝남, 거부)은 정상 경로가 통과한 뒤 따로 계획한다. 시범 기록에 "미검증"으로 적는다. 시범 중 실제로 생기면 아래 멈춤 기준을 따른다.

## 멈춤 기준

- `run-create`, `worktree create`, `worker-start`, `send`, `reply`, `worker-stop`, `worker-release`의 결과가 불명확하면(응답 없음, `outcome_unknown`, `stop_unknown`, `release_unknown` 등) 기록을 `확인 필요`로 두고 멈춘다. 같은 명령을 되풀이하지 않고, 새로 만들거나 다시 보내지 않는다. 조회(`run-list`, `orca worktree show`, `worker-show`, `worker-list`, `inbox --full`, `request-show`)로 이미 효과가 났는지 먼저 본다.
- 실제로 중단하거나 지휘로 넘겨야 하면 "정지"로 정지를 확인한 뒤 `끝(중단)`/`끝(지휘로 넘김)`으로 닫고, 자원 해제("정리")는 따로 기록한다. worktree 삭제는 모든 Dispatch가 `released`인 뒤에만, 사용자 확인으로.
- omp가 Orca 작업자를 띄웠으면 그 작업자를 정지 확인하고 멈춘다(O5 위반).
- 기준 목록 대비 이번 시범이 잘못 배정한 작업자가 시범 5 쪽에 생겼으면 멈추고 사용자에게 알린다. 출처가 불명확하면 조회만 하고 멈춘다. 시범 5 작업자는 정지하지 않는다.
- 지휘자가 맡긴 worktree를 고쳐야 할 것 같으면 고치지 않고 멈춘다.
- 서브에이전트 쓰기: 맡긴 worktree 밖(전역 설정, 다른 저장소, 시범 5)에 썼거나 아직 쓰는 중이면 작업자를 정지 확인하고 영향을 확인한다. 맡긴 worktree 안에서 이미 끝난 쓰기면 위반으로 기록하고 정상 경로는 끝까지 간다. 다만 건드리지 말 곳(`scripts/verify.mjs`, `src/store.mjs`, `.claude/skills/`)이 바뀌었으면 누가 썼든 그 결과를 `확인 통과`로 치지 않는다. 검증 기준이 바뀌었을 수 있으므로 `B`의 파일과 비교해 무결성을 본 뒤 관측만 이어 간다.
- 전역 omp 설정이 시범 중에 바뀌었으면(전후 비교) O3·O4를 `미확인`으로 두고 사용자에게 알린다.
- 사용자 확인이 필요한 곳: 준비 결과, 시범 기록 작성, worktree·브랜치·시범 저장소·Orca 등록 정리.

## 시범 기록

사용자의 "시범 기록을 써라" 뒤 `docs/pilot-omp.md`에 쓴다: 단계별 기대·실제, 7·9의 성립 여부, O1~O6 답(`미확인` 포함), 어긋난 곳과 원인(12절 문서 / Orca 동작 / omp 동작 / 실행 실수), 12절과 v-mode에 고칠 것, 미검증으로 남은 것.

## 이번에 하지 않는 것

비정상 경로(재시작·중단·보고 없이 끝남·거부), 지휘자 판단(고르기·거부) 채점, omp가 질문 필요성을 스스로 판단하는지, feature·refactoring 레시피, 지휘와 맡기기 동시 진행, 라우터(v-mode) 경유 실행, push·PR·병합, 전역 omp 설정 변경.
