# 委任_02: 『告げ口心臓』文法候補0件(Std/Adv)の原因調査→既存仕様内の是正→再検証

管理ID: FZ-TELL-TALE-HEART-RESELECT-REMAKE-01(Fable→sonnet-worker、2026-10-27)
ユーザー原文: `docs/pm/delegation_log/2026-10-27_FZ-TELL-TALE-HEART-RESELECT-REMAKE-01_USER_02.md`(必読・全文)。共通Charter=`CLAUDE.md`冒頭、実行層規則=`.claude/agents/sonnet-worker.md`。
成果物: `docs/research/FZ-TELL-TALE-HEART-RESELECT-REMAKE-01/GRAMMAR_ZERO_INVESTIGATION_01.md`。報告=`docs/pm/RESULT_PACKET_FZTTR2.md`。

## Fableが事前に確認した事実(起点)
- run=`er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01`。Std=`a2/study_text/grammar_candidates.json`、Adv=`study_text/grammar_candidates.json`(+`grammar_candidates/round_1_*.json`、`grammar_explanations.json`、`grammar_human_review.json`)。
- 両levelとも `prompt_id=part2_stepA8`、model=`gpt-6-luna`、round 1、`tier_table: []`、`no_feature_paras`=P1〜P22**全段落**、`uncovered_paras: []`。LLM usage: Std output 1,959 tokens(うちreasoning 1,851)、Adv 2,449(reasoning 2,367)=**実応答本文は約100 tokenしかない**。22段落の物語で全段落「文法特徴なし」は不自然であり、(a)Prompt/抽出対象の定義(対象文法inventory・Tier表・levelに応じた対象範囲)がZ本文に合っていない、(b)応答の解析(parser)が候補を落としている、(c)応答が切り詰められた/構造化出力の不一致、(d)Trial-08選定方式の品質基準どおりの正常結果、のいずれかを切り分けること。
- 仕様: `CURRENT_SPEC.md:2104-2107`(2026-10-27ユーザー決定: AI評価Top1/Top2のみ提示・原則1件・0件可・2件禁止・Top2のみ事前生成。Trial-08選定方式・品質仕様は不変)。実装=`er120_part2_grammar_production_01.py`(`PREGEN_MAX=2`/`GRAMMAR_MAX=1`)、`er119_grammar_review_01.py`、`er128_kp_confirmed_content_01.py`(grammar pending/validator)、Z runner `er026_family_z_fiction_production_runner_01.py`。設計・evidence=`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{DESIGN_01..03,SCHEMA_CONTRACT_02,IMPLEMENTATION_05A/05B,EVIDENCE_RESULT_05/05C,STD_CANDIDATE_RATE_01,ROUTE_STATUS_05}.md`。他記事(AI島X Std/Adv、猿の手Z、メロスZ、Y再配達等)の`grammar_candidates.json`を比較対照にする(Zで0件になりやすい傾向が「仕様どおり」なのか「Z本文に対するPrompt不適合」なのか)。

## 手順
1. **実行記録の確認**(API 0): round_1の生応答(保存されていれば)・prompt本文(`prompt_sha256`に対応するtemplate)・parser経路を読み、候補が「LLMが出さなかった」のか「出したが落とされた」のかを確定。Validator/上限/除外理由のログも確認。両levelで原因が共通か。
2. **独立評価**(API 0、あなた自身が本文を読む): Std/Adv本文(`run_reselect_01`のwriter/std.md・writer/r2.md)から、Trial-08の品質仕様(対象文法の種類・学習価値・難易度・levelとの適合)に照らして候補になり得る文法・構文を原文引用付きで列挙(Std/Adv各3〜6件目安。無理に埋めない)。Promptの対象定義(例: 対象inventory、Tier)と照らし、それらが「対象外として正しく除外された」のか「対象なのに抽出されなかった」のかを判定。
3. **判定**: (i)正常(0件妥当)→根拠。(ii)不具合(Prompt適用/parser/schema/表示)→承認済み仕様内で修正→test→`run_reselect_01`で文法抽出〜Top2事前生成〜フォームデータ再登録を再実行(有料。見積を先に記録、Cap: 本案件残¥145のうち本委任は¥30以内。KP/KW候補・本文・既存フォームの選択状態は変更しない。文法データのみ更新)→再検証(他記事への回帰: 既存evidence runの再抽出はしない、testと保存データ比較で確認)。(iii)仕様自体の問題(例: Prompt対象定義が物語文に不適合で、承認済み選定方式の変更が必要)→修正案・QCD影響を`判断候補`(区分D)として提示し、実装しない。
4. **保留の扱い**: 文法の確定(grammar_pending含む)と、それに依存する工程(Part 2解説・公開)は本調査完了まで保留。KP/KW選定・本文音声準備は独立(継続可)。フォームの「文法候補なし」表示の扱い(再登録時にユーザーがすでにKP/KW選定を送信済みなら照合コード`g10`との整合に注意: 文法集合が変わると照合コードが変わるので、ユーザーの再送が必要かを明記)。
5. **報告**(`RESULT_PACKET_FZTTR2.md`、ユーザー原文§3の7項目順): (1)本当に候補が無かったか (2)本文中の具体的候補(原文引用) (3)0件の直接原因 (4)正常/不具合判定 (5)修正・再検証結果 (6)ユーザーの新たな選定要否 (7)QCD・残Open Item。判断候補はA/B/C/D区分付き。SSOTは編集しない。Gitは本委任で作成・変更したファイルのみ`git add`(`git add -A`禁止)、commit/push可。他worker(委任_05: er127/er003/er019のLR是正)と同時進行中のため、それらのファイルには触れない。
