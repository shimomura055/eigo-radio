# AUW 委任_06 RUNTIME_EVIDENCE (15必須受入条件の対応表 + 実音声 runtime evidence) -- branch feat/auw-unified-asr-01

管理ID `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_06 / 日付 2026-10-16 / HEAD(実行時) `2ac5899e9`(Production コード無編集。本委任で追加したのは evidence runner `er078_auw_runtime_evidence_06.py` と本 evidence のみ)。
main 無変更。判定の宣言(PRODUCTION_WIRED 可否)はしない。**材料のみ**。
使用モデル(最新か): Primary ASR=gpt-4o-mini-transcribe(Production ASR_ROUTING の現行)、Secondary=Azure Speech(phrase list / JA は strict wrapper)、TTS=gemini-3.8-flash-lite-tts(Z の `speech_metadata_flash_lite`)。いずれも Production 経路そのもの(評価用に新旧を選んだものではない)。

## 0. 実行方式 (遮断の分離)
- test 実行: `-p netguard`(外部 connect/DNS を遮断する pytest plugin、scratchpad、リポジトリ外)付き。**遮断を外した有料実行は `er078_auw_runtime_evidence_06.py` の `--execute` のみ**(混ぜていない)。
- 各 execute 前に `tools/stop_scope_check_01.py --managed-id AUW-06` を実行し rc=0 を確認(`evidence_06/*/stop_check_pre.json`、`stop_check_06.json`)。自プロセスの外部停止・原因不明 rc≠0 は無し。有料 run の再起動は無し(下記 §9 の a2_secondary 再実行は自分で実装を変えた再取得で、同一条件の再試行ではない)。
- 隔離: HR queue / attempt_history / master_audio_store / reuse_telemetry / er021・er025 telemetry / cost log / Ledger を `evidence_06/<run>/` 配下へ差替(`er077_..._evidence_runner.apply_isolation` 再利用)。各 run の `runner_execute.json: shared_state_unchanged=true`(共有 state 8 ファイルの md5 前後一致)。**本番の Human Review Lock・queue には一切書いていない**(Lock state は run_dir 内)。
- 計測: OpenAI Primary ASR は Production の cost logger に記録されない経路のため runner の wrapper が 1 呼出ごとに `usage_log.jsonl` へ記録。Azure は cost logger(`cost_log.jsonl`、`LOCAL_WAV_HEADER_EXACT` 秒数)に記録。**TTS(STANDARD 同期)は cost logger に記録されない(§10 逸脱 D1)**。
- Ledger: 作業ツリーの `er006_output/pronunciation_ledger_01/ledger.json`(未commit差分あり、"melos" low confidence を含む)の snapshot を読取専用で使用(10/14 の M1 evidence と同じ設定)。

## 1. 当初目的(ユーザー原文の逐語。`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`)
- L97「この安全条件と「Secondary PASSなら採用」の原則が競合する場合は、**数値・否定などの明確な重大内容差を誤採用しないことを優先**する。保護すべき差異を警告だけで無条件に解放する仕様にはしない。」
- L112-L117「`Melos said.` の2026年10月14日の実音声検証は重要なRegression基準とする。/ - Full Story相当：12/12 PASS / - Dialogue・見出し相当：12/12 PASS / - M1新規救済：21観測 / - M1起因の誤受理：0件」
- L197-L217 必須受入条件15項目(下記 §3 の表の左列に逐語)。L217「**1項目でも未確認であればPRODUCTION_WIREDと報告しない。**」
- L219-L227 STOP 条件「数値・否定などの重大な誤PASSが発生。」「予算・安全・権限・Human Review Lockに抵触。」

## 2. 成果物
- 本書、`er078_auw_runtime_evidence_06.py`(runner)、`evidence_06/`(下記各 run の出力。wav は commit 対象外=ローカルのみ)。
- 費用サマリ `evidence_06/cost/spend_summary.json`、attempt_history 集計 `evidence_06/cost/attempt_history_stats.txt`、静的監査 `evidence_06/static_audit/`、旧main対新の JA 比較 `evidence_06/ja_old_vs_new/`。

## 3. 15必須受入条件の対応表 (A)
分類: **充足(実音声)** = 本委任で実音声取得 / **充足(既存evidence)** = 既存 evidence のファイル:行 / **一部充足** / **未充足**。test PASS だけでは「充足」としない(test は補助欄)。

| # | 原文(L201-L215) | 分類 | 根拠 / 残作業 |
|---|---|---|---|
| 1 | ユーザー承認済みのASR判定仕様と実際のProduction動作が一致。 | **一部充足** | 実音声: EN(Melos 36観測 §4、A2 減速後 §6、Dialogue Std・KP 解説 §6、両NG×3 §7)と JA(§5)で、Primary PASS→Secondary 不呼出(z_prod_path: Azure 0)、Primary NG→Secondary 1回(melos: 23 呼出/24 wav)→PWW(§4/§5)、両NG→再生成(§7)、Secondary 障害→PASS 不可(§6-S4)、値/否定差→Secondary 不呼出で不採用(§4-neg/§5)を確認。**未実施**: Family X/B/C/A(legacy)runner の end-to-end 実run、B1(b1b) level の Z narrator、JA の再生成3回 runtime。 |
| 2 | 日本語・英語、すべてのProduction音声Sectionに適用。 | **一部充足** | 静的: 呼出点 35 entry・deferred 0・pending 0・unlisted 0(`static_audit/static_audit_summary.json`)、Family×Section マトリクス `APPLICABILITY_MATRIX_01.csv`。実音声に通した Section: EN narrator(A2 Full Story 相当, 減速)・EN dialogue(Std)・EN KP 解説・JA title・JA comment(Z run_tts_stage)、EN/JA 既存 clip の判定。**実音声未実施**: Topic Intro / Preview(EN) / In One Line / Point 見出し / KP phrase EN・JA / Key Phrase JA 意味 / Family X・B・C・A 実run / Local Rewrite 経路。 |
| 3 | Primary NG→Secondary PASSがWARNING付きで採用される。 | **充足(実音声)** | EN: melos `secondary_confirmed` 7/36(`evidence_06/melos/clip_results.json`)、A2 減速後 S1(`a2_secondary/runner_execute.json` S1: Primary "Mella said." → Azure "Mello said." → PASS_WITH_WARNING、`status=OK`)。JA: Z run の `comment_1`(Primary "10分" vs 原稿 "十分" → AMBIGUOUS → Secondary exact "十分" → PASS_WITH_WARNING `NUMERIC_AMBIGUOUS_SURFACE`、`z_ja_prod_path/run/a2/audit/tts_generation_results.json`)。JA で「Primary NG の Secondary 採用」が自然発生した例は上の1件のみ(他の JA は Primary PASS)。 |
| 4 | Primary／Secondary両NGなら最大3回のTTS生成フローが成立。 | **一部充足** | 実音声: KP 解説(3回化の対象)を、ASR が再現できない非語列で Z `run_tts_stage` 経由に実行 → **TTS 3 / Primary 3 / Secondary 3(各 attempt 1回・重複0)→ STOPPED → HR queue 1行(最終 slot のみ)→ Lock HUMAN_REVIEW_REQUIRED(隔離 state)**(§7)。他 Section の 3 回は test(mock)のみ: `er078_asr_unified_wiring_05_test_01.py`(KP 3回 `test_kp_explanation_makes_three_tts_attempts_and_queues_hr_only_at_slot_three`、A2 外側ループ通算3、KP phrase 4回構成)。A2 外側ループ・JA 3回・LR 発動の実音声 runtime は未実施。 |
| 5 | 数値の同値・異値を適切に判定し、否定保護を維持。 | **充足(実音声)**(例示9件の網羅は test) | 実音声ネガティブ: EN 7/7 不採用(数値差 2・否定差 2・他語 3、`melos_negatives/runner_execute.json`)、JA 4/4 不採用(数値 3・否定 1、値ガード DIFF / 否定差 → NG_PROTECTED, Secondary 不呼出、`ja/runner_execute.json`)、A2 減速後 S3(数値差)NG_PROTECTED。ポジティブ: JA "2つ"=ASR "二つ" → 値ガード EQUAL で採用、"9か月"=ASR "9カ月" EQUAL(Z run)、"十分"=ASR "10分" → **AMBIGUOUS** でSecondary exact を待ちPWW(機械的に同値化しない)。ユーザー指定 9 例(三人/3人 等)の網羅は `er078_asr_value_guard_01_test_01.py`/JA wiring test(mock・音声なし)。 |
| 6 | Connected Speech／M1／F1の既存Regressionに悪化なし。 | **充足(実音声)** | §4。`Melos said.` Full Story 相当 12/12・Dialogue 相当 12/12(新 Primary でも保存 Primary でも一致)、M1 21 観測(保存 Primary 再生では 21/21、新 Primary では 20 -- 1件が M1 でなく Secondary 採用に変わっただけで verified)、M1 起因の誤受理 0、36/36 verified、旧 PASS→新 NG 0。 |
| 7 | 試聴リストへのWARNING連動が動作。 | **一部充足** | 実音声: Z `run_tts_stage` の生成完了 hook が `audit/pass_with_warning_listening_list.json` を実際に出力(JA comment_1 の1件、`z_ja_prod_path/run/a2/audit/`)、legacy 用 `write_listening_list_safe(standalone_html=True)` が JSON + HTML 節を出力(§8、EN Secondary 採用 + JA 2件)。**未実施**: X/Z の最終 HTML ページ組込(`er063:build_pages`、`er019:2144`)の実run(test のみ)、B/C hook の実run。 |
| 8 | Secondary二重呼び出し・予算超過・無限retryがない。 | **充足(実音声)** | 全 run で同一 wav への Azure 呼出 >1 の件数 = 0(`azure_duplicate_wavs`、melos 24 wav に対し 23 呼出[1 件は Primary PASS]、segNone 条件は run cache 命中)。retry は KP 解説で通算3回に停止(§7)。費用 JPY 約9.2 < 50。circuit breaker は mock(unit)のみ(実障害の連続は未再現)。 |
| 9 | Production正式pathのruntime evidenceがある。 | **一部充足** | 正式 path = Family Z `run_tts_stage`(a2)を実TTS・実Primary・実Secondary で実行(§6/§7)。X/B/C/A runner と b1b level は未実施(条件1・2 と同じ残り)。 |
| 10 | 必要なUnit／Regression／Integration testがPASS。 | **充足(既存evidence) + 本委任の再確認** | 委任_05 `IMPLEMENTATION_05.md:84-93`(全体 per-file: 新規失敗 0、baseline 失敗 id 同一)。本委任で AUW 中核 10 ファイルを再実行: **398 passed / 86 subtests**、netguard 遮断試行 0(`evidence_06/tests_auw_core.txt`)。全 suite の再実行は未(コードは 委任_05 から無変更)。 |
| 11 | CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSに実態を反映。 | **未充足** | 委任_07。 |
| 12 | 必要なcommit／push／mergeを確認。 | **未充足(一部)** | branch は commit/push 済み、**main merge は未**(委任_07、Gate 4 予行含む)。 |
| 13 | Dangling Reference Checkで問題なし。 | **未充足** | 委任_07。委任_06 の入力: 旧 `_post_slowdown_cascade_rescue`・各 leaf の `if stop_retrying:` 残置(IMPLEMENTATION_05 §6-4)。 |
| 14 | 未解決USER_DECISION_REQUIRED・未配線APPROVED項目を明示。 | **一部充足** | 本書 §11 に列挙(OF-AUW-08 R+ 許容集合縮小、U1/U2 暫定値、未実装の外側ループ汎化 等)。SSOT 反映は委任_07。 |
| 15 | Fableがユーザー承認内容・実装・証跡を独立照合。 | **未充足** | Fable の工程。 |

## 4. B: EN 回帰 (Melos said., 実Primary → 実Secondary(Azure))
**構成の特定**: 「12/12・12/12」= `EVIDENCE_RUN_01.md` §2(`er077_output/m1_oov_multi_pronunciation_01/EVIDENCE_RUN_01.md:15-17`)の **既存 12-take(er069 gen02 の `Melos_said_L2_{adv t1-4, std t1-4 × raw/slow6}`)× 2 条件**(`segment_id=full_story_part1`=Full Story 相当 / `segment_id=None`=Dialogue・見出し相当)。「M1 新規救済 21 観測」= その 24 観測のうち M1_MULTI_CANDIDATE_ACCEPT になった数(9+12)。同構成で実行(同じ wav・同じ 36 観測=24 + 新規 TTS 12[nonsib/repeat/neg_num の旧 clip])。
- コマンド: `.venv\Scripts\python.exe er078_auw_runtime_evidence_06.py melos --execute --budget-jpy 4`(新 Primary)と `... melos --stored-primary --execute --budget-jpy 3`(Primary は 10/14 の保存転写、Secondary のみ実Azure)。Production 関数は `er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`(統一judge 入り EN adapter)、run scope(`begin_secondary_run`)を Production runner と同様に有効化。

| 指標 | 旧(10/14 EVIDENCE_RUN_01) | 新 Primary + 実Secondary(`evidence_06/melos/`) | 保存 Primary + 実Secondary(`evidence_06/melos_stored_primary/`) |
|---|---|---|---|
| Melos said Full Story 相当 verified | 12/12 | **12/12** | **12/12** |
| Melos said Dialogue・見出し相当 verified | 12/12 | **12/12** | **12/12** |
| 全 36 観測 verified | 36/36 | 36/36 | 36/36 |
| M1 受理数(Melos said 24 観測中 / 全36中) | 21 / 21 | **20 / 20** | **21 / 21** |
| 旧 PASS → 新 NG | - | 0 | 0 |
| 誤受理(保存結果に無い新規受理) | 0 | 0 | 0 |
| PASS_WITH_WARNING / PASS | - | 35 / 1 | 35 / 1 |
| うち `secondary_confirmed`(Primary NG→Secondary 採用) | - | 7 | 6 |
| Azure 実呼出(24 distinct wav) | 25 | **23**、同一 wav への重複 **0**(`azure_duplicate_wavs=0`, `max calls per wav=1`) | 23、重複 0 |
| OpenAI Primary 呼出 | 42(Primary#2 含む) | 36 | 0(保存転写) |
| 費用(推定: Azure 秒数×0.0444 + OpenAI 1 call×0.0094) | ASR ¥2.60(EVIDENCE_RUN_01) | ¥2.42 | ¥2.08 |
- **M1 20 vs 21 の理由(clip 単位)**: `Melos_said_L2_std_t3_slow6__segNone` で、今回の実 Primary が "Mellos said."(10/14 は "Mello said.")。segNone(Tier3 不発)では P-chain で受理できず、Secondary(実Azure "Melos said.")が原稿全文を支持して `secondary_confirmed`/EXACT_MATCH で採用(verified=True、M1 ではない)。同 wav に 10/14 の保存 Primary を与えると M1 受理(21/21 に一致)。**ASR の非決定性による観測差であり、verified の悪化ではない**。
- **03 §9-4 の差分 clip**(`Melos_said_L2_adv_t1_raw__segNone`、Primary#2 廃止で保存 Secondary が無かった件): 保存 Primary "Mallow said." + **実Secondary "Mellow said."** → `secondary_confirmed`/M1_MULTI_CANDIDATE_ACCEPT で verified(`melos_stored_primary`)。API-0 再現の 26/27・20/21 は実Secondary 取得後に **27/27 相当・21/21** へ回復(27=Melos said 24 + repeat 3)。
- PASS_WITH_WARNING の大半(29/36)は `reason=primary_pass`(Primary P-chain の M1 / Tier3 corroboration 層が受理し WARNING ラベル付与)。Melos は固有名詞 clip 集合のため試聴リスト行数が多いのは想定内(一般記事では少数の見込み)。
- 実音声ネガティブ(`melos_negatives/`、既存 wav の canonical を別内容へ差替、TTS 不要、実Primary + 必要時実Secondary): "Melos did not wait five days." を six / fifteen days → NG_PROTECTED(値DIFF, Secondary 不呼出); did wait five days → NG_PROTECTED(否定差); "Melos left." を "did not leave"→NG_PROTECTED(否定差)、"sat"→NG_BOTH(Secondary 実呼出 "Melos left." も不支持); "Melos ran."→"won" NG_BOTH; "Melos said Melos left."→"won" NG_BOTH。**false_accepts=[]**。
- repeat clip(F1 residual): Primary のみ M1 `F1_RESIDUAL_CONTENT` で却下され、受理は実Azure 転写 "Melo said Melos left." に対する Secondary 採用(10/14 と同一挙動)。M1 起因の誤受理 0。

## 5. C: JA (実音声、既存 JA run の wav を再利用 + Z run で実TTS)
- 既存 wav 再判定(`ja/`、`ja_candidates.json` から選定した household/ai_factory/akb48 の数値入り title/comment、実Primary[ja-JP] → NG なら実Secondary[`_azure_stt_strict`]): 10 ケース(positive 6 / 数値差 3 / 否定差 1)。
  - **positive**: household "2つ"(ASR "二つ")→ PASS, 値ガード **EQUAL**; ai_factory "2つ"→"二つ" PASS_WITH_WARNING(`JA_NUMERIC_IRREGULAR_READING`)EQUAL; household 別take PASS_WITH_WARNING EQUAL。AKB48 の 3 clip は **固有名詞の誤認識**(伊藤百花→"伊藤評価/ひょうか"、近藤沙樹→"近藤作/咲" 等)で NG(NG_BOTH ×2[Secondary 実呼出も人名不一致]、NG_EXCLUDED A6_C1_PROPER_NOUN_DIFF ×1)。値ガードは全て EQUAL/UNKNOWN で、不採用の原因は人名。
  - **旧 main との比較(API 0, `ja_old_vs_new/compare_api0.json`)**: 同じ Primary/Secondary 転写に対し `main` の `er007_ja_secondary_asr_01` を適用 → **10/10 で verified が一致**(AKB48 の 3 clip も main で NG)。旧 PASS→新 NG は 0。(`er005_output/cost_baseline_01/akb48` の保存 `asr_verified=True` は 2026-08 時点の旧 validator 判定で、現 main でも NG=AUW 起因の PASS→NG ではない。)
  - **negative**: 原稿を "3つ"(ASR "二つ")×2、"3作" ×1 → **DIFF → NG_PROTECTED(p1_value_diff, Secondary 不呼出)**、否定差("長持ちしない")→ NG_PROTECTED(p1_negation_diff)。**false_accepts=[]**。
  - 値ガード実挙動: EQUAL(2つ/二つ、9か月/9カ月)・DIFF(3つ vs 二つ)・**AMBIGUOUS("十分" vs ASR "10分")**・UNKNOWN(Secondary 側 "二作": 助数詞「作」)を実音声で全て観測。
- Z `run_tts_stage`(a2)実TTS(`z_ja_prod_path/`): `japanese_title` "...9か月ほど..." → ASR "9カ月" → PASS(`primary_pass_approved_equivalence:READING_MATCH`, EQUAL)。`comment_1` "会議は十分で終わります。" → ASR "10分" → AMBIGUOUS → Secondary(実Azure)"十分"(exact)→ **PASS_WITH_WARNING(`secondary_exact_resolves_ambiguous`, `NUMERIC_AMBIGUOUS_SURFACE`)→ 試聴リストに掲載**。
- 費用: ja ¥1.57(Azure 33秒)+ z_ja ¥0.12 + TTS 2 clip(推定¥0.12)。

## 6. E: A2 減速後判定 / Dialogue / KP 解説 (Z `run_tts_stage`, level=a2, 実TTS)
`z_prod_path/run/a2/audit/tts_generation_results.json`(コマンド `er078_auw_runtime_evidence_06.py z --execute --budget-jpy 8`)。ClipSpec 3件(narrator=`full_story_part1_c1`[A2 6%減速], dialogue=`full_story_part1_c2`[Std 発話1, voice Charon], kp_expl_en=`kp1_explanation_en`)。全て status=OK、TTS 3(各1回)、OpenAI ASR 5(A2 は減速前後 2回ずつ)、**Azure 0**(Primary PASS のため Secondary 不要=原文「Primary PASSなら Secondary は不要」どおり)。
- `asr_judgement` が全 3 エントリの最上位に書かれる。A2 narrator/dialogue は `slowdown_applied=true`、`asr_judgement.audio_sha256` == 最終(減速後)wav の `sha256`(**減速後 wav を判定**)、`slot=1`、`reason_code=primary_pass_approved_equivalence:TIER1_*`(Dialogue は "twenty"→数値等価 TIER1_NUMERIC_EQUIVALENCE)。KP 解説の試行 meta `max_attempts: 3`(3回化が実行経路に反映)。
- **A2 減速後の Secondary 経路**(`a2_secondary/`、`apply_a2_slowdown_postprocess` を Production 関数のまま、減速前 wav[Z run の `*_original.wav`]と Melos wav を入力、実Primary/実Secondary):
  | case | 結果 |
  |---|---|
  | S1 Melos "Melos said."(減速後 Primary "Mella said.") | 実Azure 1回("Mello said.")→ `secondary_confirmed`、PASS_WITH_WARNING、status=OK、試聴リスト掲載 |
  | S2 原稿 "Banks ..."(音声は "shops") | 実Azure 1回 → NG_BOTH(`secondary_not_accepted`)、status=STOPPED、`asr_judgement_post_slowdown_ng` に監査record |
  | S3 原稿 "ten months"(音声 "nine") | **NG_PROTECTED(p1_value_diff)**、Secondary 不呼出、STOPPED |
  | S4 Secondary 障害(Azure を `(None, "mock Secondary service error")` に差替、no network) | **NG_SECONDARY_UNAVAILABLE**(`secondary_unavailable`)、PASS 不可、STOPPED |
  | S5 Secondary 障害(Azure を例外送出に差替) | 例外は `_post_slowdown_unified_judge` が fail-closed 化 → STOPPED(判定 record 無し)。PASS にはならない(§10 D3) |
  Azure 実呼出 2(S1,S2)、重複 0。
- **KP 3回目試行**: 自然発生はしなかった(§7 で強制再現した実run がある)。mock evidence: `er078_asr_unified_wiring_05_test_01.py::test_kp_explanation_makes_three_tts_attempts_and_queues_hr_only_at_slot_three`/`test_kp_explanation_success_on_third_attempt_is_ok`(`evidence_06/tests_wiring05_selected.txt`)。

## 7. 両NG → 再生成 → 通算3回 → STOP/HR (KP 解説, 実音声)
`z_fail3_prod_path/`(`... zfail --execute --budget-jpy 3`)。原稿 "Zxqvt brrkl vnmpw glorp fnuk xyzzy plugh."(ASR が再現できない非語列)を Z `kp_expl_en`(Production の `generate_key_phrase_explanation_en_verified`、`max_attempts=3`)で実行。
- 結果: TTS **3**(`attempt_history.jsonl: tts_attempts_this_call=3`)、Primary(OpenAI)3、Secondary(Azure)**3=各 attempt 1回、同一 wav 重複 0**、最終 STOPPED、**HR queue 1行**(`z_fail3_prod_path/human_review_queue.jsonl`、最終 slot=3 のみ)、Lock `HUMAN_REVIEW_REQUIRED`(隔離 `run/a2/audit/review_lock_state.json`、本番 Lock 無関係)、無限 retry なし。旧は 1 attempt あたり Primary#2/S1/S2 まで(Secondary 最大 4回)。
- 失敗終了時の最終成果物: `z_fail3_prod_path/run/a2/audit/tts_generation_results.json`(`key_phrases.1.explanation.status=STOPPED`、attempts log に3 attempt の ASR 転写と cascade 手順)、`runtime_evidence_04C.json`、`human_review_queue.jsonl`(目的=「3回NGでHR」の要件に適合)。

## 8. D: PASS_WITH_WARNING → 試聴リスト (実音声)
- 自然発生(`z_ja_prod_path`): Z の生成完了 hook(`er063_family_z_audio_01.py:989` `_pww.write_listening_list_safe(level_dir)`)が `.../a2/audit/pass_with_warning_listening_list.json` を出力: `count=1`(comment_1、`warning_labels=["NUMERIC_AMBIGUOUS_SURFACE"]`、`primary_text`/`secondary_text`/`value_guard_kind_primary=AMBIGUOUS`/`secondary=EQUAL`、`adopted_sha256`=最終wav)。`z_prod_path`(PASS のみ)の list は `count=0`(0件でも節を出す仕様どおり)。
- Primary NG・Secondary PASS の実 clip(`a2_secondary/run_a2sec/audit/`): A2 S1(EN, secondary_confirmed)+ JA 2件(`ai_factory_title_2tsu`/`household_title2_2tsu`、`JA_NUMERIC_IRREGULAR_READING`)で `write_listening_list_safe(run_dir, standalone_html=True)`(B/C/legacy hook と同じ関数)を実行 → `pass_with_warning_listening_list.json`(count=3)と `pass_with_warning_listening_list.html`(『事後試聴リスト(PASS_WITH_WARNING)』節、audio コントロール、Primary/Secondary 転写、値ガードkind)が実際に出力。**X/Z 最終 HTML ページへの組込 (`er063:1430`、`er019:2144`) は test のみで実run未**(完全な assembled run が必要)。

## 9. 費用実額 (出典: 各 `usage_log.jsonl`/`cost_log.jsonl`、集計 `evidence_06/cost/spend_summary.json`)
| run | 推定 ASR(Azure 秒数実測 + OpenAI 呼出数×単価) | TTS(推定) |
|---|---|---|
| melos(新 Primary) | ¥2.4154(OpenAI 36, Azure 23/46.78s) | 0 |
| melos_stored_primary | ¥2.0770(Azure 23/46.78s) | 0 |
| melos_negatives | ¥0.3828 | 0 |
| ja | ¥1.5743(OpenAI 10, Azure 2/33.34s) | 0 |
| z_prod_path | ¥0.0470(OpenAI 5) | 3 clip ≈¥0.186 |
| z_ja_prod_path | ¥0.1200 | 2 clip ≈¥0.124 |
| z_fail3_prod_path | ¥1.1133(OpenAI 3, Azure 3/24.44s) | 3 clip ≈¥0.186 |
| a2_secondary(最終版) | ¥0.4315 | 0 |
| a2_secondary 旧2回分(§10 D5 で出力を差し替えて削除) | ¥0.1042 + ¥0.4221 | 0 |
| **合計** | **¥8.69** | **¥0.50** |
**総額 約 JPY 9.2**(上限 JPY 50 の約18%)。OpenAI は呼出単価¥0.0094、TTS は1 clip ¥0.062(DESIGN_01 §9)の**推定**(§10 D1)。Azure は cost logger の秒数実測×¥0.0444/s。

## 10. 逸脱・発見 (正直な記録)
- **D1 TTS・OpenAI ASR の費用が Production の cost logger に記録されない**: Azure は `cost_log.jsonl` に出るが、OpenAI Primary ASR は元々、STANDARD TTS は今回の経路で cost logger に出ない(`cost_jpy: null`)。OpenAI は runner wrapper で記録したが、**TTS 計 8 clip(z 3 + z_ja 2 + z_fail3 3)は事前確認が足りず wrapper を入れないまま実行**し、費用は推定値。委任文の「記録されない経路は実行しない」に反する。額は推定 ≈¥0.5 で JPY 50 に影響なし。委任_07 で「STANDARD TTS の費用記録」を Open Item 化することを推奨(15-9 の実費算定に必要)。
- **D2 attempt_history に test 行が追記**: 本委任の中核 test(398件)実行で、既存 test の副作用により本番 `er011_output/attempt_history.jsonl` に `wiring_theme_auw*` 行が追記された(同ファイルは作業ツリーで既に差分あり、**stage しない**)。evidence run 側は隔離済みで追記なし。
- **D3 EN adapter の Tier3 corroboration step は、Azure 関数が例外を送出すると伝播する**(`er006_secondary_asr_01.py:789` `az.text()`、Tier3 は AUW 前からの既存層)。judge 本体は例外を `NG_SECONDARY_UNAVAILABLE` に変換する(segment_id=None 条件で確認)が、role gate の Tier3 step が先に Azure を呼ぶ場合は例外が上位へ。A2 減速後は `_post_slowdown_unified_judge` が fail-closed 化して STOPPED(PASS にはならない)。実際の障害モード(`(None, error)` 返却、`CancellationReason.Error`)は `NG_SECONDARY_UNAVAILABLE` になることを確認済み。誤 PASS は無いが、障害時の監査 record が無い。仕様判断を伴わない堅牢化の候補(委任_07/Fable 判断)。
- **D4 Z の audit entry は `asr_judgement` のみ保持**(`er063_family_z_audio_01.py:826`)。`asr_judgement_pre_slowdown`・`post_slowdown_*` は Z の tts_generation_results に残らない(leaf の result には存在)。additive 情報の欠落で、判定・採用には影響なし。
- **D5 a2_secondary を3回実行**: 1回目は S2/S4 の模擬原稿が値差を誘発し、Secondary 障害 case を発動できなかったため、2回目で原稿を差替え、3回目で障害を「例外送出」と「(None,error) 返却」に分けた。1・2回目の出力は削除(費用は §9 に計上)。有料 run の再起動ではなく、evidence 設計の修正。
- **D6 M1 20/21**: §4 のとおり ASR 非決定性。

## 11. 委任_07 への申し送り (SSOT 記載事項)
1. **OF-AUW-08 R+ の許容集合縮小**: JA UNCERTAIN 経路の Secondary 許容集合は 旧=`should_pass`(PHONETIC_MATCH 含む) → 新=EXACT/NORMALIZED + ORTHOGRAPHIC_VARIANT_CONFIRMED(2エンジン)のみ(`IMPLEMENTATION_04.md:104`)。本委任の実音声(JA 10 + 2 clip)では旧 main と 10/10 で判定一致、縮小による PASS→NG は観測されなかった(ただし UNCERTAIN の実 Secondary 採用例は自然発生0)。DECISION_LOG へ記録。
2. **値等価の実装位置**: 値ガード `er078_asr_value_guard_01.py`(EN/JA 共通)、JA の値等価受理は `er007_ja_secondary_asr_01.py` `_numeric_value_equivalence`(Primary 側の追加層)、EN は既存 Tier1 数値等価(P-chain, `TIER1_NUMERIC_EQUIVALENCE`)を保持したうえで、統一judge の最終 AND ゲート(値DIFF/否定差)で保護(実音声: Dialogue の "twenty" が TIER1_NUMERIC_EQUIVALENCE で採用)。ユーザー例9件の test は `er078_asr_value_guard_01_test_01.py`/JA wiring test。
3. **撤去/残置**: 残置 = `_post_slowdown_cascade_rescue`(Production 経路から呼ばれない)、各 leaf の到達不能 `if stop_retrying:`(8箇所)、`en_validator` import(test が patch)。整理は 07 判断。静的監査 phase=post_wiring 35 entry(deferred 0・pending 0)を本 HEAD で再生成し committed allowlist と完全一致。`er011_human_review_lock_01.py` は `main..HEAD` で +2 行(`build_attempts_detail` の additive key のみ、Lock ロジック無変更)。
4. **KP 3回化**(OF-AUW-12): `er019_family_x_audio_production_runner_01.py:701 KP_EXPLANATION_MAX_ATTEMPTS = 3`。実音声: 通算3回で STOPPED/HR(§7)、増分費用 §12。**ユーザー決定逐語なし(Trial 値 2 の継承を 3 へ揃えた)=DESIGN_02_ADDENDUM_01 §9 のとおり記録**。
5. 未実装(委任文外): Dialogue(Std)/Voices A2 の外側ループ汎化(DESIGN_01 §4-8)、見出し minimal2 撤去(OPEN-288)、adapter の Tier3→CMU Case A 順序最適化(無料の Case A に当たる前に Azure を1回呼ぶ。実音声での頻度: Z/Melos run で Tier3 corroboration 由来の Secondary は melos の `SECONDARY_CORROBORATED` 11/36)。
6. 未解決 USER_DECISION_REQUIRED(既出): U1(`er078_asr_unified_judge_01.py:65` C1 固有名詞・類似度除外の現行維持 True)、U2(`:66` force_secondary 範囲 A2_ONLY)は暫定値のまま。AKB48 のような**人名誤認識の JA clip は NG(NG_BOTH/NG_EXCLUDED)で、再生成か HR に回る**=U1 の判断材料(本委任の JA で3件観測)。

## 12. F: 費用試算 (attempt_history.jsonl + 実音声実測)
出典: `evidence_06/cost/attempt_history_stats.txt`(`er011_output/attempt_history.jsonl`、test/`wiring_theme*` 行を除外後 12,015 行、2026-08-27..2026-10-15)。**注意**: このログは `pool_test_theme`(8,428行)等の pilot/test 行を多く含み、STOPPED/HR 率は Production の実率ではない(上限側の参考値)。単価: TTS ¥0.062/clip、OpenAI ASR ¥0.0094/call、Azure ¥0.0444/s(KP 解説 clip ≈8秒 = ¥0.36/呼出、実測 z_fail3: 8.64/8.48/7.32秒)。
1. **KP 3回化(OF-AUW-12)**: KP 解説 73 call 中 **73 が 1 attempt で OK**(2 attempt に達した例 0)。3回目が必要になるのは「2回とも NG」のときのみ。95% 上限(rule of three)で 2回NG 率 ≤ 4.1%。1 件の 3 回目あたり増分 = TTS ¥0.062 + ASR ¥0.0094 + Azure ¥0.36 ≈ **¥0.43**。解説 5 本/セット(Adv)として、期待増分 ≈ 点推定 ¥0(0/73)、95% 上限 5×0.041×0.43 ≈ **+¥0.09/セット**、全て最悪(5本とも2回NG)でも **+¥2.2/セット**(委任_05 の ≈¥3 見積より小さい: 実測 Azure が ¥0.36)。
2. **JA UNCERTAIN 経路の再生成増分**(旧: Cascade 尽きで即 HR / 新: 通算3回まで再生成): 全期間 JA 1,455 call 中、終端が ASR_VALIDATION_UNCERTAIN だったのは **2件(0.14%)**、Production 期(2026-09-27~)は 0 件。JA 1 セット ≈15 segment とすると期待 UNCERTAIN 0.02件/セット × 最大 +2 再生成(JA TTS ≈¥0.15 + ASR ¥0.0094 + Azure 約10秒 ¥0.44 ≈ ¥0.6/回 ×2)≈ **+¥0.03/セット**。
3. **削減**: Secondary 呼出 最大4→1/Primary NG 事象(Primary#2・S#2 廃止)。実測(同一 36 観測): ASR 費用 ¥2.60 → ¥2.42(**-7%**)、OpenAI 42→36、Azure 25→23(run 内 cache で2条件目の重複 12 呼出を回避)。A2 減速後は従来 UNCERTAIN のみだった Secondary が「不一致の種類によらず Secondary 1回」に変わる増分(S2 のような内容語差で +1 Azure ≈¥0.1-0.4)は頻度未計測(IMPLEMENTATION_05 §6-2 の指摘)。
4. **合算**: 期待 **±¥0.2/セット以内**(増分 ≤ +¥0.12 / 削減 -7%×ASR 費用)。15-9 の「+¥1/セット以上は記録」閾値を下回る見込み。**現行ベースライン(¥/セット)は 15-9 のとおり未測定**のため「現行 ¥b → 予測 ¥p / 目標70円」は算出不可(差分のみ提示)。PASS_WITH_WARNING 採用による再生成回避の削減分は、ログに Primary NG→Secondary 救済の記録が無く定量化できない(方向は削減)。

## 13. G: 静的監査 最終 snapshot
`evidence_06/static_audit/allowlist_regenerated_post_wiring_HEAD.json`(HEAD `2ac5899e9`、`build_allowlist(phase="post_wiring")`)、`static_audit_summary.json`: entry 35(primary_acquisition 9 / en_adapter_entry 8 / ja_adapter_entry 3 / adapter_internal 8 / library_internal 2 / safety_qa 2 / diagnostic_not_judgement 1 / j11_unified_judge_entry 2)、**deferred/pending 系 category 0**、`A2_PENDING_ENTRIES=[]`、`PENDING_DELEGATION_05_CATEGORIES=()`、committed allowlist と entries 完全一致、inventory との差分 unlisted_new_calls=0 / vanished=0 / count_changed=0。

## 14. 判定材料 (宣言はしない)
- 満たす材料: 条件 3・5・6・8 は実音声で充足。条件 4・7 は KP 解説/hook まで実音声。誤受理 0、数値・否定の誤 PASS 0(EN 7 + JA 4 + A2 2 のネガティブ)、Melos 12/12・12/12・M1 21(保存 Primary)・誤受理 0、旧 main に対する PASS→NG 0、費用 約JPY 9.2、HR Lock 非抵触。
- 満たしていない材料(15条件の「1項目でも未確認」に該当): 条件 1・2・9 の Family X/B/C/A runner 実run、b1b level、Preview/Topic Intro/In One Line/Point 見出し/KP phrase の実音声、条件 7 の X/Z 最終ページ実run、条件 4 の A2 外側ループ・JA 3回・LR の実音声、条件 11-13・15(委任_07/Fable)。
- STOP 条件(重大誤PASS・誤受理>0・HR Lock抵触・費用超過・品質悪化)は **いずれも発生せず**。
