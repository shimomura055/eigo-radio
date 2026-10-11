# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 Phase B: 日本国内の権利スクリーニング(決定論・LLM不使用・Trial専用)。

ルール正本: Z-1(DECISION_LOG.md 9638行付近、CURRENT_SPEC.md Family Z Seed必須条件(b))
  - 日本国内でPD、または日本国内で適法に利用可能であること(必須)
  - 米国PDは必須条件にしない。かつ「米国PD」を日本の利用条件(PASS根拠)に置き換えない
    (本scriptは米国statusを記録欄にのみ書き、判定に一切使わない)
  - 原作がPDでも第三者の翻訳・英訳は別著作物として扱い、権利未確認なら流用しない
  - 判定不能・未確認はREVIEW_REQUIRED(推測でPASSしない)
委任_03(原語原作ベース): 判定は「作品(原語原作)の権利 work_rights」を主とし、「利用した版/翻訳の権利 edition_rights」は参考情報
(記事化の前提条件にしない)。既存翻訳に権利問題があっても原語原作がPDなら作品をNGにしない。
委任_03(原語原作ベース): 判定は「作品(原語原作)の権利 work_rights」を主とし、「利用した版/翻訳の権利 edition_rights」は参考情報
(記事化の前提条件にしない)。既存翻訳に権利問題があっても原語原作がPDなら作品をNGにしない。
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


def parse_card(wid, kind, sdir=None):
    p = os.path.join(SRC, sdir or wid, "card.html")
    if kind == "original_ru":
        # ru.wikisource の wikitext ヘッダ(АВТОР/ДАТАПУБЛИКАЦИИ/ИСТОЧНИК/ЛИЦЕНЗИЯ)から抽出
        wt = os.path.join(SRC, sdir or wid, "wikisource_raw.wikitext")
        c = {}
        if os.path.exists(wt):
            x = read(wt)
            m = re.search(r"АВТОР\s*=\s*\[\[(.*?)\]\]\s*\((\d{4})[—-](\d{4})\)", x)
            c["author_on_page"] = m.group(1) if m else None
            c["birth_year_on_card"] = int(m.group(2)) if m else None
            c["death_year_on_card"] = int(m.group(3)) if m else None
            m = re.search(r"ДАТАПУБЛИКАЦИИ\s*=\s*(.*?)<ref>(.*?)</ref>", x, re.S)
            c["first_pub_on_card"] = re.sub(r"&nbsp;", " ", m.group(2)).strip() if m else None
            m = re.search(r"ИСТОЧНИК\s*=\s*(.*)", x)
            c["source_on_page"] = m.group(1).strip() if m else None
            m = re.search(r"ЛИЦЕНЗИЯ\s*=\s*(\S+)", x)
            c["license_tag_on_wikisource"] = m.group(1) if m else None
        return c
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
        m = re.search(r"文字遣い種別： (\S+)", x)
        c["moji_type"] = m.group(1) if m else None
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
    sdir = w.get("source_dir", wid)  # 原語原作の取得先(L04はL04_ru=ロシア語原作)
    man = json.load(open(os.path.join(SRC, sdir, "fetch_manifest.json"), encoding="utf-8"))
    files = man["files"]
    text = next((f for f in files if f["role"] == "text"), {})
    card = next((f for f in files if f["role"] == "card"), {})
    fetch_ok = bool(text.get("ok")) and bool(card.get("ok"))
    kind = w["kind"]
    cinfo = parse_card(wid, kind, sdir)
    blocking, informational, reasons, checks = [], [], [], {}

    # --- 一次資料(原語原作)の取得可否(fail-closed)
    if not text.get("ok"):
        blocking.append("一次資料(原語原作本文)をHTTP取得できていない")
    if not card.get("ok"):
        blocking.append("図書カード/書誌ページをHTTP取得できていない")
    if kind == "ja_original" and text.get("ok") and not text.get("main_text_div_found"):
        blocking.append("青空文庫XHTMLの本文領域を抽出できていない")

    # --- 手入力データとカード照合(原著者の生没年)
    au = w["author"]
    if kind in ("ja_original", "original_ru"):
        checks["death_year_matches_card"] = cinfo.get("death_year_on_card") == au["death_year"]
        checks["birth_year_matches_card"] = cinfo.get("birth_year_on_card") == au["birth_year"]
    else:
        checks["author_death_year_listed_on_gutenberg_card"] = au["death_year"] in cinfo.get("death_years_listed", [])
    if not all(v for v in checks.values()):
        blocking.append("手入力の生没年が図書カード/書誌メタデータと一致しない")

    # --- 初出の照合(情報。判定には使わない)
    fp = w["first_publication"]
    corro = None
    for f in files:
        if f["role"] == "aux" and f.get("ok") and "Copyright_law_of_Japan" not in f["url"]:
            t = strip(read(os.path.join(SRC, sdir, f["saved_as"])))
            corro = {"aux_url": f["url"], "regex": fp["corroborate_regex"], "found": bool(re.search(fp["corroborate_regex"], t))}
    if corro is None and kind in ("ja_original", "original_ru"):
        corro = {"aux_url": card.get("url"), "regex": fp["corroborate_regex"],
                 "found": bool(re.search(fp["corroborate_regex"], cinfo.get("first_pub_on_card") or ""))}
    checks_extra = {"first_publication_corroborated": corro}
    if corro is None or not corro.get("found"):
        informational.append("初出情報(年)を出典で照合できていない(判定には使わない)")

    # --- 規則根拠の照合
    law = next((f for f in files if "Copyright_law_of_Japan" in f["url"]), None)
    phr = {}
    if law and law.get("ok"):
        lt = strip(read(os.path.join(SRC, sdir, law["saved_as"])))
        phr = {p: (p in lt) for p in rules["jp_term_rule_phrases"]}
    checks_extra["jp_term_rule_phrases_found_in_fetched_source"] = phr
    if not phr or not all(phr.values()):
        blocking.append("日本の保護期間ルールの根拠資料(二次資料)で必要フレーズを確認できない")

    # --- work_rights: 原著者(原語原作)の日本国内状態のみで判定する
    au_subj = judge_subject(au["name"], au["death_year"], au["group"], today)
    author_status = au_subj["status"]

    # --- edition_rights: 利用した版/翻訳/参考翻訳の権利(参考情報。判定・記事化の前提条件にしない)
    ed_subjects = [judge_subject(t["name"], t["death_year"], t["group"], today) for t in w.get("reference_translations", [])]
    ed_status = [s["status"] for s in ed_subjects]

    # --- 米国status(記録のみ。判定に不使用)
    if kind == "original_en_foreign":
        us_rec = "Gutenberg表示: %s(記録事項のみ。日本国内の利用条件へは置換しない)" % cinfo.get("gutenberg_copyright_field")
    else:
        us_rec = "未確認(記録事項。Z-1により日本国内PD判定には使わない)"

    # --- 総合判定(work_rightsのみ)
    if author_status == "PROTECTED":
        decision = "NG"
        reasons.append("原著者%s(没%s)は日本で保護期間中(満了%s)。米国PD等の他法域statusでは置換不可(Z-1)。"
                       % (au["name"], au["death_year"], au_subj["calc"]["expiry_used"]))
    else:
        if author_status == "REVIEW":
            blocking.append("原著者の保護期間が計算上REVIEW(戦時加算の境界)")
        if blocking:
            decision = "REVIEW_REQUIRED"
            reasons.append("原著者%s(没%s)は日本でPD(計算上、満了%s)。ただし未確認/境界事項があり機械的にPASSできない: %s"
                           % (au["name"], au["death_year"], au_subj["calc"]["expiry_used"], "; ".join(blocking)))
        else:
            decision = "PASS"
            reasons.append("原語原作の著者%s(没%s)は日本でPD(満了%s。%s)。一次資料は原語原作(%s)。"
                           % (au["name"], au["death_year"], au_subj["calc"]["expiry_used"], au_subj["calc"]["regime"],
                              w["work_source"]["text_url_label"]))
    if decision == "NG" and w.get("ja_translation_note"):
        informational.append(w["ja_translation_note"])

    # --- 未確認一覧(blockingは work_rights 由来のみ)
    unconfirmed = [{"item": b, "blocking": True} for b in blocking] + [{"item": i, "blocking": False} for i in informational]
    unconfirmed.append({"item": "法律原文・文化庁資料による確認は未実施(二次資料に基づく機械判定)。法的最終判断ではなく弁護士確認が望ましい。", "blocking": False})
    unconfirmed.append({"item": "米国等の他法域status: " + us_rec, "blocking": False})
    for note in w.get("edition_unconfirmed", []):
        unconfirmed.append({"item": note, "blocking": False})

    ed_cards = {k: cinfo.get(k) for k in ("teihon", "moji_type", "input_proof", "source_on_page", "license_tag_on_wikisource") if cinfo.get(k)}
    work_rights = {
        "role": "main_basis_of_decision",
        "original_language": w["work_source"]["language"],
        "work_title_original": w["work_source"]["title_original"],
        "primary_source_is_original_language_text": True,
        "primary_source_label": w["work_source"]["text_url_label"],
        "original_author_status_jp": author_status,
        "original_author_subject": au_subj,
        "first_publication": {"year": fp["year"], "text": fp["text"], "source": fp["source"]},
    }
    edition_rights = {
        "role": "reference_only_not_a_precondition_for_article",
        "note": "利用した版・翻訳の権利は参考情報。原語原作がPDなら、版/翻訳の権利は作品のPASS/NGに影響させない(本Trialは原語原作を自前でadaptationする設計)。",
        "edition_used": w["edition_note"],
        "edition_card_fields": ed_cards,
        "reference_translations": w.get("reference_translations", []),
        "reference_translation_subjects": ed_subjects,
        "reference_translation_status_jp": ed_status or ["n/a"],
        "reference_translation_note": w.get("reference_translation_note"),
    }
    return {
        "work_id": wid, "title_ja": w["title_ja"], "title_en": w["title_en"], "genre": w["genre"], "kind": kind,
        "screened_at": dt.datetime.now(dt.timezone.utc).isoformat(), "as_of_date": today.isoformat(),
        "screening_version": "02_original_language",
        "author": {k: au[k] for k in ("name", "birth_year", "death_year", "source")},
        "first_publication": {"year": fp["year"], "text": fp["text"], "source": fp["source"]},
        "work_rights": work_rights,
        "edition_rights": edition_rights,
        "primary_source": {
            "language": w["work_source"]["language"],
            "card_url": card.get("url"), "text_url": text.get("url"), "fetch_ok": fetch_ok,
            "text_http_status": text.get("http_status"), "text_bytes": text.get("bytes"),
            "text_plain_chars": text.get("plain_chars"), "text_sha256_raw": text.get("sha256"),
            "text_sha256_plain": text.get("plain_sha256"), "text_fetched_at": text.get("fetched_at"),
            "fetch_attempts": text.get("attempts"),
            "saved_dir": "er054_output/family_z_story_pool_trial_01/sources/%s/" % sdir,
            "card_parse": cinfo,
        },
        "edition_note": w["edition_note"],
        "work_vs_edition": {"original_work_status_jp": author_status,
                            "edition_translation_status_jp_reference_only": ed_status or ["n/a(原語版)"],
                            "reference_translation_pub_year": w.get("translation_pub_year")},
        "rights_subjects": [au_subj],
        "z1_checks": {"us_pd_used_as_jp_basis": False, "us_status_record_only": us_rec,
                      "primary_source_is_original_language": True,
                      "edition_or_translation_rights_used_as_precondition": False,
                      "data_vs_card_checks": checks, "other_checks": checks_extra},
        "unconfirmed": unconfirmed,
        "decision": decision,
        "decision_basis": "work_rights(原語原作の著者の日本国内保護期間)のみ。edition_rightsは参考。",
        "decision_reason": " ".join(reasons),
    }


def main():
    today = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 10, 11)
    data_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, "rights_data_01.json")  # 委任_02: 追加作品用データ指定可
    data = json.load(open(data_path, encoding="utf-8"))
    os.makedirs(OUTD, exist_ok=True)
    rows = []
    for wid, w in data["works"].items():
        o = screen_one(wid, w, data["rule_sources"], today)
        with open(os.path.join(OUTD, "%s.json" % wid), "w", encoding="utf-8") as f:
            json.dump(o, f, ensure_ascii=False, indent=2)
        rows.append(o)
        sys.stdout.buffer.write(("%s %s | %s\n" % (wid, o["decision"], o["decision_reason"][:150])).encode("utf-8"))
    l06 = next((r for r in rows if r["work_id"] == "L06"), {"decision": "n/a"})
    if l06["decision"] == "PASS":
        print("STOP: L06(既知の権利NG)がPASSになった。判定ロジック欠陥の疑い。", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
