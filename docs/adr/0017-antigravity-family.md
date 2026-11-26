---
status: accepted
---

# Antigravity를 셋째 계열로 더한다

지휘와 맡기기의 작업자 계열에 `antigravity`를 더한다. Antigravity CLI(`agy`)로 Gemini 모델을 쓰는 작업자다. 계열은 `codex`, `claude`, `antigravity` 셋이 된다. 사용자 결정이다(2026-11-26).

**[ADR 0012](0012-no-opencode.md)와 어긋난다.** 0012는 셋째 계열(OpenCode)을 빼면서 "계열은 Codex와 Claude 둘"로 정했다. 이 결정은 그 문장을 뒤집는다. 0012가 뺀 까닭은 셋째 계열이 실제로 쓰이지 않았는데도 계열 규칙·설정 창·검사 스크립트를 복잡하게 했다는 것이다. 이번에는 사용자가 Gemini 모델을 Claude·Codex와 같은 급으로 쓰겠다고 정했다.

- **기본 배치에 넣는다.** 구현 목록에서는 Claude 앞(Codex 다음), 검토 목록에서는 Codex 뒤에 둔다(`tiers.md` "기본 배치"). `agy`가 없거나 로그인이 없는 컴퓨터에서는 어느 목록에서든 건너뛰므로, Antigravity를 쓰지 않는 프로젝트의 배치는 지금과 같다. 명세 점검의 기본값은 그대로 `claude`다.
- **맡기기도 고를 수 있다.** 맡기기의 구현자와 검토자 목록을 프로젝트 설정 "맡기기 배치"로 정한다. 기본은 구현자 `claude:opus`, 검토자 `codex` → `antigravity` → `claude`이고, 검토자는 구현자와 다른 계열의 첫 항목이다. [ADR 0009](0009-cross-family-review-via-orca-codex.md)의 "검토는 Orca로 띄운 Codex 작업자"는 기본값으로 남고, 고정이 아니게 됐다.
- **Orca가 직접 띄운다.** Orca의 `worker-start --agent antigravity`가 `--model`·`--effort`를 받는다. [ADR 0008](0008-no-omp.md)이 omp를 뺀 까닭(Orca가 턴 시작을 관측하지 못함, 모델을 관리자가 모름)과 달리, 모델은 관리자가 표기로 정하고 Orca가 작업자로 감독한다. 아직 돌려 보지 않았으므로, 첫 실행에서 Orca가 턴을 보는지 확인하고 못 보면 그 작업자를 `실패`로 넘긴다(`backends/orca.md` "띄우기").
- **한도를 잰다.** `agy -p /usage`의 글 보고(모델 그룹마다 5시간·주간 남은 비율과 초기화 시각)를 `check-limits`의 `agy_limit.py`가 읽는다. 판정은 `Gemini Models` 그룹을 본다. 보고 형식은 문서에 없고 사용자 컴퓨터의 출력(2026-11-26)에 맞췄다. 그래서 형식이 바뀌면 `unknown`이 되고 Antigravity만 건너뛴다. 지휘 전제로 막지 않는다.

계약은 `vstack-contract@7`로 올렸다. 역할 자격의 "변경 작성자와 다른 계열"에 `antigravity`가 들어간다.

**Considered Options**: 기본 배치에 넣지 않고 설정에 적을 때만 쓰는 길(0.30.0의 첫 초안)과, 목록 끝에 대체 계열로만 두는 길도 있었다. 사용자가 Claude·Codex와 같은 주 계열을 골랐다. UI 구현은 그대로 Claude 고정이다. Gemini CLI를 쓰는 길도 있었다. 사용자가 쓰는 도구는 Antigravity CLI이고, Orca가 받는 에이전트도 `antigravity`다. Claude Code 서브에이전트로 Gemini를 쓰는 길은 없다. Claude Code의 Agent 도구는 Claude 모델만 받는다(0009). 그래서 Gemini는 작업자와, 관리자가 셸로 부르는 `agy -p`(명세 점검, 2차 의견)로만 쓴다.

**돌려 보지 않았다.** Antigravity 작업자, 맡기기의 Antigravity 구현자·검토자, `agy -p`의 읽기 전용 실행(`--mode plan --sandbox`), Orca의 턴 관측, `agy_limit.py`의 실제 실행(붙여 받은 출력으로만 확인)은 아직 시범이 없다.
