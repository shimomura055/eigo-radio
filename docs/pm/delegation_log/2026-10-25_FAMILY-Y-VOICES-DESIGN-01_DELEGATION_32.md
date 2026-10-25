FAMILY-Y-VOICES-DESIGN-01 委任_32(Round 2 準備・**API 0**): Closing一般化PromptのP1〜P5改訂と事前登録。有料生成は本委任に含めない(日次1,000円の残が約39円のため、Round 2の生成はJST日付変更後にFableが別委任で起動)。DEV/Trial専用、Production変更禁止。

## 前提
`docs/research/FAMILY-Y-VOICES-DESIGN-01/CLOSING_GENERAL_01/{TRIAL_RESULT_01,EVAL_01,PREREGISTERED_CRITERIA_01,OPUS_REVIEW_01,DESIGN_01,BUDGET_LOG_01}.md`、`prompt_closing_general_01.txt`(sha fd3dc62e…)、`er110_family_y_closing_general_trial_01.py`+test(23件)。Round 1結果: 4生成(宅配gen_1/gen_2、SNS gen_1/gen_2)、実費67.04円(ユーザー承認200円枠、残132.96円)。

## Fable独立評価(Round 1、TRIAL_RESULT_01 §B「Fable評価」欄に転記。文言は整えてよいが判断は変えない)
- 総合: **方式の実現性はVALIDATED(限定)**=人手の切り口設計なしで、2テーマとも3人の語りに根拠を持つ新しい見方を自力で選定・執筆できた(根拠引用81/81逐語一致、創作0、「人によって違う」型・勝敗型・「〜ではなく〜だ」型0/4)。ただし完成度のばらつきが大きく、Production採用の提案段階ではない。
- 作品別: 宅配gen_2=良(V3の言葉から入り「努力を採点するように聞こえる」とV2の不在票を対置、最後の問いが聞き手の体験に具体的に結びつく。案B/Cと同水準。「時間を空けて待った」はV2の語りよりやや強い言い換え)/宅配gen_1=弱〜中(切り口は妥当だが「声があった」「話もあった」の出所曖昧、最後の問い「払う前に何を知っておいてほしい？」の主語・相手が不明)/SNS gen_2=中〜良(「自分で使うこと」と「一人で危険を引き受けること」の区別、「危ないと気づく役目を任せる時期」は語りから自然に出た新しい見方。問いの「動画選び」はやや唐突、「声をかけてほしい」の主語が曖昧)/SNS gen_1=弱(3〜5文が抽象的で耳で追いにくい。問いの相手が不明)。
- 偏り: 問いが4/4「もし〜なら、どんな〜をしたい/してほしい？」型、推量語4/4、逆接4/4=型の収斂あり(品質問題未満だが是正対象)。選定が4/4中3件で候補A(並び順先頭)=順序依存の疑い。
- 安定性: 宅配は焦点が分かれ、SNSは収斂。gen_2が両テーマで良いのは偶然の可能性があり、Round 2で再確認。
- Gate: `leak_tension_reverts_to_research`は4/4 PASS(Opusが懸念した誤FAILは今回出ず)。宅配gen_1の`leak_evidence_subject` FAILは(a)本文側の課題=妥当なFAIL。
- 単価: 1生成+判定 平均16.8円(70円比約24%)=要低減。effort=medium比較をRound 2に含める。
- 2段階化=不要(事前登録ルールどおり0/4)。

## Round 2 設計(Fable決定: 次ラウンド案2を採用)
- Prompt改訂 P1〜P5(TRIAL_RESULT_01 D-5): P1 出所の曖昧な表現禁止(「〜という声があった」等。人物は役割で指す) / P2 最後の問いは「誰が誰に」答えるかが聞いて分かる形(聞き手自身への問いとして主語を明示) / P3 推量語・逆接の型の抑制(推量語は1文まで、「けれど/ただ」の定型的な使用を避ける。問いの型を固定しない=「もし〜なら、どんな〜」以外の形も可と明示するが型を列挙しない) / P4 語りより強い言い換えをしない(語りの事実の範囲で述べる) / P5 Prompt文言と決定論検査の整合(字数190〜230・1文45字以内・「」の扱いを検査側と一致させる。検査を緩めない方向で、Prompt側を検査に合わせるか検査をPromptに合わせるかは理由を書いて決める。品質基準の引き上げにならないよう旧規則水準を維持)。候補の並び順依存対策として、選定時に候補を提示順と無関係に評価する旨は既にあるため、追加で「selection_reasonに各候補の順位付け理由」を書かせる最小変更のみ。
- 新Prompt=`prompt_closing_general_02.txt`(01は残置)、sha固定test更新、記事固有語0 test、入力ブロック以外同一test、旧表現撤去test(P1〜P4の禁止語句)。
- 実行計画(Round 2、別委任で起動): (a) Prompt 02 × effort=high × 2テーマ×2生成(見積約55〜80円) + (b) Prompt 02 × effort=medium × 2テーマ×1生成(見積約17〜24円)。合計約72〜104円、残枠132.96円内。guardのGEN_EST_JPY=20(high)/14(medium)。effort切替をCLI引数で指定可能にし、gen_metaにeffortとPrompt shaを記録。
- `PREREGISTERED_CRITERIA_02.md`: Round 2の評価基準(Round 1と同じ手順+追加: 問いの型の多様性[4本中の型の種類数]、推量語・逆接の出現、出所曖昧表現0、主語明示、high vs mediumの品質差の見方[同一Prompt・テーマで比較、mediumが同等ならC優先で採用候補])。Status判定: VALIDATED=Round 2で4本中3本以上がFable「中〜良」以上かつ型収斂が改善。
- `DESIGN_01.md` §9に改訂履歴(01→02、根拠=Round 1評価)。`BUDGET_PLAN_02.md`。

## 実施
1. TRIAL_RESULT_01 §B Fable評価欄へ上記転記、§D Status=VALIDATED(限定: 方式の実現性。Round 2で品質安定化を検証)。
2. Prompt 02作成+test更新・実行(全PASS)。module改修(effort CLI、GEN_EST_JPYのeffort別)+test。
3. PREREGISTERED_CRITERIA_02.md、DESIGN_01 §9、BUDGET_PLAN_02.md。
4. `OPEN_ITEMS.md` OPEN-463 行を更新(Round 1 VALIDATED(限定)・Round 2準備済み・有料実行はJST日付変更後。1行、直前再Read・最小Edit)。`docs/pm/ACTIVE_TASK.md`。
5. 委任文逐語 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_DELEGATION_32.md`(N=565〜600を走査、冒頭「FAMILY-Y-VOICES-DESIGN-01 委任_32」。`--index -1`不可)。
Git: 禁止=`git add -A/-u/-f`、amend/rebase/force push/stash/clean/reset/checkout -f/`git checkout -- <file>`。対象pathのみ `git commit --only`→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`[競合は両方残す]→push)。secret grep 0件。並行agent稼働中。
報告: Prompt 02の差分要約(P1〜P5の文言)、test結果、Round 2の起動コマンド(Fableが翌日に使う)、commit hash・raw URL(prompt_closing_general_02.txt、TRIAL_RESULT_01.md)、RESULT_PACKET 4行。