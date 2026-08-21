# ============================================================
# er006_cost_rootfix_01_text_normalize.py
# ER-006-POOL-PILOT-COST-ROOTFIX-01: ASR比較用テキスト正規化(提案・未配線)
# ============================================================
# 9件のSTOPPED segmentを個別調査した結果、いずれも「TTSの読み上げ内容そのものは
# 概ね正しいが、ASR側の表記揺れ(トークン境界・ハイフン・母音記号・序数・英米綴り・
# ダッシュ種別)によって既存のsubstring/exact比較が通らない」パターンだった。
# このモジュールは、比較直前にcanonical textとASR textの両方へ適用する正規化を
# 提案するもの。**本番のTTS/ASR検証ロジックへはまだ配線していない**(retry loop
# 自体を触る前にユーザー確認を得るため)。
#
# 対象にした実際のmismatch(全て今回のPilotの実データに基づく):
#   - "Malmö" vs "Malmo"                         → 発音区別符号(diacritics)除去
#   - "Triangeln" vs "Triangle"                   → ※これは正規化では救えない
#     (固有名詞の音自体が近い英語化。無理に吸収すると誤読を見逃すリスクがあるため、
#      本モジュールでは対象外とし、別途「固有名詞は事前にASR用の許容綴りを
#      Ledgerへ登録する」運用での対応を提案する。7章参照)
#   - "March 4, 2011" vs "March 4th, 2011"        → 序数(th/st/rd/nd)除去
#   - "an error—not" vs "an error, not"           → ダッシュ/カンマの等価扱い
#   - "wide-scale" vs "Wide-scale"/"Widescale"     → ハイフンの有無を無視
#   - "Click-to-Cancel" vs "Click to cancel"       → ハイフンの有無を無視+大小無視
#   - "cancelling" vs "canceling"                  → 英/米綴りの等価表
#   - "blitzscaling" vs "Blitz scaling"            → 複合語の分かち書きを無視
from __future__ import annotations

import re
import unicodedata

# 英/米綴りの既知ペア(このPilotで実際に問題になったもの+一般的に知られる代表例のみ。
# 単語固有のwhitelistではなく、綴り「パターン」の等価表として扱う)
BR_AM_SPELLING_PAIRS = [
    ("cancelling", "canceling"), ("cancelled", "canceled"),
    ("colour", "color"), ("favourite", "favorite"), ("centre", "center"),
    ("organise", "organize"), ("organised", "organized"),
    ("realise", "realize"), ("realised", "realized"),
    ("travelled", "traveled"), ("travelling", "traveling"),
    ("labelled", "labeled"), ("modelling", "modeling"),
]


def strip_diacritics(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_for_asr_comparison(text: str) -> str:
    """ASR比較専用の正規化。canonical textとasr_textの両方へ同一に適用する。
    発音上区別できない表記差(diacritics/ハイフン/序数/ダッシュ種別/英米綴り/大小文字/
    複合語の分かち書き)のみを吸収する。単語そのものの置き換えは行わない
    (=内容の違いは正規化後も違いとして残る)。
    """
    t = text.lower()
    t = strip_diacritics(t)
    for br, am in BR_AM_SPELLING_PAIRS:
        t = t.replace(br, am)
    # ダッシュ類(em-dash/en-dash/hyphen)とアポストロフィ種別をASCIIへ統一
    t = t.replace("\u2014", "-").replace("\u2013", "-")
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u201c", '"').replace("\u201d", '"')
    # 序数(4th, 1st, 2nd, 3rd) → 数字のみ
    t = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", t)
    # ハイフン・複合語の分かち書きを無視するため、英数字以外を全て空白へ
    t = re.sub(r"[^a-z0-9]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def texts_equivalent(a: str, b: str) -> bool:
    return normalize_for_asr_comparison(a) == normalize_for_asr_comparison(b)


if __name__ == "__main__":
    # 実データでの検証(このPilotの9 STOPPED segmentのうち、正規化のみで
    # 「一致」に変わるケースがどれだけあるかを確認する)
    import json

    SCRATCH = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/daf25663-27ea-406d-b296-2a10ba6c8316/scratchpad"
    detail = json.load(open(f"{SCRATCH}/stopped_full_detail.json", encoding="utf-8"))
    for d in detail:
        canon = d["canonical_text"]
        if not canon:
            continue
        first_attempt_asr = d["attempts"][0]["asr_text"]
        would_pass = texts_equivalent(first_attempt_asr, canon)
        print(f"{d['theme']}/{d['level']}/{d['segment']}: attempt1で正規化後一致={would_pass}")
