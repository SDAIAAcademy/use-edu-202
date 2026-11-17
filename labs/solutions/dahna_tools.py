# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""The trainer's checkers for the labs of USE-EDU-202. Standard library only.

  uv run labs/solutions/dahna_tools.py alignment <alignment_summary.csv>
  uv run labs/solutions/dahna_tools.py matrix <matrix.csv>
  uv run labs/solutions/dahna_tools.py card <lab_card.txt>
  uv run labs/solutions/dahna_tools.py pack <pack.txt> <mini.csv>
  uv run labs/solutions/dahna_tools.py coverage <midad_runs_coverage.txt>
  uv run labs/solutions/dahna_tools.py marks <marks_sheet.csv>
  uv run labs/solutions/dahna_tools.py room <room_marks.csv>

Each check is simple and readable on purpose. None replaces reading the participant's work.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY = json.loads((HERE / "key.json").read_text(encoding="utf-8"))


def read_csv(path) -> list[list[str]]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return [row for row in csv.reader(fh) if row]


def norm(answer: str) -> str:
    """Upper case, no spaces, Arabic comma as comma, the parts sorted: 'ilo6 ، ILO4' -> 'ILO4,ILO6'."""
    parts = [p for p in re.split(r"[,،;\s]+", answer.upper().strip()) if p]
    return ",".join(sorted(parts))


# ---------------------------------------------------------------- lab 1.1
def score_alignment(path) -> dict:
    key = {r[0]: r[2] for r in read_csv(HERE / "alignment_summary_key.csv")[1:]}
    got = {r[0]: (r[2] if len(r) > 2 else "") for r in read_csv(path)[1:]}
    wrong = [item for item, answer in key.items() if norm(got.get(item, "")) != norm(answer)]
    return {"points": len(key) - len(wrong), "total": len(key), "wrong": wrong}


# ---------------------------------------------------------------- lab 1.5
def check_matrix(path) -> dict:
    rows = {r[0]: (r + [""] * 6)[:6] for r in read_csv(path)[1:]}
    out = {"uncovered": [], "unassessed": [], "weak_evidence": [], "partial_reach": [], "missing_rows": []}
    sound = set()
    for code in KEY["clo"]:
        if code not in rows:
            out["missing_rows"].append(code)
            continue
        _, _, where, who, _activity, evidence = (c.strip() for c in rows[code])
        if not where:
            out["uncovered"].append(code)
            continue
        if not evidence:
            out["unassessed"].append(code)
        elif any(evidence.startswith(w) for w in KEY["weak_evidence"]):
            out["weak_evidence"].append(code)
        if who and who != "الجميع":
            out["partial_reach"].append(code)
        if evidence and not any(evidence.startswith(w) for w in KEY["weak_evidence"]) and who in ("", "الجميع"):
            sound.add(code)
    # an intended outcome holds when at least one of its component outcomes is taught to all and assessed
    out["ilo_sound_outcomes"] = {ilo: sorted(c for c in sound if ilo in KEY["clo"][c]) for ilo in KEY["ilo"]}
    out["complete"] = not any(out[k] for k in ("uncovered", "unassessed", "weak_evidence", "partial_reach", "missing_rows"))
    return out


# ---------------------------------------------------------------- lab 2.1
STEP = re.compile(r"^\[(طالب|مدرّس)\].*\((\d+)\s*د\)\s*$")
PERSONAL_NUMBER = re.compile(r"(?<!\d)\d{10}(?!\d)")


def parse_card(path) -> tuple[dict, list[tuple[str, int]]]:
    fields, steps, current = {}, [], None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        m = STEP.match(line)
        if m:
            steps.append((m.group(1), int(m.group(2))))
            continue
        name, sep, value = line.partition(":")
        if sep and name.strip() in KEY["lab_card_fields"]:
            current = name.strip()
            fields[current] = value.strip()
        elif current and line and current != "الخطوات":
            fields[current] += " " + line
    return fields, steps


def check_card(path) -> list[int]:
    """The numbers of the checks of adaptation_checklist.txt that fail."""
    fields, steps = parse_card(path)
    text = Path(path).read_text(encoding="utf-8")
    fail = []
    needed = [f for f in KEY["lab_card_fields"] if f not in ("خطوة البيانات", "قاعدة الإفصاح", "الخطوات")]
    if any(not fields.get(f) for f in needed) or not steps:
        fail.append(1)
    if fields.get("المختبر الأصلي") not in KEY["recommended_labs"]:
        fail.append(2)
    if fields.get("ناتج المكوّن") not in KEY["clo"]:
        fail.append(3)
    if not fields.get("البيانات", "").startswith(("اصطناعية", "عامة")):
        fail.append(4)
    if PERSONAL_NUMBER.search(text):
        fail.append(5)
    if not fields.get("خطوة البيانات"):
        fail.append(6)
    if not fields.get("قاعدة الإفصاح"):
        fail.append(7)
    check = fields.get("التحقق", "")
    if not check or check.startswith(("المدرّس", "المدرس", "عضو هيئة التدريس")):
        fail.append(8)
    total = sum(m for _, m in steps)
    stated = re.search(r"\d+", fields.get("المدة", ""))
    if not stated or total != int(stated.group()):
        fail.append(9)
    if not total or sum(m for who, m in steps if who == "طالب") / total < 0.6:
        fail.append(10)
    return fail


def hands_on_share(path) -> float:
    _, steps = parse_card(path)
    total = sum(m for _, m in steps)
    return round(sum(m for who, m in steps if who == "طالب") / total * 100) if total else 0.0


# ---------------------------------------------------------------- lab 2.2
PERSONAL_COLUMNS = ("اسم", "هوية", "جوال", "هاتف", "بريد", "عنوان")


def check_pack(pack_path, mini_path) -> list[str]:
    text = Path(pack_path).read_text(encoding="utf-8")
    sections, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = ""
        elif current:
            sections[current] += line + "\n"
    findings = [f"عنوان غائب أو فارغ: {h}" for h in KEY["pack_headings"] if not sections.get(h, "").strip()]
    if "اصطناعية" not in sections.get("البيانات", ""):
        findings.append("وصف البيانات لا يقول إنها اصطناعية")
    rows = read_csv(mini_path)
    n = len(rows) - 1
    if not 20 <= n <= 60:
        findings.append(f"عدد الصفوف {n}، والمطلوب من 20 إلى 60")
    personal = [c for c in rows[0] if any(p in c for p in PERSONAL_COLUMNS)]
    numbers = any(PERSONAL_NUMBER.fullmatch(cell.strip()) for row in rows[1:] for cell in row)
    if personal or numbers:
        findings.append("أعمدة أو قيم تشبه البيانات الشخصية: " + "، ".join(personal or ["أرقام من عشر خانات"]))
    return findings


# ---------------------------------------------------------------- lab 1.4
FEMALE = ("ممرضة", "محامية", "سارة", "نورة", "منيرة")
MALE = ("مهندس ", "محامٍ", "فهد", "خالد", "عبدالله")
DEFICIT = ("رغم محدودية", "نائية", "بسيطة")


def measure_coverage(path) -> dict:
    cells, head = [], None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("== "):
            head = [p.strip() for p in line.strip("= ").split("|")]
        elif line.startswith("مِداد:") and head:
            text = line.split(":", 1)[1].strip()
            gender = "أنثى" if any(w in text for w in FEMALE) else "ذكر" if any(w in text for w in MALE) else "غير محدد"
            cells.append({
                "mitigated": head[0].startswith("بعد التخفيف"),
                "role": head[-2], "region": head[-1],
                "words": len(text.split()),
                "details": sum(1 for w in KEY["coverage"]["detail_words"] if w in text),
                "gender": gender,
                "deficit": any(w in text for w in DEFICIT),
            })
    base = [c for c in cells if not c["mitigated"]]
    by_region = {g: round(sum(c["words"] for c in base if c["region"] == g) / 3) for g in KEY["coverage"]["regions"]}
    return {
        "cells": base,
        "mitigated": [c for c in cells if c["mitigated"]],
        "mean_words_by_region": by_region,
        "details_by_region": {g: sum(c["details"] for c in base if c["region"] == g) for g in KEY["coverage"]["regions"]},
        "gender_by_role": {r: [c["gender"] for c in base if c["role"] == r] for r in KEY["coverage"]["roles"]},
        "deficit_cells": [(c["role"], c["region"]) for c in base if c["deficit"]],
    }


# ---------------------------------------------------------------- lab 2.3
def band_of(marks: list[int]) -> int:
    total = sum(marks)
    band = next(b for lo, hi, b in KEY["bands"] if lo <= total <= hi)
    return min(band, 2) if marks[2] == 0 else band      # the cap rule: no data safety, no band above 2


def score_marks(path) -> dict:
    """One participant's sheet against the reference: LO4 asks for five plans within one band."""
    ref = KEY["reference_bands"]
    out = {"plans": {}, "within_one": 0}
    for row in read_csv(path)[1:]:
        plan = row[0]
        marks = [int(x) for x in row[1:6] if x.strip() != ""]
        if plan not in ref or len(marks) != 5:
            continue
        band = band_of(marks)
        out["plans"][plan] = {"band": band, "reference": ref[plan], "distance": abs(band - ref[plan])}
        out["within_one"] += abs(band - ref[plan]) <= 1
    out["meets_lo4"] = out["within_one"] >= 5
    return out


def room_report(path) -> dict:
    ref = KEY["reference_bands"]
    bands: dict[str, dict[str, int]] = {}
    for row in read_csv(path)[1:]:
        bands.setdefault(row[0], {})[row[1]] = band_of([int(x) for x in row[2:7]])
    per_plan = {p: {"min": min(m[p] for m in bands.values()), "max": max(m[p] for m in bands.values()), "reference": ref[p],
                    "exact": sum(m[p] == ref[p] for m in bands.values())} for p in ref}
    within = {m: sum(abs(b[p] - ref[p]) <= 1 for p in ref) for m, b in bands.items()}
    cells = len(bands) * len(ref)
    return {
        "per_plan": per_plan,
        "within_one_by_marker": within,
        "markers_meeting_lo4": sum(v >= 5 for v in within.values()),
        "markers": len(bands),
        "exact_agreement_percent": round(sum(v["exact"] for v in per_plan.values()) / cells * 100),
        "widest_plan": max(per_plan, key=lambda p: per_plan[p]["max"] - per_plan[p]["min"]),
    }


COMMANDS = {"alignment": score_alignment, "matrix": check_matrix, "card": check_card, "pack": check_pack,
            "coverage": measure_coverage, "marks": score_marks, "room": room_report}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3 or sys.argv[1] not in COMMANDS:
        raise SystemExit(__doc__)
    print(json.dumps(COMMANDS[sys.argv[1]](*sys.argv[2:]), ensure_ascii=False, indent=2))
