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


# §13 委任_06d 追加 evidence (残 Section/Family 実音声・是正後経路の実音声・再利用 guard・legacy A 費用記録の是正)

管理ID `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_06d / 日付 2026-10-16 / branch `feat/auw-unified-asr-01`(起点 HEAD `e81696197`)。main 無変更。**判定の宣言(PRODUCTION_WIRED 可否)はしない。材料のみ。**
Production コード変更は **E の 1 箇所のみ**(`er003_v1_n3_01_tts_generate.py` `main()` に `cl.install(...)` 4 行追加)。他は evidence runner(`er078_auw_runtime_evidence_06d.py`/`..._06d_z.py`)・集計(`er078_auw_aggregate_06d.py`)・test(`er078_asr_unified_wiring_06d_test_01.py`)・本節・`evidence_06d/`。
使用モデル(最新か): Primary ASR=`gpt-4o-mini-transcribe`(Production の ASR_ROUTING 現行)、Secondary=Azure Speech、TTS=X/Z/KP/reuse は `gemini-3.8-flash-lite-tts`、Family B・legacy A・Dialogue(Voice A/B 経路)・C は `gemini-2.5-pro-preview-tts`(各 Family の Production 現行モデル。評価用に選んだものではない)、LLM(C Comment・Local Rewrite)は `gpt-6-luna`。
費用の記録: 全有料経路を SDK レベル wrapper で呼出『前』に STOP/予算確認+応答 usage の token×`pricing_snapshot`(USD_JPY=160)で記録(`usage_log.jsonl` の Gemini/OpenAI 133 行すべて `basis=token_actual`、固定単価・fallback 定数の使用 0。Azure 18 行は送信 wav 秒の実測×0.0444 JPY/秒)。pro-preview-tts は 20 USD/M output token(25 token/秒)=約 0.084 JPY/秒(C の 17 秒 clip 1 本=1.43 JPY を実測確認)。Production cost logger 実額との突合: b1 7.617 vs 7.617、xkp 0.54 vs 0.5376、lega1 2.2884 vs 2.2877。
前提: 各 run 前に `tools/stop_scope_check_01.py --managed-id AUW-06D --run-dir <run> ...` を実行し rc=0(`evidence_06d/<run>/stop_check_pre.json`、T-0 は `evidence_06d/stop_check_T0.json`)。外部停止・原因不明 rc≠0 は無し。T-0: 委任文 `docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_06d.md`、checker=`_06d_check.json`(FAIL: 標準テンプレ見出し欠落、非ブロッキング)。

## 13-1. 当初目的(ユーザー原文の逐語。`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`)
- L54「Primary NGなら、不一致の種類によらず原則Secondaryを実行する。」 L55「Primary NG・Secondary PASSなら、PASS_WITH_WARNINGとして採用する。」 L58「Primary・Secondary両方NGなら次のTTS再生成へ進む。」 L59「Secondaryが障害・利用不能の場合、PASS扱いせず、既存の安全な障害処理へ進む。」 L60「同じ音声に対するSecondaryの重複API呼び出しを防ぐ。」
- L97「この安全条件と「Secondary PASSなら採用」の原則が競合する場合は、数値・否定などの明確な重大内容差を誤採用しないことを優先する。」
- L201-L215 必須受入条件 15 項目(§3 左列と同じ)。L217「1項目でも未確認であればPRODUCTION_WIREDと報告しない。」

## 13-2. 実行した run 一覧と費用(`evidence_06d/cost/spend_ledger.jsonl`、合計 **JPY 23.83**、上限 45 の 53%)
| run | 内容(Production 入口) | TTS | ASR | Azure(呼出/同一wav重複) | JPY |
|---|---|---|---|---|---|
| `xkp` | X `er019 main --stage tts/assemble/player --level a2`(KGCPW 整合済み E7 の KP[gloss_alignment_status=ALIGN_PASS]+06b xrun a2 の非KP 11 clip を cache 複製) | 6 | 6 | 1 / 0 | 0.54 |
| `xkpen` | X の KP 英語入口 `ensure_key_phrase_english_component`(Master Store 経由。未登録 2 phrase+登録済み 1 phrase) | 2 | 2 | 0 / 0 | 0.10 |
| `b1` | Family B `er012 run_tts`(B1 全 Section: Topic/Preview/Comment×4/見出し×2/Voice A,B 本文/Hook×2/Tension/Closing=14 clip。**入力は各 1-2 文に縮約**、leaf・引数は run_tts のまま) | 14 | 14 | 0 / 0 | 7.62 |
| `cja`(+`cja_attempt0/1/2_*` 停止・不成立 run) | Family C `er013 main --level a2 --only-segments comment_1..3`(Comment JA の LLM 再生成+TTS、JA title) | 3 | 0 | 0 | 5.38(LLM 11 call 約 1.27+TTS 3 clip 約 4.12) |
| `dlg_recover` | Z `run_tts_stage` Dialogue(Std)、減速段階に故障注入 1 回 → 取り直し → OK | 2 | 4 | 0 / 0 | 0.75 |
| `dlg_cap` | 同、減速段階に 3 回故障注入(別文に数値語あり=保護差) → 通算 3 回 → STOPPED | 3 | 6 | 0 / 0 | 1.03 |
| `dlg_cap2` | 同、数値語なしの別文 → Secondary(Azure)経路 → 通算 3 回 → STOPPED | 3 | 6 | 1 / 0 | 1.50 |
| `kp4_leaf` | KP 英語 4 回構成の Production 入口 `generate_key_phrase_component_verified`(固有名で全 NG) | 4 | 4 | 4 / 0 | 0.70 |
| `kp4` | Z `kp_en`(同じ固有名) | 2 | 2 | 2 / 0 | 0.34 |
| `nlkp` | Z `kp_en` で "can't wait"・"30 percent"(Primary に言語ヒント ja を与え非ラテン転写を誘発) | 2 | 2 | 1 / 0 | 0.15 |
| `probe_nl` | 否定入り phrase に zh/ko/ru/ar ヒントで非ラテン転写が得られるかの実 Primary 4 呼出 | 0 | 4 | 0 | 0.02 |
| `nlneg` | 非ラテン KP 救済の否定/数値(半実音声: 実 TTS+実 Azure+保存例の非ラテン Primary 転写) | 3 | 3 | 3 / 0 | 0.54 |
| `tstop` | Z `run_tts_stage`(b1b comment×3)、Secondary(Azure)のみ mock 障害 | 4 | 4 | 0(mock 5) | 1.62(Luna 4 call 含む) |
| `derive` | 06b zep2 の実 run に対し registry 導出を失敗させて最終ページ再生成(API 0) | 0 | 0 | 0 | 0 |
| `reuse` | Z results cache 再利用: DIFF(hanshin topic_intro、blocklist)→再生成 / EQUAL(zep の full_story_part2_c1)→再利用 | 3 | 3 | 3 / 0 | 1.25 |
| `lega1` | legacy A `er003_v1_n3_01_tts_generate.main()`(是正後)→ 1 clip(b1b Charon comment、Secondary まで到達) | 3 | 3 | 3 / 0 | 2.29 |
| **06d 合計** | | **54** | **63** | **18 / 重複 0** | **23.83** |
累計: 委任_06(再推定約 9.9)+06b(52.0)+06d(23.83)≒ **JPY 85.7**。06d 単体は上限 45 内。

## 13-3. A: 残 Section の実音声 (①〜④)
**① X a2 KP**(`xkp`、`xkp/clip_table.md`・`xkp/x_out/a2/audit/tts_generation_results.json`): KGCPW 整合済み KP(E7、`gloss_alignment_status=ALIGN_PASS`)で **gloss Gate は停止せず通過**(Gate 迂回なし)。`tts`→`assemble`→`player` すべて OK。KP 日本語意味 5 clip を新規生成し **5/5 `asr_judgement` あり**(PASS 5、うち 1 件 `primary_pass_approved_equivalence:READING_MATCH`、Secondary 呼出 0)。KP 英語 5 clip は Master Store 再利用(判定なし=仕様どおり)。非KP 11 clip は cache 再利用(値ガード EQUAL → `asr_judgement_inherited` 継承 11/11、API 0 → C の X 側確認を兼ねる)。X の KP 英語の**新規生成**は `xkpen` で補完: 未登録 "hold the line"・"cut it close" を Production 入口で生成、いずれも `asr_judgement` あり(PASS)、登録済み "right away" は Master hit(API 0・判定なし)。
**② Family B B1 全体**(`b1`、`b1/clip_table.md`): 14 clip すべて **`asr_judgement` あり・PASS**(Primary のみで通過、Secondary 0・重複 0)。見出し 2・Voice A/B 本文 2・Hook 2・Tension・Closing(in_one_line)・Topic/Preview/Comment×4。見出しは `point_headings.generate`(独立 QA 維持)。**注意**: 入力縮約(各 1-2 文)のため pro-preview の 1 clip は短く(総 7.62 JPY)、長尺本文の実費とは異なる。また `run_tts` 後の `finalize_tts_results` が KP ファイル不足で例外になり(runner 側の前提不足、Production 無関係)、results JSON は未生成。判定は隔離 `attempt_history.jsonl`(14 record)から表化(06b D-B7 と同じ扱い)。有料 run は再実行せず。
**③ Family C Comment(JA)・JA title**: **Production runner 上で成立しなかった**(§13-7 F4)。`cja`: Comment 3 本の LLM 再生成は成功(gpt-6-luna、3 call)、TTS が `tts_call_for_voice("narrator")` → `generate_narration_snippet_verified_strict(text, "en", ...)` で**英語固定**のため日本語 Comment の音声が 3 回とも「生成音声長 16.9/15.3/16.4 秒が見積上限 5.5 秒を超過」で破棄され STOPPED(ASR 0 回、実費 4.46)。JA title は Comment の後段のため未到達。reuse_from 経由の旧資産では動くが、その場合は `.ok` のみ複製で `meta` を複製しないため **LLM 再生成した新しい文面にも旧音声が紐づく**(`cja_attempt1/2` で実測)。JA Comment/JA title の AUW 判定の実音声は **Z(06b zep2 a2 comment、japanese_title)と legacy A(06b lega a2 comment)** で既に取得済み(§12-2)。
**④ Dialogue(Std) 通算 3 回・KP 4 回**:
- `dlg_recover`(半実音声: 減速段階の出力を**別文の実音声を 6% 減速したもの**に 1 回だけ差替、TTS/Primary/Secondary は実物): `A2_SLOWDOWN_REVERIFY` attempt1 = 不一致 → 通常ペースから**取り直し**(TTS 通算 2 回)→ 2 回目 OK(`tts_generations_used=2`)。
- `dlg_cap`(3 回とも差替、別文に数値語 "nine"): 減速後 Primary が値差 → **`NG_PROTECTED p1_value_diff`・Secondary 不呼出**(保護差の仕様どおり)、`tts_generations_used_cumulative` 1→2→3、最終 `STOPPED`(通算 3 回で打切り、4 回目なし)。
- `dlg_cap2`(数値語なしの別文): 減速後 Primary 分類 `TTS_FAILURE`(別文の転写=内容不一致)→ **Secondary(Azure)1 回**(同一 wav は run cache で 2 回目以降不呼出=重複 0)→ 不採用 → 通算 3 回 → `STOPPED`。
- KP 英語 4 回構成の Production 入口(`kp4_leaf`、固有名 "Xzqwtrlk wrangle"): **TTS 4 回(MINIMAL×2+ENGLISH_LOCK×2)・Secondary 4 回(重複 0)・HR queue 1 行(slot 4 のみ)**、slot 1→4 が各 attempt の `asr_judgement.slot` に記録。既存例外(4 回構成・Prompt 切替・LR なし)は維持。
- ただし Z の `kp_en`(同じ固有名、`kp4`)は **TTS 2 回で `HUMAN_REVIEW_LOCKED`**(§13-7 F1)。
各 clip の `asr_judgement` 有無・state・Secondary 回数: `evidence_06d/*/clip_table.md`。

## 13-4. B: 是正後経路の実音声
**(a) 非ラテン KP 救済(06c OF-AUW-C-01)**:
- `probe_nl`: 実 Primary は "can't wait" を言語ヒント zh/ko/ru/ar でも "Can't wait!" と英語で転写(**自然発生しない**)。
- 実音声(`nlkp` kp2): "30 percent" の Primary(ja ヒント)転写 `三十百分比`(非ラテン)→ Azure `30%.` を採用転写 → **`PASS_WITH_WARNING`(layers=`non_latin`、Secondary 1 回)**。
- 半実音声(`nlneg`、実 TTS 音声+実 Azure+保存例の非ラテン Primary 転写。Primary 転写の注入は明記): ① "I can't wait for 3 days." → Azure `I can't wait for three days.` → **PASS_WITH_WARNING**(`adopted_text`=Azure 転写、最終ゲート `value_guard=EQUAL, negation_diff=false`)。② 音声が "I can wait for 3 days."(否定欠落)→ Azure `I can wait for three days.` → **`NG_PROTECTED`**。③ 音声が "I can't wait for 4 days." → Azure `... four days.` → **`NG_PROTECTED`**。保護差は救済されない(reason は adapter 非採用経路の `p1_value_diff`。`final_gate_*` ではなくその前段で不採用)。Azure 転写は `nlneg/usage_log.jsonl`。
**(d) 技術 STOP(06c OF-AUW-C-06)**(`tstop`、実 TTS+実 Primary+Secondary のみ mock 障害): `comment_1`(b1b)は 3 attempt すべて `NG_SECONDARY_UNAVAILABLE`(`technical_stop.type=SECONDARY_UNAVAILABLE`, `restartable=true`, `approval_required=false`)で最終 slot まで到達。stage 終了時に **`[TECHNICAL_STOP] Secondary ASR障害: events=4 circuit_open=True ... Human Review Lock非投入・承認不要・再実行で再開可。`** を出力(`tstop/stdout.log:2`)。**同時に事実として**: leaf の `review_lock` は最終 `STOPPED` を理由不問で **`HUMAN_REVIEW_REQUIRED`**(`tstop/run/b1b/audit/review_lock_state.json`: `comment_1` state=HUMAN_REVIEW_REQUIRED, cumulative_tts_attempts=3)に入れ、`attempt_history` も `human_review_reached=true`(**U4 の材料**: Lock ロジック変更は未実施、現行では Secondary 障害のみの最終 STOPPED が Lock に入る)。さらに b1b は NG のまま Local Rewrite(Luna 4 call+TTS 1 回)まで進んだ。circuit open 後の 2 clip 目は技術 STOP entry を返すが、**`run_tts_stage` が `KeyError: 'style'` で異常終了**(§13-7 F2。results JSON 未生成、checkpoint のみ)。
**(e) 導出失敗表示(06c OF-AUW-C-12)**(`derive`、API 0): 06b zep2 の実 run に対し registry の導出を例外で失敗させて `build_pages` を実行 → `standard.html`/`advanced.html`/`index.html` すべてに **「導出失敗(要確認)」**、「0件(該当なし…)」は出ない。失敗を注入しない対照では「導出失敗」は出ず n 件節が出る(`derive/runner_execute.json: page_check/page_check_control`、`derive/pages_fail/`)。

## 13-5. C: 再利用経路の実動作(`reuse`)
- **DIFF → 再生成**: blocklist の hanshin `topic_intro`(保存 ASR "Hanshin wins 81" vs 原稿 "8–1")を、現行 spec の `reuse_key` に合わせて cache に置き(= guard が無ければ再利用される状態)、`generate_or_reuse_z` が `reuse_value_guard_blocked_previous={reason: PROTECTED_DIFF:final_gate_value_diff, unified_state: NG_PROTECTED}` を記録して**実 TTS で再生成**(3 attempt)。新音声の Primary は "wins 8-1"(値は正しい)だが固有名 "Hanshin" の聞き違い等で `NG_BOTH` → 最終 STOPPED(古い誤り音声は採用されない)。
- **EQUAL → 再利用+継承**: 06b zep の `full_story_part2_c1`(値 "8.7 percent")は guard を通過し `reused_from_previous_run=true`・**`asr_judgement_inherited`(state=PASS)**・API 0。X の cache 再利用(`xkp`)でも非KP 11/11 が同様。
- 旧 PASS→新 NG 候補 1 件(集計 script が検出): reuse の fallback attempt1(Primary NORMALIZED_MATCH だが Azure "wins 8 to 1" が `ASR_VALIDATION_UNCERTAIN`)。これは fallback route の**既存仕様 `force_secondary`**(Primary PASS でも Secondary 許容集合 PASS を必須)による NG で、**main(旧)の同関数に同一入力を与えても `verified=False`**(`reuse/old_main_force_secondary_check.txt`、API 0)。旧 PASS→新 NG の退行ではない。

## 13-6. E: legacy A 費用記録の是正
- 変更: `er003_v1_n3_01_tts_generate.py` `main()` の theme ループで `cl.install(f"{theme['out_dir']}/raw_usage_log.jsonl")` を `run_theme` 前に呼ぶ(新単価は追加せず、`pricing_snapshot.json` は無変更)。他の legacy entry を Grep(`generate_b1_segments`/`generate_a2_segments`/`run_theme` 参照 約 50 ファイル)確認: TTS を呼ぶ入口で `cl.install` を持たないのは `er003_v1_n3_01_tts_generate.py main()` のみ(他は過去 one-off 含めすべて `cl.install` 済み。`er003_v1_n3_01_assemble.py` 等は TTS API を呼ばない)。
- test(`er078_asr_unified_wiring_06d_test_01.py`、netguard 下 4 passed、API 0): 是正前の再現(未 install の `cl.record` は `init_logger` の RuntimeError)/`main()` が theme ごとに install/install 後は Secondary(Azure)呼出の費用が記録され RuntimeError で停止せず PASS_WITH_WARNING まで進む/pricing_snapshot 無変更。
- 実音声(`lega1`): 是正後の本番入口 `main()` 経由で 1 clip(b1b Charon comment、固有名で Primary NG)を実行 → **Production cost log `lega1/theme/raw_usage_log.jsonl` に 9 record(azure 3・gemini 3・openai_asr 3)**、`compute_cost_jpy_so_far`=2.2884 JPY(wrapper 実測 2.2877 と一致)、Secondary 3 回(重複 0)、**RuntimeError なし**(clip は 3 回 NG_BOTH で STOPPED=固有名のため。HR Lock は run 内に隔離)。

## 13-7. 発見・逸脱(正直な記録。いずれも誤受理・数値/否定の誤 PASS ではない)
- **F1 Z `kp_en` の 4 回構成が 2 回で止まる**(`kp4`): `er063 kp_en` は `generate_narration_snippet_verified_strict` を 2 段で直接呼ぶが外側 guard が無く、1 段目の最終 `STOPPED` で Review Lock が `HUMAN_REVIEW_REQUIRED` を記録 → 2 段目(ENGLISH_LOCK)は `HUMAN_REVIEW_LOCKED`(0 API)。実測: TTS 2・Secondary 2・`review_lock_state` HUMAN_REVIEW_REQUIRED(cumulative 2)・**HR queue 行なし**(slot 2/4 のため queue 対象外)= Lock だけ立ち queue に出ない。`main` の同関数も同構造(`git show main:er063_family_z_audio_01.py` L667-684)で AUW 起因ではない既存挙動。legacy/X の入口 `generate_key_phrase_component_verified` は `@guarded_generate` の外側 guard で 4 回に成る(`kp4_leaf`)。候補: Z `kp_en` を外側 guard 化(承認済み 4 回構成の Z への適用)=Production 変更のため未実施。
- **F2 Z の circuit open で `run_tts_stage` が `KeyError: 'style'`**(`tstop`、`tstop/runner_execute.json: stage_exception_traceback`): 06c(d)の `guard_generate` は `generate_or_reuse_z` の生成関数全体(`build_entry` を含む)を wrap するため、技術 STOP entry が `build_entry` を通らず `style` 等を持たず、`_evidence_row`(`er063:1023`)が参照して例外。stage は `[TECHNICAL_STOP]` を報告した後に異常終了(結果 JSON 未生成、checkpoint のみ。誤 PASS なし、再実行で再開可)。06c の test は `generate_or_reuse_z` の戻り値だけを検証していた。**修正案**(未実施): `run_tts_stage` で技術 STOP entry を `build_entry(spec, out_path, entry)` へ通す、または `_evidence_row`/`_store` を欠落 key 耐性にする(約 3 行)。
- **F3 Dialogue/Voices A2 外側ループの最終 NG が Lock/HR queue に出ない**(`dlg_cap`/`dlg_cap2`): entry は `STOPPED`(Gate が止める)だが、`review_lock_state` は `RESOLVED`(leaf は毎回 OK を返すため)、HR queue 行なし、entry の `asr_judgement` は**減速前の PASS のまま**(減速後 NG の record は `asr_judgement_post_slowdown_ng` に入るが Z の entry へは出ない)。原文 L58 の「両 NG→再生成→3 回 NG で LR/HR」の末端(HR)が A2 減速後 NG では起きない。既存 `generate_a2_segment_with_slowdown`(narrator)と同構造と推定(narrator 側は未検証)。仕様判断を含むため未実施。
- **F4 C runner の JA 新規 TTS 不能+reuse_from の旧音声紐づけ**(§13-3③): `tts_call_for_voice("narrator", ...)` は `language="en"` 固定(`er013:389`)で JA Comment/JA title/preview を新規生成できない。`_copy_with_ok` は `.ok` のみ複製し `meta` を複製しないため、reuse_from 経由の資産は文面変更を検知できない(`resumable_reuse` が現行文面の sha で meta を書く)。C の Comment(JA)/JA title の「統一 ASR 判定」は C runner からは到達しない(JA leaf `generate_a2_japanese_with_reading_safety` を呼ばない)。AUW 起因ではない既存挙動だが、条件 2 の C(JA)に影響。
- **F5 Secondary 障害でも Local Rewrite が走る**(`tstop`): b1b comment は 3 attempt すべて `NG_SECONDARY_UNAVAILABLE`(音声の良否は未判定)のまま LR(Luna 4 call+TTS 1 回)へ進んだ。U4(Lock ロジック)と同根の判断事項(技術 STOP は LR/HR より前に止めるか)。
- **F6 cja の有料 run 再起動 3 回(逸脱)**: `cja_attempt0`(C runner 内部 budget guard が LLM 1 call を ¥3.00 と見積り `--budget-jpy 8` で 3 本目前に停止、LLM 2 call のみ)→ 引数を直して再実行(`cja_attempt1`: reuse_from の旧音声が再コピーされ TTS 0 回、LLM 3 call)→ reuse_from 付替えで再実行(`cja_attempt2`: meta 非複製で同様、LLM 3 call)→ reuse_src から Comment/title を除いて再実行(`cja`: F4 で STOPPED)。計 4 run(初回+再起動 3)。委任文は再起動回数を明示許可していない。各回とも原因は事前確認不足(C runner の保守的見積り・reuse_from の `.ok` 挙動)で、TTS を伴う無駄は最後の 3 clip のみ。実費は計 5.38 JPY。以降の run は事前に dry-run とコード読解で挙動を確認してから 1 回で実行した。
- **F7 tstop の共有 state 不変チェックが false**: `shared_files_changed_outside_evidence=[er011_output/attempt_history.jsonl, er021_output/.../telemetry.jsonl]`。原因は、同時刻に**私が別 shell で走らせた pytest(n3 関連 36 file)**が既存 test の副作用で本番 `attempt_history`/`telemetry` へ追記したこと(末尾が test fixture の "fox/dog"・"Ottoni" 行)。evidence run 自身は隔離済みで書込なし(他の全 run は `shared_state_unchanged=true`、JA queue 2 ファイル行数も全 run で不変)。この 2 ファイルは作業ツリーで既に差分ありのため stage しない(06 D2 と同じ)。並行実行した私の判断ミス。
- **F8 B の runner 前提不足**: `b1` の `finalize_tts_results` が `key_phrases/keywords_canonicalized.json` を要求(縮約 run では未作成)し results JSON を作れなかった(判定は attempt_history で代替)。

## 13-8. 誤受理・保護の集計(`evidence_06d/cost/aggregate_06d.json`、API 0)
最終 entry 13 件(PASS 12/PASS_WITH_WARNING 1)・attempt 単位 47 件の judge record(PASS 30/NG_BOTH 13/PASS_WITH_WARNING 1/NG_SECONDARY_UNAVAILABLE 3)。受理のうち値ガード DIFF/否定差 **0**。独立 oracle(canonical と採用転写の数字集合・否定語)の不一致 **0**。誤受理 0。旧 PASS→新 NG 候補 1(上記 13-5、旧も NG と確認=退行なし)。Secondary 同一 wav 重複 **0**(全 18 呼出)。HR Lock・共有 state への未隔離書込 **0**(F7 は私の pytest による tracked ファイル追記で evidence run 由来ではない)。STOP 条件(誤受理・数値/否定の誤 PASS・旧 PASS→新 NG・未隔離書込・費用 45 超過・Gate 迂回)の発生なし。

## 13-9. 15 必須受入条件 対応表(06d 後)
| # | 06b 後 | 06d 後 | 根拠 / 残 |
|---|---|---|---|
| 1 ASR 判定仕様と Production 動作の一致 | 一部 | **一部充足(前進)** | 06b の未実施 4 点のうち ①X a2 KP ②B B1 全体・Hook/Tension/Closing・見出し ④Dialogue 通算 3 回・KP 4 回 は実音声で取得。③C の Comment(JA)/JA title は F4 により C runner から到達不能(成立しない)。是正後経路 (a)(d)(e) は実音声(一部半実音声)。新規発見 F1・F2・F3 は誤受理ではないが Production 動作の不整合 |
| 2 日本語・英語、全 Section | 一部 | **一部充足(前進)** | 43 行マトリクス(13-10)。未充足は C の JA 新規生成(F4)と B の A2 narrator 見出し/Hook/Tension/Closing(共有 helper は Dialogue で確認) |
| 3 Primary NG→Secondary PASS を WARNING 付で採用 | 充足 | **充足** | 06b+`xkp`/`nlkp`(PASS_WITH_WARNING `non_latin`)/`nlneg` |
| 4 両 NG→最大 3 回の TTS 生成フロー | 一部 | **一部充足(前進)** | Dialogue(Std) の通算 3 回(`dlg_recover`/`dlg_cap`/`dlg_cap2`、半実音声)・KP 4 回(`kp4_leaf`)を実測。Z の KP 英語は F1 で 2 回止まり、A2 減速後 NG の HR 末端は F3 |
| 5 数値の同値・異値+否定保護 | 充足 | **充足** | `nlneg` ②③・`dlg_cap`(保護差で Secondary 不呼出)・集計 oracle 0 |
| 6 Connected Speech/M1/F1 回帰 | 充足 | 充足(06 のまま) | 06d の ASR 判定コード変更なし |
| 7 試聴リスト連動 | 充足 | **充足** | (e) 導出失敗が最終ページに表示されること+対照を実 run で確認 |
| 8 Secondary 二重呼出・予算・無限 retry なし | 充足 | **充足(circuit 異常終了 F2 は別途)** | 06d 全 run 重複 0(18 呼出)。circuit breaker は mock 障害で実際に開き stage が `[TECHNICAL_STOP]` を報告 |
| 9 Production 正式 path の runtime evidence | 一部 | **一部充足(前進)** | X(a2 KP 含む)・B(B1)・legacy A(是正後 main())・Z を各 Family の Production 入口で実音声。C の JA(F4)・B の A2 narrator 一部が残 |
| 10 Unit/Regression/Integration test PASS | 充足 | **充足** | 新規 4 passed。AUW 中核 9 file(`patch_06d/test_core.txt`、6c 44・05 50・judge 45・en 53・ja 51・value_guard 58・registry 9・static audit 15)全 passed。n3 参照 36 file(`patch_06d/test_n3_related.txt`)の失敗 13 件はすべて 06c の baseline 失敗 id と同一(新規失敗 0。`FamilyAUnchangedTest` は E の未 commit 差分のため commit 前は失敗、commit 後に解消) |
| 11 SSOT 反映 | 未充足 | 未充足(委任_07) | |
| 12 commit/push/merge | 一部 | 一部(06d は branch commit/push、merge は委任_07) | |
| 13 Dangling Reference Check | 未充足 | 未充足(委任_07) | |
| 14 未解決 UDR・未配線 APPROVED の明示 | 一部 | 一部充足 | 13-11 を追加 |
| 15 Fable の独立照合 | 未充足 | 未充足(Fable の工程) | |

## 13-10. `APPLICABILITY_MATRIX_01.csv` 43 行の実音声カバレッジ(最終版)
- **実音声 37 行**: 06b の 34 行(X-B1-01,02,03,04,05,07 / X-A2-01〜06 / Z-B1-01〜03 / Z-A2-01〜05 / Z-ALL-01,02 / A-B1-01〜04 / A-A2-01,02 / B-A2-01 / B-B1-01 / C-01 / XC-01〜03)+ **X-A2-07(KP 英語: `xkpen`)、X-A2-08(KP 日本語意味: `xkp`)、A-A2-03(KP 英語は `xkpen` の同一 Production 入口 `ensure_key_phrase_english_component`、KP 日本語意味は 06b `lega`)**。このうち B-B1-01 は 14 clip 全 Section の実音声に拡張。**B-A2-01(A2 narrator 見出し/Hook/Tension/Closing は共有 helper を Dialogue で確認、Family B の A2 narrator 実行自体は未)・C-01(Comment JA/title は F4)は一部 segment のみ**。
- 再利用・複製で判定なし=仕様どおり(5 行): X-B1-06、X-B1-08、X-B1-09、X-A2-09、Z-ALL-03。
- 既存 Gate による API 0 停止: **0 行**(X-A2-07/08 の KGCPW gloss Gate は整合済み KP で通過)。N/A: Y-00。
- 合計 37+5+0+1=43。
- 実音声とは別に半実音声の項目(故障/転写の注入を明記): Dialogue 外側ループ(減速出力の差替)、技術 STOP(Secondary mock 障害)、非ラテン救済の否定/数値(Primary 非ラテン転写の注入)、導出失敗(registry 例外の注入)、再利用 DIFF(cache entry を意図的に再利用対象に構成)。

## 13-11. 06c の逸脱記録と OPEN 候補(委任_07 が SSOT へ転記)
- **06c(A)の逸脱記録(Fable 判断を記録)**: HR Lock `record_outcome` への技術 STOP 早期 return は**実施していない**(Lock ロジック変更=ユーザー判断事項 U4)。現行はSecondary障害のみの最終 STOPPED が Lock に入る安全側挙動(06d `tstop` で実測: `review_lock_state` HUMAN_REVIEW_REQUIRED、`attempt_history` `human_review_reached=true`)。
- **06c(B)の OPEN 候補**: results cache の DIFF 16 件は再利用時の動的 guard で再生成へ回す現行実装を採用(`reuse` で実 run 確認)。判定器の偽陽性の可能性(「いちばん/一番」、装飾記号)は委任_07 で OPEN 化(本 run は DIFF 側 1 件[hanshin 8–1]で真陽性を確認、偽陽性側は未実測)。
- **06c(C)**: 本委任 E で是正済み(§13-6)。
- **OPEN 候補(新規発見、Production 変更を伴うため未実施)**: F1(Z `kp_en` 外側 guard)、F2(Z circuit open の `KeyError`)、F3(減速後 NG の HR 末端・entry の stale `asr_judgement`)、F4(C runner の JA 新規 TTS と reuse_from の meta)、F5(Secondary 障害時に LR を走らせない)。**仕様候補**: スコア表記 "8–1" と Azure "8 to 1" の等価(fallback route の `force_secondary` で NG になる)。

## 13-12. 判定材料(宣言しない)
- 満たす材料: 条件 3・5・6・7・8・10 は充足。条件 1・2・4・9 は前進(残は C JA の到達不能[F4]、B A2 narrator 一部、F1〜F3)。06d の実音声 54 TTS で誤受理 0・数値/否定の誤 PASS 0・旧 PASS→新 NG 0(候補 1 件は旧も NG)・Secondary 重複 0。E は実 clip で費用記録を確認。
- 満たしていない材料: 条件 11・12(merge)・13・15、F1〜F3 の Production 動作の不整合(誤受理ではないが「1 項目でも未確認」の判断材料)。
- 費用: 06d 約 JPY 23.83(token 実測、上限 45 内)、06+06b+06d ≒ 85.7。

## 13-13. commit 後の確認
- commit: ea72fa482 (branch feat/auw-unified-asr-01、e81696197..ea72fa482 push 済み、main 無変更)
- `secret_scan_01 --staged`: hits=0 (391 files、`.wav`/`.mp3`/Master Store 複製/reuse_src は commit 対象外)
- commit 後 `er019_family_x_pointless_01_test_01.py::FamilyAUnchangedTest` を含め 10 passed(E の未 commit 差分による失敗が解消)
- 有料 API: JPY 23.83(06d 単体)


---

# 委任_06e 追記(2026-10-16): 06d で判明した実 run 不整合 F1〜F3 の是正と再実 run

## 14-1. 当初目的(ユーザー原文の逐語。`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`)
- L58「Primary・Secondary両方NGなら次のTTS再生成へ進む。」
- L39-49(3 回 NG で LR/HR): 同原文の該当節(06c §0 / 本書 §13-1 と同じ。HR Lock・LR は既存仕様の末端)。
- DESIGN_01.md:73(KP 英語 phrase の 4 回構成 = 2026-09-01 ユーザー決定)は既存例外として維持。
T-0: 委任文 `docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_06e.md`、checker=`_06e_check.json`(FAIL: 標準テンプレ見出し欠落、非ブロッキング)。stop_scope_check: T-0 と各 run 前(`evidence_06e/stop_check_T0.json`・`evidence_06e/<run>/stop_check_pre.json`)すべて rc=0。有料 run の再起動なし(3 run 各 1 回)。

使用モデル(最新か): 06d と同じ Production 現行構成(Primary ASR=gpt-4o-mini-transcribe、Secondary=Azure Speech、TTS=gemini-3.8-flash-lite-tts、LR の LLM=gpt-6-luna)。評価用に選んだモデルではなく Production 経路そのもの(§0 と同じ)。

## 14-2. 実行 run と費用(`evidence_06e/cost/spend_ledger.jsonl`、合計 **JPY 3.51**、上限 10 の 35%、token 実測 `basis=token_actual`)
| run | 内容(Production 入口 `Z.run_tts_stage`、故障注入は 06d と同一) | TTS | Primary ASR | Azure(呼出/同一 wav 重複) | LLM | JPY |
|---|---|---|---|---|---|---|
| `tstop` | b1b comment×3、Secondary のみ mock 障害 | 4 | 4 | 0(mock) | 4(Luna、LR) | 1.3719 |
| `kp4` | a2 `kp_en` "Xzqwtrlk wrangle"(Z 入口) | 4 | 4 | 4 / 0 | 0 | 0.6467 |
| `dlg_cap2` | a2 Dialogue(Std)、減速段階の出力を別文の実音声へ 3 回差替 | 3 | 6 | 1 / 0 | 0 | 1.4922 |
06d 比: tstop 1.6239→1.3719、kp4 0.3364→0.6467(TTS 2→4 回=是正で 4 回構成が成立した分)、dlg_cap2 1.5022→1.4922。各 run の `shared_state_unchanged=true`・`shared_files_changed_outside_evidence=[]`・JA queue 2 ファイル行数不変(`runner_execute.json`)。隔離 HR queue/Lock/attempt_history は `evidence_06e/<run>/`。

## 14-3. F2 `tstop`(Z `run_tts_stage` の circuit-open 後)
- 是正: `er063_family_z_audio_01.py` `normalize_technical_stop_entry`(新)を `run_tts_stage` の `_store`/`_evidence_row` の前に挿入。技術 STOP entry を `build_entry` で通常 entry 形にし、技術 STOP 固有 key(status/technical_stop/restartable/approval_required/human_review_required/reason/events)は保持、`sha256`/`duration_seconds`=None(残存 wav を今回の結果として記録しない)。
- 実測(`tstop/runner_execute.json`、`tstop/stdout.log`): **`stage_exception=null`(06d: `KeyError: 'style'`)**。`stage_result.statuses`={comment_1: STOPPED, comment_2/comment_3: `TECHNICAL_STOP_SECONDARY_UNAVAILABLE`}。結果 JSON・`runtime_evidence_04C.json` ともに生成(`results_json_exists=true`/`evidence_json_exists=true`、06d は未生成)。comment_2/3 は TTS 0・attempts 0(`clip_table.md`/`clip_rows`)、entry は `technical_stop=true, restartable=true, approval_required=false, human_review_required=false`。stdout に `[TECHNICAL_STOP] Secondary ASR障害: events=4 circuit_open=True types=['SECONDARY_CIRCUIT_OPEN','SECONDARY_UNAVAILABLE']。Human Review Lock非投入・承認不要・再実行で再開可。`。HR queue ファイルは作られず(技術 STOP は queue 対象外)。
- 06d からの差分: 異常終了 → 正常終了+技術 STOP entry 記録+evidence 出力。**変わらないもの**(F5/U4・変更しない): comment_1 は 3 attempt すべて `NG_SECONDARY_UNAVAILABLE` で最終 `STOPPED`、leaf 内 Review Lock は `HUMAN_REVIEW_REQUIRED`(`tstop/runner_execute.json: review_lock_state.comment_1`、cumulative_tts_attempts=3)、b1b comment は LR(Luna 4 call+TTS 1)まで進んだ。

## 14-4. F1 `kp4`(Z `kp_en` 4 回構成)
- 是正: `er063` `real_generators()` の `kp_en` を、legacy/X 入口 `generate_key_phrase_component_verified`(`@guarded_generate("en")`)と同形の外側 guard 付き `_kp_en_two_stage(text, out_path, spec)` に変更。1 段目 MINIMAL×2→2 段目 ENGLISH_LOCK×2(slot_offset 0/2、total 4)の呼出・Prompt・閾値は不変。legacy と同じ会計(`fallback_attempts_log`=1 段目の attempts_log)。HR Lock ロジックは無変更。
- 実測(`kp4/runner_execute.json`、`kp4/attempt_history.jsonl`): **TTS 4・Secondary 4(同一 wav 重複 0)**(06d: TTS 2・Secondary 2・`HUMAN_REVIEW_LOCKED`)。`attempts_detail` の `asr_judgement.slot` は MINIMAL 1・2、ENGLISH_LOCK 3・4。Lock は 1 段目 STOPPED では立たず、4 回目の最終 NG 後に **`HUMAN_REVIEW_REQUIRED`(cumulative_tts_attempts=4)**。**HR queue は 1 行**(最終 slot のみ。06d: 0 行で Lock だけ立った)。mainにも同構造があった既存事象を AUW の全 Family 統一の範囲で是正。legacy 入口 `kp4_leaf`(06d)と同じ 4 回/queue 1 行。

## 14-5. F3 `dlg_cap2`(Dialogue/Voices A2 外側ループの通算 3 回目 NG)
- 是正: `er003_v1_n3_01_tts_generate.py` に `finalize_a2_slowdown_final_ng`(新)。外側ループ(`generate_with_a2_slowdown_outer_loop`=Dialogue/Voices A2、および同構造の narrator `generate_a2_segment_with_slowdown`)で、最終周回の減速後再検証が NG のときだけ呼ぶ(内側が失敗した場合は内側 guard が STOPPED を記録済みのため呼ばない)。(i) entry の `asr_judgement`=減速後 NG の判定 record、減速前 record は `asr_judgement_pre_slowdown` へ退避(減速後 NG record が無ければ None)。(ii) 既存 `review_lock.record_outcome` へ STOPPED として渡す(内側が記録済みの TTS 試行を二重計上しないよう `attempts_log` 空)。HR queue 1 行は `apply_a2_slowdown_postprocess(log_human_review=True)`→`_post_slowdown_unified_judge` が最終 slot の減速後 NG でだけ既存 `_log_human_review` を呼ぶ(既定 False=他の直接呼出は無変化)。(iii) LR は新設せず(A2 外側ループ内に LR 配線は元々無い)。
- 実測(`dlg_cap2/runner_execute.json`): TTS 3(通算 3 回で打切り、4 回目なし)・Secondary 1(同一 wav 重複 0)・entry status `STOPPED`、**entry `asr_judgement.state=NG_BOTH`(primary.label=TTS_FAILURE。06d: 減速前の PASS のまま)**、Lock **`HUMAN_REVIEW_REQUIRED`**(`final_status=STOPPED`、cumulative_tts_attempts=3。06d: `RESOLVED`)、**HR queue 1 行**(`final_status=TTS_FAILURE`。06d: 0 行)。`attempt_history` の PROCEED 行は OK/RESOLVED ×3 の後に `STOPPED/HUMAN_REVIEW_REQUIRED(tts_this_call=0、二重計上なし)`。
- 観測(未変更): Z の entry は `build_entry` が `asr_judgement_pre_slowdown` を持ち込まないため `tts_generation_results.json` には退避 PASS record は出ない(leaf result と attempt_history の PASS 行には残る。委任_07 で Z entry へ additive に載せるか判断)。減速後判定の record の `slot` は `attempt_ctx={"slot":1}` 固定で 1 のまま(既存、変更せず)。narrator 側は実音声未取得(unit test のみ)。

## 14-6. test(通信遮断 plugin `netguard` 付き、API 0)
- 新規 `er078_asr_unified_wiring_06e_test_01.py` **11 passed**(F2 run_tts_stage 水準 circuit-open[技術 STOP entry が結果 JSON に載る・残 clip TTS 0・`[TECHNICAL_STOP]` 報告・異常終了なし]/F1[是正前の再現=2 段目が `HUMAN_REVIEW_LOCKED`、4 回構成、1 段目 STOPPED で Lock 先立ちなし、1 段目 OK は 2 段目へ行かない]/F3[通算 3 回 NG で asr_judgement 更新・Lock HR・queue 1 行・二重計上なし、再取り直し成功時は finalize しない、内側失敗時は二重記録しない、narrator 同形、直接呼出は queue 非書込])。
- 既存 test の追随(α類: `apply_a2_slowdown_postprocess` の test double に additive kwarg `log_human_review` を受ける `**kw` を追加): `er078_asr_unified_wiring_05_test_01.py`(spy_pp)、`er078_asr_unified_wiring_06c_test_01.py`(fake_post×2・lambda)、`er058_asr_tts_prodfix_01_test_01.py`(`_stopped_slowdown`・`ok_slowdown`)。期待値の変更なし。
- 影響 suite per-file(`patch_06e/test_post_06e_{main,extra,rest}.json`+`test_fix_rerun.json`、`patch_06e/summary_06e.json`): main 101 file 1,853 passed/27 failed(baseline=06c 100 file 1,840/29)、extra 113 file 2,578/9(同一)、rest 102 file 2,868/29(同一)。**06c baseline の失敗 id に無い新規失敗 0**(初回に出た新規 8 件=05 の spy 1・prodfix の double 7 は上記追随で解消)。main の baseline 失敗のうち 2 件(`ProductionModuleUnchangedTest` ×2)は 06e 時点で通過。AUW 中核 file(06e 11・06c 44・05 50・prodfix 27・er063 47 ほか)は全 passed。静的監査 `er078_asr_unified_wiring_static_audit_01.py` 15 passed、CLI 差分(`evidence_06e/static_audit_diff_06e.json`)=`unlisted_new_calls:[] / vanished:[] / count_changed:[]`(06c snapshot と一致)。`er011_human_review_lock_01.py` と `er078_asr_unified_judge_01.py`(U1=True・U2=A2_ONLY)の git diff は 0 行。

## 14-7. 15 必須受入条件の差分(06d 後 → 06e 後。変化のあるもののみ)
| # | 06d 後 | 06e 後 | 根拠 |
|---|---|---|---|
| 4 両 NG→最大 3 回の TTS 生成フロー | 一部充足(Z KP 英語は F1 で 2 回止まり、A2 減速後 NG の HR 末端は F3) | **充足に近づく(F1・F3 は実音声で解消。残は C の JA 新規生成 F4 のみ)** | `kp4`: TTS 4・queue 1・Lock 4 回後。`dlg_cap2`: 通算 3 回・entry NG・Lock HR・queue 1 |
| 8 Secondary 二重呼出・予算・無限 retry なし | 充足(circuit 異常終了 F2 は別途) | **充足(F2 解消)** | `tstop`: 異常終了なし・技術 STOP entry・`[TECHNICAL_STOP]`・残 clip TTS 0。06e 全 run 重複 0 |
| 1 / 2 / 9 | 一部充足 | 一部充足(F1〜F3 の不整合は解消。残は F4=C の JA 新規生成と B の A2 narrator 実音声) | 変化なし(F4 は本委任の対象外) |
| 3 / 5 / 6 / 7 / 10 | 充足 | 充足 | 06e の ASR 判定コード変更なし(判定器・閾値・Prompt・Voice・速度は不変) |
| 11 / 12(merge)/ 13 / 15 | 未充足 | 未充足 | 委任_07 / Fable |
| 14 | 一部充足 | 一部充足 | 下記 F5・観測を追加 |

## 14-8. 逸脱・発見(正直な記録)
- **F5(変更しない・U4 と同根)**: Secondary 障害のみの最終 STOPPED が leaf 内 Lock に入り(`tstop` comment_1)、Local Rewrite まで進む件は、依頼どおり未変更。
- **Production 動作の変化(意図)**: A2 外側ループ(narrator `generate_a2_segment_with_slowdown`・Dialogue/Voices A2)の通算 3 回目の減速後 NG は、これまでの `RESOLVED`+STOPPED から **`HUMAN_REVIEW_REQUIRED` Lock+HR queue 1 行** になる(原文 L39-49 の末端)。同一 segment・同一文面の再 run は承認(`approve_regenerate`)まで `HUMAN_REVIEW_LOCKED` で 0 API になる。
- 06d の逸脱(b)の再発防止: 有料 run 3 本は suite と並行させず、suite は有料 run の完了後に実行した。ただし既存 test(ProductionModuleUnchanged 系ほか)が本番 `er011_output/attempt_history.jsonl`・telemetry 等の tracked ファイルへ追記する副作用(ProductionModuleUnchanged 系に限らない既存 test 全般)は 06d と同じく発生した(`md5sum` 前後で attempt_history 変化を確認)。これらは作業ツリーで既に差分ありのため stage していない。evidence run 自身の隔離は `shared_state_unchanged=true`。
- 新規仕様候補: なし(承認済み設計・既存原文の末端の是正)。

## 14-9. 判定材料(宣言しない)
- 満たす材料: F1・F2・F3 は Production 入口の実音声で期待どおり(誤受理 0・数値/否定の誤 PASS 0・新規失敗 0・Secondary 重複 0・Lock ロジック/U1/U2 無変更)。06e 実費 JPY 3.51、06+06b+06d+06e ≒ 89.2。
- 満たしていない材料: F4(C の JA 新規生成・reuse_from の meta)、F5/U4(ユーザー判断)、条件 11・12(merge)・13・15。

## 14-10. commit 後の確認
- commit: dbed081d1 (branch feat/auw-unified-asr-01、faa82fdf5..dbed081d1 push 済み、main 無変更)
- `secret_scan_01 --staged`: hits=0 (79 files、`.wav` は .gitignore で対象外)
- commit 前後で `er011_human_review_lock_01.py` の diff 0 行。有料 API: JPY 3.51(06e 単体)

## 15. 委任_07 追記(narrator A2 外側ループの実音声1件=途中終了、後方互換 test、main 取込後の再確認)
### 15-1. narrator A2 外側ループの実音声(06e 申し送り(d)): **途中終了(自己 timeout)・再起動なし・未完**
- 実行: `er078_auw_runtime_evidence_07.py narr_cap3 --execute --budget-jpy 5`(Z `run_tts_stage`、`kind=narrator`・clip `full_story_part1_c3`・原稿 "I did not see a lower price today."・故障注入は 06d `dlg_cap2` と同方式=減速段階 call 1〜3 の出力を別文の実音声[06b `full_story_part1_c1_original.wav`]へ差替)。隔離=`evidence_07/narr_cap3/`。上限 JPY 5・1回のみ。開始前 `stop_scope_check` rc=0(`evidence_07/stop_check_prepaid.json`)。
- 観測(`evidence_07/narr_cap3/usage_log.jsonl`・`attempt_history.jsonl`・`run/a2/narration/`): attempt1 [TTS・Primary 2・Azure 1]→減速後 NG(`A2_SLOWDOWN_REVERIFY` attempt1 STOPPED、TTS_FAILURE)→attempt2 [TTS・Primary 2]→減速後 NG(attempt2 STOPPED)まで正常(Secondary 重複 0)。**3回目 TTS の前で約 10 分停止**し、私が付けた `timeout 590` で process が終了(`runner_execute.json` 未出力)。
- **原因(仮説→反証→確定)**: 仮説「Gemini 3回目呼出の hang」→反証=usage_log に 3回目 TTS の記録なし・最後の記録は 04:06:35 でその後 04:16 まで process 生存・既存コードに sleep あり→確定=`er003_v1_crosslevel_audio_02_common.py:185` が呼ぶ `er020_tts_retry_local_rewrite_01.maybe_cooldown_before_attempt`(`:63-87`)の **10 分 cool-down**(`COOLDOWN_SECONDS=600.0`、`:56`)。Connected Speech 有効 role(`resolve_narrative_role` が `full_story_part{n}_c{k}` を FULL_STORY と認識)の通算最終 attempt の直前にだけ sleep する承認済みの既存仕様(06b `lr_en` で `cooldown_actual_seconds=600.005` を実測済み)。`dlg_cap2` は Dialogue(CS 無効)のため sleep が無かった。**私の `timeout 590` と clip id の選択ミス**であり、Production の異常ではない。
- 費用: `usage_log.jsonl` 合計 約 JPY 0.57(TTS 2・OpenAI ASR 4・Azure 1)。`evidence_07/cost/spend_ledger.jsonl` へ手動転記(`finish()` 未実行のため)。`shared_state_unchanged` の自動検証は未実行(finish 未到達)。
- **未完の理由と次の一手**: 委任文「再起動不可」のため再実行していない。完了させるなら、(1) clip を CS 無効 role[例: narrator の見出し系 `point_one_heading` 相当]へ変える、または (2) cool-down 込み(約 11〜12 分)の `timeout` で再実行(追加 TTS 3・約 JPY 1.5)。**Fable の明示許可が必要**。
- 代替の保証: narrator 外側ループ `generate_a2_segment_with_slowdown` の最終 NG→HR 末端は `finalize_a2_slowdown_final_ng` を Dialogue 外側ループと共有し、06e で Dialogue の実音声(通算 3 回→Lock HR・queue 1 行・`asr_judgement` NG_BOTH)と unit test(`er078_asr_unified_wiring_06e_test_01.py`)で確認済み。narrator 固有の実音声は本委任では未取得。

### 15-2. 後方互換 test(ADDENDUM §2 L99 / OF-AUW-13)
- 新規 `er078_asr_unified_backcompat_07_test_01.py` **53 passed**(通信遮断 plugin 付き、API 0)。旧出力=main 時点の実ファイル `er003_output/n3_01/{hanshin,health,household}/{a2,b1b}/audit/tts_generation_results.json`(6 file・141 entry・attempt 345 行、新キー 0 を test で保証)。新出力=AUW 後の実 evidence 4 file(`asr_judgement` 33 attempt 行)。
- 固定した内容: 試聴リスト導出・読込・書出し・ページ節が旧出力を「導出失敗」でなく 0 件として扱う/`build_attempts_detail`が旧 attempt を `asr_judgement=None` で読み、新キーを除いた場合と旧フィールドが完全一致/Assemble Gate の entry 単位 reader(`_segment_gate_status`・`_segment_missing_mandatory_disfluency_qa`)の出力が新キー有無で不変/集計 script `er078_auw_aggregate_06d.walk` が両方を読む/J11 reader が旧 entry で `(None, None)`/Master Store(tmp 隔離)が旧 manifest entry を従来どおり再利用し、新 manifest の `asr_judgement` は additive に `asr_judgement_inherited` で復元。`evidence_07/tests_backcompat_07.txt`。
- 補足: `verify_episode_audio_validation_gate`全体の比較は tmp に wav/asset が無いため両側とも同じ RuntimeError になる(新キー有無で結果不変の確認としては有効だが弱い)。強い確認は上記 entry 単位 reader の直接比較。

### 15-3. main 取込後の再確認
- `git merge --no-edit origin/main`(競合 0、取込は docs 21 file のみ)後、AUW 中核 12 file `411 passed`(`evidence_07/tests_auw_core_post_merge.txt`)・静的監査 15 passed かつ `unlisted_new_calls`/`vanished`/`count_changed` が空(`static_audit_post_merge.txt`)。flag OFF ロールバック経路(06c `test_g_*`)3 passed(`tests_flag_off_rollback_branch.txt`)。通信遮断 plugin の遮断ログに新規試行: `er078_asr_unified_wiring_06c_test_01.py::test_d_en_last_slot_real_ng_still_goes_to_hr` が api.perplexity.ai を DNS 試行(遮断され費用 0。既存 test の mock 不足=OPEN-378)。

### 15-4. commit 後の確認(07)
- commit: 2316deceb(branch feat/auw-unified-asr-01、cfada30b7..2316deceb push 済み、main 無変更・未merge)
- `secret_scan_01 --staged`: hits=0(33 files、`.wav` は .gitignore で対象外)
- `git worktree list` に予行 worktree なし。`stop_scope_check` 開始 rc=0・有料 run 前 rc=0・終了 rc=0(`stop_check_07.json`・`evidence_07/stop_check_prepaid.json`・`stop_check_07_end.json`)
- `er011_human_review_lock_01.py` の本委任での diff 0 行(`origin/main...HEAD` 全体では `asr_judgement` additive 2 行のみ)。有料 API: 約 JPY 0.57(07 単体)

## 15-5. 委任_07b: narrator A2 外側ループの実音声 再実行(cool-down 込み・timeout 20 分)= **完了**
- 実行: `timeout 1200 er078_auw_runtime_evidence_07.py narr_cap3 --execute --budget-jpy 3`(1回のみ・再起動なし・rc=0)。cool-down(`er020:56 COOLDOWN_SECONDS=600`)は無効化・短縮なし。clip=`full_story_part1_c3`(CS 有効 role のため cool-down 対象=今回は対象のまま完走させた)。開始前 `stop_scope_check` rc=0(`evidence_07/stop_check_prepaid_07b.json`)。前回の途中終了分は `evidence_07/narr_cap3_aborted_first/`(及び `..._stdout.txt`)へ保全。
- 観測(`evidence_07/narr_cap3/runner_execute.json`・`usage_log.jsonl`): TTS 3・OpenAI ASR 6・Azure 1。attempt1→減速後 NG→attempt2→減速後 NG→**cool-down `cooldown_actual_seconds=600.004`**→attempt3→減速後 NG→`finalize_a2_slowdown_final_ng`。entry: `status=STOPPED`・`tts_generations_used=3`・`asr_judgement.state=NG_BOTH`・`slowdown_applied=true`。Lock `full_story_part1_c3`=`HUMAN_REVIEW_REQUIRED`(`cumulative_tts_attempts=3`・`cumulative_asr_calls=3`・`budget_guard_triggered=false`)。HR queue(隔離)=1 行。Secondary(Azure)重複 wav=0(呼出 1)。`runner_execute.json` 出力済み、`shared_state_unchanged=true`、`shared_files_changed_outside_evidence=[]`、`ja_queue_lines_unchanged=true`(`finish()` 到達で自動検証)。
- 注: 期待観測の「減速後 NG」は統一 judge の `NG_BOTH`(Primary・Secondary とも不一致)として記録された。委任_07 の想定と矛盾なし。
- 費用: 本 run 約 JPY 0.72(ledger 0.573→1.2935、委任_07 + 07b 合計 約 1.29、委任 07b 上限 3 内)。
- 結果: 15-1 の「未完」は解消。narrator `generate_a2_segment_with_slowdown` の通算 3 回→HR 末端を実音声で確認。


**注記(2026-10-16 FCJ 委任_02、Dangling Reference Check。既存行は書換えない)**: 本ファイルL370付近の「C runnerから統一ASR判定に到達しない」「JA新規TTS不能(en固定)」は、FAMILY-C-JA-TTS-PRODUCTION-FIX-01で言語経路を修正した後は、C runnerからJA Section(Comment・japanese_title・preview_ja)でも`generate_narration_snippet_verified_strict(...,"ja")`経由の統一判定に到達する設計になった(test/0円検査まで。**有料の実音声evidenceは条件付きSTOP(b)で未取得**。`er079_output/family_c_ja_tts_production_fix_01/EVIDENCE_02.md`)。reuse_from旧音声紐づけも由来照合で是正済み。


## 16. 委任_10 U1是正Regression(2026-10-16 JST。追記のみ)

実装: `er078_asr_unified_judge_01.py`(A7新設・`U2_FORCE_SECONDARY_SCOPE`撤去)・`er007_ja_secondary_asr_01.py`(空転写NO_SPEECH・A7 signal・診断順)。**既定値は条件付きSTOP s1により `U1_KEEP_C1_SIMILARITY_EXCLUSIONS=True`(旧挙動)のまま**(下記§16-3)。harness=`er078_auw_runtime_evidence_10.py`、証跡=`evidence_10/`。

### 16-1. frozen replay 25行(API 0、`evidence_10/frozen_replay_10.txt`)

U1=True(旧)→U1=False(解放)で判定が変わるのは25行中2行のみ: g8_kp4_ja_charon_a1(NG_EXCLUDED[A6]→PASS_WITH_WARNING)、g7_meaning_4_a1(NG_EXCLUDED[A5]→PASS_WITH_WARNING)。verified 13→15、Azure呼出 21→23。誤PASS用C群5行(g12/g3/g4/g5/g6)は解放後もNG(誤受理0)。※frozenに解放クラスの負例は無いため、誤受理の検証は§16-3のlive負例対照で行う。

### 16-2. 保存wav x live Azure 8本(reuse wav + 保存Primary転写 + fresh Azure。`evidence_10/saved_azure/result.json`、実費 JPY 1.3333)

| clip | U1作用 | 保存時 | 新state / reason | Secondary(Azure)転写 / label | NG_EXCLUDED→NG_SECONDARY_UNAVAILABLE |
|---|---|---|---|---|---|
| S1_melos_title_hangul_a3 | A5 | NG_EXCLUDED(similarity_lt_0.4:0.0) | PASS_WITH_WARNING / secondary_confirmed | 走れ。メロス。 / NORMALIZED_MATCH | False |
| S2_melos_title_hangul_c5bk | A5 | NG_EXCLUDED(similarity_lt_0.4:0.0) | PASS_WITH_WARNING / secondary_confirmed | 走れ。メロス。 / NORMALIZED_MATCH | False |
| S3_akb48_title | A6 | NG_EXCLUDED(A6_C1_PROPER_NOUN_DIFF) | NG_BOTH / secondary_not_accepted | Akbフォーティーエイトの新曲スキッシュ。伊藤評価が二作連続センター、近藤ウサギが初選抜。 / TRUE_CONTENT_MISMATCH | False |
| S4_hr_comment1_minfb_a3 | A6 | NG_EXCLUDED(A6_C1_PROPER_NOUN_DIFF entity_like) | NG_BOTH / secondary_not_accepted | 合言葉はブルルクルクロルックブンムプヌクです。 / TRUE_CONTENT_MISMATCH | False |
| S5_hr_comment1_a1 | - | ASR_VALIDATION_UNCERTAIN(Primary NG, P3 Secondary) | NG_BOTH / secondary_not_accepted | 合言葉はプルルクルグロルプ文ムプヌクです。 / TRUE_CONTENT_MISMATCH | False |
| S6_hr_comment1_a2 | - | ASR_VALIDATION_UNCERTAIN(Primary NG, P3 Secondary) | NG_BOTH / secondary_not_accepted | 合言葉はブルルクルクルプンムプヌクです。 / TRUE_CONTENT_MISMATCH | False |
| S7_melos_title_pass_a2 | - | PASS(Primary EXACT) | PASS / primary_pass | None /  | False |
| S8_melos_title_c5bk_a2 | - | PHONETIC_MATCH(Primary PASS) | PASS / primary_pass_approved_equivalence:READING_MATCH | None /  | False |

遷移件数(NG_EXCLUDED→NG_SECONDARY_UNAVAILABLE)= **0**。shared_state差分=空、STOPファイル有無=False。

**Melos japanese_title(Hangul転写、s2切り分け)**: S1/S2はPrimary(OpenAI、language=ja固定)がHangul(`시리에 매우스`/`가시 레메로스`)を返したclip。Azure(ja-JP)は`走れ。メロス。`(NORMALIZED_MATCH)を返し、解放後はPASS_WITH_WARNING(SECONDARY_CONFIRMED=事後試聴リスト入り)。判定: Hangul転写はPrimaryの音声認識の書記体系誤り(音が`はしれ メロス`に近いHangul読み、clip長1.5秒で正常attempt 1.5〜1.6秒と同等)と整合し、「TTSが日本語でない音声」の証拠は得られなかった。ただしASR転写だけで音声言語を証明はできない → **s2は非該当(確定ではなく、事後試聴リストでの人間確認が最終担保)**。言語判定QAは新仕様のため実装していない。

### 16-3. live負例対照(synthetic誤文面TTS + fresh Primary/Azure。`evidence_10/neg_control/result.json`、実費 JPY 0.8942)

T-2確認: (1)差分再生成=N/A(新規synthetic文面のみ) (2)音声キャッシュ=なし (3)`--budget-jpy 12`明示 (4)想定外の全再生成=なし(8 clip x TTS 1回)。TTS=`TTS_EXECUTION_MODE=STANDARD`、Production JA方式(speech_metadata_flash_lite、Aoede)。

| id | 原稿(正) | TTSへ渡した誤文面 | Primary転写(live) | Azure転写 | 判定 state / reason | PASS系 |
|---|---|---|---|---|---|---|
| N1_gas_to_kasu | ガス会社に連絡してください。 | カス会社に連絡してください。 | ガス会社に連絡してください。 | None | PASS / primary_pass | True |
| N2_meta_spelled | Metaが新しい発表をしました。 | エムイーティーエーが新しい発表をしました。 | METAが新しい発表をしました。 | None | PASS / primary_pass | True |
| N3_meta_methane | Metaが新しい発表をしました。 | メタンが新しい発表をしました。 | メタンが新しい発表をしました。 | None | NG_EXCLUDED / p2_exclusion:A7_READING_DICT_MISMATCH | False |
| N4_short_word | 橋を渡ります。 | 箸を渡ります。 | 橋を渡ります。 | None | PASS / primary_pass | True |
| N5_name_one_char | 走れメロス | 走れメロン | 走れ、メロン。 | 走れ。メロン。 | NG_BOTH / secondary_not_accepted | False |
| N6_person_name | 山田太郎さんが来ました。 | 山田次郎さんが来ました。 | 山田次郎さんが来ました。 | 山田二郎さんが来ました。 | NG_BOTH / secondary_not_accepted | False |
| N7_number | 店は午後三時に開きます。 | 店は午後五時に開きます。 | 店は午後5時に開きます。 | None | NG_PROTECTED / p1_value_diff | False |
| N8_negation | これは安全ではありません。 | これは安全です。 | これは安全です。 | None | NG_PROTECTED / p1_protected_diff:negation_marker_diff:'はありません'->'す' | False |

PASS/PASS_WITH_WARNING = **3件**(N1/N2/N4)。**3件とも `primary_pass`(Primary ASRがTTS音声を原稿どおりに認識、Secondary不呼出)で、U1解放の有無と無関係**(`evidence_10/neg_control/attribution_replay_U1_true_vs_false.txt`: U1=True/FalseでN1/N2/N4は同一のPASS)。Secondaryまで到達したN5(メロス→メロン)・N6(太郎→次郎)は解放後もNG_BOTH、N3は辞書登録語としてA7除外、N7/N8はP1(数値・否定)でNG_PROTECTED。**解放経路(Secondary経由)の誤受理は0/2**。ただしdelegation条件付きSTOP s1(「1件でもPASS/PASS_WITHWARNING」)に文言上該当するため、定数を`True`のままcommitし報告(1行でFalse化可能)。N1/N2/N4でTTSが実際に誤読したか(Primaryが誤読を補正して認識したか)は音声を聴いていないため未確認。N2のPrimary転写は`META`(綴り読みをPrimaryがラテン文字化)で、登録読み辞書の不一致信号(A7)はPrimary PASS時には発火しない既存のPrimary層の特性(U1と無関係)。shared_state差分=空、STOPファイル有無=False。

### 16-4. 費用meter
実費(自作ledger見積、`evidence_10/*/cost/spend_ledger.jsonl`): 保存wav x Azure JPY 1.3333 + live負例 JPY 0.8942 = **JPY 2.2275**(見積6・Guardrail12内)。Azure公式usage_log=`evidence_10/*/cost/usage_log.jsonl`。


## 17. 委任_11(2026-10-16 JST。追記のみ): U1発効・A3集計・B-A2-01 narrator(一部)・X-B1-06・fresh JA

出典: `evidence_11/{bnarr,xkp_miss,ja_fresh}/runner_execute.json`・`usage_log.jsonl`(SDK wrapperのtoken実測、単価=`pricing_snapshot`×USD_JPY160)・`evidence_11/cost/spend_ledger.jsonl`。harness=`er078_auw_runtime_evidence_11.py`(06b `begin/finish`再利用、flag/module monkeypatchなし、`tts_backend`は本番既定)。T-2事前記録=`evidence_11/T2_PRECHECK.md`、Guardrail記録=`evidence_11/GUARDRAIL_NOTE.md`。使用モデル: TTS=Family B A2 narrator/Voice=`gemini-2.5-pro-preview-tts`(topic_intro=Charon、見出し=Aoede、Voice A=Algieba、Voice B=Erinome)、X KP英語=`gemini-3.8-flash-lite-tts`(Aoede)、ASR=`gpt-4o-mini-transcribe`、Secondary=Azure、JA Latin語lookup=`gpt-5.6-sol`(Production内蔵resolver)。

### 17-1. U1発効
`U1_KEEP_C1_SIMILARITY_EXCLUSIONS=False`(`er078_asr_unified_judge_01.py:73`)。中核17 file: **486 passed / 2 failed**(2件=koro系、既知OPEN-391)。静的監査15 passed。詳細は`IMPLEMENTATION_11.md`§1。

### 17-2. A3(OPEN-388)
是正は条件付きSTOP s4により**保留**(呼出元ANDが10箇所・7ファイル)。保存データ集計(API 0): `"length_ok": false` 216件/104ファイル、統一judge導入後の記録中は0件、`p2_exclusion:A3_LENGTH_NG`記録0件。設計案は`IMPLEMENTATION_11.md`§3。

### 17-3. B-A2-01 narrator(`bnarr`、`run_tts_a2_2v_new_topic`そのまま。parts=`er012_output/e_family_two_level_wiring_01/meta/a2/parts.json`の隔離複製、新テーマ名`auw11_meta_call_a2`、point_two_headingのみ数値入り`Why Meta paused the feature after 3 weeks`へ差替え)
**結果: 部分取得・途中終了(s6)**。`run_tts_a2_2v_new_topic`内、Voice A/B本文の次の`for`タプル構築で`parts["tension_body"]`が`KeyError`(E-family partsに`tension_body`が無い。API呼出前に検出できる入力不備を私のharnessが事前検査していなかった)。**Hook(`full_story_part1/2`)・Tension・Closing(`in_one_line`)は未生成=A-5の核心部分が未取得**。再起動は禁止事項のため実施せず。

| clip | role | state(attempt) | Primary | Secondary | 備考 |
|---|---|---|---|---|---|
| topic_intro | TOPIC_INTRO(Charon) | PASS(1) | NORMALIZED_MATCH | 不呼出 | `Today's topic is, hello, this is AI, ...` |
| point_one_heading | HEADING_READOUT | PASS(1) | NORMALIZED_MATCH | 不呼出 | 減速後A2_SLOWDOWN_REVERIFY記録あり |
| point_two_heading(数値入り) | HEADING_READOUT | PASS(1) | NORMALIZED_MATCH(`three weeks`) | 不呼出 | 数値`3`→`three`のvalue_guardをfinal gateで通過 |
| point_one(Voice A) | Voice本文 | PASS(1) | NORMALIZED_MATCH | 不呼出 | |
| point_two(Voice B) | Voice本文 | attempt1 NG_BOTH(`secondary_not_accepted`)→attempt2 PASS | TRUE_CONTENT_MISMATCH→NORMALIZED_MATCH | attempt1のみ呼出(Azure 56秒、`had paused`→`had.Caused`で不許容) | 標準の3回枠内の正当な再生成(誤受理なし) |
- attempt_history/HR Lock: `evidence_11/bnarr/attempt_history.jsonl` 9行(theme_id=`auw11_meta_call_a2`、level=`a2`、segment=topic_intro/見出し2/point_one/point_two+各A2_SLOWDOWN_REVERIFY)。共有state(`er011_output/attempt_history.jsonl`等)は`shared_state_unchanged=true`(隔離)。HR到達0。
- Master Store: 共有narration(welcome〜num_five/point_explanation等)はStore再利用(`reuse_telemetry`にreused 12件)。TTS新規生成は6回(topic_intro・見出し2・point_one・point_two×2)。
- Q5(a)〜(f)充足状況: (a)runner側`@with_secondary_run`=充足 (b)前処理=runner内蔵で充足 (c)出力パス`…/<theme>/a2/narration/<name>.wav`=充足(attempt_historyでtheme/levelが導出) (d)monkeypatch/`tts_backend`なし=充足 (e)前後差分=共有state不変・隔離由来=充足 (f)`tts_generation_results.json`・試聴リスト導出=**未充足**(`finalize_tts_results_a2_2v_new_topic`まで到達せず)。
- 費用: **JPY 16.1253**(Gemini TTS 6回計 約12.47[topic_intro 0.60・見出し 0.39/0.39・point_one 1.82・point_two 4.62/4.65]、ASR 10回 約0.96、Azure 2回[4.21秒・56.38秒]計 約2.69)。委任文の単価前提(約1.4〜1.6/clip)は`gemini-2.5-pro-preview-tts`の長尺本文では過小(音声tokenが多い)。所要191秒。

### 17-4. X-B1-06(`xkp_miss`、X B1入口`er019:_generate_or_reuse_kp`+`shared_narration.ensure_key_phrase_english_component`、`tts_backend=speech_metadata_flash_lite`[Xの正式backend])
- phrase=`a quiet refund window`(新規)。**Store miss確認**: `reuse_telemetry`に`event=generated`・`cache_miss_reason=no_existing_master`・`tts_model_id=gemini-3.8-flash-lite-tts`・voice Aoede・`style_instruction_id=key_phrase_english_component`。
- state=**PASS**(`primary_pass`、Primary NORMALIZED_MATCH `A quiet refund window.`、Secondary不呼出、attempts 1)。費用 **JPY 0.0633**。
- → APPLICABILITY_MATRIX X-B1-06を区分3→**区分1(実音声)**へ。あわせて旧記載の食い違い訂正: CSV「R(3回へ揃える)」はOF-AUW-12/DESIGN_02_ADDENDUM §9の旧案で現行ではない。正は`CURRENT_SPEC`「KP英語phrase=4回(MINIMAL2+ENGLISH_LOCK2)」(2026-09-01ユーザー正式決定、`generate_key_phrase_component_verified`の構成)。

### 17-5. fresh JA正例(`ja_fresh`): **未取得(Secondary呼出の実音声確認に至らず)**
- 原稿(変更なし): jf1=`AKB48の新曲『好きish』、伊藤百花が2作連続センター、近藤沙樹が初選抜`(evidence_10 S3と同一)、jf2=`合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。`(06b ja_hrと同一)。Production JA経路(`generate_japanese_title_for_new_topic`→`generate_a2_japanese_with_reading_safety`)。
- 事象: jf1の読み解決(Production内蔵 `er025_entity_pronunciation_resolver_core_01` の `ja_web_lookup_call`、tokens=`["AKB48","ish"]`、model=`gpt-5.6-sol`)が**1回で JPY 21.4688**(入力29,205 tok・出力868 tok、web search)を消費。その直後に私のharnessの累計Guardrail(26.0)がMeter.checkで以降の全API呼出(TTS)を遮断し、jf1・jf2とも`STOPPED`(TTS 0回、ASR 0回、Azure 0回、HR到達はstop扱い=`final_lock_state=HUMAN_REVIEW_REQUIRED`だが**隔離のattempt_historyへのみ**記録)。
- 判断: web lookup費用は想定外(委任文の見積外。T-3の暴走疑い「想定外のWeb Search発火・費用増加」に該当)→再起動せず停止(s6)。**Production resolverのJA Latin語lookup 1回21.5円は費用目標(70円/記事セット)に対して重大**(OPEN-395)。
- fresh正例のやり直しは、(1)ラテン文字を含まない原稿(jf2のようなカタカナのみ)に限定すれば本件lookupは発火しない見込み(jf2はlookupなし=`run_call_count`は1)、(2)実行にはFable/ユーザーの再起動許可が必要。

### 17-6. 費用総括(ledger `evidence_11/cost/spend_ledger.jsonl`)
bnarr 16.1253 + xkp_miss 0.0633 + ja_fresh 21.4688(うち0はTTS) = **JPY 37.6574**(委任文の見積約8、Guardrail16を超過。超過内訳: bnarrのPro TTS単価前提誤り、ja_freshの想定外web lookup)。単価の出典=各runの`usage_log.jsonl`(`basis=token_actual`)。


## 18. 委任_12 B-A2-01 narrator全体(Hook/Tension/Closing含む)+ fresh JA正例(2026-10-16、`er078_auw_runtime_evidence_11.py`、証跡=`evidence_12/`)
**事前dry-run(API 0、`socket.connect`遮断下)**: `evidence_12/bnarr_full/dryrun.json`・`evidence_12/ja_fresh2/dryrun.json`とも `pass:true`。narrator=必須キー欠落0、共有narration 10件がnetwork遮断下で全Store hit(新規TTS不要)、見積nominal 12.97〜18.03・+retry1回24.37(上限30以内)・+retry2回30.71。単価=`evidence_11/bnarr/usage_log.jsonl`(token_actual: point_one 490字=JPY1.82、point_two 544字attempt1=4.62)。fresh JA=Latin文字(A-Za-z0-9)0個、`classify_foreign_tokens_in_japanese_text`の未知Latin token 0=er025 web lookup予測0、worst-case見積2.18(上限4以内)。有料実行は`dryrun.json`の`pass:true`が無いと起動しない実装(`main`)。T-2追記: (1)新規topicで差分再生成の余地なし(9 segment全て新規) (2)共有narrationはStore hit確認済み (3)`--budget-jpy`30/4明示・meter hard stop (4)想定外の全再生成なし。

### 18-1. narrator全体(`bnarr_full`、`run_tts_a2_2v_new_topic`そのまま・monkeypatchなし・parts=`er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/parts.json`の隔離複製[無改変]、theme=`auw12_personalized_news_a2`、Voice A=Algieba/Voice B=Erinome[`voice_resolution.json`])
**結果: 9 clip全てPASS・正常終了(rc=0、所要285秒)**。`finalize_tts_results_a2_2v_new_topic`も成功。

| clip | role | state(試行) | Primary | Secondary | model/voice | 費用JPY(TTS) | 備考 |
|---|---|---|---|---|---|---|---|
| topic_intro | TOPIC_INTRO | PASS(1) | NORMALIZED_MATCH | 不呼出 | gemini-2.5-pro-preview-tts/Charon | 0.50 | |
| point_one_heading | 見出し | PASS(1) | NORMALIZED_MATCH | 不呼出 | 同/Aoede・減速あり | 0.46 | |
| point_two_heading | 見出し | PASS(1) | NORMALIZED_MATCH | 不呼出 | 同/Aoede・減速あり | 0.45 | |
| point_one | Voice A | attempt1 NG_BOTH(`secondary_not_accepted`)→attempt2 PASS | TRUE_CONTENT_MISMATCH(`first`欠落)→NORMALIZED_MATCH | attempt1のみ呼出(Azure 36.5秒、`opened`等で不許容) | 同/Algieba・減速あり | 3.02+2.98 | 標準3回枠内の正当な再生成(誤受理なし) |
| point_two | Voice B | PASS(1) | NUMERIC_EQUIVALENCE_MATCH(`primary_pass_approved_equivalence:TIER1_NUMERIC_EQUIVALENCE`) | 不呼出 | 同/Erinome・減速あり | 3.81 | |
| **full_story_part1(Hook)** | FULL_STORY | **PASS(1)** | NORMALIZED_MATCH | 不呼出 | 同/Aoede・減速あり・CS層+Repetition QA適用 | 0.98 | |
| **full_story_part2(Hook続き)** | FULL_STORY | **PASS(1)** | NUMERIC_EQUIVALENCE_MATCH(`TIER1_DIFF_ANCHORED`) | 不呼出 | 同/Aoede・減速あり | 1.15 | |
| **tension_reflection(Tension)** | 解説 | **PASS(1)** | NORMALIZED_MATCH | 不呼出 | 同/Aoede・減速あり | 2.56 | segment名は本番定数`EXTRA_SEGMENT_NAME`=`tension_reflection` |
| **in_one_line(Closing)** | 解説 | **PASS(1)** | EXACT_MATCH | 不呼出 | 同/Aoede・減速あり・disfluency_qa適用 | 1.66 | |
- 全clipに`asr_judgement`(統一judge)が記録され、HR到達0、`attempt_history.jsonl`は隔離(`evidence_12/bnarr_full/attempt_history.jsonl`、共有`er011_output/attempt_history.jsonl`は不変=`shared_state_unchanged=true`、`shared_files_changed_outside_evidence=[]`)。Master Store manifestのsha前後一致(新規segmentはStore対象外)。
- **Q5(a)〜(f)全充足**: (a)runner側`@with_secondary_run` (b)前処理=runner内蔵 (c)出力パス`…/auw12_personalized_news_a2/a2/narration/<name>.wav` (d)monkeypatch/`tts_backend`渡しなし (e)前後差分=共有state不変 (f)**`audit/tts_generation_results.json`(9 segment)と事後試聴リスト(`audit/pass_with_warning_listening_list.html`/`.json`、count=0=PASS_WITH_WARNING該当なし)が導出された**(委任_11で未充足だった項目を充足)。`required_segments_completeness.json`は`complete:false`(9/15。不足は`japanese_title`/`preview`/`comment_1-4`=JA Section。本runのscope外でFamily B JA経路は別行で実音声済み)。
- 費用: **JPY 20.8216**(Gemini TTS 10回、OpenAI ASR 18回、Azure 1回36.54秒)。見積nominal_high 18.03+retry1回24.37の範囲内。
- Hook/Tension/Closingはいずれも1回目でPrimary PASS(Secondary不呼出)=統一judge下のPrimary経路の実音声証拠。Secondary経路の実音声証拠はpoint_one attempt1(NG_BOTH)・fresh JA(下記)。

### 18-2. fresh JA(`ja_fresh2`、Latin文字を含まない既存原稿のみ、Production JA経路`generate_a2_japanese_with_reading_safety`)
- 原稿(変更なし): jf2=`合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。`(06b ja_hrと同一)、jf3=`熟すと出るガス`(Phase 0 fixture g8と同一)。U1定数 `U1_KEEP_C1_SIMILARITY_EXCLUSIONS=False`(U1発効)。
- **web lookup発火0**(usage_logに`web_search`/高額text呼出なし。text LLM 1回は`gpt-6-luna` in257/out19=JPY0.0056=Luna判定の小呼出でlookupではない)。
- **jf3(熟すと出るガス): PASS_WITH_WARNING(`secondary_confirmed`)**。Primary=TRUE_CONTENT_MISMATCH(`じくすと出るガス。`)→Secondary(Azure)呼出=`熟すと出るガス。`でaccepted→`SECONDARY_CONFIRMED`警告。Phase 0のg8救済例(旧C1 entity_like除外で対象外だった型)が**fresh TTSで実際に発生し、U1発効後にSecondary呼出・採用された実音声証拠**。n_attempts=1。
- **jf2(合言葉…): STOPPED(HR到達)**。3回のTTS全てでPrimary不一致(`ブンムプ`等)かつAzureも不一致(`ブルルクルグロルプ文むっぷ吹抜く`/`…グローブ。文府。腑貫`/`…ブンムプヌク`[`フ`脱落])→NG_BOTH×3→人手確認キュー(隔離`evidence_12/ja_fresh2/human_review_queue_ja.jsonl`)。**誤受理なし(Secondaryが保護)**。正例ではなく負例側の実音声証拠。
- 結論: 「Secondary実呼出」の正例は1 clip(jf3)取得。計画の「正例2 clip」は1正例+1保護(NG)。再実行は禁止事項(再起動不可)のためFableへ報告。費用 **JPY 3.3991**(TTS 4回gemini-3.1-flash-tts-preview、ASR 4、Azure 4回24.09秒、text 1)。
- shared_state_unchanged=true、`shared_files_changed_outside_evidence=[]`。

### 18-3. 費用総括(`evidence_12/cost/spend_ledger.jsonl`、basis=token_actual)
narrator 20.8216 + fresh JA 3.3991 = **JPY 24.2207**(Guardrail 34以内、暴走・STOPなし、`stop_check`rc=0)。委任_11のbnarr 16.13(5 segment)に対し、本runは9 segment+retry1回で20.82(単価実測を見積に使った効果で見積範囲内)。使用モデル: 評価用ではなくProduction正式path(TTS: gemini-2.5-pro-preview-tts[narrator/Voice A/B]・gemini-3.1-flash-tts-preview[JA]、ASR: gpt-4o-mini-transcribe、Secondary: Azure)をそのまま実行(最新モデル原則25節は本番ライン選定外)。
