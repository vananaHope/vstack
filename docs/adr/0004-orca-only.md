---
status: accepted
---

# 맡기기는 Orca에서만 하고, 지휘는 Orca로만 검증한다

맡기기는 작업자를 Orca로 띄우고 감독한다(`orca orchestration`의 Run, Task, Dispatch, 질문과 완료 보고). Orca가 없으면 맡기기를 하지 않고 "Orca에서 실행하라"고 알린 뒤 멈춘다. Orca 없이 맡기는 수단(Claude Code 서브에이전트로 구현하고 `codex exec`로 검토하기)은 만들지 않는다. 사용자가 Orca 없는 환경에서는 vstack을 쓰지 않기로 했고(2026-11-13), 같은 절차를 두 벌 유지하는 비용이 크다.

지휘는 첫 버전부터 Orca로만 검증했다([design.md](../design.md) 1절). agent-orchestra에서 옮겨 온 herdr 실행 환경(`skills/orchestrate-issues/backends/herdr.md`)은 지휘가 지금도 고를 수 있지만 검증하지 않았다. 지휘에서도 herdr를 뺄지는 전체 검수에서 정한다.
