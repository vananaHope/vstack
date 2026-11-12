# 7단계 계획(초안): 설정 통합, 기존 플러그인 제거, agent-orchestra 아카이브

상태: **초안. 사용자가 아래 "사용자가 정할 것"을 정하기 전이다.** 정해지면 이 문서를 고치고 묶음별로 진행한다.

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

1. 설정 위치를 정리한다("사용자가 정할 것" 3).
2. `setup.md`의 `AGENTS.md` 한 줄을 vstack 기준으로 바꾼다. 이미 그 줄이 있는 프로젝트는 `configure`가 고칠 때 바꾼다.
3. 프로젝트 설정 양식에 vstack이 실제로 읽는 것과 읽지 않는 것을 표시한다. 예: `관리자` 검토 항목은 건너뜀, "UI 다듬기"는 범위 밖.
4. 프로젝트를 vstack으로 옮길 때 할 일을 한 절로 적는다(`README.md` 또는 `setup.md`): 설정은 그대로 읽힌다, `AGENTS.md` 줄, verify 스킬, 티켓의 vstack 절.

완료 기준: `node scripts/check-links.mjs`가 기준과 같은 결과, Codex 읽기 전용 검토 `완료`, PR 병합(사용자 지시).

### B. 실제 프로젝트에서 한 번(제거 전 확인)

"사용자가 정할 것" 1에서 "먼저 한 번 돌린다"를 고르면 한다.

1. `my-video-manager`에서 이슈 하나를 고른다. 화면이 아닌 것, 레시피가 있는 것(`bug-fix` 또는 데이터 모양이 정해진 `feature`), 등급 `standard` 이하가 좋다. 고르는 것은 사용자다.
2. 그 프로젝트에 필요한 준비를 한다: verify 수단(고정 규칙 7), 티켓의 vstack 절, `AGENTS.md` 줄. 준비 변경은 그 저장소의 별도 PR이다.
3. 새 Claude Code 세션에서 `/vstack:v-mode`로 지휘한다(지시 → PR → 병합 지시).
4. 기록을 `docs/pilot-6.md`에 남기고, 어긋난 곳을 반영한다.

완료 기준: 그 이슈가 병합 관문을 지나 병합됐거나, 막힌 이유가 기록됐다. 막혔으면 C로 가지 않고 사용자에게 묻는다.

### C. 기존 플러그인 제거(사용자 PC의 설정 변경)

1. 제거 전 확인: 어느 저장소에도 `.local/orchestration/*/state.md` 가운데 `끝`이 아닌 것이 없다.
2. `claude plugin uninstall agent-orchestra@agent-orchestra`와 마켓플레이스 제거. **사용자가 "제거해"라고 지시할 때만 한다.** 되돌리려면 다시 설치하면 된다(저장소는 아카이브해도 읽을 수 있다).
3. vstack 문서에서 "기존 agent-orchestra" 길을 걷어 낸다.
   - v-mode·`vstack.md`의 "기존 agent-orchestra로 하거나" → "사용자가 정할 것" 2의 답대로.
   - 옮긴 스킬의 "(vstack 사본)"과 머리말. `disable-model-invocation`은 `check-limits`만 뗀다(읽기 전용 측정이라 모델이 불러도 된다. 지휘와 설정은 지금처럼 사용자가 실행한다).
   - 계약 `state-and-rollback.md`: 소유권 줄과 "되돌리기"를 "새로 시작"(작업을 포기하고 같은 이슈를 새 vstack 작업으로) 하나로 줄인다. 계약 예시 04의 이행 장면도 바꾼다. **계약을 바꾸므로 `vstack-contract@4`가 된다.** 판정식(G1~G5)과 작업자 의무는 그대로다. 진행 중인 작업이 없을 때 한다.
   - `upstream.json`·`UPSTREAM.md`: `user_commands`에서 `agent-orchestra:configure` 제거, 출처는 "아카이브된 원본"으로 표시, closure 검사에서 `moved` 출처를 뺀다.
4. `my-video-manager`의 `AGENTS.md` 줄과 `docs/agents/omp-orchestration.md`의 스킬 언급은 그 저장소의 PR로 고친다(사용자 지시로).

완료 기준: `claude plugin list`에 agent-orchestra 없음, 새 세션에서 `/vstack:v-mode`·`/vstack:configure`·한도 확인이 동작, 계약 예시 네 개를 `@4`로 다시 판정, Codex 검토 `완료`.

### D. agent-orchestra 저장소 아카이브(밖으로 나가는 동작)

1. 원본 README 맨 위에 "vstack으로 옮겼다"는 안내를 넣는다(그 저장소의 마지막 커밋. 사용자 지시로 push).
2. `gh repo archive vananaHope/agent-orchestra`. **사용자가 저장소 이름을 적어 지시할 때만 한다.** 아카이브는 GitHub 설정에서 풀 수 있다.
3. 로컬 클론과 `~/.agent-orchestra/`는 "사용자가 정할 것" 3의 답대로.

완료 기준: 저장소가 아카이브 상태, vstack `UPSTREAM.md`에 아카이브 날짜.

### E. omp를 지휘 작업자 종류로(계약 안)

"사용자가 정할 것" 4. 추천은 7단계에서 떼어 별도 단계로 두는 것이다. 정해야 할 것이 많기 때문이다.

- 계열: 교차 검토는 "구현자와 다른 계열"을 요구한다. omp 작업자의 모델은 omp 설정(`modelRoles`)이 정하고 vstack은 `--model`을 주지 않는다. 그러면 관리자가 배정 때 omp의 계열을 무엇으로 읽을지 정해야 한다.
- 계약: omp 작업자가 `worker-contract.md`(증거 폴더, manifest, 세션 키)를 지키는지 돌려 본 적이 없다. 맡기기 세 번은 모두 계약 밖이었다.
- 서브에이전트: 계약은 "작업자는 다른 작업자를 띄우지 않는다"고 한다. omp 안의 읽기 전용 서브에이전트를 어떻게 볼지 정해야 한다.
- Orca가 omp의 턴 시작을 관측하지 못한다(`turnStart: unsupported`). 시작 실패 판정이 Codex·Claude와 다르다.
- 이득: Codex·Claude 한도가 막혔을 때 쓸 실행기가 하나 는다. omp 설정으로 모델을 바꿔 쓸 수 있다.

하려면 계획(`pilot-7-plan.md`)과 시범이 따로 필요하다.

## 사용자가 정할 것

| # | 질문 | 추천 | 이유 |
| --- | --- | --- | --- |
| 1 | 기존 플러그인을 지우기 전에 실제 프로젝트(`my-video-manager`)에서 vstack 지휘를 한 번 돌릴까 | 먼저 한 번 돌린다(묶음 B) | vstack은 시범 저장소에서만 돌았다. 지금은 agent-orchestra가 유일한 되돌릴 길이다. 실제 프로젝트는 verify 수단과 vstack 절이 없어서, 준비 비용이 얼마인지도 이때 드러난다 |
| 2 | 제거한 뒤, vstack이 아직 하지 않는 일(레시피 없는 작업, UI 다듬기)은 어떻게 할까 | "레시피 없음"을 알리고 한 세션에서 직접 한다. 레시피는 쓸 일이 생길 때 만든다(8단계) | `my-video-manager`의 열린 이슈에 화면 작업이 많다. UI 작업 자체는 `feature` 레시피와 `UI` 배치로 지휘할 수 있고, 빠지는 것은 병합 뒤 "UI 다듬기"와 레시피 없는 작업의 지휘다 |
| 3 | 옛 이름이 남은 위치(`.local/orchestration/settings.md`, `~/.agent-orchestra/`)를 어떻게 할까 | 그대로 둔다. 문서에 "옛 이름이다"만 적는다 | 옮기면 이미 있는 프로젝트 문서(`my-video-manager`가 `~/.agent-orchestra/bin/desktop_lock.py`를 가리킨다)와 설정을 함께 고쳐야 한다. 얻는 것은 이름뿐이다 |
| 4 | omp를 지휘 작업자로 더하는 일(묶음 E) | 7단계에서 떼어 별도 단계로 | 계열 판정, 계약 준수, 서브에이전트 규칙을 새로 정하고 시범을 돌려야 한다. A~D와 묶으면 제거가 늦어진다 |

## 순서

A → (B) → C → D. E는 따로.

- A는 지금 바로 할 수 있다. 문서만 바꾼다.
- B는 다른 저장소의 준비 PR과 새 세션이 필요하다. 사용자가 이슈를 고른다.
- C·D는 되돌릴 수는 있지만 사용자 PC와 GitHub에 남는 변경이다. 각각 이름을 적은 지시로만 한다.

## 하지 않는 것

- herdr 실행 환경 검증. 첫 버전은 Orca만이다(design 1절).
- 관리자를 omp에 두는 것(design 11절 7의 "별도 단계").
- `my-video-manager`의 `omp-orchestration.md` 절차를 vstack으로 옮기는 것. 그 프로젝트의 문서다.
- 새 레시피(성능, 프로토타입, 조사). 8단계다.

## 위험

- B 없이 C를 하면, 실제 프로젝트에서 vstack이 막혔을 때 기존 방식으로 돌아가려면 플러그인을 다시 설치해야 한다(저장소가 아카이브돼도 설치는 된다. 다만 그동안 원본은 Orca 변화에 맞춰 고쳐지지 않는다).
- C의 계약 변경(`@4`)은 진행 중인 지휘 작업이 있으면 그 작업이 `@3`으로 남는다. 진행 중인 작업이 없을 때 한다.
- 제거 뒤 `check-limits`를 이름으로 부르던 습관("한도 확인해 줘")은 vstack 쪽이 받는다. `disable-model-invocation`을 떼지 않으면 `/vstack:v-mode`를 거쳐야 한다.
