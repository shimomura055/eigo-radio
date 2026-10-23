FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_02-TRIAL-IMPL-VERIFY-20261023

# 委任_02: Opus条件Aレビュー反映→DEV/Trial実装(`er112_kp_gm_trial_01.py`、Production byte不変)→1回の多armTrial→自律改善ループ→Fable評価資料。Production/Prompt/template/flag変更0。

## 前提読込
`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{ROOT_CAUSE_01,DESIGN_01,OPUS_REVIEW_REQUEST_01}.md`、`docs/pm/RESULT_PACKET_KPGM1.md`、ユーザー原文 `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER.md`(§5検証項目1〜8・§6 QCD・§7境界)。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_02.md`(index 352以降、先頭MARKER一致)。
2. **Opusレビュー保存**: 下記所見を `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/OPUS_REVIEW_01.md`(Fable転記と明記)。
3. ACTIVE_TASK自分の行のみ(並行: ASR-QUALITY PN/UKUS agent=`er111_*`・`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/` 不可触)。OPEN-474 Status更新。共有SSOTは編集直前`git status`→自分の行のみ→即commit。
4. **予算確認(必須)**: 当日(JST)の採用済み開発費を集計(daily_dev_cost相当。本日は他案件でX 172円・Y 175円・Z 62円・午前分約260円・ASR Trial≤50円が見込み)。本Trialの見積(目標30〜60円、上限80円)を足して**日次1,000円を超える見込みなら有料部分を開始せず**、実装・replay用データ・judge基盤まで整え、RESULT_PACKETに「有料部分は翌JST日に実行可」と書いて終了(Fableが判断)。超えない見込みなら続行。

## Fable判定(記録用)
Opus総合判定=「必須修正5件を反映すればTrial可、再設計不要」。骨格は実質一致(新規LLM call 0、canonicalizationで一般化、validator表拡張、Trial-02 REJECTEDと整合)。対立点4(A-3の結合文/that→a・theの選び分けと置換条件/Std-Adv整合は決定論共有armを入れる/逐語gloss定義)はいずれも品質・測定の技術修正でProduct原則変更ではない→**Fable判断でTrial実装へ進む**。採用(template・gloss Prompt・説明Prompt・validator表の変更、Std/Adv gloss共有)はすべて VALIDATED→ユーザー判断。

## Opus所見(逐語要約)
- OF-01[必須] validator表拡張でProduction moduleを編集しない: `kc._PERSON_DEPENDENT_TO_GENERIC` は `er003_key_words_canonicalization.py:431-469`、`er105:670-677`、`er003_key_words_gloss_alignment.py:167-168`(`_CONCRETE_PERSON_EN`、import時固定)・`:236-243` から参照され、表変更はProduction gloss person検査の挙動も変える。表と判定関数は `er112_*` 内でDEV注入(monkeypatch/引数注入、patch順序注意)。「Production moduleのhash不変」をTrialの開始・終了条件に。
- OF-02[必須] normalization_reason配線漏れ: 新reason `generalize_reference_word` はstrict schema enum(`:113-136` NORMALIZATION_REASONS_FULLTEXT)に無く、reason分岐ゲート3箇所(`_is_valid_fulltext_normalization :502`、`_qa_field_effective_verdict :512`、`validate_canonicalization_item :571`)が既存2reasonしか通さない→`pulled him under→pull someone under` がINVALID/REVIEW_REQUIREDで外側retry枯渇。修正: him/her(/me)は既存reason `generalize_person_dependent_reference` を流用(schema変更不要、gloss側 `PERSON_NORMALIZATION_REASON` も通る)。新reasonはthis/that置換のみに使い、enum・3ゲート・template:41を同時更新しtest。
- OF-03[必須] that→aの決め方: (1)表は `{a, an, the}` 許容、Promptは「既定a/an、慣用句の標準見出し形がtheの場合のみthe」(`cross the line`/`toe the line`)。`draw a line` はユーザー明示例なので文字列一致3/3維持、gloss/説明は語義判定。(2)置換条件=that/thisが単数可算名詞前の限定詞のときのみ。置換しない: 代名詞(句末that)/副詞(that much, not that bad)/接続詞(so that)/不可算名詞前(that advice→変更しない)。validatorに機械条件(句末不可、直後がmuch/many/is/was/said等なら不可)。(3)a/an一致はCMU辞書で直後語の先頭音素が母音かを決定論判定(API 0)。
- OF-05[必須] A-3「日本語参考と同じ中心義」は誤り伝播(reach for one's walletではAdv gloss逐語誤り・Adv説明正)→差し替え: "Use the sense the phrase has in the source sentence; the Japanese reference is only a hint for which sense." 「ONE meaning, no story-specific conditions」は維持。PROMPT_SHA256変更=B仕様変更区分は正しい。
- OF-07[必須(評価側)] 「逐語gloss」定義: 日本語でも同じ比喩が通じる例(shine a light on→光を当てる、draw a line→一線を引く/一線を画す)を誤検出。A-2に「日本語でも同じ比喩が同じ意味で自然に通じる場合はその表現でよい。通じない場合はフレーズ全体の意味」「本文で字義どおりなら字義どおり」を追加。Judge基準は「本文での語義が日本語学習者に正しく伝わるか」。baseline逐語率をこの定義で数え直す。
- OF-04[推奨] OPEN-357(`close around me` me残り)を本件に関連付け、me→someone(できればus→someone)を対象に含める(対象外なら理由)。them/itは対象外で妥当。`her`は所有格/目的格両対応で `lose her job→lose someone job` は機械で防げない→LLM+合成test。
- OF-06[推奨] Std/Adv不整合0はPrompt共有だけでは確率的に困難→同一run内で両レベルに同じused_formが出た場合にglossを決定論共有するarmを最初から入れる(新call不要)。a2/b1bの実行順序・並列性をrunnerで確認。成功基準は語義の不一致0。採用はユーザー判断。
- OF-08[推奨] gloss gate/HR副作用: `_person_mismatch_reason` がhim→someone itemに効く(「彼」残りで不一致→retry/HR)、`someone` は FUNCTION_WORDS(`:460`)外で `added_content_words` に入る。望ましい方向だがretry・HR・OUTER_RETRY_EXHAUSTED件数をbaselineと比較。
- OF-09[推奨] 段階導入でなく1回のTrialで多arm: baseline / A-1 / A-1+A-2 / A-1+A-2+A-3(+OF-06共有arm)。A0(validatorのみ)はtemplate:11がhim/her置換を禁じるため無効、最小単位はA-1(template+validator)。前後1文を渡すarmは難例のみ。
- OF-10[推奨] 検証セット補強: 合成肯定(take that step / cross that line[the確認] / that idea→an idea / told her the truth)、合成否定(that advice / that much / so that / lose her job / close around me / turn on its head[its→one's禁止])。98%/90%は方向判断。
- OF-11[情報] 正常セットは文字列一致で機械判定しbaselineから変わったitemだけJudge→30〜60円。
- OF-12[情報] 大文字残り範囲外に同意、OPEN起票推奨(Carry the Loadの逐語gloss含む)。
- OF-13[情報] Trial-02整合/Prompt 2不変/source gate無影響/template:7自問文修正/変更は全てTrial→VALIDATED→ユーザー採用。Store reuse_key・説明signature(`er019_family_x_audio_production_runner_01.py:1077-1081` used_form基準で再生成)・OPEN-471/472統合は配線前確認事項。

## 1. 設計更新 `DESIGN_02.md`(OF反映差分表、規則5本文[置換条件・例外・a/an/the]、reason配線、A-2/A-3の最終文言、共有arm、判定定義、OPEN-357関連付け、大文字残りOPEN起票)。

## 2. Trial実装(DEV専用、`er112_kp_gm_trial_01.py`+test)
- Production module byte不変(開始/終了時にhash記録)。DEV注入: 表・validator条件・template override・gloss/説明Prompt override・reason enum/ゲート拡張(DEV側で同等ロジックを複製し、er003該当関数のsource hash drift guard test)。
- 使用モデルは本番と同じ(gpt-6-luna、最新性と理由を記録)。Judge 2系統(モデル名・最新か)+Fable抜取り用一覧。
- arm: baseline / A-1 / A-1+A-2 / A-1+A-2+A-3+共有 / (難例のみ)前後1文arm。各3回。

## 3. 検証(ユーザー§5項目1〜8に対応付け)
- セット: 難例20+正常30+合成肯定/否定(OF-10)。記事B `draw that line` は文字列一致3/3+gloss「境界線を設ける」相当+Adv説明「to establish a clear boundary or limit」相当を語義判定。
- 成功基準(DESIGN_01 §5の数値をOF-07定義で更新)。retry/HR/OUTER_RETRY_EXHAUSTEDのbaseline比較。
- **自律改善ループ**: 未達armは原因分析→前提見直し(置換条件/Prompt文言/共有方式)→再検証。`ITERATION_LOG_01.md`。見込みがなくなった場合のみ停止。
- 費用: 上限80円(超過見込みなら開始前停止)。

## 4. Fable評価資料 `TRIAL_RESULT_01.md`: 最終報告10項目の1〜7(修正前後の実例Std/Adv、arm別結果表、副作用、残存リスク、X/Z適用範囲、単価影響)。採用推奨の最小arm案(Charter 1)を根拠付きで。VALIDATED自己宣言はしない。

## 5. SSOT・Git: OPEN-474 Status、OPEN新規(大文字残り/Carry the Load)、OPEN-357関連付け、DECISION_LOG(Fable判断)、REPORT_LEDGER。明示add、secret_scan hits=0、`git push origin HEAD:main`。全回帰は最後に単独実行し分類。

## 6. 禁止: Production/Prompt/template/flag/閾値/golden変更、記事B成果物・音声・ページ変更、`er111_*`編集、有料run(記事生成)、80円超過、日次1,000円超過見込みでの有料実行、VALIDATED自己宣言。

## 7. 報告(docs/pm/RESULT_PACKET_KPGM2.md): (1)OF反映表 (2)実装構成・hash不変証明 (3)arm別結果表(基準/実測/判定、項目1〜8対応) (4)記事B実例の前後 (5)反復履歴 (6)副作用・残存リスク (7)費用(出典)・時間 (8)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。