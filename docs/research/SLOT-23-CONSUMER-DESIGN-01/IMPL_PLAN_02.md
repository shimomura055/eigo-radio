# IMPL_PLAN_02 実装分割計画(Opus条件Aレビュー後に着手。read-only設計、API 0)
設計正本=`DESIGN_02.md`、矛盾一覧=`SPEC_CONFLICT_02.md`、費用=`COST_02.md`。優先順位 Q>D>C≫開発費用。独立作業は並列化(PM_GOVERNANCE 8-X)。

## 1. 前提と先行できる作業(クリティカルパス短縮)
- **A0(API 0、即時、Opus待ち不要)**: 在庫調査。(i)`kp_human_review.json`走査で「マーク無しStd review」の一覧(制作中の実記事 vs evidence/公開済みを分類)、(ii)AI島 run(`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01`)のmigration前スナップショット(hash chain検証)。
- **契約先行**: 本書§3の関数シグネチャを固定し、C/D/E(各Family配線)は契約に対するstub/fixtureで先行着手可(A/Bの完了を待たない)。
- 並行Agent: GPG委任_05C(Yのevidence)=`er121`/`er128`のgrammar・evidence系、X TTS診断=read-only(競合なし)。同一ファイルの同時編集は**関数単位で所有を分離**(下表)し、pathspec付きcommit、着手直前に`git status`/`git diff --stat`で他Agentの未commit差分を確認する(他Agent差分はstageしない)。

## 2. 並列分割と所有ファイル
| 班 | 範囲 | 所有(編集してよいファイル/関数) | 依存 | 見込み |
|---|---|---|---|---|
| **A** 共通描画+照合+G3拡張+test | `er_learning_highlight_01.py`(新: `resolve_highlights`、純関数)、`er_user_listening_page_common_01.py`(`script_block(highlights=…)`/`render_script_html`/`script_blocks_for_part`/`meaning_list_html`/`HIGHLIGHT_CSS`)、`er128_kp_highlight_01.py`(新: `load_highlight_items`/`verify_highlight_outputs`)、各test(新規) | 上記新規+common 1ファイル。`er128_kp_confirmed_content_01.py`は**触らない**(B所有)。`load_verified_items(which="highlight")`の1分岐と`verify_outputs`末尾の1行委譲のみ統合時にBが追記(後述§4) | なし(契約から着手) | 約1.5〜2h |
| **B** Std Part 1 level化+Std検査+record側 | `er003_kp_general_explanation_01.py`(level引数・Std Head・signature)、`er003_kp_source_sentence_ja_01.py`(dir分離のみ)、`er119_kp_human_review_01.py`(S1-S8、`std_part1`)、`er128_kp_confirmed_content_01.py`(S9-S12、`reconsume`コマンド、`display_spec`、`_vocab_ids_for`)、`er120_part2_wiring_01.py`(`public_study_html`)、既存test更新(T1-T5)+新規test | 左記ファイル | なし | 約2h |
| **C** X配線+AI島再ビルド | `er019_family_x_audio_production_runner_01.py`(S17-S20、player、`_build_level_table`)、新`er019_family_x_listening_page_01.py`(`tools/build_aif3_listening_page_01.py`の昇格)、X用test | 左記 | A・B(契約でstub先行→結合) | 約1.5h(+AI島assemble停止の解消待ち) |
| **D** Y配線 | `er121_family_y_runner_01.py`(S25-S27、validator)、`er121_family_y_audio_01.py`(`build_page_rows`のhighlights)、Y test | 左記 | A・B | 約1.5h |
| **E** Z配線 | `er026_family_z_fiction_production_runner_01.py`(S21-S24)、`er063_family_z_audio_01.py`(`build_page_rows`/`_user_page_rows`/`build_pages`のhighlights引数)、Z test | 左記 | A・B | 約1.5h |
| **F** evidence 6経路+実ブラウザ+Closeout素材 | 既存`er0xx_output`構造のevidence、`ER-*_REPORT.md`、ブラウザ検証(PC+スマホ幅) | evidence出力のみ(コード変更なし) | C・D・E | 約1.5〜2h |
- 並列実行: A‖B‖(C,D,Eの契約stub先行)。A・B完了→C/D/E結合→F。Opus条件Aレビューは設計(本書)に対して即時実行でき、A/B着手と並行して指摘を反映(レビュー確認前は**コミット前に**A/Bの設計適合を確認)。
- 想定所要: レビュー0.7h → A/B 2h(並列) → C/D/E 1.5h(並列) → F 2h → Fable独立受入。**クリティカルパス ≒ 6〜7h**(直列なら約11〜12h、並列化で約40%短縮)。直列化する理由: C/D/E結合はA/Bの関数確定に依存(契約先行で重なりを最大化)、FはC/D/E完了(runtime evidenceに実装が必要)。
- AI島のassemble停止(d05729316、M3 Style Gate・HRパケット公開)は別Agent担当。**依存**: AI島の最終ページ再ビルドはassembleのOK後。それまではfixture+複製runでC班を完了し、解消後に実AI島ページをAPI 0(Std Part 1生成約¥0.16のみ)で組む。

## 3. 契約(A/B/C/D/E共通。DESIGN_02 §B/§C/§F)
```
er128.load_verified_items(kp_dir, *, level, which="highlight") -> list[dict]
    # [{"candidate_id","category":1|2|3,"slot","used_form","source_span","source_sentence","source_sentence_id",
    #   "occurrence_sentence_ids","selection_resolution_method","japanese_gloss"}]; display_specマーク無し→[]
er_learning_highlight_01.resolve_highlights(specs, article_text, display_units) -> dict
    # {"highlights":{unit_key:[{"kind","start","end","candidate_id"}]},"meanings":{unit_key:[{"span_text","gloss"}]},
    #  "notices":[...]} ; 特定不能→HighlightIssue(原因コード付き。呼出側がraise_issue同型で記録)
er_user_listening_page_common_01.script_block(text, chunk_texts=None, audience="public", warnings=None, highlights=None)
er_user_listening_page_common_01.script_blocks_for_part(texts, highlights, chunk_texts_list, audience)  # Z
er_user_listening_page_common_01.meaning_list_html(meanings)  / HIGHLIGHT_CSS
er003.study_html_for_audio_dir(audio_dir, *, items=None, level="b1b")  # Adv既定バイト同一
er003.phrases_signature(items, *, model=None, level="b1b")            # b1bのsignature不変
er128 reconsume --run --level --by --user-ref                         # 冪等・hash chain付き
```

## 4. 統合手順(競合回避)
1. A・Bは別commit(pathspec)。`er128_kp_confirmed_content_01.py`はBのみが編集し、Aの`er128_kp_highlight_01.py`呼出(`load_verified_items`の`which="highlight"`分岐・`verify_outputs`末尾の委譲)はB班が契約どおり1コミットで追記。
2. C/D/Eは各自のrunner/builderのみ。共通ファイルは編集しない(必要ならA/Bへ依頼)。
3. 各班commit前に: 関連test PASS、`py -3 -m unittest`の既存回帰(下記5)、Secret grep 0。

## 5. テスト計画(API 0、DefaultOffIsolation型を含む)
- **Adv回帰**: Adv Part 1のPrompt文字列・`PROMPT_TEMPLATE_SHA256`・signature・保存JSON・HTML出力がバイト同一(Std導入前後でgolden比較)。
- **既定動作**: (a)確定レコード無し/`display_spec`無し → `script_block(highlights=None)`と全builder出力が従来とバイト同一(6経路)。(b)`display_spec`付き→ハイライト+③訳。(c)環境変数・設定dict・modeによる迂回でON/OFFできないこと(Grep+test)。
- **照合**: `carried over`/`taken a detour`/`looked at separately`/`erased`(実AI島データ)・`first_of_N`(Std`Strategy`S2、Adv`technique`S25)・複数出現の特定・大小/引用符・文内2回・LR後span消失→ISSUE・sentence_id不整合→ISSUE・完全包含→NOTICE(停止しない)・部分交差→ISSUE。
- **不変性**: 装飾タグ除去後の文字列==元台本。public出力に`⏸`0、dev出力で`⏸`がハイライト外。`check_page` PASS。
- **Std Part 1**: A2 Head・signature分離・Std item 5件・qualityチェック・retry/resume・確定保持(G4)・`std_part1`マーク無し旧reviewは従来。Validator(Y:1021-1026相当)新旧。
- **reconsume**: AI島スナップショットでmigration→hash chain有効・冪等・ユーザー選定不変・content_sha256更新のみStd。
- **回帰**: 既存の`er128_*_test`/`er119_*_test`/`er120_*_test`/`er121_*_test`/`er063_*`/`er019_*`/`er_user_listening_page_*`系を全件実行しPASS(失敗の除外は原因記録)。

## 6. 受入条件14(USER.md §6)との対応表
| # | 条件 | 担当班/検証 |
|---|---|---|
| 1 | 正式初回Production経路に①②③表示が接続 | C/D/E配線(DESIGN_02 §C)。runtime evidence(F) |
| 2 | Std/Advの②で英語解説全文が生成・表示 | B+C/D/E。F: 各経路のページに「Vocabulary & Expressions」(Std/Adv両方) |
| 3 | ①②③の表示強度が承認仕様と一致 | A(CSS)+F: 実ブラウザ撮影(PC/スマホ)+DOMのclass/computed style |
| 4 | ③の日本語意味表示 | A(`meaning_list_html`)+G3検査 |
| 5 | ユーザー確定内容と記事表示が一致 | A(G3拡張 §D)+AI島の確定ID全件一致表 |
| 6 | retry/fallback/regeneration/resume整合 | B(signature/`ensure_stage`/G4)、各Familyのresume test |
| 7 | DEV/Trial専用経路ではない | C/D/E: 正式runner・正式page builderの入口(Grepで`tools/`/`docs/research`直接依存0を確認) |
| 8 | 正式runtimeでの発火証拠 | F: 各経路で`display_spec`付きrunのページ生成ログ+ハイライト要素数 |
| 9 | 必須Regression/Validator/Integration test PASS | §5全件 |
| 10 | actual model_id・routing・Prompt・Style確認 | F: Std Part 1の応答model_id=SUPPORT_MODEL(gpt-6-luna)、routing=`KEY_PHRASE_GENERAL_EXPLANATION`、`prompt_template_sha256`(a2)、Style(音声不変の確認=audio sha不変) |
| 11 | Fable独立受入 | Fable |
| 12 | CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新 | Fable/別委任(SPEC_CONFLICT_02 S29-S30、旧記述の履歴化) |
| 13 | Git反映 | 各班pathspec commit+`git push origin HEAD:main`、raw URL |
| 14 | 未承認仕様参照・Dangling Referenceなし | F: `STD_CATEGORY2_NO_SLOT`/`CATEGORY3_NO_CONSUMER`/`Part 1はAdvancedのみ`/旧関数名`_for_b1b`のGrep残存確認(読取互換1箇所のみ許容)、DESIGN_01/USER_DECISION_DRAFT_01の失効注記 |

## 7. 報告9項目の雛形(USER.md §8。Fable宛)
1. AI島Std/Advの完成版URL(公開URL+`user_test/family_x_ai_island_form_01/index.html`)
2. ①②③のユーザー確定内容との一致結果(candidate_id・区分・件数・表層形の突合表: Std ①3/②2/③5、Adv ①3/②2/③5)
3. Std②英語解説の内容・品質検査結果(5項目表示、検査項目の結果、実費、model_id)
4. 二重下線/通常下線の実ブラウザ表示検証(PC・スマホ幅の撮影、class・computed style)
5. X/Y/Z全6経路のProduction Wiring Status(Family別・レベル別。未検証経路はWIREDと書かない)
6. Fable独立受入結果
7. QCD実績(所要時間・実費・単価影響)
8. CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/Git反映(commit hash・raw URL)
9. 残るOpen Item・ユーザー判断事項(判断候補#1「解説本文の言語」の扱いを含む)

## 8. 判断候補(設計上のユーザー判断)
- #1 Std Part 1の「英語解説」=既存Part 1と同型(日本語の解説文、Std向け難易度)の解釈(DESIGN_02 §0)=**分類B**(USER.md:95,:97を根拠に承認範囲内で自己解決)。ユーザー異議があり得る点としてFableが報告9項目に注記。
- 他に新たなユーザー判断は不要(凡例1行・包含時の扱い・thickness微調整は表示仕様の実装詳細でB)。
