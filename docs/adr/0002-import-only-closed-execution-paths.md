---
status: accepted
---

# 다른 플러그인에서는 실행 경로가 닫힌 것만 가져오고, 원칙은 원문 그대로 둔다

pstack과 mattpocock-skills에서 스킬을 가져올 때, 작업자가 실제로 따라가는 경로(레시피가 가리키는 스킬, 그 스킬이 실행하라고 하는 것)가 vstack 안에서 끝나는 것만 가져온다. 경로 하나하나를 포함, 대체, 삭제 가운데 하나로 정하고, 정하지 못한 것이 남으면 가져오지 않는다. 일괄 복사는 vstack에 없는 스킬을 부르는 문장을 그대로 들여온다.

pstack 원칙 24개는 영어 원문 그대로 둔다(`verbatim`). 원문 안의 다른 스킬 언급은 "출처 참조"로 보고 실행하지 않는다(`skills/v-mode/contracts/reference-policy.md`). 번역하거나 고치면 pstack 버전을 올릴 때 비교할 기준이 없어진다.

가져오는 방식(`verbatim`, `adapted`, `extracted`, `own`, `moved`)과 고친 내용은 `upstream.json`과 `UPSTREAM.md`에 적는다. pstack에서 무엇을 가져오기 전에는 mattpocock-skills에 같은 역할이 있는지 원문을 읽어 비교한다. 같은 역할의 스킬이 두 벌 생기면 무엇을 써야 할지 헷갈린다.
