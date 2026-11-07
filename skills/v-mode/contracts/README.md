# vstack 계약

vstack 관리자와 작업자가 지키는 계약이다. 관리자는 작업 명세에 필요한 계약 파일의 절대 경로를 넣는다. 작업자는 넘겨받은 파일만 읽는다.

| 파일 | 누가 읽나 | 내용 |
| --- | --- | --- |
| [priority.md](priority.md) | 관리자, 작업자 | 지시가 충돌할 때의 순위, 불변 규칙, 알려진 충돌과 답 |
| [worker-contract.md](worker-contract.md) | 작업자(모든 실행기) | 역할별 권한, 질문·막힘·완료 보고, 증거 쓰기 |
| [evidence.md](evidence.md) | 관리자, 작업자 | 증거 필드, 유효·통과의 정의, 수용 기준 집계, 최신성 |
| [merge-gate.md](merge-gate.md) | 관리자 | 병합 관문의 판정식과 진입점 |
| [archive.md](archive.md) | 관리자 | 증거 보관 절차, 중단 복구, 정리 조건 |
| [intake.md](intake.md) | 관리자 | 배정 전 입력 검사, 시범 부트스트랩 |
| [state-and-rollback.md](state-and-rollback.md) | 관리자 | 작업 파일 위치와 형식, 소유권, 되돌리기 |
| [reference-policy.md](reference-policy.md) | 작업자 | 원문 안의 출처 참조 가운데 실행하지 않는 것(스크립트가 만든다) |

레시피 형식은 [../recipes/FORMAT.md](../recipes/FORMAT.md)에 있다. 계약이 끝까지 판정되는지는 저장소의 `docs/contract-examples/`로 확인한다.

**버전**: 이 계약 묶음은 `vstack-contract@1`이다. `state.md`와 증거 manifest에 이 값을 적는다. 계약을 바꾸면 숫자를 올린다.

**보장 범위**: 관문은 vstack 관리자가 실행하는 병합에만 보장된다. 첫 버전의 검증 대상은 Orca 실행 환경이고, 아직 실행 시범 전이다. herdr는 검증 대상이 아니다.
