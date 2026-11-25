# 문제 해결

## 설치

**vstack이 로드되지 않는다.** vstack은 mattpocock-skills에 기대고, 그 플러그인은 `claude-plugins-official` 마켓플레이스에서 온다. 그 마켓플레이스가 없으면 mattpocock-skills가 설치되지 않고 vstack도 로드되지 않는다. `/plugin marketplace list`로 `claude-plugins-official`이 있는지 보고, 없으면 `/plugin marketplace add anthropics/claude-plugins-official`로 더한다. 빈 설정 폴더에서 명령줄로만 설치했을 때는 등록돼 있지 않았다.

**vstack을 먼저 설치했다.** 나중에 `claude-plugins-official`을 더하면 그때 mattpocock-skills가 설치된다.

**Windows에서 `Filename too long`.** `claude-plugins-official`을 더하다 이 오류가 나면 Claude Code 설정 폴더 경로가 너무 긴 것이다.

**mattpocock-skills의 버전.** vstack은 그 버전을 고정하지 않는다. 마켓플레이스의 새 버전을 따라간다.

**지운 뒤 의존성 정리.** `claude plugin prune --dry-run`으로 대상을 먼저 본다. `claude plugin prune`은 그 범위(기본 user)에서 어느 플러그인도 더는 필요로 하지 않는 자동 설치 의존성을 지운다. 다른 플러그인이 쓰거나 직접 설치한 플러그인은 남는다.

## 첫 실행

**"맡기기는 Orca에서 v-mode를 실행해야 한다".** 맡기기와 지휘는 Orca가 작업자를 띄운다. Claude Code를 Orca 안에서 연다.

**지휘가 설정 창부터 띄운다.** 프로젝트 설정이 없을 때의 정상 동작이다. 저장하면 원래 요청을 이어 간다. 창을 닫으면 지휘를 시작하지 않는다([settings.md](settings.md)).

**v-mode가 검증 수단부터 만들자고 한다.** 사소하지 않은 일인데 요구 동작을 검증할 테스트나 스크립트가 없을 때다. 그 일도 맡기기로 만든다.

**지휘가 "레시피 없음"이라고 한다.** 지휘는 `bug-fix`, `feature`, `refactoring` 레시피가 있는 티켓만 받는다. 한 단위면 맡기기로, 여러 티켓이면 레시피가 있는 유형으로 나눈다([orchestrate.md](orchestrate.md)).

**기능 브랜치에서 지휘하는데 이슈 범위를 묻는다.** 기준 브랜치가 기본 브랜치가 아니면 다룰 이슈를 번호·마일스톤·라벨로 정해야 한다([feature-branch.md](feature-branch.md)).

**병합 위치가 `원격`인데 시작하지 않는다.** 기준 브랜치가 원격에 없다. 기준 브랜치를 먼저 원격에 올리거나, 병합 위치를 `로컬`로 바꾼다.
