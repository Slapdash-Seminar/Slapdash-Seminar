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
# 체크박스 문구는 이 템플릿과 대조한다. 워크플로우는 main 의 템플릿을 받아 오므로 PR 이 바꿀 수 없다.
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pull_request_template.md")
BOX_SECTIONS = ("범위", "모듈", "확인")


def meaningful(v, allow_none=False):
    """'-', '.', '?' 같은 채움값이 아니라 실제 내용이 있는가. allow_none 이면 "없음" 도 받는다."""
    v = (v or "").strip()
    if allow_none and v == "없음":
        return True
    return len(re.sub(r"[\s\-–—_.·,:;/?!()\[\]<>'\"`~*]", "", v)) >= 2


def template_boxes():
    with open(TEMPLATE, encoding="utf-8") as f:
        sec = sections(strip_comments(f.read()))
    out = {}
    for name in BOX_SECTIONS:
        _, labels = boxes(sec.get(name, ""))
        out[name] = labels
    return out


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
    """(체크한 문구 목록, 모든 문구 목록)"""
    checked, labels = [], []
    for m in re.finditer(r"^\s*-\s*\[( |x|X)\]\s*(.+)$", text, flags=re.M):
        label = m.group(2).strip()
        labels.append(label)
        if m.group(1).lower() == "x":
            checked.append(label)
    return checked, labels


def norm_model(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def check(body, author, allowed=None):
    errs = []
    body = strip_comments(body or "")
    sec = sections(body)
    allowed = allowed if allowed is not None else template_boxes()

    need = ["사용자", "모델", "범위", "모듈", "검수", "변경 내용", "관련 요구사항", "시험", "미완 · 위험 · 되돌리기", "확인"]
    missing = [s for s in need if s not in sec]
    if missing:
        errs.append("양식의 절이 없다: " + ", ".join(missing) + ". 템플릿을 지우지 말고 채운다")
        return errs

    # 사용자
    who = field(sec["사용자"], "요청·승인")
    m = re.search(r"@([A-Za-z0-9-]+(?:\[bot\])?)", who)  # 봇 계정은 이름 끝에 [bot] 이 붙는다
    if not m:
        errs.append("사용자: 요청·승인에 GitHub 계정을 @계정 으로 쓴다")
    elif author and m.group(1).lower() != author.lower():
        errs.append("사용자: 요청·승인 @{} 이 PR 작성자 @{} 와 다르다. 그 사람 계정으로 PR 을 연다".format(m.group(1), author))
    if not meaningful(field(sec["사용자"], "이름")):
        errs.append("사용자: 이름을 쓴다")

    # 모델
    writer = field(sec["모델"], "작성 모델")
    if writer != "사람" and not meaningful(writer):
        errs.append("모델: 작성 모델을 쓴다(사람이 짰으면 \"사람\")")
        writer = ""
    if writer and writer != "사람" and not meaningful(field(sec["모델"], "도구")):
        errs.append("모델: 도구를 쓴다(예: Claude Code 2.1.x)")

    # 범위, 모듈, 확인: 템플릿에 없는 체크박스 문구는 받지 않는다
    for name in BOX_SECTIONS:
        _, labels = boxes(sec[name])
        extra = [x for x in labels if x not in allowed[name]]
        if extra:
            errs.append("{}: 템플릿에 없는 항목이 있다({}). 템플릿 문구를 고치지 않는다".format(name, ", ".join(extra[:3])))
    scope, _ = boxes(sec["범위"])
    scope = [x for x in scope if x in allowed["범위"]]
    if not scope:
        errs.append("범위: 하나 이상 고른다")
    mods, _ = boxes(sec["모듈"])
    mods = [x for x in mods if x in allowed["모듈"]]
    if len(mods) != 1:
        errs.append("모듈: 정확히 하나 고른다(지금 {}개). 여러 모듈이면 PR 을 나눈다".format(len(mods)))

    # 검수
    rv = sec["검수"]
    reviewer = field(rv, "검수 모델")
    if not meaningful(reviewer):
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
    if not meaningful(field(rv, "검수 내용")):
        errs.append("검수: 검수 내용을 쓴다")
    if not meaningful(field(rv, "남은 지적"), allow_none=True):
        errs.append("검수: 남은 지적을 쓴다(없으면 \"없음\")")

    # 나머지 글 칸
    if not meaningful(sec["변경 내용"]):
        errs.append("변경 내용: 무엇을 왜 바꿨는지 쓴다")
    if not meaningful(field(sec["관련 요구사항"], "요구사항 ID"), allow_none=True):
        errs.append("관련 요구사항: 요구사항 ID 를 쓴다(없으면 \"없음\")")
    if not meaningful(sec["시험"]):
        errs.append("시험: 돌린 명령과 결과를 쓴다")
    if not meaningful(sec["미완 · 위험 · 되돌리기"], allow_none=True):
        errs.append("미완 · 위험 · 되돌리기: 쓴다(없으면 \"없음\")")

    # 확인: 템플릿의 네 칸이 모두 있고 모두 체크
    ok, _ = boxes(sec["확인"])
    if any(x not in ok for x in allowed["확인"]):
        errs.append("확인: {}칸을 모두 체크한다".format(len(allowed["확인"])))
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

    # 봇 PR 도 예외 없이 검사한다(2026-11-07 Codex 검수 지적).
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
