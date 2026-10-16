# 委任_02B 受領委任文(T-0保存、FXPW)

管理ID: `FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`(FXPW)委任_02B(Phase 2実装 トラックB: In One Line「基本2文・必要時のみ3文」の全経路適用=Adv新Prompt・Std継承1文・文数カウンタ中立module・Writer段fail-closed STOP・Local Rewrite文数保持gate[Family X限定]・evidence保存・test)。
並行委任あり(重要): 委任_02A(トラックA: er019_family_x_style_profile_01.py / er019_family_x_audio_production_runner_01.py / er003_v1_repro01_main_generate.py / er006_master_audio_store_01.py / er063_family_z_audio_01.py系test)とDQI委任(docs/pm/PM_GOVERNANCE.md / .claude/agents/* / docs/pm/tools/)が同じ作業ツリーで動いている。本委任はそれらのファイルを編集しない。git add/commit/pushは行わない(統合委任_04でFableがcommit)。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REGISTER/REPORT_LEDGER)も編集しない。特にer019_family_x_audio_production_runner_01.pyは触らない: Local Rewrite用Family X scope(contextvar)のset呼出はTTS段(audio runner)に必要だが統合委任_04で1行追加する。本委任はcontextvar+setter(context manager)を中立moduleに定義し、er020側の判定を実装し、testではcontext manager内で検証する。

## 前委任の受入記録(Gate 7)
委任_01(commit c0c35fc83): PHASE1_MATRIX_AND_DESIGN_COMPLETE、Fable受入ACCEPTED。設計書WIRING_DESIGN_01.md §CへOpus条件Aレビュー(総評「条件付き可」)。Fableは条件を全件採用。IOL文面・3文基準はユーザー原文§4「具体的Prompt文面と3文にする基準は設計して報告する。これは既存承認仕様の実装であり、文数方針を再度Trialに戻さない。」によりユーザー承認不要(報告で提示)。

## 性質/到達上限Status/禁止事項
- 性質: Production code実装+unit/regression test(API 0)。到達上限Status: TRACK_B_IMPLEMENTED_TESTS_PASS(PRODUCTION_WIRED判定はしない)。
- 禁止: 有料API、Coffee生成、トラックA/DQIのファイル編集、git add/commit/push、SSOT編集、Family A/B/C/Zの挙動変更(er020共有moduleの新gateはFamily X scope内のみ有効。scope外では不発をtestで証明)、新retry機構(IOL自動再生成)の追加、_M1_REQ_ANCHOR行の改変(ADV:589付近、一字一句保持。assert TEMPLATE_M1 != TEMPLATE維持)、新しい編集方針の追加(必要と判断したら実装せず報告)。
- Opus独立技術レビューGate(11-3): 条件A実施済み。時間見込み120〜150分。費用JPY0。承認区分A。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(T-3: 費用上限なし=JPY0。TTSなし)。T-0保存先は本ファイル。

## ユーザー指示(原文、USER.md §4「In One Line」)
「旧Promptの `Exactly one sentence` を置換する。仕様は「基本2文、必要な場合のみ3文」で確定済み。1文を許容する旧経路を残さない。初回生成だけでなく、Standard継承、Local Rewrite、retry、regenerationにも適用する。文数だけでなく、要点・意味・示唆を自然に伝える内容品質を維持する。具体的Prompt文面と3文にする基準は設計して報告する。…ただし、新しい編集方針を追加する必要が生じた場合は、ユーザー判断を要する。」

## Fable決定(設計書§C/§F/§Gを上書き)
1. Adv新Prompt(§C-1採用、R-05修正): §C-1の文面を使用。Requirements 2文目の「its meaning or implication for the listener」を「its meaning or why it matters, as the article states it」へ変更。他は§C-1どおり(基本2文/3文は理由条件のみ・上限3・詳細追加のための3文目禁止/1文1論点/_M1_REQ_ANCHOR保持/「12-18 words」「Trial-only guidance」撤去→「roughly 12-22 words per sentence (not a strict rule)」/出力形式)。撤去確認Grepに ONE short / single most important / Exactly one sentence / 12-18 / Trial-only(対象Production module、Trial module er045等は対象外)。
2. Std継承(§C-2採用): er003_v1_n3_01_standard_a2_generate.py の `Keep the same Markdown structure (...); do not add or remove sections.` 直後に1文追加: `Keep the "In one line" section at the same number of sentences as in the article below (normally two), each as a short A2 sentence; do not merge it into one sentence.` 既存testへの影響なしを確認。
3. 文数カウンタ(R-04): 新規中立module er081_family_x_in_one_line_01.py(他moduleをimportしない純関数+contextvar): count_in_one_line_sentences(text)->int(§C-5分割規則+略語保護 U.S./Mr./Mrs./Dr./Inc./vs./e.g./i.e./No./St.+小数点保護+$始まり・引用符・改行)、IN_ONE_LINE_SPEC_COUNTS={2,3}、family_x_in_one_line_scope()(contextvarを立てるcontext manager、既存secondary_run_scope方式参照)、is_family_x_in_one_line_scope()->bool。
4. Writer段fail-closed STOP(R-03): Adv IOL生成直後(er019 family x entertainment runner _advanced_in_one_line / EFAM:373-374付近)およびStd IOL生成直後に文数を数え、{2,3}以外なら既存Mandatory STOP機構(既存パターンをGrepで特定し再利用。新機構・新sentinelを作らない)でTTS前に停止(自動再生成なし)。Adv/Std文数不一致(2 vs 3)は[WARN][IOL-SPEC]のみ。evidenceを writer_run_summary.json の advanced.in_one_line / standard.in_one_line に {sentence_count, spec_ok, model_id_actual, response_id, prompt_sha256, usage} として保存(N1/N2解消)。prompt sha256は実送信文字列から計算。
5. Local Rewrite(案L1、R-04修正): er020_tts_retry_local_rewrite_01.py の候補採否(check_localityの隣、criterion6/7と同層)に別キー `8_sentence_count_unchanged` を追加。有効条件=is_family_x_in_one_line_scope()がTrue かつ resolve_narrative_role(segment_id)=="IN_ONE_LINE"。それ以外は常にTrue(不発)。既存seven_gates/all_seven_gates_passの名前・件数・意味は保つ(新キーは別集計)。LR:158ラベル不変(案L2不採用)。
6. test(新規 er081_family_x_in_one_line_01_test_01.py等): (1)templateに Exactly one sentence/12-18/Trial-only/ONE short/single most important/for the listener が無く_M1_REQ_ANCHORを含みM1変種が従来どおり (2)カウンタ(2/3/1/4文・略語・引用符・数値・$始まり・改行) (3)fake clientで_run_writer_stage_once相当: evidence保存・1文でSTOP・2/3文で通過・Adv2/Std3でWARNのみ(API 0) (4)Std Prompt追加1文 (5)LR: scope内でIN_ONE_LINE roleの句読点のみ変更(2文→1文)候補が不採用、scope外では不発 (6)parts.jsonのin_one_lineが複数文でもsplit_family_x_article_text_v2がOK。既存test(er019_family_x_new_structure_wiring_01_test_01 / er019_family_x_entertainment_production_runner_01_test_01 / er020*test* / er003_v1_n3_01*test*)全PASS。
7. 撤去(§G): Exactly one sentence / Trial-only guidance / 12-18 words を撤去。open243_m1_enabled死コードは残置。

## 手順
1 実装→test(.venv\Scripts\python.exe -m pytest ...) 2 撤去確認Grep 3 WIRING_DESIGN_01.mdに「§K 委任_02B実装記録」追記(最終Prompt全文・3文基準・STOP実装箇所・LR gate・testリスト・統合委任_04へ残す1行[audio runnerでのfamily_x_in_one_line_scope()囲み位置: file:line]) 4 git status --short(add/commitしない)・secret scan(--paths)。

## 報告
docs/pm/RESULT_PACKET_FXPW2B.md: 1 T-0 / 2 最終Prompt全文(Adv)+Std追加1文+3文基準 / 3 STOP実装 / 4 LR gate / 5 evidence保存キー / 6 test結果 / 7 撤去確認Grep / 8 変更ファイル一覧(未commit)・secret scan / 9 逸脱・新編集方針が必要と感じた箇所 / 10 費用JPY0・所要 / 11 受入記録5項目 / 12 P1判定整合行 / 13 統合委任_04へ引き継ぐ1行(AR側scope囲み位置)。
