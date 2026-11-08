# 01. 정상 경로와 변형

## 티켓

- 작업 이름: `issue-42` · 레시피: `bug-fix@2` · 등급: `standard` · PR: #57
- 증상: 할 일을 완료로 체크한 뒤 새로고침하면 미완료로 돌아온다.

| ID | 필수 | 내용 | 검증 명령 |
| --- | --- | --- | --- |
| `AC-1@1` | 예 | 체크한 할 일이 새로고침 뒤에도 완료 상태다 | `npm run verify -- toggle-persist`(verify 스킬) |
| `AC-2@1` | 예 | 지속성 회귀 테스트가 통과한다 | `npm test -- persistence` |

### 입력 검사([intake.md](../../skills/v-mode/contracts/intake.md))

| 항목 | 값 |
| --- | --- |
| 레시피 | `bug-fix@2`, `<vstack>/skills/v-mode/recipes/bug-fix.md` |
| seam | 저장소에서 목록을 읽는 경계(`loadTodos`) |
| 재현 경로 | 앱 실행 → 할 일 하나 체크 → 새로고침 |
| 실행 조건 | bash(Git Bash), 실창 불필요 |
| 준비·정리 | `.claude/skills/verify-todo/SKILL.md`의 Launch·Doctor·Teardown |
| impl 권한 | worktree `C:\wt\issue-42`, 증거 `C:\wt\issue-42\.vstack\evidence\issue-42\<시도 ID>\` |
| rev 권한 | 증거 폴더 같음, 보고서 `<메인>\.local\vstack\issue-42\review-<k>.md`, scratch `C:\wt\issue-42\.vstack\scratch\<시도 ID>\` |
| 보관 준비 | `.vstack/`를 info/exclude에 넣음, 시도 표에 `배정됨` |

모두 있음 → 배정.

## 01a. 정상

### 시도 표

| 시도 ID | 역할 | scope | 맡은 AC | 실행기 | 세션 | 대상 | 상태 | 결과 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `impl-d195b9cc-1` | impl | | AC-1, AC-2 | codex@high | `term-c1` | (H1=1111aaa, B1=bbbb001) | 정리됨 | AC-1 통과, AC-2 통과 |
| `rev-3ecbf1e7-1` | rev | review | AC-1, AC-2 | claude | `term-r1` | (H1, B1) | 정리됨 | AC-1 통과, AC-2 통과. 지적 사소 1(변수 이름). 결론 `통과` |

구현자는 원인(앱 시작 시 빈 목록으로 저장값을 덮음)을 찾고, 실패 테스트 커밋 → 수정 커밋 순서로 쌓았다. 두 시도 모두 `tree_before` 빈 값, 이 시도에서 H1으로 빌드한 서버를 썼다.

### 집계(대상 H1/B1)

| AC | impl(가장 나중 배정) | rev(가장 나중 배정) | 집계 |
| --- | --- | --- | --- |
| AC-1@1 | `impl-d195b9cc-1` · 통과 | `rev-3ecbf1e7-1` · 통과 | 통과 |
| AC-2@1 | `impl-d195b9cc-1` · 통과 | `rev-3ecbf1e7-1` · 통과 | 통과 |

5단계 판정: 사소 1은 이슈 #43의 범위라 `다른 이슈로 넘김`(#43에 댓글).

### 관문("병합해" 지시 직후. B를 다시 읽으니 여전히 B1)

| G1 | G2 | G3 | G4 | G5 | 결과 |
| --- | --- | --- | --- | --- | --- |
| 통과 | 통과 | 통과(`rev-3ecbf1e7-1` 결론 통과, 지금 고침 없음, 사용자 질문 없음) | 통과(2개 정리됨) | 통과(rev는 커밋 안 함, claude ≠ codex) | 병합 명령 |

`gh pr merge 57 --squash --match-head-commit <H1>` → `gh pr view 57 --json state,...`가 `MERGED`, `baseRefName: main` → **병합 확인**. squash 커밋의 부모가 B1 → 경쟁 없음.

## 01b. 최신 실패 증거

01a의 `rev-3ecbf1e7-1`에서 AC-1을 돌리자 새로고침 2초 뒤 다시 미완료로 돌아갔다(늦게 도착한 동기화 응답이 덮어씀).

| AC | impl | rev | 집계 |
| --- | --- | --- | --- |
| AC-1@1 | `impl-d195b9cc-1` · 통과 | `rev-3ecbf1e7-1` · **실패 · 유효** | **실패** |
| AC-2@1 | `impl-d195b9cc-1` · 통과 | `rev-3ecbf1e7-1` · 통과 | 통과 |

- G1 실패 → **차단**. 검토 결론 `수정 필요`, 차단 지적 1.
- 5단계 `지금 고침`. 설계를 다시 잡는 수정이므로 원래 구현자 세션(`term-c1`)에 보낸다. 간헐 버그가 드러났으므로 레시피 예외에 따라 명세에 반복 재현 10회를 더한다.
- 수정 뒤 H2. 진입점 "지금 고침 수정 뒤": `impl-d195b9cc-2`(같은 세션 `term-c1`, 변경 작성자)가 (H2, B1)에서 AC-1·AC-2 전부, 재검토는 `rev-3ecbf1e7-2`(`term-r1`, `scope: review`)로 지적 해결 판정 + 수정 diff + 브랜치 전체 + AC 전부.

## 01c. 수용 기준은 통과, 중요 지적이 남음

AC-1·AC-2는 두 역할 모두 통과. 그런데 `rev-3ecbf1e7-1`이 "가져오기 기능(`importTodos`)도 같은 방식으로 저장값을 덮는다"를 `중요`로 지적했다. 결론 `수정 필요`.

- G1 통과, G3 **실패**(가장 나중 `review` 시도의 결론이 `수정 필요`, `지금 고침` 미해결) → **차단**.
- 5단계: 같은 이슈 범위라 `지금 고침`. 고치면 H가 바뀌므로 01b와 같은 경로.

## 01d. light 등급의 관리자 검토

같은 티켓을 `light`로 정했다고 하자. orchestra 기본 light 검토 목록은 `관리자 → claude → codex`다.

- 첫 버전에서 관리자는 검토자 역할을 맡지 않으므로 `관리자`를 건너뛴다.
- 구현자가 `opencode`면 다음 항목 `claude`가 다른 계열이므로 검토자로 고른다.

## 01e. dirty tree로 만든 증거

`impl-d195b9cc-1`이 마지막 수정을 커밋하기 전에 AC-1을 돌렸고, `tree_before`가 ` M src/store.ts`였다.

- `tree_before`는 시도 전체의 필드다. 그래서 그 시도의 AC-1뿐 아니라 AC-2 기록도 유효하지 않다(유효 조건 2). 둘 다 과정 증거로만 남는다.
- AC-1@1·AC-2@1의 impl 집계 **증거 없음** → G1 실패 → 차단.
- 관리자는 같은 세션에 새 시도 `impl-d195b9cc-2`(맡은 AC: **AC-1, AC-2**)로 커밋된 H1에서 다시 돌리라고 보낸다. AC-1만 맡기면 AC-2는 여전히 `impl-d195b9cc-1`에서 골라져 증거 없음으로 남는다. 이전 폴더는 바꾸지 않는다.
- `impl-d195b9cc-2`: `tree_before` 빈 값, AC-1·AC-2 통과 → 보관 → `정리됨`.

| AC | impl(가장 나중 배정) | rev | 집계 |
| --- | --- | --- | --- |
| AC-1@1 | `impl-d195b9cc-2` · 통과 | `rev-3ecbf1e7-1` · 통과 | 통과 |
| AC-2@1 | `impl-d195b9cc-2` · 통과 | `rev-3ecbf1e7-1` · 통과 | 통과 |

- 대상은 (H1, B1) 그대로라 rev를 다시 돌릴 필요가 없다. 관문 재판정: G1 통과, G2 통과, G3 통과(`rev-3ecbf1e7-1`), G4 통과(3개 정리됨), G5 통과 → 병합 가능.

## 01f. 사소 지적을 지금 고침으로 정함

01a에서 사소 1을 `지금 고침`으로 정했다고 하자.

1. `fixes.md` "코어의 그 밖의 수정": `light` 목록에서 검토자(claude)와 같은 계열을 건너뛰어 `opencode`가 같은 worktree에서 고친다. 새 세션 `term-o1`, 시도 `impl-9f9f9f9f-1`. H2=2222ccc.
2. 이 세션이 (H2, B1)의 변경 작성자이므로 impl이다. AC-1·AC-2 전부를 (H2, B1)에서 돌린다. 통과.
3. 관리자 확인: 수정 diff를 읽고 사소 1이 고쳐졌다고 판정해 `minor-check-1.md`에 남긴다. 이것은 G3의 "지금 고침 해결" 기록이다.
4. 진입점 "사소 수정 뒤": rev `review` 시도를 하나 배정한다. `rev-3ecbf1e7-2`(세션 `term-r1`, claude, scope `review`, 맡은 AC: AC-1·AC-2). 수정 diff를 검토하고 AC 전부를 돌린다. 결론 `통과`.

| 판정 근거 | 시도 |
| --- | --- |
| G1의 impl 기록 | `impl-9f9f9f9f-1` |
| G1의 rev 기록 | `rev-3ecbf1e7-2` |
| G3의 결론 | `rev-3ecbf1e7-2`(T=(H2, B1)의 가장 나중 `review` 시도) |
| G3의 지금 고침 해결 | `minor-check-1.md` |
| G5 | rev 세션 `term-r1`은 H2에 커밋하지 않았고, claude ≠ opencode(변경 작성자) |

모두 통과 → 병합 명령(`--match-head-commit <H2>`).

만약 4에서 `rev`를 `rerun-only`로 배정했다면: 대상이 바뀐 뒤의 첫 rev 시도는 `rerun-only`일 수 없으므로 배정이 잘못됐다. 그대로 진행해도 T=(H2, B1)에 `review` 시도가 없어 G3 실패 → 차단.

## 이 예시에서 쓴 계약

evidence.md(유효와 통과, 집계, 역할 자격, 최신성, scope), merge-gate.md(판정식, 진입점, 병합 명령과 확인), worker-contract.md(검토자 실행 환경, 증거 쓰기), intake.md, priority.md(반복 재현 충돌의 답).
