---
status: accepted
---

# Antigravity를 지휘의 셋째 계열로 더한다

지휘의 작업자 계열에 `antigravity`를 더한다. Antigravity CLI(`agy`)로 Gemini 모델을 쓰는 작업자다. 계열은 `codex`, `claude`, `antigravity` 셋이 된다. 사용자 결정이다(2026-11-26).

**[ADR 0012](0012-no-opencode.md)와 어긋난다.** 0012는 셋째 계열(OpenCode)을 빼면서 "계열은 Codex와 Claude 둘"로 정했다. 이 결정은 그 문장을 뒤집는다. 0012가 뺀 까닭은 셋째 계열이 쓰이지 않았는데도 계열 규칙·설정 창·검사 스크립트를 복잡하게 했다는 것이다. 이번에는 사용자가 Gemini 모델을 쓰겠다고 정했다. 그래서 0012가 지적한 비용을 줄이는 쪽으로 넣는다.

- **기본 배치에 넣지 않는다.** `tiers.md`의 기본 배치와 명세 점검의 기본값은 그대로 `codex`, `claude`다. 프로젝트 설정의 목록에 `antigravity`를 적은 프로젝트만 쓴다. `agy`가 없는 프로젝트의 동작은 바뀌지 않는다.
- **Orca가 직접 띄운다.** Orca의 `worker-start --agent antigravity`가 `--model`·`--effort`를 받는다. [ADR 0008](0008-no-omp.md)이 omp를 뺀 까닭(Orca가 턴 시작을 관측하지 못함, 의존 도구 하나 더, 모델을 관리자가 모름)과 달리, 모델은 관리자가 표기로 정하고 Orca가 작업자로 감독한다. 다만 아직 돌려 보지 않았으므로, 첫 실행에서 Orca가 턴을 보는지 확인하고 못 보면 그 작업자를 `실패`로 넘긴다(`backends/orca.md` "띄우기").
- **한도는 재지 않는다.** Antigravity의 사용량을 읽을 방법이 없다. 그래서 한도 오류를 기록해 판정한다(`limits.md` "Antigravity"). Claude·Codex처럼 `unknown`이면 맡기지 않는 규칙을 Antigravity에는 쓰지 않는다. 쓰면 한 번도 맡길 수 없다.
- **맡기기는 그대로다.** 맡기기의 구현자(Claude)와 검토자(Codex)는 바꾸지 않았다([ADR 0009](0009-cross-family-review-via-orca-codex.md)).

계약은 `vstack-contract@7`로 올렸다. 역할 자격의 "변경 작성자와 다른 계열"에 `antigravity`가 들어간다.

**Considered Options**: Gemini CLI를 쓰는 길도 있었다. 사용자가 쓰는 도구는 Antigravity CLI이고, Orca가 받는 에이전트도 `antigravity`다. Claude Code 서브에이전트로 Gemini를 쓰는 길은 없다. Claude Code의 Agent 도구는 Claude 모델만 받는다(0009). 그래서 Gemini는 작업자와, 관리자가 셸로 부르는 `agy -p`(명세 점검, 2차 의견)로만 쓴다.

**돌려 보지 않았다.** Antigravity 작업자, `agy -p`의 읽기 전용 실행(`--mode plan --sandbox`), Orca의 턴 관측은 아직 시범이 없다.
