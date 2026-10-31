# CURRENT_STATE_01 — 選定UIへのデータ供給経路と、出現回数の集計に使える既存資産

管理ID: SELECTION-UI-OCCURRENCE-COUNT-01 / OPEN-632 / 委任_01(調査・設計・精度検証。実装・UI変更・Production配線は未実施)
日付: 2026-10-31 / API費用: 0円 / ユーザー原文: `docs/pm/delegation_log/2026-10-31_LEARNING-ITEM-QUALITY-TRIO-01_USER.md` §4

参照は作業worktree(origin/main 16cef644f 基準)の行番号。run dir実体のうちGit未追跡のもの(ai_island/uk_train/melos/redelivery_fee の一部)は main tree(`C:\Users\tensh\eigo-radio`)を読み取り専用で参照した。

## 1. 学習項目(Phrase/Word)が選定UIに届くまで

```
[記事制作run]                                     [Human Review待機点で1回]                       [公開]
Writer/Translate -> support(Preview/Comment) -> KP候補生成(N5等) -> kp_candidates.json
   -> export_form_data_01.py convert() -> user_test/selection_form_v3/data/<slug>__<level>__prod.json (記事x水準の「member」)
   -> tools/publish_selection_batch_01.py -> data/batches/<id>.json (members + member_sha256) -> index.html/form_logic.js が fetch して描画
```

| 段 | ファイル:行 | 内容 |
|---|---|---|
| 候補 | run dirの `kp_candidates.json`(X: `<out>/<lv>/key_phrases/`、Y/Z: `<out>/key_phrases/<lv>/`) | 各candidateに `used_form`(N5・正規化後の一般化形)、`selection_phrase`(選定時の本文実表現)、`item.source_span`(本文逐語)、`item.source_sentence_id`、`item.occurrence_count`/`occurrence_sentence_ids`、`item.normalization_reason` |
| 変換 | `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py:160-183`(`entry()`) | `term = used_form or selection_phrase`(:164)、`selection_phrase`は `term` と異なる時だけ出力(:175-176)。`excerpt = source_sentence`(:165)。`source_span`/`source_sentence_id`/`occurrence_*`/`normalization_reason`は**出力しない** |
| 組立 | 同 `convert()` :252-306 | `phrases`/`words`(上限7/5)、超過は`overflow`、`difficulty`(:172)など参考情報を各entryに持たせる。`source_kp_candidates_path`・`family`・`level`・`source.text_sha256` を出力に持つ |
| 公開 | `tools/publish_selection_batch_01.py:138,174`(`member_sha256`)、`data/batches/*.json` | batch JSONは `members`(stem列)+`member_sha256`のみ。**回数のような記事別情報は持たない**(memberのdata JSONに載せる) |
| 表示 | `user_test/selection_form_v3/index.html:151-170`(`groupHtml`)、`form_logic.js:102`(`difficultyOf`) | 各候補は `<div class="item"><div class="lab"><label>term</label>[難易度バッジ][flag]<div class="ja">日本語訳</div>[AI理由details]</div>` + ①②③チェック |

### 1-1. 「N5の一般化表示形」と「本文の実表現」の対応は既に残っているか

**残っている**(出力data JSONの `term` と `selection_phrase` の組)。データ上の実例(batch実データ261件中78件で term != selection):

| normalization_reason | 件数(実データ) | term(表示形) <- selection_phrase(本文実表現) の例 |
|---|---|---|
| lemma_normalization | 53 | `apply to every household` <- `applied to every household` / `sink for ever` <- `sank for ever` |
| generalize_person_dependent_reference | 18 | `pull someone under` <- `pulled him under` / `lose one's trust in someone` <- `lost my trust in you` |
| remove_contextual_determiner | 2 | `sales pitch` <- `the sales pitch` |
| inherit_selection_normalization | 2 | `narrow down` <- `narrow down the source` |
| generalize_reference_word | 2 | `draw a line` <- `draw that line` |
| none | 1 | `old-fashioned` 系 |

(全run横断の候補doc: lemma_normalization 285 / generalize_person_dependent_reference 173 / inherit_selection_normalization 146 / remove_contextual_determiner 5 / generalize_reference_word 4 / none 762。`n5_generalization` は0件=既存runはN5(2026-10-30配線)以前。N5配線後の候補は `er138_kp_n5_generalization_01.py:1355-1387 apply_to_item` で `used_form=key_phrase=N5形` に、`source_span/source_sentence/display_phrase` は本文根拠として**無変更**で残る=term(N5形)とselection_phrase(本文実表現)の対応は同じ形で保たれる。N5はフレーズのみ対象 [同:15])。

- 集計に必要な情報は**data JSONの `term` + `selection_phrase`(+`kind`)だけで足りる**。追加で候補docから持ち込む必要があるのは不要(`source_sentence_id`等は使わない)。
- `candidate_id` で候補docへ戻れる(`id`/`candidate_id`)。
- 語彙の範囲: 全run・data JSONの異なる表現474件は英数字・`'`・`-`・空白のみ(記号・括弧表記なし)。人称スロット語を含むものは33件(`someone`/`something`/`one's`/`oneself` 等)。

## 2. 本文4区分(+タイトル)の正式テキスト所在

選定フォーム生成=KP review待機点では、**4区分の本文が既に全て存在する**(順序の根拠):
- X: `er019_family_x_audio_production_runner_01.py:970-974`(support生成) -> :994-997(`run_kp_with_review`)。`In One Line`は Writer の `parts.json`。
- Y: `er121_family_y_runner_01.py:34`(`STAGES = ... "text","translate","support","kp" ...`)
- Z: `er026_family_z_fiction_production_runner_01.py:1234`(`E2E_STAGES = ... "writer","std_adjust","plan","support","kp" ...`)

| 区分 | X | Y | Z |
|---|---|---|---|
| Story(本文) | `<out>/<lv>/parts.json` の `part1..3` | `<out>/translate/<lv>.md` の本文全段落(Lead/Voice紹介/Voice/Closing。`er121_family_y_structure_01.py:296 canonical_body`) | `<out>/writer/r2.md`(b1b)/`std.md`(a2)の本文(`er062_family_z_writer_01.py:1541 level_text_path`) |
| Preview | `<out>/<lv>/{b1_support_texts\|a2_support_texts}.json` の `preview` | `<out>/support/<lv>_support.json` の `preview` | 同形式 `support/<lv>_support.json` の `preview` |
| Comment | 同 `comment_1..4` | `comment_1..3`(Advancedは Comment 2 削除済み) | `comments{"1".."3"}` |
| In One Line | `parts.json` の `in_one_line` | **無し** | **無し** |
| Title | `parts.json` の `title` | md先頭 `# ` 行 | md先頭 `# ` 行 |

- **Standard(a2)のPreview/Commentは日本語**(Listening Support)。英語tokenを含まないため自然に0になる(公開enduser pageでも `std` の preview/comment は日本語: `family_y_production_surname_choice_01/enduser/data/article.json`)。
- 公開enduser page(`enduser_article_v1`)の `parts[].kind` は `topic/preview/comment/story/oneline/kp/jtitle/sfx/fixed`。Xは `oneline` あり、Y/Zは無し(実測10ページ)。
- **KP選定の入力本文(`article.md`/`canonical_body`)には X の `In One Line` が末尾段落として含まれる**: 既存 `item.occurrence_count`(選定時の厳密一致件数)は Story+In One Line の合算だった(例: untidiness `clutter` 3 = Story 2 + In One Line 1)。区分別集計は旧値と区分が異なる(精度検証§3で整合を確認)。
- KP kpの`kp_explanation_en`(Key Phrase解説の英文)・日本語訳(`ja`)・固定文(Intro/Welcome/Outro)は4区分に含まれない(=出現回数の対象外。#7を満たす)。
- 実run dirの欠落: 評価用の `KP-only evidence run`(redelivery_fee `run_kp75_ev_01`、melos `run_kp75_ev_01`、monkeys_paw replay)には support/ や Story本文が無い -> 該当区分は**未取得(0ではない)**として扱う設計が必要(設計§2-4)。通常のProduction runはstage順の保証により全区分が揃う。

## 3. 既存の出現検出ロジックと再利用可能性

| 資産 | 場所 | 内容 | 再利用 |
|---|---|---|---|
| 本文一致の語境界規約 | `er105_kp_fulltext_selector_01.py:157-179 _phrase_pattern`、:186 `locate_phrase` | 大小無視・語境界(英数字の途中に一致しない)・アポストロフィ/ダッシュ揺れ許容・文境界非跨ぎ | 規約を踏襲(トークン単位に再構成)。`occurrence_count`(:274)の定義=exact一致件数で、本設計の `exact` と不変条件で突合(精度§3) |
| 活用形生成表 | 同 :742 `IRR`、:826 `regular_forms`、:866 `forms`、:629 `_PLURAL_EXCLUDE`、:637 `_PARTICIPIAL_ADJ_EXCLUDE`、:660 `_verb_base_candidates` | 前方生成で活用形を作り表層一致を検証する承認済み表 | **読み取り再利用**(改変しない)。逆引き(活用済み語->基本形)は前方生成で検証して採用 |
| 人称スロット表 | `er003_key_words_canonicalization.py:462 _PERSON_DEPENDENT_TO_GENERIC`、`er105 :1179 reference_pair_ok` | my/your/his/... -> one's/someone's、him/me/us -> someone | 閉じた代名詞集合の根拠(設計§4-3) |
| 本文ハイライト解決器 | `er_learning_highlight_01.py:222 resolve_highlights`(:283-) | 候補docの `occurrence_sentence_ids` と `source_span` で「表示される1箇所」を決める。LR/overlay後の表示本文に対応 | **目的が違う**(1箇所の装飾位置決定)。数は数えない。流用せず、表示単位 `x_display_units`(:3226)・`y_highlight_display_units`・`full_story_display_units` の定義だけ区分判定の参考にした |
| 公開済みenduser page | `user_test/*/enduser/data/article.json` | 実表示本文を `kind` 別に保持 | 精度検証の**独立照合源**(run dirから数えた値との突合) |
| 難易度(参考表示)の前例 | `export_form_data_01.py:149-158,172`、`form_logic.js:100-108`、`index.html:157` | 各entryに参考情報を持たせ、UIだけが読む。「readable/AIF1コードには含めない(照合コード互換維持)」 | **同型で実装できる**(出現回数=選定条件に影響しない参考情報) |

NLTK(`averaged_perceptron_tagger`)はローカルにあるがリポジトリのProductionでは未使用 -> 集計本体は使わない(品質評価の補助oracleとしてのみ使用、精度§4)。

## 4. 既存UI・仕様との整合上の制約(設計に反映)

1. `form_logic.js:321 validateArticle` は未知キーを拒否しない -> entryへの追加キーは後方互換。
2. Done署名(`:402 doneSig`)・照合コード(`:276 makeCode`)は **data JSONファイルのsha256先頭6桁(`__file_sha256`)** を含む -> data JSONのバイトが変わると、その記事枠のDoneは`stale`、既存の照合コードは不一致になる。**回数の追加は新しいbatch(新ID)の新規exportでのみ行い、公開済みbatchのdata JSONへ後付けしない**(`publish_selection_batch_01.py:174` の公開済みid不変性と同じ向き)。
3. `buildText/buildReadable/buildStructured`(Claude受領形式・一括コピー)は `term/selection_phrase/ja_gloss/category` 等だけを読む。回数は含めない(難易度と同じ扱い)-> **受領形式・Done・コメント欄・入力保持・一括コピーは無変更**。
4. SELECTION-UI-TWO-TIER-01(rev05-a 2階層)の個別選定ページ(`MODE==='set'`)も同じ `render()`→`groupHtml` を通る -> 回数表示は `groupHtml` 1箇所で両階層に反映。トップ(`MODE==='top'`)は候補単位の描画を持たないので表示不要。`ASSET_VERSION`(`form_logic.js:492 'sel-v3-rev05-a'`)は他委任と同時に動く場合は競合するため、実装委任時にfetch→最新の値に+1する運用が必要。
