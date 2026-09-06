# OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01

管理ID: OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01
種別: read-only調査 + Trial-only TTS確認(Production Batch API使用)
Production変更: なし(コード・Prompt・CURRENT_SPEC・status格上げ、いずれも無変更)

## 0. 管理ID採番の確認

`OPEN_ITEMS.md`の既存最大IDはOPEN-116。本タスクは「OPEN-117」で正しい。

## 1. 目的

Key Phrase日本語gloss(訳語)に含まれる「～」について、
(1) Production TTSが実際にどう読むか
(2) placeholder検出ゲート(`er003_audio_tts_asr_safety.detect_gloss_placeholder_notation`)が広すぎないか
を切り分けて確認する。背景は Trial-13 kp4_ja(`point to`の訳
「～を示す、～を指し示す」)がTTS呼び出し前にSTOPPEDになった件。

## 2. 確認1: TTS実挙動(Trial、Production Batch API)

### 2.1 実装

Production関数`er003_v1_sing01_voice01_generate.generate_charon_japanese`
(voice=Charon、model=`p9a.JAPANESE_MODEL_NAME`=gemini-3.1-flash-tts-preview、
**Batch API**、`JAPANESE_STYLE_PREFIX`)を**Trial scriptから直接呼んだ**。
この関数はplaceholderゲート(`detect_gloss_placeholder_notation`)より
**手前・より低レベル**にあり(ゲートは`er003_v1_n3_01_tts_generate.
generate_charon_japanese_with_reading_safety`側に実装されている)、
直接呼ぶことで「ゲートを回避する」のではなく「ゲートより先に、TTSモデルが
与えたテキストへ実際にどう反応するか」だけを見た。Productionコードは
無変更・monkeypatchなし。ASR検証・Cascade判定・Duration異常検知は
`generate_charon_japanese`内部の既存Production機構
(`ja_secondary.evaluate_attempt_ja_with_cascade`、
`safety.detect_duration_anomaly`)がそのまま動作した。

script: `er011_open117_keyphrase_tilde_gate_recheck_01.py`
出力: `er011_output/open117_keyphrase_tilde_gate_recheck_01/`
(`results_open117.json`、`trial/narration/*.wav`、`player.html`、
`raw_usage_log_open117.jsonl`、`cost_summary_open117.json`)

### 2.2 結果

| # | 入力 | 結果 | ASR書き起こし(標準1回目→2回目→fallback) | duration(生成音声) | 異常 |
|---|---|---|---|---|---|
| (a) | `～を示す`(U+FF5E) | **STOPPED**(3回ともTRUE_CONTENT_MISMATCH) | 「お、死滅。」→「推しミス」→「頭を閉めす。」 | 1.8/1.6/1.86秒 | なし(全て正常範囲) |
| (b) | `～を示す、～を指し示す`(Trial-13 kp4_ja実gloss) | **STOPPED**(3回ともTRUE_CONTENT_MISMATCH) | 「示す、指し示す」→「示す、指し示す」(標準2回とも同一)→「お示す、お指し示す。」 | 2.96/2.56/—秒 | なし |
| (c) | `何かを示す`(対照) | **OK**(1回目でNORMALIZED_MATCH) | 「何かを示す。」 | 1.68秒 | なし |
| (d) | `〜を示す`(U+301C、対照) | **STOPPED**(3回ともTRUE_CONTENT_MISMATCH) | 「私密」→「お、しめす。」→「それをしめす。」 | 1.4/2.4/—秒 | なし |

音声: `er011_output/open117_keyphrase_tilde_gate_recheck_01/player.html`
(4件のwavを埋め込み再生可能)。詳細JSON:
`er011_output/open117_keyphrase_tilde_gate_recheck_01/results_open117.json`。

### 2.3 解釈

TTSは「～」「〜」という**記号自体を音として読み上げてはいない**
(「から」「なみ」「チルダ」等の観測は無し)。代わりに、文頭の
**裸の助詞「を」を含む不完全な断片**を渡されると、TTSモデルは
その都度異なる不安定な発話(無関係な空似語、助詞の脱落、honorific的な
filler「お」の付加等)を生成する。(b)は標準2回のattemptで書き起こしが
「示す、指し示す」に収束したが、これはcanonical(「～を示す、
～を指し示す」)とは一致しない(「を」が2箇所とも脱落)ため
`TRUE_CONTENT_MISMATCH`のままだった。**ハルシネーション級の異常長
(ER-005-AUDIO-WASTE-REDUCTION-01の閾値超過)は今回発生せず**、
全attemptが正常範囲内の長さだった。

日本語の`generate_charon_japanese`にはEnglish側と異なりdisfluency QA
(`er008_disfluency_qa_18`)が配線されていないため、disfluencyログは
存在しない(該当なし)。

### 2.4 cost

Production標準のGemini TTS Batch API(gemini-3.1-flash-tts-preview,
voice=Charon)+OpenAI ASR(gpt-4o-mini-transcribe)+ASR Cascade
(openai responses.create)の実費、計28 API call:

```
total_usd: 0.01012 (約1.62円)
  gemini_batch::batches.create        : $0.00851
  openai_asr::audio.transcriptions.create: $0.00064
  openai::responses.create            : $0.00097
```

計測方法: `er005_cost_logger.install()`(Production標準の計測経路)。
金額計算: `er011_open117_keyphrase_tilde_gate_recheck_01_cost_compute.py`
(`er011_specfix_cost_compute_01`の単価テーブルを利用、gemini_batch+
flashモデルのBatch単価のみ既存ER-011 Trialパターンと同様に個別補完)。

## 3. 確認2: placeholder検出ゲートの調査(read-only)

### 3.1 現行ロジック

`er003_audio_tts_asr_safety.py`:

```python
_GLOSS_PLACEHOLDER_CHARS = ("〜", "～", "…")  # U+301C / U+FF5E / U+2026

def detect_gloss_placeholder_notation(text: str) -> dict:
    text = text or ""
    found = [ch for ch in _GLOSS_PLACEHOLDER_CHARS if ch in text]
    return {"has_placeholder": bool(found), "found_chars": found, "text": text}
```

呼び出し側(`er003_v1_n3_01_tts_generate.py`
`generate_charon_japanese_with_reading_safety`/A2版)は、まず
`tts_safe_ja()`で**先頭の**「～」「〜」だけを`lstrip`し、その後の
テキストに対して`detect_gloss_placeholder_notation`を実行して
1文字でも見つかれば`STOPPED`(TTS呼び出し自体を行わない)。適用範囲は
Key Phrase日本語gloss(B1 kp_ja_charon、A2 meaning_N)経路に**限定**され、
Full Story等本文の「…」(間・余韻)には適用されない(コード確認済み)。

### 3.2 導入経緯(原文引用)

`ER-006-KP5-CANONICAL-BUG-01`(2026-08-22、commit `603fb16`):

> 2つの目的語を取る英語Key Phrase(例: "associate with")の
> japanese_glossを生成する際、LLMが辞書の見出し語定義でよく使われる
> 項変数記法(例:「〜を…と結びつける」)をそのまま出力することがある。
> 「〜」「…」はいずれも実際には発話されない記号であり、この記法のまま
> canonical_textとしてTTS/ASR比較へ渡すと、実際にどう発話させても原理的に
> 一致しようがない不良segmentになる(該当例: Public Benches B1 kp5_ja、
> **全12回のattemptがTRUE_CONTENT_MISMATCH/ASR_VALIDATION_UNCERTAIN**)。

つまり導入の直接の引き金は、二重slot型(「〜を…と結びつける」)の
未置換placeholderが実際に**12回TTS呼び出しされ、12回とも不合格**に
なった実インシデントだった(修正: 手動で「関連づける」へ書き換え)。

### 3.3 過去データ: 全13件の分類

全記事`keywords_canonicalized.json`をスキャンした結果、「～/〜/…」を
含むgloss13件を発見(Opus診断-15の報告「13件・ブロック形3件」と一致)。

| # | gloss | 位置 | 現行ゲート判定 | 分類 |
|---|---|---|---|---|
| 1 | ～への道を閉ざす | 先頭のみ | PASS(strip済み) | 辞書的slot(単一) |
| 2 | ～したい衝動 | 先頭のみ | PASS | 辞書的slot(単一、非助詞型) |
| 3 | ～に楽勝する | 先頭のみ | PASS | 辞書的slot(単一) |
| 4 | ～と関連している(health/a2) | 先頭のみ | PASS | 辞書的slot(単一) |
| 5 | ～と関連している(health/b1b) | 先頭のみ | PASS | 辞書的slot(単一) |
| 6 | 中～高強度の運動 | 中間 | **BLOCKED** | 範囲notation(placeholderではない) |
| 7 | ～の可能性が高いと見る | 先頭のみ | PASS | 辞書的slot(単一) |
| 8 | ～を…だと宣言する | 先頭+中間(「…」) | **BLOCKED** | 未解消の二重slot(本物のbug) |
| 9 | ～に新しい機会を開く | 先頭のみ | PASS | 辞書的slot(単一) |
| 10 | ～に後々まで影響を残す | 先頭のみ | PASS | 辞書的slot(単一) |
| 11 | 〜を説明する要因となる | 先頭のみ | PASS | 辞書的slot(単一) |
| 12 | 〜のデータを利用する | 先頭のみ | PASS | 辞書的slot(単一) |
| 13 | ～を示す、～を指し示す(Trial-13 kp4_ja) | 先頭+読点直後 | **BLOCKED** | 辞書的slot(二重、Trial-13の対象) |

「ブロック形3件」= #6・#8・#13。他10件は`tts_safe_ja()`の先頭stripのみで
ゲート到達前に解消されており、**現状ゲートには到達していない**。

### 3.4 追加発見(read-only、実Production記録) — 重要

ゲートを通過済み(PASS)の10件のうち、実際に本番TTS生成記録が
repo内に残っている6件を確認した(残り4件は該当パイプラインの
TTS段まで到達した記録が見つからなかった):

| gloss | 記録元 | 結果 |
|---|---|---|
| ～の可能性が高いと見る(#7) | novel_audio_01/SING01 | OK(attempt 1、NORMALIZED_MATCH相当) |
| ～に楽勝する(#3) | n3_01/hanshin/b1b | OK(**attempt 5**でようやく合格。現行の縮小予算[標準2+fallback1=計3回]では通らない) |
| ～に後々まで影響を残す(#10) | cost_baseline_01/parenting/a2 | OK(attempt 1、ただしASRが末尾を欠落「に後々まで影響？」でも許容判定) |
| 〜を説明する要因となる(#11) | cost_baseline_01/parenting/b1b | **STOPPED**(標準6回+fallback6回、計12回全て不合格。当時は旧[pre-ER-007]の厳格な文頭一致方式) |
| 〜のデータを利用する(#12) | cost_baseline_01/parenting/b1b | **STOPPED**(同12回。うち2回は**121秒・84秒の指示文パラフレーズ型ハルシネーション**を含む。ER-005-AUDIO-WASTE-REDUCTION-01[異常長検知]導入前の記録) |
| ～に新しい機会を開く(#9) | cost_baseline_01/akb48/a2 | **STOPPED**(標準6回+fallback6回、計12回**全てASR書き起こし空**=完全な無音・未検出) |

6件中3件がSTOPPED(約50%)。これは「ゲートを通過した=安全」ではなく、
「ゲートの通過は先頭の記号を消しただけで、裸の助詞から始まる本質的な
不安定さは解消していない」ことを示す実データである(ER-005の異常長
検知導入前の記録のため、現行実装では121秒級のハルシネーションは
ASR前に破棄されるが、より軽度な「misreadingで内容不一致」「無音」の
リスクは異常長検知の対象外)。

## 4. 検討: 許可条件案の評価

課題で提示された案(文頭または読点直後の「～」+直後が助詞
[を/に/が/と/へ/の/で]、かつ他のplaceholder記号なし、かつgloss限定)を
13件へ当てはめると、対象になるのは#13(Trial-13 kp4_ja)のみ(#6は
位置条件を満たさず、#8は「…」を含むため除外され、いずれも現状通り
BLOCKEDのまま)。

しかし確認1のTrial結果が示す通り、#13を実際にTTSへ通しても
**3回とも`TRUE_CONTENT_MISMATCH`**であり、許可条件を追加しても
使える音声にはならない。むしろ、現行ゲートが**TTS/ASR呼び出し
0回で即STOPPEDにする**ことで、失敗が予見できるケースへ無駄な
TTS/ASR費用・retry予算(review lockの累計試行数)を消費させずに
済んでいる、という積極的な効果があることが確認できた。

したがって、**許可条件案は`REJECTED`**(TTS上・安全性上、許可すべき
ではない。効果がないだけでなくコスト・予算の浪費になる)。

TTS投入前に「～」を除去/置換する正規化(「～を示す」→「何かを示す」
等)については、実質的にこれは「gloss自体を書き換える」ことと同義であり、
機械的な自動置換(「何か」を一律挿入する等)は文脈によって不自然な
訳文を生む可能性がある。この役割は既にPrompt側の規約B(下記)が
担うべきものであり、TTS直前の正規化として重複実装する必要性は
低いと判断した。

## 5. Prompt規約Bの扱い

`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`
(A2/B1共有、2026-09-06 ER-011-KP-VALIDATOR-...-WIRING-03でProduction配線済み):

> 日本語グロスには「～」「〜」「…」のようなプレースホルダー記号を
> 一切使わないでください。動詞句などで目的語を省略した言い方に
> したい場合は、日本語として自然な言い切りの形(例:
> 「～を示す」ではなく「示す、指し示す」)へ書き換えてください。

この規約Bの例示(「～を示す」→「示す、指し示す」)は、単に記号を
消すのではなく**裸の助詞ごと省略する**書き換えパターンを指示しており、
本Trialで発見した根本原因(裸の助詞始まりの断片がTTSにとって不安定)を
直接解消する設計になっている。範囲も「～」「〜」「…」の**全形を
一律禁止**しており、#6(範囲notation)のような非slot用法も含め
規約Aと合わせて適切にカバーされている。

**結論: 規約Bは維持すべき(撤回・縮小のいずれも不要)**。ゲートは
規約Bをすり抜けた場合の二重防御(defense-in-depth)として引き続き
有効に機能しており、範囲を狭める理由はない。

なお、規約Bは2026-09-06配線のため、3.4節で確認した10件の過去artifactは
いずれも規約B配線**以前**の記録である。新規記事では規約Bにより
再発しにくいと考えられるが、これらの過去artifactに対応する**既に
生成済みの音声資産**(公開済みのものがあれば)を本Trialの知見で
再点検するかどうかは、本タスクの範囲外でありユーザー判断が必要。

## 6. Closeout分類

**VALIDATED**(ゲート・Prompt規約Bとも現状維持が妥当。緩和条件案は
`REJECTED`)。過去artifact(音声資産)再点検の要否のみ
`USER_DECISION_REQUIRED`。

## 7. PM向けの選択肢(実装しない、報告のみ)

1. 何もしない(推奨) — ゲート・規約Bとも現状維持。新規記事は規約Bで
   保護され、ゲートは二重防御として機能する。
2. 過去artifact(10件中、実際に本番音声が生成されTTS段まで到達した
   記録がある記事)の音声を人力で再点検し、規約B配線前の資産に
   実際の品質問題(#3の5回目合格分等)が残っていないか確認する。
3. (非推奨、`REJECTED`理由あり)ゲートへ許可条件を追加する。

## 8. Production変更なしの確認

- `er003_audio_tts_asr_safety.py`(ゲート本体): 無変更。
- `er003_v1_n3_01_tts_generate.py`(呼び出し側): 無変更。
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`
  (規約A/B): 無変更。
- `CURRENT_SPEC.md`: 無変更。
- monkeypatch: 使用していない(低レベル関数を直接呼んだのみ)。
- status格上げ: なし。

## 9. 証跡

- Trial script: `er011_open117_keyphrase_tilde_gate_recheck_01.py`
- Cost計算script: `er011_open117_keyphrase_tilde_gate_recheck_01_cost_compute.py`
- 出力: `er011_output/open117_keyphrase_tilde_gate_recheck_01/`
  (`results_open117.json`, `cost_summary_open117.json`,
  `raw_usage_log_open117.jsonl`, `trial/narration/*.wav`, `player.html`)
- 過去データ根拠(read-only、repo内既存ファイル):
  `er003_output/n3_01/hanshin/b1b/audit/tts_generation_results.json`、
  `er003_output/novel_audio_01/SING01/audit/{voice01_generation_results.json,kp5_ja_fix_result.json}`、
  `er005_output/cost_baseline_01/{akb48,parenting}/{a2,b1b}/audit/tts_generation_results.json`
