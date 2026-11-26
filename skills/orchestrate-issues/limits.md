# 한도와 모드

측정은 [check-limits](../check-limits/SKILL.md)로 한다. 판정(`ok`/`warning`/`exhausted`/`unknown`)과 보고 형식은 그 문서를 따른다. 이 파일은 판정에 따라 지휘 배치를 어떻게 바꾸는지 정한다.

## 재는 때

- 지휘를 시작할 때
- 새 작업을 맡기기 직전
- 모드를 바꾸거나 되돌리기 직전
- 메모리나 기록에 "한도 소진"이 있을 때
- Codex와 Claude는 사용량이 들지 않으므로 깨어날 때마다 봐도 된다. Antigravity는 `agy -p /usage`가 사용량을 쓰는지 모르므로 지휘를 시작할 때와 Antigravity에게 새 작업을 맡기기 직전에만 잰다. 단, Codex 측정이 `codex exec`로 넘어간 동안(`source`가 `exec`)은 직전 측정이 30분 넘게 지났을 때만 다시 잰다.

## 판정에 따른 처리

- `warning`: 사용률과 초기화 시각을 사용자에게 알린다. Claude면 아래 Claude 절약 모드로 간다.
- `exhausted`: 아래 해당 모드로 전환한다.
- `unknown`: 추측하지 말고 사용자에게 알린다. 그 에이전트에게는 새 작업을 맡기지 않는다.

## 대체 모드: Codex `exhausted`

Codex의 몫을 목록의 다음 항목(Claude, 목록에 있으면 Antigravity)이 맡는다. 관리자가 스스로 전환하고 사용자에게는 전환 사실만 알린다. 한도가 돌아오면 원래 배치로 복귀하고 알린다.

- 구현: 등급 목록에서 Codex를 건너뛴다([tiers.md](tiers.md) "고르기"). 목록이 다 막히면 위 등급으로 가고, 기본 목록이면 `hard`의 Claude가 받는다.
- 검토: 검토 목록에서 Codex를 건너뛴다([tiers.md](tiers.md) "검토자 고르기"). 다른 계열(Claude가 구현했으면 Antigravity)이 목록에 있고 `ok`면 그 계열이 검토한다. 그것도 남지 않으면 새 Claude 검토자가 맡고, 주 검토자와 다른 Claude 모델에게 2차 의견을 받는다(같은 규칙의 2, [tiers.md](tiers.md) "2차 의견").
- 해당 PR 본문에 "대체 모드(Codex 한도 소진)로 구현·검토"라고 적는다.

## Claude 절약 모드: Claude `warning` 또는 `exhausted`

Claude 구현의 몫을 Codex가 맡는다(목록에 Antigravity가 있으면 목록 순서대로 Antigravity도 맡는다). 관리자도 Claude이므로 관리자 자신의 일을 줄이는 것이 먼저다. 검토는 구현보다 짧으므로 `warning`에서는 Claude 검토를 계속한다. Codex 한도가 더 빠듯한 계정에서 검토까지 Codex로 몰면 Codex가 먼저 바닥난다. 전환 사실과 측정 숫자를 사용자에게 알린다. 한도가 `ok`로 돌아오면 원래 배치로 복귀하고 알린다.

- 관리자: 직접 diff를 읽는 확인(`light` 확인, 사소 수정 확인, UI 다듬기)을 하지 않는다. 그 확인도 Codex 검토에 맡긴다. 깨어나면 메시지 처리·판정·병합만 한다.
- 검토: 검토 목록에서 `관리자`를 건너뛴다. `warning`이면 Claude 검토자는 `claude:sonnet`으로 띄운다(목록이 다른 Claude 모델을 적었어도). 그 검토에 2차 의견이 필요하고 다른 계열(Codex, Antigravity)을 쓸 수 없으면 `claude:haiku`에게 묻는다([tiers.md](tiers.md) "2차 의견"). `exhausted`면 Claude도 건너뛴다([tiers.md](tiers.md) "검토자 고르기"). Codex가 구현한 일처럼 다른 계열이 남지 않으면(목록에 Antigravity가 있고 `ok`면 Antigravity가 검토한다) **새 Codex 검토자**가 맡고, 주 검토자와 다른 Codex 모델에게 2차 의견을 받는다(같은 규칙의 2, [tiers.md](tiers.md) "2차 의견").
- UI 구현: 새 UI 이슈는 시작하지 않고 Claude 한도가 돌아올 때까지 미룬다. 이미 진행 중인 Claude 작업은 멈추지 않는다.
- 코어 구현: 등급 목록에서 Claude를 건너뛴다.
- **5시간 창이 `exhausted`가 되면 관리자도 멈춘다.** 그 전에(`warning`에서) 진행 중인 작업과 다음 순서를 사용자에게 보고하고, 초기화 시각 뒤에 이어 가겠다고 알린다. 7일 창이 `exhausted`면 사용자에게 계속할지 묻는다.
- 해당 PR 본문에 "Claude 절약 모드(Claude 한도 경고)로 검토"라고 적는다.

## Antigravity

Antigravity도 [check-limits](../check-limits/SKILL.md)의 `agy_limit.py`로 재고, 판정에 따른 처리는 위 "판정에 따른 처리"와 같다. 다른 점만 적는다.

- `agy`가 없는 컴퓨터에서는 재지 않고, 목록의 `antigravity` 항목을 건너뛴다([tiers.md](tiers.md) "고르기" 1). 알림은 지휘를 시작할 때 한 번만 한다.
- `warning`이면 사용률과 초기화 시각을 알리고 그대로 쓴다. 절약 모드는 따로 없다.
- `exhausted`면 목록에서 건너뛴다. Antigravity의 몫은 목록의 다음 항목이 맡는다. 검토에서 다른 계열이 남지 않으면 위 "대체 모드"의 같은 계열 규칙(새 작업자, 2차 의견 필수)을 따른다.
- `unknown`인데 `agy`는 있다(보고 형식이 바뀜 등): 사용자에게 알리고 `antigravity` 항목을 건너뛴다.
- 재지 못한 동안이나 잰 뒤에도 작업자나 `agy -p`가 한도·할당량 오류로 끝나면 `state.md`에 `Antigravity exhausted(<시각>, <오류 한 줄>)`를 적고 사용자에게 알린다. 다음 측정이 `ok`나 `warning`이면 그 기록을 지운다.
- 로그인 오류(`authentication required`)는 한도가 아니다. 그 작업자를 `실패`로 넘기고(`tiers.md` "맡김 기록"), 사용자에게 `agy`를 한 번 대화형으로 실행해 로그인하라고 알린다. 로그인했다는 답을 받기 전에는 건너뛴다.

## 둘 다 `exhausted`

Codex와 Claude가 둘 다 `exhausted`인 경우다. 관리자가 Claude이므로 Antigravity가 `ok`여도 새 작업을 시작하지 않는다. 진행 중인 작업 목록과 각 한도의 초기화 시각을 사용자에게 보고하고, 먼저 돌아오는 한도를 기다린다.
