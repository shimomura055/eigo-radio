# ER-003-B1-P3Z 比較一覧(英語前後の間・9パターン)

音声内容・語順・処理条件はすべてのパターンで同一。変更したのは英語(shot on target)
前後の実効的な間(既存componentの自然な無音・安全余白を含めた最終音声上の実測値)のみ。
新しいTTS生成・MFA再実行・原稿変更は行っていない(既存3component: `er003_output/b1_p3y/A01/
components/ja_before_marker.wav`・`en_shot_on_target_trimmed.wav`・`ja_after_marker.wav`
を再利用)。

| No. | ファイル名 | 目標・英語前 | 実測・英語前 | 目標・英語後 | 実測・英語後 | duration | 判定 |
|---|---|---|---|---|---|---|---|
| 01 | `01_A01_gap_before_0p2s_after_0p2s_dynamics3.wav` | 0.2秒 | 0.2秒 | 0.2秒 | 0.2秒 | 11.302秒 | OK |
| 02 | `02_A01_gap_before_0p2s_after_0p3s_dynamics3.wav` | 0.2秒 | 0.2秒 | 0.3秒 | 0.3秒 | 11.402秒 | OK |
| 03 | `03_A01_gap_before_0p2s_after_0p4s_dynamics3.wav` | 0.2秒 | 0.2秒 | 0.4秒 | 0.4秒 | 11.502秒 | OK |
| 04 | `04_A01_gap_before_0p3s_after_0p2s_dynamics3.wav` | 0.3秒 | 0.3秒 | 0.2秒 | 0.2秒 | 11.402秒 | OK |
| 05 | `05_A01_gap_before_0p3s_after_0p3s_dynamics3.wav` | 0.3秒 | 0.3秒 | 0.3秒 | 0.3秒 | 11.502秒 | OK |
| 06 | `06_A01_gap_before_0p3s_after_0p4s_dynamics3.wav` | 0.3秒 | 0.3秒 | 0.4秒 | 0.4秒 | 11.602秒 | OK |
| 07 | `07_A01_gap_before_0p4s_after_0p2s_dynamics3.wav` | 0.4秒 | 0.4秒 | 0.2秒 | 0.2秒 | 11.502秒 | OK |
| 08 | `08_A01_gap_before_0p4s_after_0p3s_dynamics3.wav` | 0.4秒 | 0.4秒 | 0.3秒 | 0.3秒 | 11.602秒 | OK |
| 09 | `09_A01_gap_before_0p4s_after_0p4s_dynamics3.wav` | 0.4秒 | 0.4秒 | 0.4秒 | 0.4秒 | 11.702秒 | OK |

全9パターンで実測誤差0秒(許容誤差±0.03秒に対して十分小さい)。

## 調整方法

`en_shot_on_target_trimmed.wav`自体の前後安全余白(P3Uで設定済み、各0.08秒)は変更していない。
目標の実効間隔は、`ja_before_marker.wav`の末尾無音と`ja_after_marker.wav`の先頭無音だけを
調整して達成した(トリム/パディングいずれも発話部分には一切触れていないことを、各パターンの
`before_adjustment.speech_content_unchanged`/`after_adjustment.speech_content_unchanged`
(すべて`true`)で確認済み。詳細は[`audio_metadata.json`](audio_metadata.json)参照)。

## 保存先

```
er003_output/b1_p3z/A01/final/
```

各ファイルはDynamics3を1回のみ適用済み(9パターン共通の固定パラメータ)。

## 試聴・最終判断

音声の自然さ(特にどの間隔が最も聞き取りやすいか)は機械承認せず、ユーザーが9ファイルを
比較して判断してください。
