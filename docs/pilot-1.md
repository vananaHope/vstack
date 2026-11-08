# 첫 시범 기록

- 날짜: 2026-11-08 · 실행 환경: Orca 1.4.253 · 계약 `vstack-contract@1` · 레시피 `bug-fix@1`
- 저장소: 비공개 `vananaHope/vstack-pilot-todo`(Node CLI 할 일 앱). 버그를 일부러 심었다: 읽기 정규화가 저장된 `done`을 무시하고 예전 필드 `completed`만 봤다.
- 이슈 #1 → PR #2 → squash 병합 `de4dde2`. 작업 파일은 그 저장소의 `.local/vstack/issue-1/`(커밋하지 않음)

## 흐름

| 단계 | 결과 |
| --- | --- |
| 입력 검사 → worktree 만들기 | `orca worktree create --branch`, 경로를 `state.md`에 적음 |
| 명세 새 눈 점검 | OpenCode가 660초 제한에 끊김 → 서브에이전트로 대체(관찰 1) |
| 구현 `impl-ffad4143-1` | Codex `gpt-6-astra@medium+fast`. 가설 3개 중 하나만 런타임 증거로 남김. 실패 테스트 커밋 `62637ab` → 수정 커밋 `f76159e`. 약 4분 |
| 보관 | staging 복사 → 파일 16개 해시 대조 → 승격 → 포인터 → 원본 정리. `정리됨` |
| 결과 대상 확정 | `HEAD`·status·커밋 범위 확인, 결과 대상 `f76159e · 335f966` |
| 검토 `rev-13e37cd5-1` | Claude, `scope: review`. 실패 테스트 커밋을 scratch에 풀어 red 확인, v1 호환을 지운 변이에서 테스트가 실패하는 것도 확인. 결론 `통과`, 사소 1 |
| 집계·판정 | AC-1@1·AC-2@1 두 역할 모두 통과. 사소 1은 유지(관찰 6) |
| 지시 대기 → "PR 올려" | 첫 게시 `push -u`, PR #2 |
| "병합해" → 관문 | 원격 일치 확인, 보관 재확인, G1~G5 통과, `--match-head-commit`으로 squash 병합 |
| 병합 뒤 | `MERGED`·기준 브랜치 확인, squash 커밋의 부모가 검증한 `B`라 경쟁 없음. `main`에서 검증 시나리오 통과 |
| 정리 | 작업자 3개 해제, 게시 SHA로 남은 변경 확인, 시도 정산 확인 → worktree·로컬·원격 브랜치 삭제 |

정상 경로만 돌았다. 막힘, 무효 증거, 보관 실패 복구, rebase와 force-push 확인, 같은 계열 검토는 아직 실제로 돌려 보지 않았다.

## 관찰과 반영

| # | 관찰 | 원인 | 반영(`vstack-contract@2`, `bug-fix@2`) |
| --- | --- | --- | --- |
| 1 | 명세 새 눈 점검을 맡긴 OpenCode가 660초 제한에 끊김 | OpenCode 로그인이 없어 `opencode-go/` 모델을 쓸 수 없었고, 오류 없이 기본 무료 모델 `opencode/big-pickle`로 돌았다. 턴마다 30~160초(측정: OpenCode 로그). 질문도 "저장소의 코드는 읽어도 된다"여서 환경 변수, 원칙 파일까지 훑었다 | opencode.md "모델 확인": 쓸 모델을 정하고, `opencode models`에 있는지 보고, 실제로 쓰였는지 확인한다. `opencode run`은 언제나 `-m`. spec-check.md 질문은 읽을 범위를 명세가 가리킨 파일로 좁혔다. 다시 잼(로그인이 없어 같은 모델의 무료판 `deepseek-v4.1-flash-free`로): 287초(좁히기 전), 234초(좁힌 뒤, git·테스트 조사 없음). 정해 둔 모델은 `opencode-go/deepseek-v4.1-flash`이고, 사용자가 OpenCode Go에 로그인한 뒤 다시 잰다 |
| 2 | manifest `session`을 작업자가 채울 수 없음. 과정 증거 위치가 없음 | 계약이 `session`을 터미널 핸들로 정했는데, 작업자는 자기 핸들을 모른다 | `session`은 세션 키. 터미널 핸들은 관리자가 `state.md`에 적어 키와 잇는다. 과정 증거는 `process/` 아래, `files`에만 |
| 3 | 레시피가 가리키는 `tdd`·`diagnosing-bugs`를 읽어도 되는지 작업자가 물음 | worker-contract "읽을 것"에 없었다 | 맡은 작업 종류의 절차에 나오는 스킬의 가리킨 절만 읽는다 |
| 4 | 작업자 시작 실패를 같은 시도 ID로 `--retry-of`했다 | 계약의 `취소`는 제출 실패만 다뤘다 | archive.md "시작 실패": 근거·정지 확인·빈 증거 폴더·worktree 그대로를 확인하고 `취소`. 다시 맡기면 새 세션 키로 새 시도 ID |
| 5 | 구현자의 `report.md`가 worktree 절대 경로를 적어, 보관 뒤 틀린 경로가 됨 | 경로 표기 규칙이 없었다 | manifest와 `report.md`에서 증거 파일을 가리키는 경로는 시도 폴더 기준 상대 경로(`cwd`는 절대 경로 그대로). 보관 뒤 위치는 `state.md` 보관 경로가 정본. 검토 명세에 보관된 구현자 시도 폴더를 적는 줄 |
| 6 | 사소 지적을 고치지 않을 선택지가 없음 | 5단계 판정은 지금 고침 / 다른 이슈 / 사용자에게 물음뿐이었다 | "근거를 들어 유지": `사소`만, 근거를 `state.md`와 PR 본문에. `차단`·`중요`가 틀렸다고 보면 사용자에게 묻는다 |
| 7 | 관리자가 `~/.codex/config.toml`에 신뢰 줄을 큰따옴표 경로로 넣어 파일 전체가 깨짐. 모든 Codex 작업자가 뜨지 않음 | Windows 경로의 `\`가 TOML 이스케이프로 읽혔다. 고친 뒤 바로 확인하지 않았다 | backends/orca.md: 백업, 작은따옴표 리터럴, 고친 바로 뒤 `codex login status` 출력에 `Error loading configuration`이 없는지 확인(측정: 깨진 설정과 맞는 설정으로 재현) |
| 8 | 작업자의 `gh issue view <n> --comments`가 빈 출력 | 터미널이 아닌 셸에서는 본문 없이 댓글만 나온다. 댓글이 없어 아무것도 안 나왔다(측정). 이번에는 명세에 수용 기준이 다 있어서 영향이 없었다 | 명세 양식과 trackers.md를 `gh issue view <n> --json title,body,comments`로 |
| 9 | 관리자가 관문 기록 줄을 "관문" 표가 아니라 "시도" 표에 넣음 | 표를 손으로 고쳤다 | 시범 저장소의 `state.md`를 바로잡음. 판정에는 영향이 없었다(관문 판정은 기록 전에 했다). 반복되면 `state.md` 갱신 도구를 검토한다 |
| 10 | 관리자가 OpenCode 출력의 `> plan · <모델>` 줄만 보고 Go 모델 호출이 성공했다고 보고함. 실제로는 `This API key can't call models`로 실패했다 | 그 줄은 호출 전에 찍힌다. 출력을 걸러 봐서 오류를 놓쳤다 | opencode.md "모델 확인" 3: 그 줄, 종료 코드 0, 답이 있는지를 함께 본다. `session_v2.model`은 `-m`일 때만 채워지므로 `session_message`의 모델을 본다 |
| - | PR 번호를 이슈 번호로 착각 | 이슈와 PR이 번호를 함께 쓴다 | SKILL.md 6단계 1: PR 번호는 `gh pr create` 출력에서 읽는다 |

## 시범 저장소 밖에 남은 것

- `~/.codex/config.toml`: 시범 worktree 신뢰 줄(백업 `config.toml.bak-vstack-pilot`). worktree는 지웠으므로 그 줄은 이제 쓰이지 않는다.
- `~/.config/opencode/opencode.json`: 시범 뒤 새로 만들었다. 모든 에이전트의 모델을 `opencode-go/deepseek-v4.1-flash`로 고정했다. OpenCode Go 로그인 전에는 `-m`으로 부르면 `Model unavailable`로 멈추고, `-m` 없이 부르면 `big-pickle`로 넘어간다(측정).
