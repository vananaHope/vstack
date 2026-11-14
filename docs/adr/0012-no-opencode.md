---
status: accepted
---

# OpenCode를 쓰지 않는다

agent-orchestra 때부터 OpenCode(OpenCode Go 구독, DeepSeek 계열 모델)를 지휘의 셋째 계열로 두었다. `light`·`standard` 구현 목록의 첫 작업자, 명세 새 눈 점검의 기본 점검자, 2차 의견, 관리자의 빠른 질문, rebase를 맡겼다. 2026-11-15(0.24.0)에 모두 뺐다. 계열은 Codex와 Claude 둘이다.

실제 프로젝트(my-video-manager)에서 OpenCode는 구현을 한 번도 맡지 않았다. 맡긴 이슈가 모두 UI라 Claude가 구현하고 Codex가 검토했다. 쓰인 곳은 명세 새 눈 점검뿐이었는데, #285에서는 두 번 종료 코드 0으로 끝나고도 답이 없어 Claude 서브에이전트로 다시 물었다. 그 한 점검에 30분 가까이 들었다. 답이 나와도 5분 안팎이 걸렸다(`spec-check.md`의 측정 234초). Codex는 짧은 질문에 6초였다(같은 문서의 측정). 도구 하나를 더 들이는 비용(로그인, 모델·`variant` 설정, `opencode run`의 입력·시간 제한 함정)에 비해 얻는 것이 없었다. 사용자 결정이다.

**Considered Options**: 프로젝트 설정에서만 빼고 vstack의 지원은 남기는 길도 있었다. 쓰는 프로젝트가 없는데 계열 규칙, 설정 창, 검사 스크립트에 셋째 계열을 계속 두면 문서와 판정만 복잡해진다. 잃은 것은 셋째 계열이다. 그래서 두 가지가 달라졌다. rebase는 원래 구현자의 계열이 한다(다른 계열이 rebase하면 다른 계열 검토자가 남지 않는다, `orchestrate-issues/vstack.md` "rebase"). 같은 계열 검토의 2차 의견은 같은 계열의 다른 모델이 준다(`orchestrate-issues/tiers.md` "2차 의견"). 무료 모델로 한도를 아끼던 몫은 Codex와 Claude 한도에서 나간다. 계약은 `vstack-contract@5`로 올렸다.
