# 02. 기준 브랜치 이동

01a가 (H1=1111aaa, B1=bbbb001)에서 두 역할 모두 통과하고 `지시 대기`가 됐다. 사흘 뒤 사용자가 "병합해"라고 했다.

## 02a. rebase 뒤 두 역할 재검증

1. 관리자가 B를 다시 읽는다: `main`이 B2=bbbb002로 갔다. 진입점 "병합해" → 바뀌었으므로 rebase 행.
2. rebase를 `light` 목록의 `opencode`에게 맡긴다. 새 세션 `term-o2`, 시도 `impl-5a5a5a5a-1`. 충돌 없음. H2=2222bbb.
3. `term-o2`가 (H2, B2)의 변경 작성자이므로 impl이다. AC-1·AC-2 전부를 (H2, B2)에서 돌린다.
4. 대상이 바뀌었으므로 rev `review` 시도를 배정한다. (H2, B2)에 커밋하지 않았고 opencode와 다른 계열인 원래 검토자 세션 `term-r1`(claude)에 `rev-3ecbf1e7-2`로 보낸다. rebase diff와 브랜치 전체를 검토하고 AC 전부를 돌린다. 결론 `통과`.

### 시도 표

| 시도 ID | 역할 | scope | 맡은 AC | 실행기 | 세션 | 대상 H | 대상 B | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `impl-d195b9cc-1` | impl | | AC-1, AC-2 | codex | `term-c1` | 1111aaa | bbbb001 | 정리됨 |
| `rev-3ecbf1e7-1` | rev | review | AC-1, AC-2 | claude | `term-r1` | 1111aaa | bbbb001 | 정리됨 |
| `impl-5a5a5a5a-1` | impl | | AC-1, AC-2 | opencode | `term-o2` | 2222bbb | bbbb002 | 정리됨 |
| `rev-3ecbf1e7-2` | rev | review | AC-1, AC-2 | claude | `term-r1` | 2222bbb | bbbb002 | 정리됨 |

### manifest(판정에 쓰는 필드만)

`impl-5a5a5a5a-1/manifest.json`

```json
{
  "contract": "vstack-contract@3", "task": "issue-42",
  "attempt": "impl-5a5a5a5a-1", "role": "impl", "executor": "opencode", "session": "5a5a5a5a",
  "recipe": "bug-fix@3",
  "target": { "head": "2222bbb…", "base": "bbbb002…", "base_ref": "main" },
  "tree_before": "",
  "env": { "build_from_head": "rebase 뒤 H2에서 npm run build, 서버 새로 시작(포트 5174)" },
  "patch_id": "p-91ab…",
  "results": [
    { "acceptance": "AC-1@1", "command": "npm run verify -- toggle-persist", "exit": 0,
      "artifacts": ["ac-1/after-reload.png", "ac-1/run.log"], "verdict": "통과" },
    { "acceptance": "AC-2@1", "command": "npm test -- persistence", "exit": 0,
      "artifacts": ["ac-2/test.log"], "verdict": "통과" }
  ],
  "files": [
    { "path": "ac-1/after-reload.png", "sha256": "…", "bytes": 47930 },
    { "path": "ac-1/run.log", "sha256": "…", "bytes": 1302 },
    { "path": "ac-2/test.log", "sha256": "…", "bytes": 2210 }
  ]
}
```

`rev-3ecbf1e7-2/manifest.json`

```json
{
  "contract": "vstack-contract@3", "task": "issue-42",
  "attempt": "rev-3ecbf1e7-2", "role": "rev", "scope": "review", "executor": "claude", "session": "3ecbf1e7",
  "recipe": "bug-fix@3",
  "target": { "head": "2222bbb…", "base": "bbbb002…", "base_ref": "main" },
  "tree_before": "",
  "env": { "build_from_head": "Doctor로 5174 서버가 내 것이 아님을 확인, 내려간 뒤 H2에서 새로 빌드·시작(포트 5175)" },
  "patch_id": "p-91ab…",
  "results": [
    { "acceptance": "AC-1@1", "command": "npm run verify -- toggle-persist", "exit": 0,
      "artifacts": ["ac-1/after-reload.png", "ac-1/run.log"], "verdict": "통과" },
    { "acceptance": "AC-2@1", "command": "npm test -- persistence", "exit": 0,
      "artifacts": ["ac-2/test.log"], "verdict": "통과" }
  ],
  "files": [
    { "path": "ac-1/after-reload.png", "sha256": "…", "bytes": 48002 },
    { "path": "ac-1/run.log", "sha256": "…", "bytes": 1311 },
    { "path": "ac-2/test.log", "sha256": "…", "bytes": 2210 }
  ]
}
```

`patch_id`는 01a의 두 시도와 같다(깨끗한 rebase). 기록만 하고 재사용 근거로 쓰지 않는다.

### 집계(대상 H2/B2)

| AC | impl | rev | 집계 |
| --- | --- | --- | --- |
| AC-1@1 | `impl-5a5a5a5a-1` · 통과 | `rev-3ecbf1e7-2` · 통과 | 통과 |
| AC-2@1 | `impl-5a5a5a5a-1` · 통과 | `rev-3ecbf1e7-2` · 통과 | 통과 |

01a의 두 시도는 대상이 (H1, B1)이라 고르지 않는다.

### 관문

| G1 | G2 | G3 | G4 | G5 | 결과 |
| --- | --- | --- | --- | --- | --- |
| 통과 | 통과 | 통과(`rev-3ecbf1e7-2`) | 통과(4개 정리됨) | 통과(`term-r1`은 H2에 커밋 안 함, claude ≠ opencode) | 병합 명령 → `MERGED` 확인 |

## 02b. rebase가 테스트를 약하게 만듦

2단계에서 충돌이 났고, rebase 작업자가 `persistence` 테스트의 assertion을 `toEqual(done)`에서 `toBeDefined()`로 바꿔 충돌을 풀었다.

- `impl-5a5a5a5a-1`: AC-2 통과(약해진 테스트라 통과).
- `rev-3ecbf1e7-2`(review): AC-2를 돌리면 통과한다. 그러나 "AC-2의 테스트가 약해졌다"를 `차단`으로 지적한다. 근거로, 원래 assertion을 넣은 테스트 사본을 자기 scratch에서 돌려 실패를 확인한다(제품 테스트 파일은 고치지 않는다). 결론 `수정 필요`.
- G1 통과, G3 **실패** → 차단.
- 5단계 `지금 고침`. 설계를 다시 잡는 수정이라 원래 구현자 세션(`term-c1`)에 보낸다. 고치면 H3 → impl(`term-c1`) 전부 + rev `review`(`term-r1`) 전부.

테스트가 약해졌는지는 수용 기준 실행이 아니라 코드 검토(G3)가 잡는다.

## 02c. 같은 세션이 rev를 맡으려 함

관리자가 실수로 rebase 세션 `term-o2`에게 "rev로도 돌려 줘"라고 보냈다고 하자(`rev-5a5a5a5a-1`).

- `term-o2`는 (H2, B2)에 커밋을 만든 세션이므로 rev 자격이 없다. 그 시도의 기록은 유효하지 않다(유효 조건 6).
- 그 시도가 AC-1·AC-2를 맡은 가장 나중 rev 시도라면, 집계는 AC마다 rev **증거 없음** → G1 실패. G5도 실패.
- 바로잡기: 자격 있는 세션에 새 rev `review` 시도를 배정한다. 그러면 그 시도가 가장 나중 시도가 된다.

## 02d. 기준 브랜치 경쟁

02a의 관문을 통과하고 병합 명령을 낸 사이에 다른 PR이 `main`에 먼저 들어가 B3=bbbb003가 됐다.

- `--match-head-commit <H2>`는 head만 본다. 병합은 성공하고 `MERGED`로 확인된다.
- squash 커밋의 부모가 B3이다(B2가 아님). 관문 기록에 "기준 브랜치 경쟁(B2 검증, B3 위에 병합)"을 적고 사용자에게 알린다.

## 02e. "병합됐어"인데 PR이 열려 있음

사용자가 "병합됐어"라고 했지만 `gh pr view 57 --json state`가 `OPEN`이다.

- 병합되지 않았다. 사용자에게 "PR #57은 아직 열려 있다"고 알리고 아무것도 정리하지 않는다. `state.md`는 그대로.

## 02f. 병합 방법이 rebase

프로젝트 설정의 병합 방법이 `rebase`이고 PR에 커밋이 2개라고 하자.

- 마지막 커밋의 부모는 이 PR의 첫 커밋이라 `B`와 비교할 수 없다. 경쟁 확인을 "확인 불가(rebase 병합)"로 기록한다.
- 관문 판정(G1~G5)과 `--match-head-commit`, `MERGED` 확인은 같다.

## 이 예시에서 쓴 계약

evidence.md(역할 자격, 최신성, 집계, manifest), merge-gate.md(진입점 "병합해"·rebase 뒤, 병합 명령과 확인, 사람이 직접 병합), archive.md(시도 표).
