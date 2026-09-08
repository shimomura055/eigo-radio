# OPEN-121-METHOD-D-FLAG15-REVIEW-ARTIFACT-02_REPORT

管理ID: OPEN-121-METHOD-D-FLAG15-REVIEW-ARTIFACT-02(Fable委任、Sonnet実行)

## 背景

`OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01`(`er011_output/method_d_flag23_review_01/`)
の23件のうち、真の重複として証拠・過去試聴で確定済みの8件(open112_trial13 /
open117_trial02_kpのin_one_line系4件+point_two系4件、既知バグ再現)はユーザー
確認対象から除外。確認対象は「誤flag可能性高14件+判断困難1件=15件」。
現行の「1回目/2回目」表示だけでは何を比較すればよいか分かりにくい、という
ユーザー指摘を受け、UIを改善した。方式Dの閾値変更・自動再生成は一切行っていない。

## 実施内容

- 抽出: `method_d_flag23_review_01/classification_table.json`(23件、読み取り
  のみ)から`classification != "真の重複(証拠あり)"`の15件を機械抽出し、除外8件
  と件数一致を`assert`で確認。
- occurrence(1回目/2回目)ごとに、方式Dの検知秒(`flag_time_a`/`flag_time_b`)
  を中心に前後1.5秒(必要なら2.5秒→4.0秒まで段階的に拡張)の確認範囲を計算し、
  その範囲に対応するscript断片を**ローカルfaster-whisper word-level timestamp**
  (`er008_disfluency_qa_18.transcribe_verbatim()`、既存モジュール無変更import、
  CPU実行・追加API課金なし)から機械抽出した。
- 完全script欄には、上記2つの断片をdifflibのトークン単位fuzzy matching
  (2語未満の一致はハイライトしない)で近似位置特定し、`<mark class="mark-a">`
  (1回目・黄)/`<mark class="mark-b">`(2回目・水色)でハイライトした(重なる場合は
  両クラス併記で自動統合)。
- occurrenceごとに、確認範囲を切り出した新規clip(`clips/`配下、既存wavは
  読み取り専用)を生成し、「該当範囲のみ再生」ボタンを追加した。
- 標準フォーマット(`audio_review_player.py`のCSS/共通関数を再利用、Source列
  なし、Script列幅広、`<audio>`常時表示・min-width 360px、同一行配置)で
  `er011_output/method_d_flag15_review_02/player.html`を新規作成。ページ冒頭に
  判定目的「この2箇所は、本来1回でよい内容が不自然に重複しているか?」と、
  「完成episodeではなく部品flag試聴ページ」である旨を明記した。除外8件は
  ページ末尾に`<details>`で折りたたみ(item_id+根拠冒頭のみ)。
- 判定欄は3択ラジオボタン(真の重複/正常音声への誤flag/判断困難)。保存機能は
  実装していない(仕様どおり)。
- `er012_output/editorial_b_voices_trial_08_audio/p3`のwavを含む1件は、読み取り
  専用で音声・timestampを参照しただけであり、`er012_output`配下への書き込みは
  一切行っていない。

## 結果(15件、occurrenceの位置特定状況)

- 両occurrence(1回目・2回目)とも位置特定できた: **15件/15件**(未特定0件)。
- fragment抽出結果は目視でも1回目/2回目が明らかに異なる箇所(内容的に無関係な
  文)を指しており、「誤flag可能性高」の一次分類と整合する(例:
  `pool_n18_notifications_specfix_v2::point_two_heading`は"muting is not the
  same as"/"same as absence"という並行構文由来の部分的語句重複で、TTS側の
  実際の重複ではないと解釈しやすい)。
- voice情報: 15件中8件で機械抽出、残り7件は「情報なし(audit記録なし)」。
- TTS instruction_type情報: 15件中6件で機械抽出、残り9件は「情報なし」。
- canonical_text未取得: 0件(15件すべて確認できた)。

## clip生成

- occurrenceごとに1本、計 **30本**(15件×2)の新規clipを`clips/`配下に生成
  (全ファイル非0バイトを確認)。既存wav・JSONは一切変更していない
  (読み取りのみ)。

## Gate 7チェック((g)(h)(j)(k)(l)のみ適用、部品flag試聴artifact)

| 項目 | 結果 |
|---|---|
| (g) 開始秒・click-seek | PASS: 各occurrenceに検知秒ボタン(自身の個別音声内へseek)+該当範囲clip単独再生ボタン |
| (h) voice名 | 一部PASS: 15件中8件で機械抽出、残り7件は「情報なし(audit記録なし)」と明記(推測なし) |
| (j) テキスト未取得は「未取得」明記 | PASS: 15件全件canonical_text確認済み。fragment未特定時は「位置未特定」と明記する分岐を実装(本run結果は該当0件) |
| (k) TTS方式明記 | 一部PASS: 15件中6件でinstruction_type機械抽出、残り9件は「情報なし」 |
| (l) 再生ボタンとscriptの同一行配置 | PASS: 全15行で個別音声・Segment/voice・occurrence情報・完全script(ハイライト)・証拠・分類・判定欄を同一行に配置 |
| (a)完成episode | 非適用(部品flag試聴、ページ冒頭に明記) |

## 変更/新規ファイル

- 新規: `er011_open121_method_d_flag15_review_02.py`(root)
- 新規: `er011_output/method_d_flag15_review_02/classification_table.json`
- 新規: `er011_output/method_d_flag15_review_02/player.html`
- 新規: `er011_output/method_d_flag15_review_02/clips/*.wav`(30本)
- 新規: 本Report
- 変更・削除・Git操作: なし(既存wav/JSON/旧player.html・`er012_*`への書き込みなし)

## 費用

¥0(TTS/ASR/LLM有料API呼び出しなし。faster-whisperはローカルCPU実行のみ)
