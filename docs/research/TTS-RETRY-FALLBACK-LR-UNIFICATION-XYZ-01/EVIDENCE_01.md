# EVIDENCE_01 — 委任_03 runtime evidence総括(必須検証12項目の対応表+Family別達成状況)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: 2026-10-27 00:49 JST

詳細: `EVIDENCE_X_01.md` / `EVIDENCE_Y_01.md` / `EVIDENCE_Z_01.md`(case別観測表・方針×シナリオ表・実測モデル)、`COST_01.md`、`HR_IMPACT_01.md`、機械判定=`evidence_runs/_aggregate_01.json`、生証跡=`evidence_runs/<case>.json`(+`.partial_before_kill`/`.resume`)。

## 1. ユーザー原文§7「必須検証」12項目の対応表

判定記号: PASS=期待どおり/DEVIATION_NATURAL=本物のASRで③等が自然NGとなり期待と異なる経路(フロー検査は通過)。`達成`=参照caseがすべてPASSまたはDEVIATION_NATURALで、かつ項目の要点を観測。

| # | 必須検証(原文) | 観測の要点 | 参照case[判定] | 判定 |
|---|---|---|---|---|
| 1 | TTS①でPASS → 追加生成・待機なし | E-N: 6 case(各Family×Std/Adv)で上書き0・TTS 1/clip・待機0・LR 0。X-Adv-15はE-S0(②でPASS)。 | X-Std-11[PASS], X-Adv-13[PASS], Y-Std-5[PASS], Y-Adv-5[PASS], Z-Std-7[PASS], Z-Adv-8[PASS] | 達成 |
| 2 | TTS②でPASS → 待機なし | ②PASSで終了(TTS=2・待機0・③に入らない)。X-Std-12はStd chunkの『①減速後NG→②PASS→Gate PASS』(Opus 4-c a)。 | X-Adv-15[PASS], X-Std-12[PASS] | 達成 |
| 3 | TTS①② NG → 180秒待機 → Fallback③ | ①②が同Style、実`sleep`で179.972〜180.000秒待機、③がFallback Style(30字短文/JA 60字/minimal/ENGLISH_LOCK/Zはlegacy)、Voice・modelは全attempt同一。 | X-Std-1b[PASS], X-Std-4[PASS], X-Adv-1[PASS], X-Std-6[PASS], Y-Std-2b[PASS], Y-Std-4b[PASS], Z-Std-4[PASS], Z-Std-2[PASS], Z-Adv-2[PASS] | 達成 |
| 4 | LRなし → ③NG後にHuman Review | LRなし部位(JA・KP・KP解説・Zセリフ)の③(KPは④)NG後、LRに入らずLock=HUMAN_REVIEW_REQUIRED+共有Audio Gate/Z Gate BLOCK(HRQ行はEN/KP/Z[post_ng]で観測、JA・Zセリフ判定注入はdriver限界でLockのみ)。 | X-Std-7[PASS], X-Adv-8[PASS], X-Std-9[PASS], X-Adv-11[PASS], Z-Adv-3[PASS], Z-Adv-3b[PASS] | 達成 |
| 5 | LRあり → ③NG後にLRを1回 → 書換え後の3回構成 → 最終NGならHR | LR 1回(実gpt-6-luna)→LR block ④⑤(元Style)⑥(Fallback)。LR後PASS(TTS=4)/LR後も全NG(TTS=6・待機2・HRQ 1行・Lock)の両方を観測。 | X-Std-2[PASS], X-Adv-2[PASS], Y-Adv-1[PASS], Y-Adv-4b[PASS], Z-Std-6[PASS], Z-Adv-4[PASS], X-Std-3[PASS], X-Std-5[PASS], X-Adv-3c[PASS], X-Adv-6[PASS], Y-Std-1[PASS], Z-Std-1[PASS], Z-Adv-1[PASS] | 達成 |
| 6 | LR再入なし、最大回数を超えない | E-S2bの全caseでTTS=6(それ以上なし)・LR=1(再入0)・待機2回・U-03(X-Adv-4)はLR LLM 0。 | X-Std-3[PASS], X-Std-5[PASS], X-Adv-3c[PASS], X-Adv-6[PASS], Y-Std-1[PASS], Z-Std-1[PASS], Z-Adv-1[PASS], X-Adv-4[PASS] | 達成 |
| 7 | KP英語のみ4回構成と180秒待機の整合 | 前段2回→実180秒→ENGLISH_LOCK 2回(PASSなら③で終了=TTS 3、全NGならTTS 4・HRQ=slot4のみ)。KP解説は3回(②→180秒→minimal③)。 | X-Std-8[PASS], X-Std-9[PASS], X-Adv-10[PASS], X-Adv-11[PASS], Y-Std-3[PASS], Y-Adv-3[PASS], Z-Std-5[PASS], Z-Adv-6[PASS], X-Adv-7[PASS], X-Adv-9[PASS], Y-Adv-2[PASS], Z-Adv-5[PASS] | 達成 |
| 8 | Std／AdvのStyle、Voice、速度保持 | 全attemptでVoice・modelが同一(Adv comment/previewはCharon)。LR後の再TTSは元role Style(X-Adv-6/Y-Adv-4b)。Std body_sの減速対象(X-Std-4/12)。③のみFallback Style。 | X-Adv-14b[PASS], X-Adv-6[PASS], Y-Adv-4b[PASS], X-Std-4[PASS], X-Std-12[PASS], Y-Std-4b[PASS] | 達成 |
| 9 | LR後のQA・ASR・採用判定 | LR block ④〜⑥も統一judge(ASR・disfluency・repetition QA)を通り、`script_version=v1`・`LR_REWRITTEN`警告付きで採用。U-03(QA単独NG)はLR不可で即HR。LR採用の本文はY Gate(`LOCAL_REWRITE_RECOVERY`)の対象。 | X-Std-2[PASS], X-Adv-2[PASS], X-Adv-4[PASS], Y-Adv-4b[PASS], Z-Std-6[PASS] | 達成 |
| 10 | runtimeでのFallback Style切替と実際の待機時間の証拠 | evidence JSONのattempt別`style_sha`/`style_head`(sidecarと一致)、`cooldown_events`の`actual_seconds`・`total_elapsed_since_ref_seconds`、`raw_usage_log`のmodel_id。 | X-Std-1b[PASS], X-Adv-1[PASS], X-Std-3[PASS], Y-Std-4b[PASS], Z-Std-2[PASS] | 達成 |
| 11 | Human Review Lock／キュー／Assemble BLOCK／STOP | E-S2b/E-S3でLock=HUMAN_REVIEW_REQUIRED+HRQ+共有Audio Gate BLOCK(Z=`FamilyZTtsResultsIncompleteStop`)。STOPはrun専用sentinelを待機40秒で設置→TTS 2回で停止・結果未保存・resume可(Y/Z)。 | X-Std-3[PASS], Y-Std-1[PASS], Z-Std-1[PASS], Z-Adv-3b[PASS], Y-Std-6[PASS], Z-Std-8[PASS] | 達成 |
| 12 | retry／regeneration／resumeでの重複生成・重複待機防止 | kill→同一args再起動で①②(R-5は①〜⑤)の再生成0・LR再呼出0・待機は残り時間のみ(総経過≥180秒)・attempt sidecar二重なし。 | X-Adv-12[PASS], X-Std-10[DEVIATION_NATURAL], X-Adv-16[PASS] | 達成 |

## 2. Family別達成状況

| Family | 判定集計 | 備考 |
|---|---|---|
| X(er019) | {'PASS': 26, 'DEVIATION_NATURAL': 3} | Std/Adv全leaf(L1〜L7)を実走。E-S6×3(R-5含む)、Opus 4-c追加2本、E-X5。 |
| Y(er121) | {'PASS': 11, 'DEVIATION_NATURAL': 3} | runner統合(Y Gate・HR終端・Voice本文L4/L2・KP・JA・STOP)。Y generator decoratorの位置ずれ(Production軽微欠陥)を発見・是正。 |
| Z(er063/er026) | {'PASS': 15} | Zセリフctx(L8)・narrator chunk・topic_intro_en(U-06実証)・KP・JA・STOP。Zセリフの実モデルは既存仕様のgemini-2.5-pro-preview-tts。 |

Lean 46case(EVIDENCE_PLAN §6の○)のうち実走済み 45/46。未実走: ['X-Adv-3'](X-Adv-3は置換語を変えたX-Adv-3cで代替実走)。Lean外の追加: X-Std-1b/X-Std-12(Opus 4-c a)/X-Adv-14b/X-Adv-15(E-S0)/X-Adv-16(R-5)/X-Adv-3c/Y-Std-2b/Y-Std-4b/Y-Adv-4b/Y-Std-6・Z-Std-8(E-STOP)/Z-Adv-3b。

## 3. 注記

- **A/B/C不変**: evidence中にA/B/C runは走らせていない。golden test(`er127_tts_block_policy_01_test_01.py` 97件、scope外単体呼出が変更前コードとbyte同一)をevidence後に再実行しOK。Y軽微修正後の`er121`関連test(style_profile 37件・runner 49件・hr_approval_guard 16件・追加2件)もOK。
- **R-4(Trial/toolも統一flow)**: 本evidenceのdriverはscope内(X/Y/Z)の正式leafを直接呼ぶため、Trial/tool用途でscope内を実行した場合は新flow(①②→180秒→③、LR後3回構成)で動く。scope外(A/B/C)は旧挙動のまま(golden)。
- **強制NGの境界**: 判定結果のNG方向のみ。Style・Prompt・Voice・速度・model・待機・回数・Gateは不変更。`injected_override_count`と`injected_overrides[]`を全caseに記録。正常系は0。
- **driver限界(正直に記録)**: JA(L7)とZセリフ(L8)は判定器自身が最終slotで書くHRQ行を、判定戻り値の注入では再現できない(Lock・最終STOPPED・Gate BLOCKは観測済み)。Z-Adv-3bは減速後NG注入でHRQ行を観測。JAは`register_terminal_hr`呼出が終端に無い点をOPEN候補として報告(EVIDENCE_X_01 所見5)。
- **未観測(明記)**: X-Adv-5・Z-Std-3・Z-Adv-7(Lean★除外、同leaf・同コードは別caseで実走)、YのE-S3/chunk経路、Z_DLG終端のStd版。
