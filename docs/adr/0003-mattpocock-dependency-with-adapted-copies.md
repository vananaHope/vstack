---
status: accepted
---

# mattpocock-skills를 의존성으로 함께 설치하고, 레시피가 쓰는 두 스킬만 고친 사본을 둔다

정렬 단계(`grill-with-docs`, `to-spec`, `to-tickets`)는 mattpocock-skills를 그대로 쓴다. 그래서 `plugin.json`에 의존성으로 적고, 다른 마켓플레이스(`claude-plugins-official`)의 의존성을 허락한다(`marketplace.json`의 `allowCrossMarketplaceDependenciesOn`). 그 마켓플레이스가 없으면 vstack이 뜨지 않는다. 사용자가 이미 쓰는 플러그인이라 두 벌을 두지 않으려는 것이다.

그런데 레시피가 경로로 읽는 `tdd`와 `diagnosing-bugs`는 고친 사본을 vstack 안에 둔다. 원본은 seam마다 사용자에게 묻고, 사람이 입력할 때까지 셸에서 기다리는 스크립트를 쓴다. 무인 작업자가 그대로 따르면 멈추거나 사용자를 막는다. 의존성으로 원본도 설치되므로 같은 이름이 두 벌 있다. 이 사본을 계속 둘지는 전체 검수에서 다시 본다.
