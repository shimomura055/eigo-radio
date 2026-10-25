# DESIGN_05(Trial-05: Part 2 Step A' = 網羅タグ付け -> 候補ごとの絶対判定 -> 決定論規則)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_10 / 日付: 2026-10-25 / Status: DEV/Trial専用。Production採用・配線は未承認。
根拠: `OPUS_REVIEW_03.md`(条件A。別案A')、`EVAL_04.md` §2-4、Fable判断(委任_10 §2)。実装: `run_trial_05.py`。基準: `PREREGISTERED_CRITERIA_05.md`(生成前commit)。

## 1. 変更の要点(Trial-04のStep Aとの差)
| 項目 | Trial-04 Step A | Trial-05 Step A' |
|---|---|---|
| 候補 | 最大5件を検討(構造的な拾い漏れ。『開いた窓』P21が4標本とも候補に挙がらず) | 本文の全文を点検し、特徴のある文を**上限なしで列挙**。特徴のない段落は段落番号一覧(`no_feature_paras`)で返す(出力を抑える) |
| 判定 | 「最も価値の高い文を選ぶ」(相対評価)と「基礎は選ばない・0件可」(絶対条件)の併記 | 列挙した文ごとに**その文単体で絶対判定**(分類コード・構造の取り違え・正しい構造・基礎のみか・層A/B/C) |
| 選ぶ主体 | LLM | **コードの決定論規則**: 層A かつ 基礎のみ=false かつ 構造取り違え欄が空でない文を、LLMのrank順(同値は段落順)で最大2件。該当なしは0件 |
| 基礎項目 | 否定側のみ+「特殊な用法なら可」の例外(抜け穴) | 否定側の基礎項目一覧(作品に依存しない文法項目)+肯定側の価値分類10コード。例外は肯定側に該当する場合のみ有効 |
| 誤読の根拠 | 制限なし | 構造の取り違え(主語・動詞・修飾先・省略の補い方)に限定。語彙の誤読は不可 |
| 呼出 | 1 | 1(Step Bは従来どおり別call) |
Step B・Part 1(α)・Part 3/4は再利用(Step B Promptは無変更、入力の選定文が変わるだけ)。Part 1/3/4はTrial-04 r1の出力を無編集で組み込む。

## 2. 入出力schema
入力: 作品名・レベル・番号付き本文(KPは渡さない)。
出力JSON: `features[]`(para, sentence[本文から逐語], feature_class[INV/CLEFT/CMP/HEAVY/POSTMOD/FRONT/APPOS/ELL/SPEC/OTHER], other_desc, misread_ja, misread_quote, correct_structure_ja, basic_only, tier[A/B/C], rank[Aのみ], construct_ja/points_ja/context_ja[tier Aかつ基礎のみfalseのみ])と`no_feature_paras[]`。
パース: 文は`run_trial_04.resolve_verbatim`で本文側の逐語文字列へ引き当て(M1と同類の構造的保証。解決不能な文は記録して規則から除外、再試行しない)。前後1文(R1)・参考訳(R4)も自動付与。JSON不正・欠落は記録のみ(自動再試行なし)。
記録のみの検査(規則には使わない): `misread_quote_in_sentence`、`uncovered_paras`(全文カバレッジ)、`sentence_replaced_by_body`。

## 3. 決定論規則(`is_eligible`/`select_rule`)
`tier=="A"` かつ `basic_only==false` かつ `misread_ja`が空でない かつ 文が本文に解決でき重複でない → 適格。適格をrank昇順(同値は段落番号昇順)に並べて先頭から最大2件。適格が0なら選定0件(0件を既定にはしない。全文タグ付けで拾った上での結果)。
`to_selected`は材料欄(construct_ja/points_ja/context_ja)が揃う場合のみStep B入力にする(欠落は記録して除外)。

## 4. (B)条件付き多数決(オフライン模擬のみ。既定OFF)
`sim_B`: 選定文の多数決ではなく、標本ごとの層A適格判定を文ごとに集計し「n回中2回以上」を母集団にしてから同じ規則で最大2件(Opus必須修正4)。層Aが空で層Bが2回以上の文は`fable_report_tierB`として記録。全N標本合意(層A適格率≥2/3)の選定は、Step B用の「合意選定」としても使う。
Checker/Validatorの新設ではない(生成済みのユーザー向け文を検査せず、選定段の入出力構造と集計規則のみ)。採用時は「選定段のアンサンブル」として開示する。

## 5. 既存機構との整合・Production境界
- Production側に英語学習テキスト解説は存在しない(DESIGN_04 §1)。本Trialは全てDEV専用で、Production code/Prompt/flagの変更0。
- 責務: 点検・タグ付け(LLM)/選定(コード)/執筆(Step B LLM)。評価語を含みうる欄(misread_ja等)はDEV記録のみでStep Bへ渡さない(`reason_dev`相当)。
- 過剰適合防止: Promptの例はいずれも作品外の自作文(dry-runで4作品の本文の文を含まないことをassert)。ホールドアウト作品を加える。
- temperature/seed/reasoningは未指定(provider default)。
