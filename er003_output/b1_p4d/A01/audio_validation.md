# ER-003-B1-P4D 完了レポート(全文ひらがな読み正規化・日本語Preview検証)

## 1. 結論

承認済みPattern Aを5 used form→「目印」置換→SudachiPy全文ひらがな読み正規化→
1回のTTS callという方式で、日本語raw音声を生成した。静的検証(禁止文字残存0・
marker5回・文数一致・句読点順序一致)は全項目合格。重点3表現(`最後の数分`・
`守備を固め`・`わずかなリード`)は、TTS前の期待変換結果・生成音声のASR認識結果
(同じ読み正規化処理を通した比較)の両方で、期待通りの変換を確認した。
**指示通り、ここで停止する(MFA・英語Component置換・Dynamics3・B1本文・通し
音声には進んでいない)。**

## 2. branch / HEAD

| 項目 | 値 |
|---|---|
| branch | main |
| このステージの変更前HEAD | `19742016e27f9820bc1910a6f5d2227357695202`(P4C完了コミット) |

## 3. Pattern A source / 5 used forms

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p2/A01/listening_preview_raw.md` |
| sha256 | `5b986705e6a55163bcc6cb6ab92a2d3a6be1970ab1b8c7adebd67ba2732aa500` |
| 文字数 | 277 |

```
shot on target
take players off
a narrow lead
close the door to the final
stoppage time
```

## 4. marker置換後source

5つのused formを出現順に「目印」へ置換(`er003_b1_p4d_audio.build_marker_replaced_source`)。
置換件数5、used form残存すべて0を確認。保存先: `source/pattern_a_with_markers.txt`。

## 5. 読み正規化の実装方式

| 項目 | 値 |
|---|---|
| tokenizer | SudachiPy `Dictionary().create()`(既定split mode) |
| 実行環境 | 隔離MFA環境(`mfa_tool/envs/mfa`、既にSudachiPy導入済み)。アプリ本体`.venv`にはsudachipyを追加していない |
| 呼び出し方法 | `er003_b1_p4d_sudachi_tokenize_helper.py`をmicromamba経由でサブプロセス実行(既存の`er003_b1_p3w_audio.run_mfa_align`と同じ隔離方式) |
| 変換規則 | 品詞大分類が「補助記号」(句読点・ダッシュ等)のtokenはsurfaceをそのまま保持。それ以外はreading_form(カタカナ)を機械的にひらがな化(Unicodeオフセット-0x60、U+30A1〜U+30F6の範囲のみ。長音記号「ー」は対象外でそのまま保持) |
| 語句別例外 | なし(品詞分類による一般規則のみ。個々の単語・表現ごとの辞書登録は一切行っていない) |

実装時、SudachiPyが記号類(「―」等)のreading_formに実際の読みではない汎用ラベル
「キゴウ」(=「記号」のカタカナ)を返すことを実機確認した。これを他の単語と同様に
機械変換すると「きごう」という誤った読み上げ文字列が生じるため、品詞が補助記号の
tokenだけはsurfaceを保持する一般規則を設けた(個別の記号ごとの例外ではなく、
品詞分類全体に適用される規則)。

## 6. tokenizer / dictionary / split mode

`sudachipy.Dictionary().create()`のデフォルト設定(追加の辞書・split mode指定なし)。
既存のMFA日本語tokenizer検証(P3W〜P4Cで確立済みの隔離環境)と同一のライブラリを
再利用している。

## 7. 全文ひらがなscript / reading map

| 項目 | 値 |
|---|---|
| path | `source/pattern_a_full_hiragana.txt` |
| sha256 | `fb9ea8c9ef6740fd83fe905199d987609b2eba9e8ec79b6c3437dee17493bd5b` |
| reading_map path | `source/reading_map.json` |
| token数 | 119 |

## 8. 変換不能token・禁止文字残存・語句追加欠落

| 項目 | 結果 |
|---|---|
| 変換不能token数 | 0 |
| ASCII英字残存 | 0 |
| Arabic numeral残存 | 0 |
| 漢字残存 | 0 |
| カタカナ文字残存(長音記号「ー」除く) | 0 |
| 「めじるし」出現数 | 5(想定通り) |
| 文数一致(source=4, script=4) | 一致 |
| 句読点並び一致 | 一致 |
| token surface復元 = marker置換後source | 一致(tokenize結果の欠落なし) |
| **総合判定** | **全項目合格** |

## 9-11. 重点3表現の変換結果(TTS前の期待値)

| 表現 | source | 期待変換 | present |
|---|---|---|---|
| 最後の数分 | 最後の数分 | `さいごのすうふん` | はい |
| 守備を固め | 守備を固め | `しゅびをかため` | はい |
| （比較用）禁止形 | ― | `しゅびをかためる` | **含まれない**(確認済み) |
| わずかなリード | わずかなリード | `わずかなりーど` | はい |

`守備を固め`は連用形「固め」のreading_form(カタメ)をそのまま使っており、辞書形
「固める」の読み(カタメル)を使っていないため、`しゅびをかためる`化は起きていない。

## 12. 日本語instruction全文

> 次の文章を、翻訳・言い換えせず、日本語のまま読み上げてください。

Voice=Aoede, Emotional + Connected, Level 2, speed number指定なし, solo narration。
P3Y以降の言語指定行以外は無変更。

## 13. TTS call count / retry count

1回のTTS callで成功(技術的retry 0回)。全文ひらがなscriptをchunk分割せず、1回で
生成した(指示通り)。

## 14. raw path / duration / sha256

| 項目 | 値 |
|---|---|
| path | `preview/raw/A01_preview_full_hiragana_with_markers.wav` |
| duration | 32.171秒 |
| sha256 | `f376a7cd31eb01e3e1e80a09b783cd2a2fd23c7938d2d9694d5c2d505f069866` |

## 15-16. ASR transcript / 読み正規化結果

ASR認識結果(診断用、境界決定には未使用):

> 前半は激しい接触と緊張が続き、両チームとも枠内周と目印を記録できないまま、
> 静かな均衡が保たれます。後半に試合が動くと、イングランドは選手を交代。目印で
> 守備を固め、わずかなリード目印を守ろうとします。アルゼンチンの決勝への道を
> 閉ざすこと。目印が現実になりそうなその時、メッシが流れを変え、ついに
> アディショナルタイム目印へ。最後の数分、寒気と痛みの境目で何が起きるのでしょうか。

同じ読み正規化処理(marker置換なしでそのままtokenize→ひらがな化)を通した結果
(`asr/asr_reading_normalized.txt`)は以下の通り(先頭のみ抜粋):

> …こうはんにしあいがうごくと、いんぐらんどはせんしゅをこうたい。めじるしで
> しゅびをかため、わずかなりーどめじるしをまもろうとします。…さいごのすうふん、
> さむけといたみのさかいめで…

## 17. 重点3表現のASR結果

| 表現 | ASR読み正規化後の対応部分 | present |
|---|---|---|
| 最後の数分 | 「さいごのすうふん」 | はい |
| 守備を固め | 「しゅびをかため」(「しゅびをかためる」は含まれない) | はい |
| わずかなリード | 「わずかなりーど」 | はい |

## 18. decode / clipping

decode: OK。clipping: 検出なし(clipping_sample_count=0)。

## 19-20. MFA実行・英語TTS call

MFA実行: 0回。英語TTS call: 0回(指示通り未実施)。

## 21. Dynamics 3適用

0回(指示section12の明記通り、読み・声色・抑揚をraw状態で評価するため未適用)。

## 22. B1本文生成

未実施。

## 23. tests / validation

- `er003_test_b1_p4d_audio.py`(新規29件、隔離環境への実サブプロセス呼び出しを
  含む統合テスト1件を含む): 全合格
- プロジェクト全体の既存テストスイート: 1063件全合格(discover実行、回帰なし)

## 24. 内容確認(全文ASR診断)の補足

生成直後の全文ASR診断(`check_full_text_content`)結果:

| 項目 | 結果 |
|---|---|
| 日本語比率 | 0.9305(日本語と判定) |
| 意図しない英語混入 | なし |
| 「目印」出現数 | 5(想定通り) |
| marked_text(marker置換後・変換前)との一致率 | 0.9366 |

一致率は高いが、「選手を交代で下げる、目印という決断で守備を固め」の部分が
ASR上「選手を交代。目印で守備を固め」と、一部語句(「下げる」「という決断」)が
欠落しているように認識された。これがTTS自体の発話漏れなのか、ASRの認識漏れ
なのかは、本レポートでは断定していない(機械的に切り分けられないため)。試聴で
ご確認ください。

## 25. ユーザーへの確認事項(指示section18)

`preview/raw/A01_preview_full_hiragana_with_markers.wav`を試聴のうえ、次を
ご判断ください。

- 声色・テンションが全文で連続しているか(短文分割方式との比較)
- `最後の数分`が自然に聞こえるか
- `守備を固め`が原稿どおり(「かためる」化していない)か
- `わずかなリード`の抑揚が自然か
- 「選手を交代で下げる、目印という決断で守備を固め」付近に、聞こえ方の異常
  (欠落・不明瞭)がないか(ASR上は一部欠落して聞こえた)
- 全文ひらがな方式が、今後の量産方式の候補になり得るか

このステージはB1本文・通し音声には進んでいません。次のステップは、この試聴
結果を踏まえてご指示ください。
