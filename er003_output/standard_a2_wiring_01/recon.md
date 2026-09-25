# recon.md — NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01 STEP 2偵察結果

事実列挙のみ(変更なし)。

## (a) 日本語Entertainment R2(Original→R1→R2)のProduction入口の有無
`CURRENT_SPEC.md` L828(News記事[日本語Entertainment読み物]のEntertainment生成方式)に
明記: 「配線先Production経路: 未確定(2026-09-24 Phase 0 recon: 日本語Entertainment
読み物記事[本方式]を生成する既存Production経路はCURRENT_SPEC上に存在しない[該当なし]。
...新規Production module設計要否はFable/ユーザー判断待ち)」。
→ **存在しない**。Status = `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`。

## (b) Advanced Natural Adaptation(CEFR B1)のProduction実装の有無
`Grep pattern="Natural English Adaptation|adaptation|advanced_natural|standard_a2" -i
glob="er0*.py"` の一致は以下7ファイルのみ、すべて`er015_*`(Trialスクリプト):
- er015_news_standard_a2_vocab_6000_cutoff_trial_01.py
- er015_news_standard_a2_vocab_banding_trial_01.py
- er015_news_standard_a2_vocab_effectiveness_trial_01.py
- er015_news_standard_a2_prompt_v2_trial_01.py
- er015_news_natural_advanced_standard_a2_trial_01.py
- er015_news_ja_to_en_adaptation_trial_01.py
- er012_editorial_b_family_production_phase1_test_01.py(誤検知の可能性、Family B
  Editorialの既存テストファイルで別文脈の"adaptation"一致と推定、詳細未確認)
→ Advanced自体のProduction module(er003/er012系)は**存在しない**。
OPEN-177(1)の記載と一致。

## (c) 記事→scaffold/TTS/assembleが要求するProduction contract
`er003_v1_n3_01_articles_generate.py` COMMON_BLOCK_TEMPLATE(英語A2/B1 News Writer
経路)は「1. Title(#見出し) 2. Main Story 3. `###`見出しをちょうど2つ 4. In One Line
相当の結び」という固定contractを要求する。
これに対し、Standard A2 v5 Prompt(Entertainment英語適応Family)は
「Output only the English title and the English body.」という単純contract
(Title行+本文のみ)であり、`###`小見出し2つやIn One Line構造を要求しない。
→ **両Familyのcontractは異なる**。Standard A2をNews Writer経路のscaffold/TTS/
assembleへそのまま接続することはできない(別のAudio/Assembly設計が必要)。

## (d) retry/fallbackの経路とPromptの一元管理方法
`er003_v1_en_direct_vfl_01_generate.py`(vfl01)の`run_writer_no_search()`/
`run_writer_with_technical_retry()`が、英語Writer系全体(News A2/B1、Discovery
Focus、Standard A2含む)で共有されるretry primitiveである。
`er012_b_family_production_runner_01.py`・`er003_v1_n3_01_articles_generate.py`
・`er003_discovery_focus_staged_production_01.py`・`er011_discovery_focus_s2_full_trial_01.py`
がいずれもvfl01をimportして使用している。
fallbackモデルは`er006_model_routing_contract_01.PROCESS_MODEL_MAP`に定義が無い
(News A2/B1 Writerもfallbackなし)。

## (e) Key Words/Phrasesの抽出元と役割
`er003_v1_n3_01_scaffold_generate.py`の`run_key_phrases()`/`run_key_phrase_selection()`
が記事本文(article_text)からKey Phraseを選定・正規化・redundancy QAする。
Standard A2生成とは独立した後段工程であり、どちらの記事本文(Advanced/Standard)を
入力するかは、Standard A2 Production経路が確定した時点で判断する必要がある
(本タスクでは未接続のため実接続テストはしていない)。

## 結論
(a)(b)がともに存在しないため、STOP条件(「Advanced Natural→Standard A2の正式
初回経路が存在せず、経路の設計[入口・Production contract付与・downstream接続]
に仕様判断が必要」)に該当する。経路設計はFable/ユーザー判断待ちとし、本タスクでは
行わない。STEP 3のProductionモジュール実装(`generate_standard_a2()`)は
「どのrunnerからも呼ばれていない未接続の単一責務関数」として実施し、Gate 3
チェックリストでは該当項目を×として記録する(詳細は`gate3_checklist.md`)。
