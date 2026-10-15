# ============================================================
# ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 (AUW) 委任_02b
# PASS_WITH_WARNING 試聴リスト(registry)。tts_generation_results.json から**再導出**する純関数(別store・二重管理なし・冪等)。
# 状態: 作業branch feat/auw-unified-asr-01 上の新規moduleのみ。Production未配線(ページ節への組込みは委任_03)。
# 入力の約束: 各セグメントdictが additive キー `asr_judgement` (= er078_asr_unified_judge_01.JudgeResult.audit_record) を持つ。
#   継承(既存音声の引継ぎ/再利用)は `asr_judgement_inherited` を同じ形で持つ(OF-AUW-15: 元のWARNINGを継承して表示)。
# ページは非ブロッキング(Assembly Gate・公開可否・HR queueに影響しない)。
# ============================================================
from __future__ import annotations

import html
import json
import os

PASSING = ("PASS_WITH_WARNING",)
LIST_FILENAME = "pass_with_warning_listening_list.json"


def _walk(node, path):
    """asr_judgement(またはasr_judgement_inherited)を持つdictを再帰的に列挙する。"""
    if isinstance(node, dict):
        if "asr_judgement" in node or "asr_judgement_inherited" in node:
            yield path, node
        for k, v in node.items():
            if k in ("asr_judgement", "asr_judgement_inherited"):
                continue
            if isinstance(v, (dict, list)):
                yield from _walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, (dict, list)):
                yield from _walk(v, path + [str(i)])


def _entry(path, node, judgement, inherited):
    sec = judgement.get("secondary") or {}
    prim = judgement.get("primary") or {}
    seg_id = node.get("segment_id") or "/".join(p for p in path if p not in ("segments",))
    return {
        "segment_id": seg_id,
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
        "reason": judgement.get("reason_code") or "",
        "slot": judgement.get("slot"),
        "script_version": judgement.get("script_version"),
        "inherited": bool(inherited),
    }


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


def render_html_section(entries: list) -> str:
    """X/Zページの『WARNING音声 試聴リスト(自動採用・事後確認用)』節。"""
    e_ = html.escape
    parts = ['<section id="pass-with-warning-listening-list"><h2>WARNING音声 試聴リスト(自動採用・事後確認用)</h2>']
    if not entries:
        parts.append("<p>該当なし(PASS_WITH_WARNINGの採用音声はありません)</p></section>")
        return "\n".join(parts)
    parts.append(f"<p>{len(entries)}件。公開をブロックしません。事後に試聴して確認してください。</p><table border=\"1\"><tr>"
                 "<th>segment</th><th>role</th><th>warning</th><th>原稿</th><th>Primary転写</th><th>Secondary転写</th><th>理由</th><th>音声</th></tr>")
    for e in entries:
        audio = (f'<audio controls preload="none" src="{e_(e["audio_path"])}"></audio>' if e["audio_path"] else "")
        tag = " (引継ぎ)" if e.get("inherited") else ""
        parts.append(
            "<tr><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                e_(str(e["segment_id"])), tag, e_(str(e["role"])), e_(", ".join(e["warning_labels"])),
                e_(str(e["canonical_text"])), e_(str(e["primary_text"] or "")), e_(str(e["secondary_text"] or "")),
                e_(str(e["reason"])), audio))
    parts.append("</table></section>")
    return "\n".join(parts)


def render_standalone_html(entries: list) -> str:
    """legacy(Family A/B/C)用の単独HTML。"""
    return ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>PASS_WITH_WARNING 試聴リスト</title></head><body>'
            + render_html_section(entries) + "</body></html>")
