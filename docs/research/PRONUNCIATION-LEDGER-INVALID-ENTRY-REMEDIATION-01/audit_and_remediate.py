"""PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01 S2/S3: 全entry分類(不正/疑義/正当)と是正。
使い方: .venv/Scripts/python.exe docs/research/.../audit_and_remediate.py [--apply]
--applyなし=分類のみ(読取専用)。--apply=不正entryをledger_disabledで隔離+melos hintの括弧別案除去(削除なし)。"""
import json, re, sys
sys.path.insert(0, ".")
import pronouncing
import er006_pronunciation_ledger_01 as L

OUT = "docs/research/PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01/audit_classification.json"
ledger = L._load()
rows = []
for lid, e in ledger.items():
    surf, et = e.get("surface", ""), e.get("entity_type", "")
    hint = e.get("pronunciation_hint", "") or ""
    reasons_invalid, reasons_doubt, fix = [], [], None
    r = L.entry_invalid_reason(surf, et, e)
    if r:
        reasons_invalid.append(r)
    if et == L.CASCADE_UNRESOLVED_ENTITY_TYPE and hint and L._clean_hint(hint) != hint:
        reasons_invalid.append(f"hint_has_parenthetical_alternative:{hint!r}")
        fix = "clean_hint"
    # 疑義(報告のみ)
    if et == L.CASCADE_UNRESOLVED_ENTITY_TYPE and len(surf.split()) == 1 and pronouncing.phones_for_word(surf.lower()):
        reasons_doubt.append("cascade自動登録の一般語(CMU収録)")
    if any(re.search(r"[（(]", a or "") for a in e.get("alternate_pronunciations", []) or []) :
        reasons_doubt.append("alternate_pronunciationsに括弧付き注記")
    if re.search(r"[぀-ヿ一-鿿]", hint):
        reasons_doubt.append("hintに日本語混入")
    if et != L.JA_READING_ENTITY_TYPE and not (e.get("sources") or []) :
        reasons_doubt.append("sources空")
    if not hint and et != L.JA_READING_ENTITY_TYPE:
        reasons_doubt.append("hint空")
    if et == L.JA_READING_ENTITY_TYPE and hint:
        reasons_doubt.append("ja_readingにEN hint(J7)")
    if e.get("tts_injection_disabled") and not reasons_invalid:
        reasons_doubt.append("tts_injection_disabled済(Phrase Listには供給継続)")
    cls = "不正(是正)" if reasons_invalid else ("疑義(報告のみ)" if reasons_doubt else "正当(維持)")
    rows.append({"ledger_id": lid, "surface": surf, "entity_type": et, "canonical_spelling": e.get("canonical_spelling"),
                 "confidence": e.get("confidence"), "class": cls, "invalid": reasons_invalid, "doubt": reasons_doubt,
                 "fix": fix or ("ledger_disabled" if any(not x.startswith("hint_has") for x in reasons_invalid) else None)})
json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in rows:
    print(r["class"], "|", r["ledger_id"], "|", r["surface"], "|", r["entity_type"][:7], "|", r["canonical_spelling"], "|",
          r["invalid"], r["doubt"], "|fix=", r["fix"])
if "--apply" in sys.argv:
    led = L._load()
    for r in rows:
        if r["class"] != "不正(是正)":
            continue
        e = led[r["ledger_id"]]
        dis = [x for x in r["invalid"] if not x.startswith("hint_has")]
        if dis:
            e["ledger_disabled"] = True
            e["ledger_disabled_reason"] = "PLIR1 2026-10-21: " + "; ".join(dis)
        if any(x.startswith("hint_has") for x in r["invalid"]):
            orig = e["pronunciation_hint"]
            e["pronunciation_hint"] = L._clean_hint(orig)
            e["ambiguity_note"] = (e.get("ambiguity_note", "") + " " if e.get("ambiguity_note") else "") + \
                f"[PLIR1 2026-10-21 hint原文(括弧別案混入のため先頭案のみ採用): {orig}]"
        e.setdefault("ledger_disabled", False)
        e.setdefault("ledger_disabled_reason", "")
    L._save(led)
    print("APPLIED")
