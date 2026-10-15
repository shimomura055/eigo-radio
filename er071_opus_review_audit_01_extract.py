"""Read-only extractor of Claude Code session jsonl (KP-GLOSS-OPUS-REVIEW-ROOT-CAUSE-AUDIT-01).
Line-streams; extracts Agent tool_use (with subagent_type) and keyword-hit records."""
import argparse, json, sys

def blocks(rec):
    m = rec.get("message") or {}
    c = m.get("content")
    if isinstance(c, str):
        return [{"type": "text", "text": c}]
    return c if isinstance(c, list) else []

def text_of(b):
    if b.get("type") == "text": return b.get("text", "")
    if b.get("type") == "tool_use": return json.dumps(b.get("input", {}), ensure_ascii=False)
    if b.get("type") == "tool_result":
        c = b.get("content")
        if isinstance(c, list): return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
        return c if isinstance(c, str) else ""
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", nargs="+", required=True)
    ap.add_argument("--keywords", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-ts", default="")
    a = ap.parse_args()
    kws = [k for k in a.keywords.split(",") if k]
    out = {"keywords": kws, "records": [], "skipped_lines": 0, "scanned": 0}
    for src in a.src:
        with open(src, encoding="utf-8", errors="replace") as f:
            for ln, line in enumerate(f, 1):
                out["scanned"] += 1
                try: rec = json.loads(line)
                except Exception: out["skipped_lines"] += 1; continue
                ts = rec.get("timestamp", "")
                if a.min_ts and ts and ts < a.min_ts: continue
                for b in blocks(rec):
                    if not isinstance(b, dict): continue
                    t = text_of(b)
                    kind = None
                    inp = b.get("input") if b.get("type") == "tool_use" else None
                    if inp and b.get("name") in ("Agent", "Task"):
                        kind = "agent_call:" + str(inp.get("subagent_type"))
                        if inp.get("subagent_type") != "opus-consultant" and not any(k in t for k in kws[1:]):
                            continue
                    elif b.get("type") == "tool_result" and any(k in t for k in kws[1:]):
                        kind = "tool_result"
                    elif rec.get("type") == "assistant" and b.get("type") == "text" and any(k in t for k in kws[1:]):
                        kind = "assistant_text"
                    else:
                        continue
                    out["records"].append({"src": src.split("projects")[-1], "line": ln, "uuid": rec.get("uuid"), "ts": ts,
                        "role": rec.get("type"), "kind": kind, "tool_use_id": b.get("id") or b.get("tool_use_id"),
                        "text": t})
    out["records"].sort(key=lambda r: r["ts"])
    with open(a.out, "w", encoding="utf-8") as f: json.dump(out, f, ensure_ascii=False, indent=1)
    print("records", len(out["records"]), "skipped", out["skipped_lines"], "scanned", out["scanned"])
main()
