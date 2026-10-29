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
    # JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: 日本語ASR v2+β(新方式)のrecordだけ、判定区分・救済根拠・救済理由・警告を加算する。
    # 旧record(judge_rule_versionなし=scope外/旧資産)にはキー自体を作らない=従来とバイト同一。ここで加えた値は報告表示専用(制御フローは読まない)。
    if "judge_rule_version" in judgement:
        v2b = judgement.get("ja_v2beta") if isinstance(judgement.get("ja_v2beta"), dict) else {}
        beta = v2b.get("beta") if isinstance(v2b.get("beta"), dict) else {}
        entry["verdict"] = judgement.get("verdict")
        entry["rescue_basis"] = judgement.get("rescue_basis")
        entry["rescue_reason_ja"] = judgement.get("rescue_reason_ja")
        entry["judge_rule_version"] = judgement.get("judge_rule_version")
        entry["listen_advised"] = bool(beta.get("listen_advised"))                    # 試聴推奨(任意)。必須ではない
        entry["secondary_reading_conflict"] = bool(beta.get("secondary_reading_conflict"))
        entry["weak_rank"] = v2b.get("weak_rank")                                      # 0=Secondary読み相違あり(最も弱い) / 1=garble説明 / 2=発音同一 / 3=その他
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
    if any(e.get("rescue_basis") for e in out):
        # R-6: 新方式(rescue_basis付き)を先頭に、証拠の弱い順(読み相違あり>garble説明>発音同一>その他)で並べる(安定ソート)。報告の表示順のみ。
        out.sort(key=lambda e: (0, e.get("weak_rank") if e.get("weak_rank") is not None else 3) if e.get("rescue_basis") else (1, 0))
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
    health = scan_v2beta_health(results)
    if health["attempt_records"] > 0:   # JA-ASR-V2-BETA 委任_02A(R-6): run単位の集計(X/Y/Z scope内のJA判定があるrunだけ。scope外=キー自体を作らない)
        payload["ja_v2beta_summary"] = dict(summarize_entries(entries), health=health)
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


def write_listening_list_safe(run_dir: str, standalone_html: bool = False, completion_label: str | None = None) -> dict:
    """生成完了hook用。**例外を投げない**(deriveの失敗は生成を失敗させない: warningログ+戻り値のerrorで報告)。
    standalone_html=Trueならlegacy(Family A/B/C)向けに`audit/pass_with_warning_listening_list.html`も書く(0件でも節を出す)。
    completion_label(既定None=従来と同一。X/Y/Zのhookだけが渡す): 日本語ASR PASS_W(新方式)の最終制作報告ブロックを標準出力へ出す(`emit_completion_block`。失敗しても例外を投げない)。"""
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
    if completion_label:
        rep["completion_block"] = emit_completion_block(run_dir, completion_label)
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
    has_new = any(e.get("rescue_basis") for e in entries)    # JA-ASR-V2-BETA 委任_02A: 新方式(v2/β)のPASS_Wがあるときだけ列を加算
    new_note = ("<p>『新方式』欄が入った行は日本語ASR v2読み規則/B-light βで救済した音声です(証拠の弱い順に先頭表示)。"
                "試聴は推奨(任意)であり、制作・組立・納品候補作成は止めません。</p>") if has_new else ""
    parts.append(f"<p>{len(entries)}件。公開をブロックしません。事後に試聴して確認してください。</p>{new_note}<table border=\"1\"><tr>"
                 "<th>segment</th><th>role</th><th>warning</th><th>原稿</th><th>Primary転写</th><th>Secondary転写</th>"
                 "<th>値ガードkind</th><th>理由</th>" + ("<th>新方式</th><th>救済理由</th>" if has_new else "") + "<th>音声</th></tr>")
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
        new_cells = ""
        if has_new:
            new_cells = "<td>%s</td><td>%s</td>" % (e_(str(e.get("rescue_basis") or "-")), e_(str(e.get("rescue_reason_ja") or "")))
        parts.append(
            "<tr><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>%s<td>%s</td></tr>" % (
                e_(str(e["segment_id"])), tag, e_(str(e["role"])), e_(", ".join(e["warning_labels"])),
                e_(str(e["canonical_text"])), e_(str(e["primary_text"] or "")), e_(str(e["secondary_text"] or "")),
                e_(vgk), e_(reason_cell), new_cells, audio))
    parts.append("</table></section>")
    return "\n".join(parts)


def render_standalone_html(entries: list, href_fn=None) -> str:
    """legacy(Family A/B/C)用の単独HTML。"""
    return ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>PASS_WITH_WARNING 試聴リスト</title></head><body>'
            + render_html_section(entries, href_fn) + "</body></html>")


# ============================================================
# JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: 日本語ASR PASS_W(新方式)の最終制作報告(完了ブロック)。
# 共通データ源=本registry(tts_generation_results.jsonの再導出)。新store・新Gateなし。**報告のみ**(verdict/rescue_basis/listen_advisedを読んで制御フローを変えない)。
# 要Human Review一覧(R-8)はverdict==HRではなく、実際のHR queue/Lock登録(review_lock_state.json・JA queue)から取る。
# ============================================================
def summarize_entries(entries) -> dict:
    """run単位の集計(R-6)。entries=derive_listening_list結果。"""
    new = [e for e in (entries or []) if e.get("rescue_basis")]
    by = {}
    for e in new:
        by[e["rescue_basis"]] = by.get(e["rescue_basis"], 0) + 1
    return {"pass_w_total": len(entries or []), "new_method_total": len(new), "count_by_rescue_basis": by,
            "secondary_reading_conflict_count": sum(1 for e in new if e.get("secondary_reading_conflict")),
            "garble_explained_count": sum(1 for e in new if "JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED" in (e.get("warning_labels") or []))}


def scan_v2beta_health(node) -> dict:
    """resultsを全走査(attempts_log含む)し、`ja_v2beta`記録の健全性を集計する(M-5: 『PRODUCTION_WIREDだが実は動いていない』を見落とさない)。"""
    h = {"attempt_records": 0, "active": 0, "disabled_by_constant": 0, "blocked_by_e3_e4": 0, "errors": 0, "error_samples": []}

    def walk(n):
        if isinstance(n, dict):
            v = n.get("ja_v2beta")
            if isinstance(v, dict) and ("judge_rule_version" in n or v.get("error") or v.get("disabled_by")):
                h["attempt_records"] += 1
                if v.get("active"):
                    h["active"] += 1
                if v.get("disabled_by"):
                    h["disabled_by_constant"] += 1
                if v.get("blocked_by"):
                    h["blocked_by_e3_e4"] += 1
                if v.get("error"):
                    h["errors"] += 1
                    if len(h["error_samples"]) < 5:
                        h["error_samples"].append(str(v["error"])[:200])
            # 採用entryのasr_judgementは、同じ判定がattempts_log内にも記録される(同一attemptの二重計上を避ける)。attempts_logにasr_judgementが
            # 1件でもあるnodeでは、node直下のasr_judgementを数えずattempts_log側を数える。attempts_logに無い(引継ぎ/旧形式)nodeは直下を数える。
            _skip_direct = any(isinstance(a, dict) and a.get("asr_judgement") for a in (n.get("attempts_log") or []) if isinstance(n.get("attempts_log"), list))
            for k, x in n.items():
                if k == "asr_judgement" and _skip_direct:
                    continue
                if isinstance(x, (dict, list)):
                    walk(x)
        elif isinstance(n, list):
            for x in n:
                if isinstance(x, (dict, list)):
                    walk(x)
    walk(node)
    return h


def collect_hr_items(run_dir: str) -> dict:
    """R-8: 要Human Review一覧。attempt単位のverdictではなく、実際のLock登録(<run_dir>/audit/review_lock_state.json の HUMAN_REVIEW_REQUIRED)と
    JA HR queue(HUMAN_REVIEW_LOG_PATH_JA)のうちwav_pathが当該run_dir配下の行から取る。読み取り失敗は error に記録(例外を投げない)。"""
    out = {"lock": [], "queue": [], "error": None}
    try:
        p = os.path.join(run_dir, "audit", "review_lock_state.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                for seg, v in (json.load(f) or {}).items():
                    if isinstance(v, dict) and v.get("state") == "HUMAN_REVIEW_REQUIRED":
                        out["lock"].append({"segment_id": v.get("segment_id") or seg, "language": v.get("language"), "reason": v.get("reason"),
                                            "wav_path": v.get("wav_path")})
        try:
            from er007_ja_secondary_asr_01 import HUMAN_REVIEW_LOG_PATH_JA as _q
        except Exception:
            _q = "er007_output/ja_asr_cascade_01/human_review_queue.jsonl"
        base = os.path.abspath(run_dir).replace("\\", "/").rstrip("/") + "/"
        if os.path.exists(_q):
            with open(_q, encoding="utf-8") as f:
                for line in f:
                    try:
                        r = json.loads(line)
                    except Exception:
                        continue
                    wp = os.path.abspath(str(r.get("wav_path") or "")).replace("\\", "/")
                    if wp.startswith(base):
                        out["queue"].append({"wav_path": r.get("wav_path"), "canonical_text": r.get("canonical_text"), "final_status": r.get("final_status"),
                                             "timestamp": r.get("timestamp")})
    except Exception as exc:  # noqa: BLE001  報告の失敗は生成を失敗させない
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def render_completion_block(entries, level_label: str, hr: dict | None = None, health: dict | None = None) -> str:
    """最終制作報告の完了ブロック(標準出力用の文)。0件でも『0件』と明記。導出失敗は『導出失敗(要確認)』。報告のみ。"""
    L = [f"【日本語ASR PASS_W(新方式)】{level_label}"]
    if isinstance(entries, ListeningListDerivationFailed):
        L.append(f"  導出失敗(要確認): 事後試聴リストを導出できませんでした(0件ではありません)。{entries.error}")
    else:
        new = [e for e in entries if e.get("rescue_basis")]
        s = summarize_entries(entries)
        L.append(f"  新方式(v2/β)のPASS_W: {len(new)}件 (β {s['count_by_rescue_basis'].get('beta', 0)} / v2 {s['count_by_rescue_basis'].get('v2', 0)} / "
                 f"Secondary読み相違あり {s['secondary_reading_conflict_count']} / 断片説明(garble) {s['garble_explained_count']}) "
                 f"※既存のPASS_WITH_WARNING全体: {len(entries)}件。試聴は推奨(任意)・制作/組立/納品候補作成は止めません。")
        if not new:
            L.append("  0件(該当なし)")
        for i, e in enumerate(new, 1):
            weak = {0: "読み相違あり(証拠が最も弱い)", 1: "断片説明(garble)", 2: "発音同一", 3: "その他"}.get(e.get("weak_rank"), "-")
            L.append(f"  {i}. [{e.get('rescue_basis')}/{weak}] {e.get('segment_id')} | 音声={e.get('audio_path')} sha={str(e.get('adopted_sha256'))[:12]}")
            L.append(f"       原稿: {e.get('canonical_text')}")
            L.append(f"       Primary: {e.get('primary_text')}  / Secondary: {e.get('secondary_text')}")
            L.append(f"       発生理由: {e.get('rescue_reason_ja')}")
            L.append(f"       警告: {', '.join(e.get('warning_labels') or [])}")
    if health is not None:
        L.append(f"  新方式の稼働状況: JA判定record {health.get('attempt_records', 0)}件 / 有効 {health.get('active', 0)} / 定数OFF {health.get('disabled_by_constant', 0)} / "
                 f"E3E4ブロック {health.get('blocked_by_e3_e4', 0)} / **無効化(エラーで従来判定へ戻った)件数 {health.get('errors', 0)}**"
                 + (f" 例: {health.get('error_samples')}" if health.get("errors") else ""))
    if hr is not None:
        if hr.get("error"):
            L.append(f"  要Human Review: 導出失敗(要確認) {hr['error']}")
        else:
            segs = sorted({x.get("segment_id") for x in hr["lock"]})
            L.append(f"  要Human Review(HR Lock登録 {len(hr['lock'])}件 / JA HR queue行 {len(hr['queue'])}件): "
                     + (", ".join(str(x) for x in segs) if segs else "なし"))
    return "\n".join(L)


def emit_completion_block(run_dir: str, level_label: str, stream=None) -> dict:
    """X/Y/Zの生成完了hook用。完了ブロックを標準出力へ出し、`audit/ja_v2beta_completion_block.json`へ同内容を保存する。**例外を投げない**(失敗は戻り値のerror)。"""
    rep = {"run_dir": run_dir, "label": level_label, "text": None, "json": None, "error": None}
    try:
        entries = load_listening_list(run_dir)
        hr = collect_hr_items(run_dir)
        src = os.path.join(run_dir, "audit", "tts_generation_results.json")
        health = None
        if os.path.exists(src):
            with open(src, encoding="utf-8") as f:
                health = scan_v2beta_health(json.load(f))
        text = render_completion_block(entries, level_label, hr, health)
        rep["text"] = text
        try:
            print(text, file=stream if stream is not None else sys.stdout)
        except UnicodeEncodeError:   # cp932等のコンソールで出せない文字があっても報告を落とさない(UTF-8で書き出す)
            sys.stdout.buffer.write((text + "\n").encode("utf-8"))
        data = {"label": level_label, "summary": summarize_entries(entries) if not isinstance(entries, ListeningListDerivationFailed) else None,
                "entries": [e for e in entries if e.get("rescue_basis")] if not isinstance(entries, ListeningListDerivationFailed) else None,
                "hr": hr, "health": health, "text": text}
        dst = os.path.join(run_dir, "audit", "ja_v2beta_completion_block.json")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        rep["json"] = dst
    except Exception as exc:  # noqa: BLE001
        rep["error"] = f"{type(exc).__name__}: {exc}"
        print(f"[WARN][pass_with_warning_registry] 完了ブロック出力に失敗(生成は継続): {run_dir}: {rep['error']}", file=sys.stderr)
    return rep
