# OpenCode Go

OpenCode Go는 빠르고 범위가 분명한 일을 맡는다. 어느 일에 쓰는지는 [tiers.md](tiers.md)의 등급별 목록이 정하고, 이 파일은 OpenCode에만 붙는 조건과 방법을 적는다. 결과는 다른 계열이 검증한다(다른 계열이 한도 때문에 없을 때의 예외는 [tiers.md](tiers.md) "검토자 고르기" 2). 누가 검증할지는 등급의 검토 목록이 정한다([tiers.md](tiers.md) "검토자 고르기").

## 맡기지 않는 일

다음 중 하나라도 해당하면 등급 목록에 있어도 OpenCode를 건너뛴다.

- UI 작업이다(프로젝트 설정의 "UI 작업").
- 프로젝트 설정의 "간단한 구현에서 뺄 영역"을 건드린다.
- 실창 검사가 필요하다.
- 설계를 새로 정해야 한다(새 도메인 개념, 공용 인터페이스, 여러 방안 중 고르기).
- 무엇을 어디에 할지 명세에 구체적으로 적을 수 없다.

명세에 경고·금지 문구가 많다는 것만으로는 설계가 필요한 일로 보지 않는다.

**크기 상한**: `standard`는 프로젝트 설정 "등급별 배치"의 크기 상한까지만 맡긴다(없으면 파일 4개 안, 변경 200줄 안팎. 테스트 포함). 이슈 본문과 관련 파일로 미리 가늠한다.

## 모델과 강도

### 모델 확인(OpenCode를 쓸 때마다)

OpenCode는 정한 모델을 쓸 수 없으면 오류 없이 기본 무료 모델로 넘어간다. 첫 시범(2026-11-08)에서 계정 로그인이 없어(`opencode auth list` → `No authenticated integrations`) `opencode-go/` 모델을 쓸 수 없었다. 그래서 명세 새 눈 점검이 `opencode/big-pickle`로 돌았고, 턴마다 30~160초가 걸려 660초 제한에 끊겼다(측정: OpenCode 로그). 같은 질문을 DeepSeek 4.1 Flash(무료판 `opencode/deepseek-v4.1-flash-free`로 잼)로 돌리면 턴마다 2~20초였다(측정). 넘어가는 방식(측정, OpenCode 2.2.5):

- `-m opencode-go/deepseek-v4.1-flash`로 주면 로그인이 없을 때 `Error: Model unavailable`로 멈춘다.
- `-m` 없이 전역 설정에만 그 모델을 적으면, 로그인이 없을 때 **오류 없이** `big-pickle`로 돈다.

1. **쓸 모델**: 등급 표기의 모델(`opencode:<provider/model>`. 명세 새 눈 점검이면 프로젝트 설정 "명세 점검" 절의 표기, [spec-check.md](spec-check.md)), 없으면 `~/.config/opencode/opencode.json`의 `model`. 둘 다 없으면 OpenCode를 쓰지 않는다. 기본 모델에 맡기지 않는다.
2. **쓸 수 있는지**: `opencode models`에 그 이름이 있는지 본다. 없으면 OpenCode를 건너뛰고(한도가 `ok`가 아닌 것과 같다) 사용자에게 알린다. `opencode-go/` 모델은 OpenCode Go 로그인(`opencode auth login`)이 있어야 목록에 나온다. 로그인은 사용자가 한다.
3. **실제로 쓰였는지**: `opencode run`이면 출력의 `> <에이전트> · <모델>` 줄**과** 종료 코드 0, 그리고 그 뒤에 답이 있는지를 함께 본다. 그 줄은 모델 호출 전에 찍혀서 호출이 실패해도 나온다(측정: 키가 모델을 부를 수 없을 때 그 줄 다음에 `Error: This API key can't call models`, 종료 코드 1). 대화형 작업자면 `~/.local/share/opencode/opencode.db`에서 그 세션의 `session_message` 기록에 든 `"model"`(`providerID`와 `id`)을 본다. `session_v2.model`은 `-m`으로 줬을 때만 채워지고, 전역 설정으로 돌면 비어 있다(측정). 그래서 빈 값만으로 기본 모델이라고 판단하지 않는다. 1의 모델이 아니면 그 결과를 쓰지 않고 사용자에게 알린다.

정한 모델을 쓸 수 없을 때 다른 모델(무료판 `-free` 포함)로 바꿔 쓰지 않는다. 바꾸는 것은 사용자가 정한다. 무료판은 데이터 처리 조건이 유료 요금제와 다를 수 있다.

### 모델과 강도 적기

OpenCode 대화형 화면은 모델 옵션을 받지 않는다(Orca `worker-start`도 OpenCode에는 `--model`을 받지 않는다). 대신 OpenCode가 worktree 루트의 `opencode.json`을 읽으므로, 띄우기 전에 거기에 기본 에이전트(`build`)의 모델(위 "모델 확인" 1)과, 정했으면 강도(`variant`)를 적는다. 모델은 정하지 않았어도 적는다.

1. worktree가 아직 없으면 먼저 만든다(실행 환경 문서의 "worktree 만들기"). 저장소에 이미 커밋된 `opencode.json`이 있으면 덮어쓰지 않는다. 그 worktree에서 `opencode debug agents`를 돌려 `build`의 `model`이 "모델 확인" 1의 모델과 같으면(강도를 정했으면 `variant`도) 5로 간다. 다르면 OpenCode를 띄우지 않고 등급 목록의 다음 실행기로 넘긴 뒤 사용자에게 알린다.
2. worktree 루트에 쓴다. `model`은 `opencode models`가 보여 주는 `provider/model` 이름이다. 예(OpenCode Go 로그인이 있을 때):

   ```json
   { "agent": { "build": { "model": "opencode-go/deepseek-v4.1-flash", "variant": "high" } } }
   ```
3. 이 파일이 커밋되지 않게 메인 저장소의 `.git/info/exclude`에 `/opencode.json`을 더한다(worktree가 함께 쓰는 파일이라 한 번이면 된다).
4. worktree에서 `opencode debug agents`를 돌려 `build`의 `model`에 정한 모델과 `variant`가 보이는지 확인한다.
5. 실행 환경 문서의 "띄우기"대로 그 worktree에 띄운다. 작업자가 처음 응답하면 "모델 확인" 3을 한다.

같은 worktree에서 다음 OpenCode 작업자의 강도가 다르면 파일을 고치고 4번을 다시 한다.

`opencode run`(아래 빠른 답변, 2차 의견, [spec-check.md](spec-check.md))에서는 **언제나** `-m provider/model`(강도를 정했으면 `#variant`)로 준다. 빼면 전역 설정이 없거나 그 모델을 쓸 수 없을 때 기본 모델로 돈다.

**`opencode run` 공통 주의**(OpenCode 2.2.5에서 확인)
- 표준 입력을 `< /dev/null`로 닫는다. 표준 입력이 터미널이 아니고 열려 있으면(셸 도구가 그렇게 넘기는 경우가 있다) 입력이 끝나기를 기다리며 세션도 만들지 않고 멈춘다.
- 시간 제한으로 끊어도 세션은 취소되지 않는다. 다음에 서비스(`opencode serve --service`)가 뜰 때 끊긴 세션을 이어서 끝까지 돌려 사용량을 쓴다. 그래서 시간 제한은 넉넉히(10분 이상) 둔다.
- 전역 기본 강도는 `~/.config/opencode/opencode.json`에서 에이전트마다 `model`과 `variant`를 **함께** 적어 준다(`{"agent": {"plan": {"model": "opencode-go/deepseek-v4.1-flash", "variant": "high"}}}`). `model` 없이 `variant`만 적으면 "unsupported legacy model variant"로 버려지고, 최상위 `model`의 `#variant`나 객체의 `variant`는 실행에 적용되지 않았다. `plan`이 띄우는 `explore`·`general` 하위 에이전트도 각자 적는다. 적용 여부는 `opencode debug agents`의 `model.variant`와 `opencode.db` `session_message`의 `"variant"`로 확인한다.

## 검증

- 검토자는 등급의 검토 목록에서 고른다([tiers.md](tiers.md) "검토자 고르기"). vstack에서는 `관리자`를 검토자로 고르지 않는다([tiers.md](tiers.md) "검토자 고르기"). 관리자 확인은 사소 수정의 지적 해결 기록으로만 쓴다([tiers.md](tiers.md) "관리자 확인").
- 지적 수정은 [fixes.md](fixes.md)의 재검토 규칙을 따른다.

## rebase

SKILL.md 6단계 2의 rebase는 `light`다.

- 명세에 rebase 전 `HEAD`를 적어 둔다.
- import, 목록 순서, 붙어 있는 줄처럼 양쪽 의도를 모두 살리기 쉬운 충돌은 OpenCode가 해결한다.
- 같은 함수의 동작이 양쪽에서 바뀐 충돌이면 `git rebase --abort`로 되돌리고 보고하게 한다. 관리자는 그 rebase를 원래 구현자에게 맡긴다.
- 검증: 관리자가 `git range-diff <rebase 전 HEAD>...HEAD`로 충돌 해결분 말고는 변경이 같은지 본다. 그다음 `<vstack>/skills/orchestrate-issues/vstack.md` "대상이 바뀌면"대로 재검증한다(rebase 작업자가 필수 수용 기준 전부, 그다음 rev `review` 시도). range-diff가 같아도 재검증을 건너뛰지 않는다.

## 빠른 답변·빠른 판단

관리자가 결론을 내기 전에 넓게 훑어야 하는 짧은 질문이다. 예를 들어 어느 파일이 무엇을 맡는지, 이슈가 어느 영역을 건드리는지, 지적의 심각도 첫 의견 같은 것이다.

- 메인 저장소에서 읽기 전용 `plan` 에이전트로 묻는다: `opencode run --agent plan -m <모델> "<질문>" < /dev/null`. 20초 안팎이 걸린다(위 "`opencode run` 공통 주의"). 답을 쓰기 전에 "모델 확인" 3을 한다.
- 답은 관리자가 근거(파일·줄)를 직접 확인한 뒤에만 쓴다. 사용자만 정할 결정은 사용자에게 묻는다.

## 2차 의견

주 검토와 따로, 같은 diff를 `plan` 에이전트에 보여 2차 의견을 받는다. 검토 보고서의 지적과 함께 판정한다.

- **언제**: 같은 계열끼리 검토할 때는 항상([tiers.md](tiers.md) "검토자 고르기" 2). 그 밖에는 프로젝트 설정의 2차 의견 값(`standard 이상` / `모든 검토`)을 따른다. 관리자 확인과 rebase 작업 자체에는 받지 않는다. rebase 뒤에 맡기는 rev `review` 시도가 같은 계열이면 그 검토에는 받는다(계약의 같은 계열 조건).
- **묻는 내용**: diff 범위(`main..HEAD`), 이슈의 완료 기준, `common-findings.md`의 절대 경로를 주고, 유형별로 해당하는 결함이 있는지 파일·줄 근거와 함께 답하게 한다.
- **쓰는 법**: 2차 의견의 지적은 관리자가 근거를 직접 확인한 것만 판정에 넣는다. 주 검토 보고서와 겹치지 않는 지적이 있으면 보고서 옆에 `second-opinion-<k>.md`로 남긴다.
