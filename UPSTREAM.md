# 출처

vstack은 세 곳에서 파일을 가져온다. 무엇을 어떻게 가져오는지의 정본은 [`upstream.json`](upstream.json)이다. 이 문서는 사람이 읽는 설명과 고친 내용의 기록이다.

## 출처 목록

| 출처 | 버전 | 커밋 | 라이선스 |
| --- | --- | --- | --- |
| [pstack](https://github.com/cursor/plugins/tree/main/pstack) | 0.15.36 | `6b0300214a09fd6029cfb7077043125758cd1fd2` | MIT, Copyright (c) 2026 Lauren Tan. [`licenses/pstack-LICENSE`](licenses/pstack-LICENSE) |
| mattpocock-skills(claude-plugins-official) | 1.3.1 | `49dd158d1076134a641b33efb035946536778336` | MIT, Copyright (c) 2026 Matt Pocock. [`licenses/mattpocock-skills-LICENSE`](licenses/mattpocock-skills-LICENSE) |
| [agent-orchestra](https://github.com/vananaHope/agent-orchestra) | 0.20.0 | `c62be33381a546fb7127088795a83378cfe35371` | MIT, Copyright (c) 2026 vananaHope. [`licenses/agent-orchestra-LICENSE`](licenses/agent-orchestra-LICENSE) |

- pstack 커밋은 가져올 때 받은 `cursor/plugins` 저장소의 HEAD다.
- mattpocock-skills와 agent-orchestra 커밋은 설치 기록(`installed_plugins.json`의 `gitCommitSha`)에서 읽었다. 설치 캐시 내용이 그 커밋과 같은지는 해시로 검증하지 않았다.

## 가져오는 방식

| 방식 | 뜻 |
| --- | --- |
| `verbatim` | 원문 그대로. 고치지 않는다. 안의 다른 스킬·원칙 언급과 링크는 가리키는 곳이 vstack 안이든 밖이든 출처 참조이며, 작업자는 따라가지 않는다([reference-policy.md](skills/v-mode/contracts/reference-policy.md)) |
| `adapted` | 복사한 뒤 고친다. 고친 내용은 아래 "고친 내용"에 적는다. 실행 경로라서 검사 대상이다: 경로는 표준 형태로 바꾸고(링크 또는 `<vstack>/` 경로, [FORMAT.md](skills/v-mode/recipes/FORMAT.md) "실행 경로 표기"), 남는 스킬 이름은 vstack 스킬이어야 하며, 특정 런타임의 스킬 도구 문장은 없앤다. 원본이 가리키던 파일은 가져오거나 `dropped`에 이유와 함께 적는다 |
| `extracted` | 원문의 일부만 떼어 새 파일로 만든다. 원본이 가리키던 파일 가운데 가져오지 않는 것은 `dropped`에 적는다 |
| `moved` | vstack이 이어받는다. 원본 저장소는 아카이브한다 |

## 단계별 가져올 것

| 단계 | 출처 | 원본 | vstack | 방식 |
| --- | --- | --- | --- | --- |
| 2 | pstack | `skills/principle-*`(24개) | `skills/principle-*` | verbatim |
| 2 | pstack | `skills/create-verification-skill` | 같음 | adapted |
| 2 | mattpocock-skills | `skills/engineering/diagnosing-bugs` | `skills/diagnosing-bugs` | adapted(`agents/openai.yaml` 제외) |
| 2 | mattpocock-skills | `skills/engineering/tdd` | `skills/tdd` | adapted(`agents/openai.yaml` 제외) |
| 2 | mattpocock-skills | `skills/engineering/codebase-design/SKILL.md`의 용어 부분 | `skills/tdd/references/codebase-vocabulary.md` | extracted(`DEEPENING.md`, `DESIGN-IT-TWICE.md`는 dropped) |
| 3 | agent-orchestra | `skills/orchestrate-issues`, `skills/check-limits`, `skills/configure` | 같음 | moved |

## 고친 내용

`adapted`·`extracted`·`moved` 파일을 고칠 때마다 여기에 적는다. 형식은 `파일 — 바꾼 것 — 이유`.

(아직 없음. 2단계부터 채운다.)

## 출처 참조

verbatim 원문 안에서 vstack에 없는 스킬을 가리키는 곳은 [`skills/v-mode/contracts/reference-policy.md`](skills/v-mode/contracts/reference-policy.md)에 있다. 이 파일은 스크립트가 만든다.

## 갱신 절차

1. 출처의 새 버전을 받는다(pstack은 `cursor/plugins` 저장소, 나머지는 플러그인 캐시나 원격 저장소).
2. 받은 체크아웃이 깨끗한지(`git status --short`가 빈 출력) 확인한다.
3. `upstream.json`의 각 항목을 이전 커밋과 비교한다. 경로는 출처의 `path`와 항목의 `from`을 이은 것이다. 예: pstack은 `git diff <이전 커밋> <새 커밋> -- pstack/skills/principle-prove-it-works`.
4. `verbatim`은 원문을 그대로 덮는다. `adapted`·`extracted`는 바뀐 부분을 보고 "고친 내용"을 다시 적용한다.
5. `upstream.json`과 이 문서의 버전·커밋을 고친다.
6. 출처 참조를 다시 만들고 검사한다. `--source` 경로는 각 출처의 저장소 루트다(pstack은 `cursor/plugins` 체크아웃, mattpocock-skills는 플러그인 캐시의 버전 폴더).

   ```
   node scripts/collect-references.mjs --source pstack=<cursor/plugins>
   node scripts/check-links.mjs --stage <현재 단계> --source pstack=<cursor/plugins> --source mattpocock-skills=<mattpocock-skills>
   ```

   `check-links`는 `--source`를 받으면 `adapted`·`extracted` 항목의 원본이 가리키던 파일이 모두 들어왔는지(`NOT CARRIED`)도 본다.

7. vstack 버전(`.claude-plugin/plugin.json`)을 올린다.
