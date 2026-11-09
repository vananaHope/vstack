# vstack

Claude Code 플러그인. `v-mode` 라우터가 요청에 맞는 레시피를 고르고, 레시피는 원칙과 검증 계약을 지키며 일한다. mattpocock 정렬 스킬(무엇을, 왜), pstack 원칙과 검증(어떻게 제대로), agent-orchestra 지휘(누가, 언제)를 하나로 묶는다.

> 만드는 중이다. 지금은 0~5단계(계약, 플러그인 골격·출처 관리, 원칙 24개와 버그 수정 레시피, 옮겨 온 지휘 스킬, Orca 시범 두 번, 최소 v-mode 라우터)까지 있다. 레시피는 버그 수정 하나다. 진행 상태와 설계는 [docs/design.md](docs/design.md)에 있다.

## 설치

vstack은 mattpocock-skills(`claude-plugins-official` 마켓플레이스)에 기댄다. 정렬 단계의 `grill-with-docs`·`to-spec`·`to-tickets`와 `wait-what`이 그 플러그인의 명령이다. vstack은 이것을 의존성으로 선언해 두었으므로, 그 마켓플레이스가 추가돼 있으면 vstack을 설치할 때 함께 설치된다. 그 마켓플레이스가 없으면 mattpocock-skills가 설치되지 않고 **vstack도 로드되지 않는다**. 먼저 `/plugin marketplace list`로 `claude-plugins-official`이 등록돼 있는지 확인하고, 없으면 아래처럼 추가한다(빈 설정 폴더에서 명령줄로만 설치했을 때는 등록돼 있지 않았다).

```
/plugin marketplace add anthropics/claude-plugins-official   # 이미 있으면 건너뛴다
/plugin marketplace add vananaHope/vstack
/plugin install vstack@vstack                                # mattpocock-skills도 함께 설치된다
```

- 순서를 바꿔 vstack을 먼저 설치했으면, 나중에 `claude-plugins-official`을 추가할 때 mattpocock-skills가 설치된다.
- mattpocock-skills는 버전을 고정하지 않았다. 그 마켓플레이스의 새 버전을 따라간다.
- vstack을 지운 뒤 의존성을 정리하려면 `claude plugin prune --dry-run`으로 대상을 먼저 본다. `claude plugin prune`은 그 범위(기본 user)에서 어느 플러그인도 더는 필요로 하지 않는 자동 설치 의존성을 지운다. 다른 플러그인이 쓰거나 직접 설치한 플러그인은 남는다.
- Windows에서 `claude-plugins-official` 추가가 `Filename too long`으로 실패하면 설정 폴더 경로가 너무 긴 것이다.

## 쓰기

`/vstack:v-mode`로 시작해 하려는 일을 말한다. v-mode가 크기와 작업 유형을 보고 갈래를 고른다.

- 바로: 질문·조사, 자명한 작은 수정
- 한 세션: 레시피가 있는 한 단위의 일(지금은 버그 수정)을 이 대화에서 레시피대로 한다. 교차 검토·병합 관문은 없다
- 지휘: 정렬(`grill-with-docs` → `to-spec` → `to-tickets`, mattpocock 플러그인 명령) → 티켓에 vstack 절 → 작업자 배정·교차 검토·증거 보관·병합 관문(Orca)

## 구성

```
.claude-plugin/          플러그인·마켓플레이스 정의
skills/v-mode/
  SKILL.md               라우터(고정 규칙, 갈래 고르기, 후보 원칙)
  contracts/             관리자와 작업자가 지키는 계약(vstack-contract@3)
  recipes/               레시피 형식과 레시피(bug-fix)
skills/principle-*/      pstack 원칙 24개(원문 그대로)
skills/diagnosing-bugs/, skills/tdd/, skills/create-verification-skill/
                         레시피가 경로로 읽는 스킬(고쳐 쓴 사본, UPSTREAM.md 참고)
skills/orchestrate-issues/, skills/check-limits/, skills/configure/
                         agent-orchestra에서 옮겨 온 지휘 스킬(v-mode가 경로로 읽음)
docs/
  design.md              설계와 변경 이력
  contract-examples/     계약 판정 예시
upstream.json            가져오는 파일 목록(정본)
UPSTREAM.md              출처, 고친 내용, 갱신 절차
licenses/                출처별 라이선스 원문
scripts/
  import.mjs             upstream.json대로 가져오기(verbatim 덮어쓰기, adapted 처음 한 번)
  collect-references.mjs 출처 참조 목록(reference-policy.md) 생성
  check-links.mjs        실행 경로의 링크 검사
```

## 검사

```
node scripts/check-links.mjs --stage <현재 단계> [--source pstack=<cursor/plugins> --source mattpocock-skills=<mattpocock-skills>]
node scripts/collect-references.mjs --source pstack=<cursor/plugins> --check
```

`check-links`가 잡는 것: 깨진 경로(`BROKEN`), vstack 파일을 표준이 아닌 인라인 경로로 가리킴(`NONSTANDARD`), vstack에 없는 스킬 이름(`SKILL`. 사용자가 직접 실행하는 다른 플러그인 명령은 `upstream.json`의 `user_commands`에 적은 것만 허용), 특정 런타임의 스킬 도구 문장(`TOOL`), `--source`를 주면 원본이 가리키던 파일의 누락(`NOT CARRIED`). 자세한 규칙은 [UPSTREAM.md](UPSTREAM.md)와 [FORMAT.md](skills/v-mode/recipes/FORMAT.md) "실행 경로 표기".

## 라이선스

MIT. [LICENSE](LICENSE). 가져온 파일의 출처와 라이선스는 [UPSTREAM.md](UPSTREAM.md)와 [licenses/](licenses/)에 있다.
