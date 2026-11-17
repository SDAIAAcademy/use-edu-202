# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""A scripted stand-in for the assistant Midad. It is not a language model.

It reads midad_script.json (the replies written for this course) and prints the recorded runs of
one lab, so the three labs run as students can be done and checked with no network and no key.

  uv run labs/solutions/stand_in_midad.py prediction
  uv run labs/solutions/stand_in_midad.py redteam
  uv run labs/solutions/stand_in_midad.py coverage
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTE = "تشغيلات مسجلة كتبها نموذج بديل مكتوب، لا نموذج لغوي. تُستخدم حين لا يتاح مساعد حي، وبها يُفحص الحل."


def render(lab: dict) -> str:
    out = [lab["title"], NOTE, ""]
    for block in lab["blocks"]:
        out.append(f"== {block['head']} ==")
        out += [f"{who}: {text}" for who, text in block["lines"]]
        out.append("")
    return "\n".join(out)


def load() -> dict:
    return json.loads((HERE / "midad_script.json").read_text(encoding="utf-8"))


def replies(name: str, head_starts: str = "") -> list[tuple[str, str]]:
    """(block head, Midad's reply) for every block of a lab whose head starts with head_starts."""
    out = []
    for block in load()[name]["blocks"]:
        if block["head"].startswith(head_starts):
            out += [(block["head"], text) for who, text in block["lines"] if who == "مِداد"]
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    script = load()
    if name not in script:
        raise SystemExit("usage: stand_in_midad.py " + "|".join(script))
    print(render(script[name]))
