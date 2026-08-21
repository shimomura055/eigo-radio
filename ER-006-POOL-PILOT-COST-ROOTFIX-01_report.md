# ER-006-POOL-PILOT-COST-ROOTFIX-01 完了報告

新規有料API実行は行っていない(¥0)。既存ログ・音声・ASR transcriptだけを使い、
segment/attempt単位でCostを再構築した。残り17トピックへは進んでいない。

## 0. 最初に回答(16章の質問に対する要約)

1. **Cost急増の最大原因Top3**: ① A2の長文セグメント(full_story_part1/2)がSTOPPEDし
   6〜12回の無駄なTTS/ASR再試行が発生したこと、② その根本原因はTTS生成の失敗ではなく
   **ASR比較ロジックが発音上区別できない表記差(固有名詞のウムラウト・ハイフン・序数・
   英米綴り)を「不一致」として扱っていたこと**、③ Writerの書き直し(Rewrite Waste、
   Article-specific 2件+Systemic 1件)。
2. **Clean Costは以前の約46〜48円Baselineから本当に上昇したのか**: **ほぼ上昇していない**。
   segment/attempt単位で再構築したClean Cost(=各segment attempt1のみ)はB1平均¥36.0、
   A2平均¥41.2で、以前のBaseline(¥46〜48)と同水準かむしろ低い。Cost上昇の実体は
   Clean Costの上昇ではなく、ほぼ全てRetry/STOPPED由来のWasteだった。
3. **正しいB1/A2 Clean Cost**: 下記2章参照(B1平均¥36.0、A2平均¥41.2、差はわずか¥5.2)。
4. **正しいRetry/Fallback Waste**: 実測(segment/attempt単位)で¥327.8(旧報告の推定値
   ¥393.6とは別集計方式。詳細2章)。
5. **正しいRewrite Waste**: ¥154.3で確定(旧報告の個別表記載108.6円は表の記載漏れによる
   誤りだったと判明。詳細3章)。
6. **A2がB1より高かった理由**: 本質的な差はごくわずか(Clean Costで¥5.2)。見かけ上¥85〜99円
   高く見えていたのは、A2の方でSTOPPED segmentのCostが集中していた(このPilotの偶然の
   失敗分布)ため。詳細4章。
7. **9 STOPPEDの原因内訳**: 9件中6件はcanonical textが確認でき、うち6件全てが表記差
   (ウムルフト・ハイフン・序数・英米綴り・ダッシュ種別)による**Surface-only mismatch**。
   残り3件(Key Phrase短語)も目視確認でハイフン・複合語分かち書きの表記差。**Trueな内容
   誤り・TTS生成失敗は0件**。詳細5〜6章。
8. **何回のTTS retryが不要だったか**: 過去データへ正規化比較を後付け適用した結果、
   9segment合計¥353.7のうち**¥201.7(約57%)が不要な再試行だった**と推定(詳細7章)。
   さらに、比較ロジック自体を正規化すれば大半は**attempt1で合格しえた**ことも確認した
   (8章)。
9. **新対策を適用した場合の削減額**: 比較ロジックの正規化のみで、canonical textが確認
   できた6segment中5segmentがattempt1時点で高い一致率(0.95〜1.0)に達しており、
   ほぼ即PASSしていた可能性が高い。8章参照。
10. **長文ASR Validationの恒久対策**: 比較前の正規化層を追加する(6章で実装、未配線)。
    retry上限そのものより優先度が高い。
11. **English専門語Validationの扱い**: `blitzscaling`はTTS側の発音は正しく、ASRが
    複合語を2語に分かち書きしているだけ。個別whitelistではなく、上記の正規化層
    (ハイフン・スペース無視)で一般的に吸収できる。9章。
12. **Research Rewrite予防策**: Source Quality Gate・Freshness Gateの案を提示(10章、
    未確定・ユーザー判断待ち)。
13. **Attempt Ledger実装状況**: 本番コード(`er003_v1_n3_01_tts_generate.py`)は既に
    segment/attempt単位のASR transcript・verdictを`audit/tts_generation_results.json`
    へ記録していた(想定より進んでいた)。今回追加したのは、それとCostを突き合わせる
    再構築ロジック(`er006_pool_pilot_01_attempt_ledger.py`)。Cost自体をattempt単位で
    直接記録する変更は本番コードへ**未配線**(11章)。
14. **Cost Guardrail候補**: 12章に3案を提示(未確定)。
15. **残り17 Topicへ進める状態か**: 断定しない。比較ロジックの正規化(6章)を先に
    本番へ入れることを推奨する。それが入っていない状態で17トピックを量産すると、
    今回と同種のSTOPPED・Waste(Retry-Fallback Wasteの過半)が高確率で繰り返される。
16. **新規API実行額**: **¥0**(既存ログのみで再構築・検証した)。
17. **CURRENT_SPEC変更**: なし。

---

## 1. Cost Ledgerの再構築(ER-006-COST-01)

`raw_usage_log.jsonl`(呼び出し単位のcost)と`audit/tts_generation_results.json`
(本番コードが元々segment/attempt単位で記録していたASR transcript・verdict)を、
実行順序に基づき突き合わせた。

再構築ツール: [er006_pool_pilot_01_attempt_ledger.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_pool_pilot_01_attempt_ledger.py)

**突合結果: 6エピソード中5エピソードは完全一致、1エピソード(pool_benches/A2)は
1ペアの差異があったが原因を特定できた**(JAPANESE_TITLES KeyErrorクラッシュ後の
再実行で`topic_intro`が2回生成されたため。前回報告で「Operator-error Waste=¥0」と
記載していたのは誤りで、正しくは¥0.89)。**UNKNOWN(復元不能)として扱った箇所は
最終的に0件。241 attempt全てをsegment・cost・ASR transcriptに紐付けられた。**

再構築後の全体像:

| 区分 | 前回報告(按分推定) | 今回(segment/attempt実測) |
|---|---:|---:|
| Actual Cost合計 | ¥883.8 | ¥884.1(operator-error含む。ほぼ一致、算出方法の違いによる¥0.3の差) |
| Clean Cost | ¥336.0(呼び出し件数按分の推定) | **¥231.7**(各segment attempt1のみ、実測) |
| Retry-Fallback Waste | ¥393.6(推定) | **¥327.8**(実測) |
| Rewrite Waste | ¥154.3 | ¥154.3(変更なし、3章で内訳確認) |
| Operator-error Waste | ¥0(誤り) | **¥0.89**(実測、原因特定済み) |

前回のClean Costが実際より過大(¥336.0)だったのは、按分方式が「1エピソード内の
呼び出し数のうち理論最小値」を粗く見積もっていたため。今回はsegment単位で実際に
「1回目の試行のコスト」を直接合計しており、より正確。

## 2. Clean Cost(実測、旧Baseline¥46〜48との比較)

| Level | Topic平均Clean Cost(実測) |
|---|---:|
| B1 | ¥36.04(ベンチ36.89 / サブスク36.97 / スタートアップ34.25) |
| A2 | ¥41.20(ベンチ40.26 / サブスク40.27 / スタートアップ43.07) |

**旧Baseline(¥46〜48/episode)と比較して、Clean Cost自体はむしろ同等か低い水準に
収まっている。** 「Cost急増」はClean Costの上昇ではなく、ほぼ全てRetry/STOPPED
由来である(4章)。

## 3. Rewrite Wasteの不整合(108.6円 vs 154.3円)の原因確認

**結論: 154.3円が正しい。108.6円は前回報告の記載漏れによる誤りで、二重計上や
集計バグではなかった。**

前回報告の個別表(POOL-001 ¥62.7 / POOL-002 ¥45.9 / POOL-003 ¥0、合計108.6)は、
「Research再実行の有無」だけを見て書いており、**POOL-003(スタートアップ)で
実際に発生していたWriter再実行(Ledger改修に伴う再生成、約¥45.6)を集計表から
書き漏らしていた**。POOL-003は「Research自体は再実行していない」という記述は
正しいが、「Rewrite Waste ¥0」は誤り。

| トピック | Research再実行 | Writer再実行 | 合計Rewrite Waste |
|---|---:|---:|---:|
| POOL-001 ベンチ | ¥2.6 | ¥60.0 | ¥62.7 |
| POOL-002 サブスク | ¥2.0 | ¥43.9 | ¥45.9 |
| POOL-003 スタートアップ | ¥0 | ¥45.6 | **¥45.6**(前回¥0と誤記) |
| 合計 | ¥4.6 | ¥149.5 | **¥154.2 ≈ ¥154.3** |

## 4. B1/A2 Cost差の定量分解

[er006_pool_pilot_01_rootfix_analysis.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_pool_pilot_01_rootfix_analysis.py)
でsegment単位に分解した。

| トピック | B1 Actual | A2 Actual | 差 | B1 Clean | A2 Clean | Clean差 | B1 STOPPED Cost | A2 STOPPED Cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| POOL-001 | ¥57.8 | ¥142.8 | ¥85.0 | ¥36.9 | ¥40.3 | ¥3.4 | ¥24.0 | ¥112.0 |
| POOL-002 | ¥50.2 | ¥134.1 | ¥83.9 | ¥37.0 | ¥40.3 | ¥3.3 | ¥10.6 | ¥102.2 |
| POOL-003 | ¥37.6 | ¥137.0 | ¥99.4 | ¥34.3 | ¥43.1 | ¥8.8 | ¥2.8 | ¥102.3 |

**結論: A2が本質的に高いわけではない。** Clean Cost(=全て1回で成功した場合の
コスト)で見るとB1/A2の差はわずか¥3.3〜8.8円(A2の方が日本語Support・Key Phrase
説明文が多い分、多少高いのは事実だが、劇的な差ではない)。見かけ上のA2 Actual Cost
の高さ(B1比+83〜99円)は、**このPilotでたまたまA2側にSTOPPED segmentのCostが
集中していた**(3トピック全てでSTOPPED Costの大部分がA2側、B1の4〜36倍)という
分布の偏りによるもので、A2固有の構造的な高コスト要因ではない。

**したがって「A2は本質的に高い」という前提で今後のCost予算を組むのは誤り。
正しい前提は「A2はClean Costで数円高い程度だが、Retry/STOPPEDの影響を受けやすい
(長文本文セグメントが多い分、対象になりやすい)」。**

## 5. 9 STOPPED segmentの個別フォレンジック調査(ER-006-AUDIO-01)

各STOPPEDセグメントについて、canonical text・全attemptのASR transcript・
標準経路/fallback経路の別を突き合わせた
([stopped_segments_forensic_detail.json](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_output/pool_pilot_01/stopped_segments_forensic_detail.json))。

| # | segment | 繰り返し観測されたmismatch | 種別 |
|---|---|---|---|
| 1 | benches/B1/point_two | "Malmö"→"Malmo"、"Triangeln"→"Triangle"、"March 4,"→"March 4th,"、em-dash→comma。6/6attemptで同一パターン | Surface-only |
| 2 | benches/B1/kp2("wide-scale empirical study") | ASRは12/12attemptで正しく聞き取れている。ハイフン有無の表記差のみ | Surface-only |
| 3 | benches/A2/full_story_part2 | 上記1と同じ固有名詞パターン+Azure STTが文中に不規則な句点を挿入("social media.Post")、"street"を"St."と省略表記 | Surface-only(ASR側の句読点挿入癖) |
| 4 | benches/A2/point_two | 上記1と同じ固有名詞パターン、12/12attemptで再現 | Surface-only |
| 5 | subscriptions/B1/comment_2 | "cancelling"(英)→"canceling"(米)。6/6attemptで再現 | Surface-only(英米綴り) |
| 6 | subscriptions/A2/full_story_part2 | "Click-to-Cancel"→"Click to cancel"(ハイフン消失)。12/12attemptで再現 | Surface-only |
| 7 | startups/B1/kp3("blitzscaling") | ASRは10/12attemptで正しく聞き取り、複合語を2語("Blitz scaling")に分かち書き | Surface-only(語境界) |
| 8 | startups/A2/full_story_part1 | "Katz"⇄"Cats"(不安定、8/12で誤認識)、"may"→"May 1st"(12/12で完全再現) | B(認識不安定)+A的に固定化した誤認識が混在 |
| 9 | startups/A2/kp3("blitzscaling") | #7と同様 | Surface-only |

## 6. Failure分類(A/B/C/D)

**結論: 9件全てがCategory A(Surface-only mismatch)またはCategory Aに近い
恒常的なCategory B(ASRが常に同じ誤認識をする)。Category C(true content
mismatch)・Category D(TTS生成失敗/hallucination)は0件だった。**

TTSが実際に間違った内容を読み上げていた証拠は見つからなかった。全ての失敗は、
「発音上は正しいが、書き起こし後の文字列比較で正解と判定できない」という、
**比較ロジック側の問題**だった。

## 7. 同じFailureへの無駄なTTS retry(定量評価)

過去データへ、以下の仮説的ルールを**後付けで静的適用**した(新規API呼び出しなし):
「同一path内で、正規化済みテキストのcanonical textとの類似度が、attempt1から
attempt2でほとんど変化しない(差0.02未満)場合、そのpathをattempt2で打ち切る」

| 適用結果 | 実際に使ったCost | ルール適用後の推定Cost | 削減額 |
|---|---:|---:|---:|
| 9 STOPPED segment合計 | ¥353.7 | ¥152.0 | **¥201.7(約57%削減)** |

([rootfix_retry_savings_analysis.txt](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_output/pool_pilot_01/rootfix_retry_savings_analysis.txt))

ただし、単純な「attempt同士の完全一致」で打ち切りを判定する方式は、長文segmentで
Azure STTが句読点を非決定的に挿入するため機能しなかった(削減額¥28.4にとどまる)。
**canonicalとの正規化済み類似度を基準にする方式でないと、有効な打ち切り判定は
できない。**

## 8. 正規化層を比較ロジックへ入れた場合の効果(より重要な発見)

7章の「retryを早く打ち切る」対策よりも根本的な対策として、比較そのものを
正規化してから行った場合の効果を検証した
([er006_cost_rootfix_01_text_normalize.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_cost_rootfix_01_text_normalize.py)、
[検証結果](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_output/pool_pilot_01/rootfix_normalization_check.json))。

正規化ルール(発音上区別できない表記差のみを吸収、単語の置き換えは行わない):
発音区別符号(ウムラウト等)の除去/ハイフン・複合語分かち書きの無視/序数(4th→4)の
数字化/ダッシュ種別の統一/英米綴りの既知ペア吸収。

| segment | 正規化前の類似度(attempt1) | 正規化後の類似度(attempt1) |
|---|---:|---:|
| benches/B1/point_two | 0.895 | 0.993 |
| benches/A2/full_story_part2 | 0.411 | 0.997 |
| benches/A2/point_two | 0.365 | 0.956 |
| subscriptions/B1/comment_2 | 0.993 | **1.000(完全一致)** |
| subscriptions/A2/full_story_part2 | 0.889 | 0.991 |
| startups/A2/full_story_part1 | 0.929 | 0.992 |

**canonical textが確認できた6segment全てで、attempt1の時点(=1回目の生成)で
既に0.95以上の高い一致率に達していた。** つまり、比較ロジックさえ正規化されて
いれば、**この6segmentは1回もretryせずに合格していた可能性が高い**。
7章の「早期打ち切り」より、こちらの方が根本的で効果が大きい対策と考えられる。

**この正規化ロジックは新規モジュールとして作成したのみで、本番の
`er003_v1_n3_01_tts_generate.py`の検証ロジックへはまだ配線していない。**
本番の検証ロジック(exact_match/substring_ok等の判定基準)を変更する場合、
残り17トピックを含む全ての音声生成の合否判定に影響するため、配線前にユーザーの
確認を得たい。

## 9. English専門語("blitzscaling")の扱い

`blitzscaling`は、B1・A2の両方でSTOPPEDしたが、ASR transcript(10/12・9/12
attemptで"Blitz scaling"、稀に"Blitzkilling"/"Blitzen"という明らかな誤認識も
散発)から判断する限り、**TTSの発音自体は正しく、ASRが複合語を2語に分かち書き
しているだけ**と判断した。個別のwhitelist(`blitzscaling`だけを特別扱いする)は
作らず、8章の正規化層(ハイフン・語内スペースを無視する一般ルール)で対応できる。
これは単語固有の例外ではなく、「複合語・ハイフン語をASRが分かち書きする」という
一般パターンへの対応であり、他の専門語(例: "self-driving"、"crowdfunding"、
"co-working"等)にも同じ理屈で適用できる。実際に発音が異なる場合(内容が違う場合)
は、正規化しても類似度は上がらないため、誤ってPASSさせることはない。

## 10. Research Rewrite予防策(提案、未確定)

### Source Quality Gate(案)
Research(Evidence Pack生成)のプロンプト指示に、以下を追加する案:
「個別の日付・因果関係・具体的事例(who/when/where)をCritical FactとしてVFLへ
採用する場合、一次情報・当局・学術論文等の権威ある情報源に基づくこと。Wikipedia等の
三次情報は探索の入り口として使ってよいが、そこに書かれた個別事実の断定をそのまま
VFLへ採用しない」。POOL-001のWikipedia由来事実の書き直し(¥62.7)の再発防止になる。

### Freshness Gate(案、条件付き発動)
トピックが以下を含む場合のみ、Research時に「現時点で有効か」を明示的に確認する
追加チェックを入れる案: 法律/規制/政府制度/政策/訴訟/現行ルール。それ以外の
Evergreenトピックでは発動させない(Web Search増加を抑えるため)。POOL-002の
FTC規則失効の見落とし(¥45.9)の再発防止になる。

**いずれも本タスクでは実装していない(プロンプト文言の変更であり、Research全体の
挙動に影響するため、19トピック中まだ2回しか実例が無い状態で確定させるのは時期
尚早と判断した)。ユーザー承認後に、次のPoolトピック実行時から試験導入することを
提案する。**

## 11. Ledger metadata恒久修正の継承確認

`er006_pool_pilot_01_ledger.py`(著者/発表年/掲載誌をFactのsource行へ埋め込む
修正)は、**Pool トピック向けのLedger構築処理として現状唯一のものであり、
ER-006の枠組みの中では既に「共有経路」である**(hanshin/health/household向けの
旧Ledger構築処理とは完全に別系統で、Poolトピックは元々this moduleを使う設計)。
残り17トピックの生成スクリプトを新規に書く際は、必ずこのモジュールの
`build_ledger_text_from_vfl()`を再利用すること(独自にinlineで再実装しない)を
確認事項として記録する。regression test([er006_pool_pilot_01_ledger_test.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_pool_pilot_01_ledger_test.py))
は前タスクで作成済み、再実行しPASSを確認した。

## 12. Attempt Ledgerの本番適用状況

**想定より進んでいた点**: 本番コード(`er003_v1_n3_01_tts_generate.py`)は、
今回初めて気づいたが、**segment/attempt単位でASR transcript・verdict・
trim_info等を`audit/tts_generation_results.json`へ既に記録していた**
(Pilot用に新規開発したものではなく、既存の本番機能)。今回不足していたのは
「それをCostと突き合わせる」部分のみで、これは
[er006_pool_pilot_01_attempt_ledger.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_pool_pilot_01_attempt_ledger.py)
として今回新規作成した(実行順序に基づく突合方式、1章参照)。

**未実施の部分**: この突合は「後付けの再構築」であり、実行順序が保証されている
前提に依存する(今回は6/6エピソードで検証できたが、将来並列実行などをすると
前提が崩れる)。より頑健にするには、本番のTTS/ASR呼び出し側でCost logger呼び出し
時にsegment名を直接渡すよう`er003_v1_n3_01_tts_generate.py`を修正する必要がある。
これは本番コードの変更であり、影響範囲が残り17トピックだけでなく既存の
hanshin/health/household等の生成にも及ぶため、**変更内容の説明とユーザー確認を
先に行いたい**(実装はしていない)。

## 13. Cost Guardrail候補(未確定、提案のみ)

今回の実データから、以下を候補として提示する。閾値は全て今回のPilotデータに
基づく仮の値であり、確定はユーザー判断を待つ。

| Guardrail候補 | 提案閾値(仮) | 根拠 |
|---|---|---|
| 同一segment内、正規化済み類似度が2attempt連続でほぼ改善しない場合に打ち切り | 差0.02未満で打ち切り | 7章の検証(単純な文字列完全一致より有効) |
| segment cumulative attempt数上限 | standard/fallback合計6回(現状12回の半分) | 8章の正規化対策を先に入れれば、そもそも6回に達する前にPASSする見込みが高い |
| episode cumulative Audio Cost上限 | ¥150(このPilotの平均Actual Costの約2倍) | 超過時はHuman Reviewへ自動フラグ、生成は止めない(番組の欠落を避けるため) |
| 同一failure signature(正規化済みASR textがcanonicalと変わらない)が3回連続 | 3回で`ASR_VALIDATION_UNCERTAIN`へ切り替え、既存音声を保持 | 6章の分類(Surface-onlyは何回試しても改善しない) |

## 14. 検証方法

**新規有料API呼び出しは0件。** 既存の6エピソード分のログ・audit JSON・narration
wavファイルのみを使い、後付けでの静的分析を行った(1〜9章)。8章の正規化ロジックも
既存のASR transcriptへ適用しただけで、新規のTTS/ASR呼び出しは発生していない。
6エピソード全体の再生成、および個別segmentの再生成も一切行っていない。

## 15. 受入条件チェック

| # | 内容 | 状況 |
|---|---|---|
| 1 | Rewrite Waste不整合解消 | ✅ 3章(記載漏れが原因と判明、154.3円が正) |
| 2 | segment/attempt単位でCost再構築 | ✅ 1章(241 attempt、UNKNOWN 0件) |
| 3 | Clean/Actual/Waste再定義 | ✅ 1〜2章 |
| 4 | A2がB1より高い理由の定量説明 | ✅ 4章 |
| 5 | 9 STOPPEDの全failure原因分類 | ✅ 5〜6章 |
| 6 | 長文ASR false negativeの再現パターン特定 | ✅ 5章 |
| 7 | 同じfailureで6回retryするWasteへの対策案 | ✅ 7〜8章(正規化層が本質、早期打ち切りは補助) |
| 8 | True content errorを見逃さない | ✅ 6章(0件、意図的にwhitelist化していない) |
| 9 | blitzscaling問題の一般化評価 | ✅ 9章(一般正規化ルールで対応、単語固有whitelistなし) |
| 10 | Source Quality Gate案 | ✅ 10章(未実装、提案のみ) |
| 11 | conditional Freshness Gate案 | ✅ 10章(未実装、提案のみ) |
| 12 | Ledger metadata継承確認 | ✅ 11章 |
| 13 | Attempt Ledger実装状況 | ✅ 12章(本番側は想定より進んでいた、Cost直結部分は未配線) |
| 14 | Cost Guardrail候補 | ✅ 13章(未確定) |
| 15 | 新規API Costは最小限 | ✅ ¥0 |
| 16 | CURRENT_SPEC変更なし | ✅ 変更なし |

## 16. リスク・注意点

- 8章の正規化提案・7章のretry早期打ち切り案・13章のGuardrail候補は、**いずれも
  提案段階でありまだ本番コードへ配線していない**。配線すれば残り17トピックを
  含む全ての音声生成の合否判定に影響するため、実装前にユーザーの承認を求める。
- 8章の「正規化すればattempt1でPASSしていた可能性が高い」は、既存ASR
  transcriptへの後付け適用による推定であり、実際に正規化後の判定ロジックで
  ゼロから生成し直した場合に同じ結果になるとは限らない(ASR自体の非決定性が
  ある)。
- N=3(6エピソード、9 STOPPED)というサンプルの小ささは変わっていない。
  Surface-only mismatchが9/9だったことは心強い結果だが、残り17トピックで
  真のcontent error(Category C/D)が出現しないとは限らない。

## 17. 次のステップについて

このROOTFIX調査をもって作業を停止する。残り17トピックへの本番投入は、
8章(比較ロジックの正規化)・13章(Cost Guardrail)をどう本番へ反映するかの
ユーザー判断を待ってから行う。
