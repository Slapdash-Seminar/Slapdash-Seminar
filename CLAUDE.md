# CLAUDE.md

대충하는발표회 모임 관리 앱 코드 저장소다. 이 파일은 안내만 한다. 규칙과 기록은 `.claude/` 에 있고, 그때그때 필요한 파일만 연다.

## 언제나

- 작업을 시작할 때와 끝낼 때 작업 공유 절차를 따른다. 스킬 `work-share`, 규칙 `.claude/rules/work-sharing/`.
- main 에는 PR 로만 들어간다. 모듈 하나 = 브랜치 하나 = PR 하나. 스킬 `module-pr`.
- 비밀값(키, 토큰, 비밀번호, `.env`)은 커밋하지 않는다. 이 저장소는 공개다.

## 상황별로 볼 곳

| 상황 | 볼 곳 |
|---|---|
| 처음 왔다, 무엇부터 | `.claude/rules/work-sharing/작업 공유 절차.md` |
| 지금 누가 무엇을 하나 | `gh pr list --state open` (작업 중은 Draft PR), `.claude/memory/_공유 대기/` |
| 기능의 결정·진행·인수인계 | `.claude/memory/<모듈>/` (모듈 폴더 이름은 브랜치 머리와 같다) |
| 폴더가 어디 있나, 새 폴더를 어디 두나 | `.claude/rules/repo-structure/폴더 구조.md` |
| 브랜치 이름, 모듈과 담당 | `.claude/rules/repo-rules/모듈과 브랜치.md` |
| PR 여는 순서, 본문 양식, `pr-form` 실패 | `.claude/rules/repo-rules/PR.md`, 스킬 `module-pr` |
| main 보호 규칙의 근거 | `.github/rulesets/README.md` |
| 기술 스택, 코드 쓰는 법 | `.claude/rules/dev-rules/` |
| 시험과 검수 | `.claude/rules/dev-rules/시험과 검수.md` |
| 작업을 공유할 수 없는 상황 | `.claude/rules/work-sharing/공유 못 할 때.md` |
| memory 를 어떻게 적나 | `.claude/rules/work-sharing/memory 쓰는 법.md` |
| 기획서·요구사항서·화면 설계 | 저장소 밖 운영 폴더(비공개). 개발에 필요한 결정은 해당 모듈 memory 에 옮겨 적는다 |
| 규칙을 새로 만들거나 고친다 | `.claude/rules/README.md` |
