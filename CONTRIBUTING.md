# vstack 고치기

vstack 자체를 고치는 사람을 위한 문서다. vstack을 쓰는 방법은 [docs/guide/](docs/guide/)에 있다. 에이전트가 따르는 저장소 규칙은 [AGENTS.md](AGENTS.md)와 [docs/agents/](docs/agents/)에 있다.

## 관례

- 이슈와 스펙은 GitHub Issues에 둔다. 트리아지 라벨 다섯 개(`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`)를 이름 그대로 쓴다([issue-tracker.md](docs/agents/issue-tracker.md), [triage-labels.md](docs/agents/triage-labels.md)).
- 커밋과 PR 제목은 `feat|docs|chore: <한국어 문장>(<플러그인 버전>)` 형식으로 쓴다. PR은 squash 병합한다.
- 동작이 바뀌는 변경은 [plugin.json](.claude-plugin/plugin.json) 버전을 올리고 [design.md](docs/design.md)에 절과 변경 이력을 더한다. 계약을 바꾸면 계약 번호도 올린다([contracts/README.md](skills/v-mode/contracts/README.md)). 문서만 고친 변경은 버전을 올리지 않는다.
- 레시피나 계약을 바꾸는 일은 PR로 하고, 병합은 저장소 주인이 승인한다(design.md 7절).
- 되돌리기 어려운 결정은 [docs/adr/](docs/adr/)에 ADR로 남긴다. 기존 ADR과 어긋나면 그 사실을 밝힌다.
- 문서는 한국어 평서문으로 쓰고, 용어는 [GLOSSARY.md](GLOSSARY.md)의 말을 쓴다. _Avoid_로 표시된 동의어는 쓰지 않는다.
- 원문 그대로 가져온 파일(`skills/principle-*` 등)은 고치지 않는다. 고쳐 쓴 사본을 바꾸면 [UPSTREAM.md](UPSTREAM.md)의 "고친 내용"에 기록한다. pstack에서 무언가 가져오기 전에 mattpocock-skills와 겹치는지 먼저 판정한다.
- 사용 안내([docs/guide/](docs/guide/))는 실행 문서를 줄여 옮긴 것이다. 실행 문서의 동작을 바꾸면 그 동작을 설명하는 안내 문서도 같은 PR에서 고친다.

## 구성

```
.claude-plugin/          플러그인·마켓플레이스 정의
skills/v-mode/
  SKILL.md               라우터(고정 규칙, 갈래 고르기, 후보 원칙)
  contracts/             관리자와 작업자가 지키는 계약(vstack-contract@7)
  recipes/               레시피 형식과 레시피(bug-fix, feature, refactoring, ui-polish, investigation, correct, perf)
                         ui-polish는 맡기기 갈래에서만 쓴다. scripts/image_diff.py는 PNG 비교
  delegate*.md           한 단위의 일을 작업자에게 맡기는 절차와 명세 양식(구현, 검토)
  main-repo.md           메인 저장소와 관리자 작업 트리를 정하는 규칙
  subagents.md           바로·맡기기 갈래에서 서브에이전트를 쓰는 규칙
agents/explorer.md       읽기 전용 조사 에이전트 vstack:explorer(Sonnet, 읽기·검색 도구만)
skills/principle-*/      pstack 원칙 24개(원문 그대로)
skills/diagnosing-bugs/, skills/tdd/, skills/create-verification-skill/
                         레시피가 경로로 읽는 스킬(고쳐 쓴 사본, UPSTREAM.md 참고)
skills/ketchup/          마지막 메시지 뒤로 바뀐 것과 사용자가 정할 것을 정리하는 스킬(pstack에서 고쳐 쓴 사본. v-mode가 경로로 읽음)
skills/benchmark-checklist/
                         성능 측정이 믿을 만한지 따지는 점검표(pstack에서 고쳐 쓴 사본. perf 레시피가 경로로 읽음)
skills/maintain-verification-skill/
                         검증 스킬과 기능 지도가 앱과 맞는지 점검하는 스킬(pstack에서 고쳐 쓴 사본. 맡기기의 구현자가 경로로 읽음)
skills/blast-radius/     변경이 다른 곳에서 깨뜨릴 것을 찾아 실행으로 증명하는 스킬
                         (pstack에서 고쳐 쓴 사본. 검토 명세와 v-mode가 경로로 읽음)
skills/orchestrate-issues/, skills/check-limits/, skills/configure/
                         지휘, 한도 확인, 프로젝트 설정 스킬(agent-orchestra에서 옮겨 와 vstack이 소유. v-mode가 경로로 읽음.
                         프로젝트 설정은 맡기기와 지휘가 함께 읽는다)
GLOSSARY.md              용어집
CONTRIBUTING.md          이 문서
docs/
  guide/                 사용 안내(사용자용. 규칙의 정본은 skills/의 실행 문서)
  design.md              설계와 변경 이력
  adr/                   되돌리기 어려운 결정 기록
  images/                README와 사용 안내의 그림(밝은·어두운 테마 SVG 두 벌. 고칠 원본은 images/src/의 HTML)
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
python -I -m unittest discover -s skills/v-mode/recipes/scripts -p "test_*.py"   # 이미지 비교 스크립트의 테스트
```

`check-links`가 잡는 것: 깨진 경로(`BROKEN`), vstack 파일을 표준이 아닌 인라인 경로로 가리킴(`NONSTANDARD`), vstack에 없는 스킬 이름(`SKILL`. 사용자가 직접 실행하는 다른 플러그인 명령은 `upstream.json`의 `user_commands`에 적은 것만 허용), 특정 런타임의 스킬 도구 문장(`TOOL`), `--source`를 주면 원본이 가리키던 파일의 누락(`NOT CARRIED`). 자세한 규칙은 [UPSTREAM.md](UPSTREAM.md)와 [FORMAT.md](skills/v-mode/recipes/FORMAT.md) "실행 경로 표기". `check-links`는 `skills/` 아래만 본다. README, CONTRIBUTING, `docs/`의 링크는 고칠 때 직접 확인한다.
