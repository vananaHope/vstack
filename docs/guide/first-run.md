# 처음 쓰기

설치하고, 프로젝트 설정을 만들고, 맡기기를 한 번 끝내는 순서다. 끝나면 vstack이 일을 어떻게 나누고 확인하는지 한 번 본 셈이다.

## 1. 갖출 것

- Claude Code와 `claude-plugins-official` 마켓플레이스(mattpocock-skills가 여기서 온다).
- [Orca](https://github.com/stablyai/orca). 맡기기와 지휘의 작업자를 Orca가 띄우므로, Claude Code를 Orca 안에서 연다([ADR 0004](../adr/0004-orca-only.md)).
- `claude`, `codex` 명령. 지휘를 하려면 `gh`도 로그인돼 있어야 한다.
- 다룰 저장소에 테스트나 스크립트 같은 검증 수단. 없으면 vstack이 그것부터 만들자고 한다.

## 2. 설치

```
/plugin marketplace add anthropics/claude-plugins-official   # 이미 있으면 건너뛴다
/plugin marketplace add vananaHope/vstack
/plugin install vstack@vstack                                # mattpocock-skills도 함께 설치된다
```

설치가 끝나도 vstack 명령이 보이지 않으면 [troubleshooting.md](troubleshooting.md) "설치"를 본다.

## 3. 프로젝트 설정 만들기

다룰 저장소에서 `/vstack:configure`를 실행한다. 저장소를 훑어 추천 값을 채운 설정 창이 차례로 뜨고, 고르기만 하면 된다. 저장하면 끝에 전제(Orca, `gh`·`claude`·`codex`, 한도, `.local/` 무시, mattpocock 설정, 검증 수단)를 점검해 항목마다 알려 준다. 빠진 것이 있으면 이때 갖춘다.

설정 위치와 절은 [settings.md](settings.md)에 있다. 설정 없이 맡기기를 해도 되지만, 지휘는 처음 실행할 때 이 설정부터 띄운다.

## 4. 맡기기 한 번

`/vstack:v-mode`로 시작해 작은 일을 하나 말한다. 동작이 바뀌지만 티켓으로 나눌 만큼 크지 않은 일이 좋다(예: "목록이 비었을 때 안내 문구를 보여 줘").

1. v-mode가 목표를 한 번 되짚고, 첫 답에 갈래 줄을 적는다. 여기서는 "맡기기, 계약 밖"이 나와야 한다.
2. 관리자(이 대화)가 맡기기 전 확인을 하고 수용 기준이 담긴 명세를 쓴다. 사람만 정할 수 있는 것(제품 동작, 취향)은 이때 묻는다.
3. Claude 구현자가 새 worktree에서 구현하고 커밋한다.
4. 관리자가 수용 기준을 다시 돌려 확인하고, Codex 검토자가 같은 worktree에서 읽기 전용으로 검토한다.
5. 고칠 지적이 있으면 구현자에게 되돌린다(최대 두 번).
6. 마지막 확인이 끝나면 관리자가 반영 방법을 묻는다. 고른 방법으로 반영하고 worktree를 정리한다.

관리자는 이 동안 제품 코드를 쓰지 않는다. 자세한 흐름은 [delegate.md](delegate.md)에 있다.

## 다음

- 갈래와 역할을 정리해 보려면 [concepts.md](concepts.md).
- 이슈 여러 개를 맡기려면 [orchestrate.md](orchestrate.md).
- 기능마다 작업 트리를 따로 두고 일하려면 [feature-branch.md](feature-branch.md).
