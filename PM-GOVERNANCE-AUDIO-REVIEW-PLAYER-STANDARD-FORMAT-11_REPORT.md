# PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11 — 実行Report

## 1. 背景・目的
ユーザー決定(2026-09-08、正式): EDITORIAL-B-FAMILY-VOICES-TRIAL-09の
player形式(`er012_output/editorial_b_voices_trial_09_audio/player.html`、
Gate 7 (a)〜(l)準拠)を、完成音声/Trial音声レビューの標準フォーマットとして
採用する。以下3点を修正: (1) Source列削除 (2) Script列拡幅
(3) 個別`<audio>`の幅拡大(再生ボタン常時可視)。

## 2. 調査(既存player生成箇所)
Grepで特定した生成関数:
- `er012_editorial_b_voices_trial_09_heading_regen_03.py::build_full_player_html_03`
  — 現在ディスク上のTrial-09 player.htmlを**最後に生成した**関数(本タスクの対象)。
- `er012_editorial_b_voices_trial_09_audio.py::build_player_html`(同ファイル旧版、
  heading_regen_03により上書き済み。今回は変更していない=historical。)
- `er012_editorial_b_voices_trial_08_audio.py::build_player_html`(Trial-08専用、
  今回は変更していない=historical。)
- `er011_output/open112_trend_theme2_b_final_audio_rerun_03/player.html`
  を生成した**.pyファイルはリポジトリ中に存在しない**(ephemeralに生成された
  ものと推定。生成元スクリプトを特定できず)。

## 3. 実施内容
1. 共通module `audio_review_player.py`(root)を新規作成。
   `PLAYER_STANDARD_CSS`・`render_timeline_row()`・`render_timeline_table()`・
   `render_single_audio_html()`・`abs_file_url()`・`SEEK_SCRIPT`を提供。
   - Source列を持たない4列ヘッダー固定(Seek/Segment・voice/Script/個別音声)。
   - CSS幅: Seek列100px・Segment列190px・個別音声セル400px、
     `<audio>`は`min-width:360px`(Chrome/Edgeで260px時に再生ボタンが
     「…」メニューへ畳み込まれる挙動を避けるため拡大)。
2. `er012_editorial_b_voices_trial_09_heading_regen_03.py::build_full_player_html_03`
   を上記共通moduleを呼ぶ形へ書き換え(Source列出力・旧インラインCSS削除)。
3. `pm_governance_audio_review_player_standard_format_11_regen.py`(新規、root)を
   作成し、既存audit JSON(`heading_regen_03_full_run_summary.json`・
   `parts.json`・`b1_support_texts.json`・`timeline.json`・`voice_resolution.json`)
   のみを読み、`build_full_player_html_03()`を直接呼んで
   `er012_output/editorial_b_voices_trial_09_audio/player.html`を再生成。
   TTS/ASR/Assemblyは一切呼んでいない(音声wav・JSONは無変更、mtime確認済み)。
4. `docs/pm/PM_GOVERNANCE.md` Gate 7補足(l)へ、標準フォーマット採用と
   3修正点を既存(l)の追記として追加(新規項目番号は増やしていない)。
   冒頭changelogにも1行追加。
5. `CURRENT_SPEC.md`をGrepで確認したが、player.htmlへの言及は全て
   「証跡ファイルの保存先パス」としての参照のみで、player形式自体を定めた
   正式仕様セクションは存在しなかったため、追記していない(指示どおり)。
6. rerun_03(`er011_output/open112_trend_theme2_b_final_audio_rerun_03/player.html`)
   は**未実施**。理由: (a) 生成元.pyが存在せず、再現に必要な
   label→text解決ロジックが新規に書き起こしになる、(b) 使用labelの命名規則が
   Trial-09と異なる(例: "Full Story Part 1 (Aoede)" / "Point One semantic
   heading (Aoede)" 等、Trial-09の"Hook Part 1"/"Narrator: One Voice heading"
   等とは別体系)、(c) TOCナビゲーション・旧新FSP1比較セクション等、標準
   タイムライン表以外の独自構造を持つため、共通関数だけでは再現できない。
   構造差・データ欠落を理由に見送り、既存ファイルには一切触れていない
   (git status差分なしを確認済み)。

## 4. 機械チェック結果(Python、ブラウザ未使用)
`er012_output/editorial_b_voices_trial_09_audio/player.html`に対し実行:
- timelineテーブルのヘッダーは4列、"Source"という文字列を含まない → PASS
- 全30行(pause_行除く)が`<td>`4個・Seekボタンを保持 → PASS
- SFX/ジングル行7件は`<audio>`を持たず「効果音」または「ジングル」の文言を含む
  ことを確認(想定どおり) → PASS
- CSS中に`min-width: 360px`・`width: 400px`が存在 → PASS

## 5. 変更ファイル一覧
- 新規: `audio_review_player.py`(root)
- 新規: `pm_governance_audio_review_player_standard_format_11_regen.py`(root)
- 変更: `er012_editorial_b_voices_trial_09_heading_regen_03.py`
- 変更(再生成のみ、音声/JSON無変更): `er012_output/editorial_b_voices_trial_09_audio/player.html`
- 変更: `docs/pm/PM_GOVERNANCE.md`(Gate 7 (l)追記1箇所、冒頭changelog1行)
- 変更なし: `er011_output/open112_trend_theme2_b_final_audio_rerun_03/player.html`(未実施)
- 変更なし: `CURRENT_SPEC.md`(追記対象箇所なし)

## 6. 未確認事項
- rerun_03 player.htmlの標準フォーマット反映は未実施(上記理由)。反映するには
  別途、rerun_03用のlabel→text解決ロジックを新規に書く委任が必要。
- ブラウザでの実見た目確認(overflowメニューの実際の非表示挙動)は未実施
  (機械チェックのみ、費用ゼロ・音声非実行の制約に従い今回は静的HTML検証に限定)。
