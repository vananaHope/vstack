# 7단계 계획: 설정 통합과 UI 다듬기(제거·아카이브는 미룸)

상태: 사용자가 범위를 정했다(2026-11-12, 아래 "사용자가 정한 것"). **이번 7단계에서 하는 것은 `blast-radius` 가져오기, 묶음 A, 묶음 F다(아래 "순서").** 묶음 B·C·D는 미뤘고, 묶음 E는 하지 않는다. 묶음 F는 한 세션용 레시피로 만들었다(아래 "UI 다듬기 레시피").

[design.md](design.md) 11절 7: "설정 통합, 기존 플러그인 제거, 기존 agent-orchestra 저장소 아카이브. omp에서 한 세션 갈래가 쓸 만하면 omp를 지휘 작업자 종류로 더한다."

## 지금 상태(2026-11-12에 잰 것)

- 설치: `vstack@vstack` 0.9.3, `agent-orchestra@agent-orchestra` 0.20.0. 둘 다 사용자 범위, 켜짐.
- agent-orchestra 저장소(`vananaHope/agent-orchestra`): 공개, 아카이브 안 됨, 마지막 커밋 `c62be33`(0.20.0, 2026-11-05). vstack이 옮겨 온 커밋과 같다. 그 뒤로 원본에 새 커밋이 없다. 열린 이슈·PR 없음. 로컬 클론 `C:/Users/gusdn/orca/agent-orchestra`는 `main`=`c62be33`, 깨끗함.
- vstack이 옮겨 온 것: `skills/orchestrate-issues`, `skills/check-limits`, `skills/configure`. 파일 목록의 차이는 vstack 쪽에만 있는 `vstack.md` 하나다(내용은 고쳤다, `UPSTREAM.md`).
- **agent-orchestra를 실제로 쓰는 프로젝트는 하나다**: `C:/Users/gusdn/orca/my-video-manager`.
  - 설정 `docs/agents/orchestration.md`(15절), `common-findings.md`가 커밋돼 있다. `AGENTS.md`가 "`orchestrate-issues` skill (agent-orchestra plugin)"이라고 가리킨다.
  - 진행 중인 지휘 작업은 없다(`.local/` 없음, worktree는 메인 하나).
  - 열린 이슈가 있다(`ready-for-agent` 여럿). 화면·시각 작업이 많다.
  - verify 스킬이 없다(`.claude/skills/`에는 애니메이션 스킬 다섯 개뿐). 티켓에 vstack 절도 없다.
  - 그 프로젝트만의 문서 `docs/agents/omp-orchestration.md`(herdr app + omp 관리자 절차)가 따로 있다. vstack과 무관하게 손으로 쓴 절차다.
  - `AGENTS.md`에 커밋하지 않은 변경이 있다(사용자 것. 건드리지 않는다).
- **vstack 지휘는 실제 프로젝트에서 돌려 본 적이 없다.** 시범 다섯 번과 omp 맡기기 세 번 모두 시범 저장소(`vstack-pilot-todo`, `vstack-pilot-omp`)였다.
- agent-orchestra는 하는데 vstack이 아직 하지 않는 것(`skills/orchestrate-issues/vstack.md` "첫 버전에서 하지 않는 것", `tiers.md`):
  - 레시피가 없는 작업의 지휘(성능, 프로토타입, 조사 등). vstack은 `bug-fix`·`feature`·`refactoring`만 맡는다.
  - UI 다듬기(관리자가 직접 구현).
  - 앞부분 선행 병합.
  - 검토 목록의 `관리자`(관리자가 diff를 직접 확인). vstack은 건너뛴다.
  - herdr 실행 환경. vstack은 옮기기만 했고 검증하지 않았다.
- vstack 안에 남은 agent-orchestra 흔적(이름만 남은 것 포함):
  - 설정의 두 번째 위치 `.local/orchestration/settings.md`·`common-findings.md`(작업 파일은 `.local/vstack/`인데 설정만 옛 폴더다).
  - 실창 잠금 `~/.agent-orchestra/bin/desktop_lock.py`, `~/.agent-orchestra/desktop.lock`.
  - 옮긴 스킬 세 개의 `disable-model-invocation: true`와 description의 "(vstack 사본)". 기존 플러그인과 이름이 겹쳐서 넣은 것이다.
  - `setup.md`가 `AGENTS.md`에 쓰는 줄 "shared by the vstack and agent-orchestra plugins".
  - "기존 agent-orchestra로 하거나"라는 안내(v-mode 레시피 표, `vstack.md` 두 곳).
  - 계약 `state-and-rollback.md`의 소유권 세 줄과 "되돌리기" 절 전체(기존 관리자로 돌아가는 두 길), 계약 예시 `04-archive-failure.md`의 이행 장면.
  - `upstream.json`의 `user_commands`에 `agent-orchestra:configure`, 출처 표의 `moved` 세 건. `check-links`의 closure 검사가 `--source agent-orchestra=<dir>`를 요구한다.

## 묶음

### A. 설정 통합(문서만, 되돌릴 수 있음)

기존 플러그인이 설치돼 있어도 할 수 있는 것만 먼저 한다.

1. 설정 위치는 그대로 둔다. `setup.md`와 `desktop.md`에 `.local/orchestration/`과 `~/.agent-orchestra/`가 옛 이름이라는 것만 적는다.
2. `setup.md`의 `AGENTS.md` 한 줄("shared by the vstack and agent-orchestra plugins")은 그대로 둔다. 제거를 미뤘으므로 아직 맞는 말이다.
3. agent-orchestra를 쓰던 프로젝트에서 vstack을 쓸 때 알 것을 README의 한 절로 적는다: 설정은 그대로 읽힌다, 옛 이름 경로, vstack 지휘가 다르게 하는 것(`관리자` 검토 항목을 건너뜀, UI 다듬기와 앞부분 선행 병합을 하지 않음), 처음 지휘하기 전에 갖출 것(검증 수단, 티켓의 vstack 절), 두 관리자를 동시에 돌리지 않음.

처음 초안에는 "프로젝트 설정 양식에 vstack이 읽지 않는 항목을 표시한다"와 "`AGENTS.md` 줄 안내"가 있었다. 양식은 두 플러그인이 함께 쓰므로 고치지 않고 위 README 절로 대신했다. `AGENTS.md` 줄은 2대로 그대로라 안내할 것이 없다.

완료 기준: `node scripts/check-links.mjs`에 새 `BROKEN`·`NONSTANDARD`·`SKILL`·`TOOL`·`NOT CARRIED`가 없다(출처 폴더를 주지 않아 나오는 `CLOSURE`는 가져온 스킬 수만큼 는다. `--source`를 준 출처는 통과해야 한다), Codex 읽기 전용 검토 `완료`, PR 병합(사용자 지시).

### B. 실제 프로젝트에서 한 번(제거 전 확인)

**미뤘다.** 제거를 다시 정할 때의 초안이다.

1. `my-video-manager`에서 이슈 하나를 고른다. 화면이 아닌 것, 레시피가 있는 것(`bug-fix` 또는 데이터 모양이 정해진 `feature`), 등급 `standard` 이하가 좋다. 고르는 것은 사용자다.
2. 그 프로젝트에 필요한 준비를 한다: verify 수단(고정 규칙 7), 티켓의 vstack 절, `AGENTS.md` 줄. 준비 변경은 그 저장소의 별도 PR이다.
3. 새 Claude Code 세션에서 `/vstack:v-mode`로 지휘한다(지시 → PR → 병합 지시).
4. 기록을 `docs/pilot-6.md`에 남기고, 어긋난 곳을 반영한다.

완료 기준: 그 이슈가 병합 관문을 지나 병합됐거나, 막힌 이유가 기록됐다. 막혔으면 C로 가지 않고 사용자에게 묻는다.

### C. 기존 플러그인 제거(사용자 PC의 설정 변경)

**미뤘다.** 아래는 나중에 다시 정할 때의 초안이다.

1. 제거 전 확인: 어느 저장소에도 `.local/orchestration/*/state.md` 가운데 `끝`이 아닌 것이 없다.
2. `claude plugin uninstall agent-orchestra@agent-orchestra`와 마켓플레이스 제거. **사용자가 "제거해"라고 지시할 때만 한다.** 되돌리려면 다시 설치하면 된다(저장소는 아카이브해도 읽을 수 있다).
3. vstack 문서에서 "기존 agent-orchestra" 길을 걷어 낸다.
   - v-mode·`vstack.md`의 "기존 agent-orchestra로 하거나" → "사용자가 정한 것" 2의 답대로.
   - 옮긴 스킬의 "(vstack 사본)"과 머리말. `disable-model-invocation`은 `check-limits`만 뗀다(읽기 전용 측정이라 모델이 불러도 된다. 지휘와 설정은 지금처럼 사용자가 실행한다).
   - 계약 `state-and-rollback.md`: 소유권 줄과 "되돌리기"를 "새로 시작"(작업을 포기하고 같은 이슈를 새 vstack 작업으로) 하나로 줄인다. 계약 예시 04의 이행 장면도 바꾼다. **계약을 바꾸므로 `vstack-contract@4`가 된다.** 판정식(G1~G5)과 작업자 의무는 그대로다. 진행 중인 작업이 없을 때 한다.
   - `upstream.json`·`UPSTREAM.md`: `user_commands`에서 `agent-orchestra:configure` 제거, 출처는 "아카이브된 원본"으로 표시, closure 검사에서 `moved` 출처를 뺀다.
4. `my-video-manager`의 `AGENTS.md` 줄과 `docs/agents/omp-orchestration.md`의 스킬 언급은 그 저장소의 PR로 고친다(사용자 지시로).

완료 기준: `claude plugin list`에 agent-orchestra 없음, 새 세션에서 `/vstack:v-mode`·`/vstack:configure`·한도 확인이 동작, 계약 예시 네 개를 `@4`로 다시 판정, Codex 검토 `완료`.

### D. agent-orchestra 저장소 아카이브(밖으로 나가는 동작)

**미뤘다.**

1. 원본 README 맨 위에 "vstack으로 옮겼다"는 안내를 넣는다(그 저장소의 마지막 커밋. 사용자 지시로 push).
2. `gh repo archive vananaHope/agent-orchestra`. **사용자가 저장소 이름을 적어 지시할 때만 한다.** 아카이브는 GitHub 설정에서 풀 수 있다.
3. 로컬 클론과 `~/.agent-orchestra/`는 "사용자가 정한 것" 3의 답대로.

완료 기준: 저장소가 아카이브 상태, vstack `UPSTREAM.md`에 아카이브 날짜.

### E. omp를 지휘 작업자 종류로(계약 안)

**하지 않는다(사용자 결정).** 검토하며 드러난, 하려면 정해야 했던 것을 기록으로 남긴다.

- 계열: 교차 검토는 "구현자와 다른 계열"을 요구한다. omp 작업자의 모델은 omp 설정(`modelRoles`)이 정하고 vstack은 `--model`을 주지 않는다. 그러면 관리자가 배정 때 omp의 계열을 무엇으로 읽을지 정해야 한다.
- 계약: omp 작업자가 `worker-contract.md`(증거 폴더, manifest, 세션 키)를 지키는지 돌려 본 적이 없다. 맡기기 세 번은 모두 계약 밖이었다.
- 서브에이전트: 계약은 "작업자는 다른 작업자를 띄우지 않는다"고 한다. omp 안의 읽기 전용 서브에이전트를 어떻게 볼지 정해야 한다.
- Orca가 omp의 턴 시작을 관측하지 못한다(`turnStart: unsupported`). 시작 실패 판정이 Codex·Claude와 다르다.
- 이득: omp의 모델 넘어가기(`usageAwareFallback`)를 지휘에서도 쓴다. 한도가 늘지는 않는다(omp는 안에서 Claude·Codex 계정을 쓴다).
- 계열 판정이 어렵다: 지금 설정은 메인이 `anthropic/claude-opus-5-5`이고 넘어가기가 켜져 있어, 배정 때 본 계열과 실제로 돈 모델의 계열이 다를 수 있다.

하려면 계획(`pilot-7-plan.md`)과 시범이 따로 필요하다.

## 사용자가 정한 것(2026-11-12)

| # | 질문 | 답 | 그래서 |
| --- | --- | --- | --- |
| 1 | 기존 플러그인을 지우기 전에 실제 프로젝트에서 한 번 돌릴까 | 제거는 미룬다 | 묶음 B·C·D는 이번에 하지 않는다. agent-orchestra는 설치된 채로 두고, 실제 프로젝트에서 vstack을 쓰다가 다시 정한다 |
| 2 | vstack이 아직 하지 않는 일은 어떻게 할까 | UI 다듬기부터 만든다 | 묶음 F를 더한다. 레시피 없는 작업의 지휘는 그대로 8단계다 |
| 3 | 옛 이름이 남은 위치(`.local/orchestration/settings.md`, `~/.agent-orchestra/`) | 그대로 둔다 | 경로는 바꾸지 않고 문서에 옛 이름이라고만 적는다(묶음 A) |
| 4 | omp를 지휘 작업자로 더할까(묶음 E) | 하지 않는다. 지휘는 지금 그대로 간다 | 지휘 작업자는 Codex·Claude·OpenCode다. omp는 한 세션의 "맡기기"(계약 밖)로만 쓴다 |

4의 경과: 처음에는 "7단계 안에서 한다"를 골랐다가, 설명(계열 판정, 증거 계약, 서브에이전트 규칙, 시범이 새로 필요하고 계약이 `@4`가 된다)을 들은 뒤 하지 않기로 했다.

## 묶음 F. UI 다듬기를 vstack에서(형태: 다, 한 세션에서만)

agent-orchestra의 UI 다듬기([ui-polish.md](../skills/orchestrate-issues/ui-polish.md))는 한 화면 묶음의 구현 이슈가 모두 병합된 뒤 **관리자가 직접** 스크린샷을 보며 고치고, `UI` 검토 목록의 다른 계열 검토를 받아 PR·병합하는 일이다. vstack은 관리자가 코드를 쓰지 않으므로 그대로 옮길 수 없다.

형태 후보(사용자가 정한다):

| 형태 | 내용 | 얻는 것 | 드는 것 |
| --- | --- | --- | --- |
| 가. 레시피 + Claude 작업자 | `ui-polish` 레시피를 만들고 지휘에서 Claude 구현 작업자에게 맡긴다. 교차 검토와 병합 관문을 그대로 거친다 | 관리자 규칙과 계약을 바꾸지 않는다 | 스크린샷으로 판단하는 일을 "관찰 가능한 수용 기준 + 검증 명령"으로 적는 법을 정해야 한다. 화면이 있는 프로젝트에서 시범이 필요하다 |
| 나. 관리자가 직접 구현 | 예전처럼 관리자가 고친다 | 예전과 같은 흐름 | 계약에 "관리자가 구현하는 예외"를 넣어야 한다(역할별 권한, 증거, 관문 G5). 계약 변경이 크다 |
| 다. 한 세션에서만 | 지휘에 넣지 않고 v-mode 한 세션 갈래에서 이 대화가 레시피대로 직접 한다 | 가장 작다. 계약을 건드리지 않는다 | 교차 검토와 병합 관문이 없다 |

어느 형태든 시범 저장소(`vstack-pilot-todo`는 CLI다)로는 돌려 볼 수 없다. 화면이 있는 프로젝트가 필요하고, 지금 그런 프로젝트는 `my-video-manager`다.

## 순서

사용자와 정한 순서다(2026-11-13).

1. **`blast-radius` 가져오기와 설정 문서 정리(묶음 A)**. PR 하나. pstack `blast-radius`를 고쳐 가져와 교차 검토 명세에 연결하고, 사용자가 직접 부를 수 있게 한다.
2. **UI 다듬기 레시피(묶음 F)**. 사용자가 한 세션용(형태 다)으로 먼저 만들기로 했다. 레시피는 pstack을 최대한 참고한다(사용자 요청): 짝이 되는 플레이북이 없어서 `visual-parity`(손대기 전 기준 스크린샷, 다듬지 않은 화면의 차이 0), `hillclimb`(하나 바꾸고 전후를 보고 남기거나 되돌림, 받아들인 변경마다 커밋), 원칙 `experience-first`를 조합한다.
3. **`my-video-manager`에서 실제로 쓴다**. UI 다듬기는 화면이 있는 프로젝트에서만 확인된다. vstack을 실제 프로젝트에 처음 쓰는 것이기도 하다.
4. B·C·D(실제 프로젝트 지휘 시범, 제거, 아카이브)는 3 뒤에 다시 정한다.

pstack의 `how`·`why`는 지금 가져오지 않는다. 조사 레시피를 만들 때(8단계) 함께 정한다. pstack의 조사 플레이북이 둘을 함께 쓰고, 지금은 부를 자리가 라우터의 "바로" 갈래 하나뿐이다. `why`는 외부 도구(MCP)마다 조사 에이전트를 쓰기 가능한 모드로 띄우는 구조라, 가져올 때는 git 기록 조사 부분만 떼어 오는 쪽을 먼저 본다.

- A는 문서만 바꾼다. 제거를 미뤘으므로 "두 플러그인이 설정을 함께 쓴다"는 문장은 그대로 둔다. 하는 것은 옛 이름 표시와 README의 "agent-orchestra를 쓰던 프로젝트에서" 절이다.

## UI 다듬기 레시피(`ui-polish@1`, 2026-11-13)

사용자가 형태를 정했다: **한 세션용으로 먼저 만든다**(위 묶음 F의 "다"). 지휘와 계약은 건드리지 않는다.

- 레시피 `skills/v-mode/recipes/ui-polish.md`: pstack `visual-parity`(기준 먼저, 기준·검사 수단을 고치지 않음, 이미지 비교), `hillclimb`(하나 바꾸고 전·후를 보고 남기거나 되돌림, 받아들인 변경마다 커밋, 시도 기록, 검사 수단을 먼저 확인하고 고정), 원칙 `experience-first`를 조합했다. 시점과 스크린샷 방식은 agent-orchestra의 UI 다듬기에서 왔다.
- 수용 기준 셋: 다듬기(항목마다 관찰 가능한 문장), 다른 화면 보존(비교 화면의 전·후가 픽셀 단위로 같음), 기존 검사.
- 이미지 비교 `skills/v-mode/recipes/scripts/image_diff.py`: 표준 라이브러리만 쓰는 PNG 비교. 같으면 종료 코드 0, 다르면 1과 달라진 영역, 비교하지 못하면 2. 테스트 14개(`test_image_diff.py`). 스크립트를 다섯 군데 일부러 틀리게 바꿔 테스트가 각각 실패하는 것을 봤다.
- 연결: v-mode 레시피 표와 "레시피 직접 따르기"(입력, 절차 범위), omp에는 맡기지 않음, 지휘에서는 레시피가 없는 것으로 봄(`vstack.md`).

### 시험 한 번

레시피를 쓴 세션이 직접, 구조도 페이지(HTML 한 장)를 임시 저장소에 두고 레시피 순서대로 한 항목을 다듬었다.

- 스크린샷 수단: 헤드리스 Edge로 구역 하나를 PNG로 찍는 스크립트. 대상 화면은 "만든 순서" 구역(밝은 테마, 어두운 테마, 폭 600), 비교 화면은 다른 두 구역.
- 2단계: 세 화면을 두 번씩 찍어 `image_diff.py`로 비교했고 모두 `identical`이었다.
- 항목: "그림 8에서 이웃한 글자 사이의 가장 좁은 틈이 12px다 → 16px 이상이다". 틈은 스크린샷의 빈 열을 세어 쟀다.
- 4단계의 시도 넷: 글꼴 바꾸기(되돌림: 같은 줄의 다른 식별자와 표기가 어긋남), 점 간격 84(되돌림: 치환 스크립트가 점 하나의 글자와 원을 지웠다. 전·후 스크린샷에서 버전 번호가 13개에서 12개로 준 것을 세어 확인), 점 간격 84를 다시(되돌림: 15px로 1px 모자람), 점 간격 88(남김: 21px).
- 5·6단계: 대상 화면의 세 상태를 다시 찍어 봤고, 비교 화면 둘은 기준과 `identical`(종료 코드 0)이었다.
- 여기서 나온 레시피 보완: 커밋 전에 diff를 읽어 상관없는 내용이 사라졌는지 본다(두 번째 시도의 손실은 스크린샷을 나란히 보는 것만으로는 놓칠 뻔했다), 잴 수 있는 항목은 숫자로 적고 못 미치면 남기지 않는다.
- 한계: 레시피를 쓴 세션이 자기 레시피를 따랐다. 화면은 정적인 HTML 한 장이고 상태가 데이터에 따라 달라지지 않는다. 디자인 토큰과 눈금, lint·빌드 같은 기존 검사(7단계)가 없는 대상이었다. 비교 화면이 실제로 깨지는 경우(6단계의 실패 경로)는 지나지 않았다. 사용자와 주고받는 부분(항목 확인, 눈금에 없는 값 묻기)도 없었다.

다음은 "순서" 3이다: 화면이 있는 실제 프로젝트에서, 새 세션이 이 레시피만 보고 다듬는다.

## `blast-radius` 평가(2026-11-13)

가져온 스킬이 다섯 번째 시범에서 첫 검토가 놓친 결함을 잡는지 한 번 돌려 봤다.

- 대상: `vstack-pilot-todo`의 `git diff f5aa577...9f66082`(리팩토링 첫 구현. 그때의 첫 검토 `rev-741e7412-1`은 통과로 판정했고, rebase 뒤 두 번째 검토가 결함을 잡았다. [pilot-5.md](pilot-5.md)).
- 준비: 저장소를 임시 폴더에 복제해 `9f66082`까지만 남겼다. 뒤의 커밋(수정, 후속 고정 테스트, 병합)은 복제본에서 지웠고(`git cat-file`로 없는 것을 확인), 저장소 안에 닫힌 파이프를 말하는 글자가 없는 것을 검색으로 확인했다.
- 실행: 새 Claude 서브에이전트 하나. 준 것은 스킬 파일 경로, 대상 저장소와 diff 범위, 변경을 쓴 쪽의 주장("리팩토링이다. CLI의 모든 출력과 종료 코드는 바꾸기 전과 같다"), 쓰기 제약뿐이다. 결함이 무엇인지는 주지 않았다. vstack 작업 밖(스킬의 "Outside a vstack task")으로 돌렸다.
- 결과: **잡았다.** 안전의 근거를 "어떤 인자와 데이터 상태에서도 출력·종료 코드·데이터 파일이 같다"로 잡고, 읽는 쪽이 살아 있는 경우는 2,964가지를 전후 비교해 같음을 보였고(검사가 차이를 잡는지는 한 줄 바꾼 사본으로 확인), 읽는 쪽이 먼저 닫힌 경우는 8가지 가운데 5가지가 다름을 실행으로 보였다(성공 명령이 종료 코드 0 → 1과 스택 추적, 사용법 오류가 2 → 1). 고칠 방법도 사본에서 확인해 냈고, 그것은 시범에서 실제로 들어간 수정과 같은 방향이다(bin이 `console.log`·`console.error`로 내보냄).
- 다시 돌려 본 것: 이 계획을 쓴 세션이 그 증명 스크립트(`broken-pipe.mjs`)를 다시 돌려 같은 결과(5가지 다름, 종료 코드 1)를 봤다.
- 걸린 것: 약 11분, 도구 호출 16번.
- 한계: 한 번이다. 비교 대상인 첫 검토는 다른 명세(레시피 `refactoring@2`의 검토 절차)로 돌았으므로 "스킬 때문에 잡았다"고 말할 수 없다. 평가를 준비한 세션은 답을 알고 있었다(프롬프트에는 넣지 않았다). vstack 검토자(증거 폴더, 명세의 scratch)로 돌린 것이 아니다.
- 평가에서 나온 스킬 문장 보완: 반증된 사실의 표기(`disproven`), 작업 밖에서 스크립트를 둘 곳(요청한 쪽이 정한 폴더가 먼저). 원문의 모호한 곳("one fact"와 "one or two facts", CLI에서 4단계와 5단계의 경계, "big or wide"의 기준)은 원문대로 뒀다.
- 증명 스크립트 사본은 `.local/stage-7-blast-radius-review/eval/`에 있다(이 PC에만).

## 하지 않는 것

- herdr 실행 환경 검증. 첫 버전은 Orca만이다(design 1절).
- 관리자를 omp에 두는 것(design 11절 7의 "별도 단계").
- `my-video-manager`의 `omp-orchestration.md` 절차를 vstack으로 옮기는 것. 그 프로젝트의 문서다.
- 새 레시피(성능, 프로토타입, 조사). 8단계다.
- omp를 지휘 작업자 종류로 더하는 것(묶음 E). 사용자가 하지 않기로 했다.
- 기존 플러그인 제거와 저장소 아카이브(묶음 C·D). 미뤘다. 아래 두 묶음의 내용은 나중에 다시 정할 때의 초안으로 남긴다.

## 위험

- B 없이 C를 하면, 실제 프로젝트에서 vstack이 막혔을 때 기존 방식으로 돌아가려면 플러그인을 다시 설치해야 한다(저장소가 아카이브돼도 설치는 된다. 다만 그동안 원본은 Orca 변화에 맞춰 고쳐지지 않는다).
- C의 계약 변경(`@4`)은 진행 중인 지휘 작업이 있으면 그 작업이 `@3`으로 남는다. 진행 중인 작업이 없을 때 한다.
- 제거 뒤 `check-limits`를 이름으로 부르던 습관("한도 확인해 줘")은 vstack 쪽이 받는다. `disable-model-invocation`을 떼지 않으면 `/vstack:v-mode`를 거쳐야 한다.
