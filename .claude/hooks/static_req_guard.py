"""정적 요구사항(docs/요구사항/정적/)을 Claude Code 가 고치지 못하게 막는 PreToolUse 훅.

.claude/settings.json 의 permissions.deny 와 함께 쓴다. deny 는 파일 수정 도구만 막으므로
셸 명령으로 쓰는 길과 `정적 요구사항 변경` 라벨을 다는 길을 이 훅이 막는다.
여기서 못 잡는 길(스크립트가 경로를 조립해 쓰는 경우 등)은 CI(static-req)가 PR 에서 잡는다.

막을 때는 종료 코드 0 과 함께 deny 결정을 JSON 으로 내보낸다. 입력을 못 읽으면 막지 않는다.
"""

import json
import re
import sys
import unicodedata

PROTECTED = "docs/요구사항/정적"
LABEL = "정적 요구사항 변경"
FILE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}

# 셸 명령에서 파일을 쓰거나 옮기거나 지우는 낌새. 읽기 명령은 통과시킨다.
WRITE_HINT = re.compile(
    r">"
    r"|\b(tee|mv|cp|rm|rmdir|touch|mkdir|ln|truncate|dd|chmod|install|rsync|del|ren|move|copy)\b"
    r"|\b(sed|perl)\b[^|;&]*\s-i"
    r"|\bgit\s+(rm|mv|checkout|restore|reset|apply|am|stash|clean|cherry-pick|revert|switch)\b"
    r"|\b(python3?|py|node|ruby|pwsh|powershell)\b"
    r"|\b(Set-Content|Add-Content|Out-File|Clear-Content|Remove-Item|Move-Item|Copy-Item|New-Item|Rename-Item)\b",
    re.IGNORECASE,
)


def norm(text):
    # macOS 는 한글 경로를 자모로 풀어(NFD) 넘길 수 있다. 비교 전에 합친다(NFC).
    return unicodedata.normalize("NFC", text or "").replace("\\", "/")


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def touches_protected(command, cwd):
    if PROTECTED in command or PROTECTED in cwd:
        return True
    # docs/요구사항 안에서 `정적/...` 처럼 상대 경로로 가리키는 경우
    return "docs/요구사항" in cwd and "정적" in command


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    tool = data.get("tool_name", "")
    args = data.get("tool_input") or {}
    cwd = norm(data.get("cwd", ""))

    if tool in FILE_TOOLS:
        path = norm(args.get("file_path") or args.get("notebook_path") or "")
        if PROTECTED + "/" in path or path.endswith(PROTECTED):
            deny(f"{PROTECTED}/ 는 정적 요구사항이라 에이전트가 고치지 않는다. "
                 f"바꿔야 하면 멈추고 사람에게 묻는다({PROTECTED}/README.md).")
        return

    if tool in SHELL_TOOLS:
        command = norm(args.get("command", ""))
        if LABEL in command:
            deny(f"`{LABEL}` 라벨은 사람이 단다. 에이전트는 이 라벨을 달거나 만들지 않는다.")
        if touches_protected(command, cwd) and WRITE_HINT.search(command):
            deny(f"이 명령은 {PROTECTED}/ 를 바꿀 수 있어 막았다. 읽기만 하려면 Read 도구나 "
                 f"cat·grep 처럼 쓰지 않는 명령을 쓴다({PROTECTED}/README.md).")


if __name__ == "__main__":
    main()
