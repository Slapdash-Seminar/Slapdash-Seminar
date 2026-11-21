# Flutter (Dart)

`app/` 에 적용한다. 공통 규칙은 `코드 공통.md`.

## 도구

- 서식은 `dart format .` 이다. 줄 길이는 기본값 80 이다.
- `flutter analyze` 결과가 0건이어야 PR 을 연다. 경고를 끄려면 그 줄에 `// ignore: 규칙이름` 과 까닭을 함께 쓴다.
- `app/` 을 처음 만드는 PR 이 `app/analysis_options.yaml` 을 아래 내용으로 둔다. 규칙을 더하거나 빼려면 이 파일부터 PR 로 고친다.

```yaml
include: package:flutter_lints/flutter.yaml

linter:
  rules:
    - always_use_package_imports
    - avoid_print
    - directives_ordering
    - prefer_const_constructors
    - prefer_final_locals
    - prefer_single_quotes
    - require_trailing_commas
    - unawaited_futures
```

## 폴더

```
app/lib/
  main.dart
  common/        여러 모듈이 같이 쓰는 위젯, 테마, 화면 이동, Supabase 연결
  <모듈>/        member, team, schedule, notice, file, admin, alert
    screens/     화면 하나에 파일 하나. 이름 끝은 _screen.dart
    widgets/     그 모듈 안에서만 쓰는 위젯
    data/        Supabase·서버 호출과 모델
    state/       화면 상태
app/test/<모듈>/ 시험. 이름 끝은 _test.dart
```

- 다른 모듈의 `screens/`, `widgets/`, `state/` 를 직접 가져다 쓰지 않는다. 같이 써야 하면 `common/` 으로 옮기는 PR 을 `skeleton` 으로 연다.
- 다른 모듈의 `data/` 는 가져다 써도 된다.

## 쓰는 법

- 파일 이름은 `snake_case.dart`, 클래스는 `UpperCamelCase`, 변수와 함수는 `lowerCamelCase` 다.
- 화면 위젯 이름은 `~Screen`, 바닥에서 올라오는 창은 `~Sheet`, 가운데 창은 `~Dialog` 로 끝낸다.
- 위젯 안에서 Supabase 나 HTTP 를 직접 부르지 않는다. `data/` 의 클래스를 거친다.
- `!` 로 null 을 억지로 벗기지 않는다. 피할 수 없으면 왜 null 이 아닌지 주석을 단다.
- 색, 글자 크기, 간격은 `common/` 의 테마 값을 쓴다. 위젯마다 숫자를 새로 쓰지 않는다.
- 상태 관리 도구는 아직 정하지 않았다. `app/` 을 처음 만드는 PR 이 하나를 골라 `.claude/memory/skeleton/결정.md` 에 남기고 이 줄을 고친다. 그 전에는 다른 도구를 섞지 않는다.
