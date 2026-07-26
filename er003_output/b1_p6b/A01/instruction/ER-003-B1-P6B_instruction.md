# ER-003-B1-P6B 2-Macrochunk生成およびmarker境界改善検証

## 1. P6Aの判定
ER-003-B1-P6Aは不合格とする。
理由：

1. `shot on target` の挿入位置で日本語助詞「を」が不自然に分断された
2. chunk01とchunk02の声質が異なり、接続が不自然だった

chunk02のASR原稿一致率が1.0であることは有益だが、音声品質の合格を意味しない。

## 2. 目的
以下の2点を、分離して検証する。

1. TTS call数を2回まで減らすことで、語句省略を避けながら声質の不連続を許容範囲へ抑えられるか
2. 英語markerだけを正確に置換し、前後の日本語助詞や音節を損なわずに英語Componentを挿入できるか

最初に日本語接続を評価し、合格した場合のみ英語置換へ進む。

## 3. 2-Macrochunk構成
承認済みPattern Aを、本来の意味の転換点で次の2つに分ける。
Macrochunk A
第1文と第2文を連続して含める。
対象内容：

* 前半の均衡
* `shot on target`
* イングランドの交代
* `take players off`
* 守備を固める決断
* `a narrow lead`

Macrochunk B
第3文と第4文を連続して含める。
対象内容：

* アルゼンチンの決勝への道
* `close the door to the final`
* メッシが流れを変える
* `stoppage time`
* 最後の数分
* 何が起きるのでしょうか

読点や英語markerの位置では分割しない。
分割数は2に固定する。4chunkおよび6chunkへ戻さない。

## 4. 日本語TTS入力
承認済みPattern Aの漢字かな交じり原稿を使用する。
5つの英語used formは、既存方式と同じ日本語markerへ置換する。
日本語原稿の語句、構文、句読点は変更しない。
特に次を保持する。

* 枠内シュート、目印を記録できないまま
* 選手を交代で下げる、目印という決断で守備を固め
* わずかなリード、目印を守ろうとします
* 決勝への道を閉ざすこと――目印――が
* アディショナルタイム、目印へ
* 最後の数分
* 何が起きるのでしょうか

## 5. TTS生成条件

* Voice：Aoede
* Emotional + Connected
* Level 2
* speed number：指定しない
* Macrochunkごとに1回
* 合計TTS call：2回
* technical retry：原則なし
* 全文ひらがな化：なし
* Dynamics 3：日本語接続の一次評価時には適用しない

共通instructionには、本編で使用している以下の連続性指示を維持する。
`Treat the narration as one continuous program, even when it is generated in separate sections.`
P6Aと生成条件が同一の場合でも、その事実を報告する。

## 6. Stage 1：日本語rawの評価
最初に、英語Componentへ置換していないmarker入り日本語rawを作る。
保存する音声：

1. Macrochunk A raw
2. Macrochunk B raw
3. AとBを接続した日本語raw

接続時には、意味上の転換点として意図的な無音を設ける。
本編共通仕様の0.8秒版を作成する。
同じraw音声から、比較用として短い接続版を作ってもよい。ただし、新しいTTS callは行わない。
比較用接続を作る場合、変更するのはAとBの間の無音時間だけとし、候補は最大2件までとする。

## 7. Stage 1の停止条件
以下のいずれかが確認された場合、英語Componentへの置換へ進まない。

* Macrochunk AとBで声質が明確に異なる
* 話速、感情、音域が大きく異なる
* 接続後、同一人物の連続した読み上げに聞こえない
* Macrochunk内で原稿の省略・追加がある
* 「最後の数分」などの重点語句に読み崩れがある

この場合はStage 1不合格として報告し、追加のmarker処理を実施しない。

## 8. Stage 1の原稿忠実性QA
各Macrochunkについて、入力とASR診断を比較する。
重点確認：

* 選手を交代で下げる
* という決断で
* 守備を固め
* わずかなリード
* 最後の数分
* 何が起きるのでしょうか
* markerの合計出現回数

入力文字列の保持テストだけでなく、ASRで疑わしい欠落箇所を抽出する。
ASR結果はユーザー試聴を代替しない。

## 9. Stage 2：marker置換境界の改善
Stage 1が合格候補の場合のみ実施する。
英語Component置換時の除去範囲は、MFAが返したmarker語そのものの時間区間を一次基準とする。
RMSベースのspeech boundsを、marker前後の日本語音節を含む除去範囲の決定に使用しない。
特に以下を守る。

* marker直後の「を」を除去しない
* marker直前の日本語語尾を除去しない
* `stoppage time` 後の「へ」を除去しない
* 「という決断で」の「と」または「という」をmarkerに含めない
* markerを除去した結果、同じ助詞が前後に重複しない
* marker周辺の日本語音声を時間伸縮しない

MFA区間に不確実性がある場合は、隣接する日本語tokenの区間と重ならないことを機械確認する。
RMSは、無音やファイル異常の診断に利用してよいが、短く静かな日本語tokenの存在判定には使用しない。

## 10. 重点置換箇所
以下について、置換前後の時間区間と隣接tokenを保存する。
shot on target
期待構造：
`枠内シュート、｜shot on target｜を記録できないまま`
確認事項：

* 英語前に日本語の「を」が付かない
* 英語後の「を」が完全に残る
* 「を」が二重にならない
* 「記録」の先頭が欠けない

take players off
期待構造：
`選手を交代で下げる、｜take players off｜という決断で`
確認事項：

* 「下げる」が欠けない
* 「という」が完全に残る
* 英語音声と「という」が不自然に重ならない

a narrow lead
期待構造：
`わずかなリード、｜a narrow lead｜を守ろうとします`
close the door to the final
期待構造：
`決勝への道を閉ざすこと――｜close the door to the final｜――が`
stoppage time
期待構造：
`アディショナルタイム、｜stoppage time｜へ`
確認事項：

* 「へ」が完全に残る
* 「へ」を無音と誤判定しない
* 文末の韻律を壊さない

## 11. 英語前後間隔
Stage 2では確定済み仕様を適用する。

* 英語前の実効間隔：0.40秒
* 英語後の実効間隔：0.30秒
* 許容差：各±0.03秒

この間隔は、marker除去区間を日本語側へ拡張することで作らない。
markerの除去と無音挿入を別処理として扱う。

## 12. Dynamics 3
Stage 2の全置換・Macrochunk接続が完了した後、最終全体へ1回だけ適用する。
各Macrochunkや各英語Componentへ個別適用しない。
Dynamics 3適用前の音声も保存する。

## 13. 機械QA
以下を確認する。
日本語生成

* TTS call数が2回である
* 各Macrochunkの入力が元原稿と対応する
* chunk間の欠落・重複がない
* markerが合計5件存在する
* 重点日本語語句が保持されている

marker置換

* 5件すべてが1回ずつ置換される
* marker音声が残っていない
* marker以外の日本語tokenを除去していない
* 直後の「を」「という」「が」「へ」が残っている
* 英語前後間隔が許容差内である

音声ファイル

* decode可能
* clippingなし
* 接続境界にクリックや二重音がない
* Dynamics 3が最終全体へ1回だけ適用されている

機械QA合格を音質承認とみなさない。

## 14. ユーザー試聴項目
Stage 1

* Macrochunk AとBの声質が同じに聞こえる
* 接続が自然である
* 各Macrochunk内の日本語が自然である
* 原稿の欠落・追加がない
* 「最後の数分」が正しい
* 「何が起きる」が正しい

Stage 2

* `shot on target` 前後の「を」が正しい
* `take players off` 前後の日本語が欠けない
* `a narrow lead` の前後が自然
* `close the door to the final` が不自然に分断されない
* `stoppage time` 後の「へ」が自然
* 英語挿入位置が原稿どおり
* 英語前後の間が自然
* 全体の声色が連続している

音声の自然さはユーザーが最終判断する。

## 15. 合格条件
以下をすべて満たす場合のみP6B合格とする。

* 2回のTTS callで原稿の欠落・追加がない
* Macrochunk間の声質差が許容範囲
* 同一人物の連続読み上げとして聞こえる
* markerだけが置換され、日本語助詞を損なっていない
* 5件の英語挿入位置が正しい
* 英語前後間隔が仕様内
* 日本語と英語の接続が自然
* ユーザーが合格と判断する

## 16. 分岐
Stage 1不合格
英語置換へ進まない。
2-Macrochunkでも声質差が大きい場合、Geminiの独立生成を自然につなぐ方式はPreview用途に不適合と判断する。
Stage 1合格、Stage 2不合格
日本語分割方式は維持し、marker境界・置換処理だけを修正する。
語句や分割数は変更しない。
Stage 2合格
2-Macrochunk方式をPreview日本語生成の候補方式とする。
完成版Previewの最終試聴へ進む。

## 17. 非対象範囲

* Amazon Polly
* Azure・Google Cloud TTS
* 4chunk・6chunkへの復帰
* 全文ひらがな化
* B1本文
* 新しいKey Phrase
* push

## 18. 実行報告
以下の順に報告する。

1. P6A不合格理由
2. 使用した2-Macrochunk構成
3. 各Macrochunkの実際のTTS入力
4. TTS call数と生成条件
5. 原稿忠実性QA
6. ASR診断
7. Stage 1試聴音声
8. Stage 1の機械判定
9. Stage 2を実施したか
10. markerごとのMFA区間
11. 隣接日本語tokenとの境界
12. 英語前後間隔
13. Stage 2試聴音声
14. Dynamics 3適用箇所
15. 作成・変更したファイル
16. テスト結果
17. 再実行方法
18. 既知のリスク
19. 指示書の保存先とハッシュ
20. Git status
21. pushを実行していないこと

ユーザー試聴前に品質合格・自然さ確認済みとは判断しないこと。
