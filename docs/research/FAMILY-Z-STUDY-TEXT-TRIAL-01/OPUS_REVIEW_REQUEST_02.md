# OPUS_REVIEW_REQUEST_02 (条件A: 新しい構造・処理フローの設計) — FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_08 Trial-04

依頼元: sonnet-worker(Fable経由で送付)/日付: 2026-10-25/読み取り専用レビュー。Opusは実装・Production採用可否の宣言をしない(`docs/pm/PM_GOVERNANCE.md` 11-3)。有料生成(Trial-04本番)はこのレビュー後のFable Goまで行わない。

## A. 依頼の背景(要点)
英語学習テキスト解説(DEV専用、Production未配線)のPart 1・2について、ユーザーは2026-10-25に「後段のCheckerを新設せず、上流設計(入力の切り分け・責務分離)で品質を改善する」Trial-04を承認(原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_04.md`)。Trial-03(03d、1 call一括)の課題:
- Part 1: 本文背景に引っ張られ、本文中の意味を表現の代表的な意味のように説明する(give wayの字義、at a moment's noticeの核の欠落、nutrient-rich crystalsを定型表現扱い)。
- Part 2: 選定・構文分析・執筆が一工程のため、基礎文法を選ぶ/難所を見落とす/説明が形式的/開発者向け選定理由がユーザー向けに混入(`whose`だけの解説、0件と1件の標本間揺れ)。

## B. 読んでほしいもの(この順)
1. `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/DESIGN_04.md`(設計・案比較・費用)
2. `PROMPT_04.md`(各工程のPrompt全文)・`run_trial_04.py`(工程接続、`p1_prompt`/`stepa_prompt`/`stepb_prompt`/`p34_prompt`/`run_pipeline`/`assemble_user`)
3. 比較基準: `PROMPT_DIFF_03d.md`・`OUTPUT_03d_*_RAW.md`・`FABLE_EVAL_03.md`・`EVAL_03.md`
4. 確認用: `dryrun_04.json`(Prompt長・sha・Part 1混入確認結果=3作品とも0件)、`_prompt_04_*.txt`

## C. 論点(a)〜(f)
**(a) Part 1の入力切り分け**: 案α(KP英語表現のみ)を主、案β(KP+本文での日本語意味)を比較腕とする設計が、「本文に引っ張られない」と「本文中の意味との矛盾なし」を両立するか。βのgloss(例「崩れる」)が字義へ引きずる懸念への緩和(Prompt文言)で足りるか。αで多義語(give way等)の意味取り違えが起きた場合の事前登録ルール(矛盾1件以上でβ採用候補)は妥当か。複合表現の「中心語句」をLLM判断に任せる(人手指定しない)方針に問題はないか。
**(b) Step A/Bの責務分離とschema**: ①`reason_dev`・`candidates_considered`をStep Bに渡さない設計で、開発者情報混入を上流で防げているか。②`context_ja`(本文中の位置づけ1文)をStep Bに渡す点は、「入力=選定英文+構文のみ」という分離の趣旨(本文背景の排除)と矛盾しないか、また表現効果の質に必要か。③Step Aの選定観点(基礎文法を埋め草にしない・0件可・上限2)で、基礎文法選定・倒置/後置修飾の見落としを上流で防げるか、`candidates_considered`は見落とし評価に十分か。④0件判定の置き場(`selected=[]`→Step Bを呼ばず固定文表示)は適切か。固定文の文面をProduction化時にどう扱うべきか。
**(c) 既存Production KP gloss(X2p')との重複・将来の配線位置**: 「本文中の意味」にProduction `japanese_gloss`(`er003_key_words_gloss_alignment.py:95`)を確定値として使い、`meaning_in_text_en`(:128、本文文脈由来)は別LLMに渡さない設計に、重複・矛盾・見落としがないか。学習テキストの配線位置(KP確定後の独立段)の見立てに問題はないか。
**(d) 呼出増(1→3〜4)の費用対効果と量産単価**: 推定 +0.2〜0.5円/記事セット(約0.7〜1.1%/70円)、処理時間+約20〜30秒の増加に対し、品質改善(Part 1の本文非依存、Part 2の選定安定)が見合う設計か。呼出削減案(Part 3/4をStep Aと同一call、等)を今回採らない判断は妥当か。Part 3がPart 1解説文を見ずKPリストとStep A選定文のみで重複回避する点の影響(Part 3重複リスク)をどう見るか。
**(e) 再現性評価N=2で何が言えるか**: 3作品×N=2で、Part 2の選定判断(0件/どの文)の一致観察から何を主張でき、何を主張してはならないか。βは1セットのみ(P1だけ)の比較で足りるか。
**(f) Validator新設なし・既存資産の再利用**: 新設Checker/Validatorがなく、評価時の逐語照合(`check_quotes_04.py`=check_quotes_03流用)とdry-run内のPart 1混入確認だけであることの確認。parse失敗時に自動再試行しない設計に問題はないか。Part 3/4ブロックが03dと完全一致(assert)である点の確認。

## D. 求める出力
- 論点ごとの所見(問題なし/修正必須[具体的な修正案]/推奨事項)と、有料Trial(約3.5〜5.1円、24 call+β腕3 call)へ進んでよいかの意見。
- 設計上の見落とし(特に、上流設計だけで防げない失敗モードがないか)。
- Opusは修正を実装せず、所見のみ返す(実装・再配線はFable判断で委任_09以降)。

## E. 参考(制約)
- 禁止: Production code/Prompt/flag変更、Checker/Validator新設、KP追加選定、音声生成、Web検索、Part 3/4 Promptの変更、API呼出(Phase 0)。
- モデル=gpt-6-luna(Trial-01〜03と同一、最新世代)。Part 3/4・出力形式はTrial-03の現行Promptのまま。
