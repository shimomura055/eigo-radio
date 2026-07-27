# ER-003-B1-P6B 実行報告(2-Macrochunk生成およびmarker境界改善検証)

## 1. P6A不合格理由

ユーザー試聴により、以下の理由で不合格と判定された。

- `shot on target` の挿入位置で日本語助詞「を」が不自然に分断された
- chunk01とchunk02の声質が異なり、接続が不自然だった

chunk02のASR原稿一致率1.0は有益な情報だが、音声品質の合格を意味しない。

## 2. 使用した2-Macrochunk構成

Pattern A原文を、P6Aの4chunk用アンカーのうち1つ(「を守ろうとします。」)
だけを使って2分割した。

| Macrochunk | 内容 | used_forms |
|---|---|---|
| A | 第1文+第2文 | shot on target, take players off, a narrow lead |
| B | 第3文+第4文 | close the door to the final, stoppage time |

読点や英語marker位置では分割していない。分割数は2に固定。

## 3. 各Macrochunkの実際のTTS入力

**Macrochunk A**:
> 前半は激しい接触と緊張が続き、両チームとも枠内シュート、目印を記録できないまま、静かな均衡が保たれます。後半に試合が動くと、イングランドは選手を交代で下げる、目印という決断で守備を固め、わずかなリード、目印を守ろうとします。

**Macrochunk B**:
> アルゼンチンの決勝への道を閉ざすこと――目印――が現実になりそうなその時、メッシが流れを変え、ついにアディショナルタイム、目印へ。最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。

## 4. TTS call数と生成条件

| 項目 | 値 |
|---|---|
| TTS call数 | 2(Macrochunk A・Bそれぞれ1回) |
| technical retry | 0回(両方とも初回成功) |
| Voice | Aoede |
| Level | Emotional+Connected / Level2 |
| speed number | 指定なし |
| Dynamics 3 | **未適用**(指示section5・6の明記通り、日本語接続の一次評価時には適用しない) |

**P6Aとの生成条件の同一性**: instruction(JAPANESE_STYLE_PREFIX)・voice・Level・
speed指定は**P6Aと完全に同一**。継続性指示("Treat the narration as one
continuous program, even when it is generated in separate sections.")も
無変更のまま含まれている。**今回変更したのはTTS call数(4回→2回)と
分割位置のみ**であり、これによって声質不連続が改善するかを検証するのが
本ステージの主目的。

## 5. 原稿忠実性QA

### 静的検証(TTS呼び出し前)

| 項目 | 結果 |
|---|---|
| Macrochunk結合 → Pattern A原文と完全一致 | 合格 |
| 5 used form残存 | すべて0 |
| 「目印」出現数合計 | 5(想定通り、A=3、B=2) |
| ASCII英字残存 | 0 |
| 6重点句(選手を交代で下げる/という決断で/守備を固め/わずかなリード/最後の数分/何が起きるのでしょうか)が原文中に存在 | 全て合格 |
| **総合判定** | **全項目合格、TTS実行可** |

## 6. ASR診断

| Macrochunk | ASR認識結果 | marker検出(期待) | 一致率 |
|---|---|---|---|
| A | 前半は激折な接触と緊張が続き、両チームとも枠内シュート目印を記録できないまま静かな均衡が保たれます。後半に試合が動くと、イングランドは選手を交代で下げる目印という決断で守備を固め、わずかなリード目印を守ろうとします。 | 3(3) | 0.9806 |
| B | アルゼンチンの結晶への道を閉ざすこと。目印が現実になりそうなその時、メッシが流れを変え、ついにアディショナルタイム目印へ。最後の数分、寒気と痛みの境目で何が起きるのでしょうか。 | 2(2) | 0.9286 |

**Macrochunk A**は「選手を交代で下げる目印という決断で守備を固め、わずかな
リード目印を守ろうとします」の部分に**一切の欠落がない**(「激しい」→
「激折な」という軽微なASR誤変換のみ)。**Macrochunk B**も「最後の数分」
「何が起きるのでしょうか」を含め完全に検出された(「決勝」→「結晶」、
「歓喜」→「寒気」は、このプロジェクト全体で繰り返し見られるASR側の
同音異義語の癖と一致するパターン)。P6Aで確認された「で下げる」「という
決断」のような欠落は、今回は一切発生していない。

## 7. Stage 1試聴音声

| 項目 | path | 内容 |
|---|---|---|
| Macrochunk A raw | `stage1/macrochunks/macrochunk01_ja.wav` | 22.451秒 |
| Macrochunk B raw | `stage1/macrochunks/macrochunk02_ja.wav` | 14.411秒 |
| 接続版(本編仕様0.8秒) | `stage1/connected/A01_stage1_connected_pause_0p8s.wav` | 37.662秒 |
| 接続版(比較用0.4秒) | `stage1/connected/A01_stage1_connected_pause_0p4s.wav` | 37.262秒 |
| 接続版(比較用0.6秒) | `stage1/connected/A01_stage1_connected_pause_0p6s.wav` | 37.462秒 |

比較用接続版は、Macrochunk A・Bの同一raw音声からAB間の無音時間だけを
変えて作成したもので、新規TTS callは行っていない(指示section6の明記通り)。

## 8. Stage 1の機械判定

| 項目 | 結果 |
|---|---|
| TTS call数=2 | 合格 |
| 原稿の欠落・追加 | 検出されず |
| markerの合計出現回数 | 5(合格) |
| 重点語句(6件)の保持 | 全て合格 |
| decode | 両Macrochunk・全接続版でOK |
| clipping | 検出なし |

**機械QAは全て合格した。ただし、これは「Macrochunk AとBの声質が同じに
聞こえるか」「接続が自然か」「同一人物の連続読み上げに聞こえるか」を
判定するものではない。これらは指示section7の停止条件そのものであり、
機械的には判定できない。したがってStage 1の合否は、ユーザーの試聴結果を
待って確定する。**

## 9. Stage 2を実施したか

**実施していない。** 指示section2「最初に日本語接続を評価し、合格した
場合のみ英語置換へ進む」、section7「Stage 1不合格の場合、追加のmarker
処理を実施しない」、section16の分岐に従い、Stage 1のユーザー試聴確認を
経ずにStage 2(marker境界改善による英語Component置換)を実行することは、
指示の趣旨に反すると判断した。

**ただし、Stage 2の実装自体は完了・検証済み。** P6Aで実際に生成した
chunk03(2件目markerの後の「へ。」がRMSベースのfind_speech_boundsで
検出できず停止した実データ)を回帰テストの材料として再利用し、新しい
MFA境界オンリー方式(RMSを一切使わず、MFAが返す`preceding_token_end_
seconds`/`following_token_start_seconds`を`adjust_trailing_silence`/
`adjust_leading_silence`の`speech_end`/`speech_start`引数へ直接渡す)が、
この実データに対して問題なく動作し、「へ」の音声を一切変更せずに目標
無音時間(0.22秒)を達成できることを、新規TTS/MFA呼び出しなしで実証した
(`er003_test_b1_p6b_audio.py::Chunk03RegressionSpliceTests`)。

## 10〜13. markerごとのMFA区間 / 隣接token境界 / 英語前後間隔 / Stage 2試聴音声

Stage 2未実施のため、実データはまだない。Stage 1がユーザー試聴で合格と
判断された場合、既存の`p3w.run_mfa_align`・`p4.find_all_marker_spans`・
`p3z.adjust_trailing_silence`/`adjust_leading_silence`(MFA境界を直接
渡す新しい呼び出し方)をそのまま使い、5箇所全てのmarker区間・隣接token・
実測gapを記録して報告する。

## 14. Dynamics 3適用箇所

Stage 1では未適用(指示通り)。Stage 2完了後、最終全体の結合音声へ1回
だけ適用する設計(未実施)。

## 15. 作成・変更したファイル

- `er003_b1_p6a_audio.py`(更新): `build_chunk_plan`に`chunk_end_anchors`引数を追加(既定値は無変更、P6Aの4chunk用アンカーのまま動作)
- `er003_b1_p6b_audio.py`(新規): 2-Macrochunk分割ラッパー、MFA境界の隣接token重複確認、絶対時刻→相対サンプル変換、Stage2用の設計定数
- `er003_v1_b1_p6b_stage1_generate.py`(新規): Stage1オーケストレーションscript
- `er003_test_b1_p6b_audio.py`(新規、11件、実TTS/MFA呼び出しなし。P6Aの実データを使った回帰テストを含む)
- `er003_output/b1_p6b/A01/`配下の成果物一式
- `er003_output/b1_p6b/A01/instruction/ER-003-B1-P6B_instruction.md`: 本指示書の保存

## 16. テスト結果

- `er003_test_b1_p6a_audio.py`(chunk_end_anchors引数追加後、既存20件を再実行): 全合格、回帰なし
- `er003_test_b1_p6b_audio.py`(新規11件、実TTS/MFA呼び出しなし): 全合格
- プロジェクト全体の既存テストスイート: 1128件全合格(discover実行)

## 17. 再実行方法

```
.venv/Scripts/python.exe er003_v1_b1_p6b_stage1_generate.py
```

Stage2は、Stage1のユーザー確認後に別スクリプトとして実装・実行する
(現時点では未着手)。

## 18. 既知のリスク

- Stage 1の機械QAは全て合格したが、これは声質・自然さの合格を保証しない。
  試聴による確認が必須。
- Stage 2は設計・回帰テストのみ完了しており、実際のMacrochunk A/B raw音声
  に対する実行はまだ行っていない。Stage 1で問題が見つかった場合、Stage 2は
  実施しない。
- 比較用接続版(0.4秒・0.6秒)は、AB間の無音時間だけを変えたものであり、
  各Macrochunk内部の音声は完全に同一。

## 19. 指示書の保存先とハッシュ

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p6b/A01/instruction/ER-003-B1-P6B_instruction.md` |
| sha256 | `a2e59fd3a94f6d69307d7c64afaae21572f70a693fbb97d70c059867d3e016ee` |
| 管理ID | ER-003-B1-P6B |
| 実行時commit | `3fde1db2cd513727dc8f26f365152fdb10810fa7`(P6A停止コミット、このステージ実行直前のHEAD) |
| 指示書からの逸脱 | なし |

## 20. Git status

このレポート作成時点では未コミット。P6B関連ファイルのみをステージして
コミットします。

## 21. push

実行していません。

---

## ユーザーへの確認事項

以下2件の接続版を試聴し、指示section7の停止条件(声質差・話速/感情/音域の
違い・同一人物として聞こえるか)をご確認ください。

- [A01_stage1_connected_pause_0p8s.wav](stage1/connected/A01_stage1_connected_pause_0p8s.wav)(本編仕様の0.8秒無音)
- [A01_stage1_connected_pause_0p4s.wav](stage1/connected/A01_stage1_connected_pause_0p4s.wav) / [0p6s](stage1/connected/A01_stage1_connected_pause_0p6s.wav)(比較用)

**Stage 1が合格と判断された場合のみ、Stage 2(marker境界改善による英語
Component置換)へ進みます。** 機械QAは全て合格していますが、「品質合格」
「自然さ確認済み」とは判断していません。

## 22. ユーザー試聴結果(Stage 1 最終判定)

**判定: 不合格**

0.8秒無音版を試聴した結果、以下2点が不合格理由として指摘された。

### 22-1. 「激しい」の誤読

Macrochunk A冒頭「前半は**激しい**接触と緊張が続き」の「激しい(はげしい)」
が、TTSにより「**げきせつな**」という、原稿にも辞書的にも存在しない読みで
発話されている。

本セクション6のASR診断では、この箇所を「前半は激折な接触と緊張が続き」
(一致率0.9806の内訳として)と記録し、「『激しい』→『激折な』という軽微な
ASR誤変換のみ」「決勝→結晶、歓喜→寒気と同種のASR側の同音異義語の癖」と
**判断していたが、これは誤りだった**。ユーザーの実聴により、ASRの書き起こし
の癖ではなく、**TTS自体が「激しい」を誤発音している**ことが確認された。

これは本シリーズで初めて確認された種類の不合格理由であり、これまで
「ASR側の癖」として片付けていた同音異義語系の差異(決勝→結晶、歓喜→寒気、
選手→戦士等)についても、今後は同様に実聴で裏取りせずにASR側の癖と
断定しないよう注意が必要。

### 22-2. Macrochunk A/B接続部の音質差

読み間違いとは別に、Macrochunk AとBの接続部(つなぎ目)で音質の違いが
感じられる。これはP6Aで指摘された「chunk01/02間の声質差」と同種の問題で
あり、TTS call数を4回→2回に減らしても、接続部の音質不連続は解消しきれて
いないことを示す。

### 22-3. 総合判定

Stage 1は不合格。指示書section16の分岐ルールに従い、Stage 2(英語Key
Phrase置換)は実施しない。次の対応方針(新しいTTS方式の検討など)は
ユーザーと別途相談の上で決定する。**先回りしての新方式実装は行わない。**
