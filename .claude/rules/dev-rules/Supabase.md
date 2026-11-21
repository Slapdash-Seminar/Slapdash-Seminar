# Supabase (DB · 권한)

`supabase/` 에 적용한다. 공통 규칙은 `코드 공통.md`.

## 마이그레이션

- 스키마는 마이그레이션으로만 바꾼다. Studio 에서 손으로 바꾸지 않는다.
- 새 파일은 `supabase migration new <영문_설명>` 으로 만든다. 예: `20261125093000_create_schedule_requests.sql`
- main 에 들어간 마이그레이션은 고치지 않는다. 바꿀 것이 있으면 새 마이그레이션을 더한다.
- 두 PR 이 같은 테이블을 바꾸면 나중에 병합하는 쪽이 파일 시각을 뒤로 바꾸고 다시 시험한다.

## 이름

| 대상 | 꼴 | 예 |
|---|---|---|
| 테이블 | 복수형 `snake_case` | `teams`, `team_members`, `schedule_requests` |
| 열 | `snake_case` | `display_name`, `discord_id` |
| 기본 키 | `id uuid primary key default gen_random_uuid()` | |
| 외래 키 | `<가리키는 테이블 단수>_id` | `team_id`, `schedule_request_id` |
| 시각 | `timestamptz`, 이름 끝 `_at` | `created_at`, `confirmed_at` |
| 참·거짓 | `is_` 또는 `has_` 로 시작 | `is_confirmed` |
| 정책 | `<테이블>_<동작>_<누가>` | `materials_select_team_member` |

- 모든 테이블에 `created_at timestamptz not null default now()` 를 둔다. 고칠 수 있는 테이블은 `updated_at` 도 둔다.
- 정해진 값만 들어가는 열(역할, 발송 상태)은 `check` 제약이나 enum 타입으로 막는다.

## 권한 (RLS)

- 테이블을 만드는 마이그레이션에서 `enable row level security` 와 정책을 함께 쓴다. 정책 없이 테이블만 만드는 PR 은 받지 않는다.
- 권한 판단은 정책과 서버에서 한다. 앱 화면에서 버튼을 숨기는 것은 편의일 뿐이다(`docs/요구사항/정적/과제 틀.md` ST-09).
- `service_role` 키는 Go 서버만 쓴다. 앱에는 `anon` 키만 들어간다.
- 정책을 고치면 PR 본문 `시험` 에 "다른 팀 회원으로 읽기가 막힌다" 처럼 막히는 경우를 하나 이상 적는다.

## 시드

- 개발용 시드(`supabase/seed.sql`)에는 가짜 이름과 `example.com` 메일만 쓴다. 실제 회원 정보와 비밀번호를 넣지 않는다.
