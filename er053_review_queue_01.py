# -*- coding: utf-8 -*-
"""er053_review_queue_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1(追加のみ、2026-10-10)。Post-EN Review Queue module。

Risk Flagger(er053_risk_flagger_production_01)の結果を、人間(ChatGPT側Human Review)が読める形で保存する。

配置(ルートは__file__基準。os.getcwd()に依存しない):
  review_queue/post_en/<article_id>/<article_level>__<rf_run_id>/
      queue.json            (schema下記)
      queue.md              (人間/ChatGPT向けの読みやすい一覧)
      inputs/sentences.json (文ID付きの記事全文)
      inputs/ledger.txt     (RFに渡した完全台帳)
      raw/<model_key>_<A3|A4>.jsonl (生API応答。条件ごと)
  review_queue/post_en/index.jsonl  (追記専用。1行=1 (記事,Level,RF run)。index.jsonl.lock でO_EXCL排他)
  review_queue/post_en/README.md

queue.jsonは**候補一覧**に徹する。`review_state`(人間の判定状態)は持たない(判定はChatGPT側が保持)。
issue_id は <article_id>__<article_level>__<article_sha256先頭8桁>__<rf_run_id>__<sentence_id>(分解せず、
各フィールドも個別に保持する)。
保存失敗時は例外を伝播させず、out_dir/risk_flagger_fallback/ へ同じ内容を保存し、WARNを出し、
entry_point.json に記録する(Review Queue保存失敗でProductionを止めない=非Blocking)。
このmoduleはgitを触らない(push運用はOPEN-245)。
"""
from __future__ import annotations

import json
import os
import re
import time

SCHEMA_VERSION = "review_queue_post_en_v1"
HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE_ROOT = os.path.join(HERE, "review_queue", "post_en")
INDEX_NAME = "index.jsonl"
LOCK_TIMEOUT_S = 10.0
LOCK_STALE_S = 300.0
CONTEXT_SENTENCES = 2

_SAFE_RE = re.compile(r"[^A-Za-z0-9._\-]")


def derive_article_id(out_dir: str) -> str:
    """writer/audioで共通に使う記事ID: out_dirのbasename(audio runnerの`FAMILY_X_AUDIO_{basename(out_dir)}_{level}`と同じ素材)。"""
    return os.path.basename(os.path.normpath(out_dir))


def safe_component(s: str) -> str:
    """ディレクトリ名として安全な文字列にする(パス区切り・..を含められない)。"""
    c = _SAFE_RE.sub("_", s or "")
    while ".." in c:
        c = c.replace("..", "_")
    c = c.strip(".") or "_"
    return c[:120]


def queue_dir(article_id: str, article_level: str, rf_run_id: str, root: str = QUEUE_ROOT) -> str:
    return os.path.join(root, safe_component(article_id), f"{safe_component(article_level)}__{safe_component(rf_run_id)}")


def make_issue_id(article_id, article_level, article_sha256, rf_run_id, sentence_id) -> str:
    return f"{article_id}__{article_level}__{article_sha256[:8]}__{rf_run_id}__{sentence_id}"


# ------------------------------------------------------------
# queue.json の組立
# ------------------------------------------------------------
def build_queue(result: dict) -> dict:
    """RF結果dict -> queue.json用dict(review_stateなし)。LLM入力には無かった前後文脈(最大2文)はここで付与する。"""
    sents = result.get("sentences", [])
    idx = {s["sid"]: i for i, s in enumerate(sents)}
    facts_by = {f["fact_id"]: f["text"] for f in result.get("facts", [])}
    raw_files = {}
    for rr in result.get("raw", []):
        raw_files.setdefault((rr["model_key"], rr["condition"]), f"raw/{rr['model_key']}_{rr['condition']}.jsonl")
    issues = []
    for it in result.get("issues", []):
        i = idx[it["sentence_id"]]
        before = [s["text"] for s in sents[max(0, i - CONTEXT_SENTENCES):i]]
        after = [s["text"] for s in sents[i + 1:i + 1 + CONTEXT_SENTENCES]]
        detected = []
        for d in it["detected_by"]:
            detected.append({**d, "raw_flag_source": raw_files.get((d["model_key"], d["condition"]))})
        issues.append({
            "issue_id": make_issue_id(result["article_id"], result["article_level"], result["article_sha256"],
                                      result["rf_run_id"], it["sentence_id"]),
            "article_id": result["article_id"], "article_level": result["article_level"],
            "article_sha256": result["article_sha256"], "run_id": result["rf_run_id"],
            "timestamp": result["timestamp"], "sentence_id": it["sentence_id"], "sentence_text": it["sentence_text"],
            "context": {"before": before, "after": after, "note": "Queue生成時のみ付与。LLM入力には含まれていない"},
            "related_fact_ids": it["related_fact_ids"],
            "facts": [{"fact_id": fid, "text": facts_by.get(fid, "")} for fid in it["related_fact_ids"]],
            "flag_reasons": it["flag_reasons"], "detected_by": detected, "confidence": it["confidence"],
        })
    return {
        "schema_version": SCHEMA_VERSION, "article_id": result["article_id"], "article_level": result["article_level"],
        "article_sha256": result["article_sha256"], "ledger_sha256": result.get("ledger_sha256"), "run_id": result["rf_run_id"],
        "timestamp": result["timestamp"], "status": result["status"], "reason": result.get("reason"),
        "splitter_version": result.get("splitter_version"), "producer": result.get("producer"), "run_label": result.get("run_label"),
        "sentence_count": len(sents), "fact_count": len(result.get("facts", [])),
        "conditions": [{k: c.get(k) for k in ("model_key", "condition", "model_id_requested", "model_id_returned", "status",
                                              "reason", "api_calls", "input_tokens", "output_tokens", "cached_tokens",
                                              "cost_jpy", "flag_count", "system_prompt_sha256", "model_mismatch")}
                       for c in result.get("conditions", [])],
        "issues": issues, "unlocated_flags": result.get("unlocated_flags", []),
        "model_stats": result.get("model_stats", {}), "warnings": result.get("warnings", []),
    }


def render_markdown(q: dict) -> str:
    L = []
    L.append(f"# Post-EN Risk Flagger Review Queue: {q['article_id']} / {q['article_level']}")
    L.append("")
    L.append(f"- run_id: `{q['run_id']}`  status: **{q['status']}**" + (f"  reason: {q['reason']}" if q.get("reason") else ""))
    L.append(f"- article_sha256: `{q['article_sha256']}`  ledger_sha256: `{q.get('ledger_sha256')}`")
    L.append(f"- level: `{q['article_level']}` (b1b=Advanced, a2=Standard)  splitter: `{q.get('splitter_version')}`  "
             f"producer: `{q.get('producer')}`  run_label: `{q.get('run_label')}`")
    L.append(f"- sentences: {q['sentence_count']}  facts: {q['fact_count']}  candidate issues: {len(q['issues'])}")
    L.append("")
    L.append("これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。")
    L.append("")
    L.append("## Conditions")
    for c in q["conditions"]:
        L.append(f"- {c['model_key']} {c['condition']}: {c['status']} flags={c['flag_count']} cost_jpy={c['cost_jpy']} "
                 f"model={c.get('model_id_returned') or c.get('model_id_requested')}" + (f" ({c['reason']})" if c.get("reason") else ""))
    L.append("")
    L.append("## Issues")
    if not q["issues"]:
        L.append("(候補なし)")
    for it in q["issues"]:
        L.append("")
        L.append(f"### {it['sentence_id']}  (confidence max {it['confidence']})")
        L.append(f"- issue_id: `{it['issue_id']}`")
        L.append(f"- sentence: {it['sentence_text']}")
        if it["context"]["before"]:
            L.append("- before: " + " / ".join(it["context"]["before"]))
        if it["context"]["after"]:
            L.append("- after: " + " / ".join(it["context"]["after"]))
        L.append("- detected_by: " + ", ".join(f"{d['model_key']}-{d['condition']}({d['confidence']})" for d in it["detected_by"]))
        for r in it["flag_reasons"]:
            L.append(f"- reason [{r['type']}]: {r['question']}")
        for f in it["facts"]:
            L.append(f"- fact {f['fact_id']}: {f['text']}")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------
# ファイル書込(原子的)・index追記(lock付き)
# ------------------------------------------------------------
def _atomic_write(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def write_queue_files(base: str, result: dict, q: dict):
    _atomic_write(os.path.join(base, "queue.json"), json.dumps(q, ensure_ascii=False, indent=2))
    _atomic_write(os.path.join(base, "queue.md"), render_markdown(q))
    _atomic_write(os.path.join(base, "inputs", "sentences.json"),
                  json.dumps([{"sid": s["sid"], "text": s["text"]} for s in result.get("sentences", [])], ensure_ascii=False, indent=2))
    _atomic_write(os.path.join(base, "inputs", "ledger.txt"), result.get("ledger_text", ""))
    by = {}
    for rr in result.get("raw", []):
        by.setdefault((rr["model_key"], rr["condition"]), []).append(rr)
    for (mk, cd), rows in by.items():
        _atomic_write(os.path.join(base, "raw", f"{mk}_{cd}.jsonl"),
                      "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


class _IndexLock:
    def __init__(self, path: str, timeout: float = LOCK_TIMEOUT_S, stale: float = LOCK_STALE_S, sleep=time.sleep):
        self.path, self.timeout, self.stale, self.sleep = path, timeout, stale, sleep
        self.fd = None

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        t0 = time.time()
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.fd, str(os.getpid()).encode())
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.path) > self.stale:
                        os.remove(self.path)         # 古い(異常終了で残った)lockのみ除去
                        continue
                except OSError:
                    pass
                if time.time() - t0 > self.timeout:
                    raise TimeoutError(f"index lock timeout: {self.path}")
                self.sleep(0.05)

    def __exit__(self, *a):
        try:
            if self.fd is not None:
                os.close(self.fd)
        finally:
            try:
                os.remove(self.path)
            except OSError:
                pass


def append_index(root: str, entry: dict, lock_timeout: float = LOCK_TIMEOUT_S):
    """index.jsonl に1行追記(既存行は不変)。1行1write+fsync。"""
    os.makedirs(root, exist_ok=True)
    p = os.path.join(root, INDEX_NAME)
    line = (json.dumps(entry, ensure_ascii=False) + "\n").encode("utf-8")
    with _IndexLock(p + ".lock", timeout=lock_timeout):
        with open(p, "ab") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())


def read_index(root: str = QUEUE_ROOT) -> list:
    p = os.path.join(root, INDEX_NAME)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def index_entry(q: dict, rel_path: str, result: dict) -> dict:
    return {"article_id": q["article_id"], "article_level": q["article_level"], "article_sha256": q["article_sha256"],
            "run_id": q["run_id"], "timestamp": q["timestamp"], "status": q["status"], "reason": q.get("reason"),
            "issue_count": len(q["issues"]), "queue_path": rel_path, "producer": q.get("producer"), "run_label": q.get("run_label"),
            "splitter_version": q.get("splitter_version"),
            "cost_jpy": round(sum((c.get("cost_jpy") or 0) for c in q["conditions"]), 6)}


# ------------------------------------------------------------
# 保存(非Blocking)
# ------------------------------------------------------------
def save_queue(result: dict, out_dir: str = None, root: str = QUEUE_ROOT) -> dict:
    """RF結果をReview Queueへ保存する。**例外を伝播させない**。
    成功: {"saved": True, "path": <queue dir>, "fallback": False}
    失敗: out_dir/risk_flagger_fallback/<level>__<rf_run_id>/ へfallback保存し WARN、entry_point.jsonへ記録。
          {"saved": False, "fallback": True/False, "fallback_path": ..., "error": ...}"""
    out = {"saved": False, "path": None, "fallback": False, "fallback_path": None, "error": None}
    try:
        q = build_queue(result)
        base = queue_dir(result["article_id"], result["article_level"], result["rf_run_id"], root)
        write_queue_files(base, result, q)
        rel = os.path.relpath(base, root).replace("\\", "/")
        append_index(root, index_entry(q, rel, result))
        out.update(saved=True, path=base)
        return out
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {str(e)[:200]}"
    print(f"[WARN][ReviewQueue] 保存に失敗しました({out['error']})。out_dirのfallbackへ保存します(非Blocking)。")
    try:
        if out_dir:
            fb = os.path.join(out_dir, "risk_flagger_fallback", f"{safe_component(result.get('article_level', ''))}__{safe_component(result.get('rf_run_id', ''))}")
            write_queue_files(fb, result, build_queue(result))
            out.update(fallback=True, fallback_path=fb)
    except Exception as e2:  # noqa: BLE001
        out["error"] += f" | fallback_failed: {type(e2).__name__}: {str(e2)[:100]}"
    if out_dir:
        try:
            p = os.path.join(out_dir, "entry_point.json")
            data = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
            data.setdefault("risk_flagger_queue", {})[result.get("article_level", "?")] = {
                "saved": False, "error": out["error"], "fallback_path": out["fallback_path"], "rf_run_id": result.get("rf_run_id")}
            os.makedirs(out_dir, exist_ok=True)
            tmp = p + f".tmp{os.getpid()}"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, p)
        except Exception:  # noqa: BLE001
            pass
    return out
