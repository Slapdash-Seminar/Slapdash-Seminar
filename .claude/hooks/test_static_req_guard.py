"""static_req_guard.py 시험. 실행: python .claude/hooks/test_static_req_guard.py (실패 0 이어야 한다)"""
import json, subprocess, sys, unicodedata
import os
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static_req_guard.py")
R = "/repo"
cases = [
 ("Write", {"file_path": R+"/docs/요구사항/정적/과제 틀.md"}, R, True),
 ("Edit", {"file_path": r"C:\x\docs\요구사항\정적\README.md"}, R, True),
 ("Edit", {"file_path": unicodedata.normalize("NFD", "/u/docs/요구사항/정적/a.md")}, R, True),
 ("Edit", {"file_path": R+"/docs/요구사항/가변/README.md"}, R, False),
 ("Edit", {"file_path": R+"/docs/요구사항/정적"}, R, True),
 ("Bash", {"command": "cat 'docs/요구사항/정적/과제 틀.md'"}, R, False),
 ("Bash", {"command": "grep -n ST docs/요구사항/정적/*.md"}, R, False),
 ("Bash", {"command": "echo x > 'docs/요구사항/정적/과제 틀.md'"}, R, True),
 ("Bash", {"command": "sed -i 's/a/b/' docs/요구사항/정적/x.md"}, R, True),
 ("Bash", {"command": "git checkout main -- docs/요구사항/정적"}, R, True),
 ("Bash", {"command": "rm 정적/x.md"}, R+"/docs/요구사항", True),
 ("Bash", {"command": "ls 정적"}, R+"/docs/요구사항", False),
 ("PowerShell", {"command": r"Set-Content -Path docs\요구사항\정적\a.md -Value x"}, R, True),
 ("Bash", {"command": "gh pr edit 3 --add-label '정적 요구사항 변경'"}, R, True),
 ("Bash", {"command": "echo hi > docs/요구사항/가변/a.md"}, R, False),
 ("Read", {"file_path": R+"/docs/요구사항/정적/a.md"}, R, False),
]
bad = 0
for tool, inp, cwd, want in cases:
    out = subprocess.run([sys.executable, H], input=json.dumps({"tool_name": tool, "tool_input": inp, "cwd": cwd}), capture_output=True, text=True, encoding="utf-8")
    got = '"deny"' in out.stdout
    ok = got == want and out.returncode == 0
    bad += not ok
    print("OK " if ok else "BAD", tool, list(inp.values())[0][:60], "deny" if got else "allow", out.stderr[:80])
out = subprocess.run([sys.executable, H], input="not json", capture_output=True, text=True)
print("bad json ->", out.returncode, repr(out.stdout))
print("fail", bad)
sys.exit(1 if bad else 0)
