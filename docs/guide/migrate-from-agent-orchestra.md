# agent-orchestra를 쓰던 프로젝트에서

vstack이 agent-orchestra를 대신한다. agent-orchestra 플러그인은 지웠고 원래 저장소는 아카이브했다(2026-11-14, [ADR 0001](../adr/0001-move-agent-orchestra-into-vstack.md)). vstack 하나만 설치하면 된다.

- 프로젝트 설정(`docs/agents/orchestration.md` 또는 `.local/orchestration/settings.md`)과 `common-findings.md`는 그대로 읽는다.
- `.local/orchestration/`(개인용 설정 위치)과 `~/.agent-orchestra/`(실창 잠금)는 agent-orchestra 때의 이름이다. 경로는 바꾸지 않았다([ADR 0007](../adr/0007-keep-agent-orchestra-legacy-paths.md)). vstack의 작업 파일은 `.local/vstack/`에 따로 둔다.
- vstack 지휘가 다르게 하는 것: 레시피가 있는 작업(버그 수정, 기능, 리팩토링)만 맡는다. 레시피가 없는 일은 한 단위면 맡기기 갈래로 수용 기준만으로 맡기고, 여러 티켓이면 티켓마다 레시피가 있는 유형으로 나누거나 레시피를 먼저 만든다. 검토 목록의 `관리자` 항목은 건너뛴다. UI 다듬기는 지휘에서 하지 않고 맡기기 갈래의 `ui-polish` 레시피로 한다. 앞부분 선행 병합은 하지 않는다(`skills/orchestrate-issues/vstack.md` "첫 버전에서 하지 않는 것").
- 처음 지휘하기 전에 갖출 것: 요구 동작을 검증할 수단(없으면 v-mode가 검증 스킬 만들기부터 한다)과 티켓의 vstack 절(v-mode가 초안을 쓰고 승인을 받는다).
- agent-orchestra 때 끝나지 않은 작업(`.local/orchestration/*/state.md`)은 vstack이 이어받지 않고 사용자에게 알린다.
