# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 Phase B: 日本国内の権利スクリーニング(決定論・LLM不使用・Trial専用)。

ルール正本: Z-1(DECISION_LOG.md 9638行付近、CURRENT_SPEC.md Family Z Seed必須条件(b))
  - 日本国内でPD、または日本国内で適法に利用可能であること(必須)
  - 米国PDは必須条件にしない。かつ「米国PD」を日本の利用条件(PASS根拠)に置き換えない
    (本scriptは米国statusを記録欄にのみ書き、判定に一切使わない)
  - 原作がPDでも第三者の翻訳・英訳は別著作物として扱い、権利未確認なら流用しない
  - 判定不能・未確認はREVIEW_REQUIRED(推測でPASSしない)
Production(er026等)から参照されない。実行: python -I er054_family_z_story_pool_rights_screen_trial_01.py [基準日YYYY-MM-DD]
"""
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, "er054_output", "family_z_story_pool_trial_01")
SRC = os.path.join(BASE, "sources")
OUTD = os.path.join(BASE, "screening")
WARTIME_DAYS = 3794  # 連合国民の戦時加算(1941-12-08前に取得された著作権、英米等)。出典: en.wikipedia Copyright_law_of_Japan
AMEND_DATE = dt.date(2018, 12, 30)  # 没後70年化(TPP11整備法)施行日。切れていた作品には非遡及
BORDERLINE_DAYS = 730  # 戦時加算込みの50年満了が改正日の2年以内なら専門家確認(REVIEW_REQUIRED)


def read(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8", "replace")


def strip(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))


def jp_term(death_year, wartime_applied, today):
    """日本の保護期間満了日を計算する。"""
    add = dt.timedelta(days=WARTIME_DAYS if wartime_applied else 0)
    exp50 = dt.date(death_year + 50, 12, 31) + add
    if exp50 < AMEND_DATE:
        expiry = exp50
        regime = "没後50年(旧法)で2018-12-30前に満了済み。2018年の70年化は非遡及のためPD確定"
    else:
        expiry = dt.date(death_year + 70, 12, 31) + add
        regime = "没後50年満了が2018-12-30以後のため、没後70年(2018改正)が適用される"
    borderline = bool(wartime_applied and exp50 < AMEND_DATE and (AMEND_DATE - exp50).days < BORDERLINE_DAYS)
    return {"death_year": death_year, "wartime_applied": wartime_applied,
            "expiry_50y_incl_wartime": exp50.isoformat(), "expiry_used": expiry.isoformat(), "regime": regime,
            "pd_as_of_today": expiry < today, "borderline_wartime_near_2018_boundary": borderline,
            "days_before_2018_boundary": (AMEND_DATE - exp50).days if exp50 < AMEND_DATE else None}


def judge_subject(name, death_year, group, today):
    """1権利者(原著者/訳者)の日本国内状態: PD / PROTECTED / REVIEW。
    allied_3794は保守的に戦時加算を適用。JPは加算なし。それ以外は加算あり/なし両方を計算し結論が割れたらREVIEW。"""
    base = {"subject": name, "group": group}
    if group == "allied_3794":
        t = jp_term(death_year, True, today)
        base["calc"] = t
        status = "REVIEW" if t["borderline_wartime_near_2018_boundary"] else ("PD" if t["pd_as_of_today"] else "PROTECTED")
    elif group == "JP":
        t = jp_term(death_year, False, today)
        base["calc"] = t
        status = "PD" if t["pd_as_of_today"] else "PROTECTED"
    else:
        t0, t1 = jp_term(death_year, False, today), jp_term(death_year, True, today)
        base["calc"] = t0
        base["calc_with_wartime_sensitivity"] = t1
        if t0["pd_as_of_today"] and t1["pd_as_of_today"] and not t1["borderline_wartime_near_2018_boundary"]:
            status = "PD"
        elif (not t0["pd_as_of_today"]) and (not t1["pd_as_of_today"]):
            status = "PROTECTED"
        else:
            status = "REVIEW"
    base["status"] = status
    return base


def parse_card(wid, kind):
    p = os.path.join(SRC, wid, "card.html")
    if not os.path.exists(p):
        return {}
    x = strip(read(p))
    c = {}
    if kind == "ja_original":
        m = re.search(r"没年： (\d{4})-", x)
        c["death_year_on_card"] = int(m.group(1)) if m else None
        m = re.search(r"生年： (\d{4})-", x)
        c["birth_year_on_card"] = int(m.group(1)) if m else None
        m = re.search(r"作品名： (\S+)", x)
        c["title_on_card"] = m.group(1) if m else None
        m = re.search(r"初出： (.{0,160}?) (?:作品について|文字遣い種別)", x)
        c["first_pub_on_card"] = m.group(1) if m else None
        m = re.search(r"底本： (.{0,80}?) 出版社： (.{0,40}?) 初版発行日： (.{0,60}?) ", x)
        c["teihon"] = " / ".join(m.groups()) if m else None
        m = re.search(r"入力： (.{0,30}?) 校正： (.{0,30}?) ファイル", x)
        c["input_proof"] = list(m.groups()) if m else None
        c["aozora_published"] = bool(c["death_year_on_card"])
    else:
        m = re.search(r"Copyright (.{0,50}?\.)", x)
        c["gutenberg_copyright_field"] = m.group(1) if m else None
        c["death_years_listed"] = sorted(set(int(y) for y in re.findall(r"\d{4}-(\d{4})", x)))
        c["author_translator_lines"] = re.findall(r"(?:Author|Translator|Contributor) ([^\d]{0,80}\d{4}-\d{4})", x)
    return c


def screen_one(wid, w, rules, today):
    man = json.load(open(os.path.join(SRC, wid, "fetch_manifest.json"), encoding="utf-8"))
    files = man["files"]
    text = next((f for f in files if f["role"] == "text"), {})
    card = next((f for f in files if f["role"] == "card"), {})
    fetch_ok = bool(text.get("ok")) and bool(card.get("ok"))
    cinfo = parse_card(wid, w["kind"])
    blocking, informational, reasons, checks = [], [], [], {}

    # --- 一次資料の取得可否(fail-closed)
    if not text.get("ok"):
        blocking.append("一次資料(本文)をHTTP取得できていない")
    if not card.get("ok"):
        blocking.append("図書カード/書誌ページをHTTP取得できていない")
    if w["kind"] == "ja_original" and text.get("ok") and not text.get("main_text_div_found"):
        blocking.append("青空文庫XHTMLの本文領域を抽出できていない")

    # --- 手入力データとカード照合
    au = w["author"]
    if w["kind"] == "ja_original":
        checks["death_year_matches_card"] = cinfo.get("death_year_on_card") == au["death_year"]
        checks["birth_year_matches_card"] = cinfo.get("birth_year_on_card") == au["birth_year"]
    else:
        checks["author_death_year_listed_on_gutenberg_card"] = au["death_year"] in cinfo.get("death_years_listed", [])
        for tr in w.get("translators", []):
            checks["translator_%s_death_year_listed" % tr["name"]] = tr["death_year"] in cinfo.get("death_years_listed", [])
    if not all(v for v in checks.values()):
        blocking.append("手入力の生没年が図書カード/Gutenbergメタデータと一致しない")

    # --- 初出の照合(情報。判定には使わない)
    fp = w["first_publication"]
    corro = None
    for f in files:
        if f["role"] == "aux" and f.get("ok") and "Copyright_law_of_Japan" not in f["url"]:
            t = strip(read(os.path.join(SRC, wid, f["saved_as"])))
            corro = {"aux_url": f["url"], "regex": fp["corroborate_regex"], "found": bool(re.search(fp["corroborate_regex"], t))}
    if corro is None and w["kind"] == "ja_original":
        corro = {"aux_url": card.get("url"), "regex": fp["corroborate_regex"],
                 "found": bool(re.search(fp["corroborate_regex"], cinfo.get("first_pub_on_card") or ""))}
    checks_extra = {"first_publication_corroborated": corro}
    if corro is None or not corro.get("found"):
        informational.append("初出情報(年)を出典で照合できていない(判定には使わない)")

    # --- 規則根拠の照合
    law = next((f for f in files if "Copyright_law_of_Japan" in f["url"]), None)
    phr = {}
    if law and law.get("ok"):
        lt = strip(read(os.path.join(SRC, wid, law["saved_as"])))
        phr = {p: (p in lt) for p in rules["jp_term_rule_phrases"]}
    checks_extra["jp_term_rule_phrases_found_in_fetched_source"] = phr
    if not phr or not all(phr.values()):
        blocking.append("日本の保護期間ルールの根拠資料(二次資料)で必要フレーズを確認できない")

    # --- 権利者別の日本国内状態
    subjects = [judge_subject(au["name"], au["death_year"], au["group"], today)]
    for tr in w.get("translators", []):
        subjects.append(judge_subject(tr["name"], tr["death_year"], tr["group"], today))
    author_status = subjects[0]["status"]
    trans_status = [s["status"] for s in subjects[1:]]

    # --- 米国status(記録のみ。判定に不使用)
    if w["kind"] == "ja_original":
        us_rec = "未確認(記録事項。Z-1により日本国内PD判定には使わない)"
    else:
        us_rec = "Gutenberg表示: %s(記録事項のみ。日本国内の利用条件へは置換しない)" % cinfo.get("gutenberg_copyright_field")

    # --- 総合判定
    decision = None
    if author_status == "PROTECTED":
        decision = "NG"
        reasons.append("原著者%s(没%s)は日本で保護期間中(満了%s)。米国PD等の他法域statusでは置換不可(Z-1)。"
                       % (au["name"], au["death_year"], subjects[0]["calc"]["expiry_used"]))
    elif "PROTECTED" in trans_status:
        decision = "NG"
        reasons.append("翻訳者の著作権が日本で存続(翻訳版は別著作物、Z-1(4))")
    else:
        if author_status == "REVIEW":
            blocking.append("原著者の保護期間が計算上REVIEW(戦時加算の境界)")
        if "REVIEW" in trans_status:
            days = min(s["calc"]["days_before_2018_boundary"] for s in subjects[1:] if s["status"] == "REVIEW")
            blocking.append("翻訳者の保護期間が計算上REVIEW(戦時加算込みの没後50年満了が2018-12-30の%d日前で境界に近く、"
                            "国籍・個別訳者・戦時加算の適用要否が未確認のため機械的にPDと確定できない)" % days)
        if blocking:
            decision = "REVIEW_REQUIRED"
            reasons.append("原著者%s(没%s)は日本でPD(計算上、満了%s)。ただし未確認/境界事項があり機械的にPASSできない: %s"
                           % (au["name"], au["death_year"], subjects[0]["calc"]["expiry_used"], "; ".join(blocking)))
        else:
            decision = "PASS"
            reasons.append("原著者%s(没%s)は日本でPD(満了%s。%s)。%s"
                           % (au["name"], au["death_year"], subjects[0]["calc"]["expiry_used"], subjects[0]["calc"]["regime"],
                              "翻訳者も日本でPD。" if w.get("translators") else "青空文庫が公開。翻訳・第三者著作物なし(日本語原作)。"))
    if decision == "NG" and w.get("ja_translation_note"):
        informational.append(w["ja_translation_note"])

    # --- 未確認一覧
    unconfirmed = [{"item": b, "blocking": True} for b in blocking] + [{"item": i, "blocking": False} for i in informational]
    unconfirmed.append({"item": "法律原文・文化庁資料による確認は未実施(二次資料に基づく機械判定)。法的最終判断ではなく弁護士確認が望ましい。", "blocking": False})
    unconfirmed.append({"item": "米国等の他法域status: " + us_rec, "blocking": False})
    if w["kind"] == "ja_original":
        unconfirmed.append({"item": "底本(出版社版)の校訂・注記等の第三者権利は個別確認していない(青空文庫は著作権消滅作品のみ公開する運用。Family Zは本文を自前adaptation)", "blocking": False})
    if wid == "L04":
        unconfirmed.append({"item": "『賭け』個別の訳者(Koteliansky/Murry/共訳)が本文・メタデータから特定できていない", "blocking": True})
        unconfirmed.append({"item": "Koteliansky/Murryの国籍(戦時加算の対象か)を一次確認できていない", "blocking": True})
    if wid == "L06":
        unconfirmed.append({"item": "日本語訳版の訳者・版・権利は本Trialで未特定(原著が日本で保護期間中のため判定がNGであることは変わらない)", "blocking": False})
        unconfirmed.append({"item": "同梱のMacy/Sullivan分の権利は個別判定していない(原著者がNGのため結論に影響しない)", "blocking": False})

    return {
        "work_id": wid, "title_ja": w["title_ja"], "title_en": w["title_en"], "genre": w["genre"], "kind": w["kind"],
        "screened_at": dt.datetime.now(dt.timezone.utc).isoformat(), "as_of_date": today.isoformat(),
        "author": {k: au[k] for k in ("name", "birth_year", "death_year", "source")},
        "first_publication": {"year": fp["year"], "text": fp["text"], "source": fp["source"]},
        "primary_source": {
            "card_url": card.get("url"), "text_url": text.get("url"), "fetch_ok": fetch_ok,
            "text_http_status": text.get("http_status"), "text_bytes": text.get("bytes"),
            "text_plain_chars": text.get("plain_chars"), "text_sha256_raw": text.get("sha256"),
            "text_sha256_plain": text.get("plain_sha256"), "text_fetched_at": text.get("fetched_at"),
            "fetch_attempts": text.get("attempts"),
            "saved_dir": "er054_output/family_z_story_pool_trial_01/sources/%s/" % wid,
            "card_parse": cinfo,
        },
        "edition_note": w["edition_note"],
        "work_vs_edition": {"original_work_status_jp": author_status,
                            "translation_status_jp": trans_status or ["n/a(日本語原作)"],
                            "translation_pub_year": w.get("translation_pub_year")},
        "rights_subjects": subjects,
        "z1_checks": {"us_pd_used_as_jp_basis": False, "us_status_record_only": us_rec,
                      "third_party_translation_treated_as_separate_work": w["kind"] != "ja_original",
                      "data_vs_card_checks": checks, "other_checks": checks_extra},
        "unconfirmed": unconfirmed,
        "decision": decision,
        "decision_reason": " ".join(reasons),
    }


def main():
    today = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 10, 11)
    data = json.load(open(os.path.join(BASE, "rights_data_01.json"), encoding="utf-8"))
    os.makedirs(OUTD, exist_ok=True)
    rows = []
    for wid, w in data["works"].items():
        o = screen_one(wid, w, data["rule_sources"], today)
        with open(os.path.join(OUTD, "%s.json" % wid), "w", encoding="utf-8") as f:
            json.dump(o, f, ensure_ascii=False, indent=2)
        rows.append(o)
        sys.stdout.buffer.write(("%s %s | %s\n" % (wid, o["decision"], o["decision_reason"][:150])).encode("utf-8"))
    l06 = next(r for r in rows if r["work_id"] == "L06")
    if l06["decision"] == "PASS":
        print("STOP: L06(既知の権利NG)がPASSになった。判定ロジック欠陥の疑い。", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
