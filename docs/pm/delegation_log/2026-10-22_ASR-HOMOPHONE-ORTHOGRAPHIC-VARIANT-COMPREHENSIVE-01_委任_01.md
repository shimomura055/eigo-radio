FABLE-DELEGATION-MARKER: ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-委任_01-20261022

管理ID: ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01(新規OPEN採番)。ユーザー指示「英語ASR 同一発音・異表記の包括対策」の第1段=**包括調査・既存機構の対応表・設計案・オフライン検証計画(+可能な範囲のオフライン検証)**。費用0(API禁止。保存音声・保存転写・ローカル処理のみ)。**Production既存ファイルの編集禁止**(並行してOPEN-458 KPQ 委任_02がer104/er078/er105/er003/er006/er019/er026/er063を編集中)。新規moduleは`er109_*`。品質原則「発音が同一なら同等、発音が異なるものは同等にしない」はユーザー承認済み。具体方式はOpusレビュー+検証後にVALIDATED→ユーザー採用判断(未承認の新仕様をProductionへ配線しない)。既存承認仕様の**不具合修正**に当たる部分は自律修正可だが、本委任では「不具合修正か新規救済範囲か」の分類まで(修正は次委任)。

## 0. 読む・保存
- `docs/pm/PM_BRIEF.md`、`.claude/agents/sonnet-worker.md`、PM_GOVERNANCE 11-3・27-7
- ユーザー原文を `docs/pm/delegation_log/2026-10-22_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_USER.md` へ見出しから末尾まで逐語保存(§6)。T-0保存 `..._委任_01.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索、本文先頭marker `FABLE-DELEGATION-MARKER: ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-委任_01-20261022` 一致で確定)。
- 直接の背景: `docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/{EVIDENCE_01,AZURE_ITN_IMPACT_01}.md`(C1〜C6)、`docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/{IMPLEMENTATION_DESIGN_01,OPUS_REVIEW_COND_A_01}.md`(①②、F1 C1技術評価)。

## 1. 既存機構の地図(file:行付き。全文読込ではなくGrep/部分Read)
英語ASR判定経路の全層を列挙し、各層が「どの表記差を同等化しているか」「どこで同一発音が不一致になるか」を表にする: `er006_secondary_asr_01.py`(統一judge、CS Equivalence層、Tier3、CMU Case A/homophone、M1、最終ANDゲート)、`er078_asr_unified_judge_01.py`/`er078_asr_value_guard_01.py`(値ガードの数詞↔数字正規化、atomizer、`soft_one`)、`er008_asr_variant_hardening_15_homophone_en.py`(homophone_en、`entity_span_arpabet_match`、代表発音方針G9)、`er011_connected_speech_equivalence_layer_production_01.py`(連結音)、`er094_multiword_homophone_01.py`(多語同音、OPEN-439)、`er006_m1_multi_candidate_01.py`(M1)、classify_asr_match本体(`val.` module)、contraction処理、`tts_safe_kp_en`、`er104_kp_three_asr_vote_01.py`(票分類: P/S/Whisperで判定原則が同一か)、Whisper票の正規化、Store再利用・X引継ぎ(`er019_family_x_validation_inheritance_01`)・Z(`er063`)の再判定入口、A/B/C共有部(27-7: 開発停止中だが共有Validator変更の互換性確認対象)。各ASR(OpenAI/Azure/Whisper)の表記整形(ITN)の既知傾向もログから整理。

## 2. パターンの体系的洗い出し(ユーザー例示は下限。限定しない)
数字↔英単語(基数・序数・年号・分数・小数・電話/時刻・`one's`型所有格)、所有格・アポストロフィ・短縮形(`it's/its`、`they're/their`、`won't`)、同音異義語・異綴語(`wait/weight`、`grey/gray`、`colour/color`、`whisky/whiskey`)、単語↔複数単語(`a lot/alot`、`every one/everyone`、`in to/into`、`work out/workout`)、略語・頭字語・記号の読み上げ(`U.S./US/u s`、`AI/A.I.`、`%/percent`、`&/and`、`$/dollars`、`+/plus`、`°/degrees`、`vs./versus`、`Mr./mister`、`Dr./doctor`、`St.`)、ハイフン/スペース/句読点/大文字小文字(`well-being/wellbeing/well being`、`e-mail/email`)、ASR各社の自動整形(数字化、単位、通貨、日付、`okay/OK`、`gonna/going to`、filler除去、`'cause/because`)、その他(同音の活用形 `passed/past`、`-ed/-t` 異綴 `learned/learnt`、固有名詞の表記ゆれは既存G9方針を尊重)。
各パターンについて: 例/発音同一性の根拠(CMU音素列一致か規則か)/既存対策の有無とfile:行/未対応の理由/対策方法案/偽PASSリスク/分類(A=既存で対応済み、B=既存承認仕様の不具合修正=自律可、C=新規救済範囲=Trial→VALIDATED→ユーザー判断)。

## 3. 保存データの実測(API 0)
全保存ASR記録(KP・非KP、X/Z、A/B/Cの保存分も対象。`review_lock_state.json`、`narration/attempts/*.json`、Store evidence、`attempt_history`はtext無しなので補助)から、NGまたはPASS_WITH_WARNINGになった行について「期待文とASR転写がCMU音素列(または規則正規化後)で一致するのに表記差でNG」の件数をパターン別に集計(母数・出典path付き)。HRに至った件数も。既知の「発音が異なるNG例」(問題音声21件、Melos母音誤読、take part B「Take Tart」等)を負例セットとして固定。

## 4. 設計案(共通照合層。Family別パッチ不可)
- 位置: 各票(P/S/W)の分類前の「表記正規化+発音同値化」層を1つ(例: `er109_asr_orthographic_equivalence_01.py`)。入力=期待文・転写、出力=同値判定+適用ルール一覧+原転写(監査)。既存classify_asr_match・homophone_en・CS層・値ガードとの接続点と、重複実装の回避(既存機構の再利用/統合)。
- 方式候補: (a)決定論の正規化(数字→語(基数/序数/年号/通貨/%/単位)、記号→読み、略語→綴り読み、ハイフン/句読点/大小文字、clitic)→(b)CMU音素列比較(token列をCMUで音素化し、連結して比較。複数発音は「いずれか一致」とするか「代表発音のみ」とするかを安全性で比較し推奨を出す。CMU未登録tokenは比較不能=同値化しない)→(c)既存の同音救済(homophone_en/多語同音/CS)との順序。値ガード(数値・否定保護)との関係: 正規化後に数値が一致すれば保護差は発生しない設計にし、「発音が異なる数値(2↔3)」は従来どおり保護。
- 監査: 判定結果・適用ルール・原転写・正規化後文字列をattempt json/evidenceへ加算的に記録。
- 適用範囲: Family X/Zの全英語ASR経路(本文・KP・解説)、retry/fallback/regeneration/resume/Store再利用/X引継ぎ、Whisper票。A/B/C共有部は互換性確認のみ(挙動差分0を要件にするか、同じ改善を受けるかはFable/ユーザー判断事項として提示)。
- ①②(OPEN-458)との整合: 独立に検証可能にする(flag/層の分離)。C1(Azure辞書形)は本方式に包含されるかを明記。
- 機械生成テスト: 保存distinct期待文(KP 656句+本文文)から異表記ペアを自動生成(数字化、記号化、clitic、ハイフン等)した正例と、発音が異なる改変(数字変更、否定脱落、語置換、音素1つ違いの最小対)の負例を作り、設計案の判定を回す(オフライン、API 0)。結果: 正例の同値率、負例の誤同値率(目標0)。
- Opus確認事項(Q形式)とユーザー判断候補(新規救済範囲の一覧)。

## 5. 成果物・SSOT
- `docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/{INVESTIGATION_01,PATTERN_CATALOG_01,DESIGN_PROPOSAL_01}.md`、集計json、`er109_asr_orthographic_equivalence_01.py`(未配線プロトタイプ+test。Production参照0をtestで固定)、機械生成ペアの検証結果json。
- 新OPEN(`INVESTIGATION_DESIGN_PENDING_OPUS`)、`docs/pm/REPORT_LEDGER.md`1行。commit(自分のファイルのみ)、secret_scan hits=0、`git push origin HEAD:main`。`docs/pm/RESULT_PACKET_AHO1.md`(4行+判定整合行)、ACTIVE_TASKは並行タスク行の追記のみ。
- 報告: パターン表(A/B/C分類と件数)、保存データの偽NG件数、設計案の要点と機械生成テスト結果(正例同値率・負例誤同値率)、Opus確認事項、ユーザー判断候補、次委任の所要見込み。

## 6. ユーザー原文(逐語保存用)
# 英語ASR 同一発音・異表記の包括対策

## 1. 目的

**発音が同一なのに、ASRの転写表記が異なるだけでNGになる問題を包括的に解消する。**

`one ⇔ 1`、`one's ⇔ 1's` は今回確認された具体例にすぎない。

同種の問題を幅広く調査し、個別例のハードコードではなく、汎用的・再利用可能な仕組みとして解決してください。

**対象はFamily X／ZのKey Phraseに限定せず、すべての英語ASR判定経路。**

ただし、現在開発停止中のFamily A／B／Cの個別開発は開始しない。共有Validator変更による互換性・影響確認は実施する。

## 2. 品質原則

- 綴り・表記・意味が異なっても、発音が同一なら同等として扱う。
- `one ⇔ 1`、`one's ⇔ 1's` を必ず含める。
- 発音が実際に異なるものを同等として受理してはならない。
- 既存の承認済み同音救済、数値正規化、短縮形、複数形、複合語等の仕様を再利用・統合する。
- すでに対策済みのものは重複実装しない。
- 安全性や品質基準を独断で変更しない。

## 3. 包括調査

既存Repo・過去Trial・Production実装・保存済みASRデータを調査し、同一発音なのにNGになるパターンを体系的に洗い出す。

特に以下を確認する。

- 数字と英単語の表記差
- 所有格・アポストロフィ・短縮形
- 同音異義語・異綴語
- 単語と複数単語の同音関係
- 略語・頭字語・記号の読み上げ表記
- ハイフン・スペース・句読点・大文字小文字
- その他、ASR各社の自動表記整形による差

これは例示であり、調査対象をこの一覧に限定しないこと。

既存のCMU発音辞書、同音判定機構、その他の承認済み発音照合方法を活用する。

各パターンについて、既存対策の有無・未対応の理由・対策方法を整理する。

## 4. Opus独立レビュー

**Opusによる独立レビューを必須**とする。

特に次の点をレビューする。

1. 想定される同音異表記パターンに重要な漏れがないか。
2. 既存Validatorのどこで同一発音が不一致になっているか。
3. 提案する一般化が既存の同音救済機構と整合するか。
4. 正常音声の偽NGを十分に削減できるか。
5. 発音の異なる音声を誤PASSしないか。
6. Family X／Zおよび共有ASR経路のretry／fallback／resume／Store再利用に漏れがないか。
7. 不要な追加APIや量産コストを発生させないか。

Opusの指摘はClaude／Fableで解消し、必要な場合は設計を再検討すること。

## 5. 実装・検証

今回すでにAPPROVED_FOR_PRODUCTIONとなっている次の2項目と整合させる。

① Key Phrase音声の数値・否定保護解除  
② CMU未登録語をKey Phraseに選定しない

今回の包括対策は、上記①②とは独立して検証可能にする。

**原則として共通Validator／共通音声照合層で対応し、Family別の個別パッチを増やさない。**

最低限、以下を確認する。

- `one ⇔ 1`、`one's ⇔ 1's` が同等に扱われる。
- 既存保存音声で同一発音の表記違いによる偽NGが解消される。
- 発音が異なる既知のNG例はNGのまま。
- OpenAI／Azure／Whisperの各票に同一の判定原則が適用される。
- Key Phrase以外の英語音声でも動作する。
- retry／fallback／regeneration／resume／Store再利用にも適用される。
- 判定結果、適用した同音ルール、原転写を監査できる。
- 既存Production品質Gate・Regressionが維持される。

網羅性を高めるため、既存データに加えて機械生成した異表記ペアによるテストも活用する。

検証はできる限り保存音声とローカル処理で実施し、不要なTTS・ASR API費用を発生させない。

## 6. 承認境界・Status

本指示により、包括調査・Opusレビュー・設計・必要な検証を承認する。

**同一発音を同等に扱うという品質原則はユーザー承認済み。**

ただし、具体的な包括判定方式には未確認の品質リスクがあるため、Opusレビューと検証で安全性を確認する。

既存承認済み仕様の不具合修正に該当する部分は、自律的に修正・検証してよい。

新しい同音救済範囲や既存安全Gateの判定変更に該当する部分は、Trial成功時点でVALIDATEDとして報告し、Production採用判断をユーザーに求める。

未承認の新仕様を正式Productionへ配線しないこと。

既承認の①②については、この調査を理由に不合理に停止させず、独立してProduction Wiringを進める。

## 7. 完了報告

以下を簡潔に報告すること。

1. 発見した異表記パターンと対策状況
2. 既存機構で対応済み／新規対策が必要なものの区別
3. 保存データにおける偽NGの改善件数
4. 偽PASSが増えていない証拠
5. Opusレビュー結果と是正状況
6. Family別・経路別の適用範囲
7. Production Wiring状況と未完了事項
8. 開発費・量産単価への影響
9. SSOT／Git反映状況
10. ユーザー判断が必要な新仕様だけを抽出

品質を守りながら、最小限の追加コストと最短Deliveryで進めること。

**今回の問題を個別例の修正だけで終わらせず、同種の偽NGを構造的に防ぐことを最優先とする。**