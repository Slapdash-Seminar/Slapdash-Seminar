"""정적 요구사항과 그 보호 장치를 바꾼 PR 은 사람이 단 라벨이 있어야 통과시킨다.

static-req 작업(.github/workflows/static-req.yml)이 부른다. PR 의 코드를 받지 않고
GitHub API 로 바뀐 파일 이름만 읽는다.

환경 변수: GITHUB_REPOSITORY, PR_NUMBER, PR_LABELS(JSON 배열), GH_TOKEN
로컬 시험: python check_static_req.py --files "docs/요구사항/정적/과제 틀.md" README.md [--labels "정적 요구사항 변경"]
"""

import argparse
import json
import os
import sys
import unicodedata
import urllib.request

LABEL = "정적 요구사항 변경"
PROTECTED_DIRS = ("docs/요구사항/정적/",)
PROTECTED_FILES = (
    ".claude/settings.json",
    ".claude/hooks/static_req_guard.py",
    ".github/workflows/static-req.yml",
    ".github/scripts/check_static_req.py",
)


def norm(path):
    return unicodedata.normalize("NFC", path or "")


def is_protected(path):
    path = norm(path)
    return path.startswith(PROTECTED_DIRS) or path in PROTECTED_FILES


def changed_files(repo, number, token):
    names, page = [], 1
    while True:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/pulls/{number}/files?per_page=100&page={page}",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req) as resp:
            batch = json.load(resp)
        for item in batch:
            names.append(item["filename"])
            if item.get("previous_filename"):  # 이름을 바꿔 빼낸 경우도 잡는다
                names.append(item["previous_filename"])
        if len(batch) < 100:
            return names
        page += 1


def judge(files, labels):
    hits = sorted({norm(f) for f in files if is_protected(f)})
    if not hits:
        print("정적 요구사항과 보호 장치는 바뀌지 않았다. 통과.")
        return 0
    print("이 PR 이 바꾼 보호 대상:")
    for f in hits:
        print(f"  - {f}")
    if LABEL in labels:
        print(f"`{LABEL}` 라벨이 있다. 사람이 확인한 변경으로 보고 통과.")
        return 0
    print(f"`{LABEL}` 라벨이 없다. 실패.")
    print("에이전트는 이 파일들을 고치지 않는다. 사람이 바꾼 것이면 이슈로 합의한 뒤 라벨을 단다.")
    print("절차: docs/요구사항/정적/README.md")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--labels", nargs="*", default=[])
    args = ap.parse_args()
    if args.files is not None:
        return judge(args.files, args.labels)
    labels = json.loads(os.environ.get("PR_LABELS") or "[]")
    files = changed_files(os.environ["GITHUB_REPOSITORY"], os.environ["PR_NUMBER"], os.environ["GH_TOKEN"])
    return judge(files, labels)


if __name__ == "__main__":
    sys.exit(main())
