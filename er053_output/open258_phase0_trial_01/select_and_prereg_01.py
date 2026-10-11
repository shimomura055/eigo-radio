import sys, math, json, hashlib
sys.path.insert(0, "er053_output/open258_phase0_trial_01")
from open258_phase0_common import *

rows = json.load(open(OUT + "/manifest_all_candidates_01.json", encoding="utf8"))
W = json.load(open(OUT + "/whisper_aux_01.json", encoding="utf8"))
CAP = 4.6   # 保守見積(秒切上げ)の計画上限。5円上限に対し約8%の余裕
C_PRIORITY = [12, 3, 4, 5, 1, 6, 22, 42]
sel = []
for r in rows:
    r = dict(r)
    if r.get("audio_missing"):
        r["plan_call"] = False; r["plan_reason"] = "音声欠落"; r["role_run"] = r["role"]; sel.append(r); continue
    k = f'g{r["group"]}_{r["seg"]}_a{r["attempt"]}'
    w = W[k]; r["whisper"] = {"small": w["small"], "medium": w["medium"], "agree_any": w["agree_any"], "agree_both": w["agree_both"]}
    if r["role"] == "A_meta": r["role_run"] = "A_meta"
    else: r["role_run"] = "B_rescue_candidate" if w["agree_any"] else "C_negative"
    sel.append(r)
spent = 0.0
def take(r, reason, role=None):
    global spent
    c = math.ceil(r["duration_s"]) * JPY_PER_SEC
    if spent + c > CAP: r["plan_call"] = False; r["plan_reason"] = "予算上限(計画CAP)のため今回対象外"; return False
    spent += c; r["plan_call"] = True; r["plan_reason"] = reason
    if role: r["role_run"] = role
    return True
def elig(r): return not r.get("duplicate_of") and not r.get("audio_missing") and not r["existing_exclusions"] and "plan_call" not in r
def pick(g, seg=None, att=None):
    return [r for r in sel if r["group"] == g and (att is None or r["attempt"] == att) and elig_or_probe(r)]
def elig_or_probe(r): return not r.get("duplicate_of") and not r.get("audio_missing") and "plan_call" not in r
def run(items, reason, role=None, need=None):
    for r in items:
        if need and r["role_run"] != need: continue
        if r["existing_exclusions"] and role != "P_exclusion_probe": continue
        take(r, reason, role)
RC = "V1対象(既存ルールで除外なし)"
run([r for r in sel if r["role_run"] == "A_meta" and elig_or_probe(r)], RC + "(出演/出現3 attempt)")
# C: 誤PASS検証(TTS誤り代理)。ユーザー命名例(縛られず/体内時計)優先
for g, att in [(12, None), (3, None), (4, None), (5, 1), (6, 1)]:
    run(pick(g, att=att), RC + "・誤PASS検証用(whisper small/medium とも原稿と不一致=TTS誤り候補)", need="C_negative")
# B: 14群救済候補(短尺順)。g21(19秒)は最後に回す
Bsel = [r for r in sel if r["role_run"] == "B_rescue_candidate" and elig_or_probe(r) and r["group"] not in (21, 22, 1, 36)]
run(sorted(Bsel, key=lambda r: r["duration_s"]), RC + "。救済候補=whisper small/mediumのいずれかが原稿に一致")
run(pick(36), RC + "。救済候補(%→パーセント差)")
# 除外規則プローブ(14群中のg7: ratio<0.4除外の妥当性)
run(pick(7), "既存除外(ratio<0.4)該当だが14群の一員。除外の妥当性確認用プローブ(Production手順では呼ばない)", "P_exclusion_probe")
run(pick(21), RC + "。救済候補(長尺19秒)")
run(pick(5, att=2) + pick(6, att=2), RC + "・誤PASS検証用(追加)", need="C_negative")
run(pick(1), RC + "。救済候補(whisper mediumのみ一致=曖昧)")
run(pick(42) + pick(6, att=4), "既存除外該当だが除外妥当性確認用プローブ(Production手順では呼ばない)", "P_exclusion_probe")
for r in sel:
    if "plan_call" not in r:
        r["plan_call"] = False
        r["plan_reason"] = "sha重複(同一音声は1回のみ): " + str(r.get("duplicate_of")) if r.get("duplicate_of") else ("既存除外該当のため呼ばない: " + ",".join(r["existing_exclusions"]) if r.get("existing_exclusions") else "計画対象外")
json.dump(sel, open(OUT + "/manifest_selected_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
calls = [r for r in sel if r.get("plan_call")]
sec = sum(r["duration_s"] for r in calls); secc = sum(math.ceil(r["duration_s"]) for r in calls)
est = sec * JPY_PER_SEC; estc = secc * JPY_PER_SEC
mh = hashlib.sha256(open(OUT + "/manifest_selected_01.json", "rb").read()).hexdigest()
L = []
L.append("# PREREGISTRATION_01 (OPEN-258-JA-SECONDARY-ASR-PHASE0-TRIAL-01 委任_01)")
L.append("")
L.append("作成: 2026-10-11 / Azure実行前に確定。Trial専用(Production未変更)。Secondary=Azure STT(ja-JP、Phrase Listなし、1音声1回)。")
L.append("使用モデル: Primary=既存ログのgpt-4o-mini-transcribe(再実行しない)、Secondary=Azure Speech STT(既存SDK関数再利用)、補助=faster-whisper small/medium(無料ローカル)。最新モデル原則: 新規LLM呼び出しなし(Secondaryは検証対象方式そのもの)。")
L.append(f"manifest_selected_01.json sha256: `{mh}`(manifest_all_candidates_01.json=全候補、whisper_aux_01.json=補助転写)")
L.append("")
L.append("## 原稿の確定方法")
L.append("各segmentの原稿は、attempt_history.jsonl/lock stateの`canonical_text_sha256`とsha256が一致する文字列をrun dir内から探して確定(複数ヒット時はPrimary転写に最近接)。設計書の『後で合格したattemptのASR文字列』(proxy)は原稿ではない場合があり(例: g23は原稿=焙煎前、proxy=倍線前)、本Trialは確定原稿を使う。META 3件は設計書記載の原稿。")
L.append("")
L.append("## 判定手順(V1)")
L.append("1. Primary NG(TRUE_CONTENT_MISMATCH、既存classify_ja_asr_match、Resolver LLM=OFFで現行コード再判定)。")
L.append("2. 既存除外: 数字不一致/否定不一致(protected_check_ja)・全体類似度<0.4・instruction echo・現行コードでTCMでない -> Secondaryを呼ばない。")
L.append("3. 追加除外(設計書4節、Phase1候補の新規小ルール): 単独格助詞1文字replace、差分に漢数字/年月日を含む。集計は「既存除外のみ」と「追加除外あり」の2通り。呼び出しは既存除外のみで決め、追加除外該当でもSecondaryは実行して結果を記録する(追加ルール必要性の評価)。")
L.append("4. Azure Secondary(p4.get_full_text_via_azure_stt_continuous、ja-JP、Phrase Listなし)を1音声1回。")
L.append("5. classify_ja_asr_match(原稿, Secondary転写)が EXACT_MATCH/NORMALIZED_MATCH -> SCG-PASS候補。それ以外(PHONETIC_MATCH含む)はNG(従来の再生成/STOP維持)。取得不能もNG扱い。")
L.append("")
L.append("## 誤PASS定義・ground truth代理")
L.append("誤PASS=音声が原稿と実際に異なるのにSecondaryがSCG-PASSにしたもの。Role=C(whisper small・medium(原稿非提示)がともに原稿と不一致、かつPrimary転写も原稿と不一致、後の別attemptで原稿通りに合格または別の誤り)を『TTS誤りの代理』とし、C群でSecondaryがPASSしたら**1件でも即STOP**。Role=Bは『whisper small/mediumのいずれかが原稿に一致=TTS正の可能性』の代理で、真のground truthではない(確定はユーザー試聴のみ。META 3件はユーザー試聴で出演確認済み)。")
L.append("")
L.append("## 費用見積")
L.append(f"単価: Azure STT ${USD_PER_HOUR}/hour(登録単価) x {JPY_PER_USD}円/USD = {JPY_PER_SEC:.5f}円/秒(Azure実請求は未確認)。")
L.append(f"呼び出し予定 {len(calls)}回 / 音声合計 {sec:.1f}秒 -> 約{est:.2f}円。各回を秒切上げした保守見積 {secc}秒 -> **{estc:.2f}円**(上限5円、実行中はcall前に累計(切上げ秒)を確認し5円超見込みで中止)。")
L.append(f"判定: {'上限内(実行可)' if estc <= BUDGET_JPY else '上限超過 -> STOP'}")
L.append("")
L.append("## 対象音声一覧(全候補。call=Yのみ実行)")
L.append("Role: A_meta=出演/出現3attempt、B=救済候補(TTS正の代理)、C=誤PASS検証(TTS誤りの代理)、P=除外規則プローブ。g=OPEN258_OFFLINE_EVIDENCE_01.jsonのgroup index。")
L.append("")
L.append("| g | role | seg#att | wav | sha256(先頭12) | 秒 | 原稿 | Primary転写 | 現行判定 | 既存除外 | 追加除外 | whisper small / medium | call | 理由 |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in sel:
    if r.get("audio_missing"):
        L.append(f"| {r['group']} | {r['role']} | {r['seg']}#{r['attempt']} | (欠落) | | | | | | | | | N | 音声欠落 |"); continue
    wsm = r["whisper"]
    L.append(f"| {r['group']} | {r['role_run']} | {r['seg']}#{r['attempt']} | `{r['wav']}` | {r['sha256'][:12]} | {r['duration_s']} | {r['canonical'][:50]} | {r['primary_asr'][:50]} | {r['primary_cls']} | {r['existing_exclusions'] or '-'} | {r['extra_exclusions'] or '-'} | {wsm['small']['text'][:40]} / {wsm['medium']['text'][:40]} | {'Y' if r['plan_call'] else 'N'} | {r['plan_reason'][:70]} |")
open(OUT + "/PREREGISTRATION_01.md", "w", encoding="utf8").write("\n".join(L) + "\n")
print("calls", len(calls), "sec", round(sec, 1), "ceil_sec", secc, "est_yen", round(est, 2), "ceil_est_yen", round(estc, 2))
from collections import Counter
print(Counter(r["role_run"] for r in calls))
