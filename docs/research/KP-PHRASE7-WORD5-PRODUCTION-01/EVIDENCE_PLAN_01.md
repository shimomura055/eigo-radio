# EVIDENCE_PLAN_01: 6経路(X/Y/Z x Std/Adv)のruntime evidence取得計画(委任_03用。本委任では実行しない)
KP-PHRASE7-WORD5-PRODUCTION-01 委任_01 / 2026-10-27 / 計画のみ(API 0・JPY0)。方式は`docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/EVIDENCE_01.md`・`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/EVIDENCE_PLAN_01.md`と同型(**KP stage限定・新規run dir・TTS/本文生成なし**)。特定Familyの証拠で全FamilyのPRODUCTION_WIREDを宣言しない(原文§6)。

## 1. 観測項目(原文§6-1〜9との対応)
| # | 事実 | 方法 |
|---|---|---|
| O1 | 6経路で正式初回経路が**P7(call1)+W5'(call2)**で動く(§6-1) | 各docの`prompt_sha256={call1:2e930193…, call2:187f1b87…(確定sha)}`、messageの先頭一致、`kp_candidates.json`/`work/keywords_selector_prompt.txt` |
| O2 | Key Word 5条件・補足・出力規則が効いている(§6-2) | W5'返答(raw)を本文照合: 全語が本文一致・1語、理由が1文40字以内、語数併記、**KP含有語が候補に残らない**。**易語の有無は評価しない**(記録のみ) |
| O3 | 本文一致・1語・包含重複除外(§6-3) | doc`dropped[]`のstage別件数(`validate/not_single_word/duplicate_of_top3/cmu`)、Gate後候補が全て本文一致 |
| O4 | 上限未満でも不要な補完をしない(§6-4) | E=0のlevelで`backfill.triggered=false`・usage logの補完call行0。初回が7/5未満(例: フレーズ4件)かつE=0の事例を1つ以上(Trial-02 UK Std型: P7=4件) |
| O5 | Gate除外時のみ種類別に補完・既存保持(§6-5) | **自然発動した場合のみfresh観測**。発動しなければ**「未観測」と報告**し、replayで代替(§3)。replayは「凍結入力+実LLM補完」と明記しfreshと混ぜない |
| O6 | KP救済・QA・HR・フォーム連携(§6-6) | 救済自然発火は`flags.rescued`が出たlevelのみ(未観測なら未観測)。HR依頼書12行の生成、AUTO宣言`declare-absent`で`kp_selection_final`、フォームexportへの12件投入(read-only) |
| O7 | resume/retryで二重生成・書換えなし(§6-7) | 同一引数再起動で`candidates_sha256`不変・usage行数不変(API 0)。reselectは実行しない(費用・HR状態を壊す) |
| O8 | actual model_id・routing・Prompt hash・入出力・Gate結果・補完/救済記録(§6-9) | usage log(`gpt-6-luna`、process=A2_SUPPORT/B1_SUPPORT)、`outer_retry_log.json`、`keywords_runtime_metadata.json`、doc`backfill/rescue_provenance/shortfall_detail` |
| O9 | Z固有: SRC D1・人称整合の単語候補への適用 | Zの全候補`gates.src_d1=PASS`(単語はambiguous/unresolvedで落ちる率を記録=Z実効単語数) |

## 2. fresh run(新規run dir・KP stageのみ・6 level-run)
HR候補を保全するため**既存run dirは使わず新run dirへ入力複製**(`..._run_kp75_ev_01`)。各起動前に`py tools/stop_scope_check_01.py --managed-id KP-PHRASE7-WORD5-PRODUCTION-01 --run-dir <run> --out <json>`(rc=0確認、rc=3は新規API呼出なし)。起動間隔150秒以上(RESTART_STORM回避)。**Z・Y・Xは互いに独立なので並列起動**(別run dir・別Family。起動間隔のみ守る)。
| Family | 記事(入力) | コマンド(前回evidenceと同型、`--help`で最終確認) |
|---|---|---|
| X | `uk_train_speaker_playback`(Trial-02でP7=4件・基本寄り単語多。上限未満事例)の`run_nws_02`article.md複製。補助でAI島の`run_ai_01`複製(自然発動の機会を増やす) | `.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug uk_train_speaker_playback --run run_kp75_ev_01 --level both --stage scaffold --scaffold-only kp --budget-jpy 40` |
| Y | `redelivery_fee`(`run_01`複製。translate/・text/) | `.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_kp75_ev_01 --stages kp --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 40 --tts-execution-mode STANDARD` |
| Z | `melos`(`run_fzcw_e1_01`のwriter/r2.md・std.md複製)。**猿の手はOPEN-548(seed provenance不一致のfail-closed)で新規KP生成不可**のためmelosを採用 | `.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story melos --slug melos --run run_kp75_ev_01 --stage kp --mode real --approved-budget-jpy 40 --tts-execution-mode STANDARD` |
- Std=A2(a2)・Adv=B1(b1b)。KP段はStd/Advで同一関数をレベル別に1回ずつ実行(`--level both`/`--stages kp`が両レベルを回す)。rc=4はHR待機(正常)。
- 再起動確認(O7)は各Family 1回(同一コマンド再実行、API 0)。RESTART_STORM回避(同一run dir 5分内3回起動なし)。
- 注意(Z再起動時の段指定): 完成段の再実行は1起動で`--stages provision_shell,gate,assemble,pages,page_verify`を指定(OPEN-480)。KP stage単独は`--stage kp`でこの対象外。

## 3. replay(Gate除外→補完を確実に観測。O5の代替・補強)
- 方式: 凍結本文+凍結した**初回P7/W5'返答**(Trial-02 `runs/*/trial_result.json state.p7_raw / w3_raw`を流用。Gateで`duplicate_of_top3`になった含有語[Trial-02: 3件]を含む)を`select_fn/vocab_call_fn`に注入し、正式`generate_candidates`で実行。**補完のP7/W5' call・補完分canonicalization・gloss・QA・RQAは実LLM**。KPI provenance=「replay=凍結入力+実LLM補完」(freshと混ぜない)。
- 想定case(各1回、6 level-runのreplay、補完call 1〜2/回): Trial-02の6 run(AI島Std/Adv、UK Std/Adv、猿の手Std/Adv)。含有語の`duplicate_of_top3`→E_word≥1→単語補完、validate/数字除外→E_phrase≥1→フレーズ補完を実測(猿の手Std/Advは**入力本文を凍結で使うのみ**でseed不要)。
- 重複混入変形(API 0): 補完返答を採取後、同じ返答に現存候補と同一句を足して`vocab_call_fn`へ再注入し「重複は捨てる(R-3)」「補完単語がフレーズに含まれる場合は落とす」を確認。

## 4. 費用見積(¥/経路、合計≤¥60、1,000円/日内)
根拠: Trial-02 1 level平均¥1.76(W5+canon+gloss+RQA)+P7 ¥0.12=約¥1.9(`COMPARISON_02.md`)。補完発動時は+約¥0.5〜1.0/回(P7またはW5' 1 call+canonicalization増)。
| 項目 | 回数 | 小計 |
|---|---|---|
| fresh 6 level-run(X/Y/Z x Std/Adv) | 6 x ¥1.9 | ¥11.4 |
| 追加fresh(自然発動の機会: AI島X Std/Adv。猿の手は不可のため追加Zは別作品の本文複製が必要なら追加検討) | 2 x ¥1.9 | ¥3.8 |
| replay(補完実LLM) | 6 x ¥1.0 | ¥6.0 |
| 再起動確認 | 0(API 0) | ¥0 |
| 予備(P7 attempt再選定・外側retry・やり直し) | - | ¥10 |
| **合計** | | **約¥31(上限¥60、案件見積≤300円)** |
経路別: X Std/Adv 各¥1.9(+補助 各¥1.9)、Y Std/Adv 各¥1.9、Z Std/Adv 各¥1.9(いずれも補完発動時+≤¥1)。承認枠(7-7: 案件見積300円以下・承認済みScope内)に収まる。有料run再起動は委任文が許した回数のみ。モデル=gpt-6-luna(Production SUPPORT_MODEL契約。routing/actual model_idを記録)。

## 5. 自然発火が必要な項目の扱い
救済(O6)・補完(O5)・Y/Z Advの補完(OPEN-549)・X/Z救済(OPEN-544)・call1最終attempt除外・AUTOでn_auto<3の挙動は、**自然に発動しなければ未観測と報告**し、replay/mock testで代替した旨を区別して書く。freshの未観測を理由に実装を変えない・runを増やさない(費用・追加Trial目的化の禁止)。

## 6. 取得物の保存先
`docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/`配下(`EVIDENCE_01.md`, `evidence_01.json`, `evidence_runs/`, `replay_results/`, `stop_check_*.json`)。既存の`er0XX_output`構造にはrun dirのみ(X=`er019_output/family_x_audio_production_wiring_01/…__run_kp75_ev_01`、Y=`er121_output/…`、Z=`er026_output/…`)。新しい証跡置き場は作らない。

## 7. 判定の分け方
Family別・レベル別に`EVIDENCE_COLLECTED`を記録し、**PRODUCTION_WIRED判定はFable**。X/Y/Zのうち一つでもfresh未実施・経路不到達なら、そのFamilyはPRODUCTION_WIREDとしない。
