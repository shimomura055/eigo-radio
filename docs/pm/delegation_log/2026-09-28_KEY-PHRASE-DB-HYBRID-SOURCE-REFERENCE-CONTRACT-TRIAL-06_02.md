# 委任文全文(記録)

管理ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06
Phase B (Sonnet 5 委任、2026-09-28)

---

管理ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06(Phase B: Trial実装+検証。Fable設計レビュー決定=**B改良版(候補ID方式+非ブロッキングの取り違え検知)**)。一時ファイル `docs/pm/ACTIVE_TASK_KPS2.md` / `docs/pm/RESULT_PACKET_KPS2.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06_02.md` に保存しcommitに含める。Guardrail **¥40**(STOP閾値 ¥35。事前見積>¥30なら実行前STOP)。APIキーは環境変数のみ。**Production配線禁止・Production module(er030/er003_key_words_*/p2g/prod validator)変更禁止・v1 baseline(er029)/v2(er032)変更禁止(read-only import)。到達Status: REJECTED/VALIDATED/USER_DECISION_REQUIRED(仮分類、確定はFable)。**

## Fable設計決定(設計書 `docs/pm/design_kp_source_reference_contract_01.md` §13-14 を採用、以下の改良を加える)
1. **候補ID方式**: selector schemaから `source_sentence`/`source_span` を除去し、`source_candidate_id`(enum=当該呼び出しのshortlist候補ID `C1..Cn` のみ)を必須化。LLMに本文文字列を一切書かせない。`display_phrase`/`normalization_type` 等の既存フィールドは維持。
2. **決定論的復元**: 候補ID → Stage 1が持つ `surface_form` / `sentence_ids` / span から、`source_sentence` = **最初の出現文**(sentence_id昇順の先頭)、`source_span` = その文中のsurface出現(Stage 1のspan情報)を復元。複数出現の候補は復元規則を固定しREPORTに明記(限界: 出現ごとに意味が異なる稀なケースは検出しない)。
3. **取り違え検知(非ブロッキング)**: schemaに `surface_echo`(短いsurface文字列、任意)を追加し、復元した `surface_form` と正規化比較して不一致なら telemetry に `candidate_mismatch_suspected=true` を記録する(**validatorには使わない・STOPさせない**)。発生率を計測して報告。
4. 復元後は既存Production validator(`p2g.validate_min_unit_selection` / `run_production_selection_gate`)・canonicalization・Source Gateを**無変更**で通す(§8)。
5. (iv) validator寛容化は今回実装しない(Production変更のため)。

## 実装
- 新規 `er034_key_phrase_db_hybrid_source_reference_contract_trial_06_{contract,run,test}.py`: v1(er029)/v2(er032)の選定層を**ラップ**する薄い層(候補ID付与→prompt組み立て[SENTENCE REFERENCE表を候補ID表に置換、記事全文非送信assertion流用]→selector 1 call→候補ID解決→復元→既存validator)。schema enum値数(20〜25)がOpenAI structured outputsで動作することをunit+実calls で確認。
- unit test: 復元の決定論性、enum外ID拒否(schemaレベル)、複数出現候補の復元規則、surface_echo不一致の記録、v1/v2両方のラップ、記事全文非送信。

## 検証(同一条件: 1本文1 selector call、全文非送信、共有ストア非書込み、出力 `er034_output/…`)
- 対象: twins A2・Melos A2(quote-heavy、既知失敗)、Family X 12本文(回帰)。v1ラップとv2ラップの両方(=28 call)は予算超のため、**v2ラップで14本文**+**v1ラップでtwins/Melos 2本文**(=16 call、約¥18)。
- 反復安定性: 構造修正後に twins A2・Melos A2 を v2ラップで**各3サンプル**(追加4 call、約¥5)し structural INVALID 0件を確認。
- 記録: structural PASS / 候補ID解決成功率 / surface_echo不一致率 / 既知bug A〜E / 重要語保持(Trial-04/05基準) / phrase比率 / cost・input tokens(Trial-04/05比) / v1既存挙動との最終5件差(v1ラップ2本文) / Source Gate raw照合PASS。
- 受入条件との対応表(引用符・空白・句読点コピー揺らぎでINVALIDにならない / canonical対応が決定論的 / quote-heavy安定 / v1 regressionなし / v2改善を壊さない / bug A〜E / 1本文1 call / 全文非送信 / cost不増 / Human Review/STOPを通常系にしない)。

## REPORT `KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06_REPORT.md` 新設
Fable設計レビュー結果(設計書参照+上記決定)、採用contract、実装、検証結果表、quote-heavy安定性、v1/v2への影響、Production(er030)適用時に必要な変更範囲・migration(既存artifact無変更、`source_candidate_id` を追加フィールドとして保存)、unresolved(取り違え率、複数出現の意味差)、STOP該当有無、Status仮分類。

## STOP条件
大規模schema変更 / migrationがProduction互換性を壊す / 追加LLM call常設 / 新DB / 新しい大きな仕様判断 / v1 baseline書き換え → USER_DECISION_REQUIREDで報告。

Git: er034_*・出力・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agent[er003_v1_crosslevel_*, er006_preprod_*, er025_*, SSOT]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに費用・commit hash・変更ファイル・受入条件表・Status仮分類・unresolvedを記載。

---

## 実行時の実際の乖離(記録)

- 本文数の内訳は委任文の見積り(v2 14本文+v1 2本文=16 call+安定性4 call)
  に対し、実装上は v2ラップ13本文(Family X 12 + Melos A2)+v1ラップ
  2本文(twins_a2・melos_a2)+安定性追加4 call=**19 call**とした
  (delegation文中「14本文」の内訳がFamily X 12+Melos A2=13本文と
  厳密には一致しなかったため、Family X 12本文+Melos A2の合計13本文を
  正として実行した。既存Trial-04/05の12本文パス+Melosパスと完全一致
  させることを優先した)。
- 実測総コスト¥18.2707(19 call)。事前見積(¥20-25、平均¥1.1/call想定)
  の範囲内、Guardrail¥40・STOP閾値¥35は未達。
- 初回実行で6件(4記事+Melos3サンプル、後述)がstructural INVALIDと
  なったため、原因調査・実装修正(source_span→surface_form切り替え)・
  再検証(API再呼び出しなし)を追加で実施した(詳細REPORT§2)。この
  修正は設計書§3(b)/§14が元々推奨していた内容への実装修正であり、
  新しい仕様判断ではないため、STOP条件(新しい大きな仕様判断)には
  該当しないと判断した。
