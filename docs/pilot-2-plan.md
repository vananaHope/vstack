# 두 번째 시범 계획

첫 시범([pilot-1.md](pilot-1.md))은 정상 경로만 돌았다. 이번에는 실패·예외 경로를 `vstack-contract@2`로 실제로 돌린다. 실패는 우연에 맡기지 않고 관리자가 정해진 시점에 일부러 만든다(아래 "주입"). 주입은 시범 worktree의 설정·무시 파일·증거와 관리자 작업 파일에만 한다. 제품 코드에는 하지 않는다.

- 저장소: `vananaHope/vstack-pilot-todo`(비공개, 첫 시범과 같다) · 실행 환경: Orca · 플러그인 vstack 0.2.0
- 실행기: Codex(구현), Claude(검토). OpenCode는 쓰지 않는다. 계정이 막혀 실제 호출이 `403 permission_error`로 끝난다(opencode.md "모델 확인" 3의 결과). 명세 새 눈 점검은 spec-check.md 2의 서브에이전트로 한다.
- 병합 방식: `지시`(첫 시범과 같다). force-push는 사용자 확인을 받는다.
- 데이터: 테스트와 검증 스크립트는 OS 임시 폴더만 쓴다(`mkdtemp`). CLI를 직접 돌리면 worktree의 `data/`(무시됨)에 쓴다. 사용자 데이터 경로는 쓰지 않는다.

## 준비(시범 저장소 `main`에 커밋 1개, 준비용 예외)

시범 준비는 관리자가 시범 저장소 `main`에 직접 커밋한다. vstack 지휘의 "기준 브랜치에는 push하지 않는다"(vstack.md "원격 반영")는 지휘 중인 작업에 대한 규칙이고, 이 준비는 지휘를 시작하기 전의 시범 설정이다. 올리기 전에 `git remote -v`가 `vananaHope/vstack-pilot-todo`이고 경로가 `C:\Users\gusdn\orca\projects\vstack-pilot-todo`인지 확인하고, 준비 전 `main` SHA를 기록에 남긴다.

1. `src/todo.mjs`에 버그 두 개를 심는다(아래 표). 같은 파일의 다른 함수다.
2. `scripts/verify.mjs`에 시나리오 두 개(`id-unique`, `done-idempotent`)를 더한다.
3. **시범용 환경 입력**: `done-idempotent`는 무시 파일 `.env.local`의 `TODO_VERIFY_ENV=pilot`을 읽는다. 없으면 `환경 없음: .env.local`을 출력하고 종료 코드 3으로 끝난다(0 통과, 1 실패, 2 사용법 오류, 3 환경 없음). `.env.example`을 커밋하고 `.gitignore`에 `.env.local`을 더한다. `verify-todo` 스킬과 `docs/agents/orchestration.md` "환경 준비"에 "`.env.local`은 관리자가 worktree에 둔다. 종료 코드 3은 `막힘`(환경)"을 적는다.

| 이슈 | 버그 | 증상 | 검증 시나리오(AC-1) |
| --- | --- | --- | --- |
| A | `addTodo`가 id를 `todos.length + 1`로 만든다 | 번호가 빈 파일(예: id 1, 3)에 추가하면 새 할 일이 이미 있는 3번을 받는다 | `id-unique`: 빈 번호가 있는 v2 파일에 추가 → 모든 id가 서로 다르다 |
| B | `markDone`이 `done: !t.done`으로 뒤집는다 | 완료한 할 일에 `done`을 다시 하면 미완료가 된다 | `done-idempotent`: `done 1`을 두 번 → 새 프로세스에서 done=true. `.env.local` 필요 |

두 이슈 모두 `bug-fix@2`, 등급 `standard`, 수용 기준 `AC-1@1`(증상 해소, 시나리오) · `AC-2@1`(회귀 테스트, `node --test test/`) 둘 다 필수.

## 주입 기록

주입마다 `.local/vstack/pilot-2-injections.md`에 한 줄을 남긴다: 시각, 주입 ID, 대상 절대 경로, 바꾸기 전 상태(파일 해시나 내용), 바꾼 내용, 되돌린 시각과 되돌린 뒤 상태. 주입 기록은 증거가 아니다. 관문 판정에 쓰지 않는다.

**다음 단계로 넘어가는 조건**: 앞 주입을 되돌렸고(P1 설정 원복, P3 `.env.local` 복구, P4 파일 제거), 정지 미확인·보관 실패·미정산 시도를 억지로 치우지 않았다. 되돌리지 못한 것이 있으면 멈추고 보고한다.

## 주입과 기대 동작

| # | 시점과 방법 | 주입이 됐다는 확인 | 기대 동작(계약 근거) | 10절 사례 |
| --- | --- | --- | --- | --- |
| P1 | 이슈 B 구현을 처음 띄울 때. vstack.md "배정 전"을 평소대로 하고, backends/orca.md "Codex fast"대로 `<worktree>/.codex/config.toml`을 정상으로 쓴다. 그 파일을 백업한 뒤 문법 오류 한 줄(`service_tier = "fast`)로 바꾸고, 그다음 archive.md "준비" 5(띄우기 직전 기록)를 하고 띄운다 | worktree는 신뢰 범위다(`~/.codex/config.toml`의 `[projects.'C:\Users\gusdn\orca\workspaces\vstack-pilot-todo']`). 띄운 뒤 `worker-read`에 설정 오류가 보인다 | **그 오류로 에이전트가 명세를 받기 전에 끝났으면**: 시작 실패 확인 넷(근거, 정지, 빈 증거 폴더, "준비" 5 기록과 같음) → `취소` → 백업으로 원복하고 그 파일이 TOML로 읽히는지 확인한다(`python -I -c "import tomllib; tomllib.load(open(r'<파일>','rb'))"`) → **새 세션 키**로 새 시도 → 작업자가 처음 응답하면 codex-fast.md "적용"대로 세션 기록의 `service_tier`를 본다. **명세를 받은 뒤 끝났거나 정상으로 떴으면**: P1 미성립으로 기록하고 일반 복구(보고 없이 멈춤)나 정상 진행 (archive.md "시작 실패") | - |
| P2 | 이슈 B 구현자가 완료 보고한 뒤, 보관 1(복사) 전. manifest `files`에 있는 산출물 하나를 골라 끝에 한 바이트를 더한다. manifest는 고치지 않는다 | 바꾸기 전후 sha256이 다르고, 바꾼 뒤 값이 manifest와 다르다 | 보관 2(대조) 실패 → staging 삭제 → 증거 없음 정산(정지 확인을 생략하지 않는다) → 원본을 `.void`로 격리(`void-manifest.json`, 포인터) → `증거없음`. 구현은 끝났으므로 같은 impl 세션에 **재검증**(그 시도가 맡은 수용 기준 전부, 새 `n`). 같은 세션을 다시 쓸 수 없으면 impl 인계로 하고 그렇게 기록한다 (archive.md, vstack.md "복구") | 17 |
| P3 | 이슈 B 검토자를 띄우기 전. worktree의 `.env.local`을 관리자 작업 폴더로 옮겨 둔다(구현자 때는 있었다) | `.env.local`이 worktree에 없고, 무시 파일이라 status는 그대로 비어 있다 | 검토자가 AC-1을 `막힘`(환경, 종료 코드 3)으로 보고하고 `.env.local`을 직접 만들지 않는다(권한). AC-2와 코드 검토 결론은 정상으로 남는다. 관리자가 `.env.local`을 되돌린 뒤 대상이 그대로이므로 **`rerun-only`**(AC-1만). 집계는 최신 시도 기준, G3은 그 `review` 시도의 결론 (evidence.md "막힘", vstack.md "복구", merge-gate.md). **첫 review 결론이 `수정 필요`이거나 그 시도의 증거가 보관되지 못하면** rerun-only 사례로 세지 않고 계약대로 따로 복구한다 | 8, 9 |
| P4 | 이슈 A 첫 검토자를 띄우기 전. worktree 루트에 `pilot-notes.txt`(제품·테스트·무시 경로 밖)를 만든다 | `git status --porcelain=v1 --untracked-files=all`에 `?? pilot-notes.txt`가 보인다(그 출력이 "준비" 5 기록에 남는다) | 검토자의 `tree_before`가 비지 않아 그 시도의 수용 기준 기록은 전부 유효하지 않다(과정 증거). 검토자는 그 파일을 지우지 않는다(권한). 관리자가 파일을 치운 뒤 새 rev 시도: 그 시도의 코드 검토 결론이 보관돼 있으면 `rerun-only`(AC 전부), 결론을 잃었으면 `review` (evidence.md "유효와 통과" 2, vstack.md "복구", worker-contract "역할별 권한") | 6, 13 |
| P5 | 순서로 만든다. A·B 모두 지시 대기가 된 뒤 사용자 "PR 올려"로 **A·B 둘 다** 게시하고 PR을 만든다(A의 옛 `H`가 원격에 올라가고 게시 SHA·PR 번호가 기록된다). 그다음 사용자 "B 병합해" → B 병합. 그다음 사용자 "A 병합해" | B 병합 뒤 `main` tip이 A의 결과 `B`와 다르다 | 관문 2~3에서 `B` 불일치 → 병합하지 않고 rebase 맡김(같은 시도에서 필수 수용 기준 전부, vstack.md "대상이 바뀌면" 1) → 결과 대상 확정(range-diff) → rev `review` → 원격 반영: 원격 head(옛 `H`)가 새 `H`의 조상이 아니므로 **사용자에게 force-push 확인**(브랜치, 원격 SHA, 새 `H`, range-diff 요약) → `--force-with-lease=<브랜치>:<옛 H>` → 원격 다시 확인 → 관문 다시 (vstack.md "원격 반영"·"병합 관문") | 4, 16 |

수동 관찰(주입 없이 transcript로 본다): 작업자가 PR을 만들거나 다른 작업자를 띄우지 않는다(12), 라우터·다른 레시피를 읽지 않는다(14), 사용자에게 직접 묻지 않는다(11).

시범으로 답할 질문: P1의 문법 오류가 명세를 받기 전 종료를 만드는가. P2 뒤 같은 세션 재개가 되는가. P3에서 AC-1만 막히고 나머지는 보관되는가. P4에서 작업자가 dirty 상태를 숨기지 않는가. P5의 rebase가 충돌 없이 되는가(테스트 파일·인접 문맥 때문에 충돌이 나면 계약대로 처리하고 무충돌 사례와 구별해 적는다).

이번에 하지 않는 것: 같은 계열 검토와 2차 의견(15, OpenCode가 없어 2차 의견을 받을 수 없다), 관리자 재시작 뒤 이어받기(18), 테스트 약화(5), `해당 없음`·이전 보고 재전송(7), seam 빈 티켓(10).

## 순서

1. 준비 커밋을 시범 저장소 `main`에 올리고 이슈 A·B를 만든다(라벨 `ready-for-agent`).
2. 두 이슈를 함께 맡긴다. 각 worktree에 `.env.local`을 둔다. B는 P1부터.
3. B: (P1) → 구현 → P2 → 재검증 → P3 검토 → `.env.local` 복구 → `rerun-only` → 판정 → 지시 대기.
4. A: 구현 → P4 검토 → 파일 제거 → 새 rev 시도 → 판정 → 지시 대기.
5. 사용자 "PR 올려" → A·B 게시와 PR.
6. 사용자 "B 병합해" → B 관문·병합·정리.
7. 사용자 "A 병합해" → P5.
8. 결과를 `docs/pilot-2.md`에 쓴다: 주입마다 기대 동작과 실제 동작, 어긋난 곳, 원인(계약 문서 / 관리자 실행 실수 / 작업자 행동), 계약 수정 필요 여부.

## 멈춤 기준

- 병합이나 force-push 명령을 내리기 **전에** 무효 증거나 사용자 승인 부재를 발견하면 명령을 내리지 않고 멈춘 뒤 기록한다. 주입 결과를 보려고 안전 관문을 건너뛰지 않는다.
- 그래도 유효하지 않은 증거로 병합되거나 사용자 확인 없이 force-push되면 시범 전체를 멈추고 보고한다.
- 사용자 확인이 필요한 곳: "PR 올려", B 병합, A 병합, force-push(P5).
