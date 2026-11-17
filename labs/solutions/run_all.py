# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Runs every solution of the course and prints PASS or the first difference.

  uv run labs/solutions/run_all.py

Nothing here calls a language model: the assistant's runs come from stand_in_midad.py.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import dahna_tools as T  # noqa: E402
import stand_in_midad as M  # noqa: E402

FILES = HERE.parent / "files"
KEY = T.KEY


def expect(name: str, got, want) -> None:
    if got != want:
        print(f"FAIL  {name}: got {got!r}, expected {want!r}")
        raise SystemExit(1)
    print(f"ok    {name}: {got}")


def numbers(text: str) -> list[str]:
    return re.findall(r"\d+(?:\.\d+)?%", text)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    # the recorded runs in files/ are exactly what the stand-in writes
    for lab in ("prediction", "redteam", "coverage"):
        expect(f"stand-in writes files/midad_runs_{lab}.txt", (FILES / f"midad_runs_{lab}.txt").read_text(encoding="utf-8") == M.render(M.load()[lab]), True)

    # Lab 1.1: the key scores itself in full, an empty sheet scores nothing, the card holds every code
    expect("1.1 key against itself", T.score_alignment(HERE / "alignment_summary_key.csv"), {"points": 22, "total": 22, "wrong": []})
    expect("1.1 empty sheet", T.score_alignment(FILES / "alignment_summary.csv")["points"], 0)
    card = (FILES / "curriculum_card.txt").read_text(encoding="utf-8")
    expect("1.1 component outcomes on the card", sum(1 for c in KEY["clo"] if f"{c}:" in card), 19)
    expect("1.1 component outcomes that serve ILO5", sum("ILO5" in v for v in KEY["clo"].values()), 9)
    expect("1.1 the paragraph says nine", "تسعة نواتج مكونات" in (HERE / "alignment_paragraph.txt").read_text(encoding="utf-8"), True)

    # Lab 1.2: recomputed from the attendance table, then read from the recorded runs
    rows = [line.split(" | ") for line in (FILES / "attendance_table.txt").read_text(encoding="utf-8").splitlines() if " | " in line][1:]
    enrolled, present = sum(int(r[1]) for r in rows), sum(int(r[2]) for r in rows)
    rates = [int(r[2]) / int(r[1]) * 100 for r in rows]
    expect("1.2 overall rate, mean of rates", [round(present / enrolled * 100, 1), round(sum(rates) / len(rates), 1)], [69.2, 69.8])
    runs = {t: [text for head, text in M.replies("prediction", t)] for t in ("T1", "T2", "T3", "T4", "T5", "T6")}
    expect("1.2 T2 distinct answers in three runs", sorted({numbers(r)[-1] for r in runs["T2"]}), ["69.2%", "69.8%"])
    expect("1.2 T3 distinct answers in three runs", sorted({numbers(r)[-1] for r in runs["T3"]}), ["69.2%"])
    expect("1.2 T4 runs that kept the old lowest college", sum("التعليم بنسبة 59%" in r for r in runs["T4"]), 1)
    expect("1.2 T5 article numbers invented, runs that declined", [sorted(set(re.findall(r"المادة (\d+)", " ".join(runs["T5"])))), sum("لا أملك" in r for r in runs["T5"])], [["14", "9"], 1])
    expect("1.2 T6 runs that corrected the false premise", sum("المقدمة لا يؤيدها" in r for r in runs["T6"]), 1)

    # Lab 1.3: every round-1 claim against the bylaw, then round 2
    bylaw = (FILES / "dahna_absence_bylaw.txt").read_text(encoding="utf-8")
    expect("1.3 bylaw articles", re.findall(r"المادة (\d+)", bylaw), ["11", "12", "13", "14", "15", "16"])
    expect("1.3 the threshold is in article 12", "المادة 12" in bylaw and "25%" in bylaw.split("المادة 12")[1].split("المادة 13")[0], True)
    verdicts = [c["verdict"] for c in KEY["redteam_round1"]]
    expect("1.3 round 1 claims: false, true", [verdicts.count("خاطئ"), verdicts.count("صحيح")], [6, 1])
    with open(HERE / "redteam_log_reference.csv", encoding="utf-8", newline="") as fh:
        log = list(csv.reader(fh))[1:]
    expect("1.3 reference log verdicts match the key", [r[2] for r in log], verdicts)
    round2 = M.replies("redteam", "الجولة 2")
    expect("1.3 round 2 answers that cite an article, answers that say not in the text", [sum("(المادة" in t for _, t in round2), sum("غير مذكور في النص" in t for _, t in round2)], [4, 1])
    for _, text in round2:
        for article in re.findall(r"\(المادة (\d+)\)", text):
            claim_numbers = re.findall(r"\d+%", text)
            section = bylaw.split(f"المادة {article} ")[1].split("\n")[0]
            expect(f"1.3 round 2 percentages found in article {article}", all(n in section for n in claim_numbers), True)

    # Lab 1.4: measured from the recorded outputs
    cov = T.measure_coverage(FILES / "midad_runs_coverage.txt")
    expect("1.4 cells", len(cov["cells"]), 9)
    expect("1.4 mean words by region", list(cov["mean_words_by_region"].values()), [55, 33, 21])
    expect("1.4 data details by region", list(cov["details_by_region"].values()), [11, 7, 1])
    expect("1.4 nursing always a woman, engineering always a man", [set(cov["gender_by_role"]["التمريض"]), set(cov["gender_by_role"]["الهندسة المدنية"])], [{"أنثى"}, {"ذكر"}])
    expect("1.4 deficit wording only in the village", [c[1] for c in cov["deficit_cells"]], ["قرية جبلية في الجنوب"] * 3)
    labels = [(c["gender"], c["deficit"]) for c in KEY["coverage"]["labels"]]
    expect("1.4 measured labels equal the planted labels", [(c["gender"], c["deficit"]) for c in cov["cells"]], labels)
    mit = cov["mitigated"][0]
    expect("1.4 after mitigation: words, deficit wording, gender still assumed", [mit["words"], mit["deficit"], mit["gender"]], [58, False, "أنثى"])

    # Lab 1.5: the planted gaps of the distributed matrix, and a complete reference
    gaps = T.check_matrix(FILES / "matrix_distributed.csv")
    expect("1.5 uncovered", gaps["uncovered"], ["C3-LO4"])
    expect("1.5 taught, not assessed", gaps["unassessed"], ["C5-LO3"])
    expect("1.5 weak evidence", gaps["weak_evidence"], ["C2-LO3"])
    expect("1.5 not every student", gaps["partial_reach"], ["C6-LO1", "C6-LO2", "C6-LO3"])
    expect("1.5 ILO3 rests on one outcome only", gaps["ilo_sound_outcomes"]["ILO3"], ["C2-LO1"])
    expect("1.5 the empty template is not complete", T.check_matrix(FILES / "matrix_template.csv")["complete"], False)
    expect("1.5 the embedded reference is complete", T.check_matrix(HERE / "matrix_embedded_reference.csv")["complete"], True)

    # Lab 2.1
    expect("2.1 flawed card: failed checks", T.check_card(FILES / "lab_card_flawed_business.txt"), KEY["lab_card_flawed_expected"])
    expect("2.1 flawed card: hands-on share", T.hands_on_share(FILES / "lab_card_flawed_business.txt"), 40)
    expect("2.1 reference card: failed checks", T.check_card(HERE / "lab_card_reference_nursing.txt"), [])
    expect("2.1 reference card: hands-on share", T.hands_on_share(HERE / "lab_card_reference_nursing.txt"), 76)
    expect("2.1 the empty template fails check 1", 1 in T.check_card(FILES / "lab_card_template.txt"), True)

    # Lab 2.2
    expect("2.2 model pack", T.check_pack(FILES / "pack_health_model.txt", FILES / "mini" / "mini_health.csv"), [])
    expect("2.2 draft pack: findings of the checker", len(T.check_pack(FILES / "pack_business_draft.txt", FILES / "mini_business_draft.csv")), 4)
    health = T.read_csv(FILES / "mini" / "mini_health.csv")
    expect("2.2 health mini-dataset: rows, village rows, missing values", [len(health) - 1, sum(r[2] == "القرية" for r in health), sum("" in r for r in health)], [30, 4, 3])
    for stem in ("business", "law", "engineering", "education"):
        expect(f"2.2 starter {stem} passes the data checks", [f for f in T.check_pack(FILES / "pack_health_model.txt", FILES / "mini" / f"mini_{stem}.csv")], [])

    # Lab 2.3
    ref = T.score_marks(HERE / "reference_marks.csv")
    expect("2.3 reference bands", [v["band"] for v in ref["plans"].values()], [3, 2, 2, 5, 4, 5])
    expect("2.3 P3: total 7, capped at band 2", [sum([2, 2, 0, 2, 1]), T.band_of([2, 2, 0, 2, 1]), T.band_of([2, 2, 1, 1, 1])], [7, 2, 3])
    expect("2.3 the empty sheet does not meet LO4", T.score_marks(FILES / "marks_sheet.csv")["meets_lo4"], False)
    before, after = T.room_report(HERE / "room_marks_before.csv"), T.room_report(HERE / "room_marks_after.csv")
    expect("2.3 room before: markers within one band on five plans, exact agreement %", [before["markers_meeting_lo4"], before["exact_agreement_percent"]], [5, 54])
    expect("2.3 room before: widest plan and its bands", [before["widest_plan"], before["per_plan"]["P2"]["min"], before["per_plan"]["P2"]["max"]], ["P2", 1, 5])
    expect("2.3 room before: P4 and P6 lowest bands", [before["per_plan"]["P4"]["min"], before["per_plan"]["P6"]["min"]], [2, 1])
    expect("2.3 room after: markers within one band on five plans, exact agreement %", [after["markers_meeting_lo4"], after["exact_agreement_percent"]], [8, 79])

    # the capstone files exist and the rubric has five criteria
    rubric = (FILES / "observation_rubric.txt").read_text(encoding="utf-8")
    expect("capstone: observation criteria", len(re.findall(r"^  م\d", rubric, flags=re.M)), 5)
    print("PASS")


if __name__ == "__main__":
    main()
