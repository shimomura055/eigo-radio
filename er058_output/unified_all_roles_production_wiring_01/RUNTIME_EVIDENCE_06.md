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

---

# §12 委任_06b 追加 evidence (残 Section・残 Family・最終ページ組込・3回NG→LR/HR の実音声)

管理ID `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_06b / 日付 2026-10-16 / branch `feat/auw-unified-asr-01`(起点 HEAD `7bb4e5d1a`)。**Production コード無編集**(`git status` で tracked の .py 変更 0。追加は evidence runner 3本 `er078_auw_runtime_evidence_06b.py`/`er078_auw_tabulate_06b.py`/`er078_auw_aggregate_06b.py`、費用再推定 `er078_auw_cost_revise_06b.py`、本 §12、`evidence_06b/`)。main 無変更。**判定の宣言(PRODUCTION_WIRED 可否)はしない。材料のみ。**
使用モデル(最新か): Primary ASR=`gpt-4o-mini-transcribe`、Secondary=Azure Speech(phrase list / JA strict)、TTS=Z/X/legacy A は `gemini-3.8-flash-lite-tts`(Z・X は `speech_metadata_flash_lite`)、Family B の Voice A/B・Family C の Story(brother 等)は `gemini-2.5-pro-preview-tts`(その Family の Production 現行モデル。評価用に選んだものではない)、Local Rewrite は `gpt-6-luna`。いずれも各 Family の Production 経路そのもの。
前提: 各 run 前に `tools/stop_scope_check_01.py --managed-id AUW-06B ...` を実行し rc=0(`evidence_06b/<run>/stop_check_pre.json`、T-0 は `evidence_06b/stop_check_T0.json`)。外部停止・原因不明 rc≠0 は無し。有料 run の再起動は無し(`ja_hr`/`crun` の「やり直し」は pre-TTS の Production Gate 停止後に**入力を変えた別 run**で、停止した run は `*_attempt0_*` として残置)。T-0: 委任文 `docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_06b.md`、checker 結果 `_06b_check.json`(FAIL: 標準テンプレート必須セクション欠落。委任文の指示どおり継続)。

## 12-1. 実行した run 一覧と費用
共通の隔離: 06 と同じ `apply_isolation`(HR queue / attempt_history / Master Store / telemetry / Ledger snapshot)に加え、06b で **Local Rewrite 回復 artifact**(`local_rewrite_recovery/`)と、初回 `ja_hr` で漏れが判明した **JA Foreign Token Gate queue**・**JA HR queue(`HUMAN_REVIEW_LOG_PATH_JA`)** も evidence 配下へ差替(初回漏れは §12-8 D-B1/D-B2)。run 前後で 8 共有 state の md5 + `git status` 差分の md5 snapshot を比較(`runner_execute.json: shared_state_unchanged`/`shared_files_changed_outside_evidence`)。

| run | 内容(Production 入口) | TTS | OpenAI ASR | Azure(呼出/秒/同一wav重複) | 費用 JPY | 費用の出典 |
|---|---|---|---|---|---|---|
| `zep` | Family Z 最小 episode(a2+b1b 各11-12 clip)`run_tts_stage`→`provision_shell_assets`→`run_audio_gate`→`run_assembly`→`build_pages` | 23 | 27 | 0 / 0 / 0 | 2.96 | 校正推定(§12-9)。wrapper 値 1.68 は固定単価で過小 |
| `zep2` | 同上、PASS_WITH_WARNING が出る原稿へ差替 | 23 | 27 | 5 / 17.8s / 0 | 4.13 | token 実測 |
| `lega` | Family A legacy n3 `generate_b1_segments`+`generate_a2_segments`(最小 theme) | 32 | 39 | 3 / 17.0s / 0 | 4.80 | 校正推定(wrapper 3.11) |
| `head` | Point 見出し(`point_headings.generate`)3 case | 5 | 5 | 3 / 19.6s / 0 | 1.49 | 校正推定(wrapper 1.23) |
| `lr_en` | b1b Full Story narrator 3回NG→LR(EN)→v1 | 7 | 7 | 6 / 34.1s / 0 | 3.72 | 校正推定+LR の Luna 8 call 推定(wrapper 未計測) |
| `a2_fail` | A2 Full Story narrator(6%減速経路)3回NG→LR→HR | 3 | 3 | 3 / 12.8s / 0 | 1.45 | token 実測(Luna 2 call 含む) |
| `ja_hr` | JA comment 3回NG→HR(LR なし) | 3 | 3 | 2 / 9.8s / 0 | 0.95 | 校正推定(wrapper 0.65) |
| `xrun` | Family X `er019 main` を `--stage tts`→`assemble`→`player`(Coffee scaffold をコピー) | 27 | 31 | 1 / 5.2s / 0 | 16.13 | Production cost logger(`xrun/x_out/raw_usage_log.jsonl`、`er019.compute_cost_jpy_so_far`) |
| `brun` | Family B `er012 main` level=a2 stage=all | 4 | 4 | 0 | 8.84 | Production cost logger(`brun/b_a2/a2/audit/raw_usage_log.jsonl`) |
| `bb1` | Family B(B1) Voice A/B 本文 leaf(`er012:run_tts` と同一引数) | 2 | 2 | 0 | 6.63 | token 実測 |
| `crun` | Family C `er013 main` level=a2 `--only-segments story_003 story_002 story_007` | 3 | 6 | 0 | 0.95 | Production cost logger(`crun/c_out/a2/audit/er005_cost_log.jsonl`) |
| 停止した2 run | `ja_hr_attempt0_foreign_token_gate_stop`(JA Foreign Token Gate が TTS 前に停止)、`crun_attempt0_story001_symbol_gate_stop`(禁止記号 Gate が TTS 前に停止) | 0 | 0 | 0 | 0 | API 0 |
| **06b 合計** | | **132** | **154** | **23 / 重複0** | **約 52.0** | `evidence_06b/cost/spend_ledger.jsonl`+`cost/revised_estimates.json`(`ledger_total()`=52.04) |

累計: 委任_06 は報告 JPY 9.2 だったが、同じ固定単価(TTS 0.062/clip・ASR 0.0094/call)で過小だったため再推定 **約 9.9**(`evidence_06/` の音声秒から。ASR 0.64→1.23、TTS 0.50→1.15、Azure 7.52 は実測のまま)。**06+06b ≒ JPY 61.9**(06b 単体 52.0 は上限 80 の 65%)。
**費用記録について(委任文の「記録できない経路は実行しない」)**: 実行前に OpenAI ASR / Gemini TTS / Gemini text / Azure 4 関数を SDK・関数レベルで wrapper 計測したが(`usage_log.jsonl`、呼出『前』に予算・STOP を check)、**初期の固定単価が実費の 1/2〜1/6 と判明**(xrun の token 実測: flash-lite TTS 0.0243 JPY/音声秒、OpenAI ASR 0.0047 JPY/音声秒。固定 0.062/clip は 2.5 秒分)。かつ **LR の Luna(OpenAI Responses)は初期 wrapper に無かった**。zep2 以降は応答 usage の token×`pricing_snapshot`(Production の `compute_cost_jpy_so_far` と同式、USD_JPY=160)で記録(Responses 計測は a2_fail から)。それ以前の run は校正推定を採用し、**推定である点は上表に明記**。誤差は ±30% 程度を見込むが、どの見積でも上限 80 まで十分な余裕があった。

## 12-2. A: 残 Section の実音声(Section × clip 表)
全 clip の `asr_judgement` 表: `evidence_06b/zep/clip_table.md`、`zep2/clip_table.md`、`lega/clip_table.md`、`xrun/clip_table.md`、`crun/clip_table.md`、`bb1/clip_table.md`、`lr_en/`・`a2_fail/`・`ja_hr/` の `clip_table.md`(列: 有無・state・reason・slot/script_version・Secondary 呼出・azure calls・値ガード・減速・TTS 使用数。集計は `*.json`)。要点:

| Section | EN | JA | 実音声 evidence(run:clip) |
|---|---|---|---|
| Topic Intro | a2/b1b | - | zep・zep2・lega・xrun の topic_intro(`xrun/clip_table.md:3` は a2 で Primary が "Prices" と聞き違え、Secondary が "price tags" を支持→ **PASS_WITH_WARNING secondary_confirmed**) |
| Preview | b1b | a2 | zep/zep2/lega/xrun の preview |
| Comment | b1b | a2 | 同上(zep2 a2 comment_1 "会議は十分で…"→ Primary "10分"→AMBIGUOUS→Secondary exact→PWW `NUMERIC_AMBIGUOUS_SURFACE`、`zep2/clip_table.md:6`) |
| In One Line | b1b / a2(減速) | - | lega b1b/a2(`lega/clip_table.md:15,31`)、xrun a2/b1b |
| Point 見出し | b1b / a2 | - | lega(`lega/clip_table.md:9,25`)、`head/`(下記)。brun a2 の見出しは承認済み asset の再利用(判定なし) |
| Key Phrase phrase | a2 / b1b | - | zep/zep2/lega の `kp1_english`(新規生成・判定あり)。xrun b1b の `kp*_english`・`kp*_phrase_repeat` は Master Store/複製の再利用(API 0・判定なし=仕様どおり) |
| Key Phrase 日本語意味 | - | a2 | zep/zep2/lega の `kp1_japanese_meaning` |
| KP 英語解説 | b1b | - | zep/zep2 `kp1_explanation`、xrun b1b `kp1-5_explanation` |
| Dialogue(複数Voice) | a2(Std 6%) / b1b | - | zep/zep2 `full_story_part1_c2`(speaker melos) |
| b1b level の Z narrator | b1b | - | zep/zep2 b1b `full_story_part1-3_c1` |
| A2 narrator 6% 減速 | a2 | - | zep/zep2/lega/xrun の a2 Full Story(`slowdown_applied=true`、減速後 wav の sha で判定) |
| Local Rewrite(EN) / JA は LR なし→HR | b1b / a2 | a2 | §12-4 |

- **Point 見出し(見出し例外維持)** `head/runner_execute.json`: 数値見出し("8.7 percent"→ASR "8.7%"→PASS・値ガード EQUAL)、否定見出し("does not mean"→PASS・negation_diff=False)、固有名見出し("Mayor Xzqwtrlk")→ **3回試行(各 attempt 1回の Azure、同一 wav 重複 0)→ STOPPED・HR queue 1行**(`head/human_review_queue.jsonl`)。見出し固有の `max_len`・`disfluency_checked`・`asr_verified` は結果 dict に維持(`head/runner_execute.json` rows)。見出しの独立 QA・意味保護は維持されている(独自の3回構成のまま、Secondary は各 attempt 1回)。
- 各 clip の `asr_judgement` 有無: zep・zep2 は **23/23**、lega は 30/31(残1は Master Store 再利用 `kp1_english`)、xrun は新規生成分すべて、crun は再生成した 3 segment すべて。状態: 最終 entry 110 件が PASS 103 / PASS_WITH_WARNING 7(`cost/aggregate_06b.json`)。**Secondary 同一 wav 重複 0**(全 run の `usage_log.jsonl`、集計 azure 23 呼出)。

## 12-3. B: 残 Family end-to-end

| Family | 入口(Production) | 結果 | (i) `asr_judgement` | (ii) 試聴リスト JSON/ページ節 | (iii) 最終ページ | (iv) 共有 state | (v) HR Lock |
|---|---|---|---|---|---|---|---|
| **X** | `er019 main --stage tts/assemble/player --level both`(`speech_metadata_flash_lite`、Coffee scaffold コピー) | b1b: tts 全 OK→assemble OK→player。a2: 非 KP 11 segment OK、**KP 5本は Production の KGCPW gloss 再整合 Gate が API 0 で停止**(コピー元 KP に `gloss_alignment_status` が無い。`xrun/x_out/a2/audit/tts_generation_results.json` の `STOPPED_GLOSS_ALIGNMENT_FAILED`)、a2 episode は `EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT` | 新規生成 26 件すべて有り(`xrun/clip_table.md`)。KP 英語/phrase_repeat 10 件は Master Store/複製の再利用(判定なし) | `audit/pass_with_warning_listening_list.json`(a2: 1件、b1b: 0件) | **`xrun/x_out/player.html:62`「0件(該当なし…)」(Advanced)と `:64`「1件。公開をブロックしません…」(Standard、topic_intro の PWW 行)**。b1b は assemble 済み音声+節、a2 は audio 未組立(gloss HR)+節 | 一致 | 隔離 Lock(`x_out/*/audit/review_lock_state.json`)のみ |
| **B(a2)** | `er012 main all a2`(出力先定数のみ evidence へ差替) | Voice A/B 本文 point_one/point_two を新規 TTS(減速)→ finalize OK(`required_segments_completeness`: complete)。**Assembly は Production の Key Phrase 出典整合 Gate(KEY_PHRASE_SOURCE_MISSING)で停止**(コピーされた KP が本文に無い。AUW 無関係の既存 Gate。`brun/b_a2/a2/audit/key_phrase_source_gate.json`) | point_one/two に有り(PASS `primary_pass`)。他 13 segment は承認済み asset の sha 再利用(判定なし) | `audit/pass_with_warning_listening_list.{json,html}`(0件) | 単独 HTML のみ(player は Assembly 停止のため無し) | 一致 | 隔離 |
| **B(B1)** | `er012 run_tts` と同一引数の leaf 呼出(B1 全体は LLM scaffold を要するため segment 単位) | point_one/point_two OK | 有り(PASS) | `bb1/b_b1/b1b/audit/…`(0件) | 単独 HTML | 一致 | 隔離 |
| **C** | `er013 main --level a2 --only-segments story_003 story_002 story_007 --config(コピー)`(他 segment は `reuse_from`) | Gate **PASS**(`crun/c_out/a2/audio_validation.json`)、3 segment を narrator/device(Charon)/brother(voice 本文)で再生成 | 再生成 3 件に有り(PASS)。reuse 分は judge 導入前の旧 asset のため無し | `audit/pass_with_warning_listening_list.{json,html}`(0件) | 単独 HTML+`write_evidence_player` | 一致 | 隔離 |
| **A(legacy n3)** | `n3.generate_b1_segments`+`generate_a2_segments`(最小 theme、TTS 31 clip) | 31/31 OK | 30/31(残1は Master Store 再利用) | b1b: 0件、a2: **1件(comment_1: Primary "値段" ≠ 原稿 "値札" → Secondary "値札" → PWW `SECONDARY_CONFIRMED`、`lega/theme/a2/audit/pass_with_warning_listening_list.html:2`)** | 単独 HTML(legacy の最終成果物) | 一致 | 隔離 |
| **Z(最終ページ)** | `run_assembly`→`build_pages` | a2/b1b とも assembly OK、standard/advanced/index.html 生成 | 23/23 | – | **`zep/pages/standard.html:2`・`advanced.html:2` に 0件節**、**`zep2/pages/standard.html:2`・`advanced.html:2` に「2件」節(a2: comment_1 `NUMERIC_AMBIGUOUS_SURFACE`+full_story_part1_c1 `SECONDARY_CONFIRMED`、b1b: `M1_MULTI_CANDIDATE`+`SECONDARY_CORROBORATED`)** | 一致 | 隔離 |

- 「共有 state 無変更」は全 run で `shared_state_unchanged=true`(8 ファイル md5)。ただし git-status snapshot で **初回 `ja_hr` が未隔離の JA 側 queue 2本へ各1行追記**(D-B1/D-B2)。それ以外の共有ファイル変更は 0(`runner_execute.json` の `shared_files_changed_outside_evidence`。lega・lr_en に出る同 2 ファイルは並行実行中の `ja_hr` の追記)。
- X の a2 KP と B の Assembly は **AUW とは無関係な既存 Production Gate**(KGCPW gloss 再整合、Key Phrase 出典整合)による停止で、Gate を回避せず停止のまま記録した(0 API / 追加費用なし)。

## 12-4. C: 3回NG → LR(EN) / HR(JA) の実音声

| run | 経路 | 実測(`attempt_history.jsonl` の `attempts_detail[].asr_judgement`) | 最終成果物 |
|---|---|---|---|
| `lr_en`(b1b narrator、原稿 "Mayor Xzqwtrlk said the new bridge would open in May.") | **通算3回(v0, slot1/2/3)すべて NG_BOTH(Primary NG→Secondary 1回→NG)→ 10分 cool-down(`cooldown_actual_seconds=600.005`)→ LR → v1 再 TTS** | v0: 実 Azure 1回/attempt(slot1・3 は Tier3 層が先に取得し judge は cache 使用=`called:false,cached:true`)。LR 後 v1: NG_BOTH ×3(各 Secondary 1回)→ 4回目 **PASS_WITH_WARNING `LR_REWRITTEN`(v1, slot1, 書換後テキストに対し EXACT_MATCH)** | `lr_en/run/b1b/audit/tts_generation_results.json`(status OK, `audio_text_deviation`)、`pass_with_warning_listening_list.json`(count 1: `warning_labels:["LR_REWRITTEN"]`)、`lr_en/local_rewrite_recovery/…json`、`lr_en/human_review_queue.jsonl`(4行、D-B5)。TTS 7 / ASR 7 / Azure 6(同一wav重複 0) |
| `a2_fail`(A2 narrator、6%減速経路) | 通算3回 NG_BOTH(各 attempt Azure 1)→ LR 候補生成+QA(Luna 2 call)→ **`HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA`** → HR | slot1/2/3、v0、`secondary_not_accepted` | `a2_fail/run/a2/audit/tts_generation_results.json`(status `STOPPED`)、`a2_fail/human_review_queue.jsonl`、`review_lock_state.json`(`HUMAN_REVIEW_REQUIRED`、隔離)。TTS 3 / ASR 3 / Azure 3 |
| `ja_hr`(JA comment、"合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。") | JA は LR なし→ **標準2回+fallback1回=通算3回で HR**。1・2回目 NG_BOTH(ASR_VALIDATION_UNCERTAIN→Secondary 1回→不採用)、3回目 **`NG_EXCLUDED A6_C1_PROPER_NOUN_DIFF`(U1 の固有名詞除外を現行維持)、Secondary 不呼出**、slot3 | 3回で停止、`local_rewrite_recovery` 無し | `ja_hr/run/a2/audit/tts_generation_results.json`(`STOPPED`)、`review_lock_state.json`(`HUMAN_REVIEW_REQUIRED`)、`ja_hr/attempt_history.jsonl`(per-attempt の judge record)。TTS 3 / ASR 3 / Azure 2 |
| `head`(見出し) | 見出し独自の3回構成で停止、Azure 1/attempt | §12-2 | `head/human_review_queue.jsonl`(1行) |

- **A2 外側ループ**: `a2_fail` は 3 attempt すべて減速前判定で NG のため、減速後の再判定には進んでいない。A2 の「減速後 Secondary」は 06 `a2_secondary/` と、本 §12 の `zep2`(a2 full_story_part1_c1 が減速後 wav で `secondary_confirmed`、`zep2/clip_table.md:9`)で実音声確認済み。
- **U2 暫定(`A2_ONLY`)の挙動記録**: EN の LR 後 v1 でも Primary NG なら Secondary 1回(lr_en の v1 NG ×3 すべて Azure 各1)。a2_fail でも Primary NG 後の Secondary は通常 cascade と同じ各 attempt 1回。

## 12-5. E: 誤受理 0・数値/否定の誤 PASS 0・旧 PASS→新 NG 0(06b 全 run、`cost/aggregate_06b.json`、API 0)
- 最終 entry 110 件(PASS 103 / PWW 7)・attempt 単位 127 件の judge record を機械集計: 受理のうち **値ガード DIFF または否定差 = 0**。独立 oracle(canonical と採用転写の数字集合・否定語の差)で不一致 **0**(集計 script の誤検知1種=JA「ずれ/ズレ」を否定語「ず」と誤認、否定パターンを絞込み後に 0)。
- **旧 PASS→新 NG 候補**(同一 attempt で Primary が passed なのに最終 NG): **0**。実例: `xrun` a2 full_story_part3 attempt1 は **TTS が原稿にない否定("isn't an estimate" ← 原稿 "is an estimate")を発話**し、Primary が `TRUE_CONTENT_MISMATCH`、値/否定ガードが `NG_PROTECTED p1_value_diff` で不採用→再生成 attempt2 が PASS(`xrun/attempt_history.jsonl`)。Primary 側でも不合格であり旧 PASS ではない。
- STOP 条件(重大な誤 PASS・HR Lock 抵触・予算超過)は発生なし。

## 12-6. Section 固有例外(原文 L143-153)の維持
1. Key Phrase: 学習対象表現は変更しない(KP 英語は `used_form` そのまま TTS・判定、LR 対象外)。zep/zep2/lega で `kp1_english` PASS、書換無し。2. JA LR: 流用していない(`ja_hr` は LR 無しで HR)。3. 見出し・短文: 独立 QA 維持(`head`)。4. A2 6% 減速: 減速後 wav の sha で判定(zep/zep2/lega/xrun、`slowdown_applied=true`)、減速前後の ASR・再生成は通算上限内。5. Dialogue: speaker melos の Voice 区分・既存 segment 構造維持(zep/zep2 `full_story_part1_c2`)。

## 12-7. 15 必須受入条件 対応表(更新版)
原文は `docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md` L201-L215(各条件の逐語は §3 の左列と同じ)。L217「**1項目でも未確認であればPRODUCTION_WIREDと報告しない。**」

| # | 06 時点 | 06b 後 | 06b の根拠 / 残作業(費用見込み) |
|---|---|---|---|
| 1 ASR判定仕様と Production 動作の一致(L201) | 一部 | **一部充足(前進)** | Z(a2/b1b 全 Section)・X(b1b 全+a2 非KP)・legacy A(b1b/a2 全 Section)・C(3 voice leaf)・B(Voice A/B a2/B1)の実音声で、Primary PASS→Secondary 不呼出、NG→Secondary 1回→PWW、両NG→通算3回、値/否定ガード、減速後判定を確認。**未実施**: ①X a2 の KP(gloss Gate 停止=KGCPW の KP 再生成が前提、約 JPY 5〜8) ②Family B の B1 全体・Hook/Tension/Closing・見出しの再生成(承認済み asset を再利用。pro-preview-tts が 1 clip 約 JPY 2〜3.3、約 JPY 10〜15) ③C の Comment(JA, LLM)・JA title の再生成 ④Dialogue(Std)・KP phrase 4回構成の通算上限 runtime(test のみ) |
| 2 日本語・英語、全 Section(L202) | 一部 | **一部充足(前進)** | 静的 35 entry/deferred 0。`APPLICABILITY_MATRIX_01.csv` 43 行のうち §12-10 のとおり **実音声 34 行、一部 1 行(A-A2-03 の KP 英語は再利用)、再利用で判定なし 5 行(仕様どおり)、既存 Gate で API 0 停止 2 行(X-A2-07/08)、N/A 1 行**。実音声行でも B-A2-01・B-B1-01・C-01 は一部 segment のみ(条件1 ②③) |
| 3 Primary NG→Secondary PASS を WARNING 付で採用(L203) | 充足 | **充足** | 06 + xrun a2 topic_intro(`xrun/clip_table.md:3`)、lega a2 comment_1(`lega/clip_table.md:21`、JA)、zep2 a2 full_story_part1_c1(減速後)/comment_1(`zep2/clip_table.md:6,9`)ほか PWW 7 件 |
| 4 両NG→最大3回の TTS 生成フロー(L204) | 一部 | **一部充足(前進)** | 実音声: KP 解説(06)、b1b Full Story narrator(3回→10分 cool-down→LR→v1)、A2 narrator(3回→LR 候補不成立→HR)、JA comment(3回→HR・LR なし)、Point 見出し(3回→HR)。**残**: Dialogue(Std)・KP phrase(4回構成)の通算上限 runtime(test のみ。各 約 JPY 2〜4/ケース) |
| 5 数値の同値・異値+否定保護(L205) | 充足 | **充足** | §12-5 + xrun 実例(TTS の否定誤発話を遮断) |
| 6 Connected Speech/M1/F1 回帰(L206) | 充足 | 充足(06 のまま) | 06 §4。06b でも旧 PASS→新 NG 0 |
| 7 試聴リストへの WARNING 連動(L207) | 一部 | **充足** | X/Z の**最終 HTML ページ**に節(0件・n件の双方): `zep/pages/*.html:2`(0件)、`zep2/pages/*.html:2`(2件)、`xrun/x_out/player.html:62,64`(0件/1件)。legacy A 単独 HTML(`lega/theme/a2/audit/pass_with_warning_listening_list.html:2` 1件)。B/C の hook は実行され JSON+HTML(0件)を出力(B/C で WARNING>0 の自然発生は無し) |
| 8 Secondary 二重呼出・予算超過・無限 retry なし(L208) | 充足 | **充足** | 06b 全 run の同一 wav への Azure 重複 0(23 呼出)。retry は通算3回+LR で停止(`lr_en` は LR の入れ子 4 回で収束、D-B4 参照)。予算: 06b 約 52.0 < 80。実障害での circuit breaker 連続発動は mock のみ(06 と同じ) |
| 9 Production 正式 path の runtime evidence(L209) | 一部 | **一部充足(前進)** | Z・X・B(a2)・C・legacy A はいずれも各 Family の Production 入口(CLI `main()` / `run_tts_stage` / `generate_*_segments`)で実音声。残: 条件1の ①〜④ |
| 10 Unit/Regression/Integration test PASS(L210) | 充足(既存) | 充足(既存) | 本委任は Production コード無編集のため再実行せず(06 の 398 passed を継承)。evidence 用スクリプト自体の test は無し |
| 11 SSOT 反映(L211) | 未 | **未充足(委任_07)** | |
| 12 commit/push/merge(L212) | 未(一部) | 未充足(一部) | 本委任の commit/push は §F、merge は委任_07 |
| 13 Dangling Reference Check(L213) | 未 | **未充足(委任_07)** | |
| 14 未解決 UDR・未配線 APPROVED の明示(L214) | 一部 | 一部充足 | §12-8・§12-11 を追加。SSOT 反映は委任_07 |
| 15 Fable の独立照合(L215) | 未 | **未充足(Fable の工程)** | |

## 12-8. 逸脱・発見(正直な記録)
- **D-B1 初回 `ja_hr` が未隔離の JA Foreign Token Gate queue へ 1 行追記**: JA 原稿に Latin 語を入れたため Production の Foreign Token Gate が **TTS 前に停止**し、`er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`(untracked、既存 343 行)の **344 行目**に追記(`grep -n evidence_06b` で特定可、API 0)。runner を修正(同 queue パスを evidence 配下へ差替)して再発防止。**行の除去は権限分類器に拒否されたため未実施(残置)**。Fable/ユーザー判断: 当該1行の除去可否。
- **D-B2 同 `ja_hr`(2回目、Latin 語なし)が未隔離の JA HR queue へ 1 行追記**: `er007_output/ja_asr_cascade_01/human_review_queue.jsonl`(tracked・作業ツリーは既に差分あり)の **12 行目**(`evidence_06b/ja_hr` を含む行)。`HUMAN_REVIEW_LOG_PATH_JA` を隔離(以後の run は 0)。**除去は未実施**(上と同じ理由)。06 の隔離(`apply_isolation`)は EN 側 queue のみで JA 側が漏れていた(06 は JA 失敗経路を走らせていないため未発現)。
- **D-B3 費用 wrapper の不足と校正**(§12-1): 固定単価の過小、Luna(Responses)未計測。委任文の「全経路の費用記録を事前確認」が単価の妥当性まで担保できていなかった。06 の JPY 9.2 も約 9.9 に再推定。
- **D-B4(発見) Local Rewrite の入れ子再帰は Production の既存挙動で、`LR 1回/segment` が守られていない**: `lr_en` では `run_local_rewrite_recovery` が **4回**(`lr_en/attempt_history.jsonl:1-4` の `LOCAL_REWRITE_RECOVERY`)。理由: LR 内の再 TTS(`generate_news_narration_wide_margin.__wrapped__`, `max_attempts=1`)が失敗すると、その関数自身が末尾の LR 回復(`er003_v1_sing01_news_tail_fix.py:317` 付近の loop 後 LR)を再度呼ぶ。`main` にも同構造あり(`git show main:er003_v1_sing01_news_tail_fix.py` の L291・L317)で **AUW 起因ではない**。終了は LLM が通る候補を出すか候補不成立まで(上限なし)。matrix XC-02 の「LR 1回/segment」と不整合。
- **D-B5(発見) LR で解決した segment でも HR queue に 4 行残る**(`lr_en/human_review_queue.jsonl`)。通算上限到達時の NG が LR 前に queue へ書かれる既存構造(AUW の is_last_slot 配線で v1 の最終 slot NG も書く)。最終的には RESOLVED なので queue は過剰通知になりうる。
- **D-B6(発見) `audio_text_deviation` は最初の LR の書換(`The mayor, Xzqwtrlk, said…`)を記録するが、実際に発話・採用された音声は入れ子 4 回目の書換(`…whose name is spelled out as the letters X, Z, Q, W, T, R, L, and K…`)**(`lr_en` の `tts_generation_results.json` の `audio_text_deviation.audio_text_after` と `asr_judgement.primary.text` が不一致)。監査 record が実音声とずれる(Production 既存構造+入れ子 LR)。LR 後 v1 の判定対象が書換後テキストである点も含め仕様判断を伴うので修正せず報告。
- **D-B7 Z の失敗 entry は per-attempt の `asr_judgement` を保持しない**(06 D4 と同種): `ja_hr`/`a2_fail`/`head` の `tts_generation_results.json` は status のみで、判定詳細は `attempt_history.jsonl`(隔離)にある。
- **D-B8 既存 Gate による停止**(AUW 無関係、Gate は回避せず): Family C `story_001` の禁止記号(コロン)Gate(`crun_attempt0…`)、X a2 の KGCPW gloss Gate、B a2 の Key Phrase 出典整合 Gate。いずれも API 0 の fail-closed。
- **D-B9 C runner 自身の費用推定との差**: C runner の `cost_estimate=Y3.60` は固定単価(TTS 0.9/ASR_DIAG 0.3)で、cost logger 実額 0.95 と大きく異なる。
- **D-B10 集計 script の誤検知**: JA「ずれ/ズレ」を否定語「ず」と誤検知(否定パターンを絞込み、再集計で 0)。

## 12-9. 費用の再推定方法
`er078_auw_cost_revise_06b.py`: TTS=呼出数×平均 clip 秒×0.0243、ASR=呼出数×平均 clip 秒×0.0047(いずれも `xrun/x_out/raw_usage_log.jsonl` の token 実測から校正)、Azure=送信 wav 秒の実測×0.0444。結果 `cost/revised_estimates.json`。xrun/brun/crun は Production cost logger の実額に置換。lr_en は LR の Luna 8 call を 1 call 約 0.12 JPY(gpt-6-luna 0.1/0.5 USD per M token、約 1500 in/1200 out)で加算。

### 12-9(追補・委任_06c): 「Primary NGのたびにAzure 1回」の増分費用試算(OF-AUW-C-10、API 0)
出典: `er078_auw_cost_increment_06c.py`(`er011_output/attempt_history.jsonl`、action=PROCEED・language=en・test/wiring系theme除外)→ `evidence_06c/cost_increment_06c.json`。単価: Azure 0.0444円/秒(=$1/h x 160円/USD / 3600)。
- **増分の発生源**: 旧は Primary が TRUE_CONTENT_MISMATCH(TCM)の場合 Secondary 不呼出。新(原文L54-55)は不一致の種類によらず(保護差・除外表を除き)Secondary 1回。ASR_VALIDATION_UNCERTAIN は旧 Cascade でも Azure を呼んでいた(旧最大2回→新1回=削減側)ので増分に数えない(悲観ケースのみ数える)。
- **実測入力(本文 = Full Story part・Point 本文、EN)**: attempt_detail 付き 217 attempt 中 TCM 6(2.8%、95%上限 5.9%)・UNCERTAIN 14(6.5%)。1 call あたり TTS attempt 平均 1.235(全 600 call)。KP 英語 phrase は TCM 5.6%(6/108)だが約2秒/clip(Azure 約0.09円/呼出)で 5本/level でも約0.03円=無視できる。短文ナレーション(preview・topic_intro・comment)は 38 attempt 中 TCM 1。
- **試算(1 記事セット = Advanced 本文3 part + Standard 本文3 part。Standard は減速前後の2判定で最大2回)**:

| 本文 part の音声長 | Azure/呼出 | 中央値(TCM率 2.8%) | 95%上限(TCM率 5.9%) | 悲観(TCM+UNCERTAIN 9.2%を全て増分) | 全6 part が各1回NG(非現実的な上限) |
|---|---|---|---|---|---|
| 40秒 | 1.78円 | **0.55円/セット** | 1.17円 | 1.82円 | 16.0円 |
| 60秒 | 2.66円 | **0.82円/セット** | 1.74円 | 2.72円 | 23.9円 |

- 15-9「+1円/セット以上は記録」: 中央値(0.55〜0.82円)は閾値未満、95%上限(1.2〜1.7円)・悲観(1.8〜2.7円)は閾値超 → 記録対象。目標70円/セットに対する比: 中央値 約0.8〜1.2%、悲観でも約2.6〜3.9%。現行ベースライン(円/セット)は 15-9 のとおり未測定のため「現行→予測」は差分のみ提示。
- KP 解説3回化(§12-7 1)の増分(期待+0.09円・最悪+2.2円/セット)と本試算は独立に加算される(合算の悲観側でも約5円/セット以内)。PASS_WITH_WARNING 採用による再生成回避(削減側)は、ログに Primary NG→Secondary 救済の記録が無く定量化できない(削減方向、未差引き)。
- 注意: attempt_history.jsonl は近年のみ attempts_detail を持つ(217 attempt)。TCM 6 件は小標本のため 95%上限を併記した。

## 12-10. `APPLICABILITY_MATRIX_01.csv` 43 行の実音声カバレッジ
- 実音声(34 行): X-B1-01,02,03,04,05,07 / X-A2-01,02,03,04,05,06 / Z-B1-01,02,03 / Z-A2-01,02,03,04,05 / Z-ALL-01,02 / A-B1-01,02,03,04 / A-A2-01,02 / B-A2-01(Voice A/B 本文)/ B-B1-01(Voice A/B leaf)/ C-01(narrator・device・voice 本文)/ XC-01,02,03。
- 一部(1 行): A-A2-03(KP 日本語意味は実音声、KP 英語は Master Store 再利用)。
- 再利用・複製で判定なし=仕様どおり(5 行): X-B1-06(新規生成は他 Family の同一 leaf で確認)、X-B1-08(複製)、X-B1-09・X-A2-09・Z-ALL-03(固定 shell=copy)。
- 既存 Gate の API 0 停止(2 行): X-A2-07,08。N/A: Y-00。

## 12-11. 委任_07 / Fable への申し送り
1. **D-B4〜D-B6(LR の入れ子再帰・queue 過剰通知・監査 record のずれ)**: AUW 起因ではない Production 既存挙動。AUW の受入条件(条件 4・8)と矛盾しうるため、仕様判断(LR を厳密に1回に制限するか、入れ子の最終書換を `audio_text_deviation` に反映するか)を Fable/ユーザーへ(技術的解決案: 再 TTS 側で `enable_connected_speech_equivalence_layer=False` の leaf を呼ぶ=LR 内 LR を禁止、は承認済み仕様 D の意味変更を伴うため未着手)。
2. **D-B1/D-B2 の queue 追記2行の除去可否**(上記)。
3. 未実施の実音声(条件 1・2・4・9 の残): ①X a2 KP(KGCPW の KP 再生成が前提)②Family B の B1 全体・Hook/Tension/Closing・見出し ③C の Comment(JA)・JA title ④Dialogue(Std)・KP phrase 4回構成の通算上限。見込み費用: ①約 JPY 5〜8、②約 JPY 10〜15、③約 JPY 4〜6(LLM 含む)、④約 JPY 3〜8。合計でも 06b の残予算(80−52.0=約 28)内。
4. **Z の実行方法(D-B11)**: Z の Production runner `er026_family_z_fiction_production_runner_01.py` は writer/KP の LLM stage と最終予算 guard を含み最小構成で使えないため、本 evidence は同 runner の tts/shell/gate/assembly/pages 各 stage が呼ぶ `er063` 関数(`er026:1364,1381,1390,1400,1408`)を**同順で直接呼出**した(`zep`/`zep2`)。er026 は `cl.install(cost_log)`(`er026:1738`)を呼ぶが、直接呼出の evidence run では呼ばれないため、Z の費用は本 evidence の wrapper(§12-1)で記録した。legacy A(`er003_v1_n3_01_tts_generate.py` の `main()`)は `cl.install` を呼ばない(Production 自体の費用 logger 未記録経路。06 D1 の再確認)。15-9 の実費算定に必要なら OPEN 化を推奨。
5. 06b の evidence runner は `er078_auw_runtime_evidence_06b.py`(全 run がこの1ファイルの part 切替)。再現手順は `evidence_06b/<run>/stdout.log` とコマンド `.venv\Scripts\python.exe er078_auw_runtime_evidence_06b.py <part> --execute --budget-jpy N`。

## 12-12. 判定材料(宣言しない)
- 満たす材料: 条件 3・5・6・7・8 は実音声で充足。条件 1・2・4・9 は大幅前進(残は §12-11-3 の4点)。誤受理 0・数値/否定誤 PASS 0・旧 PASS→新 NG 0(06b 110 entry/127 attempt)。X/Z の最終 HTML に試聴リスト節(0件・n件)が出ることを実 run で確認。HR Lock 非抵触(全 Lock は run 内)。
- 満たしていない材料(「1項目でも未確認」に該当): 条件 1・2・4・9 の残4点、条件 11・12(merge)・13・15。ならびに D-B4〜D-B6(LR 入れ子)の仕様判断、D-B1/B2 の queue 2行。
- 費用: 06b 約 JPY 52.0(推定を含む、上限 80 内)、06+06b ≒ 61.9。
