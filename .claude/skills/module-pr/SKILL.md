---
name: module-pr
description: 이 저장소에 모듈 단위 PR 을 연다. 브랜치 이름, 시험, 다른 모델 검수, PR 양식 채우기, 로컬 pr-form 검사, Draft 풀기까지 밟는다. "PR 올려줘", "PR 만들어", "병합 준비", "pr-form 실패", "PR 본문 써줘" 같은 말에 쓴다.
---

# module-pr

규칙의 정본은 `.claude/rules/repo-rules/PR.md` 와 `.claude/rules/dev-rules/시험과 검수.md` 다. 다르면 규칙을 따른다.

## 순서

1. 바뀐 파일이 한 모듈인지 본다. `git diff --stat main...HEAD`. 둘 이상이면 사용자에게 나누자고 한다.
2. 시험을 돌리고 명령과 결과를 모은다. 화면이 바뀌었으면 캡처.
3. 검수를 맡긴다. 검수 모델은 작성 모델과 달라야 한다(기본 Codex). 지적을 고치고 횟수를 센다.
   검수 모델을 쓸 수 없으면 Draft 로 두고 본문 검수 칸에 "대기 · 까닭 · 다시 할 때" 를 쓴다. 병합하자고 하지 않는다.
4. `.github/pull_request_template.md` 를 복사해 `pr-body.md` 로 채운다(`.gitignore` 가 막아 커밋되지 않는다).
   - 요청·승인: PR 을 여는 GitHub 계정(`gh api user -q .login`)
   - 작성 모델: 정확한 ID(예: `claude-opus-5-5`). 도구: 예 `Claude Code 2.1.x`
   - 모듈은 하나만, 범위는 여러 개
   - 마지막 확인 칸은 사실일 때만 체크
5. 로컬 검사: `python .github/scripts/check_pr_form.py --file pr-body.md --author <계정>`. 통과할 때까지 고친다.
   이 PR 이 `.github/pull_request_template.md` 나 `check_pr_form.py` 를 바꾸면 4·5번 모두 main 의 양식과 검사기로 한다(`PR.md` 6번). `pr-form` 이 main 의 것을 쓰기 때문이다.
6. Draft 가 있으면 `gh pr edit <번호> --body-file pr-body.md` 다음 `gh pr ready <번호>`. 없으면
   `gh pr create --base main --head <브랜치> --title "<모듈>: <요약>" --body-file pr-body.md`.
7. `gh pr checks <번호>` 로 `pr-form` 결과를 본다.
8. 병합은 사람이 한다. Claude 는 병합하지 않는다.

`진행.md` 의 끝 줄은 `work-share` 의 "끝" 이 이 스킬보다 먼저 쓰고 push 한다. 이 스킬은 끝 줄을 쓰지 않는다. 아직 없으면 4번 전에 `work-share` "끝" 1번을 먼저 한다.

## 이력

- 2026-11-18 만듦. 옛 루트 `CLAUDE.md` 의 "PR 규칙" 절을 규칙 파일과 이 스킬로 나눔.
- 2026-11-21 고침(PR #2 Codex 검수 1·2회차). `work-share` 와 서로 부르던 끝 줄 단계를 하나로. 양식·검사기를 바꾸는 PR 은 main 의 것으로 검사.
