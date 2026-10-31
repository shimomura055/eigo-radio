# FX-UNTIDINESS-COMMENT4-JA-GLOSS-FIX-01 委任_01
# 既存の訳生成関数 er135_enduser_translate_01.translate_part を、対象part(adv_19=Comment 4)に限定して再実行する。
# 変更点は「Promptの文脈欄(直前partの英文)と指摘欄(既存のretry指摘枠)に追加する」ことだけ。Prompt雛形・検査・対訳照合・cache保存は既存どおり(雛形の一般変更なし)。
# 使い方: python retranslate_part_01.py --cache-dir <enduser_sync_cache> --article <enduser/data/article.json> --out <evidence dir> [--dry]
import argparse, json, os, sys, time
sys.path.insert(0, os.getcwd())
import er135_enduser_translate_01 as TR

NOTE = ("『things left out』は、片づけられずに出したまま・置きっぱなしになっている物(直前のパートの『working things left out』=働く出しっぱなし)の意味。"
        "『省かれた』『省略された』『除外された』と訳さない。")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--article", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--level", default="adv")
    ap.add_argument("--part", default="adv_19")
    ap.add_argument("--ctx-part", default="adv_18")
    ap.add_argument("--sid-note", default="adv_19-s044")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    art = json.load(open(a.article, encoding="utf-8"))
    parts = {p["key"]: p for p in art["levels"][a.level]["parts"]}
    p, cp = parts[a.part], parts[a.ctx_part]
    sents = [{"sid": s["sid"], "en": s["text"], "para": pi} for pi, para in enumerate(p["paragraphs"]) for s in para]
    ctx = [{"sid": s["sid"], "en": s["text"]} for para in cp["paragraphs"] for s in para]
    note_idx = [i for i, s in enumerate(sents) if s["sid"] == a.sid_note][0]
    os.makedirs(a.out, exist_ok=True)
    doc = TR.load_generated(a.cache_dir)
    key = TR.para_key(TR._paragraphs(TR._clean_sentences(sents))[0])
    old = doc["entries"].get(key)
    json.dump({"cache_key": key, "old_entry": old}, open(os.path.join(a.out, "old_entry.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log = []

    class Wrap:
        def __init__(self):
            self.inner = None if a.dry else TR.DefaultLLM()
            self.calls = []
        def __call__(self, kind, prompt):
            if kind == "translate":
                if TR.TRANSLATE_CONTEXT_LABEL not in prompt:
                    prompt = prompt.replace(TR.TRANSLATE_TARGET_LABEL,
                                            TR.TRANSLATE_CONTEXT_LABEL + "\n".join(f"- {s['en']}" for s in ctx) + "\n\n" + TR.TRANSLATE_TARGET_LABEL, 1)
                prev = (old or {}).get("ja", [None] * (note_idx + 1))[note_idx]
                line = f"- {note_idx + 1}番: {NOTE}" + (f"(前回の訳: {prev})" if prev else "") + "\n"
                if TR.RETRY_NOTE_LABEL in prompt:
                    prompt = prompt.replace(TR.RETRY_NOTE_LABEL, TR.RETRY_NOTE_LABEL + line, 1)
                else:
                    prompt = prompt.replace(TR.TRANSLATE_BODY, "\n" + TR.RETRY_NOTE_LABEL + line + TR.TRANSLATE_BODY, 1)
            log.append({"kind": kind, "prompt": prompt})
            if a.dry:
                raise SystemExit("dry: prompt only\n" + prompt)
            r = self.inner(kind, prompt)
            self.calls = self.inner.calls
            log[-1]["response"] = r
            return r
    w = Wrap()
    if old is not None:
        del doc["entries"][key]
        TR.save_generated(a.cache_dir, doc)   # 旧entryを除去(old_entry.jsonに保存済み)。translate_partが新規生成して再保存する
    try:
        res = TR.translate_part(f"{a.level}:{a.part}", sents, level=a.level, family="X", cache_dir=a.cache_dir, llm=w)
    finally:
        json.dump(log, open(os.path.join(a.out, "llm_log.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(res, open(os.path.join(a.out, "result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    print("calls", w.calls and [(c["kind"], c["cost_jpy"]) for c in w.calls])

if __name__ == "__main__":
    main()
