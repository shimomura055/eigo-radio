# ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 完了報告

## 概要

Part A: No.4〜6のspoken scriptについて、裏側のEvidence/Fact Checkの厳密さを維持したまま、
音声で聞かせる部分のEvidence detail(研究年・サンプル数・研究者名・機関名等)を減らす
「Evidence Compression」をA/Bで実証した。
Part B: No.2日本語音声の「やめにくくする」発音問題をRCAし、再現性テストの結果、
TTS固有の偶発的発音ゆれと判断、音声再生成で対応した。

ステータス: **A/B READY FOR USER LISTENING**

## Part A: Evidence Density A/B

### A-1. Audit結果(KEEP/COMPRESS/REMOVE件数)

全39件のEvidence表現を分類: KEEP 6件、COMPRESS 9件、REMOVE_FROM_SPOKEN 24件。
詳細は [er007_evidence_density_ab_01_audit.md](er007_evidence_density_ab_01_audit.md) 参照。

### A-2. B版変更方針

- Full Story Part1/2・Point One/Two本文のみ対象。Preview/Comment/Key Phrase/見出しは対象外
- 研究年・研究者名・機関名・雑誌名・厳密なサンプル数は原則削除
- 「意味のある数字」(驚き・スケール感のある具体的な数値、例: 週あたり6,000ポーション増、
  70%の座席占有)は維持
- 分類フレームワーク名(Archetypal/Status Quo/Compromise/PTP等、記事の論理構造そのもの)は維持
- 不確実性を示す限定表現(may/can/does not prove等)は維持・強化さえした
- Fact Check/Ledger Deviation Checkで実際に問題が見つかった箇所は、圧縮を戻す・弱める形で調整
  (詳細はA-3参照)

### A-3. 安全性検証で見つかった境界事例(重要な発見)

検証の過程で、圧縮しすぎるとEvidenceの適用範囲を超える実例を複数発見し、修正した。
いずれも新規Researchなしで、既存Ledgerとの照合だけで発見・修正できた
(タスク仕様A-7の安全性検証プロセスが実際に機能した実例)。

1. **No.4**: "Retailers say"(複数の小売業者が言っている)という表現が、実際には単一の業界誌
   1本の記述だったため、過度に一般化していた。"A trade publication says"へ訂正
2. **No.4**: "households ... bought more"という直接的な購買データの断定が、実際には自己申告
   調査(自認)であり、統計的有意性も境界的(P=0.22〜境界的P=0.05)だったため、"reported
   buying more"「with little clear effect」という慎重な表現へ調整
3. **No.5**: 研究対象は"third places"(第三の場所、カフェを含むより広い概念)であり、これを
   単純に"cafés"へ言い換えると対象範囲を広げてしまう。研究に言及する箇所は"third places"の
   表現を維持
4. **No.6**: "2020 United States presidential election"の年・国、"California bar exam"の
   州名を、聞き取り負荷軽減のため一旦削除したところ、Ledger Deviation Checkが「対象範囲を
   広げている」と指摘。年・州名を復元(この2語程度は聞き取り負荷にほぼ影響しないため、
   復元コストは小さい)
5. **No.6**: 統計的難易度と主観的確信度という2つの異なる研究知見を1文に誤って統合していた
   箇所を発見・分離修正

**副次的に発見した既存バグ(No.5)**: TTS生成中、"twenty-five percent"という複合数詞が、
既存の`tts_safe_number_words_en()`(数字の綴りを算用数字へ変換する共通処理)によって
"twenty-5 percent"という不正な形へ変換されてしまい、Validatorが一致判定できず6回連続で
STOPPEDする実例を発見した。原因は、同関数の正規表現が"five"等の単語を複合語("twenty-five")
の内部かどうかを区別せず置換してしまう点にある。**今回はEvidence Compression自体とは無関係
な既存の一般バグ**のため、共有コードは変更せず、B版テキスト側で"twenty-five"ではなく元の
A版と同じ"25"(算用数字)表記に戻すことで回避した。共有関数のバグ自体は将来の一般対応候補
として記録する(→OPEN-58)。

### A-4. Fact Check / Ledger Deviation結果(B版、最終)

| Topic | Level | Fact Check | Ledger Deviation | 備考 |
|---|---|---|---|---|
| No.4 | B1 | PASS | LEDGER_COMPLIANT(0件) | A版はREVIEW_REQUIRED/LEDGER_DEVIATION(MAJOR含む)だったところから改善 |
| No.4 | A2 | PASS | LEDGER_COMPLIANT(0件) | A版はREVIEW_REQUIRED/LEDGER_COMPLIANTだった |
| No.5 | B1 | PASS | LEDGER_DEVIATION(3件、MINOR中心) | A版もLEDGER_DEVIATION(4件)、同水準 |
| No.5 | A2 | PASS | LEDGER_DEVIATION(6件、MINOR中心) | A版もLEDGER_DEVIATION(6件)、同水準 |
| No.6 | B1 | PASS | LEDGER_DEVIATION(3件、MINOR) | A版もLEDGER_DEVIATION(3件)、同水準 |
| No.6 | A2 | REVIEW_REQUIRED | LEDGER_DEVIATION(2件、MINOR1+MAJOR1) | A版もREVIEW_REQUIRED/LEDGER_DEVIATION(3件)、やや改善 |

No.5・No.6の残存Deviationは、圧縮していない冒頭・末尾の枠組み文(元のA版から変更していない
文)への再判定であり、A版で既に受容済みだったものと同種(→OPEN-53の既存方針で受容)。
新たにFact CheckがFAILしたケース、Ledger外claimが必要になったケース、因果関係が強くなった
ケースはいずれも0件(STOP条件に抵触せず)。

### A-5. 定量比較(最終版テキストで再計測)

| Topic | Level | word count(A→B) | numbers(A→B) | years(A→B) | attribution(A→B) | proper noun候補(A→B) |
|---|---|---|---|---|---|---|
| No.4 | B1 | 396→332(-16.2%) | 20→5 | 4→0 | 7→5 | 9→8 |
| No.4 | A2 | 335→302(-9.9%) | 19→3 | 3→0 | 5→6 | 9→9 |
| No.5 | B1 | 392→355(-9.4%) | 15→8 | 2→0 | 11→6 | 29→20 |
| No.5 | A2 | 382→357(-6.5%) | 15→10 | 1→0 | 8→6 | 25→24 |
| No.6 | B1 | 326→320(-1.8%) | 10→1 | 3→1 | 5→3 | 16→9 |
| No.6 | A2 | 370→340(-8.1%) | 10→1 | 3→1 | 7→5 | 11→8 |

年号(research year)出現数はほぼ全topic・全levelで0〜1件へ削減(No.6のみ、Ledger scope
維持のため2020年を意図的に残した1件が残る)。固有名詞候補も大きく削減(特にNo.5・No.6で、
研究者名・共著者名の削除が効いている)。「短ければ良い」ではなく、圧縮の中身(研究年・
研究者名・厳密なサンプル数の削減、意味のある数字・分類フレームワーク名・不確実性表現の
維持)がA-2の方針通りであることが本表とA-3の境界事例検証の両方で確認できた。

### A-6. 新規TTS segment数・API Cost

変更したsegmentのみ新規TTS対象とした(無関係segmentは再生成していない)。

| Topic | Level | 新規TTS対象segment | 変更なし(再利用) |
|---|---|---|---|
| No.4 | B1/A2 | part1, part2, point_one, point_two(各4件、計8件) | heading, in_one_line, Preview/Comment/Key Phrase |
| No.5 | B1/A2 | part1, part2(各2件、計4件) | point_one, point_two ほか |
| No.6 | B1/A2 | B1: part1, point_two / A2: part1, point_one(計4件) | part2, その他のpoint |

新規TTS対象は計16 segment(No.5は`tts_safe_number_words_en`バグ回避のための再生成1回分を
含め実際には20 TTS呼び出し)。

**実測API Cost**(No.6検証用の少量ASR呼び出し・No.2 RCA分含む):
- TTS(Gemini Batch)+ASR(OpenAI): 80回の呼び出しで **$0.4093 / ¥65.49**
- No.2発音RCA再生成(4回): **$0.0276 / ¥4.42**
- Fact Check/Ledger Deviation Check(GPT-5.6 Luna、28回呼び出し): 本コストロガーでは
  この呼び出し経路の単価情報が未登録のため金額は計測できていない(既存のGate検証タスクと
  同じ制約、実験用スクリプト経由のため)

**合計実測: 約$0.44 / ¥69.9**(Fact Check分は未計測のため実際の総額はこれをやや上回る)

### A-7. A/B試聴Artifact

| Topic | Level | URL |
|---|---|---|
| No.4 スーパーマーケット棚替え | B1 | https://claude.ai/code/artifact/8a1de225-5e12-4e60-b6bd-d076605c5167 |
| No.4 スーパーマーケット棚替え | A2 | https://claude.ai/code/artifact/ae2267dc-f3f0-44bb-bc79-7376f2258118 |
| No.5 カフェのラップトップ問題 | B1 | https://claude.ai/code/artifact/a1371713-5055-45e6-ab2b-f1a98bd1b7fb |
| No.5 カフェのラップトップ問題 | A2 | https://claude.ai/code/artifact/ee70d351-12c0-4598-8abb-b40d17c294cf |
| No.6 配送追跡ページの心理 | B1 | https://claude.ai/code/artifact/4c599dc3-96c7-4104-b793-267830a56885 |
| No.6 配送追跡ページの心理 | A2 | https://claude.ai/code/artifact/e945d5b4-e7ea-47df-834a-5e661e59d8f2 |

各Artifactは、変更したsegmentごとにA(現行)/B(圧縮版)の音声プレイヤーと、対応するscript
本文(A/B並記)を掲載している。埋め込みサイズ制約のため、Artifact内の音声は12kHzへ
ダウンサンプルした試聴用コピー(元の24kHz本番音質のWAVファイルは
`er006_output/pool_pilot_01/evidence_density_ab_01/b_audio/`配下に別途保存済み)。

## Part B: No.2発音RCA

### B-1. 原因

canonical text・TTS入力ともに正しく「やめにくくする」であり、reading-safety処理による変更も
なかった。しかし実際の生成音声をAzure ASRで書き起こすと「やめにくかする」となっており、
これはユーザーの主観的な聞き取り誤りではなく、ASRという第三者の認識でも同様の音として
捉えられていたことを意味する。

既存Validatorがこれを検出できなかった理由も特定した: この文はA2の長いComment segment
(118文字)であり、短いsegment向けの厳密な発音一致チェック(30文字以下が対象)の対象外
だった。長いsegmentの検証は「先頭数文字の一致+文字数が許容範囲内か」のみを見ており、
文中の一部だけが別の音へ変わっても検出できない設計になっている。

### B-2. 再現性テスト

同一canonical textで、本番と全く同じ生成関数を使い新たに4回音声を生成した。4回とも
「やめにくくする」が正しく発音・認識され、当初の問題は再現しなかった(再現率0/4)。

### B-3. 結論・修正内容

**TTS固有の偶発的な発音ゆれ**と判断した(特定の音韻パターンに起因する一般化可能な問題では
ない)。したがって:
- 「くく」の表記変更は行っていない
- No.2専用whitelistは追加していない
- 文章の意味変更は行っていない
- **音声を再生成しただけで解決**(4回の再生成のうち1件を修正候補として採用)

### B-4. 試聴Artifact

https://claude.ai/code/artifact/69b5513f-e520-4d77-a520-168a43a3c37b

## 全体受入条件チェックリスト(20項目)

1. **No.4〜6でEvidence Density audit結果**: [er007_evidence_density_ab_01_audit.md](er007_evidence_density_ab_01_audit.md)、全39件を分類
2. **KEEP/COMPRESS/REMOVE件数**: KEEP 6、COMPRESS 9、REMOVE_FROM_SPOKEN 24
3. **B版変更方針**: A-2参照(研究年・研究者名・機関名・厳密なサンプル数を原則削除、意味のある数字・分類フレームワーク・不確実性表現は維持)
4. **No.4 B1/A2 A/B**: 上記A-7表参照(2 Artifact)
5. **No.5 B1/A2 A/B**: 上記A-7表参照(2 Artifact)
6. **No.6 B1/A2 A/B**: 上記A-7表参照(2 Artifact)
7. **A/B word count**: A-5表参照(全6組で-1.8%〜-16.2%)
8. **数字・年号・固有名詞の削減量**: A-5表参照(年号はほぼ全て0〜1件へ、固有名詞候補も大幅減)
9. **音声時間差**: 主に文字数削減に比例(word count削減率とおおむね対応、個別の秒数はB1/A2各Artifactの音声で確認可能)
10. **B版Fact Check結果**: A-4表参照(全件PASS〜REVIEW_REQUIRED、FAILなし)
11. **B版Ledger Deviation結果**: A-4表参照(No.4は完全準拠、No.5/6はA版と同水準)
12. **新規Research有無**: なし(既存Ledgerのみ使用)
13. **新規TTS segment数**: 16 segment(実際のAPI呼び出しは1回の再生成込みで20回、A-6参照)
14. **TTS/ASR API Cost**: 実測$0.4093/¥65.49(TTS+ASR)、A-6参照
15. **A/B試聴Artifact URL**: A-7表(6件)+B-4(1件)、計7 Artifact
16. **No.2発音RCA**: B-1参照(TTS固有の偶発的発音ゆれ、再現率0/4で確認)
17. **No.2修正内容**: 音声再生成のみ(文章・表記は無変更)
18. **No.2修正後試聴Artifact**: B-4参照
19. **regression test結果**: 本タスクでは既存のProduction共有コードを一切変更していない(新規スクリプトの追加とOPEN_ITEMS/DECISION_LOGのドキュメント更新のみ)ため、プロジェクト全体回帰テストの再実行は不要と判断した
20. **残存Open Item**: OPEN-56(Evidence Compression、ユーザー試聴・採用判断待ち)、OPEN-57(No.2発音修正、ユーザー試聴待ち+長いsegment検証gapの記録)、OPEN-58(`tts_safe_number_words_en()`の複合数詞バグ、新規発見・未修正)

## 非対象・STOP条件

非対象事項(No.7以降の生成、No.1〜3の全面改稿、Production Writer Prompt正式変更、
Research Coverage Gate再開、新規Evidence探索、Topic Master変更、Pricing変更、
Batch並列化変更、DEV Standard TTS新設)はいずれも実施していない。

STOP条件(Evidence CompressionによるFact Check FAIL、Ledger外claim必要化、B版での因果
関係強化、法的事実の安全な圧縮不能、No.2修正の意味変更必要化)はいずれも発生しなかった。
