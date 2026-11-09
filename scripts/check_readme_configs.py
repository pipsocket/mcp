"""Check that the README's setup snippets are valid and connect to the server in server.json.

Each client's section is checked against what that client needs for a remote server that signs in
with OAuth: the server's URL over HTTP, and no API key or headers.
"""

import json
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTION = re.compile(r"^### (.+)$", re.MULTILINE)
CODE_BLOCK = re.compile(r"^```(\w+)\n(.*?)^```", re.MULTILINE | re.DOTALL)

# The JSON shape each client's own documentation gives for a remote HTTP server. Claude Code reads an
# entry with no "type" as a local (stdio) server, so it needs "type": "http". Cursor's remote entries
# are just a "url".
JSON_ENTRY_KEYS = {
    "Claude Code": {"type": "http"},
    "Cursor": {},
}


def sections(readme: str) -> dict[str, str]:
    """The README's level-3 sections, by heading."""
    parts = SECTION.split(readme)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}


def check_json(client: str, block: str, server_url: str) -> list[str]:
    try:
        config = json.loads(block)
    except json.JSONDecodeError as error:
        return [f"{client}: JSON snippet is not valid JSON: {error}"]

    entries = config.get("mcpServers") if isinstance(config, dict) else None
    if not isinstance(entries, dict) or not entries:
        return [f"{client}: JSON snippet has no mcpServers entries"]

    expected = {**JSON_ENTRY_KEYS[client], "url": server_url}
    return [
        f"{client}: entry {name!r} is {entry!r}, expected {expected!r}"
        for name, entry in entries.items()
        if entry != expected
    ]


def check_claude_code_command(line: str, server_url: str) -> list[str]:
    words = shlex.split(line)
    positional = []
    options = {}
    rest = words[3:]  # after "claude mcp add"
    while rest:
        word = rest.pop(0)
        if word.startswith("-"):
            options[word] = rest.pop(0) if rest else ""
        else:
            positional.append(word)

    problems = []
    if options.get("--transport") != "http":
        problems.append(f"Claude Code: command must use --transport http: {line}")
    if options.get("--scope", "local") not in {"local", "project", "user"}:
        problems.append(f"Claude Code: unknown --scope in: {line}")
    if set(options) - {"--transport", "--scope"}:
        problems.append(f"Claude Code: command adds options a remote OAuth server doesn't need: {line}")
    if positional != ["pipsocket", server_url]:
        problems.append(f"Claude Code: command must add pipsocket at {server_url}: {line}")
    return problems


def main() -> int:
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    server_url = server["remotes"][0]["url"]
    readme = sections((ROOT / "README.md").read_text(encoding="utf-8"))

    problems = []
    checked = 0
    for client in JSON_ENTRY_KEYS:
        if client not in readme:
            problems.append(f"README.md has no '### {client}' section")
            continue
        blocks = CODE_BLOCK.findall(readme[client])
        json_blocks = [body for language, body in blocks if language == "json"]
        if not json_blocks:
            problems.append(f"{client}: no JSON snippet")
        for body in json_blocks:
            problems += check_json(client, body, server_url)
            checked += 1

    commands = [
        line.strip()
        for language, body in CODE_BLOCK.findall(readme.get("Claude Code", ""))
        if language == "sh"
        for line in body.splitlines()
        if line.strip().startswith("claude mcp add")
    ]
    if not commands:
        problems.append("Claude Code: no 'claude mcp add' command")
    for command in commands:
        problems += check_claude_code_command(command, server_url)
        checked += 1

    for problem in problems:
        print(problem, file=sys.stderr)
    if not problems:
        print(f"{checked} setup snippets are valid and point at {server_url}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
