# 우선순위

## 적용 범위

사용자 지시와 런타임 권한 안에서 vstack 문서끼리 충돌할 때의 순위다. 사용자 지시나 런타임이 막는 일을 이 순위로 할 수 있게 되지는 않는다.

## 순위

위가 이긴다.

1. **불변 규칙**(아래 목록). 작업 명세가 덮어쓸 수 없다.
2. **작업 명세**. 명세가 정할 수 있는 항목은 아래 "명세가 정하는 항목"뿐이다.
3. **레시피에 적힌 예외**
4. **후보 원칙**. 적용 조건이 맞을 때만 쓴다.
5. **가져온 스킬 원문의 지시**

같은 순위끼리 충돌하면 작업자는 관리자에게 묻고, 답을 받기 전에는 그 부분을 진행하지 않는다. 관리자는 답을 명세에 반영한다.

## 불변 규칙

- 역할별 권한([worker-contract.md](worker-contract.md) "역할별 권한")
- 증거의 필드·유효·통과 정의와 판정 규칙([evidence.md](evidence.md))
- 완료 보고한 증거 폴더는 바꾸지 않는다([worker-contract.md](worker-contract.md) "증거 쓰기")
- 병합 관문([merge-gate.md](merge-gate.md))
- 보관 완료의 정의와 정리 조건([archive.md](archive.md))
- 출처 참조는 실행하지 않는다(아래 "출처 참조")
- 안전 멈춤: force-push, 배포, 사용자·운영 데이터 삭제는 멈추고 사용자에게 확인한다. 작업자가 만든 scratch와, 보관을 검증한 증거 원본을 지우는 것은 정상 절차이며 이 규칙에 들지 않는다.

## 명세가 정하는 항목

수용 기준(ID·버전·필수 여부), 검증 명령, 반복 재현 횟수, 대상 범위와 건드리지 말 영역, 전환 방식, 레시피와 그 버전, 후보 원칙 목록, 증거로 캡처할 것.

## 출처 참조

원문 그대로 가져온 파일(원칙 24개 등) 안에는 다른 스킬이나 원칙을 가리키는 문장과 링크가 있다. vstack에 없는 스킬(예: `principle-prove-it-works`의 `show-me-your-work`)도 있고, vstack 안의 다른 원칙도 있다. 이것은 모두 출처를 보존하려고 남긴 **출처 참조**다. 작업자는 원문이 "그 스킬을 실행하라"고 해도 실행하지 않고, 링크를 따라가 다른 원칙을 읽거나 적용하지도 않는다. 원칙은 명세와 레시피가 후보로 준 것만 읽고 적용한다. 목록은 [reference-policy.md](reference-policy.md)에 있다(`scripts/collect-references.mjs`가 만든다).

## 알려진 충돌과 답

| 충돌 | 근거 | 답 |
| --- | --- | --- |
| `tdd`는 seam마다 사용자 확인을 받는데, 작업자는 사용자를 막으면 안 된다 | mattpocock `tdd/SKILL.md:22~24`, pstack `principle-never-block-on-the-human` | seam은 정렬 단계에서 정해 티켓에 싣는다. 배정 전 입력 검사가 빈 seam을 잡는다([intake.md](intake.md)). 작업 중 seam이 틀렸다고 판단하면 관리자에게 묻고 `막힘`으로 기다린다. 답 전에는 성공 완료를 보내지 않는다 |
| `grilling`·`to-tickets`는 사용자 승인을 기다린다 | `grilling/SKILL.md:28~30`, `to-tickets/SKILL.md:42~56` | 정렬·명세 단계에서만 쓴다. 작업자 레시피에 넣지 않는다 |
| expand–contract를 허용하는데, pstack 리팩토링은 옛·새 경로 병존을 금지한다 | `to-tickets/SKILL.md:40`, pstack `playbooks/refactoring.md:11` | 티켓의 "전환 방식"을 따른다. 기본은 한 번에 전환. 영향 범위가 넓거나 외부 호출자가 있거나 green을 유지할 수 없으면 expand–contract |
| `diagnosing-bugs`는 반복 재현을 요구하는데, orchestra 명세는 요구할 때만 반복한다 | `diagnosing-bugs/SKILL.md:51`, orchestra `task-template.md:47` | 버그 레시피가 정한다. 간헐·동시성 버그면 반복 필수(횟수는 명세), 결정적 버그면 한 번 |
| pstack 플레이북은 PR 열기로 끝나는데, 작업자는 PR을 못 만든다 | orchestra `task-template.md:35` | 작업자의 끝은 검증·커밋·완료 보고. PR·병합은 관리자 |
| 검토자는 파일 수정·흔적 금지인데, 증거를 남겨야 한다 | orchestra `review-template.md:31` | 역할별 권한을 따른다. vstack 검토 양식에서 그 문장을 권한 표로 바꾼다 |
| 가져온 스킬이 "사용자에게 물어라"라고 한다 | `diagnosing-bugs/SKILL.md:55` 등 | 작업자는 관리자에게 묻는다 |
| 원칙 원문이 vstack에 없는 스킬을 실행하라고 한다 | 위 "출처 참조" | 실행하지 않는다 |
