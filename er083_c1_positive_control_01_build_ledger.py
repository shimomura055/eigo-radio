# -*- coding: utf-8 -*-
"""er083_c1_positive_control_01_build_ledger.py
C1陽性対照Trial用の**テスト用Ledger**を構成する(DEV/Trial専用、API 0。無料HTTP取得済みの原文との照合のみ)。

前提: er019 run_mey_01 の VERIFIED 11件(読取のみ)は、背景Fact(攻撃主体・流れ)を含まない(前Trial)。
本scriptは、その11件の末尾に、**実在する一次資料(国連DPPA/UN News 2026-10-09)に書かれている**背景Factを
F12〜F14として追加した `test_ledger_mey_positive_01.{txt,json}` を作る。架空の主張は作らない。
 - .txt = Production `verified_fact_ledger.txt` と同形式(B3入力)。ヘッダ等は付けない(B3 promptに混入するため)。
 - .json = メタ(is_test_ledger=true, test_origin, 各Factの出典URL・媒体・原文引用・取得時刻・HTTP status・検証根拠)。
出力先は er083_output/c1_positive_control_01/test_ledgers/ のみ(Production run dir・er019_output配下へは書かない)。

  python er083_c1_positive_control_01_build_ledger.py --src-dir <取得済みHTML置き場> [--check-only]
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_LEDGER = os.path.join(ROOT, "er019_output", "middle_east_yemen_saudi", "run_mey_01", "research_ledger", "verified_fact_ledger.txt")
OUT_DIR = os.path.join(ROOT, "er083_output", "c1_positive_control_01", "test_ledgers")
OUT_TXT = os.path.join(OUT_DIR, "test_ledger_mey_positive_01.txt")
OUT_JSON = os.path.join(OUT_DIR, "test_ledger_mey_positive_01.json")

# 取得記録(curl.exe -L -s -A "Mozilla/5.0"、HTTP 200、2026-10-20 UTC。本文はcommitしない)
SOURCES = {
    "S1": {"file": "src_02.html", "url": "https://dppa.un.org/en/press-releases/special-envoy-for-yemens-remarks-to-the-security-council-as-delivered",
           "publisher": "国連政治・平和構築局(DPPA)", "title": "Special Envoy for Yemen's remarks to the Security Council [as delivered]",
           "date": "2026-10-09", "fetched_at_utc": "2026-10-20T01:03:02Z", "http_status": 200, "source_type": "OFFICIAL_STATEMENT_TRANSCRIPT"},
    "S2": {"file": "src_01.html", "url": "https://dppa.un.org/en/news/yemen-has-returned-to-full-scale-war-special-envoy-warns",
           "publisher": "国連政治・平和構築局(DPPA)", "title": "Yemen has returned to full-scale war, Special Envoy warns",
           "date": "2026-10-09", "fetched_at_utc": "2026-10-20T01:02:44Z", "http_status": 200, "source_type": "OFFICIAL_NEWS_SUMMARY",
           "note": "run_mey_01 の F01 の出典URLと同一(委任_01の原因調査で突合せる点)"},
    "S4": {"file": "src_05.html", "url": "https://osesgy.unmissions.org/en/news/statement-by-un-special-envoy-for-yemen-hans-grundberg-on-latest-attacks-against-saudi",
           "publisher": "国連イエメン担当事務総長特使事務所(OSESGY)", "title": "Statement by UN Special Envoy for Yemen, Hans Grundberg, on latest attacks against Saudi Arabia",
           "date": "2026-10-11", "fetched_at_utc": "2026-10-20T01:13:11Z", "http_status": 200, "source_type": "OFFICIAL_STATEMENT",
           "note": "run_mey_01 の F11 の出典URLと同一(委任_01の原因調査で突合せる点)。原文は攻撃主体(Ansar Allah)を明記"},
    "S3": {"file": "src_03.html", "url": "https://news.un.org/en/story/2026/10/1168559",
           "publisher": "国連ニュース(UN News)", "title": "Security Council LIVE: Yemen has fallen back into full-scale war, warns UN envoy",
           "date": "2026-10-09", "fetched_at_utc": "2026-10-20T01:03:12Z", "http_status": 200, "source_type": "OFFICIAL_NEWS_EDITORIAL"},
}

ADDED = [
    {
        "fact_id": "F12", "expected_role": "E_CORE(誰が=攻撃主体の帰属)", "category": "who",
        "ledger_line": (
            "[VERIFIED] F12: 国連イエメン担当特使ハンス・グルンドベルグは、2026年10月9日の国連安全保障理事会での説明で、アンサール・アッラー(Ansar Allah)が"
            "サウジアラビアの民間・エネルギー施設への攻撃を行ったと述べ、その中にアブハ国際空港とリヤドのキング・ハーリド国際空港への最近の攻撃が含まれ、"
            "民間人に死傷者が出たとした。特使は10月11日の声明でも、サウジの民間インフラへの継続的な攻撃をアンサール・アッラーによるものとして非難し、同組織に攻撃の停止を求めた。\n"
            "  scope: サウジアラビアの民間・エネルギー施設への攻撃についての攻撃主体の帰属(国連特使の発言と声明)\n"
            "  conditions: 帰属は国連イエメン担当特使の安保理での発言と10月11日の声明として報告されたもの。動機は述べられていない。\n"
            "  date_or_period: 2026-10-09〜2026-10-11\n"
            "  causal_strength: OBSERVED_REPORTED\n"
            "  notes_for_writer: 帰属元(国連イエメン担当特使の安保理での発言と声明)を明示する。攻撃の動機は述べられていないため書かない。"
        ),
        "source_ids": ["S1", "S4"],
        "quotes": [("S4", "I strongly condemn the continuing attacks against civilian infrastructure in the Kingdom of Saudi Arabia by Ansar Allah, including the latest attack on 10 October against King Khalid International Airport in Riyadh which killed 12 people and injured over 300, according to Saudi authorities."),
                   ("S4", "I repeat my call on Ansar Allah to cease these attacks."),
                   ("S1", "Ansar Allah has also carried out attacks against civilian and energy infrastructure in the Kingdom of Saudi Arabia, "
                          "including recent attacks against Abha International Airport and King Khalid International Airport in Riyadh, which killed and injured civilians. "
                          "I echo the Secretary-General’s condemnation, and repeat my call on Ansar Allah to cease these attacks.")],
        "verification_basis": "一次資料2点(国連DPPA掲載の特使発言全文、OSESGYの特使声明)の原文に主語(Ansar Allah)・対象(サウジの民間・エネルギー施設、アブハ/リヤド空港)・停止要請が直接記載(DIRECTLY_STATED)。引用文は取得HTMLの本文に逐語一致(machine照合: check_quotes)。",
    },
    {
        "fact_id": "F13", "expected_role": "E_OK(何の流れ=紅海・海上交易路・エネルギー市場との接続。特使の評価)", "category": "context",
        "ledger_line": (
            "[VERIFIED] F13: 同じ説明で特使は、アンサール・アッラーによるサウジ関連の商船への紅海での脅威が、海上交易路の支配をめぐるより広い対立と国際エネルギー市場の逼迫と"
            "絡み合いつつあると述べた。また、中東の不安定が引き続きイエメン情勢に影響し、イエメンの動きが地域に波及しているとも述べた。\n"
            "  scope: イエメン情勢と地域(紅海の海上交通、エネルギー市場)との関係についての国連特使の評価\n"
            "  conditions: 国連特使の評価として述べられたもの。サウジ施設への攻撃の動機を直接説明したものではない。\n"
            "  date_or_period: 2026-10-09\n"
            "  causal_strength: OBSERVED_REPORTED\n"
            "  notes_for_writer: 特使の評価として帰属を明示し、攻撃の動機として言い換えない。"
        ),
        "source_ids": ["S1"],
        "quotes": [("S1", "Ansar Allah’s threats against Saudi-linked commercial ships in the Red Sea undermine the freedom of navigation of every country. "
                          "These threats are becoming enmeshed with the broader confrontation over control of maritime trade routes and the stresses on the international energy market."),
                   ("S1", "Ongoing instability in the Middle East continues to impact dynamics in Yemen, while developments in Yemen in turn reverberate across the region.")],
        "verification_basis": "一次資料の原文に直接記載。評価は特使の発言として帰属(動機の断定ではない)。引用文は取得HTMLに逐語一致。",
    },
    {
        "fact_id": "F14", "expected_role": "E_OK(何の流れ=9月のフーシ派攻勢・米イラン戦争の波及。UN Newsの要約)", "category": "context",
        "ledger_line": (
            "[VERIFIED] F14: 国連ニュース(UN News)は、2026年10月9日の安保理会合の記事で、9月に始まったフーシ派の攻勢が12年に及ぶイエメンの戦争を急激に激化させ、"
            "米国・イラン戦争の波及が新たな避難民危機を招いていると伝えた。同記事は、サウジの空港やエネルギー施設への越境ミサイル・ドローン攻撃が同週も続いたこと、"
            "イラン支援のフーシ派とサウジ支援の政府軍の戦闘がタイズ周辺で激化していることを要点として挙げた。\n"
            "  scope: イエメンの戦争の局面とサウジ施設への越境攻撃(国連ニュースによる要約)\n"
            "  conditions: UN Newsの記事冒頭の要点(編集文)。個々の攻撃の主体や動機を個別に立証したものではない。\n"
            "  date_or_period: 2026-10-09\n"
            "  causal_strength: OBSERVED_REPORTED\n"
            "  notes_for_writer: 国連ニュースの要約として帰属を明示し、攻撃の動機として言い換えない。"
        ),
        "source_ids": ["S3"],
        "quotes": [("S3", "a Houthi offensive launched in September has sharply escalated the 12-year-long war for control of the country and spillover from the US-Iran war has provoked a new displacement crisis"),
                   ("S3", "Cross-border missile and drone strikes on Saudi airports and energy infrastructure have continued this week"),
                   ("S3", "Fighting between Iran-backed Houthis and Saudi-backed Government forces is intensifying around Taiz")],
        "verification_basis": "UN Newsの記事冒頭要点の原文に直接記載。編集文であるため帰属はUN Newsの要約とする。引用文は取得HTMLに逐語一致。",
    },
]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def strip_html(raw: str) -> str:
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", raw)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def check_quotes(src_dir: str) -> dict:
    """各引用が取得HTML本文に逐語一致(空白正規化のみ)で含まれるかを機械照合。"""
    texts, shas = {}, {}
    for sid, s in SOURCES.items():
        p = os.path.join(src_dir, s["file"])
        raw = open(p, "rb").read()
        shas[sid] = sha256_bytes(raw)
        texts[sid] = norm(strip_html(raw.decode("utf-8", errors="replace")))
    res = {}
    for f in ADDED:
        res[f["fact_id"]] = [{"source": sid, "found": norm(q) in texts[sid], "chars": len(q)} for sid, q in f["quotes"]]
    return {"source_html_sha256": shas, "quote_check": res, "all_found": all(r["found"] for v in res.values() for r in v)}


def build(src_dir: str) -> dict:
    qc = check_quotes(src_dir)
    if not qc["all_found"]:
        raise RuntimeError("[STOP] 引用が取得原文と逐語一致しないFactあり: " + json.dumps(qc["quote_check"], ensure_ascii=False))
    base_bytes = open(BASE_LEDGER, "rb").read()
    base_sha = sha256_bytes(base_bytes)
    new_text = "\r\n\r\n".join(f["ledger_line"].replace("\n", "\r\n") for f in ADDED) + "\r\n"
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_TXT, "wb") as fh:
        fh.write(base_bytes + b"\r\n" + new_text.encode("utf-8"))
    meta = {
        "is_test_ledger": True,
        "test_origin": "FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_02: C1陽性対照Trial用。run_mey_01のVERIFIED 11件(無改変)+実在一次資料のFact 3件(F12〜F14)",
        "production_use": "禁止(DEV/Trial専用。Production run dir・Ledger・runnerへ混入しない)",
        "base_ledger": {"path": "er019_output/middle_east_yemen_saudi/run_mey_01/research_ledger/verified_fact_ledger.txt", "sha256_bytes": base_sha, "n_facts": 11, "modified": False},
        "test_ledger_txt": {"path": "er083_output/c1_positive_control_01/test_ledgers/test_ledger_mey_positive_01.txt",
                            "sha256_bytes": sha256_bytes(open(OUT_TXT, "rb").read()), "n_facts": 11 + len(ADDED)},
        "format": "Production verified_fact_ledger.txt と同形式(ヘッダ無し、[VERIFIED] Fxx: ... + 追加行)",
        "sources": {sid: {k: v for k, v in s.items() if k != "file"} for sid, s in SOURCES.items()},
        "fetch_command": "curl.exe -L -s -A \"Mozilla/5.0\" -o <scratchpad>/xrg2/src_0N.html \"<url>\"(本文はcommitしない)",
        "source_html_sha256": qc["source_html_sha256"],
        "added_facts": [{
            "fact_id": f["fact_id"], "category": f["category"], "expected_role": f["expected_role"],
            "ledger_line": f["ledger_line"], "source_ids": f["source_ids"],
            "source_urls": [SOURCES[s]["url"] for s in f["source_ids"]],
            "quotes_original": [{"source": s, "text": q} for s, q in f["quotes"]],
            "quote_check": qc["quote_check"][f["fact_id"]],
            "verification": "VERIFIED", "support_level": "DIRECTLY_STATED", "verification_basis": f["verification_basis"],
        } for f in ADDED],
        "verification_caveat": "F12〜F14のVERIFIED付与は、Production Verifier(LLM)ではなく、本Trial作成者が一次資料の原文と逐語照合した結果。Production Ledger(run_mey_01)へは混入しない。",
        "expected_set": {"E_core": ["F12"], "E_ok": ["F13", "F14"], "meaning": "E_core追加=核心機能成功。E_okの追加は許容。それ以外(F01〜F11)の追加=期待外"},
        "cross_reference_for_delegation_01": "S2=run_mey_01のF01の出典URLと同一、S4=F11の出典URLと同一。いずれの原文もサウジ施設への攻撃主体をAnsar Allahと明記(S4は文中、S1/S2は特使発言)。一方F01・F11のLedger記述には主体名が含まれない=Research/Ledger化段階での欠落(原因特定は委任_01)。S1はS2の元発言全文。",
    }
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
    return meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-dir", required=True)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args(argv)
    if a.check_only:
        print(json.dumps(check_quotes(a.src_dir), ensure_ascii=False, indent=2))
        return 0
    m = build(a.src_dir)
    print(json.dumps({"txt": m["test_ledger_txt"], "all_quotes_found": True, "n_added": len(m["added_facts"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
