# -*- coding: utf-8 -*-
"""Human Review(HR)試聴ページ・完成候補ページの掲載対象policy(共通関数)。FZ-DIALOGUE-LR-ADOPTION-01 委任_05、ユーザー正式決定
(`docs/pm/delegation_log/2026-10-29_FZ-DIALOGUE-LR-ADOPTION-01_USER_02.md` §2、PM_GOVERNANCE 30-5)。

原則: **ユーザーが聴いて判断する音声だけを掲載する**。ASR NGで比較判断を求めない失敗Take・不採用Take・確認不要Takeは掲載しない。
試行履歴・NG理由・全Takeの証拠は内部ログ(attempt state / review_lock / HRQ / EVIDENCE json)に**そのまま保持**する(削除しない)。
完成候補ページは最終採用音声を中心に、HR採用の事実を簡潔な1行で示す(再生UIは本文の行にある最終音声のみ)。
新Gate・新品質基準ではない(表示の絞り込みだけ。Gate・試行記録・判定は不変)。副作用なし・API 0の純関数。

Take dictの形(キーはすべて任意、無い場合は掲載側の既定): id / asr_state(文字列。'NG'を含む=ASR NG、例 NG_BOTH/TRUE_CONTENT_MISMATCH/ASR_NG) /
asr_ng(bool、asr_stateより優先) / user_judgment_requested(bool。ASR NGでも『耳で読み誤りかを判断してほしい』場合に明示) / adopted(bool。最終採用) / candidate(bool)。
"""
from __future__ import annotations
import html as _html
from typing import Iterable

NG_MARKERS = ("NG", "MISMATCH", "FAIL")      # asr_stateに含まれればASR NG扱い(PASS_WITH_WARNING等は含まない)


def is_asr_ng(take: dict) -> bool:
    """ASR NGのTakeか。asr_ng(bool)があればそれを優先、無ければasr_state文字列のNG語を見る。"""
    if "asr_ng" in take and take["asr_ng"] is not None:
        return bool(take["asr_ng"])
    st = str(take.get("asr_state") or "").upper()
    if "PASS" in st:
        return False
    return any(m in st for m in NG_MARKERS)


def is_listing_target(take: dict) -> bool:
    """ユーザーの判断対象として掲載すべきTakeか。最終採用 / 判断を明示要求 / ASR NGでないcandidate は掲載、ASR NGで判断要求なしは非掲載。"""
    if take.get("adopted") or take.get("user_judgment_requested"):
        return True
    return not is_asr_ng(take)


def select_listing_takes(takes: Iterable[dict]) -> tuple:
    """(listed, omitted)。順序は保つ。omittedは内部ログ(EVIDENCE json等)へ必ず残す(`omitted_internal_record`)。"""
    listed, omitted = [], []
    for t in takes:
        (listed if is_listing_target(t) else omitted).append(t)
    return listed, omitted


def omitted_internal_record(omitted: Iterable[dict]) -> list:
    """非掲載Takeの内部記録(idと理由のみ。音声・NG理由本体は元のattempt記録に保持されている)。"""
    return [{"id": t.get("id"), "reason": "ASR NGでユーザー判断対象ではないため試聴ページ非掲載(内部記録に保持)", "asr_state": t.get("asr_state")} for t in omitted]


def render_hr_adoption_section(items: list) -> str:
    """完成候補ページの事後確認節(最終採用音声中心)。items=[{"label": "Advanced 武弘の証言(part3_c6)", "note": "...簡潔な1文"}]。空=空文字(従来ページとバイト同一)。
    再生UIは出さない(最終音声は本文の再生順スクリプトの行にある)。不採用Takeは載せない。"""
    if not items:
        return ""
    lis = "".join(f"<li><b>{_html.escape(str(i['label']))}</b>: {_html.escape(str(i['note']))}</li>" for i in items)
    return ("<section id='post-check-hr'><h2>事後確認(Human Reviewで採用した音声)</h2>"
            "<p>自動検査では判定できず、ユーザーが試聴して採用を決めた音声です(最終採用の音声は上の再生順スクリプトの該当行で聴けます)。</p>"
            f"<ul>{lis}</ul></section>")


def collect_hr_adoptions(results_by_level: dict) -> list:
    """tts_generation_results.json(level->segments dict)から z_adoption=='human_review_adopted' のclipを集める。
    LR不採用(HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG真)は注記に1句だけ添える。"""
    out = []
    for level, segs in (results_by_level or {}).items():
        for sid, e in (segs or {}).items():
            if (e or {}).get("z_adoption") != "human_review_adopted":
                continue
            lr = bool(e.get("local_rewrite_audio_superseded_by_human_approval"))
            label = f"{'Advanced' if level == 'b1b' else 'Standard'} {sid}"
            note = "ユーザーがHuman Reviewで試聴し、この音声を採用しました。" + ("Local Rewriteによる本文変更は採用せず、元の本文のままです。" if lr else "本文は変更していません。")
            out.append({"label": label, "note": note})
    return out
