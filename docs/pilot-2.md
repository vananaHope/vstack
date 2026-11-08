# 두 번째 시범 기록

- 날짜: 2026-11-08 · 실행 환경: Orca · 계약 `vstack-contract@2` · 레시피 `bug-fix@2` · 플러그인 vstack 0.2.0
- 계획: [pilot-2-plan.md](pilot-2-plan.md)(Codex 검토 2회, "실행 가능")
- 저장소: `vananaHope/vstack-pilot-todo`. 준비 커밋 `d7ed08d`(버그 두 개, 검증 시나리오 두 개, 시범용 환경 입력 `.env.local`)
- 이슈 A #3 → PR #5 → squash `59a71e2` · 이슈 B #4 → PR #6 → squash `de6b8c6`
- 작업 파일: 그 저장소의 `.local/vstack/issue-3/`, `issue-4/`, `pilot-2-injections.md`(주입 기록), `assign-log.md`
- 걸린 시간: 첫 배정 22:26 → A 병합 23:07(약 41분). 작업자 실행 10번(Codex 5: 구현 2·재검증 1·rebase 1·시작 실패 1, Claude 5: review 3·rerun-only 2)과 명세 새 눈 점검 서브에이전트 2번

## 주입 결과

다섯 주입 모두 기대 동작과 실제 동작이 같았다. 유효하지 않은 증거로 병합되거나 확인 없이 force-push된 일은 없었다.

| # | 주입 | 실제 동작 | 판정 |
| --- | --- | --- | --- |
| P1 | B 첫 구현 전에 worktree `.codex/config.toml`을 문법 오류로 바꿈 | `worker-start`가 `state: failed`, `failedStage: dispatch_input`, "dispatch preamble was not delivered … Error parsing project config file"로 끝났다. 명세를 받기 전 종료다. 확인 넷(근거, `worker-release` 뒤 `exited/released`, 증거 폴더 없음, 띄우기 직전 기록과 같음) → `취소`. 백업으로 원복(해시 같음) → 새 세션 키로 새 시도. `--retry-of` 대신 새 명세 파일로 새 Task를 만들었다(명세의 시도 ID가 바뀌므로) | 통과 |
| P2 | B 구현 완료 뒤, 보관 전에 `ac-1/run.log` 끝에 한 바이트 | 보관 2(대조)가 크기 446≠445·sha256 불일치로 실패, staging 삭제. 작업자 liveness가 `unverifiable`이라 정지로 보지 않고 `보고됨`으로 두고 기다림 → 자동 해제 뒤 `exited/released` 확인 → `격리대기` → `.void`(파일 19개, `void-manifest.json`, 포인터) → 남은 원본 삭제 → `증거없음`. 구현은 끝났으므로 재검증. 원래 세션이 닫혀 **impl 인계**(새 세션 키) | 통과 |
| P3 | B 검토자 전에 `.env.local`을 관리자 폴더로 옮김 | 검토자가 AC-1을 `막힘`(종료 코드 3, 환경)으로, AC-2를 `통과`로, 코드 검토 결론을 `통과`로 보고. `.env.local`을 만들지 않았고, `env.ignored_inputs`에 해시 없이 "없음"으로 적었다(지어내지 않음). 원위치(해시 같음) → AC-1만 `rerun-only` → 통과 | 통과 |
| P4 | A 첫 검토자 전에 worktree 루트에 `pilot-notes.txt` | 검토자가 `tree_before`=`?? pilot-notes.txt`를 기록하고 두 AC 실행을 과정 증거로만 남겨 `막힘`으로 보고. 파일을 지우거나 고치지 않음(해시·mtime 같음). 코드 검토 결론은 `통과`로 보관 → 관리자가 파일 삭제 → `rerun-only`(AC 전부) → 통과 | 통과 |
| P5 | B를 먼저 병합해 `main`을 앞서게 한 뒤 A "병합해" | 관문 3에서 원격 `main` `de6b8c6` ≠ 증거 `B` `d7ed08d` → 병합 안 함 → `light` 작업자(Codex, fast 켬, `service_tier=priority` 확인)에게 rebase → 충돌 없음, range-diff 두 커밋 모두 `=` → 새 대상에서 impl AC 전부 + 새 rev `review` → 원격 head(옛 `H`, 게시 기록 있음)가 새 `H`의 조상이 아님 → 사용자에게 브랜치·원격 SHA·새 `H`·range-diff를 보여 확인받음 → 직전 재확인 뒤 `--force-with-lease=issue-3-id-unique:6b5d368` → 원격 확인 → 관문 다시 → 병합, 부모가 `de6b8c6`라 경쟁 없음 | 통과 |

수동 관찰(관리자가 작업자 보고·변경·worker-list로 본 것이고, 전 실행의 transcript로 증명한 것은 아니다): 작업자가 PR을 만들거나 다른 작업자를 띄우지 않았다(12). 라우터·다른 레시피를 읽지 않았다(14). 사용자에게 직접 묻지 않았다(11). `review` 시도 3번 모두 실패 테스트 커밋을 scratch에 풀어 red를 확인했다.

사소 지적(수정 커밋 본문 없음)이 검토마다 나왔다(3번). 세 번 모두 "근거를 들어 유지"로 판정했다. 레시피는 "맞았던 가설을 커밋 메시지에 적는다"이고 제목이 그 가설을 담는다. 같은 지적이 반복되므로 다음에는 레시피 문구를 분명히 할지(제목이면 되는지, 본문이 필요한지) 정한다.

## 계약 질문(다음 버전 후보)

| # | 질문 | 이번에 한 것 | 제안 |
| --- | --- | --- | --- |
| Q1 | 보관 실패 뒤 "같은 impl 세션에 재검증"이 Orca에서 가능한가 | 정지 확인 = 터미널 해제라, 확인하고 나면 그 세션은 없다. impl 인계로 했다 | (반영 @3) 계약은 "같은 impl 세션(없으면 impl 인계)"이라 어긋나지 않는다. 정지 확인 중 터미널이 해제되면 그 세션은 다시 쓰지 않고 impl 인계, `retained`만으로는 정지 확인이 아니라고 vstack.md "복구"에 적었다(한 번의 관찰이라 Orca 전체 규칙으로 단정하지 않는다) |
| Q2 | 결과 대상 확정에서 status가 비지 않으면 "그 시도의 기록은 판정에 쓰지 않는다"의 "기록"에 코드 검토 결론도 드는가 | P4: dirty가 배정 전부터 있었고(띄우기 직전 기록과 같음) `H`가 같아서, 수용 기준 기록만 무효로 보고 결론은 유지(복구 표의 "결론을 잃지 않았으면 rerun-only") | (반영 @3) status가 비지 않으면 배정 전부터 있던 변경이어도 시도 전체(코드 검토 결론 포함)를 판정에 쓰지 않는다. 처음에는 "띄우기 직전 기록과 같으면 결론 유지"로 제안했으나, 추적 소스의 미커밋 수정이 결함을 가린 채 검토되면 그 결론으로 병합될 수 있다는 Codex 차단 지적으로 좁혔다. **이번 P4 처리(결론 유지 + rerun-only)는 @3에서는 허용되지 않는다**(새 `review`가 맞다). 이번에는 무관한 메모 파일이었고, A의 실제 병합은 rebase 뒤 깨끗한 새 `review`(rev-aed90bbd-1)로 G3를 판정했다 |
| Q3 | `tree_before`가 비지 않은 실행의 `verdict`를 무엇으로 적는가 | 검토자가 스스로 `막힘`으로 적었다 | (반영 @3) evidence.md에 "그 기록의 `verdict`는 `막힘`, `note`에 이유"를 두고, 집계에서 유효하지 않은 기록은 `verdict`와 관계없이 증거 없음이라고 적었다 |
| Q4 | 명세 양식에 "git 무시" 안내가 없다 | 명세 새 눈 점검 두 번 모두 "`.vstack/`가 무시되는가"를 물었다. 관리자가 명세에 한 줄 넣었다 | (반영 @3) 두 양식에 git 무시 줄. 금지 대상은 무시 규칙 파일(`.gitignore`, `info/exclude`)로 한정했다 |

## 관리자 실행에서 나온 것

- **Bash 도구의 역슬래시**: heredoc(`<<'EOF'`) 안에서도 `\\`가 `\`로 바뀌었다. 첫 시범 반영 PR에서 경로 예시가 깨진 원인이 이것이다. 이번에는 Windows 경로를 슬래시로 쓰고 스크립트(`path.win32`)로 바꾸거나, 파일을 Write 도구로 만들어 피했다.
- **Python `tomllib` 없음**: 이 PC의 Python이 3.11 미만이라 계획의 P1 원복 확인(TOML 파싱)을 못 썼다. 새 Codex 세션 기록의 `service_tier`로 설정을 읽었는지 확인했다(codex-fast.md "적용"과 같은 방법).
- **`state.md` 갱신**: 첫 시범의 표 위치 실수(관찰 9)를 막으려고, 바꿀 문자열이 정확히 한 번 나오는지 확인한 뒤 임시 파일에 쓰고 바꾸는 스크립트로만 고쳤다. 이번에는 위치 실수가 없었다.
- **명세 새 눈 점검(서브에이전트)**: 점검하는 Claude가 자기를 구현자로 보고 "`executor`가 codex인데 실제와 다르다"고 물었다. 질문에 "실행기는 명세가 정한다"를 더하면 줄일 수 있다.
- **반복 작업 스크립트**: 보관(복사·대조·승격·확인·정리)과 격리(`.void`)를 스크립트로 만들어 썼다(관리자 scratchpad, 저장소 밖). 계약의 단계와 1:1이라 vstack에 도구로 넣을지 검토할 만하다.

## 시범 저장소 밖에 남은 것

- `~/.codex/config.toml`의 시범 worktree 신뢰 줄(첫 시범 때 추가, 백업 `config.toml.bak-vstack-pilot`). 시범 worktree는 모두 지웠다.
