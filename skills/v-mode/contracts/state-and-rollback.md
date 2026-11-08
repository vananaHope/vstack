# 작업 파일과 되돌리기

## 위치

vstack 작업의 파일은 메인 저장소의 `.local/vstack/<작업 이름>/`에 둔다. 기존 agent-orchestra의 `.local/orchestration/<작업 이름>/`과 다른 폴더다.

- 폴더를 나누면 기존 agent-orchestra 관리자가 vstack 작업의 `state.md`를 **자동으로 읽지 않는다**. 그것만으로 소유권이 보장되지는 않는다. 기존 관리자는 열린 PR과 살아 있는 작업자도 "진행 중"으로 본다(orchestra `SKILL.md` 1단계). 소유권은 아래 "소유권"과 "되돌리기"의 명시적 절차로 지킨다.
- 프로젝트 설정(`docs/agents/orchestration.md` 또는 `.local/orchestration/settings.md`)과 `common-findings.md`는 두 쪽이 같이 읽는다. vstack은 설정을 읽기만 하고, 형식을 바꾸지 않는다.
- 맡김 기록은 `.local/vstack/assign-log.md`에 따로 쌓는다(레시피·검토자·증거 판정 열 포함).
- 실창 잠금은 기존과 같은 `~/.agent-orchestra/desktop.lock`을 쓴다. 기존 관리자와 vstack 관리자가 동시에 돌아도 같은 데스크톱을 서로 막게 하려는 의도적인 공유다.

## state.md 형식

```
<단계>                      ← 첫 줄. orchestra 단계 이름 + `병합 대기`
등급: standard · 작업자: codex@high
workflow: vstack · contract: vstack-contract@3 · recipe: bug-fix@3 · 소유: vstack
막힘: <풀릴 조건>            ← 막혔을 때만

## 수용 기준
| ID | 필수 | 내용 |

## 시도
| 시도 ID | 역할 | 작업 종류 | scope | 맡은 수용 기준 | 실행기 | 세션 | dispatch ID | 배정 대상 H·B | 결과 대상 H·B | 상태 | 보관 경로 | manifest sha256 | 비고 |

## 관문
| 시각 | H | B | G1 | G2 | G3 | G4 | G5 | 결과 |

## 게시
| 시각 | 브랜치 | 게시한 SHA | 방법(첫 게시 / push / force-with-lease(확인받음) / 원격 일치 확인) |
```

- `배정 대상`은 맡길 때의 `H`·`B`(새 수정이면 시작 커밋과 `B`), `결과 대상`은 완료 보고를 받고 manifest와 worktree를 확인해 관리자가 적는 `H`·`B`다. 수용 기준 집계(evidence.md)는 결과 대상을 쓴다.
- `세션`은 Orca 작업자 터미널 핸들, `dispatch ID`는 전체 값이다. 둘 다 띄운 뒤 `worker-start`·`send` 결과에서 읽어 채운다. 시도 ID의 세션 키는 관리자가 띄우기 전에 정한 것이고, manifest의 `session`도 이 키다(작업자는 터미널 핸들을 모른다). 이 표가 세션 키와 터미널 핸들을 잇는다. 역할 자격(evidence.md)과 집계를 재시작 뒤에도 판정하려고 남긴다.
- `비고`에는 `impl 인계(<이유>)`, `취소(<제출 확인 실패 또는 시작 실패의 근거>)`, 정산 이유 등을 적는다.

## 소유권

- 한 작업은 한 관리자 구현만 소유한다. `소유: vstack`인 작업은 vstack 관리자만 진행한다.
- vstack 관리자가 `workflow` 줄이 없는 `.local/orchestration/` 작업을 발견하면 이어받지 않고 사용자에게 알린다.
- vstack 관리자는 기존 agent-orchestra 관리자와 같은 저장소에서 동시에 지휘하지 않는다. 둘이 같은 이슈를 고를 수 있기 때문이다.

## 되돌리기

vstack에 문제가 생겨 기존 agent-orchestra로 돌아갈 때, 사용자가 둘 중 하나를 고른다. 어느 쪽이든 먼저 vstack 관리자가 그 작업의 작업자를 모두 정지하고 정지를 확인한다.

1. **새로 시작**(이 작업의 PR을 버리고 같은 이슈를 처음부터)
   1. 열린 PR이 있으면 사용자에게 물어 닫는다(열린 PR이 있으면 기존 관리자는 그 이슈를 진행 중으로 보고 맡기지 않는다).
   2. 시도를 모두 정산한다.
   3. **worktree는 지우지 않고 보존한다.** orchestra의 worktree 지우기 규칙은 병합된 worktree만 허용하므로 미병합 worktree에는 쓸 수 없다. 대신 그 worktree의 브랜치를 `vstack-abandoned/<작업 이름>-<날짜>`로 이름을 바꿔, 기존 관리자가 새로 만들 `<작업 이름>-<slug>` 브랜치와 겹치지 않게 한다. 보존한 경로와 브랜치를 사용자에게 알린다.
   4. 보존한 worktree를 지우는 것은 미병합 변경의 삭제이므로 안전 멈춤([priority.md](priority.md))에 든다. 사용자가 폐기를 명시적으로 고르고, 작업자 정지가 확인되고, 시도가 정산됐을 때만 지운다. 지우기 전에 브랜치를 원격에 백업할지 사용자에게 묻는다.
   5. `state.md` 첫 줄을 `끝`, 소유를 `소유: 포기(<날짜>, 새로 시작)`로 바꾼다.
   6. 기존 관리자로 같은 이슈를 새 작업으로 맡긴다.
2. **명시적 이행**(PR과 worktree를 살린다)
   1. 시도를 모두 정산한다. 정산되지 않은 시도가 있으면 이행하지 않는다.
   2. `.local/vstack/<작업 이름>/`의 명세·검토 보고서를 `.local/orchestration/<작업 이름>/`로 복사한다.
   3. 기존 형식의 `state.md`를 새로 쓴다(시도·관문 절 없음). 증거는 `.local/vstack/`에 그대로 둔다.
   4. vstack 쪽 `state.md`의 소유를 `소유: 이행됨(<날짜>, agent-orchestra)`로 바꾼다.
   5. 사용자에게 "이 작업은 이제 vstack 관문 없이 병합된다"고 알린다.
   6. 기존 관리자는 지휘를 시작할 때 `.local/orchestration/*/state.md`를 훑으므로 이 작업을 이어받는다.

## 옮긴 orchestra 사본의 내부 참조

agent-orchestra를 vstack으로 옮길 때(만드는 순서 3단계) 다음을 바꾼다. 이 계약의 범위가 아니라 그 단계의 완료 조건이다.

- `/agent-orchestra:configure`, 이름으로 부르는 `check-limits` → vstack 안의 경로
- "스킬 폴더"를 `Base directory for this skill`에서 받는 문장 → 사용자가 `/vstack:...`로 실행하면 그대로 받고, 파일을 직접 읽어 실행할 때는 명세가 루트 경로를 준다
- `.local/orchestration/` → `.local/vstack/`(설정과 `common-findings.md`는 위 "위치"대로 기존 경로를 읽는다)
- `backends/orca.md` → 현재 `orca skills get orchestration` 안내 기준으로 다시 쓴다
