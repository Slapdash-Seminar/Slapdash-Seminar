# Go

`server/` 에 적용한다. 공통 규칙은 `코드 공통.md`.

## 도구

- 서식은 `gofmt -w .` 이고, import 정리는 `goimports` 를 쓴다.
- `go vet ./...` 과 `go test ./...` 이 통과해야 PR 을 연다.
- Go 판은 `server/go.mod` 의 `go` 줄이 정한다. 올리려면 그 PR 에서 까닭을 적는다.

## 폴더

```
server/
  cmd/server/main.go      시작점. 설정을 읽고 연결만 한다
  internal/<모듈>/         schedule(후보 시간 계산), notice(디스코드 발송) 등
  internal/common/         설정, 로그, DB 연결, 디스코드 클라이언트
```

- 모듈 사이 호출은 `internal/<모듈>` 이 내보낸 함수와 타입으로만 한다.
- 시험은 같은 폴더의 `_test.go` 에 둔다. 경우가 여럿이면 표 기반 시험(table-driven)으로 쓴다.

## 쓰는 법

- 이름은 Go 관례를 따른다. 패키지는 소문자 한 단어, 밖에 내보내는 것은 `UpperCamel`, 안에서만 쓰는 것은 `lowerCamel` 이다.
- 오류는 `fmt.Errorf("후보 시간 계산: %w", err)` 처럼 감싸 위로 넘긴다. 같은 오류를 로그에 남기고 또 넘기지 않는다. 한 번만 처리한다.
- 요청 처리 함수 안에서 `panic` 하지 않는다.
- 오래 걸리거나 밖을 부르는 함수는 첫 인자로 `ctx context.Context` 를 받는다.
- JSON 필드 이름은 `snake_case` 다. DB 이름과 맞춘다. 예: `json:"candidate_slot_id"`
- 설정은 환경 변수에서 `internal/common` 이 한 번 읽는다. 다른 곳에서 `os.Getenv` 를 부르지 않는다.
- 시간은 저장과 계산을 UTC 로 하고, 화면에 보일 때만 한국 시간으로 바꾼다.
