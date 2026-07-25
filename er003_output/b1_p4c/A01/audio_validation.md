# ER-003-B1-P4C 完了レポート(「目印」マーカーでListening Preview完成版を再生成)

## 1. 結論

P4Bで停止したchunk05(`stoppage time`)を含め、6chunk全てが1回の生成で内容確認に
合格し、5つのmarker chunk全てでMFAが「目印」の区間を1件ずつ特定できた。5つの
英語Key Phraseへの置換・前後間隔の調整・6chunk結合・Dynamics3適用まで完了し、
Listening Preview完成版(raw / Dynamics3)を生成できた。**B1本文・Preview+本文の
結合音声は生成していない(本ステージのスコープ外)。**

## 2. branch / HEAD

| 項目 | 値 |
|---|---|
| branch | main |
| このステージの変更前HEAD | `53122ca981a54a4532314a4fbd8f5066d68fd50b`(P4B停止コミット) |

## 3. Pattern A source

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p2/A01/listening_preview_raw.md` |
| P4Bとの一致確認 | `source_hashes.json`のpattern_a_text_sha256がP4Bと同一。Pattern A変更0 |

## 4. Chunk構成(P4Bの6chunk構成を再利用)

| chunk_id | 種別 | Key Phrase | source_text |
|---|---|---|---|
| 01 | marker | shot on target | 前半は激しい接触と緊張が続き、両チームとも枠内シュート、shot on targetを記録できないまま、静かな均衡が保たれます。 |
| 02 | marker | take players off | 後半に試合が動くと、イングランドは選手を交代で下げる、take players offという決断で守備を固め、 |
| 03 | marker | a narrow lead | わずかなリード、a narrow leadを守ろうとします。 |
| 04 | marker | close the door to the final | アルゼンチンの決勝への道を閉ざすこと――close the door to the final――が現実になりそうなその時、 |
| 05 | marker | stoppage time | メッシが流れを変え、ついにアディショナルタイム、stoppage timeへ。 |
| 06 | normal | (なし、「最後の数分」を含む) | 最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。 |

TTS textはused formを「目印」へ置換したもの(chunk06は無変更)。

## 5. Source復元・静的検証結果

| 項目 | 結果 |
|---|---|
| 6chunk結合 → 承認済みPattern A原文 | 完全一致 |
| marker chunk数 | 5 |
| normal chunk数 | 1 |
| marker chunk毎のused form残存(source/TTS) | source1回・TTS0回、全chunk合格 |
| TTS text内「目印」出現数 | marker chunk毎に1回、合計5回 |
| ASCII英字残存 | 全chunkで0 |
| **総合判定** | **全項目合格、TTS実行可** |

## 6. 日本語instruction全文(P3Y以降で確立、無変更)

> 次の文章を、翻訳・言い換えせず、日本語のまま読み上げてください。

設定: Voice=Aoede, Emotional + Connected, Level 2, speed number指定なし, solo narration。
(LEVEL2_INSTRUCTION・POINT_LABEL_FIDELITY_RULEを含む共通instructionの残り部分は
`er003_b1_p4_audio.build_japanese_style_prefix`が生成するものをそのまま再利用し、
言語指定行以外は1文字も変更していない。)

## 7. chunk別TTS生成結果

全chunk、1回目の生成で技術的失敗・内容確認失敗のいずれもなく合格した(2回目の
再生成は発生していない)。

| chunk_id | duration | sha256(先頭16文字) | decode | clipping |
|---|---|---|---|---|
| 01 | 8.931s | `2137fb46580cd28b` | OK | なし |
| 02 | 8.371s | `a3a21600af9b279f` | OK | なし |
| 03 | 3.611s | `0eac745fe5fec179` | OK | なし |
| 04 | 6.771s | `2c93b129668f39d0` | OK | なし |
| 05 | 4.531s | `85018b116ab035c1` | OK | なし |
| 06 | 5.371s | `110742e73aa5710a` | OK | なし |

## 8. chunk別ASR結果(診断用、境界決定には未使用)

| chunk_id | ASR認識結果 | 「目印」相当語の検出 | 判定 |
|---|---|---|---|
| 01 | 「前半は激しい接触と緊張が続き、両チームとも枠内周と目印を記録できないまま静かな均衡が保たれます。」 | 「目印」検出 | 合格 |
| 02 | 「後半に試合が動くと、イングランドは選手を交代で下げる。目印という決断で守備を固め。」 | 「目印」検出 | 合格 |
| 03 | 「わずかなリード目印を守ろうとします。」 | 「目印」検出 | 合格 |
| 04 | 「アルゼンチンの結晶への道を閉ざすこと。目印が現実になりそうなその時。」 | 「目印」検出 | 合格 |
| 05 | 「メッシが流れを変え、ついにアディショナルタイム目印へ。」 | 「目印」検出 | 合格 |
| 06 | 「最後の数分、寒気と痛みの境目で何が起きるのでしょうか。」 | (normal chunk、対象外) | 合格 |

## 9. ASR表記揺れの扱い

今回の5chunk全てで、ASRは「目印」を漢字表記のまま認識した(P4Bで見られた
「会津」「アイズ」等の表記揺れは今回発生しなかった)。ただし判定ロジック自体は
`ALLOWED_MARKER_SPELLINGS = ("目印", "めじるし", "目じるし")`のいずれかが
含まれていれば合格とする設計であり、表記完全一致を合否条件にしていない
(指示section9の明記通り)。marker以外の軽微なASR誤変換(01「シュート」→
「周と」、04「決勝」→「結晶」、06「歓喜」→「寒気」)は、いずれも
`content_similarity_ratio`が閾値0.5を十分上回っており(0.88〜1.0)、不合格
判定の対象にしていない。

## 10. 「最後の数分」の重点確認

| 項目 | 結果 |
|---|---|
| source phrase | 最後の数分 |
| ASR transcript | 「最後の数分、寒気と痛みの境目で何が起きるのでしょうか。」 |
| ASR上の対応部分 | 「最後の数分」がそのまま検出された |
| 音声file path | `preview/ja_chunks/chunk06_ja.wav` |
| 判定 | 合格(1回目の生成で合格、再生成は発生していない) |

## 11. MFA alignment結果

| 項目 | 値 |
|---|---|
| MFA version | 3.4.1 |
| acoustic/dictionary model | japanese_mfa |
| beam / retry_beam | 100 / 400(既定の隔離環境設定をそのまま使用) |

| chunk_id | 「目印」start | end | duration | 直前token | 直後token |
|---|---|---|---|---|---|
| 01 | 5.10s | 5.61s | 0.51s | シュート | を |
| 02 | 5.12s | 5.71s | 0.59s | 下げる | と |
| 03 | 1.67s | 2.27s | 0.60s | リード | を |
| 04 | 3.42s | 4.02s | 0.60s | こと | が |
| 05 | 3.57s | 4.22s | 0.65s | タイム | へ |

5件全てで「目印」の区間を1件ずつ特定できた(未検出・複数検出は0件)。

## 12. 5 used forms(実際にPattern A内で使われている表記)

```
shot on target
take players off
a narrow lead
close the door to the final
stoppage time
```

## 13. 英語Component生成・再利用状況

| chunk_id | used form | 状態 | duration | sha256(先頭16文字) |
|---|---|---|---|---|
| 01 | shot on target | 既存流用(`er003_output/b1_p3u/A01/components/en_shot_on_target_trimmed.wav`) | 1.231s | `82a4b01ea4dc466b` |
| 02 | take players off | 新規生成 | 1.431s | `9c926677bacf70c6` |
| 03 | a narrow lead | 新規生成 | 1.011s | `12d342150b586abc` |
| 04 | close the door to the final | 新規生成 | 2.331s | `5481eb5bb0a4a1d2` |
| 05 | stoppage time | 新規生成 | 1.291s | `b6e7547a445ddb82` |

いずれも技術的失敗・retry発生なし。

## 14. 5箇所の実測before/after gap

| chunk_id | 実測before | 実測after | 許容差内(before) | 許容差内(after) |
|---|---|---|---|---|
| 01 | 0.40s | 0.30s | はい | はい |
| 02 | 0.40s | 0.30s | はい | はい |
| 03 | 0.40s | 0.30s | はい | はい |
| 04 | 0.40s | 0.30s | はい | はい |
| 05 | 0.40s | 0.30s | はい | はい |

目標(before=0.40s±0.03s、after=0.30s±0.03s)を5件全てで達成(誤差0)。

## 15. 「目印」残存・英語表現の欠落/重複

| 項目 | 結果 |
|---|---|
| 置換後chunkに「目印」が残存 | 0(各marker区間をMFAで特定した範囲を完全に削除して置換) |
| 英語used formの欠落 | 0(5件全て1回ずつ挿入) |
| 英語used formの重複 | 0 |

## 16. 一般chunk境界(固定無音を追加しない、実測のみ)の測定結果

| 境界 | 実測無音 | 1.0秒超過 |
|---|---|---|
| 01→02 | 0.48s | いいえ |
| 02→03 | 0.48s | いいえ |
| 03→04 | 0.40s | いいえ |
| 04→05 | 0.64s | いいえ |
| 05→06 | 0.50s | いいえ |

固定0.8秒・英語境界用0.4秒/0.3秒はいずれも追加していない(各chunk本来の
無音のみ)。全境界が1.0秒未満のため、停止せず結合を継続した。

## 17. Preview raw / Dynamics3

| 項目 | 値 |
|---|---|
| raw path | `preview/final/A01_b1_listening_preview_raw.wav` |
| raw duration | 42.331s |
| raw sha256(先頭16文字) | `0b513f6362f31fb2` |
| Dynamics3 path | `preview/final/A01_b1_listening_preview_dynamics3.wav` |
| Dynamics3 duration | 42.331s |
| Dynamics3 sha256(先頭16文字) | `f0ed4eef90ec1943` |
| Dynamics3適用回数 | 1回(Preview全体へ一括適用、個別chunk・英語Componentへの重複適用なし) |
| decode | raw/Dynamics3ともOK |
| clipping | raw/Dynamics3ともなし |

## 18. Pattern A変更・B1本文・通し音声の確認

| 項目 | 結果 |
|---|---|
| Pattern A変更 | 0 |
| B1本文生成 | 0(未実施) |
| Preview+本文の結合音声生成 | 0(未実施) |

## 19. tests / validation

- `er003_test_b1_p4b_audio.py`(marker_token引数追加後、既存20件を再実行): 全合格、回帰なし
- `er003_test_b1_p4c_audio.py`(新規16件、P4B実機ログを再現した回帰ケース含む): 全合格
- プロジェクト全体の既存テストスイート: 1034件全合格(discover実行)

## 20. commit / push

- コミット予定メッセージ: `ER-003-B1-P4C rebuild preview with mejirushi markers`
- PROTOTYPE / NOT_APPROVED
- push: 実施しない
- amend / rebase / squash / force push: 実施しない

## 21. ユーザーへの確認事項

`preview/final/A01_b1_listening_preview_dynamics3.wav`を試聴のうえ、以下を
ご判断ください。

- 5箇所の英語切替(shot on target / take players off / a narrow lead /
  close the door to the final / stoppage time)の自然さ
- chunk境界(01→02〜05→06)の間の自然さ(今回は固定無音を使っていないため、
  実測値0.40〜0.64秒のばらつきがある)
- `preview/ja_chunks/chunk06_ja.wav`(「最後の数分」を含む文)が、P4Aで問題視
  された崩れなく自然に聞こえるか

このステージではB1本文・通し音声には進んでいません。次のステップ(B1本文生成、
Preview+本文の結合)は、Preview完成版の試聴結果を踏まえてご指示ください。
