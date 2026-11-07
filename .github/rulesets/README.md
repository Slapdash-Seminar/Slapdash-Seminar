# 저장소 규칙 (ruleset)

`main.json` 은 기본 브랜치(main)에 거는 규칙이다. 모든 변경이 모듈 단위 PR 로 들어오고,
PR 마다 누가 시켰는지, 어떤 모델이 짰는지, 무엇으로 몇 번 검수했는지가 남게 한다.

## 출발점과 바꾼 곳

출발점은 개인 자료 `github rules/context-hall_ruleset.json` 이다(원본 `base_rules.json` 을 Context-Hall 에 맞춘 판).

| 출발점 | 바꾼 것 | 까닭 |
|---|---|---|
| 필수 상태 확인 `test`, `CodeQL` | `pr-form` 하나 | 저장소에 아직 코드가 없어 `test`·`CodeQL` 은 결과가 오지 않는다. 결과가 안 오면 PR 이 영영 병합되지 않는다. `pr-form` 은 `.github/workflows/pr-form.yml` 의 작업 이름이고, PR 양식을 검사한다 |
| `code_scanning` (CodeQL) | 뺌 | 앱 코드인 Flutter(Dart)는 CodeQL 이 분석하지 못한다. Go 서버 코드가 생기면 다시 넣는다 |
| `copilot_code_review` | 뺌 | 이 프로젝트의 검수는 작성 모델과 다른 모델(기본 Codex)이 하고, 그 기록은 PR 본문 검수 절에 남긴다 |
| 병합 방식 merge, squash, rebase | squash 만 | PR 하나가 main 의 커밋 하나가 된다. 모듈 단위 이력이 그대로 남는다. GitHub 는 squash 커밋에 공동 작성자 줄을 붙인다 |
| (없음) | `deletion` 추가 | main 브랜치를 지우지 못하게 한다 |

그대로 둔 것: PR 필수, 승인 수 0, 리뷰 스레드 해결 필수, 강제 push 금지(`non_fast_forward`), 우회 없음(`bypass_actors` 비움).

`pr-form` 은 `pull_request_target` 으로 돈다. 작업 파일과 검사 스크립트를 PR 쪽이 아니라 main 에서 가져오므로,
PR 이 검사기를 고쳐 스스로 통과시킬 수 없다. 대신 PR 쪽 코드를 받아 실행하는 단계를 이 작업에 넣으면 안 된다.

승인 수를 0 으로 둔 까닭: Claude 가 사용자 계정으로 PR 을 열면 그 사용자는 자기 PR 을 승인할 수 없다.
승인을 1 로 올리면 다른 팀원이 매번 승인해야 병합된다. 팀이 원하면 `required_approving_review_count` 를 1 로 바꾼다.

## 사용자를 어떻게 확인하나

PR 본문 사용자 절의 `요청·승인: @계정` 은 `pr-form` 이 PR 작성자 계정과 같은지 확인한다.
PR 작성자는 GitHub 가 기록한 값이라 본문에 무엇을 쓰든 바뀌지 않는다. 그래서 "누구 계정으로 열었나" 는 믿을 수 있다.

더 단단하게 하려면 커밋 서명을 켠다. 각자 SSH 서명 키를 GitHub 에 올리고 `git config commit.gpgsign true` 로 서명하면
커밋마다 Verified 가 붙는다. 그다음 이 규칙에 `required_signatures` 를 더한다. 지금은 넣지 않았다. 팀원 모두 서명 설정을 한 뒤에 켠다.

## 거는 순서

1. 첫 커밋(이 폴더와 PR 양식)을 main 에 올린다. 규칙이 걸리면 main 에 직접 올릴 수 없다.
2. 저장소를 공개로 바꾼다. 무료 조직 플랜에서는 공개 저장소만 규칙이 실제로 적용된다.
   Settings > General > Pull Requests 에서 squash 병합만 켜 둔다. 규칙의 `allowed_merge_methods` 와 맞춘다.
3. 시험 PR 을 하나 열어 `pr-form` 이 한 번 돌게 한다. 상태 이름이 잡혀야 필수 확인으로 고를 수 있다.
4. Settings > Rules > Rulesets > New ruleset > Import 로 `main.json` 을 넣는다. 또는
   `gh api repos/Slapdash-Seminar/Slapdash-Seminar/rulesets --method POST --input .github/rulesets/main.json`
5. 앱·서버 코드가 생기면 `test` 작업과 Go 용 CodeQL 을 필수 확인에 더한다.
