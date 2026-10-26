## 管理ID

KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01(ユーザー追加指示②④: ユーザーがフォームで確定した「英語表現・日本語訳・①②③区分・採用文法と解説全文」を、以降の生成・組立・公開(HR Lock/retry/fallback/resume/本文ハイライト/公開ページ)で**勝手に変更しない**設計。read-only調査+設計+Opus条件A依頼文。API 0・JPY0。実装は委任_02)。並行Agent: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_02(フォーム側①③、`user_test/selection_form_v3/`・export tool)。あなたは本委任でコードを編集しない。所有=`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/{CURRENT_FLOW_01,RISK_MAP_01,DESIGN_01,TEST_PLAN_01,EVIDENCE_PLAN_01,OPUS_REVIEW_REQUEST_01}.md`、`docs/pm/delegation_log/2026-10-27_KP-CONFIRMED-CONTENT-PROTECTION-01_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_KCP1.md`。SSOT編集権なし。pathspec付きcommit。ユーザー原文は並行Agentが`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_02.md`へ保存(②④が本委任の正本。未作成なら本委任文の引用を使う)。

## 性質/禁止

- 性質: 新しい横断契約(確定内容の不変性)の設計=**Opus条件A対象**。到達上限=DESIGN_READY。
- 禁止: コード/SSOT編集、Gate緩和、新Prompt、禁止Git操作。
- 時間見込み: 約2.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_KP-CONFIRMED-CONTENT-PROTECTION-01_DELEGATION_01.md` をN=699から順に試し、先頭「## 管理ID」+「KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01」のものを採用。

## ユーザー指示(該当部・逐語)

**② ユーザー確定内容の保護（重要）**

ユーザーがフォーム上で選定・確定した次の情報は、以降の生成・組立・公開工程で勝手に変更しない。

- Key Phrase／Key Wordの英語表現
- 各英語表現に対応する日本語訳
- ①②③の選定区分
- 採用した文法事項と、エンドユーザー向け文法解説全文

選定確定後、AIによる自動書換え・再選定・別訳への置換は禁止する。

既存のHuman Review Lock・retry／fallback／resume・本文ハイライト・公開ページまで、同じ確定内容が一貫して引き継がれる設計とする。

既存の品質Gateは維持する。確定内容に品質上の問題が見つかった場合は、黙って変更せず、修正案を提示して再確認を求める。

**④ 検証・Status**

フォームの公開ページで表示・選定・送信を確認する。

特に、選定確定後の英語・日本語訳・文法解説が勝手に変化しないことを、既存Production経路と後続工程を含めて検証する。

既存の承認済み品質基準・Gateを変更しない。

必要なテスト、runtime evidence、SSOT/Git反映を完了し、Family別にPRODUCTION_WIREDの受入条件を満たすこと。

既存委任の承認範囲内で対応し、新たな仕様判断が必要な場合のみ報告してください。

(引用ここまで)

## 実施事項

1. **現行フロー(`CURRENT_FLOW_01.md`)**: HR確定(現行=HR CLI `select`/verdicts、将来=フォーム→ChatGPT→Claude→確定record取込)から公開までの、確定内容が通る全箇所をX/Y/Zで列挙: KP候補の`used_form`/`key_phrase`/display、日本語訳(gloss→P8-KP日本語意味音声・ページ表示)、①②③区分(現行の採用枠=先頭3 KP/Adv先頭5単語解説との対応)、文法(Part 2: 英文選択→解説生成→HR→ページ)、本文ハイライト(KP下線/単語解説)、HR Lock(`er011`)、retry/fallback/resume/`--regenerate-stage`、救済(er125)、補完(er119_backfill)、再選定(RESELECTION round)、gloss再整合、LR(本文TTSの書換えがKP英語/本文ハイライト位置に影響するか)、ページ生成。
2. **リスク地図(`RISK_MAP_01.md`)**: 確定後に自動変更が起こり得る箇所を事実(ファイル:行)で列挙し、各々「変更する/しない/条件付き」を判定。例: 救済がHR確定済みkeyを再導出しないか、gloss再整合が確定訳を置換しないか、resumeで旧候補docを読み戻す際に確定内容と不一致が起きないか、`--regenerate-stage`で候補生成が走ると確定内容が失われないか、LRで本文が書き換わるとKP本文一致・ハイライトが崩れないか(現行のLR後のKP整合処理)、Part 2解説の再生成条件、ページビルドのテンプレートが確定訳を使うか。
3. **設計(`DESIGN_01.md`)**: (a)「確定レコード」(`confirmed_selection.json`: 記事×レベル、候補ごと英語表現・日本語訳・区分、文法名+解説全文、確定日時・確定者=ユーザー・出所=フォーム送信JSON schema v2[並行委任の`DATA_MODEL_02`参照]・sha)をrun dirの`audit/`に置く。(b)確定後の各工程で「確定レコードと成果物の一致」をfail-closedで検査するGate(assemble/pages前。不一致=BLOCK+修正案提示、黙って変更しない)。(c)変更が必要な工程(救済・補完・再選定・gloss再整合・解説再生成)は確定レコード存在時に**確定項目を不変入力として扱う**(再導出・置換しない。品質NGは`CONFIRMED_CONTENT_ISSUE`として提示)。(d)retry/fallback/resume/regenerateは確定レコードを読み戻し、再生成時も確定内容を入力固定。(e)LRは本文narrationの書換えであり確定KPには触れない契約(KP英語TTSはENGLISH_LOCK)。本文ハイライトは確定英語表現で本文一致を再検証し、不一致なら修正案提示。(f)既存Gate不変、新flagは承認済み仕様のため既定ON、A/B/C不変、X/Y/Z共通点に配線。(g)現行HR CLI経路(select)との互換=HR verdictsから確定レコードを生成する変換(フォーム未使用時も同じ保護が効く)。
4. **test/evidence計画**: 受入=確定後に英語・日本語訳・区分・解説が不変であること(各工程の変更試行→BLOCK)、resume/regenerate後も同一、ページ出力に確定訳が出る、Family別evidence(1記事ずつ、確定レコードを置いて後続工程を実走。見積≤¥10/Family)。
5. **Opus論点(`OPUS_REVIEW_REQUEST_01.md`)**: 確定レコードの正本性/fail-closed Gateの位置/救済・補完・再選定との優先順位/LRとハイライトの整合/resume・regenerateの読み戻し/A/B/C不変/現行HR CLI互換/evidence十分性。

## 事前指定Read一覧

- `er119_kp_human_review_01.py`(Grep `select|verdict|RESELECTION|auto_select|render_request_md|gloss|study_text|grammar` ±10)、`er119_kp_candidates_01.py`(Grep `backfill|rescue|gloss` ±10)、`er125_kp_rescue_production_01.py`(Grep `def |RESCUED` ±5)、`er120_part2_grammar_production_01.py`(構造)、`er011_human_review_lock_01.py`(Grep `canonical_text|approve|lock` ±5)、X/Y/Z runnerのKP stage・pages stage(Grep `run_kp_with_review|kp_candidates|pages|highlight|underline` ±10)、`er020_tts_retry_local_rewrite_01.py`(Grep `local_rewrite|rewritten_text` ±5: LRが本文に与える影響と記録)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/DATA_MODEL_01.md`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/DATA_CONTRACT_01.md`、`CURRENT_SPEC.md` Grep `Human Review|HR確定|KP下線|ハイライト|Part 2` ±5

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_KP-CONFIRMED-CONTENT-PROTECTION-01_DELEGATION_01.md --json-out ...\_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_KCP1.md`にOPEN新規起票文案(確定内容保護=承認済み追加指示・DESIGN_READY)、判断候補(新たな仕様判断が必要な場合のみ。例: フォーム確定とHR Lockの承認の関係、区分②③の公開ページ表示が未承認の表示変更に当たるか)。

## Git

- commit message: `KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01: 確定内容(英語・日本語訳・区分・文法解説)の不変性設計(現行フロー・リスク地図・確定レコード・fail-closed Gate・Opus依頼、read-only)`。trailer: `Delegation: KP-CONFIRMED-CONTENT-PROTECTION-01/01`。push。

## 報告

`docs/pm/RESULT_PACKET_KCP1.md`: (0)T-0、(1)現行フローとリスク地図の要点(変更し得る箇所の一覧)、(2)設計要点(a)〜(g)、(3)test/evidence計画・費用、(4)Opus論点、(5)判断候補、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・raw URL。末尾10行要約。