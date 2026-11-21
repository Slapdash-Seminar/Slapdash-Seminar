"""정적 요구사항(docs/요구사항/정적/)과 그 보호 장치를 Claude Code 가 고치지 못하게 막는 PreToolUse 훅.

.claude/settings.json 의 permissions.deny 와 함께 쓴다. deny 는 파일 수정 도구만 막으므로
상대 경로로 쓰는 길, 셸 명령으로 쓰는 길, 보호 장치를 끄는 길, PR 승인을 대신하는 길을 이 훅이 막는다.

한계: 셸 명령은 글자로만 본다. 변수나 스크립트가 경로를 조립해 쓰면 못 잡는다.
그래서 마지막 관문은 GitHub 의 2인 승인(.github/CODEOWNERS, 코드 오너 승인)이다.

막을 때는 종료 코드 0 과 함께 deny 결정을 JSON 으로 내보낸다. 입력을 못 읽으면 막지 않는다.
"""

import json
import posixpath
import re
import shlex
import sys
import unicodedata

STATIC = "docs/요구사항/정적"
# 보호 장치. 이것을 고치면 정적 보호가 꺼진다.
GUARDS = (
    ".claude/settings.json",
    ".claude/settings.local.json",
    ".claude/hooks/static_req_guard.py",
    ".github/CODEOWNERS",
)
FILE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}

# 셸 명령에서 파일을 쓰거나 옮기거나 지우는 낌새. 읽기 명령은 통과시킨다.
WRITE_HINT = re.compile(
    r">"
    r"|\b(tee|mv|cp|rm|rmdir|touch|mkdir|ln|truncate|dd|chmod|install|rsync|del|ren|move|copy)\b"
    r"|\b(sed|perl)\b[^|;&]*\s-i"
    r"|\bgit\s+(rm|mv|checkout|restore|reset|apply|am|stash|clean|cherry-pick|revert|switch)\b"
    r"|\b(Set-Content|Add-Content|Out-File|Clear-Content|Remove-Item|Move-Item|Copy-Item|New-Item|Rename-Item)\b",
    re.IGNORECASE,
)
# 인터프리터. 정적 경로가 나오는 명령에서는 옵션 모양과 상관없이 막는다(-Bc, --eval, 표준 입력 코드 등).
INTERPRETER = re.compile(
    r"\b(python3?|py|node|deno|bun|ruby|perl|php|pwsh|powershell|bash|sh|zsh|cmd)\b",
    re.IGNORECASE,
)
# 보호 장치 이름만 나오는 명령에서는 코드를 명령줄이나 표준 입력으로 넘길 때만 막는다.
# 훅 시험처럼 스크립트 파일을 돌리는 것은 통과시킨다.
INLINE_CODE = re.compile(
    r"\b(python3?|py|node|deno|bun|ruby|perl|php)\b[^|;&]*\s(-[A-Za-z]*[ce][A-Za-z]*\b|--eval\b|--command\b|-(\s|$))"
    r"|\b(pwsh|powershell|bash|sh|zsh|cmd)\b[^|;&]*\s(-[A-Za-z]*c[A-Za-z]*\b|-command\b|-encodedcommand\b|/c\b)"
    r"|<<"
    r"|\|\s*(python3?|py|node|deno|bun|ruby|perl|php|pwsh|powershell|bash|sh|zsh)\b",
    re.IGNORECASE,
)
# PR 승인은 사람이 한다. 에이전트가 승인하면 2인 동의가 무너진다.
APPROVE = re.compile(
    r"\bgh\s+pr\s+review\b[^|;&]*(--approve|\s-a\b)"
    r"|\breviews\b[^|;&]*\bAPPROVE\b",
    re.IGNORECASE,
)
ABSOLUTE = re.compile(r"^(/|[A-Za-z]:/)")


def norm(text):
    # macOS 는 한글 경로를 자모로 풀어(NFD) 넘길 수 있다. 비교 전에 합친다(NFC).
    return unicodedata.normalize("NFC", text or "").replace("\\", "/")


def low(text):
    # Windows·macOS 는 경로의 대소문자를 가리지 않는다. 비교는 소문자로 한다.
    return text.lower()


def resolve(path, cwd):
    # 상대 경로는 cwd 에 붙이고 `..` 를 푼다.
    if path and not ABSOLUTE.match(path) and cwd:
        path = cwd.rstrip("/") + "/" + path
    return posixpath.normpath(path) if path else ""


def is_protected(path):
    p = "/" + low(path).lstrip("/")
    if "/" + STATIC + "/" in p + "/":
        return True
    return any(p.endswith("/" + low(g)) for g in GUARDS)


def deny(reason):
    # Windows 콘솔 인코딩(cp949)에 흔들리지 않게 ASCII 로 내보낸다. JSON 이 \u 를 풀어 준다.
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def tokens(command):
    # 따옴표로 묶은 글은 한 덩어리로 본다. 가변 문서에 "정적 요구사항" 이라는 글을 쓰는 것은 경로가 아니다.
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return command.split()


def touches_static(command, cwd):
    command, cwd = low(command), low(cwd)
    if STATIC in command or STATIC in cwd:
        return True
    # docs/요구사항 안에서, 또는 그리로 cd 한 뒤 `정적/...` 처럼 상대 경로로 가리키는 경우.
    # 글자로만 보므로 `echo 정적 > 가변/a.md` 처럼 낱말을 쓰는 명령도 막힌다. 그때는 Edit 도구를 쓴다.
    if "docs/요구사항" in cwd or "요구사항" in command:
        for t in tokens(command):
            t = t.rstrip("/")
            if t == "정적" or t.startswith("정적/") or t.endswith("/정적") or "/정적/" in t:
                return True
    return False


def touches_guard(command):
    names = [low(g.rsplit("/", 1)[-1]) for g in GUARDS] + [".claude/settings", "codeowners"]
    return any(n in low(command) for n in names)


def main():
    try:
        # Windows 는 표준 입력을 cp949 로 읽어 한글 경로를 깨뜨린다. 바이트로 받아 UTF-8 로 푼다.
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return
    tool = data.get("tool_name", "")
    args = data.get("tool_input") or {}
    cwd = norm(data.get("cwd", ""))
    why = f"{STATIC}/README.md"

    if tool in FILE_TOOLS:
        path = resolve(norm(args.get("file_path") or args.get("notebook_path") or ""), cwd)
        if is_protected(path):
            deny(f"{path} 는 정적 요구사항이나 그 보호 장치라 에이전트가 고치지 않는다. "
                 f"바꿔야 하면 멈추고 사람에게 묻는다({why}).")
        return

    if tool in SHELL_TOOLS:
        command = norm(args.get("command", ""))
        if "disableallhooks" in low(command):
            deny("훅을 끄는 설정은 에이전트가 만들지 않는다.")
        if APPROVE.search(command):
            deny(f"PR 승인은 사람이 직접 한다. 정적 요구사항은 두 사람의 동의가 있어야 바뀐다({why}).")
        static = touches_static(command, cwd)
        guard = touches_guard(command)
        if (static and (WRITE_HINT.search(command) or INTERPRETER.search(command))) or \
                (guard and (WRITE_HINT.search(command) or INLINE_CODE.search(command))):
            deny(f"이 명령은 정적 요구사항이나 그 보호 장치를 바꿀 수 있어 막았다. 읽기만 하려면 Read 도구나 "
                 f"cat·grep 처럼 쓰지 않는 명령을 쓴다({why}).")


if __name__ == "__main__":
    main()
