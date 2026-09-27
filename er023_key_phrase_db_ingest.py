# ============================================================
# er023_key_phrase_db_ingest.py
# KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
# 群1DB(CEFR-J・NGSL系・Wiktionary idioms/phrasal verbs/proverbs)の
# ローカル取込ローダー。取得済みファイルは
# er023_output/key_phrase_db_trial_01/db/ 配下(本モジュールはネット
# アクセスしない。Wiktionary multiword termsのtargeted lookupのみ、
# 呼び出し元が明示的にAPIを呼ぶ関数を別途提供する)。
#
# 性質: Trial専用(er023_output/はProduction経路から一切参照されない)。
# 既存Production module(er003_key_words_*, er015_*)はimportして再利用
# するのみで変更しない。
# ============================================================

from __future__ import annotations

import csv
import json
import os
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from typing import Optional

DB_ROOT = os.path.join("er023_output", "key_phrase_db_trial_01", "db")

CEFR_J_XLSX_PATH = os.path.join(DB_ROOT, "cefr_j", "CEFR-J_Wordlist_Ver1.6.xlsx")
NGSL_CSV_PATHS = {
    "NGSL": os.path.join(DB_ROOT, "ngsl", "NGSL_12_lemmatized_for_teaching.csv"),
    "NAWL": os.path.join(DB_ROOT, "ngsl", "NAWL_12_lemmatized_for_teaching.csv"),
    "BSL": os.path.join(DB_ROOT, "ngsl", "BSL_120_lemmatized_for_teaching.csv"),
    "NGSL-Spoken": os.path.join(DB_ROOT, "ngsl", "NGSL-Spoken_12_lemmatized_for_teaching.csv"),
}
WIKTIONARY_JSON_PATHS = {
    "idiom": os.path.join(DB_ROOT, "wiktionary", "idioms.json"),
    "phrasal_verb": os.path.join(DB_ROOT, "wiktionary", "phrasal_verbs.json"),
    "proverb": os.path.join(DB_ROOT, "wiktionary", "proverbs.json"),
}

WIKTIONARY_API = "https://en.wiktionary.org/w/api.php"
WIKTIONARY_USER_AGENT = "eigo-radio-trial/1.0 (research; KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01)"


def _normalize_key(text: str) -> str:
    """DB見出し語の照合キー正規化(大文字小文字・NFKC・空白圧縮のみ、
    アポストロフィ・ハイフンは表層のまま保持する=表記ゆれは呼び出し側の
    候補生成時に複数バリアントを生成して吸収する設計とする)。"""
    t = unicodedata.normalize("NFKC", text or "")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


# ------------------------------------------------------------
# CEFR-J
# ------------------------------------------------------------
def load_cefr_j(xlsx_path: str = CEFR_J_XLSX_PATH) -> dict:
    """headword(正規化key)->{"cefr": level, "pos": pos, "is_multiword": bool}
    のdictを返す(sheet='ALL')。同一headwordが複数行にまたがる場合は
    最初に見つかったCEFR levelを保持する(観測用途であり優先順位付けの
    ranking計算には使わない)。"""
    import openpyxl
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb["ALL"]
    result = {}
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        headword, pos, cefr = row[0], row[1], row[2]
        if not headword:
            continue
        # "a.m./A.M./am/AM" のようなスラッシュ区切り異表記は個別に展開する
        for variant in str(headword).split("/"):
            variant = variant.strip()
            if not variant:
                continue
            key = _normalize_key(variant)
            if key not in result:
                result[key] = {
                    "cefr": cefr, "pos": pos,
                    "is_multiword": " " in key,
                }
    wb.close()
    return result


# ------------------------------------------------------------
# NGSL family(lemma,inflected_form1,inflected_form2,...の行形式)
# ------------------------------------------------------------
def load_ngsl_family(csv_paths: dict = NGSL_CSV_PATHS) -> dict:
    """表層形(正規化key、lemma自身も含む)-> {"lists": [list_name,...],
    "lemma": lemma_headword} のdictを返す。"""
    result: dict = {}
    for list_name, path in csv_paths.items():
        with open(path, "r", encoding="cp1252", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                forms = [x.strip() for x in line.split(",") if x.strip()]
                if not forms:
                    continue
                lemma = forms[0]
                for form in forms:
                    key = _normalize_key(form)
                    if not key:
                        continue
                    entry = result.setdefault(key, {"lists": set(), "lemma": _normalize_key(lemma)})
                    entry["lists"].add(list_name)
    # setをsorted listへ変換(JSON化・再現性のため)
    for key, entry in result.items():
        entry["lists"] = sorted(entry["lists"])
    return result


# ------------------------------------------------------------
# Wiktionary(事前取得済みカテゴリタイトル一覧、ns=0のみ)
# ------------------------------------------------------------
def load_wiktionary_titles(json_paths: dict = WIKTIONARY_JSON_PATHS) -> dict:
    """canonical_key(正規化title)-> {"categories": [category_type,...]}
    のdictを返す。category_typeは"idiom"/"phrasal_verb"/"proverb"。"""
    result: dict = {}
    for category_type, path in json_paths.items():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for title in data["titles"]:
            key = _normalize_key(title)
            entry = result.setdefault(key, {"categories": set(), "surface_titles": set()})
            entry["categories"].add(category_type)
            entry["surface_titles"].add(title)
    for key, entry in result.items():
        entry["categories"] = sorted(entry["categories"])
        entry["surface_titles"] = sorted(entry["surface_titles"])
    return result


# ------------------------------------------------------------
# Wiktionary multiword terms: targeted lookup(dump全体は取得しない)
# ------------------------------------------------------------
def wiktionary_multiword_targeted_lookup(candidates: list, batch_size: int = 50,
                                          sleep_sec: float = 1.5) -> dict:
    """候補文字列のリストを受け取り、Category:English multiword terms
    への所属有無だけをMediaWiki APIで確認する(prop=categories、
    clcategories指定でフィルタ、ページ本文・カテゴリ一覧全体は取得
    しない)。戻り値: {"results": {candidate_title: bool}, "api_calls": n,
    "elapsed_sec": t}。candidatesは既に「他DB未一致」に絞り込み済みの
    ものを渡す前提(呼び出し側の責務)。"""
    results = {}
    calls = 0
    t0 = time.time()
    unique_candidates = sorted(set(candidates))
    for i in range(0, len(unique_candidates), batch_size):
        batch = unique_candidates[i:i + batch_size]
        titles_param = "|".join(batch)
        params = {
            "action": "query", "titles": titles_param, "prop": "categories",
            "clcategories": "Category:English multiword terms", "cllimit": "500",
            "format": "json",
        }
        url = WIKTIONARY_API + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": WIKTIONARY_USER_AGENT})
        data = None
        for retry_i in range(5):
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.load(resp)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and retry_i < 4:
                    wait = float(e.headers.get("Retry-After", 5)) if e.headers else 5
                    time.sleep(max(wait, 2 ** retry_i))
                    continue
                raise
        calls += 1
        pages = data.get("query", {}).get("pages", {})
        matched_titles = set()
        for _, page in pages.items():
            if "categories" in page and page.get("categories"):
                matched_titles.add(page.get("title"))
        for cand in batch:
            results[cand] = cand in matched_titles
        if i + batch_size < len(unique_candidates):
            time.sleep(sleep_sec)
    elapsed = time.time() - t0
    return {"results": results, "api_calls": calls, "elapsed_sec": round(elapsed, 2),
            "candidate_count": len(unique_candidates)}


def load_all_group1_dbs() -> dict:
    return {
        "cefr_j": load_cefr_j(),
        "ngsl_family": load_ngsl_family(),
        "wiktionary": load_wiktionary_titles(),
    }
