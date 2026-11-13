---
status: accepted
---

# agent-orchestra를 vstack으로 옮기고, 원래 저장소는 vstack이 완성된 뒤 아카이브한다

지휘(이슈를 작업자에게 맡기고 교차 검토와 병합까지 하는 흐름)는 사용자가 직접 만든 agent-orchestra에 있었다. 두 플러그인을 나란히 두고 서로 부르게 하는 대신, 그 스킬(`orchestrate-issues`, `check-limits`, `configure`)을 vstack으로 옮겨 vstack의 계약에 맞게 고쳤다. 두 저장소에 같은 절차가 두 벌로 갈라져 자라지 않게 하려는 것이다.

원래 플러그인은 지우지 않고 되돌릴 길로 남겨 둔다. 지우고 아카이브하는 시점은 아래 셋이 모두 맞을 때다(2026-11-14 사용자 결정).

1. "관리자는 관리만" 변경이 병합됐다.
2. 전체 검수에서 사용자가 고른 것을 고쳤다.
3. 실제 프로젝트(`my-video-manager`)에서 v-mode로 맡기기와 지휘를 각각 한 번 이상 끝까지 돌렸고, 그동안 agent-orchestra로 돌아갈 일이 없었다.

**Considered Options**: 두 플러그인을 함께 두고 vstack이 agent-orchestra를 부르는 길은 버렸다. 고칠 곳이 두 저장소로 나뉘고, vstack의 계약(증거, 병합 관문)을 agent-orchestra 쪽 문서에 넣을 수 없었다.
