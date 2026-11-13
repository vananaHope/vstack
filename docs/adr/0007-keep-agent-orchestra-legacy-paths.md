---
status: accepted
---

# agent-orchestra 때의 경로 이름을 바꾸지 않는다

vstack 지휘는 프로젝트 설정을 `.local/orchestration/settings.md`(또는 `docs/agents/orchestration.md`)에서 읽고, 실창 잠금에 `~/.agent-orchestra/`를 쓴다. vstack의 이름이 아니지만 그대로 둔다. agent-orchestra를 쓰던 프로젝트에 이미 이 파일들이 있고, 두 플러그인이 같은 설정을 읽어야 되돌릴 길(0001)이 산다. 문서에는 "agent-orchestra 때의 이름"이라고만 적는다(2026-11-12 사용자 결정).

agent-orchestra를 은퇴시킨 뒤(2026-11-14, 0001)에도 그대로 둔다. 되돌릴 길은 없어졌지만, 이미 있는 프로젝트의 설정과 문서·스크립트가 이 경로를 가리킨다.

vstack 자신의 작업 파일은 따로 둔다: 지휘는 `.local/vstack/`, 맡기기는 `.local/vstack-delegate/`.
