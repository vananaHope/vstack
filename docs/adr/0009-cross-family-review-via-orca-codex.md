---
status: accepted
---

# 다른 계열의 검토는 Orca로 띄운 Codex 작업자가 하고, 서브에이전트는 읽기 전용 조사에만 쓴다

맡기기에서 구현자는 Claude(Opus)이고, 검토자는 같은 worktree에 Orca로 띄운 Codex 작업자다. 관리자가 검토 보고서를 직접 읽고 지적마다 고칠지 정한다.

`codex exec -s read-only`로 부르는 길도 있었다. Orca 작업자로 띄우면 기다리는 동안 관리자가 턴을 끝낼 수 있고, 같은 검토자에게 "보내기"로 재검토를 맡기면 앞 맥락이 남는다([pilot-delegate.md](../pilot-delegate.md)에서 재검토 한 번을 그렇게 돌렸다). 지휘의 Codex 작업자도 이미 Orca로 띄운다.

Claude Code의 서브에이전트는 Claude 모델만 쓴다. 그래서 서브에이전트에게 코드 검토를 맡기지 않는다. 같은 계열의 검토는 교차 검토가 아니다. 서브에이전트는 읽기 전용 조사에만 쓰고(Sonnet), 코드를 쓰지 않는다. 같은 worktree를 나눠 쓰기 때문이다. pstack은 서브에이전트가 코드를 쓰고 역할마다 다른 계열 모델을 고른다(`poteto-mode/SKILL.md` 94~98줄, `UPSTREAM.md`의 `subagents.md` 절). vstack은 그 가운데 부르는 쪽의 책임과 요청문 쓰는 법만 가져왔다.
