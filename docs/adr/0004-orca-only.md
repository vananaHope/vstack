---
status: accepted
---

# 작업자를 띄우는 실행 환경은 Orca만 쓴다

맡기기와 지휘는 작업자를 Orca로 띄우고 감독한다(`orca orchestration`의 Run, Task, Dispatch, 질문과 완료 보고). Orca가 없으면 v-mode는 바로 갈래만 하고, 그 밖의 일은 "Orca에서 실행하라"고 알리고 멈춘다. Orca 없이 맡기는 수단(Claude Code 서브에이전트로 구현하고 `codex exec`로 검토하기)은 만들지 않는다. 사용자가 Orca 없는 환경에서는 vstack을 쓰지 않기로 했고(2026-11-13), 같은 절차를 두 벌 유지하는 비용이 크다.

agent-orchestra에서 옮겨 온 herdr 실행 환경 문서(`skills/orchestrate-issues/backends/herdr.md`)는 남아 있지만 검증하지 않았다.
