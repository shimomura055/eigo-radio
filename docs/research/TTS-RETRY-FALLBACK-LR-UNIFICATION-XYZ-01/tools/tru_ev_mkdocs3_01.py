# -*- coding: utf-8 -*-
"""EVIDENCE_01.md(必須検証12項目の対応表+Family別達成状況)を生成(API 0)。参照caseの存在とverdictを機械確認する。"""
import collections, datetime, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ROOT = os.path.abspath(f"{BASE}/../../..")
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
os.chdir(ROOT)
import tru_ev_aggregate_01 as agg
import tru_ev_docs_01 as D

data, res = D.load()
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M JST")

ITEMS = [
    ("1", "TTS①でPASS → 追加生成・待機なし", "E-N: 6 case(各Family×Std/Adv)で上書き0・TTS 1/clip・待機0・LR 0。X-Adv-15はE-S0(②でPASS)。",
     ["X-Std-11", "X-Adv-13", "Y-Std-5", "Y-Adv-5", "Z-Std-7", "Z-Adv-8"]),
    ("2", "TTS②でPASS → 待機なし", "②PASSで終了(TTS=2・待機0・③に入らない)。X-Std-12はStd chunkの『①減速後NG→②PASS→Gate PASS』(Opus 4-c a)。",
     ["X-Adv-15", "X-Std-12"]),
    ("3", "TTS①② NG → 180秒待機 → Fallback③", "①②が同Style、実`sleep`で179.972〜180.000秒待機、③がFallback Style(30字短文/JA 60字/minimal/ENGLISH_LOCK/Zはlegacy)、Voice・modelは全attempt同一。",
     ["X-Std-1b", "X-Std-4", "X-Adv-1", "X-Std-6", "Y-Std-2b", "Y-Std-4b", "Z-Std-4", "Z-Std-2", "Z-Adv-2"]),
    ("4", "LRなし → ③NG後にHuman Review", "LRなし部位(JA・KP・KP解説・Zセリフ)の③(KPは④)NG後、LRに入らずLock=HUMAN_REVIEW_REQUIRED+共有Audio Gate/Z Gate BLOCK(HRQ行はEN/KP/Z[post_ng]で観測、JA・Zセリフ判定注入はdriver限界でLockのみ)。",
     ["X-Std-7", "X-Adv-8", "X-Std-9", "X-Adv-11", "Z-Adv-3", "Z-Adv-3b"]),
    ("5", "LRあり → ③NG後にLRを1回 → 書換え後の3回構成 → 最終NGならHR", "LR 1回(実gpt-6-luna)→LR block ④⑤(元Style)⑥(Fallback)。LR後PASS(TTS=4)/LR後も全NG(TTS=6・待機2・HRQ 1行・Lock)の両方を観測。",
     ["X-Std-2", "X-Adv-2", "Y-Adv-1", "Y-Adv-4b", "Z-Std-6", "Z-Adv-4", "X-Std-3", "X-Std-5", "X-Adv-3c", "X-Adv-6", "Y-Std-1", "Z-Std-1", "Z-Adv-1"]),
    ("6", "LR再入なし、最大回数を超えない", "E-S2bの全caseでTTS=6(それ以上なし)・LR=1(再入0)・待機2回・U-03(X-Adv-4)はLR LLM 0。",
     ["X-Std-3", "X-Std-5", "X-Adv-3c", "X-Adv-6", "Y-Std-1", "Z-Std-1", "Z-Adv-1", "X-Adv-4"]),
    ("7", "KP英語のみ4回構成と180秒待機の整合", "前段2回→実180秒→ENGLISH_LOCK 2回(PASSなら③で終了=TTS 3、全NGならTTS 4・HRQ=slot4のみ)。KP解説は3回(②→180秒→minimal③)。",
     ["X-Std-8", "X-Std-9", "X-Adv-10", "X-Adv-11", "Y-Std-3", "Y-Adv-3", "Z-Std-5", "Z-Adv-6", "X-Adv-7", "X-Adv-9", "Y-Adv-2", "Z-Adv-5"]),
    ("8", "Std／AdvのStyle、Voice、速度保持", "全attemptでVoice・modelが同一(Adv comment/previewはCharon)。LR後の再TTSは元role Style(X-Adv-6/Y-Adv-4b)。Std body_sの減速対象(X-Std-4/12)。③のみFallback Style。",
     ["X-Adv-14b", "X-Adv-6", "Y-Adv-4b", "X-Std-4", "X-Std-12", "Y-Std-4b"]),
    ("9", "LR後のQA・ASR・採用判定", "LR block ④〜⑥も統一judge(ASR・disfluency・repetition QA)を通り、`script_version=v1`・`LR_REWRITTEN`警告付きで採用。U-03(QA単独NG)はLR不可で即HR。LR採用の本文はY Gate(`LOCAL_REWRITE_RECOVERY`)の対象。",
     ["X-Std-2", "X-Adv-2", "X-Adv-4", "Y-Adv-4b", "Z-Std-6"]),
    ("10", "runtimeでのFallback Style切替と実際の待機時間の証拠", "evidence JSONのattempt別`style_sha`/`style_head`(sidecarと一致)、`cooldown_events`の`actual_seconds`・`total_elapsed_since_ref_seconds`、`raw_usage_log`のmodel_id。",
     ["X-Std-1b", "X-Adv-1", "X-Std-3", "Y-Std-4b", "Z-Std-2"]),
    ("11", "Human Review Lock／キュー／Assemble BLOCK／STOP", "E-S2b/E-S3でLock=HUMAN_REVIEW_REQUIRED+HRQ+共有Audio Gate BLOCK(Z=`FamilyZTtsResultsIncompleteStop`)。STOPはrun専用sentinelを待機40秒で設置→TTS 2回で停止・結果未保存・resume可(Y/Z)。",
     ["X-Std-3", "Y-Std-1", "Z-Std-1", "Z-Adv-3b", "Y-Std-6", "Z-Std-8"]),
    ("12", "retry／regeneration／resumeでの重複生成・重複待機防止", "kill→同一args再起動で①②(R-5は①〜⑤)の再生成0・LR再呼出0・待機は残り時間のみ(総経過≥180秒)・attempt sidecar二重なし。",
     ["X-Adv-12", "X-Std-10", "X-Adv-16"]),
]


def status(cid):
    v = res.get(cid, {}).get("verdict")
    return v or "未実行"


def main():
    rows = []
    for no, req, how, cids in ITEMS:
        miss = [c for c in cids if c not in res]
        assert not miss, (no, miss)
        sts = ", ".join(f"{c}[{status(c)}]" for c in cids)
        ok = all(status(c) in ("PASS", "DEVIATION_NATURAL") for c in cids)
        rows.append(f"| {no} | {req} | {how} | {sts} | {'達成' if ok else '要確認'} |")
    fam = {}
    for f in "XYZ":
        c = collections.Counter(res[k]["verdict"] for k in data if k in agg.CASES and agg.CASES[k]["family"] == f)
        fam[f] = dict(c)
    lean = set(re.findall(r"^\| ([XYZ]-(?:Std|Adv)-\d+) \|.*\| ○ \|$", open(f"{BASE}/EVIDENCE_PLAN_01.md", encoding="utf-8").read(), re.M))
    done = {k for k in data if k in agg.CASES}
    lean_done = sorted(lean & done)
    lean_missing = sorted(lean - done)
    txt = f"""# EVIDENCE_01 — 委任_03 runtime evidence総括(必須検証12項目の対応表+Family別達成状況)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: {NOW}

詳細: `EVIDENCE_X_01.md` / `EVIDENCE_Y_01.md` / `EVIDENCE_Z_01.md`(case別観測表・方針×シナリオ表・実測モデル)、`COST_01.md`、`HR_IMPACT_01.md`、機械判定=`evidence_runs/_aggregate_01.json`、生証跡=`evidence_runs/<case>.json`(+`.partial_before_kill`/`.resume`)。

## 1. ユーザー原文§7「必須検証」12項目の対応表

判定記号: PASS=期待どおり/DEVIATION_NATURAL=本物のASRで③等が自然NGとなり期待と異なる経路(フロー検査は通過)。`達成`=参照caseがすべてPASSまたはDEVIATION_NATURALで、かつ項目の要点を観測。

| # | 必須検証(原文) | 観測の要点 | 参照case[判定] | 判定 |
|---|---|---|---|---|
{chr(10).join(rows)}

## 2. Family別達成状況

| Family | 判定集計 | 備考 |
|---|---|---|
| X(er019) | {fam['X']} | Std/Adv全leaf(L1〜L7)を実走。E-S6×3(R-5含む)、Opus 4-c追加2本、E-X5。 |
| Y(er121) | {fam['Y']} | runner統合(Y Gate・HR終端・Voice本文L4/L2・KP・JA・STOP)。Y generator decoratorの位置ずれ(Production軽微欠陥)を発見・是正。 |
| Z(er063/er026) | {fam['Z']} | Zセリフctx(L8)・narrator chunk・topic_intro_en(U-06実証)・KP・JA・STOP。Zセリフの実モデルは既存仕様のgemini-2.5-pro-preview-tts。 |

Lean 46case(EVIDENCE_PLAN §6の○)のうち実走済み {len(lean_done)}/{len(lean)}。未実走: {lean_missing}(X-Adv-3は置換語を変えたX-Adv-3cで代替実走)。Lean外の追加: X-Std-1b/X-Std-12(Opus 4-c a)/X-Adv-14b/X-Adv-15(E-S0)/X-Adv-16(R-5)/X-Adv-3c/Y-Std-2b/Y-Std-4b/Y-Adv-4b/Y-Std-6・Z-Std-8(E-STOP)/Z-Adv-3b。

## 3. 注記

- **A/B/C不変**: evidence中にA/B/C runは走らせていない。golden test(`er127_tts_block_policy_01_test_01.py` 97件、scope外単体呼出が変更前コードとbyte同一)をevidence後に再実行しOK。Y軽微修正後の`er121`関連test(style_profile 37件・runner 49件・hr_approval_guard 16件・追加2件)もOK。
- **R-4(Trial/toolも統一flow)**: 本evidenceのdriverはscope内(X/Y/Z)の正式leafを直接呼ぶため、Trial/tool用途でscope内を実行した場合は新flow(①②→180秒→③、LR後3回構成)で動く。scope外(A/B/C)は旧挙動のまま(golden)。
- **強制NGの境界**: 判定結果のNG方向のみ。Style・Prompt・Voice・速度・model・待機・回数・Gateは不変更。`injected_override_count`と`injected_overrides[]`を全caseに記録。正常系は0。
- **driver限界(正直に記録)**: JA(L7)とZセリフ(L8)は判定器自身が最終slotで書くHRQ行を、判定戻り値の注入では再現できない(Lock・最終STOPPED・Gate BLOCKは観測済み)。Z-Adv-3bは減速後NG注入でHRQ行を観測。JAは`register_terminal_hr`呼出が終端に無い点をOPEN候補として報告(EVIDENCE_X_01 所見5)。
- **未観測(明記)**: X-Adv-5・Z-Std-3・Z-Adv-7(Lean★除外、同leaf・同コードは別caseで実走)、YのE-S3/chunk経路、Z_DLG終端のStd版。
"""
    open(f"{BASE}/EVIDENCE_01.md", "w", encoding="utf-8").write(txt)
    print("ok", fam, len(lean_done), len(lean), lean_missing)


if __name__ == "__main__":
    main()
