FABLE-DELEGATION-MARKER: KPFT-DESIGN-委任_01-20261022

# 委任(KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_01: ユーザー正式決定(`APPROVED_FOR_PRODUCTION`)「Key Phrase選定を候補DB照合方式→記事全文をGPT-6 Lunaへ直接渡す方式(正式Prompt 2)へ変更、各レベル5件→3件、既存の原形化・一般化工程は維持、Family X/Z共通」のための**現状調査+影響範囲調査(5件前提の全箇所)+レベル別仕様との整合確認+実装設計+未配線module/test**。Production .py未編集・API 0・JPY0。設計後にOpus条件Aレビュー→配線は次委任)

## 管理ID
KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_01(新規。置換対象=M2P0 DB hybrid(`er030_*`、CURRENT_SPEC ~L1984/L1229/L1253、KP優先順位A方式)、KP件数5(CURRENT_SPEC「B1 Key Phrase」「Key Phrase選定(A2)」節等)。関連=直近Trial(OPEN-445/446/448: Luna全文渡しの遵守100%・Prompt第3条の知見)、並行設計中=KP3V(`er104`、KP音声判定の3-ASR多数決=選定方式とは独立)、PNAP(`er103`、固有名詞アラーム=KP対象外)。並行agentはProduction .pyを編集しないが`er019`/`er026`/`er063`/`er003`を読む。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち。新規OPEN番号は編集直前にGrep最新+1)。

## 性質/到達上限Status/禁止事項
- 性質: Production実装の前段。到達Status: `APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`(Production既存ファイル未編集=`PRODUCTION_WIRED`ではない)。
- Opus Gate: **条件A該当(KP選定の処理フロー置換+件数変更=後段全工程に波及)**。Fableが設計書を対象にOpusレビューを手配する。
- 修正範囲(11-8): 本委任で編集可=新規`er105_*`(未配線module/test)、`docs/research/KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01/`、OPEN_ITEMS新規行、REPORT_LEDGER、delegation_log。**Production既存.py・Prompt template・CURRENT_SPEC・DECISION_LOG・Store・過去記事成果物は編集不可**。
- 時間見込み(8-X): 約5〜6時間(影響範囲調査2.5h[5件前提のGrep網羅が中心]/レベル整合0.5h/設計1.5h/module+test 1h)。X/Zの調査は並列に読める。
- 費用/日次: JPY0。当日既使用 約JPY878。実装後のruntime evidence(X/Z各1記事のKP stage→TTS 3KP→ASR→組立、見積は本委任で算出。概算各20〜40円)は**翌JST日**実施の前提で計画。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止(Grep)。他agentの未commit差分を混ぜない。承認範囲を広げない(選定モデル=Luna固定、Prompt 2は一字一句固定[本文受け渡し区切りの付加のみ可、Trialと同じ]、原形化・一般化は既存工程を再利用、レベル別品質基準・KP ASR判定仕様・Std/Advの再生順序[Std: 英→日本語意味→英/Adv: 英→英語解説→英]は維持。過去記事・保存音声の再生成禁止)。

## ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01_USER.md`へ本文無改変で保存、文字数・sha256を記録)
---
# Claude Code指示：Key Phrase新選定方式の正式Production採用・Family X/Z共通

## 1. ユーザー正式決定

以下をFamily X/Z共通のProduction仕様として正式採用する。

1. **Key Phrase選定を、候補DB照合方式から記事全文を直接LLMに渡す方式へ変更する。**
2. 選定モデルは **GPT-6 Luna** とする。
3. 選定Promptは下記Prompt 2を採用する。
4. **Key Phrase数を各レベル5件から3件へ変更する。**
5. 既存の原形化・一般化工程は維持・再利用する。
6. 比較Trialは不要。Production実装・検証まで進める。

Status：`APPROVED_FOR_PRODUCTION`

到達目標：Family X/Z双方で`PRODUCTION_WIRED`

## 2. 正式Prompt

以下を選定専用Promptとして採用する。

---

以下の記事から、英語上級者が学ぶ価値のある単語・フレーズ・表現・イディオムを**3つ**選んでください。

以下の順序で処理し、上位条件を優先してください。

1. **本文一致（絶対条件）**：本文中の連続した語句だけを抜き出す。変更・言い換え・追加・創作は禁止。
2. **5語以内（絶対条件）**：スペース区切りで正確に数える。6語以上は出力禁止。
3. **学習ポイントの明確化と最小化（必須）**：学ぶべき語彙・熟語・表現を明確にし、意味と自然さを保てる最短の形で抽出する。不要な目的語・修飾語・文脈は除く。5語は上限であり、目標ではない。短縮によって学習価値が失われる場合のみ、必要な語を残す。
4. **上級者向けの学習価値**：上級者でも学ぶ価値のある語彙・イディオム・慣用表現を優先する。
5. **易しい表現の除外**：基本語だけで構成され、字面どおりに意味が分かる表現や、上級者なら知っている易しい表現は除外する。
6. **3件選定**：条件を満たす候補から3件選ぶ。適切な候補が不足する場合のみ3件未満とし、数合わせはしない。

**出力直前に各候補を本文と照合し、改変がないこと、5語以内であることを再確認してください。語数も併記してください。**

---

一般化はこの選定Promptで実施しない。既存の後段工程で処理する。

## 3. Production経路の変更

Family X/Zそれぞれについて、正式初回Production経路を変更する。

- 既存の候補DB生成・照合・shortlist前提を取り除く。
- 記事全文をLunaへ渡して直接選定する。
- 本文一致・語数・件数を機械検証する。
- 選定結果を既存の原形化・一般化工程へ接続する。
- 原形化後の学習ポイント・意味・自然さを維持する。
- 既存の日本語意味・英語解説・TTS・ASR・完成記事組立との整合を確保する。

特に、全文からの自由抽出に変更することで既存の候補IDやsource span契約が破綻しないよう、必要な内部調整を行うこと。

実装方法は合理的な範囲で自律判断してよいが、承認済み品質基準を独断で変更しない。

## 4. Key Phrase 3件化

Family X/ZのStandard／Advancedともに、Key Phraseを最大3件とする。

以下のすべてを確認・修正する。

- 選定・原形化・一般化
- 意味・解説生成
- 音声生成・ASR判定
- retry・fallback・regeneration・resume
- Master Audio Store再利用条件
- 記事組立・表示・再生順序
- 完成報告・ユーザー試聴ページ
- Validator・テスト・固定件数チェック

**旧仕様の5件前提を残さないこと。**

ただし、過去の完成記事・保存済み音声を不必要に変更・再生成しない。

## 5. Family共通仕様・品質条件

以下を維持する。

- Standard／Advancedそれぞれの既存レベル別品質基準
- 既存の原形化・一般化品質
- Key Phrase英語フレーズの承認済みASR判定仕様
- Standard：英語Phrase → 日本語意味 → 英語Phrase
- Advanced：英語Phrase → 英語解説 → 英語Phrase
- その他の承認済みProduction品質条件

**注意：Prompt 2は「英語上級者向け」という文言を含む。**

Family X/ZのStandardにもそのまま適用すると、既存のレベル別学習品質と衝突する可能性がある。

既存のレベル別仕様と整合するよう、Standard／Advancedへの適用を確認すること。承認済みレベル品質を変更する必要がある場合は、独断で変更せずUSER_DECISION_REQUIREDとして報告する。

## 6. 受入条件

Family X/Zの双方について、以下を確認する。

1. 正式Production初回経路が候補DBではなく全文直接選定になっている。
2. actual model IDがGPT-6 Lunaである。
3. 正式Prompt 2の選定条件が反映されている。
4. Key Phraseが最大3件になっている。
5. 本文に存在しない語句・6語以上の表現が採用されない。
6. 原形化・一般化が正常に機能する。
7. 後段の意味・解説・音声・ASR・組立が正常に動作する。
8. retry／fallback／regeneration／resumeが新方式と整合する。
9. 旧候補DBや5件前提のDangling Referenceがない。
10. 必須Regression／Validator／integration testがPASSする。
11. Family X/Z双方の正式runtime evidenceがある。
12. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitが更新されている。

必要十分な品質を満たした時点で完了する。不要なモデル比較・追加Trial・過剰な磨き込みは行わない。

## 7. QCD・STOP条件

品質（Q）＞速度（D）＞量産単価（C）≫開発費用。

- 既存資産を再利用し、最短でProduction配線する。
- 独立作業を並列化する。
- 不要な待機・日付分割を行わない。
- 開発費の日次原則1,000円（JST）と個別承認枠を遵守する。
- 実装・テストの不具合は承認範囲内で自律解決する。
- 既存の音声・完成記事を不必要に再生成しない。
- 品質基準の変更、承認範囲外の仕様変更、重大なblocker、予算超過がある場合はSTOPして報告する。

## 8. Fable受入・Closeout

Fableによる独立受入評価を実施する。

最終報告では、次を簡潔に示すこと。

1. Family X/ZそれぞれのProduction Status
2. 候補DB方式から全文選定方式への切替証拠
3. Luna model ID・正式Promptの適用証拠
4. Key Phrase 3件化の動作証拠
5. 原形化・一般化・後段音声との整合
6. retry／fallback／Store／resumeの確認結果
7. 品質・速度・量産単価への影響
8. SSOT／Git反映とFable受入判定
9. 残存Open Item・必要なユーザー判断

**今回の目的は新旧方式の優劣を再比較することではない。ユーザーが正式採用を決定した全文選定方式と3件化を、Family X/Zの実際のProductionで動作させることである。**

両FamilyでGate 3を満たすまで追跡し、未確認事項があればPRODUCTION_WIREDと判定しないこと。
---

## Fableの事前整理(設計の前提。再照合しズレは報告)
- 現行経路(X): `er019_family_x_audio_production_runner_01.py:411`→`er003_v1_n3_01_scaffold_generate.py` `run_key_phrases`(db_hybrid[`er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection`、shortlist cache、source span検証、Strategy L fallback]→canonicalization(:742)→gloss整合→Redundancy QA retry)。Z: `er026_family_z_fiction_production_runner_01.py`/`er063_family_z_audio_01.py`のKP経路(Grep `run_key_phrases|key_phrase`)。新経路=**全文+Prompt 2をLunaへ1回**→出力解析(表現・語数)→機械検証(本文連続一致[厳密]・≤5語・≤3件・重複なし)→既存canonicalization→以降は既存。Trialの`er098`/`er101`/`er102`のparser・validatorを**Production品質で再実装**(手動override禁止、解析失敗はretry→上限でstage失敗=fail-closed)。
- 既存契約の調整: 候補ID/source span契約(`er030_key_phrase_db_hybrid_source_reference_contract_01.py`、`_verify_source_spans_against_raw_article`)を新経路でも満たす形(全文一致検証で原文spanを確定し同じ構造で渡す)にし、後段(gloss整合D1、KP source gate `key_phrase_source_gate`、Store key、M3 style gate)が壊れないことを設計で保証。Strategy L fallbackの要否(新経路の失敗時=Luna再呼出上限内のretry→stage失敗。旧Strategy Lへのfallbackは「候補DB前提を取り除く」趣旨から撤去候補、Opusに確認)。
- 3件化の影響範囲(網羅Grep必須): `5`固定のvalidator/test/組立(`kp1..kp5`、`range(5)`、`== 5`、`KP_COUNT`、`kp5_`、segment plan、Store manifest key、試聴ページ生成、完成報告、Redundancy QA、gloss整合のslot数、validation inheritance、KP dual audit`5+5`、X/Zのstyle profile、`er019_family_x_kp_en_k2_store_01`、`er063`)。各箇所を「定数化して3へ」「可変長対応」「撤去」に分類。**過去記事(5件)の再生成・Store既存エントリの変更はしない**(可変長対応で後方互換)。
- レベル別仕様との整合(ユーザー§5注意): CURRENT_SPEC「B1 Key Phrase」「Key Phrase選定(A2)」「Standard/Advanced」節(Grep `Key Phrase選定|B1 Key Phrase|Standard|Advanced|上級`)で、Standard側のKP選定基準(例: B1学習者向け/Listening Blocker等)が承認済みか確認。Prompt 2の「英語上級者」をStandardにそのまま適用すると**承認済みレベル品質と衝突するか**を判定し、衝突する場合は(ア)Prompt 2をそのまま両レベルに適用(ユーザー決定の文面どおり)/(イ)Standardのみ文言調整(承認が必要)/(ウ)Standard用の既存基準維持、の選択肢と影響を`判断候補`として整理(独断で変更しない)。
- Store再利用: KP音声の再利用キーは表現テキスト+profile。3件化で同一表現なら再利用可(件数は無関係)。KP3V(3-ASR多数決)が並行設計中=再利用判定の仕様はそちらの設計に合わせる(本設計では「KP判定仕様は別管理IDで更新中、本件は件数・選定のみ」と明記し、衝突箇所[Store field、kp audit]をリストアップ)。
- 量産単価: 選定費はTrial実測(全文渡しLuna 0.26〜0.35円/セット)+canonicalization(既存)−shortlist/DB照合費(撤去分)。3件化でTTS/ASR/解説生成が2/5減(見積を実測ベースで)。
- runtime evidence計画: X=既存Family X記事1本(例 coffee_prices or paycheck run_pp_02の本文)をKP stageから再実行(Writer再実行なし)→3KP→TTS→ASR→組立→試聴ページ(新run dir、旧run無変更)。Z=Family Z記事(melos)同様。見積(円)と翌JST日実施。

## 実行内容
1. 調査→`INVESTIGATION_01.md`(現行経路図X/Z file:行、5件前提の全箇所一覧[分類付き]、契約・後段依存)。
2. レベル整合→`LEVEL_SPEC_CHECK_01.md`(承認済み仕様の引用[CURRENT_SPEC行]、衝突判定、選択肢)。
3. 設計→`IMPLEMENTATION_DESIGN_01.md`(新module `er105_kp_fulltext_selector_01.py`[Prompt 2固定+区切り、Luna呼出(routing contract経由、model ID記録)、parser、機械検証、原文span確定、既存canonicalization接続、retry/fail-closed]、定数`KP_COUNT_MAX=3`の置き場と可変長化方針、配線点ごとの差分案X/Z、撤去一覧[er030 DB hybrid経路・shortlist cache・Strategy L・5固定check]、Store/resume/retry整合、試聴ページ・完成報告の3件表示、test計画、runtime evidence計画・見積、ロールバック手順、量産単価影響)。Opus条件Aに答えられる粒度。
4. 未配線module+unit test(`er105_*_test_01.py`: Prompt sha固定・parser・検証・3件上限・解析失敗fail-closed)。Production .py無編集。
5. SSOT: `OPEN_ITEMS.md`新規行「KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01」`APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`。`REPORT_LEDGER.md`1行。CURRENT_SPEC/DECISION_LOG追記文案はRESULT_PACKETへ。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01_委任_01.md`(Nは`FABLE-DELEGATION-MARKER: KPFT-DESIGN-委任_01-20261022`を含むAgent tool_useの通番、282前後。先頭行で一致確認)。
6. commit→push→到達確認。`ACTIVE_TASK.md`固定ヘッダ。`RESULT_PACKET_KPFT1.md`。

## 事前指定Read/Grep
- Read: `er003_v1_n3_01_scaffold_generate.py`(Grep `def run_key_phrases|canonical|redundancy|strategy_l|db_hybrid`→該当範囲)、`er030_key_phrase_db_hybrid_selector_01.py:389-600`、`er019_family_x_audio_production_runner_01.py:395-440`、`er026_family_z_fiction_production_runner_01.py:1470-1500`、`er063_family_z_audio_01.py`(Grep `kp|key_phrase`)、`er098_kp_six_model_trial_01_{common,validate}.py`(parser/validatorの流用元)、`docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/TRIAL_RESULT_02.md` §8-2(Prompt受け渡し調整)。
- Grep(網羅): `kp[1-5]_|kp_count|KP_COUNT|range\(5\)|== 5|len\(.*\) *(==|!=|<) *5|five|5件|5つ` in `er0*.py`/`tools/*.py`/`user_test`生成script、`shortlist|db_hybrid|strategy_l|StrategyL` in `er0*.py`、CURRENT_SPEC `Key Phrase選定\(A2\)|B1 Key Phrase|KP選定優先順位|M2P0|Listening Blocker`。

## Git
- 明示add: `er105_*.py`、`docs/research/KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01/**`、delegation_log 2件、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`。
- commit: `KPFT 委任_01: KP全文選定(Luna・Prompt 2)+3件化(ユーザー承認APPROVED_FOR_PRODUCTION)のX/Z配線に向けた調査・5件前提の影響範囲・レベル整合確認・実装設計・未配線module+test、Production未編集、¥0`。

## 報告(RESULT_PACKET_KPFT1.md)
経路図要点/5件前提の箇所数と分類/レベル整合の判定と選択肢(`判断候補`)/設計要点・撤去一覧・契約調整/test結果/runtime evidence計画・見積/量産単価影響/KP3V・PNAPとの衝突箇所/CURRENT_SPEC・DECISION_LOG追記文案/RESULT_PACKET 4行/raw URL。