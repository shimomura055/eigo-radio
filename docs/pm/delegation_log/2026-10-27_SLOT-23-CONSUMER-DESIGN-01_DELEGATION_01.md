## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_01(フォームv3の選定区分①②③のうち、現行Productionに消費者がない**Standardの②追加解説**と**③本文ハイライト・短い日本語意味(Std/Adv)**の公開ページ/音声/学習コンテンツでの扱いを、X/Y/Z共通で設計する。read-only・API 0。背景: ユーザー正式決定(2026-10-27 全面修正版/AI島指示§7「①②③の区分に応じた音声・解説・本文ハイライトを適用」)により区分の適用が求められている一方、初回フォーム指示では「本文ハイライト新機構のProduction配線は先行しない」とされ、確定内容保護設計では③等を`unconsumed[]`で保持中。公開物の構成変更を伴うため、**設計→Fable→ユーザー確認(必要最小限)→Opus条件A→実装**の順)。並行Agent: AI-ISLAND 委任_03(AI島制作、runner実行のみ)、GPG 05B、YSP 08、FORM 06。コード/SSOT編集なし。あなたの所有=`docs/research/SLOT-23-CONSUMER-DESIGN-01/{CURRENT_CONSUMERS_01,DESIGN_01,COST_01,OPUS_REVIEW_REQUEST_01,USER_DECISION_DRAFT_01}.md`、`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_S23D1.md`(gitignore、`-f`禁止)。pathspec付きcommit。

## 性質/禁止

- 性質: 新しい公開物構成(③ハイライト・Std②)の設計=ユーザー確認事項の整理+Opus条件A依頼文。到達上限=DESIGN_READY(ユーザー確認待ち)。
- 禁止: コード編集、承認済みの①/Adv Part 1(①+②=5件)の意味変更、音声仕様変更の前提化(③は文字のみが原則)、禁止Git操作。
- 時間見込み: 約1.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_SLOT-23-CONSUMER-DESIGN-01_DELEGATION_01.md` をN=730から順に試し、先頭「## 管理ID」+「SLOT-23-CONSUMER-DESIGN-01 委任_01」のものを採用(同時刻にAI-ISLAND 委任_03あり)。

## 実施事項

1. **現行消費者(`CURRENT_CONSUMERS_01.md`)**: X/Y/Z×Std/Advで、KP(①)の音声・ページ表示、Adv Part 1単語解説(=①+②の5件か、現行は「先頭5候補」か=HR AUTOとフォーム確定の差)、Std学習ページの構成、本文表示(ハイライト機構の有無: `user_test/unified.html`の`applyKeyPhraseHighlight`等の旧資産、X/Y/Z Production builderのKP下線/強調の有無)、短い日本語意味の表示箇所をファイル:行で。参照フォームHTML(`docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html`)の①②③ラベル・説明文の原文(ユーザーが定義した区分の意味)を引用。
2. **設計(`DESIGN_01.md`)**: (a)②=「追加解説」: Advでは既存Part 1単語解説の枠(①+②=5件)で消費=追加実装なし(確定順序①→②)。Stdでは現行Part 1なし→選択肢A: Stdにも同じ単語解説ブロック(文字のみ、音声なし=費用0)、B: Std②は短い日本語意味の表示のみ(③と同じ扱い)、C: Std②は学習ページに「追加解説」節(Adv Part 1と同一Prompt・文字のみ、生成費用=Step相当)。各案の費用・工程・既存承認仕様(Part 1はAdv限定の現行)との整合。(b)③=「本文ハイライト・短い日本語意味」: 本文表示(原稿欄)で確定英語表現(本文表層形=`source_span`)をハイライト(下線/色)し、ホバー/脚注/本文直下リストで短い日本語意味(確定訳)を表示。音声は変更しない。X/Y/Z共通builder(`er_user_listening_page_common_01.py`)に`highlight_items`を渡す機構、本文一致の再検証(確定内容保護のG3拡張=不一致はBLOCK+修正案)、LR(本文書換え)との関係(書面は不変=影響なし)。(c)確定レコードとの接続: `unconsumed[]`→消費者へ(③/Std②)、`load_verified_items`経由。(d)Family差(Xは記事別script→`public_study_html(level=)`/common builder経由)。(e)既存公開記事への適用(再ビルドのみ・音声不変、対象=確定レコードのある記事のみ)。(f)test/evidence計画(6経路、API 0見込み)。
3. **費用(`COST_01.md`)**: 各案の生成費用(Std②案C=Adv Part 1相当のcall費用実測から)、量産単価影響。
4. **ユーザー確認案(`USER_DECISION_DRAFT_01.md`)**: 必要最小限の確認事項のみ(例: Std②の扱いA/B/C=推奨付き、③の表示形式=推奨1案、既存公開記事への遡及適用の要否)。既に決まっている事項(①の意味、Adv ①+②=Part 1、③は文字のみ、音声不変)は確認に含めない。
5. **Opus論点(`OPUS_REVIEW_REQUEST_01.md`)**: ハイライトの本文一致・多重一致・活用形・大文字(例「Strategy」タイトル由来)の扱い、確定保護G3拡張、X/Y/Z共通化、既存ページ回帰、費用。

## 事前指定Read一覧

- `docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html`(①②③の説明文: Grep `①|②|③|ハイライト|追加解説` ±3)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{DATA_MODEL_02,SURVEY_01}.md`
- `docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/{DESIGN_02,CURRENT_FLOW_01}.md`(unconsumed・区分の消費者・ハイライト所見)、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{CURRENT_FLOW_01,IMPLEMENTATION_03}.md`(Std学習ページ構成・common builder)
- `er_user_listening_page_common_01.py`(全体)、`er003_kp_general_explanation_01*.py`(Part 1: Grep `def |vocab|5|items` ±5)、`er119_kp_human_review_01.py`(Grep `SLOT_RULES|vocab|kp` ±5)、`er019_family_x_audio_production_runner_01.py`/`er121_family_y_audio_01.py`/`er063_family_z_audio_01.py`(Grep `underline|highlight|mark|japanese_meaning|study_html` ±5)、`user_test/unified.html`(Grep `applyKeyPhraseHighlight` ±10)
- `docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER.md`(初回フォーム指示: Grep `ハイライト` ±3)、`2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER.md` §7

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_SLOT-23-CONSUMER-DESIGN-01_DELEGATION_01.md --json-out ...\_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_S23D1.md`にOPEN新規起票文案(②③消費者=設計・ユーザー確認待ち)。

## Git

- commit message: `SLOT-23-CONSUMER-DESIGN-01 委任_01: 選定区分②(Std追加解説)/③(本文ハイライト・短い日本語意味)の消費者設計(X/Y/Z共通、read-only、API 0)`。trailer: `Delegation: SLOT-23-CONSUMER-DESIGN-01/01`。push(`git push origin HEAD:main`)。

## 報告

`docs/pm/RESULT_PACKET_S23D1.md`: (0)T-0、(1)現行消費者の事実、(2)設計要点、(3)費用、(4)ユーザー確認案(最小限・推奨付き)、(5)Opus論点、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・raw URL。末尾5行要約。