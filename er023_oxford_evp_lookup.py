# ============================================================
# er023_oxford_evp_lookup.py
# KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
# Oxford 3000/5000・Oxford Phrase List・EVPの「評価専用」候補単位lookup。
#
# 遵守事項(委任条件どおり):
#   - 群2DB(Oxford/EVP)はProduction判定には使わない。評価専用。
#   - proprietary listの一括取得・ローカルDB化・大量保存はしない
#     (下記の実装方針の注記を参照)。
#   - 保存するのは候補ごとの「一致有無・CEFRレベル・種別・参照URL・
#     取得日時」のみ(ページ本文・リスト全体は保存しない)。
#
# 実装方針の注記(解釈上の決定、Fable/ユーザー確認事項として明記):
#   Oxford 3000/5000・Oxford Phrase Listは、Oxford側が単語/フレーズ
#   ごとの個別照会APIを提供しておらず、公開Webページ1枚に全件がHTML
#   属性(data-hw/data-ox3000/data-ox5000/data-oxford_phrase_list)として
#   埋め込まれている(db_survey_key_phrase_sources_01.md 1-2節で確認
#   済みの構造)。そのため本Trialでは「そのページを1回だけ取得し、
#   メモリ上でのみ候補ごとの所属確認を行い、取得したHTMLやパース済み
#   全件テーブルはディスクへ保存しない(この関数の呼び出しプロセスの
#   メモリ上にのみ存在し、プロセス終了とともに破棄される)」という
#   方式を「候補単位の公開ページ照会」の実装として採用した。ページ
#   本文を永続化しない点、DB化・大量保存をしない点は遵守しているが、
#   「1候補=1 HTTPリクエスト」という文字どおりの意味ではない解釈で
#   ある点はREPORTで明示し、Fable/ユーザーの確認を仰ぐ。
#
#   EVP(englishprofile.org)は、db_survey確認時点でBubble.io製SPAで
#   あり静的HTTP GETでは本文が取得できない(JS描画が必要)。本Trialでは
#   隠しAPIの探索・逆解析は行わない(ライセンス未確認の商用データへの
#   意図しないアクセス回避のため)。EVPは本Trialでは
#   `lookup_not_available`として扱う(STOP条件相当だが、Oxford側は
#   照会可能なため、EVPのみ利用不可としてTrial全体は継続する)。
# ============================================================

from __future__ import annotations

import datetime
import re
import urllib.request

OXFORD_WORDLIST_URL = "https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000"
OXFORD_PHRASE_LIST_URL = "https://www.oxfordlearnersdictionaries.com/wordlists/oxford-phrase-list"
_UA = "Mozilla/5.0 (compatible; eigo-radio-trial/1.0; KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01)"

_OX_WORD_RE = re.compile(
    r'data-hw="([^"]+)"\s+data-ox3000="([^"]*)"\s+data-ox5000="([^"]*)"')
_OX_PHRASE_RE = re.compile(
    r'data-hw="([^"]+)"\s+data-oxford_phrase_list="([^"]*)"')


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


class OxfordEvpLookupSession:
    """1回のTrial実行内で、Oxfordの2ページをそれぞれ1回だけ取得し、
    メモリ上のdictとして保持する(ディスクへ保存しない)。候補単位の
    lookup呼び出しごとに、参照URL・取得日時を記録して返す。"""

    def __init__(self):
        self._word_index = None
        self._phrase_index = None
        self._word_fetch_meta = None
        self._phrase_fetch_meta = None
        self.evp_available = False
        self.evp_unavailable_reason = (
            "englishprofile.org はBubble.io製SPAであり静的HTTP GETでは本文が"
            "取得できない(db_survey_key_phrase_sources_01.md 3節、"
            "2026-09-27確認済み)。本Trialでは隠しAPIの探索は行わない。"
        )

    def _ensure_word_index(self):
        if self._word_index is not None:
            return
        html = _fetch(OXFORD_WORDLIST_URL)
        idx = {}
        for m in _OX_WORD_RE.finditer(html):
            hw, ox3000, ox5000 = m.group(1).lower(), m.group(2), m.group(3)
            idx[hw] = {"ox3000": ox3000 or None, "ox5000": ox5000 or None}
        self._word_index = idx
        self._word_fetch_meta = {
            "url": OXFORD_WORDLIST_URL,
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "entries_parsed": len(idx),
        }
        del html  # ページ本文はここで破棄、以降保持しない

    def _ensure_phrase_index(self):
        if self._phrase_index is not None:
            return
        html = _fetch(OXFORD_PHRASE_LIST_URL)
        idx = {}
        for m in _OX_PHRASE_RE.finditer(html):
            hw, level = m.group(1).lower(), m.group(2)
            hw = hw.replace("…", "...")
            idx[hw] = {"oxford_phrase_list": level or None}
        self._phrase_index = idx
        self._phrase_fetch_meta = {
            "url": OXFORD_PHRASE_LIST_URL,
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "entries_parsed": len(idx),
        }
        del html

    def lookup(self, candidate_canonical_form: str) -> dict:
        """1候補についての照会結果を返す。matched_sources: ["oxford_3000_5000"]
        / ["oxford_phrase_list"] / [] のいずれか(両方一致も理論上あり得る
        ため list)。cefr_level_hint: Oxfordのband値(a1〜c1)、複数一致時は
        最初に見つかったもの。"""
        self._ensure_word_index()
        self._ensure_phrase_index()
        key = candidate_canonical_form.lower().strip()
        matched_sources = []
        cefr_level_hint = None
        if key in self._word_index:
            matched_sources.append("oxford_3000_5000")
            cefr_level_hint = self._word_index[key]["ox5000"] or self._word_index[key]["ox3000"]
        if key in self._phrase_index:
            matched_sources.append("oxford_phrase_list")
            if cefr_level_hint is None:
                cefr_level_hint = self._phrase_index[key]["oxford_phrase_list"]
        return {
            "candidate": candidate_canonical_form,
            "matched_sources": matched_sources,
            "matched": len(matched_sources) > 0,
            "cefr_level_hint": cefr_level_hint,
            "reference_urls": (
                ([OXFORD_WORDLIST_URL] if "oxford_3000_5000" in matched_sources else [])
                + ([OXFORD_PHRASE_LIST_URL] if "oxford_phrase_list" in matched_sources else [])
            ) or [OXFORD_WORDLIST_URL, OXFORD_PHRASE_LIST_URL],
            "looked_up_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "evp_available": False,
            "evp_reason": self.evp_unavailable_reason,
        }

    def fetch_metadata(self) -> dict:
        return {"oxford_word_list": self._word_fetch_meta, "oxford_phrase_list": self._phrase_fetch_meta}
