# 멀티 세션 vs 서브에이전트 (2026-11 조사)

> omp 세션이 2026-11-10에 쓴 조사 메모다. 출처를 따로 검증하지 않았다. 설계 근거로는 방향만 쓴다([design.md](design.md) 12절).

## 정의

| 구분 | 멀티(병렬) 세션(사람이 조율) | 서브에이전트 |
|---|---|---|
| 실체 | 독립된 풀 에이전트 인스턴스 여러 개, 보통 세션마다 별도 git worktree/브랜치 | 한 세션 안에서 메인 에이전트가 띄우는 보조 에이전트 |
| 컨텍스트 | 세션끼리 서로 모름. 공유하는 건 사람(오케스트레이터)뿐 | 자체 컨텍스트 창. 메인 대화 이력은 기본적으로 받지 않고 위임된 작업만 받음 |
| 결과 전달 | 각자 브랜치/PR로 산출, 사람이 리뷰·머지 | 요약된 결과만 메인 에이전트에 반환 |
| 조율 주체 | 사람 | 메인 에이전트 |
| 주 용도 | 서로 다른 파일을 건드리는 독립 작업(기능, 버그, 마이그레이션) | 코드베이스 탐색, 리서치, 검증, 리뷰처럼 결과만 중요한 범위 한정 작업 |
| 늘어나는 것 | 동시에 진행 중인 작업 수 | 한 작업 안에서의 집중도(메인 컨텍스트 오염 방지) |

출처:
- Claude Academy, "Parallel sessions and subagents": 병렬 세션 = 별도 worktree의 풀 Claude Code 인스턴스, 서로 모름. 서브에이전트 = 세션 내 범위 한정 헬퍼, 자체 컨텍스트·도구 제한. https://academy.claude.com/courses/ai-native-sdlc-playbook/parallel-sessions-and-subagents
- VS Code, "Understand AI agents": 세션은 병렬 실행 가능하나 같은 폴더면 코드 격리는 안 됨. 서브에이전트는 컨텍스트 격리·병렬 실행·요약 결과 반환, 단 자체 모델 요청을 하므로 총 토큰이 줄지는 않음. https://code.visualstudio.com/docs/agents/concepts/agents

## 중간 형태: 에이전트 팀

Claude Code "agent teams"(실험 기능, 기본 비활성): 리드 세션 + 독립 Claude Code 인스턴스 팀원들이 공유 작업 목록과 메일박스로 직접 메시지를 주고받음. 서브에이전트보다 토큰 비용이 높고, 순차 작업·같은 파일 편집·의존성 많은 작업에는 단일 세션이나 서브에이전트가 낫다고 명시. https://code.claude.com/docs/en/agent-teams

## 트렌드

- 도구가 "여러 에이전트 동시 감독" 중심으로 재편: OpenAI Codex 앱(2026-02)은 프로젝트별 스레드에서 여러 에이전트를 병렬 실행하고 worktree로 격리하는 "command center"로 출시. https://openai.com/index/introducing-the-codex-app/
- Anthropic 2026 Agentic Coding Trends Report, Trend 2: 단일 에이전트에서 오케스트레이터 + 전문 에이전트 계층 구조로 이동할 것이라 예측(예측이지 측정치 아님). https://claude.com/resources/guides/2026-agentic-coding-trends-report/capability-trends-what-agents-can-do
- 채택 규모: JetBrains Developer Ecosystem Survey 2026(1.5만 명+) — 전문 개발자 90%가 주 1회 이상, 68%가 매일 코딩 에이전트 사용. Claude Code 사용률 39%(1월 18%), Codex 16%(1월 3%). 세션/서브에이전트 방식별 사용률은 조사되지 않음. https://blog.jetbrains.com/research/2026/08/ai-coding-agent-adoption-2026/

## 반론·한계

- Google Research(2026-01, 180개 구성 통제 실험): 병렬화 가능한 작업에서는 중앙 오케스트레이터형이 단일 에이전트 대비 +80.9%, 순차 계획 작업에서는 모든 멀티에이전트 변형이 39~70% 하락. 서로 대화하지 않는 독립 병렬 구조는 오류를 최대 17.2배 증폭, 오케스트레이터형은 4.4배. 도구가 많을수록(코딩 에이전트처럼 16개+) 조율 비용이 커짐. https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/
- Anthropic 멀티에이전트 리서치 시스템(2025-06): 리서치에서 멀티에이전트가 단일 대비 +90.2%, 대신 토큰은 채팅 대비 약 15배. "대부분의 코딩 작업은 리서치보다 진짜 병렬화 가능한 부분이 적다"고 명시. https://www.anthropic.com/engineering/multi-agent-research-system
- Cognition "Don't Build Multi-Agents"(2025-06): 서브에이전트들이 서로의 암묵적 결정을 모른 채 병렬로 코드를 쓰면 결과가 충돌. 컨텍스트 공유와 단일 스레드를 기본으로 권장. https://cognition.com/blog/dont-build-multi-agents
