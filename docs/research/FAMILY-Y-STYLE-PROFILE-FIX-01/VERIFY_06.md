# VERIFY_06 — `_03`静的ページとProduction builder新出力の整合(委任_08、API 0・JPY0・pages再生成なし)
方法: `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`(=`_03`の生成元run)に対し、Production builder(`ya.build_page_rows`/`ya.render_y_page`)をscratchの音声dirへdry buildし(リポジトリ・`user_test/`へ出力なし)、`user_test/family_y_production_redelivery_fee_03/index.html`と比較。script=`tools/verify_06.py <scratch dir>`(プロジェクトvenvのpythonで実行)。

| 項目 | 結果 |
|---|---|
| 台本ブロック(`<div class='script'>`) | 新public出力26個=`_03`の26個。新出力は`_03`のsubsequence(順序・本文一致)=**一致** |
| Key Phraseテーブル | 6個=6個、subsequence=**一致** |
| 音声参照 | 新出力の音声src 52個すべて`_03`に存在。通し音声(std_full.mp3/adv_full.mp3)のsha256は`_03/audio`と**同一**(mp3化は決定論的) |
| 説明文 | 新public: 承認文言1回(本文外)、`_03`: 承認文言2回(上部+制作情報)・旧文言0 → 文言一致 |
| マーカー | 新public出力0件、新dev出力(同run)の境界マーカー0(run_style_fix_01の実Chunk分割=0。`chunked_segments_in_run=0`) |
| `check_page(public)` / `check_y_page_notice` | PASS / ok |
| **不整合(指摘)** | `_03/index.html`に記号`⏸`が**凡例1行に1件**残る(「⏸=実際のTTS Chunk分割境界(開発確認用表示)。今回の記事にChunk分割境界はなく、表示はありません。」)。VERIFY_05は「⏸残存0」と記録したが実際は凡例の記号1件。新builder(public)の出力には凡例行自体が無い=`_03`の静的ページだけ公開物に開発用記号の凡例が残っている。**所有外(委任_07の静的ページ)のため未編集。修正案: 当該1行(`<br>⏸=…表示はありません。`)を削除=音声・本文・KP不変。修正へ進む(次委任、1行修正)** |

制約: `_03`のpages再生成は不要・禁止(承認済み音声)。上記1行修正も静的ページへの後処理で行い、再生成しない。
