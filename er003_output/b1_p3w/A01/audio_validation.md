# ER-003-B1-P3W 音声検証レポート(機械確認のみ、自然さ・聞きやすさの判定なし)

## 1. Step 1/2: MFA環境確認・スモークテスト

| 項目 | 結果 |
|---|---|
| MFA隔離環境(mfa_tool/) | 存在確認OK |
| スモークテスト対象 | `er003_output/b1_p3t/A01/raw/ja_full_sentence.wav`(既存音声、再利用) |
| スモークテストsha256 | `a239ef34a7623be6c82d9d7994647f18df0423d684e13c3e990ebe8d559b19bd` |
| スモークテスト語順一致 | 一致(22語、原稿順と完全一致) |

詳細: [`environment/mfa_environment_report.md`](environment/mfa_environment_report.md) 相当の情報は
`audio_metadata.json`の`env_check`に記録。TextGrid: [`environment/smoke_test_ja_full_sentence.TextGrid`](environment/smoke_test_ja_full_sentence.TextGrid)

## 2. Step 3: マーカー入り日本語音声

| 項目 | 結果 |
|---|---|
| TTS用一時原稿 | 「前半は激しい接触と緊張が続き、両チームとも枠内シュート、キーワード挿入位置を記録できないまま、静かな均衡が保たれます。」 |
| マーカー語出現回数(原稿内) | 1回 |
| 生成音声 | `raw/ja_with_spoken_marker.wav`、10.811秒、decode OK、clippingなし |

**訂正の開示**: Step4(alignment)の失敗原因調査中、既存の生成済み音声を確認せずスクリプトを
再実行してしまい、意図せず2回目の実TTS呼び出しが発生した(本ステージ合計でTTS呼び出し2回)。
最終的にadoptしたのは2回目の生成結果であり、以降は既存ファイルを再利用する形へスクリプトを
修正済み。詳細は`audio_metadata.json`の`ja_tts_note`を参照。

## 3. Step 4: MFA alignment

| 項目 | 結果 |
|---|---|
| 使用モデル | acoustic: japanese_mfa、dictionary: japanese_mfa |
| 初回結果(デフォルトビーム) | `NoAlignmentsError`(1発話で整列パス0件) |
| 原因 | Kaldiデコーダの探索幅不足(語彙・無音長・ASR等とは無関係な、MFA標準のビーム幅パラメータの問題と実機診断で特定) |
| 対処 | `--beam 100 --retry_beam 400`(MFA公式エラーメッセージが提示する標準的な対処)を採用し再実行 |
| 最終結果 | 成功 |
| マーカーtoken列(実際の認識) | 「キーワード」→「挿入」→「位置」(辞書内の3語へ分割認識。マーカー語間に短い無音intervalが入ったが、無音を除いた語順一致で連続と判定) |
| 直前token | 「シュート」(5.36〜5.79秒) |
| マーカー区間 | 5.79〜6.71秒(0.92秒) |
| 直後token | 「を」(6.71〜6.82秒) |

無音長・ASRタイムスタンプ・GPTによる位置推測はいずれも使用していない。境界特定の根拠はMFAの
alignment結果(TextGrid)の語順一致のみ。

## 4. Step 5: マーカー区間の英語音声への置換

| 項目 | 結果 |
|---|---|
| 使用した英語音声 | `er003_output/b1_p3u/A01/components/en_shot_on_target_trimmed.wav`(既存、再TTS生成なし) |
| sha256 | `82a4b01ea4dc466b72190f91b350df69f2ab340438a04c096d5452b1201f418b` |
| duration | 1.231秒 |
| ja_before_marker duration | 5.790秒(0〜5.79秒) |
| ja_after_marker duration | 4.101秒(6.71秒〜末尾) |
| マーカー区間削除 | `remove_marker_span`により[5.79, 6.71)を完全に削除(前後は単純なスライスのみで、マーカー音声内容は一切再利用しない。単体テストで内容非混入を確認済み) |
| 「枠内シュート」末尾の欠落 | なし(ja_before_markerは「シュート」終了時刻5.79秒までを保持) |
| 「を」先頭の欠落 | なし(ja_after_markerは「を」開始時刻6.71秒から保持) |

## 5. 結合(0.12秒固定ポーズ)・マーカー残存確認

| 項目 | 結果 |
|---|---|
| 順序 | ja_before_marker → 0.12秒 → en_shot_on_target_trimmed → 0.12秒 → ja_after_marker |
| 境界無音1(挿入直前) | RMS 0.0(完全無音)、長さ0.12秒(仕様通り) |
| 境界無音2(挿入直後) | RMS 0.0(完全無音)、長さ0.12秒(仕様通り) |
| マーカー語の残存 | 0(マーカー区間[5.79,6.71)はja_before/ja_afterのいずれにも含まれない。スライス処理のみで内容混入なしを単体テストで確認済み) |
| `shot on target`使用回数 | 1回 |
| 日本語語順の変更 | なし |
| 0.5秒を超える無音区間(全体スキャン) | 検出なし(想定外の長い無音は存在しない) |

## 6. duration整合性

ja_before(5.790秒)+ 境界無音(0.12秒)+ en(1.231秒)+ 境界無音(0.12秒)+ ja_after(4.101秒)
= 11.362秒。raw結合音声の実測durationと完全一致。

## 7. 結合音声(raw / final)

| 項目 | raw | final(Dynamics3適用後) |
|---|---|---|
| decode | OK | OK |
| duration | 11.362秒 | 11.362秒 |
| clipping | 検出なし | 検出なし |
| peak dBFS | -3.1 | -2.53 |
| integrated LUFS(概算) | -18.74 | -18.74 |

Dynamics3は1回のみ適用(固定パラメータ: threshold_percentile=60, ratio=8:1, knee=6dB,
attack=5ms, release=200ms)。ラウドネスは元のC0(-18.74 LUFS)に整合(誤差0.0 LU、目標0.3 LU以内)。

## 8. 承認済み原稿・非対象範囲の確認

| 項目 | 結果 |
|---|---|
| 承認済み原稿の意味変更 | 0(TTS用一時原稿はマーカー語を1箇所追加しただけで、それ以外の語彙・語順・助詞は無変更) |
| Pattern A全文生成 | 0 |
| B1本文生成 | 0 |
| GPTによる挿入位置推測 | 0 |
| ASR境界推定 | 0 |
| 最長無音利用 | 0 |

## 9. 対象外(ユーザー判断が必要)

音声の自然さ、イントネーション、「を」の聞こえ方、マーカー語間の短い間が完成音声の
自然さに影響しているかは、本レポートでは判定していません。試聴の上でご判断ください。
