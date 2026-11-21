---
name: work-share
description: 이 저장소에서 작업을 시작하거나 끝낼 때, 세션을 닫거나 사용량 한도·대화 압축이 가까울 때 팀원과 작업을 공유한다. 시작할 때 열린 PR·memory·공유 대기를 읽고, Draft PR 로 하는 일을 알리고, 끝날 때 memory 를 갱신한다. push 를 못 하는 등 공유할 수 없으면 가능한 만큼 기록한다. "작업 시작", "이어서 하자", "오늘 여기까지", "인수인계", "누가 뭐 하고 있어", "공유해줘" 같은 말에 쓴다.
---

# work-share

규칙의 정본은 `.claude/rules/work-sharing/` 다. 이 스킬은 그 절차를 빠짐없이 밟게 하는 점검표다. 규칙과 다르면 규칙을 따른다.

## 시작

```bash
git switch main && git pull --ff-only && git fetch --prune
gh pr list --state open --search "<모듈>: in:title"           # 같은 모듈의 열린 PR
git branch -r --list "origin/<모듈>/*"                        # PR 없이 올라온 브랜치
gh issue list --state open --search "[작업 공유] in:title"    # 저장소 밖에서 남긴 공유
ls ".claude/memory/_공유 대기/"                                # 공유 못 한 기록
```

1. 맡은 모듈을 정한다(`.claude/rules/repo-rules/모듈과 브랜치.md`). 둘에 걸치면 사용자에게 나눌지 묻는다.
2. `.claude/memory/<모듈>/진행.md` 맨 위 다섯 줄, `결정.md`, 관련 `_공유 대기/` 파일, `docs/요구사항/` 의 `정적/과제 틀.md` 와 `가변/기능/<모듈>.md`(일에 따라 `가변/비기능.md`, `검증.md`, `용어.md`, `화면.md`)를 읽고 사용자에게 두세 줄로 알린다. `정적/` 은 읽기만 한다.
3. 같은 모듈에 남이 하는 일(PR, 브랜치, 이슈)이 있으면 시작하지 않는다. 사용자에게 알리고, 그 PR 이나 이슈에 댓글로 범위 나누기나 이어 받기를 정한다. PR 도 이슈도 없는 브랜치면 조율 이슈를 새로 연다. 답이 없을 때 누가 정하는지는 `작업 공유 절차.md` "시작할 때" 3번.
4. 새 작업이면 브랜치를 따고 `진행.md` 맨 위에 시작 줄을 쓴다(`memory 쓰는 법.md` 의 꼴). 커밋, push, Draft PR.

```bash
git switch -c <모듈>/<요약>
git push -u origin HEAD
gh pr create --draft --base main --title "<모듈>: <요약>" --body "작업 중: <무엇을>"
```

5. 이어 받기면 새 브랜치와 새 PR 을 만들지 않는다. 그 브랜치를 받고 인수인계 줄을 써서 push 한다. 그 브랜치에 PR 이 없을 때만 Draft PR 을 연다.

```bash
git switch <그 브랜치> && git pull
# 진행.md 맨 위에 인수인계 줄을 쓴 뒤
git commit -am "<모듈>: 인수인계" && git push
```

## 하는 동안

- 결정이 생기면 그 자리에서 `결정.md` 에 쓴다.
- 한 덩어리가 끝날 때마다 커밋하고 push 한다. 막힘·질문은 `gh pr comment <번호> --body "..."`.

## 멈출 때 (세션 끝, 한도 임박, 압축 예고)

1. 하던 도구 호출만 끝내고 새 일을 시작하지 않는다.
2. `진행.md` 맨 위에 지금 상태 한 줄(무엇까지 했나, 다음에 할 첫 일).
3. 커밋하고 push. 실패하면 아래 "공유 못 할 때".

## 다시 시작 (세션이 예고 없이 끊긴 뒤)

```bash
git status
git log --oneline @{u}..HEAD                 # push 안 된 커밋 (원격 브랜치가 있을 때)
git log --oneline origin/main..HEAD          # 한 번도 push 안 한 브랜치일 때
gh pr list --author @me --state open
```

`진행.md` 맨 위 줄과 대조해 빠진 것을 찾는다. 먼저 `진행.md` 에 "이어 받음" 줄을 쓰고, 남은 변경과 함께 커밋·push 한다. 처음 push 하는 브랜치면 Draft PR 도 연다. 내가 쓴 `_공유 대기/` 파일이 있으면 올린다.

## 끝

1. `진행.md` 에 끝 줄. 남은 일을 같이 쓴다. 커밋하고 push 한다. 끝 줄은 여기서만 쓴다.
2. 스킬 `module-pr` 로 시험·검수·본문을 마치고 Draft 를 푼다. `module-pr` 은 끝 줄을 다시 쓰지 않는다.

## 공유 못 할 때

`.claude/rules/work-sharing/공유 못 할 때.md` 의 표에서 할 수 있는 가장 위 칸을 쓴다.
push 를 못 하면 로컬에 커밋하고 `.claude/memory/_공유 대기/YYYY-MM-DD_<계정>_<모듈>_<요약>.md` 를 같은 양식으로 쓴다.
사용자에게 "공유하지 못했고 어디에 적었는지" 를 꼭 말한다.

## 하지 않는 것

- main 에 직접 커밋하지 않는다.
- 남의 브랜치에 push 하지 않는다. 필요하면 PR 댓글로 묻는다.
- 비밀값을 memory·PR·이슈에 쓰지 않는다.

## 이력

- 2026-11-18 만듦. 레포 구조 개편(`.claude/` 의 rules·memory·skills)과 함께.
- 2026-11-21 고침(PR #2 Codex 검수 1·2회차). 새 작업과 이어 받기 분기, 시작 때 PR 없는 브랜치와 `[작업 공유]` 이슈도 보기, 같은 모듈 동시 작업이면 멈추고 정하기, 끊긴 뒤 다시 시작, 끝 줄은 한 번만.
- 2026-11-21 고침. 시작할 때 모듈 요구사항 파일도 읽기(`docs/요구사항/`).
