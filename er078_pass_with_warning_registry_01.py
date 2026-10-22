# ============================================================
# ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 (AUW) 委任_02b/03
# PASS_WITH_WARNING 試聴リスト(registry)。tts_generation_results.json から**再導出**する純関数(別store・二重管理なし・冪等)。
# 状態: 作業branch feat/auw-unified-asr-01。委任_03でEN配線(adapter)・生成完了hook・X/Z/legacyページ節に接続済み。
# 入力の約束: 各セグメントdictが additive キー `asr_judgement` (= er078_asr_unified_judge_01.JudgeResult.audit_record) を持つ。
#   継承(既存音声の引継ぎ/再利用)は `asr_judgement_inherited` を同じ形で持つ(OF-AUW-15: 元のWARNINGを継承して表示)。
# ページは非ブロッキング(Assembly Gate・公開可否・HR queueに影響しない)。deriveの失敗は生成を失敗させない
# (`write_listening_list_safe`はwarningログを出して握りつぶす)。
# ============================================================
from __future__ import annotations

import html
import json
import os
import sys

PASSING = ("PASS_WITH_WARNING",)
LIST_FILENAME = "pass_with_warning_listening_list.json"
STANDALONE_FILENAME = "pass_with_warning_listening_list.html"
SECTION_ID = "pass-with-warning-listening-list"
SECTION_TITLE = "事後試聴リスト(PASS_WITH_WARNING)"


# attempt単位のログ(試行途中のasr_judgement)は「採用音声」ではないため走査しない(採用はsegment最上位のasr_judgementのみ)。
_SKIP_KEYS = ("asr_judgement", "asr_judgement_inherited", "attempts_log", "standard_attempts_log", "fallback_attempts_log",
              "attempts", "cascade_steps", "post_slowdown_cascade", "local_rewrite_recovery")


def _walk(node, path):
    """asr_judgement(またはasr_judgement_inherited)を持つdictを再帰的に列挙する(attempt logの中は見ない)。"""
    if isinstance(node, dict):
        if "asr_judgement" in node or "asr_judgement_inherited" in node:
            yield path, node
        for k, v in node.items():
            if k in _SKIP_KEYS:
                continue
            if isinstance(v, (dict, list)):
                yield from _walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, (dict, list)):
                yield from _walk(v, path + [str(i)])


def _vg_kind(judgement, which):
    vg = judgement.get("value_guard") or {}
    sub = vg.get(which) or {}
    return sub.get("kind") if isinstance(sub, dict) else None


def _entry(path, node, judgement, inherited):
    sec = judgement.get("secondary") or {}
    prim = judgement.get("primary") or {}
    seg_id = node.get("segment_id") or "/".join(p for p in path if p not in ("segments",))
    entry = {
        "segment_id": seg_id,
        "entry_key": "/".join(path),
        "role": node.get("role") or judgement.get("role") or (path[-1] if path else ""),
        "level": node.get("level") or judgement.get("level") or "",
        "lang": node.get("language") or judgement.get("lang") or "",
        "warning_labels": list(judgement.get("warnings") or []),
        "audio_path": node.get("path") or "",
        "adopted_sha256": node.get("sha256") or judgement.get("audio_sha256") or "",
        "original_wav": node.get("original_wav") or node.get("pre_slowdown_path") or "",
        "canonical_text": node.get("text") or node.get("canonical_text") or "",
        "primary_text": prim.get("text"),
        "secondary_text": sec.get("text"),
        "value_guard_kind_primary": _vg_kind(judgement, "primary"),
        "value_guard_kind_secondary": _vg_kind(judgement, "secondary"),
        "reason": judgement.get("reason_code") or "",
        "slot": judgement.get("slot"),
        "script_version": judgement.get("script_version"),
        "inherited": bool(inherited),
    }
    # ASR-HOMOPHONE 委任_04(D): er109(表記違い同音)が合否に寄与した音声だけ、事後試聴リストに根拠(適用規則・同値span・警告)を加算表示する。
    # ortho不使用の判定にはキー自体を作らない=A/B/Cの出力はバイト同一。
    oe = judgement.get("orthographic_equivalence")
    if isinstance(oe, dict) and oe.get("applied"):
        spans, rules = [], []
        for site in oe.get("sites") or []:
            er = site.get("er109") or {}
            for r in er.get("rules") or []:
                if r not in rules:
                    rules.append(r)
            for sp in er.get("spans") or []:
                spans.append({"site": site.get("site"), "canon": sp.get("canon"), "asr": sp.get("asr"), "rule": sp.get("rule"),
                              "warnings": sp.get("warnings")})
        entry["orthographic_equivalence"] = {"version": oe.get("version"), "scope": oe.get("scope"), "rules": rules, "spans": spans,
                                             "warnings": list(oe.get("warnings") or [])}
    return entry


def derive_listening_list(tts_generation_results: dict) -> list:
    """tts_generation_resultsからPASS_WITH_WARNINGの採用音声を列挙(sha256+ラベルで重複排除)。
    途中STOP(未生成/STOPPEDセグメント)があっても、それまでの採用済みWARNING分を返す。"""
    out, seen = [], set()
    for path, node in _walk(tts_generation_results or {}, []):
        for key, inherited in (("asr_judgement", False), ("asr_judgement_inherited", True)):
            j = node.get(key)
            if not isinstance(j, dict) or j.get("state") not in PASSING:
                continue
            if node.get("status") not in (None, "OK"):
                continue  # STOPPED等=採用音声なし
            e = _entry(path, node, j, inherited)
            dedup = (e["adopted_sha256"] or e["segment_id"], tuple(e["warning_labels"]))
            if dedup in seen:
                continue
            seen.add(dedup)
            out.append(e)
    return out


def write_listening_list(run_dir: str) -> str:
    """<run_dir>/audit/tts_generation_results.json -> <run_dir>/audit/pass_with_warning_listening_list.json (冪等)。"""
    audit_dir = os.path.join(run_dir, "audit")
    src = os.path.join(audit_dir, "tts_generation_results.json")
    results = {}
    if os.path.exists(src):
        with open(src, encoding="utf-8") as f:
            results = json.load(f)
    entries = derive_listening_list(results)
    payload = {"source": "audit/tts_generation_results.json", "count": len(entries), "entries": entries}
    os.makedirs(audit_dir, exist_ok=True)
    dst = os.path.join(audit_dir, LIST_FILENAME)
    tmp = dst + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, dst)
    return dst


class ListeningListDerivationFailed:
    """委任_06c(OF-AUW-C-12): 試聴リスト導出失敗の表現。`[]`(=「0件・該当なし」)と区別するため空listを返さない。
    iterate/len/boolは空として振る舞う(未更新の呼出元がクラッシュしない)が、`== []`ではなく、render_html_sectionは
    「導出失敗(要確認)」と表示する。"""

    def __init__(self, run_dir: str, error: str):
        self.run_dir, self.error = run_dir, error

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __bool__(self):
        return False

    def __repr__(self):
        return f"ListeningListDerivationFailed(run_dir={self.run_dir!r}, error={self.error!r})"


def load_listening_list(run_dir: str):
    """<run_dir>/audit/tts_generation_results.json から直接導出して返す(ページ生成用。ファイルを書かない)。
    成功: list。resultsファイルが無い: `[]`(そのrunにWARNING対象が無い=0件)。**導出失敗**(読込/解析/導出の例外):
    `[]`ではなく`ListeningListDerivationFailed`を返す(ページ生成は失敗させない=非ブロッキング、節に「導出失敗(要確認)」と表示)。"""
    src = os.path.join(run_dir, "audit", "tts_generation_results.json")
    try:
        if not os.path.exists(src):
            return []
        with open(src, encoding="utf-8") as f:
            return derive_listening_list(json.load(f))
    except Exception as exc:  # 非ブロッキング: ページ生成を失敗させない
        print(f"[WARN][pass_with_warning_registry] 試聴リスト導出に失敗(「導出失敗(要確認)」と表示): {run_dir}: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return ListeningListDerivationFailed(run_dir, f"{type(exc).__name__}: {exc}")


def write_listening_list_safe(run_dir: str, standalone_html: bool = False) -> dict:
    """生成完了hook用。**例外を投げない**(deriveの失敗は生成を失敗させない: warningログ+戻り値のerrorで報告)。
    standalone_html=Trueならlegacy(Family A/B/C)向けに`audit/pass_with_warning_listening_list.html`も書く(0件でも節を出す)。"""
    rep = {"run_dir": run_dir, "json": None, "html": None, "count": None, "error": None}
    try:
        rep["json"] = write_listening_list(run_dir)
        with open(rep["json"], encoding="utf-8") as f:
            data = json.load(f)
        rep["count"] = data["count"]
        if standalone_html:
            p = os.path.join(run_dir, "audit", STANDALONE_FILENAME)
            with open(p, "w", encoding="utf-8") as f:
                f.write(render_standalone_html(data["entries"]))
            rep["html"] = p
    except Exception as exc:
        rep["error"] = f"{type(exc).__name__}: {exc}"
        print(f"[WARN][pass_with_warning_registry] 試聴リスト出力に失敗(生成は継続): {run_dir}: {rep['error']}", file=sys.stderr)
        if standalone_html:  # 委任_06c(OF-AUW-C-12): 「0件」と誤表示せず「導出失敗(要確認)」を単独HTMLにも出す(失敗してもここは例外を投げない)
            try:
                p = os.path.join(run_dir, "audit", STANDALONE_FILENAME)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(render_standalone_html(ListeningListDerivationFailed(run_dir, rep["error"])))
                rep["html"] = p
            except Exception:
                pass
    return rep


def render_html_section(entries: list, href_fn=None) -> str:
    """X/Zページ・legacy単独ページの『事後試聴リスト(PASS_WITH_WARNING)』節。0件のときも節を出す(「0件」と明記)。

    href_fn(entry)->str: 音声リンク(相対/URL)を返す関数。未指定は entry["audio_path"]。空文字ならリンク無し。"""
    e_ = html.escape
    parts = [f'<section id="{SECTION_ID}"><h2>{SECTION_TITLE} WARNING音声 試聴リスト(自動採用・事後確認用)</h2>']
    if isinstance(entries, ListeningListDerivationFailed):
        parts.append("<p><strong>導出失敗(要確認)</strong>: 試聴リストを導出できませんでした(0件ではありません)。"
                     f"{e_(entries.error)} / {e_(str(entries.run_dir))}</p></section>")
        return "\n".join(parts)
    if not entries:
        parts.append("<p>0件(該当なし: PASS_WITH_WARNINGの採用音声はありません)</p></section>")
        return "\n".join(parts)
    parts.append(f"<p>{len(entries)}件。公開をブロックしません。事後に試聴して確認してください。</p><table border=\"1\"><tr>"
                 "<th>segment</th><th>role</th><th>warning</th><th>原稿</th><th>Primary転写</th><th>Secondary転写</th>"
                 "<th>値ガードkind</th><th>理由</th><th>音声</th></tr>")
    for e in entries:
        href = href_fn(e) if href_fn is not None else e.get("audio_path", "")
        audio = (f'<audio controls preload="none" src="{e_(str(href))}"></audio> <a href="{e_(str(href))}">mp3</a>' if href
                 else "(音声リンクなし)")
        tag = " (引継ぎ)" if e.get("inherited") else ""
        vgk = "/".join(str(k) for k in (e.get("value_guard_kind_primary"), e.get("value_guard_kind_secondary")) if k) or "-"
        reason_cell = str(e["reason"])
        oe = e.get("orthographic_equivalence")
        if oe:   # ASR-HOMOPHONE 委任_04: er109が寄与した音声だけ、同値と判定したspan(原稿->転写・規則)を理由欄へ加算表示(キー無し=従来と同一)
            reason_cell += " | er109: " + "; ".join(f"{' '.join(map(str, s.get('canon') or []))} -> {' '.join(map(str, s.get('asr') or []))} ({s.get('rule')})"
                                                  for s in (oe.get("spans") or []))
        parts.append(
            "<tr><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                e_(str(e["segment_id"])), tag, e_(str(e["role"])), e_(", ".join(e["warning_labels"])),
                e_(str(e["canonical_text"])), e_(str(e["primary_text"] or "")), e_(str(e["secondary_text"] or "")),
                e_(vgk), e_(reason_cell), audio))
    parts.append("</table></section>")
    return "\n".join(parts)


def render_standalone_html(entries: list, href_fn=None) -> str:
    """legacy(Family A/B/C)用の単独HTML。"""
    return ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>PASS_WITH_WARNING 試聴リスト</title></head><body>'
            + render_html_section(entries, href_fn) + "</body></html>")
