# PR

main 에는 PR 로만 들어간다. 규칙(`.github/rulesets/main.json`)이 직접 push 를 막고, `pr-form` 검사가 통과해야 병합된다.
목적은 코드마다 누가 시켰고, 어떤 모델이 짰고, 무엇으로 검수했는지 남겨 책임과 신뢰도를 확인하고 다시 보기 쉽게 하는 것이다.
Claude 는 스킬 `module-pr` 로 이 순서를 밟는다.

## 순서

1. main 에서 브랜치를 딴다(`모듈과 브랜치.md`). main 에서 직접 커밋하지 않는다.
2. 처음 push 할 때 Draft PR 을 연다. 팀원이 "누가 무엇을 하는지" 를 여기서 본다(`work-sharing/작업 공유 절차.md`).
3. 짠다. 커밋 메시지 끝에 공동 작성자 줄을 붙인다. 예: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
4. 시험을 돌린다. 명령과 결과를 적어 둔다.
5. 작성 모델과 다른 모델로 검수한다(`dev-rules/시험과 검수.md`). 재설계 판정이면 병합하지 않는다.
6. `.github/pull_request_template.md` 를 그대로 채워 `pr-body.md` 로 저장하고 로컬에서 먼저 검사한다.
   `python .github/scripts/check_pr_form.py --file pr-body.md --author <PR 을 여는 GitHub 계정>`
7. 본문을 넣고 Draft 를 푼다. `gh pr edit <번호> --body-file pr-body.md` 다음 `gh pr ready <번호>`.
   Draft 없이 바로 열 때는 `gh pr create --base main --head <브랜치> --title "<모듈>: <요약>" --body-file pr-body.md`.
8. `pr-form` 이 실패하면 본문을 고친다. 본문을 고치면 검사가 다시 돈다.
9. 병합은 squash 만 된다. PR 하나가 main 의 커밋 하나가 된다.

## 본문에서 틀리기 쉬운 곳

- 사용자의 `요청·승인` 은 PR 을 여는 GitHub 계정이다. 검사가 PR 작성자와 대조한다. 다른 사람이 시켰으면 그 사람 계정으로 연다.
- 작성 모델은 정확한 모델 ID 로 쓴다(예: `claude-opus-5-5`). 검수 모델이 같으면 검사에서 떨어진다.
- 모듈은 정확히 하나만 체크한다. 범위는 여러 개여도 된다.
- 칸을 "-", "없음" 같은 말로만 채우면 떨어진다. 남은 지적, 미완처럼 정말 없을 때만 "없음" 을 쓴다.
- `pr-form` 은 main 의 양식과 검사기를 쓴다. PR 안에서 양식을 바꿔도 그 PR 의 검사는 옛 양식을 따른다.
