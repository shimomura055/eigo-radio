# OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01_REPORT

管理ID: OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01(Fable委任、Sonnet実行)

## 背景

OPEN-121既存音声sweep(`OPEN-121-EXISTING-AUDIO-SWEEP-REVIEW-AND-CLIPS-02`、
commit `11f68bc`、レポート実体は`OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01_REPORT.md`)
で、方式D Production既定閾値(run≥0.12秒)により既存PASS音声(en本文517件、
既知事例除く)中23件がflagされている(`FLAG_D` 15件+`FLAG_D+FLAG_A` 8件=23件、
`results/production_params_reclassification_02.json`のmain_rowsから抽出)。
ユーザー方針: 閾値変更・自動再生成は一切せず、まず23件を実際に試聴確認する
ための軽量player(標準フォーマット)を用意する。本タスクはその抽出・一次分類
(機械的、証拠ベース)・player作成のみを行った(最終判断はユーザー試聴)。

## 実施内容

- 抽出元: `production_params_reclassification_02.json`(main_rows、judgement
  `FLAG_D`/`FLAG_D+FLAG_A`)、`inventory.json`(canonical_text)、`method_d.json`
  (best_run_length_seconds・top_matches[時刻・lag・類似度])。
- 一次証拠として、各segmentの生成時ASR検証結果(`tts_generation_results.json`
  の`asr_text`/`asr_verdict`/`audio_classification`)、既存disfluency QA
  (`disfluency_evidence.repeats`)、方式Aの独立ASR(faster-whisper)による
  反復span検知結果(`a_flagged_spans`)、review_lock状態を機械抽出して
  突き合わせた。追加のTTS/ASR/LLM API呼び出しは一切行っていない(¥0)。
- 出力: `er011_output/method_d_flag23_review_01/`
  - `classification_table.json`(23件、証拠・一次分類・根拠を機械抽出)
  - `player.html`(標準フォーマット、`audio_review_player.py`のCSS/構造を
    流用。ただし本artifactは23件の異なる個別wavの集合であり単一の
    完成episode音声が存在しないため、Seekは各行「自分自身の音声」内へ
    移動する形に調整した。ページ冒頭に「完成episodeの試聴ページではない」
    旨を明記)
- 既存wav・JSONは一切変更・上書きしていない(読み取りのみ、git差分は
  新規2件[スクリプト・出力ディレクトリ]のみ)。

## 一次分類 集計(23件)

| 一次分類 | 件数 | best_run_length_seconds分布 |
|---|---|---|
| 真の重複(証拠あり) | 8 | 0.16〜0.32秒 |
| 誤flagの可能性高 | 14 | 0.12〜0.16秒 |
| 判断困難 | 1 | 0.17秒 |

代表例:
1. `open112_trial13`/`open117_trial02_kp`の`in_one_line`系4件+`point_two`系4件
   (計8件、真の重複): 既知バグ「In One Line BEFORE_FIX」「Point Two BUGGY」と
   同一script・同一flag位置。方式Aの独立ASR(faster-whisper)transcriptに
   文全体が2回連続で出現しており(`disfluency_evidence.transcript`に直接
   確認可能)、2026-09-07にユーザー実試聴で実在バグと確定済み。
2. `pool_n18_notifications_specfix_v2`の`point_two_heading`(誤flag可能性高):
   生成時disfluency QA(別経路の独立ASR)が`flagged=false`・`repeats=[]`で
   明示的に反復なしと確認済み。run=0.12秒(Production閾値ちょうど境界値)。
3. `pool_startups`の`full_story_part1`(判断困難): `tts_status=STOPPED`
   (標準/minimal経路とも6回で不合格、正式`verified=true`の記録なし)。
   6回のASR試行いずれも反復語句はないが、narration/に残る音声がどの試行に
   対応するか特定できず、生成ステータス自体が未検証のため判断困難とした。

## 閾値再校正Trial要否の材料(判断はしない)

- 「真の重複」8件のrun長は0.16〜0.32秒、「誤flag可能性高」14件は0.12〜0.16秒
  で、**0.16秒付近で重なりがある**(`point_two`系の真の重複2件がrun=0.16秒、
  誤flag候補側にもrun=0.16秒が1件)。単純なrun長閾値の引き上げだけでは
  完全に分離できない可能性が高い(Production側が方式D単独ではなく方式A・D'
  とのOR統合で運用している設計の妥当性を示唆する材料)。
- 「誤flag可能性高」14件中5件がrun=0.12秒ちょうど(現行閾値の境界値)で、
  該当箇所のdisfluency QA/ASR検証はいずれも反復なしを示している。
- 上記はあくまで機械的証拠に基づく一次分類であり、Sonnetは実際に音声を
  聴いていない。最終判断はユーザーの`player.html`試聴による。

## Gate 7チェック(部品試聴artifact、(g)(h)(j)(k)(l)のみ適用)

| 項目 | 結果 |
|---|---|
| (g) 開始秒・click-seek | PASS: 各行に方式Dのrun検知2箇所(1回目/2回目)の秒数ボタンあり。行自身の個別音声内へseek(完成episode一体のplayerではないため、単一track前提の(g)本来の「segment order」は非適用) |
| (h) 各segmentの使用voice名 | 一部PASS: 23件中12件でvoice/model情報を機械抽出、残り11件は音声生成時の記録にvoiceフィールドが無く「情報なし(audit記録なし)」と明記(推測なし) |
| (j) テキスト未取得は「未取得」明記 | PASS: canonical_text 23件すべて確認できた(1件は`new_segments_result.json`の実記録から補完)。個別ASR記録が無い2件(originalバリアント)は証拠欄に「未取得(生成時ASR記録が見つからず)」と明記 |
| (k) TTS方式明記 | 一部PASS: 23件中16件でinstruction_type/model情報を機械抽出、残り7件は「情報なし」と明記 |
| (l) 再生ボタンとscriptの同一行配置 | PASS: 全23行で再生ボタン・Segment/voice・Script・証拠・一次分類を同一行に配置 |
| (a)完成episode | 非適用(本artifactは部品flag試聴であり、ページ冒頭にその旨を明記) |

## 変更/新規ファイル

- 新規: `er011_open121_method_d_flag23_review_01.py`(root)
- 新規: `er011_output/method_d_flag23_review_01/classification_table.json`
- 新規: `er011_output/method_d_flag23_review_01/player.html`
- 新規: 本Report
- 変更・削除・Git操作: なし

## 費用

¥0(既存JSON読み取り・ローカルHTML生成のみ。TTS/ASR/LLM API呼び出しなし)
