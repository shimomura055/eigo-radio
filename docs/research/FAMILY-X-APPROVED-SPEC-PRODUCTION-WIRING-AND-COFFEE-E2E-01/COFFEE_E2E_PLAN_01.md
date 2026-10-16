# COFFEE_E2E_PLAN_01(FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_01、2026-10-16、計画のみ・JPY0・Coffee生成なし)

**位置づけ**: ユーザー指示§5の12工程を、実装完了(WIRING_DESIGN_01のOpus条件Aレビュー→Phase 2実装)後に実走するための計画書。**本委任では何も実行していない**。有料E2E開始前に本書の費用見積をFableが提示し、承認済み予算・既存Gateを守る(ユーザー指示§8)。**Researchから音声までを無条件に一気通貫で実行しない**(§5)ため、stageごとにSPEC_WIRING_MATRIX_01の該当行と照合するチェックポイント(CP)を置く。
**TTS**: 全音声stageで`TTS_EXECUTION_MODE=STANDARD`を明示(T-2、`PM_GOVERNANCE.md` 7-1/7-2。Batch例外理由なし)。単価はSTANDARD($0.5/$6.0 per Mtok、`er005_output/cost_baseline_01/pricing_snapshot.json`、USD_JPY=160)。
**Python**: `.venv/Scripts/python.exe`(存在確認済み)。

---

## 1. 旧Coffee成果を新記事の正本として流用しない担保

| 担保 | 内容 | 根拠 |
|---|---|---|
| 新run名 | text: `er019_output/coffee_prices/run_fxpw_01`、audio: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01`(AR既定derive)。既存の`run_l3_01`/`run_l3_01_stdregen`/`run_p8_wiring_01`/`run_v5_ms_01`/`run_m2p0_n01_01`と衝突しない。実行前に**dirが存在しないこと**を確認 | `ER:98-103`は既存`verified_fact_ledger.txt`を黙って再利用する【N2】ため、新dirが必須 |
| `reuse_from`禁止 | Family Xの両runner/`EFAM`に`reuse_from`機構は存在しない(Grep 0件)。`--out-dir`への旧Coffee dirの指定・コピー・seed(`er071_coffee_assemble_seed_03.py`型のv5再利用)を**行わない** | 本計画 |
| Theme | 旧Coffeeの`--theme`文字列(`run_l3_01/entry_point.json`のargs.theme、コーヒー価格上昇の原因と店頭価格への影響)を**テーマとしてのみ**維持。Research結果・Ledger・B3・原稿・KP・音声は一切引継がない | ユーザー指示§5・§1 |
| Master Audio Store | KP英語はK2用の新`style_instruction_id`(`key_phrase_english_component_k2`)+versionにK2 sha12(WIRING_DESIGN §B-2)=**旧MINIMAL style音声は構造的にヒットしない**。ただし**固定shell音声(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five、`SN:63-70`)はStoreから再利用される**(記事内容を含まない共通固定音声・Styleは今回の6仕様の対象外)ため、これを「旧Coffee流用」と誤読しないよう、最終報告の流用/新規一覧に明記する | `SN:63-70,231,241,266` |
| 流用検査(実走後) | (1)`research_ledger/runtime_evidence.json` `reused:false`・response_id≠旧、(2)`ledger`/`selected_brief`/`ja_writer/revision2.md`のsha256が旧Coffee 5run(上記)のいずれとも不一致、(3)`tts_generation_results.json`の全segmentが`reused_from_previous_run`を持たない(shellを除く)、(4)`reuse_telemetry.jsonl`でKP英語の`reused:true`が無い(または同一run内のStd/Adv共用のみ) | 本計画 |

## 2. 工程(ユーザー§5の12工程)・コマンド・STOP/HR Gate・照合項目

共通: 各コマンドの前に`py -3 tools/stop_scope_check_01.py --managed-id FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 --run-dir <run> --out <json>`(rc=3でSTOP)。Python実行は`.venv/Scripts/python.exe`。`THEME`は旧Coffeeのtheme文字列(Fableが最終確認)。

| # | 工程(ユーザー§5) | コマンド | STOP / Human Review Gate | マトリクス照合(必須PASS) | 費用(期待/最悪 JPY) |
|---|---|---|---|---|---|
| S0 | 実走前(JPY0) | `git status/log`、実装commitとOpus条件Aレビュー済みの確認、WIRING_DESIGN §Fのunit/regression/integration全PASS、`--stage plan`(dryrun)で`audit/style_profile.json`に`fx_20261016`が記録されること、出力dirの非存在確認、費用承認の記録 | 実装未了・test失敗・Opus未了・費用未承認=開始しない | X19(既定解決)、X20〜X26(定数sha突合test PASS) | 0 |
| S1 | 1. Research新規 + 2. Verified Fact Ledger新規 | `.venv/Scripts/python.exe er019_family_x_entertainment_production_runner_01.py --theme "<THEME>" --slug coffee_prices --out-dir er019_output/coffee_prices/run_fxpw_01 --run-label FXPW-COFFEE-E2E-01 --budget-jpy 120 --stage research` | `assert_budget_ok`(120)。web_search費用はOPEN-242修正で計上。budget超過=STOP | X01,X02: `research_ledger/runtime_evidence.json`の`reused:false`・model_id・response_id・web_search_call_count、`verdict_counts.json`、旧Ledgerとsha不一致 | 46.8 / 60 |
| S2 | 3. B3(Sol) | `... --stage storyline_b3`(同out-dir、Research/Ledgerは今回dirの既存を再利用=正当な再利用) | 返却model不一致STOP(`ER:153-157`)。注記契約(V1〜V10)違反は課金前STOP | X04,X05: `storyline_b3/runtime_evidence.json`の`model_id_actual`が`gpt-6.1-sol`、`prompt_shas`のB3定数shaが現行`b3.prompt_shas()`と一致、`annotation_manifest.json producer=deterministic_v2` | 7.0 / 9 |
| **CP-A** | S1〜S2後 | Sonnetが照合表を作りFableへ報告 | Ledger/選定Factの目視(事実性の異常、web_search異常、旧Coffeeとの同一性) | 上記+費用実績 | — |
| S3 | 4. W-1 Writer R0→R1→R2(すべてSol) | `... --stage writer --budget-jpy 120` | 記号Validator STOP(`JASymbolCheckStopError`、技術QA)。U-1来歴Gate | X06,X07,X08,X33(下記§3の表を全て埋める) | 11.5 / 20 |
| **CP-B** | S3後 | 照合表+JA記事(`ja_writer/revision2.md`)の確認 | Writer証拠が1つでも欠落/Sol以外のmodel=STOP | §3 | — |
| S4 | 5. Advanced英語化(+IOL新規2〜3文)+RF b1b | `... --stage advanced --budget-jpy 120` | 段落3分割retry後のSTOP。RFは非Blocking(Review Queue保存) | X09,X11: `writer_run_summary.json advanced`のmodel_id_actual、`in_one_line.sentence_count∈{2,3}`・`spec_ok:true`・prompt_sha256、`b1b/article.md`のIOLが2〜3文 | 1.5 / 3 |
| S5 | 6. Standard難易度調整+RF a2 | `... --stage standard --budget-jpy 120` | 同上。**ここで構造的にMandatory STOP**(ERには音声stageが無い、`ER:24-27,468`) | X10,X11,X03: Std IOLが2〜3文、`derived_from_advanced_sha256`=現行Adv sha、両levelでReview Queue保存・件数報告 | 1.6 / 3 |
| **CP-C** | S5後(=ERのMandatory STOP) | 照合表+Review Queue(`review_queue/post_en/`)の未解決flagged一覧 | **Mandatory STOP**。flaggedがあればHuman Reviewの判断をFable経由で確認してから音声へ | X03,X09〜X11 | — |
| S6 | 音声plan(JPY0) | `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_fxpw_01 --level both --stage plan --tts-backend speech_metadata_flash_lite` | M5(backend)、M2(既存run state無し)。`audit/style_profile.json`作成 | X19,X20〜X26: `profile_id=fx_20261016`、`roles`6件のsha、`style_profile_plan.full_story_style_sha256`=PD06 | 0 |
| S7 | 7. M2P0+A方式でKP新規抽出・選定 + 8. KP日本語意味(gloss)・Adv英語解説text + Preview/Comment text | `TTS_EXECUTION_MODE=STANDARD ... --stage scaffold --level both --tts-backend speech_metadata_flash_lite --budget-jpy 100` | gloss HR待ち(`EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT`、rc=2)=**STOP**。M2→Strategy L fallback発火=**必須ユーザー報告**。`CANONICALIZATION_INVALID`再発=STOP(同じ原因が既存retryで解決しない場合) | X12〜X16: `kp_supply=m2`、KP5件が両level完走、`m2_fallback`=null、A方式(P0 sha固定test PASS)、explanation 15語1文 | 3.8 / 12 |
| **CP-D** | S7後 | 照合表+KP一覧(used_form/日本語gloss/explanation)+Comment/Preview text | KP品質(断片KP、gloss不整合)の目視。OPEN-343再発=STOP | X12〜X16、OPEN-343 triage結果 | — |
| S8 | 9. IOL(text=S4/S5で生成済み)+10. 正式StyleでTTS(Adv) | `TTS_EXECUTION_MODE=STANDARD ... --stage tts --level b1b --tts-backend speech_metadata_flash_lite --budget-jpy 100` | `assert_production_tts_backend`、`ensure_rf_record`(三者sha)、review_lock(3回NG→Human Review)、共有narration Gate、`STOPPED` segment | X20,X22,X24,X25: Full Story=PD06(M4 pass)、KP英語=K2(Store key version=`+k2.<sha12>`、`fallback_used`一覧)、KP解説=P7、Preview=E1。`minimal_fallback`/`local_rewrite_recovery`なし | 12.3 / 28 |
| S9 | 10. 正式StyleでTTS(Std) | `... --stage tts --level a2 ...` | 同上+Std fallback(`STD_FALLBACK_USED_OR_UNKNOWN`) | X20,X21,X23,X26: Full Story=PD06+`slowdown_info`(ratio≒1.06)+減速後ASR PASS、KP日本語意味=P8_KP、Preview/Comment=R2、Std IOLの音声 | 11.7 / 27 |
| **CP-E** | S9後 | 照合表(Style適用の全segment一覧)+`pass_with_warning_listening_list.json`+`style_profile_gate.json`予告(assemble前にM3を仮実行できる範囲で) | HR queue未処理・`PASS_WITH_WARNING`の聞き取り対象列挙 | X20〜X30 | — |
| S10 | 11. Standard/Advanced Assembly | `... --stage assemble --level both --tts-backend speech_metadata_flash_lite` | Audio Validation Gate、M3 Style Gate(`BLOCKED_STYLE_PROFILE_GATE`)、gloss HR関所。BLOCK=迂回せず人間承認(`record_human_approval`)かsegment再生成 | X30: `style_profile_gate.json status=PASS`(または人間承認記録)、両level `assemble`完了 | 0 |
| S11 | 12. 試聴ページ生成・実再生確認 | `... --stage player` → `user_test/`配下へ配置してcommit/push(GitHub Pagesが標準配布経路、`PM_GOVERNANCE.md` L336-345) | Gate 7 (a)〜(l)+(m)(到達可能URL確認)。`file:///`・raw系URL禁止 | X31,X17: playerが開く(HTTP 200)、両levelの全segment音声が取得可、表題=R2 title | 0 |
| **CP-F** | S11後 | 最終照合(§4)・ユーザー試聴依頼 | ユーザー試聴待ち(主観評価はユーザー) | 受入条件1〜12(ユーザー§9) | — |

**CP運用の提案**: CP-A〜CP-Fごとに照合表(PASS/FAIL・証拠path)を作り、**全PASSかつSTOP条件なしなら次stageへ進む**。1件でもFAILなら停止してFableへ報告する(自動再試行・迂回をしない、同一原因2回でSTOP)。委任単位は(a)S0〜CP-C(text)、(b)S6〜CP-E(audio生成)、(c)S10〜CP-F(assemble・page・SSOT)の3分割を推奨(Fableの照合を各境界で挟む)。

## 3. Writer証拠(ユーザー§6)の取得方法

| ユーザー§6の項目 | 取得元(path/キー) | 既存機能で可能か |
|---|---|---|
| B3 actual model_id | `er019_output/coffee_prices/run_fxpw_01/storyline_b3/runtime_evidence.json` `model_id_actual` | **可**(`meta/run_sol61_01`で`gpt-6.1-sol`を実測済み) |
| R0 / R1 / R2 actual model_id | `ja_writer/runtime_evidence.json` `original.model`・`r1.model`・`r2.model`、`model_mismatch`、`requested_model` | **可**(同上) |
| W-1正式経路の使用 | 同`chain_method=="W-1"`、`chain_method_detail=="factlock_r0__r1_r2_independent_sol61"`、`annotated_md_sha256`が`storyline_b3/selected_brief_annotated.md`のshaと一致、`entry_point.json`の`ja_writer_module_sha256` | **可** |
| R1→R2入力契約 | `r1/r2.previous_response_id_used==false`、R2のuser messageがR1 raw(`revision1.md`原文)から`USER_TMPL`で組まれたshaと一致(`r2.user_message_sha256`をオフライン再計算[API 0]) | 保存値は**可**。再計算照合は既存関数(`w1.sha_text`+`USER_TMPL`)を使う小スクリプト(JPY0、追加仕様なし) |
| Fact Lock・B3注記・AN3 | `verbatim_shas`14キー(R0_PROMPT/FACTLOCK_R0_BLOCK_HEAD/TAIL/MUSTFIX_PRIORITY/R0_BLOCK/AN3/SYMBOL_PREVENTION等)を現行`w1.verbatim_shas()`と照合、`annotation_manifest.json`・`annotation_rules_sha256`・`writer_constraints_sha256` | **可** |
| 実送信Prompt SHA(JA Writer) | R0: `r0_calls[].prompt_sha256`(`W1:353`)、R1/R2: `user_message_sha256`(`W1:394`)。B3: `prompt_shas`(**定数のsha、実送信文のshaではない**) | **ほぼ可**(B3は定数shaのみ=実送信文の直接保存は無い。B3はAI Storyline決定1 callで入力=Ledger+topic。追加が必要なら任意) |
| 実送信Prompt SHA(英語化・IOL・Std) | 現状**記録なし**【N1】 | **追加実装が必要**(WIRING_DESIGN §C-5/§H: `EFAM`のevidenceへ`prompt_sha256`/`model_id_actual`/`response_id`/`sentence_count`を追記。API増なし) |
| retry/regeneration時のrouting | 実run: R0記号再生成が発火すれば`r0_calls[].stage=="w1_r0_symbol_regen"`のmodel、R2再実行の`r2_all_attempts`。**発火しない場合は実run証拠が取れない** → Phase 2のmock testでretry経路が同じrouting key・`require_model`を通ることを固定(`call_astra`/`call_luna_r0`) | 実run証拠は条件付き。mock testで補完 |
| 旧Luna/Astra経路への退行なし | `raw_usage_log.jsonl`の`stage`別`model_id`集計(`storyline_b3`/`w1_r0`/`w1_astra_r1`/`w1_astra_r2`がすべて`gpt-6.1-sol`、`luna`/`astra`を含まない)をオフライン集計(JPY0)、`ja_writer_o_r1_r2`の非呼出(AST test) | **可**(集計script 1本、追加仕様なし) |
| Fact QA・品質Gate | RF b1b/a2(非Blocking)の`status`/`issue_count`、Review Queue、記号QA `symbol_qa` | **可** |

## 4. 最終照合(CP-F、ユーザー§9の受入条件との対応)

1. 正式初回経路で全承認仕様=マトリクス全33行の⑩列をPASS。2. retry/fallback/regen/resume=WIRING_DESIGN §Dのtest PASS+実run中に発火した分のevidence。3. DEV/Trial専用のみの仕様なし=Grep(`PD6`/`K2`/`P8`/`p7`等がTrial scriptにのみ存在しない)。4. 正式経路runtime evidence=上記。5. model_id・routing・Prompt SHA=§3。6. Validator/Regression/integration=§F全PASS。7. ResearchからAssembly=S1〜S10。8. Std/Adv完成・試聴可能=S11。9. 承認済み仕様と完成記事・音声の全件照合=matrix⑩のPASS表。10. SSOT更新・11. commit/push/merge=別途。12. 未報告Trial・未登録Open Item・未処理Blocking=0を確認。**1件でも未達ならPRODUCTION_WIRED判定をしない**(Fable判定)。

## 5. 費用見積(ステージ別・STANDARD単価・出典付き)

| stage | 期待 JPY | 最悪 JPY | 出典・算出 |
|---|---|---|---|
| S1 Research + Ledger | 46.8 | 60 | `er019_output/coffee_prices/run_l3_01/cost.json` research 21.96 + ledger 24.88(同テーマ・同経路の実績)。最悪=web_search回数増(+30%) |
| S2 B3(Sol) | 7.0 | 9 | `er019_output/meta/run_sol61_01/cost.json` storyline_b3 6.956(Sol実績) |
| S3 W-1 R0/R1/R2(Sol) | 11.5 | 20 | 同cost.json w1_r0 6.598 + w1_astra_r1 2.668 + w1_astra_r2 2.277 = 11.543。最悪=R0記号再生成(+6.6)+R2再実行(+2.3) |
| S4 Advanced+IOL+RF b1b | 1.5 | 3 | `run_l3_01/cost.json` advanced 0.349 + RF b1b(0.254+0.231+0.335+0.341=1.161)。IOL単価は承認Trial実績JPY0.12(Adv)(`IN_ONE_LINE_REWRITE_01.md`)で+微増 |
| S5 Standard+RF a2 | 1.6 | 3 | 同 standard 0.381 + RF a2(0.227+0.27+0.381+0.381=1.259) |
| **text小計** | **68.4** | **95** | |
| S7 scaffold(KP M2P0 LLM+gloss+explanation text+Preview/Comment text) | 3.8 | 12 | `er071_output/m2p0_n01_production_wiring_01/COST_ESTIMATE_01.md` §2-1(KP LLM期待1.8/最悪約6、`KP_ARTICLE_COST_CAP_JPY=15`)+support text約1〜3(推定) |
| S8 TTS Adv | 12.3 | 28 | 同COST_ESTIMATE_01 §2-3: Adv Full Story 5.2×retry係数1.3=6.8、他Advsegment(topic_intro/preview/comment_1-4/in_one_line 7clip)約2.5、KP英語K2 5clip約1.5、KP解説5clip約1.5(V5実績「約1.5」)、Azure期待0〜3 |
| S9 TTS Std | 11.7 | 27 | Std Full Story 5.4×1.3=7.0、他Std segment(topic_intro/preview/comment_1-4/in_one_line/japanese_title 8clip)約3.0、KP日本語意味P8 5clip約1.2(KP英語はStoreでAdvと共用=0)、Azure期待0〜3 |
| S10 Assembly / S11 Player・publish | 0 | 0 | ローカル処理 |
| **audio小計** | **27.8** | **67** | |
| **合計(E2E)** | **約96** | **約162** | 未確認単価(KP短clip、Azure)は`raw_usage_log.jsonl`の実測で置換(COST_ESTIMATE_01と同方針) |
| 偶発リスク(合計に含めない) | — | +21〜43 | OPEN-395(#94): JA Latin語web lookupが1回JPY21.47(`er058_output/.../IMPLEMENTATION_11.md`、REPORT_LEDGER L329)。Coffee日本語にICO/USDA等があり未登録の場合に最大2回程度 |

**Cap提案**: text stage `--budget-jpy 120`、audio stage `--budget-jpy 100`(期待の約1.5倍=soft stop、最悪は上限内)。soft stop到達でFableへ報告(自動継続しない)。

## 6. 本日累計(JST 2026-10-16)と日次1,000円(7-9)

- 出典: `docs/pm/REPORT_LEDGER.md`の2026-10-16行の費用記載を合算: L325 AUW委任_07 約0.57 + L327 FAMILY-C 委任_03 実費12.65 + L328 KP-EN-EXPLANATION-PACING-TRIAL 実費2.86 + L329 AUW委任_11 実費37.66 + L330 AUW委任_12 実費24.22 + L331 AUW委任_13 実費1.42 = **約79.4円**(下限。L326/L332/L334〜L336等のJPY0行を含む。L333のAUW「通算約JPY156」は日をまたぐため日次には加算していない)。台帳に費用が載らない委任があり得るため下限値。**`docs/pm/tools/daily_dev_cost_01.py --date 2026-10-16`を実行**(read-only・API 0、出力=`daily_cost_20261016.json`): ログ(`raw_usage_log.jsonl`等810ファイル/243記録をUTC→JST換算)採用値=**58.47円**、ledger側の機械抽出は2行・0円(「費用JPY<数>」書式のみ拾うため)。台帳の手集計(約79.4)とスクリプト値(58.47)は集計根拠が異なるため、**保守的に大きい方の約79.4円を採用**する(スクリプトは単価未登録を0円にしない設計で`unpriced:{}`)。
- E2E(期待96/最悪162+偶発43)加算後の本日累計見込み: **約175円(最悪約285円)**。日次1,000円に対し**超過見込みなし**(残約715〜825円)。7-9「当日累計+見積が1,000円を超える見込み=事前承認」の対象外。
- ただし**7-7: 見積100円超=ユーザー判断**。期待96は100円以下だが最悪162は超えるため、**Fableが実行前にユーザー費用承認を取る**ことを推奨(ユーザー指示§8「費用見積提示」に整合)。
- **15-9(量産単価70円/記事セット)**: 本E2Eは仕様配線の実証run(15-9「仕様変更・調査目的のrunはTrial特有/異常対応として別枠」)だが、同時にSol期のFamily Xセット原価の初の実測になる。期待約96円は目標70円を超える見込み(内訳: Research+Ledger 46.8=49%、Sol Writer 18.5=19%、Full Story TTS 約14=15%)。**品質＞納期＞量産単価**であり70円はSTOP条件でないが、15-9に従い「超過見込み」を記録し、実績確定後に改善策・代替案をFableが検討する(本計画では仕様変更しない)。新仕様の量産単価影響: IOLが+1文(TTS/ASR微増、約+JPY0.1〜0.3/セット)、K2のfallback増の場合は+0.3〜1.0程度(`fallback_used`で実測)。ベースラインはFamily X未測定(15-9)。

## 7. STOP条件(ユーザー§10)との対応

| ユーザー§10 | 本計画での検出点 |
|---|---|
| 過去承認と矛盾する新仕様が必要 | CP-A〜Fの照合で矛盾検出時 |
| 承認済みPrompt正本を特定できない | S0で6定数のソース突合test(特定済み) |
| 重大な設計変更でOpus条件Aが必要 | 本設計書→Opus条件A(Fableが委任)。実装中に設計外の変更が必要になればSTOP |
| 新しいTrialが必要 | IOL文面で「新しい編集方針」が必要と判明、または品質改善案を見つけた場合 |
| Mandatory Human Review/Budget Gate/品質Gate | ER Mandatory STOP(CP-C)、review_lock、gloss HR、M3、Audio Validation Gate、`--budget-jpy` |
| 同じ原因の失敗再発 | 既存retry後に再発したらSTOP(OPEN-343型の`CANONICALIZATION_INVALID`含む) |
| 実装範囲不明 | 本マトリクスで0件(未確認は「未確認」と明記済み) |
| 新規ユーザー判断が必要 | UDR候補は現時点なし(SPEC_WIRING_MATRIX §3)。IOL out-of-spec(1文/4文以上)が出たらSTOPしFable判断 |

## 8. リスク・補足

- E2E実走では**ユーザー指示の「IOL 1文を許容する旧経路を残さない」**ため、IOLが`spec_ok=false`ならS4/S5でSTOP(自動再生成なし)。再生成する場合は`--regenerate-stage advanced`→`standard`の順(IOLのみの再生成は存在しない。コスト約JPY2〜3)でFable判断。
- Advの速度変化(PD06に速度語なし)は試聴確認項目(FXWA §14-4)。ユーザー試聴で遅すぎ/速すぎが出た場合は新Trial(STOP→報告)。
- `file:///`と`raw.githubusercontent.com`は試聴配布に使わない。GitHub Pages反映遅延(deploy数分+Cache-Control 600秒)を見込み、headless取得でHTTP 200を確認してから「提示した」と扱う。
- 本計画は**Coffee生成を伴わない**。実行は設計書のOpus条件Aレビュー→Phase 2実装→test全PASS→費用承認の後。

- 【委任_02A R-11】Std Full StoryはPD06を逐語(A2減速instruction非連結、`std_append_slower_instruction=False`)で用い、生成後6%減速(既存)を維持する。Stdの遅さは6%減速のみ(PD06に速度語なし)。**試聴確認項目**: Std Full Storyの体感速度(6%減速+PD06の併用が遅すぎ/速すぎないか)、Adv Full Storyの速度(PD06のみ)、KP英語(K2)の語頭語尾、Std KP日本語意味(P8-KP)、Adv KP英語解説(P7)。ユーザー試聴で問題が出た場合は新Trial(STOP→報告)。

## §実行直前チェック(委任_04時点、2026-10-16、実行はしていない・JPY0)

**状態**: Phase 2配線はcommit済み(本commit=メッセージ冒頭『FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_02A/02B/04』)。Coffee正式実走は**未実施**。`PRODUCTION_WIRED`ではない(runtime evidence待ち)。実走は、Fableがユーザーへ費用を提示し承認を得た後の別委任で行う。

### (a) stage(a) text の実行コマンド全文(S1: Research新規+Verified Fact Ledger新規)
新out_dir `er019_output/coffee_prices/run_fxpw_01`(既存run_l3_01等のResearch/Ledger再利用を防ぐため必ず新規dir)。テーマ文字列は既存Coffee実走のものを使う(新規記事テーマ選定ではなくCoffee再実走、ユーザー指示§5。出典=`er019_output/coffee_prices/run_l3_01/entry_point.json`の`theme`)。

```
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_entertainment_production_runner_01.py --theme "<run_l3_01/entry_point.json の theme 文字列をそのまま>" --slug coffee_prices --out-dir er019_output/coffee_prices/run_fxpw_01 --run-label FXPW-COFFEE-E2E-01 --budget-jpy 120 --stage research
```
(STAGE(a)自体はTTSを含まないが、全stageで`TTS_EXECUTION_MODE=STANDARD`を明示する運用(T-2)に揃える。実走前に`tools/stop_scope_check_01.py --managed-id <新ID> --run-dir er019_output/coffee_prices/run_fxpw_01`を実行しrc=3なら中止。) 以降のS2〜S11は本書§1の表のコマンドに従う(音声stageは`--tts-backend`省略でも既定=`speech_metadata_flash_lite`、明示してもよい)。

### (b) 前提条件
1. `er019_output/coffee_prices/run_fxpw_01`が**存在しない**こと(`verified_fact_ledger.txt`・`research_ledger/`の既存再利用防止。新out_dirでは`runtime_evidence.json`の`reused:false`をX01で確認)。
2. 音声stage前に`--stage plan`(API0)で`audit/style_profile.json`の`profile_id==fx_20261016`・`style_profile_source==default_new_run_fx_20261016`を確認(委任_04でrun_l3_01を入力とするdry-runにて確認済み: 6 role sha=FULL_STORY 3a680861e4d9d1bc… / SUPPORT_JA 625826c1187b6381… / PREVIEW 8862317ff76693ff… / KP_EXPLANATION_EN 0518000694e31ef7… / KP_EN 9d905cfe6c040cd0… / KP_JA_MEANING b12c8721eab8434b…)。
3. 実装commit・Opus条件Aレビュー反映済み・回帰test PASS(委任_04: 37ファイル956 PASS、6 FAILは全件本件非起因=`docs/pm/RESULT_PACKET_FXPW4.md`)。
4. 追跡済み出力ファイル(`er011_output/attempt_history.jsonl`等)の既存dirty変更はstageしない。

### (c) 費用見積(再掲、出典=本書§5表)
期待 約JPY96 / 最悪 約JPY162(text小計 68.4/95、audio小計 27.8/67)。偶発リスク(合計に含めない): OPEN-395 JA Latin語web lookup +21〜43。Cap提案=text stage `--budget-jpy 120`、audio stage `--budget-jpy 100`。

### (d) 本日累計(JST 2026-10-16)の再計算
`docs/pm/REPORT_LEDGER.md` 2026-10-16行の費用記載を再合算: L325 約0.57 + L327 12.65 + L328 2.86 + L329 37.66 + L330 24.22 + L331 1.42 = **約79.4円**(本書§6と同値。FXPW委任_01/02A/02B/04・DQI等はJPY0行)。なお委任_04の回帰でer078 06c testが作業ツリー状態依存でPerplexity researchを実呼出した疑いがあり(推定数円以下、未計上・log未取得)、保守的に**約80〜85円**とみなす。E2E加算後: 期待で約176〜181円、最悪(+偶発43含む)で約285〜290円。

### (e) 7-7・日次1,000円との関係
- 日次1,000円(7-9): 最悪でも約290円で**超過見込みなし**(残約710円以上)。事前承認の対象外。
- 7-7(見積100円超=ユーザー判断): 期待96は100円以下だが**最悪162は100円超** → Fableが実走前にユーザー費用承認を取る(判断候補、区分A: 7-7の既判断ルール適用)。承認前に有料runを開始しない。


## §実走記録(委任_06、2026-10-16、Mandatory STOP解除後の音声工程S6〜S11。事実のみ)

- 実行: S6 plan(CLI Style/Prompt/backend指定なし、profile fx_20261016・source=default_new_run_fx_20261016・backend=speech_metadata_flash_lite・6 role sha全一致)→S7 scaffold(rc0、KP M2P0+A、m2_fallback=null、gloss NO_TARGETS)→S8 TTS Adv(rc0)→S9 TTS Std(rc0)→S10 assemble(rc0、style_profile_gate両level PASS)→S11 player。各stage前にstop_scope_check rc=0。再起動なし(各stage1回)。
- 出力dir: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01`(実行前に非存在確認)。試聴ページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_fxpw_e2e_01/index.html(commit bb22ab0af、HTTP 200確認=初回200は3分後、Playwright実再生: audio 51/51再生OK・seek OK・console error 0・全編秒数一致[Adv 306.63 / Std 327.29]。証拠=`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/audit/pages_play_evidence_06.json`)。Landing(articles_2026_0918.html)は20記事一覧で既存Coffee試聴ページも未掲載のため更新せず(既存方式踏襲)。
- 全segment Style適用表: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/audit/e2e_segment_style_table.json`(Adv: FULL_STORY x3 3a680861e4d9/PREVIEW 8862317ff766/KP_EN 9d905cfe6c04 x10/KP_EXPLANATION_EN 0518000694e3 x5。Std: FULL_STORY x3/SUPPORT_JA 625826c1187b x5/KP_EN x5[うち2件は同run内Adv生成音声のStore共用]/KP_JA_MEANING b12c8721eab8 x5)。K2 fallback 0件。
- 費用: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/audit/cost_by_stage_e2e_06.json`(集計script `er019_coffee_fxpw_cost_06.py`)。
- 非STOPの確認事項: PASS_WITH_WARNING 事後試聴リスト3件(Adv KP3英語[一次ASR "Character-driven." / 二次 "Tariff driven." で確定]/KP3解説[一次 "caused by terrorists." / 二次 "Caused by tariffs." 確定]/KP5解説、全てSECONDARY_CONFIRMED。segment表上はKP3 phrase_repeatも同warningで計4 component)は聞き取り対象として試聴ページ末尾に列挙。OPEN-401(derived_from_advanced_sha CRLF偽陽性warning、観測のみ)を新規登録。


## §Fable判定(委任_07、2026-10-16)
- 判定: Family X承認仕様の正式Production配線=**PRODUCTION_WIRED**(Fable判定。ユーザー原指示§6確認項目10件を委任_06のruntime evidence・test・SSOT・commitで照合し全件充足)。Opus条件Cは条件Aレビュー(OF-FXPW-R-01〜12)再利用(11-3 K)。正本=`CURRENT_SPEC.md`同日Fable判定行。
- 付帯(範囲限定、未達ではない): (a)Coffee記事run_fxpw_01=`USER_LISTENING_PENDING`(試聴未実施・PASS扱いしない) (b)Adv/Std英語本文の送信Prompt SHA記録は未実装(N1、OPEN-402) (c)IOL Writer段STOP・K2 fallback・Std fallback分岐はtest evidenceのみ (d)OPEN-399/401は非Blocking継続 (e)量産原価94.025/Batch換算87.497で70円目標+17.5超過(別途`FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01`で分析中、STOP条件ではない)。
