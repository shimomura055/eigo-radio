# EXISTING_SPEC_CHECK_01 (委任_29 Phase 0: 既存仕様・Gate・入力データの照合。API 0)

作成: 2026-10-25。DEV/Trial専用。Production変更0。

## 1. Y合意構成・Closing分量(変更しないもの)
| 項目 | 内容 | 根拠(file:line) |
|---|---|---|
| 本文構成 | Lead / Voice1 / Voice2 / Voice3 / Tension+Closing(1段落)の5パート。3 Voices固定。独立Closing廃止 | `OPEN_ITEMS.md:976`(OPEN-463 確定済み基本方針) |
| 人物紹介・AI編集アナウンス廃止・In One Line廃止 | 委任_28で採用候補。本Trialは**触れない** | `REDELIVERY_REVISION_01/DESIGN_01.md` §2 |
| Closing分量 | 約200字(検査範囲175〜245字、1文55字以内、「？」終わり、数字・一人称・AI編集語なし) | `er110_family_y_redelivery_revision_01.py:47-48,312-342 check_closing` |
| Voice本文 | 無変更。再配達=R0(Gate PASS・byte一致を実行時検査)、SNS=run_03のvoices_final(Gate PASS 0/21 flagged) | `er110_family_y_redelivery_audio_01.py:138 load_r0`、`er110_output/family_y_opinion_based_02/sns_age_limit/run_03/run_status.json`(`gate_status_note`) |
| 変更対象 | **Tension+Closingの生成方式のみ**(本Trial) | 委任文 |

注意(Fable向け・判断候補ではなく確認事項): OPEN-463の確定方針は「Tensionは旧B『共通前提→分岐点→非対称性』継承」。委任_28の案A/B/Cも、本Trialの生成物も、この骨格に**固定せず**「新しい見方」を主軸にしている(委任_28から継続)。本Trialは、新しい見方が『分岐点→非対称性』の一形として自然に現れるかは強制しない。正式化時に旧B骨格との関係を整理する必要がある(区分=D、Trial継続には影響なし)。

## 2. Leakage Gate: `leak_tension_reverts_to_research`
- **判定文(現行・不変)**: 「最終パートの中心が、3人がなぜ違う答えに至るのかの掘り下げになっており、調査・研究データそのものの説明・比較へ戻っていない場合PASS」(`er110_family_y_persona_text_trial_01.py:379`。旧B由来は`er012_b_family_voices_writer_generic_01.py:1053`)。
- **承認意図**: 旧BのTension設計で、研究結果の要約・Discovery-syntaxへ本文が戻るのを防ぐ目的(`DECISION_LOG.md:8511`: 「Researchersは〜」型の研究報告要約に戻るFAIL。『Gateは一切変更していない』)。Yでは実在意見ベースでResearch/Factを使わないため、**意図(調査データへ戻らない)に対しては、Yの新方式で実害になることは稀**。一方、PASS条件の肯定側「3人がなぜ違う答えに至るのかの掘り下げ」が、「Voiceの外へ一歩踏み出す新しい見方」と衝突しうる(`INVENTORY_OLD_B_VOICES_01.md:141,169`のY継承整理参照)。
- **委任_28の誤FAIL事例**: 案A v1(『不在』という言葉の切り口)が1判定でFAIL。理由文=『研究やデータには戻っていないが、3人の違いの掘り下げでなく、一般化された状況と書き手の解釈が中心』(`REDELIVERY_REVISION_01/EVAL_01.md:18`)。局所書き換えが切り口を失わせた(`closing_A_v1/closing_final.txt`)。Fable整理=偽陽性(`EVAL_01.md:19`)。案B・案Cは各1判定でPASS(0 flagged)。
- **本Trialでの扱い**: Gateは`p.run_leak(kind="tension")`を**判定1回のみ**実行して記録。FAILでも書き換えない(`p.run_gate`の局所書き換えは使わない)。FAIL理由を (a)本文の課題(実際に調査要約・Discovery構文・2対1陣営分け等) (b)Gate側の課題(新しい見方を『違いの掘り下げでない』と誤判定)に分類。Gate定義の変更は提案のみ(承認済みGate変更=ユーザー承認事項)。
- 他項目の想定リスク: `leak_binary_camp_split`(2対1陣営)は一般化Promptで禁止済み。`leak_evidence_subject/discovery_syntax/memorable`は新しい見方が「〜という傾向がある」型の報じる文構造になるとFAILしうる(Promptの禁止事項に「材料にない事実を足さない」「説教・一般論を避ける」を入れた)。

## 3. 入力データ(所在・構造)
| 項目 | 宅配の再配達(redelivery_fee) | SNSの年齢制限(sns_age_limit) |
|---|---|---|
| テーマ・論点 `question_ja` | `OPINION_BASED_02/THEME_DATA_02.json` `world_frame.question_ja` | `er110_family_y_opinion_based_02.py` `WORLD_FRAME_02["question_ja"]`(`er110_family_y_opinion_based_01.py:52`) |
| 前提・範囲 `shared_premise_ja` | 同 `world_frame.shared_premise_ja` | `WORLD_FRAME_02["shared_premise_ja"]`(`opinion_based_02.py:45`) |
| 用語の意味 `distinctions` | 同 `world_frame.distinctions`(5語) | `WORLD_FRAME_02["distinctions"]`(4語) |
| Persona 3(役割・人物像・大事にしていること) | `THEME_DATA_02.json` `sheets.voice_N.{role_ja,persona_sketch_ja,stake_ja}` | `SHEETS_02[voice_N].{role_ja,persona_sketch_ja,stake_ja}`(`opinion_based_02.py:166`、`PERSONAS_04.md`の機械可読版) |
| Voice本文 3 | `er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md`(R0、委任_28と同一) | `er110_output/family_y_opinion_based_02/sns_age_limit/run_03/voices_final.json`(Gate PASS) |
| 共通Research/Fact | なし(実在意見ベース。`fact_scopes`は空) | なし |
- 両テーマとも同じ正規化関数`normalize_input`→`render_blocks`で同形のブロックにする(テーマ別の分岐は入力ファイルの読み出しだけ。Prompt側の差は0をtestで固定)。
- SNSの既存データには**Tension/Closing本文はない**(Voice本文までのTrial)。よって「既存Closingとの比較」は宅配のみ(案A/B/C)。SNSは絶対評価(+旧版にTensionが無いことを明記)。
- 入力に**入れないもの**: 既存Closing(案A/B/C・旧版)、切り口(`ANGLES`)、Gate結果、委任_28の切り口語。
