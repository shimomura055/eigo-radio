# -*- coding: utf-8 -*-
"""ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04B Trial A(費用0円、既存転写+既存validator純関数のみ、API呼出なし)。
既存音声のNG判定を、保存済みPrimary/Azure転写とlocal whisper(small/medium)転写の突合で分類し、統一フロー
(Primary -> NGならSecondary -> どちらかPASSで採用 -> 両NGで再生成)ならどう判定されたかを表にする。
出力: er058_output/trial_abc/trial_a_tables_01.md (TRIAL_A_EXISTING_AUDIO_01.md の素材)。read-only。
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "er058_output", "trial_abc")
import er007_ja_asr_validator_01 as javal  # noqa

lines = []
P = lambda s="": lines.append(s)  # noqa

# ---------------- A-1 日本語(Phase 0 25音声) ----------------
rep = json.load(open(os.path.join(ROOT, "er056_output", "asr_tts_cross_language_reconciliation_01", "ja_offline_replay_01.json"), encoding="utf-8"))
wh = json.load(open(os.path.join(ROOT, "er053_output", "open258_phase0_trial_01", "whisper_aux_01.json"), encoding="utf-8"))
G8_LIKE = {"g8_kp4_ja_charon_a1"}
NEEDS_LISTEN = {"g11_kp5_ja_aoede_a1", "g27_kp1_ja_charon_a1", "g18_meaning_2_a2", "g18_meaning_2_a3", "g1_meaning_4_a1"}


def jcls(canon, asr):
    c = javal.classify_ja_asr_match(canon, asr, allow_reading_resolver=False)
    return c.classification, bool(c.should_pass)


def classify_row(key, gt, p_pass, s_pass, w_small, w_med):
    """NG/救済の原因分類(代理ラベルによる。人間試聴は未実施)。"""
    if gt == "correct_user" and not p_pass:
        return "Primary側のASR誤認(ユーザー試聴で出演を確認済み=偽NG)"
    if gt == "error_proxy":
        return "真の誤読(代理: whisper 2モデル+Primaryが原稿と不一致、Azureも原稿と不一致)"
    if key in NEEDS_LISTEN:
        return "未確定(要試聴): Azure PASSだがPrimary/whisperは原稿と不一致"
    if p_pass:
        return "(Primary PASS: NG無し)"
    if s_pass and (w_small or w_med):
        return "Primary側のASR誤認(Azure+whisperが原稿と一致=偽NG)"
    if s_pass:
        return "未確定(要試聴): Azureのみ原稿一致"
    if w_small and w_med:
        return "Validator厳格/表記差(Azureも原稿と不一致だがwhisper 2モデルは原稿一致)"
    if w_small or w_med:
        return "未確定(要試聴): whisper片方のみ原稿一致"
    return "未確定(要試聴): 全ASRが原稿と不一致(真の誤読 or 共通ASR誤認、区別不能)"


P("### A-1. 日本語 Phase 0 25音声(統一フロー適用。Azureは保存済み転写=Phrase Listなし)")
P("統一フロー判定 = Primary PASSなら採用 / Primary NGでAzure PASSなら採用 / 両NGなら再生成。現行(CURRENT)は SCG除外(C1等)でAzureを呼ばない場合があるため、現行結果も併記(replay JSONの値)。")
P("")
P("| key | GT代理 | 原稿 | Primary転写→判定 | Azure転写→判定 | whisper small/medium | 統一フロー | 現行(CURRENT) | NG原因分類 |")
P("|---|---|---|---|---|---|---|---|---|")
flow_counts = {}
rows_out = []
for r in rep["rows"]:
    key, gt = r["key"], r["gt"]
    pc, pp = jcls(r["canonical"], r["primary"])
    sc, sp = jcls(r["canonical"], r["secondary"])
    sp = sp and sc in ("EXACT_MATCH", "NORMALIZED_MATCH")  # Secondaryは厳格PASS集合のみ(現行SCGと同じ)
    w = wh.get(key, {})
    ws = bool(w.get("small", {}).get("agrees_with_canonical"))
    wm = bool(w.get("medium", {}).get("agrees_with_canonical"))
    if pp:
        flow = "採用(Primary)"
    elif sp:
        flow = "採用(Secondary)"
    else:
        flow = "NG(再生成)"
    cur_txt = ("PASS" if r["pass_CURRENT"] else ("Azure不呼出(除外:" + str(r["excl_CURRENT"]) + ")" if not r["call_CURRENT"] else "NG"))
    cat = classify_row(key, gt, pp, sp, ws, wm)
    flow_counts[(gt, flow)] = flow_counts.get((gt, flow), 0) + 1
    rows_out.append(dict(key=key, gt=gt, primary=r["primary"], azure=r["secondary"], pc=pc, sc=sc, ws=ws, wm=wm, flow=flow, cat=cat))
    esc = lambda t: (t or "").replace("|", "/")  # noqa
    P(f"| {key} | {gt} | {esc(r['canonical'])[:30]} | {esc(r['primary'])[:30]} [{'PASS' if pp else 'NG'}:{pc[:12]}] | {esc(r['secondary'])[:30]} [{'PASS' if sp else 'NG'}:{sc[:12]}] | {'一致' if ws else '不一致'}/{'一致' if wm else '不一致'} | {flow} | {cur_txt[:20]} | {cat} |")
P("")
P("統一フロー結果 x GT代理(件数):")
P("")
P("| GT代理 | 採用(Primary) | 採用(Secondary) | NG(再生成) |")
P("|---|---|---|---|")
for gt in ["correct_user", "correct_strong", "correct_probable", "needs_listen", "error_proxy"]:
    P(f"| {gt} | {flow_counts.get((gt,'採用(Primary)'),0)} | {flow_counts.get((gt,'採用(Secondary)'),0)} | {flow_counts.get((gt,'NG(再生成)'),0)} |")
json.dump(rows_out, open(os.path.join(OUT, "trial_a_ja_rows_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- A-3 英語 他NG segment (local proxy) ----------------
d = os.path.join(ROOT, "er056_output", "en_asr_confirm_retry_redesign_01")
lp = json.load(open(os.path.join(d, "local_proxy_results_01.json"), encoding="utf-8"))
med = {m["wav"]: m for m in json.load(open(os.path.join(d, "local_proxy_medium_followup_01.json"), encoding="utf-8"))}
ng = [x for x in lp if x["kind"] == "NG"]
P("")
P("### A-3. 英語 他NG segment 20本(Standard/Advanced の Primary NG 保存音声、Azure転写は保存されていないためlocal small/mediumのみ=Secondary代理)")
P("")
P("| segment | Primary種別 | local small | local medium | 統一フローでSecondary(代理)がPASSなら | 原因分類 |")
P("|---|---|---|---|---|---|")
cat_counts = {}
for x in ng:
    m = med.get(x["wav"])
    sm = x["local_pass"]
    md = m["medium_pass"] if m else None
    cat0 = x["primary_category"]
    if cat0 == "PASS":
        cat = "ASR以外のgate由来(Primary再判定ではPASS: 長さ/Repetition QA/Disfluency QA等)"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        P(f"| {x['segment_id']} | {cat0} | {'PASS' if sm else 'NG'} | {('PASS' if md else 'NG') if m else '未実施'} | (ASRは対象外) | {cat} |")
        continue
    if cat0 in ("NUMERIC_NEGATION", "NUM_NEG") or "NUM" in cat0 or "NEG" in cat0:
        cat = "真の誤読の可能性高(数値/否定、local NG なら)" if not sm else "未確定(要試聴): localは原稿一致"
    elif sm or md:
        cat = "Primary側ASR誤認 or Validator厳格(別系統ASRが原稿一致)"
    else:
        cat = "未確定(要試聴): 別系統ASRも原稿不一致"
    cat_counts[cat] = cat_counts.get(cat, 0) + 1
    flow = "採用(救済)" if (sm or md) else "NG(再生成)"
    P(f"| {x['segment_id']} | {cat0} | {'PASS' if sm else 'NG'} | {('PASS' if md else 'NG') if m else '未実施'} | {flow} | {cat} |")
P("")
P("原因分類件数: " + ", ".join(f"{k}={v}" for k, v in cat_counts.items()))

open(os.path.join(OUT, "trial_a_tables_01.md"), "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
