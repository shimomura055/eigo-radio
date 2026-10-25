# 補足(事前登録の合否基準外): E4でPASS→Cascadeに変わる実データ4行(保存Secondary転写なし)に、Azure応答を『注入』して、Cascade後の判定が既存どおりに動くことを示す。
# 注入=評価用stub(ネットワーク呼出0)。A=Azureが原稿どおり(canonicalと同一)を返した場合 / B=AzureがPrimaryと同じ誤り転写を返した場合。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open333_e4_inject_01.py
import contextlib, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import proto_open333_fix_06 as P6
import er007_ja_secondary_asr_01 as sec

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
d = json.load(open(D + "open333_e4_eval_01.out.json", encoding="utf8"))
targets = [r for r in d["real"] if r["HEAD"]["klass"] == "PASS" and r["F06_E4"]["klass"] == "CASC"]
E.api0_guard_on()


def judge(canon, prim, sec_text, arm):
    orig = sec._azure_stt_strict
    sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (sec_text, None)
    cm = P6.apply_in_process(arm) if arm else contextlib.nullcontext()
    try:
        with cm:
            r = sec.evaluate_attempt_ja_with_cascade_detail(canon, prim, E.dummy_wav(), cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig
    j = r["asr_judgement"]
    return j["state"], j["reason_code"], (j.get("warnings") or [])


print(f"対象 {len(targets)}行(HEAD=PASS, E4=Cascade, 保存Secondary転写なし)")
for r in targets:
    c, p = r["canon"], r["asr"]
    print(f"\n{r['id'][-40:]}  canon={c[:30]}  primary={p[:30]}")
    for nm, st in (("A:Azureが原稿どおり", c), ("B:AzureがPrimaryと同じ誤り", p)):
        h = judge(c, p, st, None)
        a = judge(c, p, st, "E4_E4N")
        print(f"   {nm:24s} HEAD={h[0]}/{h[1]}   E4(+E4N)={a[0]}/{a[1]} {a[2]}")
E.api0_guard_off()
