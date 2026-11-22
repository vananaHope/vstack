# 출처 참조 정책

> 이 파일은 `scripts/collect-references.mjs`가 만든다. 손으로 고치지 않는다.

`upstream.json`에서 `mode: verbatim`으로 가져온 원문 안의 다른 스킬 언급 목록이다. 원문은 고치지 않는다.

verbatim 원문 안의 참조는 가리키는 곳이 vstack 안이든 밖이든 모두 **출처 참조**다. 작업자는 따라가지 않는다([priority.md](priority.md) "출처 참조").

## vstack에 없는 스킬을 가리키는 참조

원문이 "그 스킬을 실행하라"고 해도 실행하지 않는다. 같은 일이 필요하면 오른쪽 열을 따른다.

| 파일 | 줄 | 참조 | 형태 | vstack에서 대신 따르는 것 |
| --- | --- | --- | --- | --- |
| `skills/principle-type-system-discipline/SKILL.md` | 15 | `typescript-best-practices` | bold | 원칙 `type-system-discipline` 본문만 따른다 |

## vstack 안을 가리키는 참조

vstack에 있는(또는 들어올) 파일을 가리키지만, 이것도 출처 참조다. 작업자는 이 링크를 따라가 다른 원칙을 읽거나 적용하지 않는다. 명세·레시피가 후보로 준 원칙만 읽고 적용한다.

| 파일 | 줄 | 참조 | 형태 |
| --- | --- | --- | --- |
| `skills/principle-explain-the-number/SKILL.md` | 14 | `benchmark-checklist` | link |
