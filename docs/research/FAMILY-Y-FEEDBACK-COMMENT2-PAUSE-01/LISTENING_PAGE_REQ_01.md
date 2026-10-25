# LISTENING_PAGE_REQ_01 — 試聴ページ改修の要件(実装は委任_03、本書は要件整理のみ)

管理ID: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_02(Lane B)。ユーザー原文§4(分割位置の明示・各分割の0.2秒有無・可能ならChunk個別再生・分割位置と不自然ポーズの比較しやすさ・見た目の段落とTTS実分割を混同させない・不要に複雑なUIにしない)。

## 前提(今回の『宅配』の実状)
E-1は**全segmentが分割0**(`CHUNK_WIRING_CHECK_01.md`)。したがって今回のページで『TTS実分割位置』として表示できる境界は無く、正直な表示は「実分割なし(1回のTTS生成)/追加0.2秒なし」。ユーザーの目的(分割位置とポーズ位置の比較)を満たすには、**実分割の表示に加えて『実測した長い停止の位置』を台本上に重ねる**必要がある(これが無いとページが「分割なし」の一言になり比較できない)。

## 最小要件
R1. **Voice 1〜3・Lead・Closing・導入の各行**(Std/Advとも)に、TTS生成単位バッジを出す: 「TTS 1回(分割なし/段落=1)」または分割時「TTS n分割」。根拠は`audit/chunk_tts_decision.json`の`segments.<sid>.chunked/paragraphs/chunk_ids`と`audit/chunk_plan_<level>.json`。Stdは『対象外(Std本文は分割しない)』と明記。
R2. **台本上の境界マーカー**: chunk化したsegmentでは、各chunkの文を別ブロックにし、境界に `▼ TTS分割(段落境界)＋0.2秒追加` を表示。分割なしsegmentでは境界マーカーなし(R1のバッジのみ)。**本文の見た目の段落(日本語の元原稿の改行等)とは別の記号・色**にし、凡例を1行置く。
R3. **0.2秒の有無の明示**: 各境界に `追加0.2秒: あり` と、実測値(`assemble_summary`系の`gap_offsets_in_episode_s`、`er121_family_y_audio_01.py:805-826`で記録済み)を併記。分割なしは『追加0.2秒: なし』。
R4. **実測の長い停止マーカー(今回の主目的に直結、分割の有無に依存しない)**: 各英語Voice行の台本の該当語位置に `⏸1.25s` のように、≥700msの停止を表示(閾値は表示専用で採否に使わない)。`tools/yfb_silence_scan_01.py`+`yfb_pause_align_01.py`の出力(`measure/aligned/*.json`)を使う。位置は推定(±2〜3語)である旨の注記を1行。時刻はそのVoice行の音声内の秒(`mm:ss`)で表示するので、ユーザーは再生しながら確認できる。
R5. **Chunk個別再生**: chunk化したsegmentのみ、各chunkのwav(`<run>/<level>/narration/<segment>_k<j>.wav`)をmp3へ変換して小さな再生ボタンを付ける(既存`mp3()`ヘルパー `er121_family_y_audio_01.py:910-914`流用)。**分割なしの今回は、Voice行の音声そのもの(行ごとのmp3は既存の`adv_NN.mp3/std_NN.mp3`)が『TTS 1生成単位=1 chunk』なので追加の個別再生は不要**。ただしE-1 Voice 1だけは『HR採用前後・各attempt』を聴き比べたいというユーザーの関心に応えるなら、`attempts/y_voice_1_attempt*.wav`のmp3を並べる案(任意。R4の停止数/最大停止をキャプションに)。
R6. **UIは増やさない**: 既存の行表(`er_user_listening_page_common_01.render_standard_page` `:50-67`)のblocksに、バッジ(R1)・マーカー(R2〜R4)を差し込む。新タブ・ダッシュボードは作らない。

## 既存pages生成への追加点(行番号、実装は委任_03)
- `er121_family_y_audio_01.py:897-964` `build_page_rows`: 行ごとのblocksを組み立てる関数。`:927-939`のsegment行(`part in label_to_sid`)で `blocks.append(_script(parts["segments"][sid]))`(`:937`)の前後に、R1バッジ・R2/R3境界・R4停止マーカーの差し込みを追加する。引数に`measure`(停止検出JSON)を追加する場合は`stage_pages`(`er121_family_y_runner_01.py:1043-1061`、`ya.build_page_rows(...)`呼出 `:1056`)から渡す。
- chunk情報: `:301-304`で`chunk_tts_decision.json`に`segments.<sid>`を記録済み(`chunked/paragraphs/chunk_ids`)。分割時の0.2秒実測offsetは`:805-826` `_chunk_assembly_summary_y`の`parents.<sid>.gap_offsets_in_episode_s`。
- 停止検出の入力: 行ごとのmp3を作る箇所(`:932-933`)のslice(`x[s0:s0+dur]`)に対して、停止検出関数を呼べば、再生時間軸と同じ秒でマーカーを出せる(完成音声そのものを測るので、narration wavとの食い違いが出ない)。numpyのみで可(ffmpeg不要)。
- 検証: `page_verify`(`er121_family_y_runner_01.py:1068-1101`)の既存checkは本文・注意書き等。新規マーカーは**blocking検査にしない**(表示専用)。API 0。
- 変更は表示(試聴ページ)のみ。Productionの音声・Gate・Promptは不変。X/Zのページ共通builderの既定(`render_y_page`が既に`ys.notice_html()`でY専用の差分を持つ構造 `:966-971`)に倣い、Y側の関数内で完結させる。

## 今回の『宅配』ページに出る内容(予定)
- 全segment: 「TTS 1回(分割なし)・追加0.2秒なし」バッジ。Stdは「Std本文は分割対象外」。
- Voice 1(Std/Adv): 長い停止マーカー例(推定位置)— Std: 約29.0s `the | company` 付近に ⏸1.88s、18.4s ⏸0.83s ほか / Adv: 13.7s `so, | I` ⏸1.25s、28.2s ⏸1.13s、8.1s ⏸1.02s。Voice 2/3も同基準で表示し、Voice 1の長さが目立つことを視覚的に比較できる。
- 凡例: 「▼=TTSの実分割(今回なし)/⏸=実測した停止(推定位置)/見た目の段落とは無関係」。
