FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_14-OPUS-A-REFLECT-PHASE0-CALIBRATION-AND-TWO-ISSUES-TRIAL-20261023

# FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14: Opus条件Aレビュー(DESIGN_05)の必須修正を反映(DESIGN_06)→Phase 0(既存出力で検査器を較正)→DEV Trial(②possessor_role写像、①独立検査+flag項目のみ再生成、代替arm)→X/Z DEV注入text E2E→Fable盲検資料→報告。**上限60円(Phase 0含む)**、Production変更0、未承認仕様の配線なし。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(line 2、KP行)、`.claude/agents/sonnet-worker.md`、`docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_{USER_06,委任_13}.md`、`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{ROOT_CAUSE_03,DESIGN_05,OPUS_REVIEW_REQUEST_05}.md`、`AUDIT_01/*`、`TRIAL_02/GOLD_LABELS_FINAL_01.md`、`TRIAL_03/FABLE_BLIND_RESULT_03.md`、`er112_kp_gm_trial_0{1,2,3}.py`、`er112_output/kp_gm_design_05/`、コード: `er003_key_words_canonicalization.py:431-473,497-518,562-583,672-678`、`er105_kp_fulltext_selector_01.py:670-709`、`er003_key_words_gloss_alignment.py:95,205-243,301-321,549-608,637,679-746`、`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt:11,12,39`、`er019_family_x_audio_production_runner_01.py:1077-1095`、`er026_family_z_fiction_production_runner_01.py:1517-1543`、test `er064_kp_idiom_trial_01_test_01.py`、`er003_test_key_words_canonicalization.py`。

## 1. Fable判断(Opus照合済み)
Opus総合判定=「必須修正後にTrial可」。方向(②role先行判定+決定論写像・追加call 0/①独立検査+flag項目のみ再生成・未flagはバイト同一/Std-Adv整合・G2/G3本採用・Sol全面切替・決定論字義検出は不採用/fail-open/attempt上限2維持)はClaude案と一致。対立点はいずれもTrial設計の精度であり、新仕様・承認済み内容の変更ではないため、**必須修正OF-D5-01〜05を全て反映し、推奨06〜13も採用**してTrialへ進める。C/C'同等時は**Cを優先**(Q>D>C、非劣化の構造保証。Claude案を退ける)。

## 2. Opusレビュー(逐語で `OPUS_REVIEW_05.md` に保存。見出し「Opus独立技術レビュー(条件A) DESIGN_05/ROOT_CAUSE_03 2026-10-23」)
---
総合: 必須修正後にTrial可。②方向性妥当だがroleが項目単位で複数人称語KP(put oneself in someone's shoes)を壊す/修復がfulltext部分窓・lemma併用に未対応。①方式C妥当だが検査の英語逆訳が「英語の字義=英語の慣用」型(draw a line/an unseen clock)で元に戻りsame_meaningと判定→目標事例を見逃す欠陥。原因分析は必要条件としては正しいが生成側誘因2つを見落とし(OF-06/07)。
[必須]OF-D5-01 ② roleを項目単位から人称トークン単位へ: 再帰代名詞(yourself等→oneself)はroleを問わず決定論でself。所有格は `possessor_roles:[{token,role}]` 出現順配列(要素数=display中の所有格数を決定論照合)。根拠 gloss_alignment:208。
[必須]OF-D5-02 ② 修復の適用範囲と整合: (i)置換しないことはどのroleでも常に許可と明記(mind your own business型・迷えば置換しないを一般化へ強制しない)。(ii)「noneなのに置換」はINVALIDでなくdisplayの語へrevert。(iii)fulltextのkeyはdisplayの部分窓・lemma併用あり(er105:694-709)、`person_generalization_pairs`は等長前提(gloss_alignment:240-241)→窓対応をer105から再利用。(iv)修復後に `changed_from_display_phrase`・`normalization_reason`・QA実効値(`qa_person_reference_generalized`は修復前keyの自己申告。FAIL残りはCANONICALIZATION_REVIEW_REQUIRED[:672-678]増)を決定論で再計算、前例 `_qa_field_effective_verdict`(:508-518)。
[必須]OF-D5-03 ① 検査callの逆訳設計: `gloss_alone_reading_en`を英語短句にすると「線を引く」→"draw a line"に戻り見逃す。修正: 出力順 (1)`usage_meaning_en`(KP+文から本文での意味)→(2)`gloss_alone_reading_en`(日本語意味だけから)→(3)`gloss_conveys`。(1)(2)は「KPの内容語を使わない平易な言い換え」とし内容語との重なりを決定論検査、重なれば「検査不成立」記録。flag条件 `usage_in_sentence=="figurative"` は再現率を下げる恐れ→「conveys単独」と「figurative AND conveys」を同一出力から事後計算で比較(追加費用0)。
[必須]OF-D5-04 ① C/C'採否規則を対称に: C'採用条件=(a)recall点推定がC以上 かつ(b)未flag項目の悪化がB0の2rep間ノイズ内。欠ければC。差額約0.05円/記事、同等ならC優先(Claude案と対立)。
[必須]OF-D5-05 ① 事象が少ない場合の事前宣言: B0のNGが閾値(例6件)未満なら比率でVALIDATEDとせず「既知NG+検出recall/precision+flag項目のBefore/After」で判定。推奨Phase 0: Trial_02/03の既存出力(gold/Fableラベル付き約360セル、字義NG5件、take the wheel/carry the load含む)を検査器にかけて較正(約2〜3円)。
[推奨]OF-D5-06 ①原因に生成Prompt側の誘因: 新規生成は再整合用Prompt流用(gloss_alignment:549-608): 字義訳を良しとする例 fall into→「～に落ちる」(:602)、「全語と過不足なく一致」(:585)、QA名 `qa_reflects_all_key_phrase_words`(:95,637)、`added_word_mappings`。G1はn=14・1rep・Sonnet判定で否定根拠にならず、方式Cの再生成も同Promptを通り字義再発経路。修正: 「G3参考」armを「新規生成項目だけ再整合用の指示・例を除いたmessage」armに置換(追加call 0)。
[推奨]OF-D5-07 ②原因に例示の偏り: 規則3の例が their→someone's/your→someone's のみ(:11)、規則4の例 pumps its fist→pump one's fist(:12)+its→{one's}許可表が apply its findings→one's を誘発。修正: self/other/non_personの一般例を均等に(特定記事の語句は使わない)。
[推奨]OF-D5-08 ② roleとkey食い違い時: 「roleに合わせる修復」と「displayへ戻す」をC1A同一出力に事後適用して比較(API 0)、「正しかったのはroleかkeyか」指標を追加。閉じた語彙内でLLM自身の構造化判定に基づく1トークン置換は自由文補正に当たらず思想矛盾なし。
[推奨]OF-D5-09 ② roleの2軸定義: 軸1=動作主と同一指示か、軸2=人か物か。動作主と同一で人/擬人化→one's、動作主でない人→someone's、動作主でない物・組織→現状維持(their enforce their rules含む)。物が動作主の定型句(find its way/run its course/take its toll)は現状維持(its)許容と明記。テンプレ:39 `qa_person_reference_generalized` 定義も「roleに従った現状維持はPASS」へ。
[推奨]OF-D5-10 ① 再生成後の再検査: flag項目のみ再検査する変種を測る(約0.05円/回)。attempt 2採用済み項目は `FLAGGED_UNREPAIRED_NO_ATTEMPT` で区別記録。
[推奨]OF-D5-11 C-Solの費用基準不整合: 実行するなら別の費用基準を事前明記。
[推奨]OF-D5-12 非劣化の分母: 「新規悪化≤全出力1%」は薄まる→flag項目内の悪化数・率を主指標、goldのPASS→FAIL 0件を要件。
[推奨]OF-D5-13 test影響: my/ourにsomeone's追加で `er064_kp_idiom_trial_01_test_01.py`(Rule7 INVALID固定)・`er003_test_key_words_canonicalization.py` の期待値が変わりうる→Grep対象明記。
[情報]OF-D5-14 決定論字義検出不可(「一線を引く」が「線」を含む)。gloss callへusage_type追加=C'と同じ。 OF-D5-15 Std/Adv整合不採用に同意。 OF-D5-16 fail-open妥当、ただし `SKIPPED_TECH_FAIL`/`FLAGGED_UNREPAIRED` 件数をrun summaryと記事報告に必ず出す。 OF-D5-17 b1bでgloss変化→Adv 5件まとめて再生成(約0.07円/回)、flagは確率的でKP stage再実行時にStore reuseが崩れうる(TTS再生成)。 OF-D5-18 「1/3以下」は「解消」ではない。残存NG率とCI・既知事例の結果を明示、「解消」はanchor・F層残存ほぼ0の場合のみ。判定基準値はTrial内事前宣言としてFable確定可、採用時の品質水準は§7(4)に残す。 OF-D5-19 §7概ね適切(B仕様不変、signature再生成連鎖で吸収、11-7不適用)。§7に「規則3の例示変更(OF-07)」「新規生成message変更armを採る場合のgloss Prompt変更」を追加。
一致: ②(a)追加call 0/①方式C/不採用群/fail-open/attempt上限2/Production不変。対立: トークン単位role(01)/none+置換はrevert(02)/英語逆訳(03)/同等ならC(04)/生成Prompt誘因とG3参考armの差替え(06)/例示偏り(07)。
---

## 3. 作業
### T-0 記録・予算
- 委任文逐語保存 `..._委任_14.md`(`py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、MARKER一致)。ACTIVE_TASK KP行: 委任_14 Status=`TWO_ISSUES_TRIAL_IN_PROGRESS`、上限60円、報告=`docs/pm/RESULT_PACKET_KPGM14.md`。当日累計を`daily_dev_cost_01`で確認(JST日付に注意: 10-23は上限1,400円、10-24に跨ぐなら1,000円)。費用は `TRIAL_04/BUDGET_LOG_01.md` に段階記録、累計48円到達で見込み再計算、60円超過見込みなら停止前にFableへ。
### T-1 DESIGN_06(API 0)
OF-01〜13を反映した改訂設計。特に: ②トークン単位 `possessor_roles` 配列+再帰代名詞決定論self+2軸定義+物動作主定型句の現状維持+none/迷いは置換なし/revert+窓対応(er105再利用)+修復後の決定論再計算(changed_from/normalization_reason/QA実効値)+規則3例示の均等化案(特定記事語句なし)+test影響Grep。①検査callの出力順と内容語重なり検査+flag条件2種の事後比較+C/C'対称規則(同等ならC)+少事象の事前宣言+再検査変種+`FLAGGED_UNREPAIRED_NO_ATTEMPT`記録+費用基準(C-Solは実施しない、またはする場合は別基準を明記)+非劣化主指標(flag項目内悪化、gold PASS→FAIL 0)。判定基準(事前宣言、Fable確定): (i)既知字義NG事例(draw a line、an unseen clock)の検出recall、F層での残存字義NG(目標ほぼ0、「解消」表記はF層残存0かつanchor 0の場合のみ)、(ii)flag項目内の悪化0〜ノイズ内、gold PASS→FAIL 0、(iii)②は既存29件+Trial KPで不一致0・正しいKP破壊0、INVALID/REVIEW_REQUIRED増0、(iv)追加費用≤0.15円/記事。
### T-2 Phase 0: 検査器較正(≤3円)
Trial_02/03の既存Std出力(gold/Fableラベル付き)を①検査器(OF-03設計)にかけ、字義NG5件のrecall、take the wheel/carry the load等の偽陽性、「検査不成立」率、flag条件2種の比較を出す。較正結果が悪ければ検査Prompt/出力順を1回だけ改訂し再測(費用内)。結果→`TRIAL_04/PHASE0_CALIBRATION_01.md`。
### T-3 Trial(DEV er112基盤、Production変更0)
- KP集合: 過去115 KPを再利用し、**結果に依らない事前層別**(F層=比喩・慣用、N層=コロケーション・用語・句動詞)を見出し語と本文のみから決定(層定義を記録)。②は所有格を含むKP全件(既存29+Trial内)+再帰/二重所有/物動作主定型句/総称you/組織their の合成例(個別対策ではなく型の網羅)。
- arm: B0(現行)/C(検査+flag項目のみ再生成、attempt上限2内)/C'(自己監査)/C-recheck(flag項目再検査変種)/M(新規生成項目だけ再整合用の指示・例を除いたmessage、OF-06)。②: C1A(possessor_roles付きcanonicalization)に対し「roleに合わせる修復」vs「displayへ戻す」を事後適用で比較(OF-08)。2rep(B0とCは必須2rep、他は1repでも可、費用内で)。
- 判定: 確定gold+Fable盲検(arm伏せ表 `TRIAL_04/fable_blind_04.md` + key分離)。Sonnet Judgeは参考。改善件数・残存NG・新規悪化(flag項目内/全体)・②不一致件数・INVALID/REVIEW_REQUIRED件数・`SKIPPED_TECH_FAIL`/`FLAGGED_UNREPAIRED*`件数を集計。
- X/Z DEV注入 text E2E(TTSなし、各1本、約6〜10円): ②③を含むcanonicalization→gloss→(b1bのみ)Adv説明の連鎖がretry/fallback込みで通ること、signature変化でAdvが再生成されること、Production module sha256が開始/終了で同一であることを記録。
### T-4 配線設計更新(API 0)→`WIRING_DESIGN_04.md`
採用時のX/Z共通変更点(canonicalization schema/規則3例示/decoding後処理/検査call/再生成経路/fail-open/記録項目/test影響[OF-13]/A-1同梱/既存完成記事の扱い/Store reuse影響[OF-17])と、ユーザー判断事項一覧(記事あたり+1 call、規則3例示変更、新規生成message変更[Mを採る場合]、fail-open/attempt1採用の安全方針、判定基準値)。
### T-5 報告・SSOT・Git
`TRIAL_RESULT_04.md`(ユーザー§4の6項目: 根本原因/対策と仕組み/Before-After具体例/改善件数・残存NG・新規悪化/X/Z共通仕様・Production影響/QCDと必要判断。手段と目的を区別、「解消」表記はOF-18の条件下のみ)。OPEN-474追記。CURRENT_SPEC/Production変更0。secret scan 0件→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。報告=`docs/pm/RESULT_PACKET_KPGM14.md`(使用model名・最新か明記)。

## 4. 禁止・制約
Production code/Prompt/flag/閾値/golden変更0(er112系とdocsのみ、DEV注入はhook/公開引数のみでProduction fileに注入コードを残さない)。個別対策(特定表現のfew-shot/辞書登録)禁止。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。PIDは自分のもののみ(26-6)。上限60円無断超過禁止(Judge等の並列発行時はcap検査を発行前累計+見込みで行う)。`py` または `.venv\Scripts\python.exe` を使用。秘密情報出力禁止。
## 5. handback
完了/予算警告/blocker/USER_DECISION_REQUIRED候補(例: 設計上B仕様変更が不可避と判明)で。途中経過は小刻みに返さない。