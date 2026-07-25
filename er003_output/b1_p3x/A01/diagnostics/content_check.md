# ER-003-B1-P3X Step 1: 各音声の実内容確認(診断用ASR使用、境界決定には使用せず)

診断には Azure Cognitive Services Speech-to-Text(P3U/P3Wで既に使用実績のある既存依存関係)を、
言語を明示指定して使用した。境界(時刻)の決定には一切使用していない。あくまで「その音声が
実際に何語で何を話しているか」を確認するための診断用途に限定した。

## 対照(健全性確認): 既知に正しい日本語音声

| 項目 | 結果 |
|---|---|
| 対象 | `er003_output/b1_p3t/A01/raw/ja_full_sentence.wav`(P3T成果物、修正なし) |
| ja-JP認識結果 | 「前半は激しい接触と緊張が続き今日チームとも枠内シュートを記録できないまま静かな均衡が保たれます」 |
| 判定 | 期待通り日本語(「両」が「今日」と誤認識される既知の癖はあるが、全体として日本語音声であることは明確) |

この対照確認により、診断ツール自体は日本語音声を正しく日本語として認識できることを確認した
(診断ツールの誤設定による偽陽性ではない)。

## 診断対象1: `raw/ja_with_spoken_marker.wav`(現在のファイル、2回目のTTS生成結果)

| 項目 | 結果 |
|---|---|
| path | `er003_output/b1_p3w/A01/raw/ja_with_spoken_marker.wav` |
| sha256 | `56349635d1fe8f49d29f88aacf62676e13ef99cad3bada9c1fdeeff99632c1cb` |
| duration | 10.811秒 |
| sample rate / channels | 24000Hz / 1 |
| ja-JP認識結果 | 英単語がローマ字的に連結された文字列(日本語として認識不能。実質英語) |
| en-US認識結果 | "the first half is marked by intense physical contact and a sense of tension with both teams unable to register a shot on goal leading to a quiet stalemate"(流暢な英文) |
| 期待内容 | マーカーを含む日本語全文 |
| 判定 | **一致しない。英語。日本語ではない。** |

## 診断対象2: マーカー音声1回目の生成結果(現在は上書きされ現存しないが、診断作業中に取得した複製が残存)

| 項目 | 結果 |
|---|---|
| 複製path | `mfa_tool/fresh_marker_corpus/test_fresh.wav` |
| sha256 | `f3856d4283c95c557f8e63425894cd7bc177d0d674a6b833c82289bc8a3432da`(P3W1回目TTS呼び出し結果と一致) |
| duration | 11.491秒 |
| ja-JP認識結果 | 英単語がローマ字的に連結された文字列(日本語として認識不能) |
| 認識内容(意訳される英文) | "the first half brought cracking contact and attends atmosphere with both teams failing to register a shot on target, a shattered mutual silent equilibrium" |
| 判定 | **こちらも英語。日本語ではない。1回目・2回目とも独立して英語化していた。** |

1回目と2回目で文言が異なる(単なるバッファの使い回しではなく、それぞれ独立してTTSが実行され、
その都度異なる英語の言い回しを生成したことを示す)。

## 診断対象3〜5: components(切り出し結果)

| ファイル | ja-JP/en-US認識結果 | 判定 |
|---|---|---|
| `components/ja_before_marker.wav` | "the first half is marked by intense physical contact and a sense of tension with" | 英語。期待(日本語)と不一致 |
| `components/en_shot_on_target_trimmed.wav` | "shot on target" | 期待通り(英語のKey Phraseとして正しい) |
| `components/ja_after_marker.wav` | "to register a shot on goal leading to a quiet stalemate" | 英語。期待(日本語)と不一致 |

## 診断対象6: `final/A01_b1_mfa_marker_replacement_raw.wav`

| 項目 | 結果 |
|---|---|
| 判定 | 英語+英語+英語(3コンポーネントを指示通りの順で結合しているが、日本語であるべき前後2コンポーネントが既に英語だったため、全体が英語のまま) |

## 結論

`raw/ja_with_spoken_marker.wav`(TTS生成の時点、Pythonによる切り出し・結合処理より前)が
既に英語であることを確認した。これはStep 2の分岐A(「`ja_with_spoken_marker.wav`が英語」)に
該当する。詳細な根本原因は[`../root_cause_report.md`](../root_cause_report.md)を参照。
