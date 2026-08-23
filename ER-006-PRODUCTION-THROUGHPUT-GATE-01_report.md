# ER-006-PRODUCTION-THROUGHPUT-GATE-01 完了報告

**管理ID: ER-006-PRODUCTION-THROUGHPUT-GATE-01**
**日付: 2026-08-23**

No.4〜6の実際のProduction生成を使い、1 Topicのend-to-end所要時間・複数
Topic並列時の実スループット・20 Topic/dayの現実性を測定した。

## 1. 測定方法とデータソース

- Phase 1(Single Topic Baseline): No.4を単独でend-to-end生成
- Phase 2(Parallel Topic Test): No.5とNo.6を同時刻(2026-08-23 11:45:42 JST)に並列実行
- 全て`er005_cost_logger`が記録した実際のタイムスタンプ・API使用量ログ
  (`er006_output/pool_pilot_01/raw_usage_log.jsonl`)から算出。推測・
  机上計算ではない

## 2. Stage別実測(3 Topic)

| Topic | Research | Writer+Support(累計、反復込み) | TTS(Batch、B1) | TTS(Batch、A2) | Assembly | 総wall-clock |
|---|---|---|---|---|---|---|
| No.4 Supermarket | 86.6s(最終採用run) | 約2,549s(4回のResearch/Writer反復込み、§3参照) | 4,427.0s(73.8分) | 7,957.6s(132.6分) | 4.3s | **14,938s(4.15時間)** |
| No.5 Cafes | 85.3s | 555.8s(1回で収束) | 8,661.6s(144.4分) | 4,544.7s(75.7分) | 4.2s | **13,210.5s(3.67時間)、並列実行** |
| No.6 Delivery | 43.8s | 389.5s(1回で収束) | 約7,622s(127.0分、推定) | 8,760.4s(146.0分) | 4.1s | **16,831s(4.67時間)、並列実行+自己復旧作業込み** |

**TTS(Audio)stageが総所要時間の83〜95%を占める**(No.4=83.0%、No.5=
93.4%、No.6=95.8%)。Research+Writer+Supportは反復なしなら合計10〜15分
程度で、TTSと比較すると誤差程度の比重でしかない。

## 3. No.4で発生した反復について(正直な内訳)

No.4は初回の情報源選定が薄く(学術論文2件のみ)、Ledger逸脱チェックが
MAJOR3件を検出したため、情報源を段階的に4件まで追加しながらResearch→
Writerを3回再実行した。これは**情報源選定の質という一回限りの問題**
であり、Batch TTS自体の遅さとは独立した要因である。No.5・No.6は
初回の情報源選定で十分な結果が得られ、Writer+Supportは1回で収束して
いる(No.5: 555.8秒、No.6: 389.5秒)。今後のTopic(No.7以降)でも、
情報源選定さえ丁寧に行えば、この種の反復は必須ではないと考えられる
(ただしFact Checker/Ledger Deviation Checkによる指摘自体は、正しく
機能している安全装置であり、今後も発生しうる)。

## 4. Batch Job数・Retry数・Human Review数

| Topic | Batch job数 | Batch成功 | Batch技術的失敗(自動retry) | STOPPED/ASR_VALIDATION_UNCERTAIN区間数 |
|---|---|---|---|---|
| No.4 | 67 | 65 | 2 | 1(A2 comment_2) |
| No.5 | 67 | 66 | 1 | 2(B1 full_story_part1/2) |
| No.6 | 88 | 88 | 0 | 3(B1 full_story_part1[UNCERTAIN]、A2 full_story_part1・point_one[STOPPED]) |

Human Review行きの区間は、既存3記事(No.1-3)で確認された固有名詞ASR
誤認識パターン(Ottoni型)と同種のもの(No.5の"The Barn"・"Neukölln"、
No.6の研究者名等)が中心と見られる。詳細はUser Review Artifact参照。

## 5. Data Race / Logging Corruption チェック(STOP条件)

No.5・No.6の並列実行を通じて、共有ログファイル
(`raw_usage_log.jsonl`)への同時書き込みを監視した。並列フェーズ終了
時点で全1,783行を検証し、**JSON解析エラーは0件**だった。Master Audio
Storeについても、No.4の完走時点で共通ナレーション(Welcome/番号読み上げ
等)のキャッシュが既に温まっていたため、No.5・No.6は主に既存キャッシュ
を再利用する形となり、書き込み競合の実質的なリスクは低かった(トピック
固有のnarrationファイルは各トピック専用のパスに書き込まれるため、
そもそもパス衝突がない設計)。**STOP条件(data race/logging corruption)
には該当しなかった。**

## 6. 20 Topic/day 判定

### 6-A. 1-lane throughput

TTSが支配的なため、Research/Writer反復なしの「クリーンな1 Topic」の
所要時間は、No.5の実績(約3.67時間、TTS約220分+その他約11分)を代表値
として採用する。

24時間 ÷ 3.67時間/Topic ≈ **6.5 Topic/day(1 lane)**

### 6-B. Observed parallel throughput(2 lane)

No.5・No.6は同時刻に開始し、No.5が3.67時間、No.6が4.67時間(自己復旧
作業込み、純TTS作業時間ベースでは約4.55時間)で完了した。2 lane並列
実行によって、**単独実行(No.4: 3.44時間TTS)と比べて個々のTopicの
所要時間に大きな劣化は見られなかった**(No.5のTTSはむしろNo.4よりやや
長いが、誤差・content差の範囲)。これは、Gemini Batch APIが2並列
リクエストを大きく減速させずに処理できることを示唆する。

2 lane・約4時間で2 Topic処理できたとすると:
24時間 ÷ 4時間 × 2 lane ≈ **12 Topic/day(observed 2-lane concurrency)**

### 6-C. 20 Topic/dayに必要な推定parallelism

20 Topic/day ÷ 6.5 Topic/day/lane ≈ 3.08 lane

**最低4 lane相当の並列実行**が必要と推定される(3 laneでは約19.5
Topic/dayとわずかに届かない計算になるため、安全マージンを見て4 lane)。

### 6-D. 30 Topic/day参考値

30 Topic/day ÷ 6.5 Topic/day/lane ≈ 4.6 lane → **5 lane相当**が必要と
推定される。

### 6-E. ボトルネック工程

**Gemini Batch TTS(Audio生成stage)が明確なボトルネック**である
(全Topic共通で総所要時間の83〜96%を占める)。Research/Writer/Support
は合計しても10〜45分程度で、Audio生成(3.4〜4.7時間)と比べると小さい。

### 6-F. 仮説の検証結果(タスク仕様§22)

- **仮説A(並列Topic化だけで20 Topic/day達成可能)**: 部分的に支持
  される。2 lane並列で個々のTopicの所要時間が大きく劣化しなかった
  ことは、並列化がスケールする可能性を示唆する。ただし4〜5 laneでの
  検証は未実施であり、この規模での挙動は未確認
- **仮説B(1 segment=1 Batch jobの待ち時間が支配的で、並列Topic化
  だけでは不足する)**: 支持される。TTS/Audio stageが全Topicで
  総時間の83〜96%を占めており、これはToPic単位の並列化では解消され
  ない、segment単位の待ち時間の積み上げそのものである。20 Topic/day
  達成には、Topic並列化に加えて相応の数のlane(推定4本以上)が必要
- **仮説C(ボトルネックはTTSではなくResearch/Writer/Retry)**: 支持
  されない。Research+Writer+Support(反復なし)は合計10〜15分程度で、
  TTS(3.4〜4.7時間)と比べて桁違いに小さい

### 6-G. 判定

**`AT_RISK`**

根拠:
- 数値上は4 lane並列実行で20 Topic/dayの理論値(約26 Topic/day相当)
  に届く。2 lane並列での実測は、この方向性を支持する結果だった
- ただし、今回実測できたのは**2 lane並列のみ**であり、4〜5 laneでの
  実際のAPI rate limit・コスト・システムリソースへの影響は未検証
- No.6のように複数segmentがSTOPPED/UNCERTAINになるTopicでは、TTSの
  所要時間が最大で32%程度伸びる(No.4比)ことを実測した。Topicごとの
  ばらつきを考慮すると、平均値ちょうどでの運用は余裕がない
- Human Reviewに要する実際の人手時間は、今回の測定に含まれていない
  (機械側の所要時間のみ)
- したがって「20 Topic/dayは現実的に見込めるが、実証されたとは言えず、
  マージンが薄い」という`AT_RISK`評価が最も正確である。3 Topicのみの
  測定であることを踏まえ、「20 Topic/day実証済み」とは書かない

## 7. このタスクでは速度改善を実装していない

Batch multi-item化・大規模parallel worker化・queue architecture変更・
concurrency制御新設は、タスク仕様§21により実装していない。上記の
判定・推定はあくまで測定結果の報告であり、改善策の実装判断は次タスク
に委ねる。

## 8. Cost(参考情報、原価再最適化はスコープ外)

| Topic | Research+Writer+Support | TTS(Batch) | ASR(English, OpenAI) | ASR(Japanese, Azure) | 合計 |
|---|---|---|---|---|---|
| No.4 | ¥73.5 | ¥54.6 | ¥4.2 | ¥11.2 | **¥143.5** |
| No.5 | ¥21.5 | ¥62.7 | ¥5.7 | ¥5.8 | **¥95.6** |
| No.6 | ¥18.4 | ¥85.0 | ¥8.1 | ¥5.9 | **¥117.4** |
| 平均 | ¥37.8 | ¥67.4 | ¥6.0 | ¥7.6 | **¥118.8** |

既存のExpected Production Cost baseline(¥111.17/pair、ER-006-
VALIDATOR-NUMERIC-COST-RECONCILE-01)と近い水準。No.4のみ情報源反復
分だけ高い。3件のみのサンプルであり、この結果だけで原価モデルを
再設計しない(タスク仕様§23の通り)。

## 参照元

[POOL_TOPIC_MASTER.md](POOL_TOPIC_MASTER.md)、
[ER-006-POOL-ADOPTION-AUDIT-01_diff.md](ER-006-POOL-ADOPTION-AUDIT-01_diff.md)、
`er006_output/pool_pilot_01/pool_n4_supermarket/throughput_summary.json`、
`er006_output/pool_pilot_01/{pool_n4_supermarket,pool_n5_cafes,pool_n6_delivery}/cost_summary.json`
