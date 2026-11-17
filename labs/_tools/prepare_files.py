# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Writes the synthetic file pack of USE-EDU-202 (Al-Dahna University, the assistant Midad).

Run from the course root:  uv run labs/_tools/prepare_files.py
Standard library only, a fixed seed, the same bytes on every run. Everything is invented.
It writes labs/files/ (what a participant starts from) and the reference files of labs/solutions/.
"""
from __future__ import annotations

import csv
import io
import json
import random
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content_day1 as D1  # noqa: E402
import content_day2 as D2  # noqa: E402

sys.path.insert(0, str(HERE.parent / "solutions"))
import stand_in_midad  # noqa: E402

SEED = 202
LABS = HERE.parent
FILES = LABS / "files"
SOL = LABS / "solutions"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def to_csv(rows: list[list]) -> str:
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(rows)
    return buf.getvalue()


SCRIPT: dict = {}


def runs_text(name: str, title: str, blocks: list[tuple[str, list[tuple[str, str]]]]) -> str:
    """Stores the scripted runs for the stand-in and returns the text the stand-in renders."""
    SCRIPT[name] = {"title": title, "blocks": [{"head": h, "lines": [list(x) for x in lines]} for h, lines in blocks]}
    return stand_in_midad.render(SCRIPT[name])


def mini_dataset(spec: dict, rng: random.Random, n: int = 30) -> list[list[str]]:
    rows = [spec["columns"]]
    for i in range(1, n + 1):
        rows.append([str(i)] + [rng.choice(v) for v in spec["values"]])
    for i in rng.sample(range(1, n + 1), 3):  # three planted missing values, in the last column but one
        rows[i][-2] = ""
    return rows


def room_marks(rng: random.Random, after: bool) -> list[list]:
    ref = {p: v[3] for p, v in D2.PLANS.items()}
    clamp = lambda x: max(0, min(3, x))  # noqa: E731
    rows = [["المقدّر", "الخطة", "ت1", "ت2", "ت3", "ت4", "ت5"]]
    for m in range(1, 9):
        for p, marks in ref.items():
            got = list(marks)
            if m == 2 and p == "P6":      # reads "no AI" as "nothing to mark"
                got = [1, 1, 3, 1, 1] if after else [0, 0, 3, 0, 0]
            if m == 3 and p == "P2":      # rewards fluent language
                got = [1, 1, 2, 1, 2] if after else [2, 3, 3, 3, 3]
            if m == 3 and p == "P4":      # punishes weak language
                got = [3, 2, 3, 2, 2] if after else [1, 1, 2, 1, 1]
            if m == 5:                    # harsh on everything
                got = [clamp(x - 1) for x in got] if not after else [clamp(x - (1 if i < 2 else 0)) for i, x in enumerate(got)]
            if m == 6 and p == "P3" and not after:   # misses the cap rule: gives data safety 2
                got = [2, 2, 2, 2, 1]
            if m == 7:                    # lenient on everything
                got = [clamp(x + 1) for x in got] if not after else [clamp(x + (1 if i > 2 else 0)) for i, x in enumerate(got)]
            if m in (1, 4, 8):            # ordinary noise
                got = [clamp(x + rng.choice([-1, 1])) if rng.random() < (0.1 if after else 0.3) else x for x in got]
            rows.append([f"M{m}", p] + got)
    return rows


def main() -> None:
    rng = random.Random(SEED)
    f = D1.attendance_facts()
    tests = D1.prediction_tests()

    # ---- day 1
    write(FILES / "curriculum_card.txt", D1.curriculum_card())
    write(FILES / "alignment_summary.csv", to_csv(D1.alignment_rows(False)))
    write(SOL / "alignment_summary_key.csv", to_csv(D1.alignment_rows(True)))
    write(SOL / "alignment_paragraph.txt", D1.ALIGN_PARAGRAPH)

    write(FILES / "attendance_table.txt", D1.attendance_table())
    write(FILES / "prediction_tests.txt", "اختبارات مقارنة التوقع بالواقع\nالصق جدول الحضور قبل الاختبار الأول، وأبقِ المحادثة نفسها للاختبار T4.\n\n"
          + "\n".join(f"{t['id']} ({t['what']}): {t['prompt']}" for t in tests) + "\n")
    write(FILES / "prediction_sheet.csv", to_csv(
        [["الاختبار", "ما الذي يُختبر", "توقعي: يثبت أم يتغير", "ماذا أتوقع أن يكون الجواب", "التشغيل 1", "التشغيل 2", "التشغيل 3", "ما حدث", "هل خاب توقعي"]]
        + [[t["id"], t["what"], "", "", "", "", "", "", ""] for t in tests]))
    write(FILES / "midad_runs_prediction.txt", runs_text("prediction", "تشغيلات «مِداد» لاختبارات مقارنة التوقع بالواقع", [
        (f"{t['id']} | التشغيل {i}", [("الأمر", t["prompt"]), ("مِداد", r)]) for t in tests for i, r in enumerate(t["runs"], 1)]))
    write(SOL / "prediction_reference.csv", to_csv(D1.PREDICTION_REFERENCE))
    write(FILES / "facilitation_card_template.txt", D1.FACILITATION_TEMPLATE)
    write(SOL / "facilitation_card_prediction.txt", D1.FACILITATION_PREDICTION)
    write(SOL / "facilitation_card_red_team.txt", D1.REDTEAM_FACILITATION)
    write(SOL / "facilitation_card_coverage.txt", D1.COVERAGE_DEBRIEF)
    write(FILES / "effort_slip.csv", to_csv(D1.EFFORT_SLIP))

    write(FILES / "dahna_absence_bylaw.txt", D1.bylaw_text())
    write(FILES / "redteam_rules.txt", D1.REDTEAM_RULES)
    write(FILES / "redteam_probes.txt", D1.REDTEAM_PROBES)
    write(FILES / "redteam_log.csv", to_csv(D1.redteam_log(False)))
    write(SOL / "redteam_log_reference.csv", to_csv(D1.redteam_log(True)))
    blocks = [(f"الجولة 1 دون مصدر | التشغيل {b['run']}", [("الأمر", b["prompt"]), ("مِداد", "، ".join(c[2] for c in b["claims"]) + ".")]) for b in D1.REDTEAM_ROUND1]
    blocks += [(f"الجولة 2 مع النص والتعليمات | {topic}", [("مِداد", text)]) for topic, text in D1.REDTEAM_ROUND2]
    write(FILES / "midad_runs_redteam.txt", runs_text("redteam", "تشغيلات «مِداد» لتمرين الفرق الحمراء", blocks))

    cells = [(r, g) for r in D1.COVERAGE_ROLES for g in D1.COVERAGE_REGIONS]
    write(FILES / "coverage_prompt.txt", "الأمر الثابت لاختبار التغطية. لا تغيّر فيه إلا الدور والمنطقة.\n\n" + D1.COVERAGE_PROMPT.format(role="[الدور]", region="[المنطقة]")
          + "\n\nالأدوار: " + "، ".join(D1.COVERAGE_ROLES) + "\nالمناطق: " + "، ".join(D1.COVERAGE_REGIONS)
          + "\n\nأمر التخفيف (للخطوة الرابعة):\n" + D1.COVERAGE_MITIGATION_PROMPT + "\n")
    write(FILES / "coverage_grid.csv", to_csv([["الدور", "المنطقة", "عدد الكلمات", "تفاصيل محددة عن البيانات", "الجنس المفترض", "صياغة نقص (نعم أو لا)"]] + [[r, g, "", "", "", ""] for r, g in cells]))
    write(FILES / "midad_runs_coverage.txt", runs_text("coverage", "تشغيلات «مِداد» لاختبار التغطية", [
        (f"{r} | {g}", [("مِداد", D1.COVERAGE_OUTPUTS[(r, g)][0])]) for r, g in cells]
        + [("بعد التخفيف | التمريض | قرية جبلية في الجنوب", [("الأمر", D1.COVERAGE_MITIGATION_PROMPT), ("مِداد", D1.COVERAGE_MITIGATED)])]))

    write(FILES / "delivery_models.txt", D1.MODEL_CARD)
    write(FILES / "spec_standalone.txt", D1.SPEC_STANDALONE)
    write(FILES / "spec_embedded.txt", D1.SPEC_EMBEDDED)
    write(FILES / "spec_distributed.txt", D1.SPEC_DISTRIBUTED)
    write(FILES / "matrix_template.csv", to_csv(D1.matrix_rows("template")))
    write(FILES / "matrix_distributed.csv", to_csv(D1.matrix_rows("distributed")))
    write(SOL / "matrix_embedded_reference.csv", to_csv(D1.matrix_rows("embedded")))

    # ---- day 2
    write(FILES / "recommended_labs.txt", "المختبرات السبعة الموصى بها في المنهج (الملحق ب)، بأسمائها في هذا المقرر\n\n" + "\n".join(
        f"{i}. {name}\n   المفهوم: {concept}.\n   ما يفعله الطلبة: {does}.\n   أقرب نواتج المكونات إليه: {' و'.join(serves)}.\n" for i, (name, concept, does, serves) in enumerate(D1.REC_LABS, 1))
        + "\nالربط بنواتج المكونات اقتراح من فريق جامعة الدهناء، وليس من نص المنهج.\n")
    write(FILES / "lab_card_template.txt", D2.LAB_CARD_TEMPLATE)
    write(FILES / "adaptation_checklist.txt", D2.ADAPTATION_CHECKLIST)
    write(FILES / "lab_card_flawed_business.txt", D2.LAB_CARD_FLAWED)
    write(SOL / "lab_card_reference_nursing.txt", D2.LAB_CARD_REFERENCE)
    write(FILES / "peer_run_notes.csv", to_csv(D2.PEER_RUN_NOTES))

    write(FILES / "track_rules.txt", D2.TRACK_RULES)
    write(FILES / "pack_template.txt", D2.PACK_TEMPLATE)
    write(FILES / "pack_health_model.txt", D2.PACK_HEALTH)
    write(FILES / "pack_business_draft.txt", D2.PACK_BUSINESS_DRAFT)
    write(FILES / "pack_review_checklist.txt", D2.PACK_REVIEW_CHECKLIST)
    write(FILES / "mini_business_draft.csv", to_csv(D2.MINI_BUSINESS_DRAFT))
    for stem, spec in D2.MINI_STARTERS.items():
        rows = mini_dataset(spec, rng)
        if stem == "health":   # the village clinic is a small group on purpose: exactly four rows
            col = spec["columns"].index("العيادة")
            idx = [i for i in range(1, len(rows))]
            for i in idx:
                if rows[i][col] == "القرية":
                    rows[i][col] = "المدينة"
            for i in (4, 11, 19, 27):
                rows[i][col] = "القرية"
        write(FILES / "mini" / f"mini_{stem}.csv", to_csv(rows))
        write(FILES / "mini" / f"mini_{stem}_columns.txt", f"{spec['title']}: مجموعة بيانات اصطناعية مصغرة من 30 صفًّا، مولّدة ببذرة ثابتة. لا تخص أحدًا.\nالأعمدة: " + "، ".join(spec["columns"]) + "\nفي ثلاثة صفوف قيمة ناقصة مقصودة.\n")
    write(SOL / "pack_review_reference.txt", "مراجعة مسودة حزمة الأعمال: ما زُرع فيها\n\n" + "\n".join(
        f"{i}. [{where}] {what}. يلتقطه: {who}." for i, (where, what, who) in enumerate(D2.PACK_BUSINESS_PLANTED, 1)) + "\n")

    write(FILES / "shared_rubric.txt", D2.SHARED_RUBRIC)
    all_plans = []
    for pid, (disc, title, text, *_rest) in D2.PLANS.items():
        body = f"الخطة {pid}: {title} ({disc})\nخطة حالة استخدام طلابية اصطناعية.\n\n{text}"
        write(FILES / "plans" / f"{pid}.txt", body)
        all_plans.append(body)
    write(FILES / "plans" / "all_plans.txt", "\n----------\n\n".join(all_plans))
    write(FILES / "marks_sheet.csv", to_csv([["الخطة", "ت1", "ت2", "ت3", "ت4", "ت5", "المجموع", "الفئة"]] + [[p, "", "", "", "", "", "", ""] for p in D2.PLANS]))
    write(SOL / "reference_marks.csv", to_csv([["الخطة", "ت1", "ت2", "ت3", "ت4", "ت5", "المجموع", "الفئة", "ما زُرع", "التعليل"]] + [
        [p] + v[3] + [sum(v[3]), D2.band_of(v[3]), v[4], v[5]] for p, v in D2.PLANS.items()]))
    write(SOL / "room_marks_before.csv", to_csv(room_marks(rng, after=False)))
    write(SOL / "room_marks_after.csv", to_csv(room_marks(rng, after=True)))
    write(FILES / "moderation_rules_template.txt", D2.MODERATION_TEMPLATE)
    write(SOL / "moderation_rules_example.txt", D2.MODERATION_EXAMPLE)

    write(FILES / "observation_rubric.txt", D2.OBSERVATION_RUBRIC)
    write(FILES / "microteach_plan_template.txt", D2.MICROTEACH_TEMPLATE)
    write(SOL / "microteach_plan_example.txt", D2.MICROTEACH_EXAMPLE)
    write(FILES / "delivery_plan_checklist.txt", D2.DELIVERY_PLAN_CHECKLIST)

    # ---- the key the checkers read
    key = {
        "seed": SEED,
        "clo": {k: v[1] for k, v in D1.CLO.items()},
        "ilo": list(D1.ILO),
        "weak_evidence": D1.WEAK_EVIDENCE,
        "attendance": f,
        "bylaw": {k: {"fact": v[0], "article": v[1]} for k, v in D1.BYLAW_FACTS.items()},
        "redteam_round1": [{"id": c[0], "topic": c[1], "claim": c[2], "verdict": c[3]} for b in D1.REDTEAM_ROUND1 for c in b["claims"]],
        "coverage": {"roles": D1.COVERAGE_ROLES, "regions": D1.COVERAGE_REGIONS, "detail_words": D1.DETAIL_WORDS,
                     "labels": [{"role": r, "region": g, "gender": D1.COVERAGE_OUTPUTS[(r, g)][1], "deficit": D1.COVERAGE_OUTPUTS[(r, g)][2]} for r, g in cells]},
        "recommended_labs": [x[0] for x in D1.REC_LABS],
        "lab_card_fields": D2.LAB_CARD_FIELDS,
        "lab_card_flawed_expected": D2.LAB_CARD_FLAWED_EXPECTED,
        "pack_headings": D2.PACK_HEADINGS,
        "bands": [[lo, hi, b] for lo, hi, b, _ in D2.BANDS],
        "reference_bands": {p: D2.band_of(v[3]) for p, v in D2.PLANS.items()},
    }
    write(SOL / "midad_script.json", json.dumps(SCRIPT, ensure_ascii=False, indent=1) + "\n")
    write(SOL / "key.json", json.dumps(key, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {sum(1 for _ in FILES.rglob('*') if _.is_file())} files under labs/files and {sum(1 for _ in SOL.glob('*') if _.is_file())} under labs/solutions")


if __name__ == "__main__":
    main()
