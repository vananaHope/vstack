# 실행 환경: Orca

SKILL.md의 동작([SKILL.md](../SKILL.md) "실행 환경")을 Orca에서 하는 방법이다. 이 문서는 Orca 1.4.253의 안내(`orca skills get orchestration`)와 각 명령의 `--help`를 기준으로 썼다. Orca가 업데이트돼 명령이나 옵션이 안 맞으면 `orca skills get orchestration`과 `orca orchestration <명령> --help`를 먼저 보고, 이 문서를 고친다.

`orca`는 이번 세션에서 고른 실행 파일이다(`ORCA_CLI_COMMAND`가 있으면 그 값, Linux의 Orca 밖 터미널이면 `orca-ide`). 모든 명령에 같은 실행 파일을 쓴다.

## 하지 않는 것

지금 Orca는 아래를 하지 말라고 안내한다. 옮겨 오기 전 agent-orchestra(아카이브됨)의 방법이라 다른 문서에 남아 있을 수 있으니 쓰지 않는다.

- `check --wait`를 백그라운드로 돌리거나 받은 편지함을 훑는 스크립트를 돌리지 않는다. Orca가 관리자를 깨운다.
- 작업자 터미널에 직접 키를 보내지 않는다(`orca terminal send`). 작업자에게 말할 때는 `send`를 쓴다.
- 작업자에게 다음 일을 맡기려고 `worker-start --terminal`로 터미널을 재사용하지 않는다. 일반 후속 지시는 `send`를 쓴다. 예외는 recovery 안내(`orca skills get orchestration --reference references/recovery-and-cleanup.md`)가 명시한 복구, 곧 일이 정산되고 재사용이 입증된 터미널에서 같은 Task를 다시 시작하는 경우뿐이다.
- `worker-retain`은 `worker-keep-open`의 옛 이름이다(명령 목록에는 없지만 아직 동작한다). 새 이름을 쓴다.

## 준비

지휘 세션 전체에 Run 하나를 쓴다. `orca orchestration run-current`로 이 관리자에 묶인 Run을 본다. 없으면:

- 끝나지 않은 작업의 `state.md`에 `Run:` 줄이 있으면(관리자를 다시 시작했다) `orca orchestration run-use --id <그 Run>`으로 그 Run에 묶는다. 새 Run을 만들지 않는다. 이전 관리자가 띄운 작업자의 보고와 시도 표의 dispatch가 그 Run에 있다. 결과의 `runId`가 그 값인지 본다.
- 그 밖에는 `orca orchestration run-create --objective "<저장소> 이슈 지휘"`로 만든다. 새로 만든 Run을 `state.md`의 `Run:` 줄에 적는다.

아래의 `<run>`이 그 Run이다. 다른 Run이 함께 있으면 명령마다 `--run <run>`을 붙인다.

네 번째 시범에서는 관리자가 없던 동안 도착한 보고가 `run-use` 뒤에 다시 전달되지 않았다. 그래서 그런 보고는 다시 전달되기를 기다리지 않고 아래 "기다리기"의 `inbox`로 직접 읽는다([../vstack.md](../vstack.md) "관리자 재시작"). 받은 편지함의 읽음·처리 표시(`read`, `handled`)로 관리자가 처리했는지 판단하지 않는다. 같은 시범에서 관리자가 없었는데도 그 표시가 붙어 있었다.

## worktree 만들기

작업자를 새 worktree로 띄울 때는 이 단계 없이 `worker-start`가 만든다(아래 "띄우기"). 띄우기 전에 worktree 안에 설정 파일을 써야 할 때(Codex fast)만 먼저 만든다.

`orca worktree create --name <작업 이름>-<slug> --branch <작업 이름>-<slug> --repo path:<메인 저장소> --base-branch main --setup run --json`. `--branch`를 주지 않으면 Orca의 기본 접두사가 붙어 SKILL.md가 가정하는 브랜치 이름(`<작업 이름>-`로 시작)과 달라진다. 결과의 worktree 경로와 브랜치를 `state.md`에 적어 둔다.

## 띄우기

명세는 파일로 넘긴다(`--spec-file`). 셸 인자로 한국어 명세를 넘기면 따옴표·줄바꿈에서 깨지기 쉽다.

- **새 worktree**: `orca orchestration worker-start --spec-file <task.md 절대 경로> --worktree new-top-level --repo path:<메인 저장소> --name <작업 이름>-<slug> --base-branch main --agent <에이전트> --task-title "<작업 이름>: <한 줄 요약>"`.
  `worker-start`에는 `--branch`가 없다. 띄운 뒤 `orca worktree show --worktree path:<경로> --json`으로 실제 브랜치를 읽어 `state.md`에 적는다. 이름이 `<작업 이름>-`로 시작하지 않으면 SKILL.md의 "진행 중" 판정(브랜치 접두사)이 맞지 않으므로, 브랜치 이름이 중요하면 위 "worktree 만들기"로 먼저 만든다.
- **기존 worktree**(검토자, 지적 수정, rebase, 미리 만든 worktree): `--worktree path:<worktree 경로>`. 새 터미널이 열린다.
- 새 worktree(`new-top-level`, `new-child`)에 띄운 작업자는 **끝나도 열린 채 남는다**(Orca 기본값). 기존 worktree에 띄운 작업자는 끝나면 스스로 닫히고, 약 2분 뒤 자동 해제된다. 기존 worktree 작업자의 터미널 상태(띄운 서버 등)를 살려 둬야 하면 `--keep-open`을 붙인다. 어느 쪽이든 아래 "정리"에서 확인한다.

에이전트별 모델·강도:

- **Claude·Codex**: `--model <모델> --effort <강도>`. `--effort`는 `--model`이 있어야 한다. 강도만 정했으면 모델은 그 에이전트 설정의 기본 모델을 적는다. 둘 다 없으면 두 옵션을 뺀다.
- **Codex fast**: `worker-start`에는 Codex 설정을 넘길 옵션이 없다. 아래 "Codex fast"대로 worktree의 Codex 설정으로 준다.

`worker-start`가 실패하면 같은 명령을 다시 돌리지 않는다. 결과의 `failedStage`를 보고 `orca skills get orchestration --reference references/recovery-and-cleanup.md`를 따른다.

### Codex fast

Codex는 작업 폴더의 `.codex/config.toml`을 전역 설정보다 우선해 읽으므로 거기에 쓴다. 이 파일은 신뢰된 경로에서만 읽힌다(`$CODEX_HOME/config.toml`의 `[projects.'<경로>'] trust_level = "trusted"`. 상위 경로를 신뢰해도 된다).

신뢰 줄을 더해야 하면 전역 설정을 고치는 것이다. 다음을 지킨다.

- 먼저 `config.toml`을 백업한다.
- 경로는 TOML 리터럴 문자열(작은따옴표)로 쓴다: `[projects.'C:\Users\<사용자>\orca\workspaces\<저장소>']`. 큰따옴표 안의 `\`는 이스케이프로 읽혀 파일 전체를 읽지 못하게 되고, 그러면 모든 Codex 작업자가 뜨지 않는다(첫 시범에서 그랬다).
- 고친 **바로 뒤** `codex login status`를 돌려 출력에 `Error loading configuration`이 없는지 본다. 종료 코드만 보지 않는다(로그인이 없어도 1이다). 오류면 백업으로 되돌린다.
- 전역 설정을 바꿨다는 것과 백업 위치를 사용자에게 알린다.

1. worktree가 아직 없으면 먼저 만든다(위 "worktree 만들기"). 저장소에 이미 커밋된 `.codex/config.toml`이 있으면 쓰지 않고 전역 설정대로 띄운 뒤 사용자에게 알린다.
2. `<worktree>/.codex/config.toml`에 켜면 `service_tier = "fast"`, 끄면 `service_tier = "default"`를 쓴다. 끌 때도 파일을 지우지 않고 적는 것은 전역 설정이 fast일 수 있기 때문이다. 같은 worktree에 다음 Codex 작업자를 띄울 때마다 다시 정해 고친다.
3. 이 파일이 커밋되지 않게 `git -C <worktree> rev-parse --git-path info/exclude`가 가리키는 파일에 `/.codex/`를 더한다(한 번이면 된다).
4. 위 "띄우기"대로 띄운다.

`.codex/config.toml`이 없거나 `state.md`에 fast 기록이 없으면 이 단계를 빠뜨린 것이다.

## 제출 확인

`worker-start` 결과에 `dispatchId`, `taskId`, `terminal`이 있고 `state`가 `ready`면 Orca가 명세를 맡겼다. 셋을 `state.md` 시도 표에 적는다(`terminal`이 그 세션의 터미널 핸들이다. 시도 ID의 세션 키와 이 표에서 이어진다).

작업이 실제로 시작됐는지 의심스러우면 `orca orchestration worker-show --dispatch <id>`와 `orca orchestration worker-read --dispatch <id>`로 본다. 터미널에 키를 보내 바로잡지 않는다. 시작되지 않았으면 위 "띄우기"의 실패 처리를 따른다. 터미널은 떴지만 에이전트가 명세를 받기 전에 끝났으면(설정 오류 등) `<vstack>/skills/v-mode/contracts/archive.md` "시작 실패"로 그 시도를 `취소`로 정산하고, 원인을 고친 뒤 새 세션 키로 새 시도를 만들어 띄운다. `--retry-of`를 써도 시도 ID는 새로 만든다.

## 기다리기

맡길 일을 다 맡겼으면 **턴을 끝낸다**. 작업자가 보고하거나 묻거나 멈추면 Orca가 관리자를 깨운다.

- 깨어나면 메시지가 대화에 통째로 들어온다. 그것을 처리한다. 깨운 메시지가 `check` 명령을 알려 주면(터미널이거나 메시지가 너무 클 때) 그 명령을 돌린다.
- `question`: SKILL.md 3단계의 "질문"이다. 답은 아래 "답하기".
- `worker_done`: SKILL.md 3단계의 "완료 보고"다. 그 Task를 끝낸다. 작업자가 보고한 실패를 완료로 바꾸지 않는다.
- `escalation`(`stopReason` 있음): 작업자가 `worker_done` 없이 멈췄다. `worker-read`로 상황을 보고, `send`로 이어 가게 하거나, 아래 "정지" 뒤 다시 맡기거나, 사용자에게 알린다.
- 놓친 메시지가 있는 것 같으면 `orca orchestration inbox --terminal run:<run> --limit 50`으로 이미 처리된 메시지까지 본다.

## 답하기

`orca orchestration reply --id <질문 msg_id> --body "<답>"`. 답이 작업이나 사용자 지시에서 나오면 바로 답하고, 사용자만 정할 수 있으면 사용자에게 먼저 묻는다.

## 보내기

작업자에게 다음 지시(지적 수정, 재검토, `main` 변경 안내)를 보낼 때는 `orca orchestration send --to dispatch:<그 작업자의 마지막 dispatch id> --subject "<주제>" --body "<지시>"`.

- 일하는 중인 작업자는 지금 턴이 끝날 때 받는다.
- 끝났거나 닫힌 작업자는 같은 터미널에서 다시 열려 후속 Task로 받고, `worker_done`으로 보고한다. 결과의 새 `dispatchId`를 시도 표에 적는다. 세션(`terminal`)은 그대로다.
- 지시가 길면 본문을 파일로 쓰고 `--body "$(cat <파일>)"`로 넘긴다(bash). 한국어가 깨지면 파일 경로를 본문에 적어 읽게 한다.

## 남겨 두기

기존 worktree에 띄운 작업자는 끝나면 Orca가 닫지만, 위 "보내기"로 다시 열 수 있고 맥락도 남는다. 새 worktree에 띄운 작업자는 끝나도 열린 채 남는다(위 "띄우기"). 그래서 재검토·지적 수정에 다시 쓸 작업자는 보통 따로 할 일이 없다.

기존 worktree 작업자의 터미널 상태 자체(띄운 개발 서버, 시뮬레이터 등)를 살려 둬야 할 때만 `orca orchestration worker-keep-open --dispatch <id>`를 한다(띄울 때 `--keep-open`과 같다).

## 정지

작업자를 멈춰야 할 때(사용자의 취소, 증거 없음 정산 전의 정지 확인 등): `orca orchestration worker-stop --dispatch <id>`.

**정지 확인**은 다음을 모두 만족할 때만이다.

1. `worker-stop`의 종료 코드가 0이고 결과에 `stop_unknown`이 없다.
2. 결과에 `next`가 있으면 그것을 따랐다.
3. `orca orchestration worker-show --dispatch <id>`에서 그 Dispatch가 끝난(settled) 상태이고 에이전트가 살아 있다는 표시가 없다.

- `processAction`의 값만으로 판정하지 않는다. `closed_agent_terminal`은 Orca가 닫기를 요청했다는 뜻이며, 종료를 증명하지 못한 `stop_unknown`에서도 나온다.
- `stop_unknown`(종료 코드 1)이면 정지를 증명하지 못한 것이다. `worker-show`와 결과를 보고 사용자에게 "정지 미확인"을 알린다. 같은 명령을 되풀이하지 않고, 그 시도의 정산·격리·재시작·worktree 삭제를 멈춘다.
- 응답 없음, 시간 초과, liveness `unverifiable`만으로는 정지로 보지 않는다.

## 정리

작업자 터미널을 다 쓴 뒤(그 작업을 병합했거나 그만뒀을 때) 한다. worktree를 지우기 전에 반드시 한다.

1. 이 작업의 시도 표에 있는 dispatch마다 `orca orchestration worker-list --run <run> --json`(또는 `worker-show --dispatch <id>`)으로 터미널 상태를 본다.
2. 상태별로:

   | 상태 | 할 일 |
   | --- | --- |
   | `released` | 끝 |
   | `reclaimable` | `orca orchestration worker-release --dispatch <id>`(자동 해제 `autoReleaseAt`을 기다려도 된다) |
   | `retained`(새 worktree 기본값, `worker-keep-open`) | 정산된 작업자면 `worker-release --dispatch <id>`. 사용자가 직접 열어 둔 것이면 닫지 않고 사용자에게 묻는다 |
   | `active` | 아직 일하는 중이다. 기다리거나 위 "정지" |
   | `release_pending` | 결과의 `next`나 recovery 안내대로 기다린다 |
   | `release_unknown`(종료 코드 1) | 해제를 증명하지 못했다. 사용자에게 알리고 그 worktree를 지우지 않는다 |

3. 모든 dispatch가 `released`(`worker-release`가 `already_released`로 답한 것 포함)가 되면 정리가 끝난 것이다. 하나라도 아니면 아래 "worktree 지우기"를 하지 않는다.
   - 위 "보내기"로 같은 터미널을 후속 dispatch에 넘겨준 앞선 dispatch는 `worker-list`에 터미널 상태가 비어 있고, `worker-release`가 `retained`·`reason: ownership_transferred`로 답한다(omp 맡기기 시범, Orca 1.4.255). 그 터미널을 이어받은 마지막 dispatch가 `released`면 앞선 dispatch도 끝난 것으로 본다.

`worker-release`는 Orca가 만든 그 작업자의 터미널만 닫는다. 사용자가 열어 둔 터미널, 원래 있던 터미널, 신원을 증명할 수 없는 터미널은 닫지 않고 `retained`로 답한다. 그런 터미널이 남으면 막힘으로 두고 사용자에게 알린다.

## worktree 지우기

위 "정리"가 끝난 뒤에만 한다.

`orca worktree rm --worktree path:<worktree 경로> --delete-branch`. 지금 Orca는 기본으로 로컬 브랜치를 남긴다. `--delete-branch`를 줘도 Orca가 병합됐다고 증명하지 못한 브랜치는 남는다. 결과에 브랜치 삭제 근거가 없으면 `git branch -d <브랜치>`를 한 번 해 본다. squash·rebase 병합이면 git이 병합 여부를 알 수 없어 거부할 수 있다. 거부되면 `-D`로 강제로 지우지 않는다. 브랜치를 남기고, 남긴 브랜치와 이유(병합 커밋 SHA, 병합 방법)를 사용자 보고에 적는다.

## 작업자가 보고하는 방법

명세 양식의 `{실행 환경: 완료 보고}`와 `{실행 환경: 질문}`에 넣는 문장이다. 작업자에게는 Orca가 Task·Dispatch ID가 든 머리말을 함께 넣어 준다.

- 완료 보고(구현자): "완료 보고는 orchestration `worker_done`으로 하고 `--outcome succeeded` 또는 `--outcome failed`를 붙인다."
- 완료 보고(검토자): "보고서 파일 경로를 `--report-path`로 넘긴다. `worker_done` 본문은 3문장 이내로 결론만."
- 질문: "질문은 orchestration `ask`로 하고 턴을 끝낸다. Orca가 답으로 깨운다."

