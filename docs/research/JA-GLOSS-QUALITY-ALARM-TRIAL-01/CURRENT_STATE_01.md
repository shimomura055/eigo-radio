# JA-GLOSS-QUALITY-ALARM-TRIAL-01 現状調査 (CURRENT_STATE_01)

管理ID=JA-GLOSS-QUALITY-ALARM-TRIAL-01 / OPEN-636 / 委任_01 / 2026-10-31 / 調査のみ(Production変更0)。
ユーザー原文=docs/pm/delegation_log/2026-10-31_JA-GLOSS-QUALITY-ALARM-TRIAL-01_USER.md(§3 基本仕様:40-、§5 :108- HR画面の想定)。
凡例: 【事実】=ファイル・記録で確認 / 【推定】=記録から言えるが直接の証拠はない。
関連: 訳生成の経路と根本原因は docs/research/JA-GLOSS-NUANCE-01/CURRENT_STATE_01.md §2(再掲しない)。本書は「生成後に訳がHRへ届くまで」と「HR画面側」に絞る。

## 1. 日本語訳が生成されてHRページへ届くまで

| 段 | 内容 | file:line |
|---|---|---|
| 1. 生成 | gloss新規生成(X2p' newgen_meaning_v1、2026-10-24ユーザー正式採用)。入力=対象item一覧+**記事本文の全文**(`【記事本文(参考)】`)、1 callで全item一括、gpt-6-luna、reasoning_effort=high | er003_key_words_gloss_alignment.py:710(build_user_message_newgen_meaning)、:152-156(japanese_gloss規則)、:470/:493(effort・Responses API) |
| 2. 生成直後の検査 | gloss非空・括弧/数字/記号・人称語・新3欄の非空とenumのみ。**意味・ニュアンスの検査はない** | er003_key_words_gloss_alignment.py:784(validate_item_corrected) |
| 3. 候補doc | 候補(phrases<=7+words<=5=最大12/level)は `kp_candidates.json` に `japanese_gloss`・`source_sentence`・`gates.gloss`・`flags`・`reason_ja` として保持 | er119_kp_human_review_01.py:527-545(presentation_blockers: gloss_hr_pending/gloss_not_official) |
| 4. 提示可否 | gloss gateが公式でない候補は提示しない(fail-closed) | er119_kp_human_review_01.py:542-545 |
| 5. フォーム用data | `ja_gloss`(=japanese_gloss、ページ表示・P8-KP音声と同一)・`ja_gloss_status`(official/provisional/missing)・`excerpt`(=source_sentence)・`reason_ja` を記事×levelのJSONへexport | docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py:97-99(gloss_status)、:165-167(meaning_ja/ja_gloss/excerpt) |
| 6. HRフォーム | `user_test/selection_form_v3/index.html`(+form_logic.js、dataは `data/<slug>__<level>__prod.json`)。公開URL=`https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/index.html` | user_test/selection_form_v3/ |
| 7. 確定 | ユーザーがチェックを付けて選定(①Key Phrase<=3 / ②追加解説 / ③本文意味表示)→「選定結果をコピー」→ChatGPT貼付→照合コード付きreadable→`restore`→`confirm`。確定レコードはjapanese_glossを**保護対象(ユーザーが見て確定した表示値)** | user_test/selection_form_v3/form_logic.js:199(コピー行に「日本語訳:」を含む)、er128_form_readable_restore_01.py:358-360(restore)、er128_kp_confirmed_content_01.py:14,91(保護対象) |
| 8. 訳の修正指示 | フォーム最下部の自由コメント(textarea#comment)でユーザーが指示→開発側が `confirm-revise --gloss <candidate_id>=<新訳>` を実行。履歴に `gloss_before/gloss_after` を記録し、gateを `HUMAN_RESOLVED` にする | er128_kp_confirmed_content_01.py:1765-1800(cmd_revise)、:31(使用例) |

【事実】現状、HR段階の日本語訳に対して「意味・自然さ」を独立に検査する仕組みはない(段2は形式検査のみ)。ユーザーが気づいた誤りは、実績として少なくとも `equivalent width`(『光の線の特徴を表す幅』→『等価幅』、2026-10-30のHR回答)で自由コメントから修正されている(er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01/{a2,b1b}/key_phrases/confirmed_selection.json の history extra.gloss_before/gloss_after)。HR確定後に判明した誤り(verdict『結論』、Comment 4『省かれたもの』等)は公開ページに出た後でユーザーが指摘している(OPEN-630、OPEN-631 J4)。

## 2. HR画面で訳が出る箇所・操作・既存の警告表示

### 2-1. 訳の表示箇所(user_test/selection_form_v3/index.html)【事実】
- 候補行: `<div class="ja"><span class="gl gl-<status>">正式訳</span> <span class="jatext">訳</span></div>`(index.html:161)。ラベル=`GLOSS_LABEL`(正式訳/仮訳・未確定/日本語訳未生成、form_logic.js:87-91 glossOf)。
- 候補名のtooltip(title)=`訳｜該当英文`(:159、tip=[g.text, it.excerpt])。つまり**該当英文(source_sentence)はtooltipでしか見えない**。
- 「AI理由・確認用」折りたたみ(`details.why`、`reason_ja`がある候補のみ、:163、form_logic.js:93 reasonOf)。確認用であって確定内容ではないと明記。
- 確定済み表示(lockbox): 確定10件は「確定済み/用語/(本文: selection_phrase)/正式訳+訳」(:143-150)。

### 2-2. 承認/修正の操作【事実】
- 承認: 区分チェック(①②③)とDoneボタン(Done=内容ハッシュに署名)。訳そのものを承認する個別ボタンは**ない**(訳は表示値として確定に入る)。
- 修正指示: 自由コメント1欄のみ(画面最下部)。訳の個別編集UIはない(form_logic.js 自由コメント normalizeComment)。
- → アラームは「承認操作を妨げず、コメント記入の判断材料になる」位置づけが自然。個別の『修正する』ボタンを足す必要はない(ユーザー原文§5「そのまま承認するか、訳語の修正を指示します」と整合)。

### 2-3. 既存の警告・参考表示の方式【事実】(再利用できる先例)
| 既存表示 | 方式 | 参照 |
|---|---|---|
| `.flag` | 候補名の横の黄色バッジ(`it.flag_note_ja||it.flag`、tooltip付き、折返し可) | index.html:7,26,160(.flag)|
| `.kpwarn` | 赤字(#ad4938・太字)の警告文クラス | index.html:11(CSS定義) |
| 【データ警告】 | `data_warnings`をstatus行に連結表示 | index.html:128 |
| 難易度(`df`) | **表示専用の参考情報(Gateではない)。選択/LIMITS/Done署名/照合コード(AIF1/BATCH1)に一切含めない**(KP-DIFFICULTY-4LEVEL-DISPLAY-01の先例) | form_logic.js(difficultyOf、コメント)、index.html:158-160(df) |
| 重複アラーム | 非blocking(確定・音声・組立を止めない)。完了報告ブロック/事後確認節に「重複アラーム N件」を表示。ペアは候補doc `flags.redundant_with` | er119_kp_human_review_01.py:575-630(redundancy_alarms)、:1205(render_redundancy_alarms)、er119_redundancy_alarm_display_test_01.py |
| レビューmd表 | `| rank | mark | 表現 | 日本語訳 | 該当英文 | 理由 | flags |` を人間向けに出力 | er119_kp_human_review_01.py:1566-1580 |

【設計への含意】品質アラームは「難易度表示と同じ表示専用の参考情報」として、データJSONに任意フィールドを足し、署名・照合コード・確定内容に入れない方式が既存先例と整合する(確定済み訳の保護 `PROTECTED_ITEM_FIELDS`[er128_kp_confirmed_content_01.py:91]を侵さない)。Production化はユーザー正式採用後であり、本Trialは複製したDEVフォームのみ。

## 3. 検査に使える文脈情報の所在【事実/推定】

| 情報 | 所在 | HR前に利用可? |
|---|---|---|
| 学習対象表現 | 候補doc `used_form`/`key_phrase`/`display_phrase` | 可(事実) |
| 現在の日本語訳 | 候補doc `japanese_gloss`(=フォーム `ja_gloss`) | 可(事実) |
| 該当英文 | 候補doc `source_sentence`(フォーム `excerpt`) | 可(事実) |
| 前後の文・記事全体 | gloss生成入力の `【記事本文(参考)】`(run dirの `gloss_alignment_prompt.txt`、例 er019_output/.../kp_candidates/round_1/work/gloss_alignment_prompt.txt)。levelごと(Std/Adv)の全文 | 可(事実。生成時に既に渡している同一入力。再利用でき追加取得不要) |
| level(Standard/Advanced) | run dirの `a2`/`b1b`、フォームdata `level` | 可(事実) |
| 生成時メタ情報 | 生成出力 `meaning_in_text_en`/`naive_ja`/`naive_ja_conveys`/`reasoning`(gloss_alignmentのitem_log。JA-GLOSS-NUANCE-01 data/newgen_records_all_01.json に1,045件分を収録) | 可(事実。**既に支払い済みの出力で追加call 0**。ただし旧公開記事の全itemに残っているかは未確認) |
| 既存の英語・日本語解説 | `er003_kp_general_explanation_01.py` が英語表現のみを入力に生成(JA-GLOSS-NUANCE-01 CURRENT_STATE_01 §1-2)。HR前に存在するか | 【推定】HR選定前の全候補には存在しない(確定後の別工程と読める)。未確認。→設計では「解説は入力に含めない」を既定とし、公開済み項目のみ補助入力として使える |

## 4. 現状のまとめ(設計への入力)
1. 検査を入れる自然な位置=「候補docのglossが公式gate通過後・フォームdata export前」(候補12件/level を1 batchで)。ただしこれはProduction配線の話であり、本Trialでは**事後(保存済みdata)に対して同じ入力を再構成して検査**する。
2. 必要な入力(表現・訳・英文・記事全文・level)はすべて候補doc+既存の生成入力に既にある。**追加の取得call 0**。
3. 既存アラームは非blocking・表示専用の先例がある(重複アラーム、難易度)。
4. 訳の修正はコメント経由。UIに編集機能を足さない設計が既存仕様と整合。
5. 既存実績のラベル源: ユーザー修正が記録に残るのは `equivalent width` 1種のみ(history gloss_before/after)。ユーザー指摘の他の例(verdict・things left out・culprit・charge・radius)は指摘が会話・原文§3にあり、gloss側の記録に修正履歴はない(= T1の件数は限られる。EVAL_SET_01.md §2)。
