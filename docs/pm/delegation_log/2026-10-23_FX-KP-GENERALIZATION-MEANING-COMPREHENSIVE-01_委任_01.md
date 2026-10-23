FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_01-ROOTCAUSE-DESIGN-20261023

# 委任_01: Key Phrase 一般化・文脈意味・意味説明の包括対策 — 原因究明+設計(Opusレビュー前まで)。read-only+設計文書。Production/Prompt/flag変更0。API費用≤10円(理由記録)。

## 背景(ユーザー新指示 2026-10-23)
記事B「英国の電車マナー」(uk_train_speaker_playback run_nws_02)のKP: Adv `draw that line`=「to decide where the limit is between what is acceptable and what is not」、Std `draw that line`=「その線を引く」。期待: KP `draw a line`/Std「境界線を設ける」/Adv「to establish a clear boundary or limit」。要点①一般化(時制・指示語・所有格を持ち込まず自然な再利用形)②本文中の意味を正しく捉える(逐語訳不可)③学習者向けに汎用化、中心的意味を1つ簡潔に。Scope=原因究明・設計・Opusレビュー・Trial実装・反復検証・Fable評価・記録(VALIDATED止まり、Production配線未承認)。記事Bの完成候補・音声は保全、無断反映禁止。新規LLM工程・API追加は安易にしない(既存Prompt・工程改善優先)。

## T-0
1. **ユーザー指示原文を逐語保存**: jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` の最新userメッセージ(「# Claude Code / Fableへの指示 ## Family X Key Phrase品質改善 — 一般化・意味説明の包括対策【修正版】」)を `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER.md` へ改変なしで保存。
2. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <同jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_01.md`(index 348以降、先頭MARKER一致)。
3. ACTIVE_TASK自分の行のみ(並行: ASR-QUALITY PN/UKUS 2 agent=Trial実装中、`er111_*`・`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/` は触らない)。OPEN_ITEMS: 新規行(本管理ID、Status=ROOT_CAUSE_DESIGN_IN_PROGRESS)+OPEN-467へ「記事B KP `draw that line` 品質未解決事項(修正候補: draw a line/境界線を設ける/to establish a clear boundary or limit、新仕様採用後に正式経路で反映、現成果物保全)」を追記。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 1. 原因究明(証拠 file:line)
- 現行X/ZのKP工程全体: 選定(fulltext_p2 / kp_backend、KPFT 3件、CMU gate、5語以下、本文存在ルール)、一般化(既存の承認済み一般化ルール・Prompt文言。KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 OPEN-458 ①②の内容と範囲を確認)、Std日本語意味生成(kp1_japanese_meaning)/Adv英語説明生成のPrompt・入力(本文文脈を渡しているか)・モデル、検査(Validator/gloss alignment/kp_vote_check/KP3V=音声側)。X/Zで共通か別実装か。
- 記事B run_nws_02 のKP生成の実ログ(prompt・response・選定候補・採用理由)を追い、(a)`draw that line`が一般化されなかった原因(選定時にそのままsurfaceを採用/一般化指示が選定段にしか無い/Validatorの「本文存在」ルールが一般化形を弾く等)、(b)Adv説明が記事文脈依存になった原因、(c)Stdが逐語訳になった原因(慣用句判定なし/文脈未投入/短すぎる出力制約)、(d)Std/Adv間不整合の構造原因(別callで独立生成・共有の意味定義なし)、(e)既存ルールが実効性を欠いた理由(Promptの位置・優先度・例示の有無・出力形式・検証の欠落)を特定。
- 過去の同種問題・Trial・承認済み対策(KPQ ①②、kp_gloss_alignment、`reach for one's wallet`型の one's 一般化があるなら既存ルール)との関係。
- 定量(API 0): 直近X/Z記事(≥10記事、Std/Adv計≥60 KP)のKPを機械+目視で分類: 一般化不足(指示語/時制/所有格残り)、逐語訳疑い、文脈依存説明、Std/Adv不整合、5語超。発生率を出す。

## 2. 包括対策の設計(DESIGN_01、推奨1案+代替、比較表)
- ユーザー要求①〜⑥(一般化/文脈意味/汎用性/慣用表現/レベル間整合/簡潔1意味)を、**既存Prompt・工程の改善を優先**して満たす構成。候補例(採否は設計者): (A)選定段の出力を「本文surface+学習用基本形(lemma形)+文脈での中心的意味(1文、英語)」の構造化出力に変え、Std日本語意味/Adv英語説明は共通の「中心的意味」から導出(1意味定義を共有して整合確保)、(B)一般化規則の明文化(冠詞 a/one's、時制原形、指示語除去、句動詞・慣用句の辞書形)+「本文存在」ルールは surface で検証し表示は基本形(既存ルールとの両立)、(C)慣用句は辞書形で意味説明、逐語訳禁止の検査(日本語意味がsurface語の直訳連結に一致する場合に警告=決定論、API 0)、(D)既存検査の整理(不要化する旧ルールの撤去)。新規LLM callを増やさない構成を優先し、増やす場合は費用と代替を明示。
- 音声・ASR側への影響(KP英語音声はKP表示形で生成されるため、一般化形=TTS入力になる。KP3V/kp_vote_check/CMU gate/5語の整合、Store reuse_key、HR)。X/Z共通部分とFamily固有部分の区別。
- 検証計画: 検証例=記事B `draw that line`+過去KPから一般化・慣用・文脈解釈が難しい事例≥15件(複数記事、X/Z)+正常KP≥30件(副作用0確認)。検証項目1〜8(ユーザー§5)。成功基準(数値)。Trial費用見込み(モデル名・最新か)。
- 70円目標への影響、不要旧ルール撤去候補。

## 3. 成果物
`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{ROOT_CAUSE_01,DESIGN_01,OPUS_REVIEW_REQUEST_01}.md`(Opus論点: 一般化の過不足/文脈意味保持/慣用句誤解釈/Std-Adv整合/既存仕様・過去Trial整合/過剰Prompt制約の副作用/より単純・低コストな方法)。commit/push(明示add、secret_scan hits=0)。

## 4. 禁止
Production/Prompt/flag/閾値変更、記事B成果物・音声・ページ変更、Trial実装(Opus後)、`er111_*`/ASR-QUALITY配下の編集、有料run。

## 5. 報告(docs/pm/RESULT_PACKET_KPGM1.md)
(1)根本原因(a)〜(e)と既存仕様が機能しなかった理由 (2)定量 (3)推奨案・代替・比較表 (4)音声/ASR側整合 (5)検証計画・成功基準・費用 (6)Opus論点 (7)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。