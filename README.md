# vstack

Claude Code 플러그인. `v-mode` 라우터가 요청에 맞는 레시피를 고르고, 레시피는 원칙과 검증 계약을 지키며 일한다. mattpocock 정렬 스킬(무엇을, 왜), pstack 원칙과 검증(어떻게 제대로), agent-orchestra 지휘(누가, 언제)를 하나로 묶는다.

> 만드는 중이다. 지금은 0~2단계(계약, 플러그인 골격·출처 관리, 원칙 24개와 버그 수정 레시피)까지 있다. 진행 상태와 설계는 [docs/design.md](docs/design.md)에 있다.

## 설치

```
/plugin marketplace add vananaHope/vstack
/plugin install vstack@vstack
```

## 구성

```
.claude-plugin/          플러그인·마켓플레이스 정의
skills/v-mode/
  contracts/             관리자와 작업자가 지키는 계약(vstack-contract@3)
  recipes/               레시피 형식과 레시피(bug-fix)
skills/principle-*/      pstack 원칙 24개(원문 그대로)
skills/diagnosing-bugs/, skills/tdd/, skills/create-verification-skill/
                         레시피가 경로로 읽는 스킬(고쳐 쓴 사본, UPSTREAM.md 참고)
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

`check-links`가 잡는 것: 깨진 경로(`BROKEN`), vstack 파일을 표준이 아닌 인라인 경로로 가리킴(`NONSTANDARD`), vstack에 없는 스킬 이름(`SKILL`), 특정 런타임의 스킬 도구 문장(`TOOL`), `--source`를 주면 원본이 가리키던 파일의 누락(`NOT CARRIED`). 자세한 규칙은 [UPSTREAM.md](UPSTREAM.md)와 [FORMAT.md](skills/v-mode/recipes/FORMAT.md) "실행 경로 표기".

## 라이선스

MIT. [LICENSE](LICENSE). 가져온 파일의 출처와 라이선스는 [UPSTREAM.md](UPSTREAM.md)와 [licenses/](licenses/)에 있다.
