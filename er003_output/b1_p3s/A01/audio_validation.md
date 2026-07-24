# ER-003-B1-P3S 音声検証レポート(機械確認のみ、自然さ・聞きやすさの判定なし)

## 1. 単独span(3ファイル)

| span | 存在 | decode | duration(秒) | sample rate | channels | peak(abs) |
|---|---|---|---:|---:|---:|---:|
| span_01_ja_before | OK | OK | 5.611 | 24000 | 1 | 0.700 |
| span_02_en_keyword | OK | OK | 1.891 | 24000 | 1 | 0.700 |
| span_03_ja_after | OK | OK | 4.251 | 24000 | 1 | 0.700 |

- 3ファイルとも存在し、decode可能、duration > 0。
- peak(abs)が3ファイルとも0.700で揃っているのは、`er002_common.normalize_pcm`(採用済み、目標ピーク0.7)がチャンク単位に適用された結果であり、想定通り。
- 冒頭・末尾切れ・意図しない長い無音は、durationが各spanの実発話量と整合していることから確認(極端な過不足なし)。

## 2. 結合サンプル

| 項目 | 結果 |
|---|---|
| 結合順 | span_01_ja_before → span_02_en_keyword → span_03_ja_after(日本語→英語→日本語) |
| 各span使用回数 | 1回ずつ(重複・欠落なし) |
| 境界無音 | 0.2秒 × 2箇所 |
| 無音箇所1のRMS | 0.0(完全無音) |
| 無音箇所2のRMS | 0.0(完全無音) |
| raw(Dynamics3適用前)decode | OK、12.153秒 |
| final(Dynamics3適用後)decode | OK、12.153秒 |
| sample rate / channels | 24000Hz / 1(モノラル) |
| clipping(raw) | 検出なし(clipping_sample_count=0) |
| clipping(final) | 検出なし(clipping_sample_count=0) |
| Dynamics3適用 | 適用済み(1回のみ、`dynamics3_applied=true`) |
| ラウドネス整合 | target -20.5 LUFS → final -20.5 LUFS approx(誤差0.0 LU、目標0.3 LU以内) |

## 3. duration整合性

各spanのduration合計(5.611 + 1.891 + 4.251 = 11.753秒)+ 境界無音2箇所(0.2秒 × 2 = 0.4秒) = 12.153秒。結合サンプルの実測durationと完全一致。

## 4. source変更確認

Pattern A source(`er003_output/b1_p2/A01/listening_preview_raw.md`)のsha256は、実行前後で一致(`0ed84df5...`で不変)。

## 5. API呼び出し・再試行

| span | call数 | retry数 |
|---|---:|---:|
| span_01_ja_before | 1 | 0 |
| span_02_en_keyword | 2 | 1(技術的失敗による1回のみの再試行、同一payload) |
| span_03_ja_after | 1 | 0 |

品質目的の再生成は行っていない(全て技術的成否のみで判定)。

## 6. 対象外(ユーザー判断が必要)

音声の自然さ、同じ話者に聞こえるか、日英切替の違和感、間(0.2秒)の適切さは、本レポートでは判定していません。試聴の上でご判断ください。
