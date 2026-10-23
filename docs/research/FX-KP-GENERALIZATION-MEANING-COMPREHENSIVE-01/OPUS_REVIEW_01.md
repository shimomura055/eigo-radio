# OPUS_REVIEW_01: 条件A独立技術レビュー結果(Fable転記)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 2026-10-23。本ファイルはOpusレビュー所見を**Fableが委任_02の委任文に転記した逐語要約**を、実行層(Sonnet)がそのまま保存したもの(Opus原文ではない)。対象=DESIGN_01.md。

## Fable判定
Opus総合判定=「必須修正5件を反映すればTrial可、再設計不要」。骨格は実質一致(新規LLM call 0、canonicalizationで一般化、validator表拡張、Trial-02 REJECTEDと整合)。対立点4(A-3の結合文/that→a・theの選び分けと置換条件/Std-Adv整合は決定論共有armを入れる/逐語gloss定義)はいずれも品質・測定の技術修正でProduct原則変更ではない→Fable判断でTrial実装へ進む。採用(template・gloss Prompt・説明Prompt・validator表の変更、Std/Adv gloss共有)はすべて VALIDATED→ユーザー判断。

## 所見
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
