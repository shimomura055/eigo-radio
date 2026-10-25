# ADOPTION_NOTE_04(Trial-04。採用検討時の注意事項。DEV専用メモ。Production採用・配線は未承認)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_09 / 2026-10-25
本メモは採用が決まった場合の配線上の注意の記録であり、採用の提案・承認ではない(APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDではない)。

## 1. 配線位置と依存関係
- 英語学習テキスト解説(Part 1〜4)はProductionに存在しない(`Vocabulary & Expressions`等のGrep該当0)。新しい独立段として追加する形になる。
- Part 1: **KP確定(canonical化+gloss整合)の後**。入力はKPの英語表現のみ(案α)。本文生成・KP選定・gloss整合の既存段は変更しない。
- Part 2 Step A/B、Part 3/4: **本文最終確定の後**。Step Aは番号付き本文全体を読む。
- **本文をregen/Local Rewriteで作り直した場合は、Part 2〜4(本文依存)を作り直す**。Part 1は本文に依存しない(KPが変われば再生成)。学習テキストは本文・KPの派生物として扱い、作り直しの無効化条件(本文sha・KP一覧の変化)を持たせる必要がある。
- 呼出構成: P1 ∥ Step A → (Step B ∥ Part 3/4)。Part 3/4にはPart 1解説(R2)とStep A選定文が入る。Step AはM1(`resolve_verbatim`)で本文側の文字列に確定する。
- 既存のretry/fallback機構との整合は未設計: Trialではparse失敗時に自動再試行しない。Productionでは既存retry方針に合わせた設計が別途必要。
- **【追記 2026-10-25 委任_14】Part 1(案α)は`PART1_WIRING_*`(設計`PART1_WIRING_DESIGN_01.md`[§13〜§17=Opus条件A反映後]、証跡`PART1_WIRING_EVIDENCE_01.md`)でX/Z共通module`er003_kp_general_explanation_01.py`として配線済み(Z=`WIRED_PENDING_FABLE`・訳欄判断待ちでページ描画停止中/X=`WIRED_EXCEPT_USER_PAGE`、PRODUCTION_WIREDはFable受入後)。上記「Productionに存在しない」は配線前の記録として残す(履歴)。Part 2〜4は引き続き未配線。**

## 2. 項目4(英文の日本語訳)の生成元(未解決課題)
- Productionには「KP引用英文の独立した確定日本語訳」の出所がない。Trial-04では03d第1標本の訳を`INPUT_04.json`に固定して流用した(Beforeとの比較条件を揃えるため。評価対象外)。
- 配線時は生成元を別途設計する必要がある(例: 専用の短いLLM call、Part 1の別LLMとは独立させる)。本文背景を持つ工程でよいが、Part 2のStep Bの訳(同一英文に2つの訳が並ぶ場合)との整合はR4(参考訳)で扱っている。

## 3. gloss(本文中の意味)の品質 ― ユーザー判断候補
- Production `japanese_gloss`は本文で使われている語義を表す設計(`er003_key_words_gloss_alignment.py:149,156`)。Trial-04ではこれを項目2の確定値としてそのまま表示している。
- 例: `at a moment’s notice`のgloss「急なことにも即座に」は即応性に寄り、核の意味(予告がほとんどない)から外れる。解説(項目5)で核の意味が補われるため表示上の矛盾は出なかったが、glossそのものの質は別問題。
- glossの修正は**Production KP工程の変更**でありユーザー承認が必要(判断候補。現タスクと独立=分類C)。本Trialでは変更していない。

## 4. 現時点で採用に進めない/進める条件(Sonnet所見、判定はFable・ユーザー)
- Part 1(案α): 事前登録基準を満たす(EVAL_04 §1)。採用の技術的な障害は見当たらない。判定保留は`at a moment’s notice`の結びの即応寄り(目視確認要)。
- Part 2: 事前登録基準が未達(EVAL_04 §2)。設計見直し案(A)(B)(C)の判断・実装が先。見直しは新しい処理構造なのでOpus条件Aレビューが必要。
- 採用する場合の量産単価: 約0.46円/記事セット(70円の約0.65%)。Part 2見直し案(B)を採ると約+0.3円。
- **【追記 2026-10-25 委任_14】Part 1はユーザー正式採用(APPROVED_FOR_PRODUCTION、USER_05)を受け配線済み。Production実測=0.088〜0.137円/set(4call平均0.116円、70円比0.12〜0.20%)・+約10〜16秒。上記『at a moment’s notice結びの即応寄り』は分類C(追加Trial不要・ユーザー明示)のまま。Part 1の訳欄(T1/T2)は判断待ちで、判断記録が出るまでページへ描画しない。**

- **【追記 2026-10-25 委任_16】訳欄はユーザーがT1(専用翻訳工程)を正式承認(`..._USER_07.md`)、実装・描画有効化済み。入力=逐語照合済み引用英文のみ(gloss不使用)、実測+0.031〜0.039円/set(解説+訳 0.103〜0.139円/set)・+約4秒、Z/Xとも`WIRED_PENDING_FABLE`。X公開ページ共通builder組込み済み(既公開ページは未更新)。正確性確認=`PART1_T1_CHECK_01.md`。**

## 5. Validator/Checker
新設していない。引用逐語照合(`check_quotes_04.py`)は評価時のみの決定論スクリプトで、Pipelineに組込んでいない。M1の`resolve_verbatim`はStep Aの文を本文側の文字列に確定する構造保証であり、判定器ではない。

## 6. Trial-05追記(2026-10-25 委任_10。採用提案ではない)
- Part 2の選定は、Trial-05のStep A'(網羅タグ付け→候補ごとの絶対判定→コード規則)で拾い漏れは解消したが、層A/B判定の揺れで安定は未達(`EVAL_05.md`)。Part 2の最終設計は未確定のため、Part 2の配線設計は保留。
- **基礎項目一覧・価値側分類の最終定義は、採用提案時にユーザーへまとめて提示する**(Opusレビュー指示)。現状の暫定定義は`PREREGISTERED_CRITERIA_05.md` §2と`run_trial_05.py`のSTEPA5。肯定側`SPEC`に使役/知覚動詞が含まれ基礎項目と衝突する欠陥が見つかっており(EVAL_05 H3)、そのまま採用してはならない。
- **(B)(選定段のアンサンブル=複数回実行の集計)を採用する場合はユーザーへ開示する**: Checker/Validatorの新設ではないが、ユーザー原則に近い性質のため。n=3並列で量産単価は約1.8円/セット(70円の2.6%)、処理時間は約+35〜70秒。
- 量産単価(A'のみ)は約0.81円/セット(70円の1.2%)。Opus見込み(約0.55円)より高い(Step A'が1 call 0.51円、推論トークン支配)。

**Status(2026-10-25 Fable受入、委任_17)**: 案α+T1訳工程= Family Z・Family X とも `PRODUCTION_WIRED`(OPEN-512)。既公開ページ反映は保留(Fable判断)。Part 2〜4は未配線。
