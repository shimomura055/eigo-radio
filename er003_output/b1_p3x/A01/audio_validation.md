# ER-003-B1-P3X 音声検証レポート(停止のため大部分が対象外)

本ステージはStep 2の分岐A(「`ja_with_spoken_marker.wav`が英語」)に該当すると判定し、
Step 5(既存音声だけでの再結合)へは進まず停止した。そのため、指示section「修正後の
必須確認」の大半は実施していない(対象となる修正後音声が存在しないため)。

## 実施した確認(Step 1・Step 2)

| 項目 | 結果 |
|---|---|
| 各既存音声のsha256・duration記録 | 完了([`diagnostics/audio_lineage_before_fix.json`](diagnostics/audio_lineage_before_fix.json)) |
| 各既存音声の実際の言語・内容確認(診断用ASR) | 完了([`diagnostics/content_check.md`](diagnostics/content_check.md)) |
| 最初に英語化した工程の特定 | 完了。TTS応答そのもの(Step 3)が既に英語(`raw/ja_with_spoken_marker.wav`) |
| 根本原因の特定 | 完了([`root_cause_report.md`](root_cause_report.md)) |
| Pythonコード側(切り出し・結合)の健全性確認 | 完了。問題なし(frame範囲・concat順・境界無音・sha256整合はいずれも指示通り) |
| en_shot_on_target_trimmed.wavがP3U成果物と一致 | 一致(sha256完全一致) |

## 実施しなかった確認(対象音声が存在しないため)

以下は「修正後の必須確認」に含まれるが、有効な日本語sourceが存在せず再構築(Step 5)を
行っていないため、対象外とする。

- 日本語前半/後半が実際に日本語であること
- final rawが日本語→英語→日本語であること
- `キーワード挿入位置`が残っていないこと
- `を`が英語の後にあること
- fixed final(raw/Dynamics3適用後)のdecode・clipping確認

## 新規TTS呼び出し

0回。既存音声(`raw/ja_with_spoken_marker.wav`、`components/en_shot_on_target_trimmed.wav`、
診断用複製`mfa_tool/fresh_marker_corpus/test_fresh.wav`)の読み込み・診断のみを行った。

## テストについて

本調査の結果、Pythonコード側(`er003_b1_p3w_audio.py`/`er003_v1_b1_p3w_generate.py`)には
バグが見つからなかった(lineage追跡により、切り出し・結合処理はいずれも指示通り正しく
動作していることを確認済み)。そのため、production コードの変更は行っておらず、新規の
単体テスト追加も行っていない。既存のP3W関連テスト(28件)を再実行し、変更なしで
全件PASSすることを確認した(回帰なし)。

## 対象外(ユーザー判断が必要)

音声の自然さの判断は本来対象外だが、そもそも今回は日本語であるべき音声が英語だったため、
自然さ以前の問題として試聴は推奨しない。今後の対応方針(再生成を許可するか、別の
マーカー語・別の方式を検討するか等)はユーザーが判断してください。
