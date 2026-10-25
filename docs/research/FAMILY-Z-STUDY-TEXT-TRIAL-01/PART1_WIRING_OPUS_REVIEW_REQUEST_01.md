# PART1_WIRING_OPUS_REVIEW_REQUEST_01(条件A: 新しい処理フローの設計) — FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_13 Part 1 Production Wiring

依頼元: sonnet-worker(Fable経由で送付)/日付: 2026-10-25/読み取り専用レビュー。Opusは実装・PRODUCTION_WIRED判定・Production採用可否の宣言をしない(`docs/pm/PM_GOVERNANCE.md` 11-3)。同一内容は重複レビューしない。

## A. 依頼の背景(要点)
- ユーザーは2026-10-25、Trial-04案α(Key Phraseの英語表現のみを別LLMへ渡して日本語の一般解説を生成)を**APPROVED_FOR_PRODUCTION**とし、Family X/Zの正式経路へ配線しPRODUCTION_WIREDまで進めるよう指示(原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_05.md`:10-54)。未承認の追加改善・品質基準変更は禁止。「新しい未承認仕様の採用まで包括承認するものではない」。
- 調査の結果、**現行Productionにはこの解説(Part 1)の生成箇所自体が無い**(置換対象なし=新しい独立段の追加)。KP表の「英語での説明」(`kp_explanations.json`)は音声用の別成果物で並存させる。
- Production経路に新しいLLM呼出工程を追加する=新しい処理フロー(条件A必須)。本レビュー後に実装委任へ進む。

## B. 読んでほしいもの(この順)
1. `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/PART1_WIRING_SPEC_CHECK_01.md`(現行経路・X/Z経路・TrialとProductionの差分表・訳の生成元調査)
2. `PART1_WIRING_DESIGN_01.md`(配線設計(a)〜(k))
3. `part1_wiring_tests_draft_01.py`(test雛形。Section A実行済み 3 passed、B/C/Dは実装待ちskip)
4. Trial正本: `DESIGN_04.md`・`PROMPT_04.md` §1・`run_trial_04.py:74,194,288`・`ADOPTION_NOTE_04.md`・`OPUS_REVIEW_02.md`(M1/M2/R1-R5)・`EVAL_04.md`(Part 1基準)・`usage_04a_*.json`
5. Production該当箇所: `er026_family_z_fiction_production_runner_01.py:1692-1776`(stage_kp/kp_expl_b1b)、`er062_family_z_writer_01.py:64-68,690`(DEPENDENTS/ensure_stage)、`er019_family_x_audio_production_runner_01.py:387-480,1069,2706-2717`(scaffold/kp_expl resolver/rc=3)、`er019_family_x_kp_explanation_01.py:258`(retry方針の先例)、`er063_family_z_audio_01.py:1918-1985`・`er_user_listening_page_common_01.py:44-210`(ページ/標準適合check)

## C. 論点(a)〜(h)
**(a) 入力隔離の保証**: 型(`list[str]`のみ)・値検証(英語表現形のみ、CJK/改行拒否)・抽出点の単一化(`generate_for_kp_items`)・送信直前のリーク検査(source_sentence/gloss/meaning_in_text_en/naive_ja全体がPromptに含まれない)・audit(input/prompt sha)・test、の多層で十分か。見落としの経路(例: `used_form`に文脈語が残る場合、`display_phrase`と`used_form`の取り違え、将来の引数追加)は無いか。リーク検査の「長さ≥表現長+4の部分文字列」基準は妥当か。
**(b) 再生成制御とresume整合**: キーを「表現文字列+順序のみ」(本文sha・gloss・引用文を含めない)にする設計は、(1)Zの`ensure_stage`(sig変化=`ProvenanceMismatch`でSTOP→明示`--regenerate-stage kp_part1_b1b`)と(2)Xの自動再生成(`_resolve_kp_explanations_text`型)で、本文Regen/Local Rewrite/KP再選定/HR解決/外側retry後のあらゆる経路で「古い解説の誤表示」も「無駄な再生成」も防げるか。Zの`kp_expl_b1b`はDEPENDENTS未登録でsig不一致STOPに依存しているが、`kp_part1_b1b`も同様でよいか(DEPENDENTSに`kp_b1b→kp_part1_b1b`を足すべきか)。X/Zの挙動差(Z=明示/X=自動)を既存踏襲のまま許容してよいか。
**(c) retry/fallbackの既存仕様整合**: 技術retry1回(parse/構造のみ)→fail-closed STOP(Z `FamilyZE2EStop`/X `kp_stage_status`→rc=3)、旧方式fallbackなし・空欄続行なし、が既存の`generate_kp_explanations`・KP stage fail-closed(KPMP-03)・外側retryと矛盾しないか。Part 1をKP外側retryの**外側(後)**に置いた判断は妥当か(Part 1失敗でKP選定をやり直さない)。「Part 1失敗でも音声は継続」の非blocking案を採らない判断(新挙動回避・TTS前fail-fastで費用損失最小)は妥当か。
**(d) X/Z両経路の一貫性**: 同一module・同一関数を呼ぶ構造にした。呼出点がZ=`stage_kp`内(ensure_stage)/X=`run_theme_scaffold`内+`--stage study_text`である非対称は許容か。Xの`tts`段だけを実行する運用(scaffold未経由)で欠落しないか(scaffoldが常に先行する前提で足りるか、tts段にfail-fast前提チェックを足すべきか)。
**(e) Dangling Reference**: 旧Part 1生成が存在しないという調査結果(Grep)の確認、Trial資産(docs/research)を残置しProductionからimportしない方針、`kp_expl`との並存、routing表への新process追加が既存の列挙test(`er009_n1_routing_governance_10_pricing_table_open251_test.py:12`等)・static auditに与える影響、の抜け漏れ。ページに`Part 1`番号を出さず`Vocabulary & Expressions`見出しのみとする判断(Part 2〜4未採用)は妥当か。
**(f) 表示・ページ標準の整合**: Zの`build_pages`にAdvanced節の任意`study_html`を追加(未指定=バイト同一)する案が、承認済み「ユーザー試聴ページ標準フォーマット」(CURRENT_SPEC:2927、`check_page`のC3/C4/C5)の変更に当たらず、標準適合checkを壊さないか(class名・内部情報regex)。標準適合checkに「study block任意・存在時は整形式」の項目を足すべきか。Xのper-article公開ページが共通builderを持たない点(組込みを別OPENにする案)の扱い。
**(g) 費用**: 追加原価実測0.0775円/set(range 0.0689〜0.0889、70円比約0.11%)・時間+約11〜13.5秒(直列)・Luna使用(最新世代原則との整合)の評価。直列のままでよいか(kp_explとの並列化は複雑化に見合わない判断)。E2E発火証拠の費用見積約0.3〜0.4円(完成済みrun artifactの再利用、新規記事・TTSなし)の妥当性と、実公開ページ更新をE2E証拠から切り離す判断。
**(h) 日本語訳の生成元の扱い**: 既存仕様に生成元が無い事実(SPEC_CHECK §5)と、T1(専用翻訳call、+約0.03円/set、解説LLMとは別入力)/T2(訳欄なし)/T3(解説LLMに兼務=入力隔離を破るため却下)/T4(X日本語原稿対応=Z不可のため却下)の整理は妥当か。T1の入力に「前後1文(本文から決定論取得)」を含める設計は、案αの入力隔離(解説LLM側)を損なわず、翻訳側の指示語解決に必要かつ十分か。未決のまま実装を先行する範囲(項1/2/3/5)の切り方は、未承認の新仕様を暗黙に採用していないか。

## D. 求める出力
- 論点(a)〜(h)ごとに「問題なし/修正必須(具体的修正案)/推奨事項」。
- 実装委任へ進んでよいか、進む前に必須の設計修正があるか。特に(a)(b)(c)は必須修正の有無を明示。
- 見落としているX/Z経路(Regenerate/Local Rewrite/HR Lock/resume)があれば列挙。
- 新しい構造(Validator新設等)の提案は、必要性がProduction安全に直結する場合に限り、新仕様としてユーザー判断が要る旨を付して記載(本設計はValidatorを新設しない)。
