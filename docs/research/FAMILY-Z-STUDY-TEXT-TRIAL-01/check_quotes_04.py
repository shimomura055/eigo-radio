# 決定論的な引用逐語一致照合(DEV、評価時のみ。check_quotes_03と同ロジック)。OUTPUT_04_*_USER.md の英語スパン(5語以上)が本文に逐語で存在するかを確認。Part 4と「比較用」行は対象外。
# 使い方: py check_quotes_04.py   -> quote_check_04.json
import re, sys, os, json
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
import run_trial_04 as t4
def norm(s): return re.sub(r"\s+", " ", s.replace("’","'").replace("‘","'").replace("“",'"').replace("”",'"').replace("*","")).strip().lower()
res = {}
for f in sorted(os.listdir(BASE)):
    m = re.match(r"OUTPUT_04_(gift|ig_nobel|open_window)_(.+)_USER\.md", f)
    if not m: continue
    src = norm(t4.work_data(m.group(1))["text"])
    out = open(os.path.join(BASE, f), encoding="utf-8").read().split("## Part 4")[0]
    ok = 0; bad = []; comp = []
    for line in out.splitlines():
        for sp in re.findall(r"[A-Za-z0-9’‘“”\"'\-—,.;:!?() ]{20,}", line):
            sp = sp.strip(" ,;:()*")
            if len(re.findall(r"[A-Za-z]+", sp)) < 5: continue
            n2 = norm(sp).strip('" ,.;:!?')
            if n2 in src: ok += 1
            elif "比較" in line: comp.append(sp)
            else: bad.append(sp)
    res[f] = {"verbatim_ok": ok, "not_found_non_comparison": bad, "comparison_or_other": comp}
json.dump(res, open(os.path.join(BASE, "quote_check_04.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f, v in res.items(): print(f, "ok", v["verbatim_ok"], "NOTFOUND", len(v["not_found_non_comparison"]))
