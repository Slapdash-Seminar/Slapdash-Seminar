"""static_req_guard.py 시험. 실행: python .claude/hooks/test_static_req_guard.py (fail 0, 종료 0 이어야 한다)

훅이 실제로 받는 것처럼 표준 입력에 UTF-8 바이트를 넣고, 자식의 출력도 UTF-8 로 읽는다.
Windows 기본 인코딩(cp949)에서도 그대로 돌아야 한다.
"""

import json
import os
import subprocess
import sys
import unicodedata

H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static_req_guard.py")
R = "/repo"
REQ = R + "/docs/요구사항"

# (도구, 입력, cwd, 막아야 하나)
CASES = [
    # 파일 도구
    ("Write", {"file_path": R + "/docs/요구사항/정적/과제 틀.md"}, R, True),
    ("Edit", {"file_path": r"C:\x\docs\요구사항\정적\README.md"}, R, True),
    ("Edit", {"file_path": unicodedata.normalize("NFD", "/u/docs/요구사항/정적/a.md")}, R, True),
    ("Edit", {"file_path": R + "/docs/요구사항/정적"}, R, True),
    ("Write", {"file_path": "정적/a.md"}, REQ, True),
    ("Write", {"file_path": "docs/요구사항/x/../정적/a.md"}, R, True),
    ("Edit", {"file_path": R + "/.claude/settings.json"}, R, True),
    ("Write", {"file_path": ".claude/settings.local.json"}, R, True),
    ("Edit", {"file_path": R + "/.claude/hooks/static_req_guard.py"}, R, True),
    ("Edit", {"file_path": R + "/.github/CODEOWNERS"}, R, True),
    ("Edit", {"file_path": R + "/docs/요구사항/가변/README.md"}, R, False),
    ("Write", {"file_path": "가변/기능/team.md"}, REQ, False),
    ("Edit", {"file_path": R + "/docs/정적분석.md"}, R, False),
    ("Read", {"file_path": R + "/docs/요구사항/정적/a.md"}, R, False),
    # 셸 읽기
    ("Bash", {"command": "cat 'docs/요구사항/정적/과제 틀.md'"}, R, False),
    ("Bash", {"command": "grep -n ST docs/요구사항/정적/*.md"}, R, False),
    ("Bash", {"command": "ls 정적"}, REQ, False),
    ("Bash", {"command": "cat .claude/settings.json"}, R, False),
    # 셸 쓰기
    ("Bash", {"command": "echo x > 'docs/요구사항/정적/과제 틀.md'"}, R, True),
    ("Bash", {"command": "sed -i 's/a/b/' docs/요구사항/정적/x.md"}, R, True),
    ("Bash", {"command": "git checkout main -- docs/요구사항/정적"}, R, True),
    ("Bash", {"command": "rm 정적/x.md"}, REQ, True),
    ("Bash", {"command": "cd docs/요구사항 && echo x > 정적/a.md"}, R, True),
    ("PowerShell", {"command": r"Set-Content -Path docs\요구사항\정적\a.md -Value x"}, R, True),
    ("Bash", {"command": "echo '{}' > .claude/settings.json"}, R, True),
    ("Bash", {"command": "echo x >> .github/CODEOWNERS"}, R, True),
    ("Bash", {"command": "echo '{\"disableAllHooks\": true}' > x.json"}, R, True),
    ("Bash", {"command": "echo hi > docs/요구사항/가변/a.md"}, R, False),
    # 대소문자 (Windows·macOS 는 같은 파일)
    ("Write", {"file_path": R + "/DOCS/요구사항/정적/a.md"}, R, True),
    ("Edit", {"file_path": R + "/.CLAUDE/Settings.json"}, R, True),
    ("Edit", {"file_path": R + "/.github/codeowners"}, R, True),
    ("Bash", {"command": "echo x > DOCS/요구사항/정적/a.md"}, R, True),
    # 오탐이면 안 되는 것
    ("Bash", {"command": "python .claude/hooks/test_static_req_guard.py"}, R, False),
    ("Bash", {"command": "python -B .claude/hooks/test_static_req_guard.py"}, R, False),
    ("Bash", {"command": "echo '정적 요구사항과 맞춘다' >> 가변/기능/team.md"}, REQ, False),
    ("Bash", {"command": "echo '정적 요구사항과 맞춘다' >> docs/요구사항/가변/README.md"}, R, False),
    # 명령줄 코드로 쓰기
    ("Bash", {"command": "python -c \"open('docs/요구사항/정적/a.md','w').write('x')\""}, R, True),
    ("Bash", {"command": "rm -r 정적"}, REQ, True),
    ("Bash", {"command": "python -Bc \"open('docs/요구사항/정적/a.md','w').write('x')\""}, R, True),
    ("Bash", {"command": "node --eval \"require('fs').writeFileSync('docs/요구사항/정적/a.md','x')\""}, R, True),
    ("Bash", {"command": "python - <<'PY'\nopen('docs/요구사항/정적/a.md','w').write('x')\nPY"}, R, True),
    ("Bash", {"command": "echo \"open('docs/요구사항/정적/a.md','w')\" | python -"}, R, True),
    ("Bash", {"command": "python -Bc \"open('.claude/settings.json','w').write('{}')\""}, R, True),
    ("Bash", {"command": "echo '{}' | python - .claude/settings.json"}, R, True),
    # 4회차: 검색어·파일 이름·데이터 파이프·낱말은 막지 않는다
    ("Bash", {"command": "rg -n 'python' docs/요구사항/정적/README.md"}, R, False),
    ("Bash", {"command": "grep -n sh docs/요구사항/정적/README.md scripts/check.sh"}, R, False),
    ("Bash", {"command": "cat .claude/settings.json | python -B -m json.tool"}, R, False),
    ("Bash", {"command": "echo settings.json >> docs/요구사항/가변/README.md"}, R, False),
    ("Bash", {"command": "echo codeowners >> docs/요구사항/가변/README.md"}, R, False),
    ("Bash", {"command": "cat docs/요구사항/정적/README.md | sh"}, R, True),
    ("Bash", {"command": "ls docs/요구사항/정적 && /usr/bin/python3 x.py"}, R, True),
    ("Bash", {"command": "cd .claude && echo '{}' > settings.json"}, R, True),
    ("Bash", {"command": "echo '{}' > settings.json"}, R + "/.claude", True),
    ("Bash", {"command": "cat .claude/settings.json | python -"}, R, True),
    # 5회차: 접두어·앞 공백, 상위 폴더 상대 경로
    ("Bash", {"command": "  python -Bc \"open('docs/요구사항/정적/a.md','w').write('x')\""}, R, True),
    ("Bash", {"command": "env FOO=1 python -Bc \"open('docs/요구사항/정적/a.md','w')\""}, R, True),
    ("Bash", {"command": "sudo -u me python -Bc \"open('docs/요구사항/정적/a.md','w')\""}, R, True),
    ("Bash", {"command": "FOO=1 node -e \"x\" docs/요구사항/정적/a.md"}, R, True),
    ("Bash", {"command": "echo '{}' > ../settings.json"}, R + "/.claude/hooks", True),
    ("Bash", {"command": "echo x >> ../CODEOWNERS"}, R + "/.github/rulesets", True),
    ("Bash", {"command": "echo x > ./static_req_guard.py"}, R + "/.claude/hooks", True),
    ("Bash", {"command": "cat ../settings.json"}, R + "/.claude/hooks", False),
    ("Bash", {"command": "echo hi > notes.md"}, R + "/.claude/hooks", False),
    # 6회차: 보호 파일을 읽어 다른 곳에 쓰거나 경로를 글로 적는 것은 통과
    ("Bash", {"command": "cat ../settings.json > /tmp/settings-copy.json"}, R + "/.claude/hooks", False),
    ("Bash", {"command": "echo '../settings.json' > notes.md"}, R + "/.claude/hooks", False),
    ("Bash", {"command": "cat ../CODEOWNERS > /tmp/codeowners-copy"}, R + "/.github/rulesets", False),
    ("Bash", {"command": "cp /tmp/x ../settings.json"}, R + "/.claude/hooks", True),
    ("Bash", {"command": "rm ../CODEOWNERS"}, R + "/.github/rulesets", True),
    ("Bash", {"command": "echo x | tee ../settings.json"}, R + "/.claude/hooks", True),
    # 7회차 참고: git 하위 명령과 chmod 의 대상
    ("Bash", {"command": "git restore -- ../settings.json"}, R + "/.claude/hooks", True),
    ("Bash", {"command": "git checkout main -- ../CODEOWNERS"}, R + "/.github/rulesets", True),
    ("Bash", {"command": "chmod 600 ../settings.json"}, R + "/.claude/hooks", True),
    ("Bash", {"command": "git log -- ../settings.json"}, R + "/.claude/hooks", False),
    # 8회차: 미리 보기만 하는 git 옵션은 통과
    ("Bash", {"command": "git clean -n -- ../settings.json"}, R + "/.claude/hooks", False),
    ("Bash", {"command": "git clean --dry-run -- ../settings.json"}, R + "/.claude/hooks", False),
    ("Bash", {"command": "git rm -n -- ../settings.json"}, R + "/.claude/hooks", False),
    ("Bash", {"command": "git rm -- ../settings.json"}, R + "/.claude/hooks", True),
    # 글자로만 보므로 막히는 정상 명령. Edit 도구로 쓰면 된다(정적 README)
    ("Bash", {"command": "echo 정적 > 가변/note.md"}, REQ, True),
    ("Write", {"file_path": "가변/note.md"}, REQ, False),
    # 승인 대신하기
    ("Bash", {"command": "gh pr review 3 --approve"}, R, True),
    ("Bash", {"command": "gh pr review 3 -a -b ok"}, R, True),
    ("Bash", {"command": "gh api repos/o/r/pulls/3/reviews -f event=APPROVE"}, R, True),
    ("Bash", {"command": "gh pr review 3 --comment -b '좋아요'"}, R, False),
]


def run(stdin_bytes):
    # 자식은 그 PC 의 기본 인코딩 그대로 돌린다. 훅이 실제로 도는 조건이다.
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    return subprocess.run([sys.executable, H], input=stdin_bytes, capture_output=True, env=env)


def main():
    sys.stdout.reconfigure(errors="replace")  # cp949 콘솔에서 자모(NFD) 출력으로 죽지 않게
    bad = 0
    for tool, inp, cwd, want in CASES:
        payload = json.dumps({"tool_name": tool, "tool_input": inp, "cwd": cwd}, ensure_ascii=False)
        out = run(payload.encode("utf-8"))
        got = b'"deny"' in out.stdout
        ok = got == want and out.returncode == 0
        bad += not ok
        print("OK " if ok else "BAD", tool, str(list(inp.values())[0])[:60],
              "deny" if got else "allow", out.stderr.decode("utf-8", "replace")[:80])
    out = run(b"not json")
    print("깨진 입력 ->", out.returncode, repr(out.stdout))
    bad += out.returncode != 0 or out.stdout != b""
    print("fail", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
