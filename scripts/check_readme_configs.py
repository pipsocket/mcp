"""Check that the README's JSON config snippets parse and point at the server in server.json."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_BLOCK = re.compile(r"^```json\n(.*?)^```", re.MULTILINE | re.DOTALL)


def main() -> int:
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    server_url = server["remotes"][0]["url"]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    problems = []
    blocks = JSON_BLOCK.findall(readme)
    if not blocks:
        problems.append("README.md has no JSON config snippets")

    for number, block in enumerate(blocks, start=1):
        try:
            config = json.loads(block)
        except json.JSONDecodeError as error:
            problems.append(f"snippet {number} is not valid JSON: {error}")
            continue
        entries = config.get("mcpServers", {})
        if not entries:
            problems.append(f"snippet {number} has no mcpServers entries")
        for name, entry in entries.items():
            if entry.get("url") != server_url:
                problems.append(f"snippet {number}, {name}: url is {entry.get('url')!r}, not {server_url!r}")

    for problem in problems:
        print(problem, file=sys.stderr)
    if not problems:
        print(f"{len(blocks)} JSON snippets are valid and point at {server_url}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
