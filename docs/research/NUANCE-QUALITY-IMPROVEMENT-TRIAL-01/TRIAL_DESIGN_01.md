# TRIAL_DESIGN_01: ニュアンス解説の品質改善Trial(NUANCE-QUALITY-IMPROVEMENT-TRIAL-01 委任_01)

到達Status上限=VALIDATED。DEV/Trial専用。Production Prompt・関数・runnerは未編集。正本原文=`docs/pm/delegation_log/2026-10-29_NUANCE-DISPLAY-ORDER-AND-HR-PRECHECK-01_USER.md` §4(L82-166)。

## 1. 現状調査(現行ニュアンス生成の仕様、file:line)
- 生成Prompt: `er134_nuance_explanation_01.py:90-165` `PROMPT_GEN`(v3)。最大1件。入力=本文・暫定選定KP・提示pool最大12件・文法Top2(`build_inputs` :319)。焦点例(a)近い表現との使い分け (b)文脈で変わる印象 (c)確信度・態度 (d)日本語訳の落とし穴。4条件(文脈性/日本語話者の落とし穴/レベル適合/非重複)すべて満たす場合のみ候補、迷えば0件。
- 出力schema: `:122-152`。candidate={expression, focus, quote_en(本文逐語1〜2文), quote_ja, explanation_ja, differs_from_kp_word_ja, criteria_check, learning_value_self_rating, learning_value_reason_ja}。必須=`_CAND_REQ`(:622)。explanation_jaは**Promptで120〜260字**(:148)、検証は60〜700字(:50-51, :625以降)。
- 現行Promptの「何をどう書くか」の指示は`explanation_ja`の1行(:148)のみ=「比較する表現・場面を最低1つ具体的に示し、何がどう違うか(語感・印象・使い分け)を書く」。比較英文の提示・要点の書き方の指定は無い(=出力が意味の言い換え中心になりやすい原因の仮説)。
- QA Gate: `quote_check`(:477 本文逐語)、`structural_check`(:423 KP・poolとの語の重複、段1)、`judge_overlap`(:731 別callのLLM重複判定、段2)、`decide`(:758 verdictを決定論算出)、self_rating!=highは決定論で0件(:678)。いずれも`run_candidate`(:848)内。
- レベル別: `LEVEL_NOTE`(:198-203) Standard=A2目標英文/学習者A2〜B1、Advanced=B1目標英文/学習者B1〜B2。件数=各level最大1件(`generate_candidate`は`candidate`単数)。
- 下流: 採用候補はsidecarへ固定項目(expression, focus, explanation_ja, quote_en, quote_ja, sha)だけ転記(`er120_part2_wiring_01.py:578-593`)。**追加fieldを採用する場合は、この転記・HR提示・ページ描画の拡張が必要(Production変更。本Trialでは行わない)**。
- 現行出力例(Y姓記事): Std=`at least a little`(「…最低限のラインを示し…控えめに伝えています」144字)、Adv=`at least`(…。`er121_output/family_y_production_01/surname_choice/run_02/{a2/,}study_text/nuance_candidate.json`)。

## 2. 改善Prompt案(Trial専用コピー。`tools/nqt01.py` NEW_TAIL → `nqt02.py` v2 → `nqt05.py` v3)
Production Promptの「手順」節以降を差し替える形(前半=記事・KP・役割分担・4条件・選ばないものは現行と同一=既存仕様・Gate・本文根拠を維持)。
- 方針1〜6の反映: (1)単なる意味説明を禁じ「使い分け・文脈による変化」の発見を求める (2)comparison型=本文の1文を最小限書き換えた似た英文を並べ、各訳+違い (3)context型=比較が不自然なら比較なしで文脈・話者意図・効果を説明 (4)個数は固定せず2〜4個(本文の文を必ず1個含む) (5)自然で正確な比較も文脈説明も作れないなら0件(手順3-4に明記) (6)レベル別(Std: A2〜B1語彙・2〜3個・平易/Adv: 語感・含みの細かい差・2〜4個)、quote_en本文逐語・4条件・非重複・self_rating・既存QA Gateは不変。
- v1→v2(独立監査の観察への対処1回目): 比較が「有無の二項」に偏る→差が段階/選択肢で見える並びを優先。説明冒頭が「〜と訳すと」の定型化→禁止。
- v2→v3(同2回目): 独立監査で「強い感謝を求めない」「譲れない条件」「意図せず」等の**表現の意味を超えた断定**が複数案で再発、1案に本文にない事情の補完(逸脱)→断定禁止・事情補完禁止・point/比較/解説の重複回避を追加。
- 比較: 同じ修正の反復ではなく、観察された欠陥の種類ごとに規則を変えた(v2=構造、v3=正確性)。v3後は改善が飽和(下記RESULT)と判断し停止。

## 3. 出力schema案の比較
| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| A: 既存schemaのまま(explanation_jaに比較を文章で含める) | 下流変更0 | 比較(A/B/C+訳+差)が1つの文字列に埋まり、HR・ページで構造表示できない。字数が700字上限に近づく |
| **B(Trialで採用): 既存fieldを全て維持+追加** | `point_ja`(ポイント1文)、`comparison_type`(comparison/context)、`comparisons[{label,en,ja,note_ja,is_text}]`、`explanation_ja`=「ここが重要」要点 | 構造検査(本文の文を1個含む・個数)が機械化でき、ユーザー参考例(ポイント→比較→ここが重要)をそのまま描画できる。explanation_ja単体でも従来どおり成立(後方互換) | sidecar転記・HR提示・ページ描画・重複判定入力の拡張が必要(採用時のProduction変更) |
結論: B推奨(採用時は拡張が必要な点を明示)。重複判定(`judge_overlap`)は現行形のままexplanation_jaのみ参照して動作したが、採用時はcomparisonsも判定入力に含める要否を検討。

## 4. 評価軸と判定基準(ユーザー原文§4 Trial実施方針に対応)
| 軸 | 判定(○/△/×) | NG条件 |
|---|---|---|
| 学習価値 | ○=具体的な英文比較/文脈説明により使い分け・文脈変化が分かり新しい発見がある。△=正しいが言い換え中心。×=学習価値なし | — |
| 正確性 | ○=英語用法・比較文・訳が正確。△=断定が強い等の軽微な過剰。×=誤り・不自然な比較英文 | 比較例が不自然/不正確 → 品質NG |
| 自然さ | 日本語解説・英文・訳の自然さ | — |
| 逸脱 | 本文にない事実・事情を補っていないか | 本文逸脱 → 品質NG |
| レベル差 | Std/Advで語彙・長さ・難度に差があるか | — |
評価者: (a)独立監査=gpt-6.1-sol(生成と別モデル・上位。匿名化・順序シャッフルして1〜5採点+指摘)、(b)筆者(Worker)の確認、(c)Fable独立評価(後続)、(d)最終はユーザー。
合格目安(VALIDATED案): 改善版が現行版を学習価値で上回り(監査平均+0.5以上)、正確性が同等以上、逸脱0〜(再発1件以下)、QA Gate通過、費用増が70円目標に実質無影響。

## 5. 対象と条件
- 対象: Y姓記事(Std/Adv)、X「AIの島」(Std/Adv)、Z「告げ口心臓」(Std/Adv)、Y「再配達料」(Std/Adv)=3 Family・4記事・8セル。X「月」候補はdoc/Trial入力が整っていた公開済みX記事(AIの島)で代替(入力組立が確立済みのため)。
- 各セルで: 現行(CUR)=現行Prompt+現行parse/重複判定を実行、改善(自由選定)、改善(同一表現固定=現行が選んだ表現。Y姓はStd=`at least a little`/Adv=`at least`)。Y姓はv3固定を各levelで3回再生成し再現性も確認。
- 入力同一(同じ`build_inputs`出力)、モデル同一=`gpt-6-luna`(`er006_model_routing_contract_01.py:50` SUPPORT_MODEL=現行Production route)。QA Gate(`run_candidate`)は現行関数を入力・出力とも変更せず参考実行(readのみ)。
- 費用上限¥40(独立監査込み)。

## 6. 記録方針
生成物・raw応答・usage(token/秒/円)=`out/`(`usage_log.jsonl`、`raw/`、`<cell>_<COND>.json`、`*_AUDIT*.audit.json`)。比較ページ=`user_test/nuance_quality_trial_01/index.html`(`tools/build_page.py`で再生成)。
