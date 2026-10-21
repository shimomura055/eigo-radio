# 中核数値(134,515 people)調査 CORE_NUMBER_QUERY_01

管理ID: FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_07(調査のみ、API 0、コード/仕様/成果物変更なし)
ユーザー原文: `docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_CORE-NUMBER-QUERY_USER.md`
記事Aの実データ: `er019_output/paycheck_personality/run_pp_01/`(以下 RUN)

## 結論
**Yes。`134,515人`は実装上の「中核数値(`【中核数値】`印)」として決定論的に選ばれている。** 印を付けたのはAI(LLM)ではなく、B3直後の決定論producer(`er053_b3_deterministic_producer_01.py`、LLM call 0、`annotation_manifest.json:21 "llm_calls":0`)。ユーザーの言う「中核数値」と実装用語`【中核数値】`は同一概念(Writerが記事に書いてよい数字の許可印)。

## 1. 134,515の追跡(層ごと)
| 工程 | 扱い | 根拠 |
|---|---|---|
| Ledger | F04に「最大134,515人」。`numeric_value`欄に「最大134,515人」、notes_for_writerに「134,515人がすべてのモデルに参加した」と書かない | RUN/research_ledger/verified_fact_ledger.txt:19-24 |
| B3 Fact選定(LLM gpt-6.1-sol) | F04を採用(Test3=YES「証拠基盤と最大標本数の正確な理解に必要な例外」)。**ここで選ばれたのはFact(F04)であり数値ではない**。採用ID=[F02,F04,F07,F08,F15] | RUN/storyline_b3/fact_selection_evidence.json(fact_tests F04、selected_fact_ids) |
| 決定論producer(数値印) | `最大134,515人`・`134,515人`は同一概念C2として`class: core`。注記済みbriefの【事実2】に`134,515人【中核数値】` | RUN/storyline_b3/annotation.json(numbers[1],[2])、selected_brief_annotated.md:8 |
| 注記検査 | a_alignment/b_numbers/c_core_peripheral/d_tags/e_sidecar 全PASS | RUN/storyline_b3/annotation_manifest.json checks |
| W-1 R0(Fact Lock、gpt-6.1-sol) | 中核印の数字だけ使える規則(5)に従い、「最大134,515人」を記載。印は本文に残さない | er053_family_x_factlock_ja_writer_01.py:86-93、RUN/ja_writer/factlock/r0.md:5 |
| R1/R2 | 逐語維持。**R1/R2のPrompt(USER_TMPL)に数字規則は無く**(「事実は変えずに…」のみ)、維持はモデルの挙動。数値に対する決定論Gateは無い(周辺数値を書いた場合のGate化は不採用、DECISION_LOG.md:20547)。結果として全段で134,515が一致 | er053_family_x_factlock_ja_writer_01.py:63、RUN/ja_writer/factlock/r1.raw.md:8、r2.raw.md:8、revision2.md:8 |
| EN Advanced/Standard | 「as many as 134,515 people」「up to 134,515 people」 | RUN/b1b/article.md:8、RUN/a2/article.md:8 |
| Risk Flagger | 134,515自体はflagされず。flagはs11「In every study…at least three times」(F04の趣旨との関係)のみ | review_queue/post_en/paycheck_personality__run_pp_01/b1b__rf20261021T034829Z-e230/queue.md:24 |
| TTS/ASR | TTS入力も134,515。ASR書き起こしにも「134,515」(Advanced: primary_pass、Standard: TIER1_NUMERIC_EQUIVALENCE継承PASS) | er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01/{b1b,a2}/audit/tts_generation_results.json segments.full_story_part1 |

なぜ正確に維持されたか: (1)中核印で「使ってよい数字」と決定論的に確定、(2)Ledgerの「最大」「解析ごとにN異なる」を表記ごと(範囲・限定)briefへ複写、(3)R0がFact Lock規則(5)で丸め・換算禁止、(4)RFとASRが事後検査。(3)以外の層の維持はモデル挙動に依存し、決定論保証は(1)(2)とASR保護数値のみ。

## 2. 中核数値の選定基準(記事A実例つき)
| 項目 | 内容 | 区分 | 根拠 |
|---|---|---|---|
| 判断主体 | 決定論コード`derive_ranks`(LLM関与なし)。人間/LLMの裁量なし | 明文(コード) | er053_b3_deterministic_producer_01.py:479-549 |
| 対象表記の抽出 | 組立済みFact行(+Storyline行)から正規表現で数値表記を抽出 | 明文(コード) | 同:375,169 |
| 適格 | 数量/日付のみ。年・序数・名称内数字は不適格。主数字が当該Factの台帳`numeric_value`欄に在ること(日付は`date_or_period`先頭と一致) | 明文(コード、承認仕様3-5-2) | 同:420-447 |
| 件数上限 | `cap = max(3, min(6, 概念数//2))`。記事Aは概念9→cap 4 | 明文(コード、承認仕様) | 同:450-451,533-541。RUN annotation.json notes「cap(4)超過で周辺化: 0.0589」 |
| 優先順 | Storylineに出る量 → 他の量 → 日付。同順位はFact内の出現順 | 明文(コード) | 同:534-541。設計根拠 er052_output/b3_rootfix_trial_02/DESIGN_REVIEW_01.md:16 |
| 記事Aの結果 | 中核4=11件(C1)・134,515人(C2)・3回以上(C4)・0.0630(C5)。周辺=少なくとも1(不適格)・0.0589・1.30年・11(cap外) | 実データ | RUN/storyline_b3/annotation.json |
| 134,515が選ばれた理由 | Storylineに数字は無く、適格(numeric_valueに有)で、出現順がF04内2番目=cap内 | 実データ+コード | 同上 |
| 承認 | D-det v2+決定論assembler=APPROVED_FOR_PRODUCTION(ユーザー最終決定2026-10-10)。初期Fact Lock Trial時の「中核数値のみ上限3件」(DECISION_LOG.md:20302)はD-det v2のcapルールで置換 | 承認記録 | DECISION_LOG.md:20547、CURRENT_SPEC.md:1177 |
| AIの裁量が及ぶ点 | 「どのFactをBriefに採用するか」(B3 LLM、4テスト+下限VERIFIED2件)。採用Factから外れた数値は中核になり得ない。B3の採用数は固定上限なし(Test1〜4で原則除外、下限2) | AI裁量(Fact単位) | er019_family_x_storyline_b3_fact_selection_01.py:41-44、CURRENT_SPEC.md:1179 |
| Writerの裁量 | 中核印の数字から何を使うかはWriter(記事に書く義務ではない)。周辺印は書かない。印なし数字は使わない | Prompt規則+Writer裁量 | er053_family_x_factlock_ja_writer_01.py:86-93 |

## 3. Family X / Z の違い
- **Family X**: 上記が全て適用(Research→Ledger→B3→決定論producer→W-1→RF)。
- **Family Z(Fiction)**: Research/Verified Fact Ledger/B3/決定論producer/【中核数値】/Fact Lock/Risk Flaggerの経路自体が無い(er062_family_z_writer_01.py:8「B3Zなし」、Zの`er026_family_z_fiction_production_runner_01.py`に該当参照0)。「中核数値」の選定概念は存在しない。数字に関する保護はTTS/ASR側のみ。
- **共通**: ASRの保護数値(`protected_check`、er006_preprod_hardening_01_validation.py:677-701)は中核/周辺を区別せず、全数値tokenの不一致を検出する。X/Z共通。

## 4. 用語の対応
- 「中核数値」= 実装の`【中核数値】`印(B3 producer、Family Xのみ)。「Writerが記事に書いてよい数字」の意味で、「記事の主題として重要な数字」を意味しない(機械的規則)。
- `protected_number`/ASR保護数値は別概念(音声照合で全数値を守る)。
- Fact Lockの【事実N】は数値ではなくFactの出典タグ。

## 5. 付記
- 判断候補: なし。仕様と実装は整合していた。
- 観察のみ(仕様候補ではなく事実記録): cap上限により、重要度に関わらず出現順で中核が決まる。例: 記事Aで0.0589(勤勉性→収入の関連)は周辺化。
