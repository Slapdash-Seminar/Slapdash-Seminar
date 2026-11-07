"""PR 본문이 양식(.github/pull_request_template.md)을 채웠는지 검사한다.

GitHub Actions 에서는 환경 변수로 받는다.
  PR_BODY    PR 본문
  PR_AUTHOR  PR 작성자 GitHub 계정
로컬에서는 PR 을 열기 전에 이렇게 돌린다.
  python .github/scripts/check_pr_form.py --file body.md --author <내 GitHub 계정>

통과하면 종료 코드 0, 고칠 곳이 있으면 목록을 찍고 1.
"""
import argparse
import os
import re
import sys

RESULTS = {"통과", "조건부 통과", "재설계"}
CONFIRM_COUNT = 4


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def sections(body):
    out, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def field(text, name):
    m = re.search(r"^\s*-\s*" + re.escape(name) + r"\s*[:：]\s*(.*)$", text, flags=re.M)
    return m.group(1).strip() if m else ""


def boxes(text):
    checked, total = [], 0
    for m in re.finditer(r"^\s*-\s*\[( |x|X)\]\s*(.+)$", text, flags=re.M):
        total += 1
        if m.group(1).lower() == "x":
            checked.append(m.group(2).strip())
    return checked, total


def norm_model(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def check(body, author):
    errs = []
    body = strip_comments(body or "")
    sec = sections(body)

    need = ["사용자", "모델", "범위", "모듈", "검수", "변경 내용", "관련 요구사항", "시험", "미완 · 위험 · 되돌리기", "확인"]
    missing = [s for s in need if s not in sec]
    if missing:
        errs.append("양식의 절이 없다: " + ", ".join(missing) + ". 템플릿을 지우지 말고 채운다")
        return errs

    # 사용자
    who = field(sec["사용자"], "요청·승인")
    m = re.search(r"@([A-Za-z0-9-]+)", who)
    if not m:
        errs.append("사용자: 요청·승인에 GitHub 계정을 @계정 으로 쓴다")
    elif author and m.group(1).lower() != author.lower():
        errs.append("사용자: 요청·승인 @{} 이 PR 작성자 @{} 와 다르다. 그 사람 계정으로 PR 을 연다".format(m.group(1), author))
    if not field(sec["사용자"], "이름"):
        errs.append("사용자: 이름을 쓴다")

    # 모델
    writer = field(sec["모델"], "작성 모델")
    if not writer:
        errs.append("모델: 작성 모델을 쓴다(사람이 짰으면 \"사람\")")
    if writer and writer != "사람" and not field(sec["모델"], "도구"):
        errs.append("모델: 도구를 쓴다(예: Claude Code 2.1.x)")

    # 범위, 모듈
    scope, _ = boxes(sec["범위"])
    if not scope:
        errs.append("범위: 하나 이상 고른다")
    mods, _ = boxes(sec["모듈"])
    if len(mods) != 1:
        errs.append("모듈: 정확히 하나 고른다(지금 {}개). 여러 모듈이면 PR 을 나눈다".format(len(mods)))

    # 검수
    rv = sec["검수"]
    reviewer = field(rv, "검수 모델")
    if not reviewer:
        errs.append("검수: 검수 모델을 쓴다")
    elif writer and writer != "사람" and norm_model(reviewer) == norm_model(writer):
        errs.append("검수: 검수 모델이 작성 모델과 같다. 다른 모델로 검수한다")
    cnt = field(rv, "검수 횟수")
    if not re.fullmatch(r"\d+(\s*회)?", cnt) or int(re.match(r"\d+", cnt).group()) < 1:
        errs.append("검수: 검수 횟수를 1 이상의 숫자로 쓴다")
    res = field(rv, "결과")
    if res not in RESULTS:
        errs.append("검수: 결과는 통과, 조건부 통과, 재설계 중 하나다")
    elif res == "재설계":
        errs.append("검수: 결과가 재설계다. 다시 짜고 검수한 뒤 연다")
    if not field(rv, "검수 내용"):
        errs.append("검수: 검수 내용을 쓴다")
    if not field(rv, "남은 지적"):
        errs.append("검수: 남은 지적을 쓴다(없으면 \"없음\")")

    # 나머지 글 칸
    if not sec["변경 내용"]:
        errs.append("변경 내용: 무엇을 왜 바꿨는지 쓴다")
    if not field(sec["관련 요구사항"], "요구사항 ID"):
        errs.append("관련 요구사항: 요구사항 ID 를 쓴다(없으면 \"없음\")")
    if not sec["시험"]:
        errs.append("시험: 돌린 명령과 결과를 쓴다")
    if not sec["미완 · 위험 · 되돌리기"]:
        errs.append("미완 · 위험 · 되돌리기: 쓴다(없으면 \"없음\")")

    # 확인
    ok, total = boxes(sec["확인"])
    if total < CONFIRM_COUNT or len(ok) < total:
        errs.append("확인: 네 칸을 모두 체크한다")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--author")
    a = ap.parse_args()
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            body = f.read()
    else:
        body = os.environ.get("PR_BODY", "")
    author = a.author if a.author is not None else os.environ.get("PR_AUTHOR", "")

    if author.endswith("[bot]"):
        print("봇 PR 이라 양식 검사를 건너뛴다: " + author)
        return 0

    errs = check(body, author)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if errs:
        msg = "PR 양식에서 고칠 곳 {}개\n".format(len(errs)) + "\n".join("- " + e for e in errs)
        print(msg)
        if summary:
            with open(summary, "a", encoding="utf-8") as f:
                f.write("## PR 양식 검사: 고칠 곳 {}개\n\n".format(len(errs)) + "\n".join("- " + e for e in errs) + "\n")
        return 1
    print("PR 양식 검사 통과")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## PR 양식 검사 통과\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
