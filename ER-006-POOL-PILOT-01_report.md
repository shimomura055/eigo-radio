# ER-006-POOL-PILOT-01 完了報告

## 1. 何をしたか(目的)

固定Poolトピック3本(社会・暮らし/ビジネス/スタートアップ)を、Topic Selectionを飛ばして
（コスト0円）、既存の本番アーキテクチャ(Source Search→Evidence Pack→VFL→Verification→
Writer→Fact Check→Support→Support Fact Check→TTS→ASR/Audio QA→Assembly)にそのまま
通し、B1・A2それぞれの完成品を作った。目的は「20トピック本番投入の前に、実測コスト・所要
時間・失敗パターンのベースラインを取ること」。3トピックだけでは統計的に確定的な結論は出せ
ないため、本報告でも「これで安心」「これはダメ」のどちらの断定も避けている。

対象トピック:

| コード | カテゴリ | タイトル |
|---|---|---|
| ER-006-POOL-001 | 社会・暮らし | Why Are More Cities Rethinking Public Benches? |
| ER-006-POOL-002 | ビジネス | Why Do Companies Make Subscriptions So Easy to Start—and Hard to Stop? |
| ER-006-POOL-003 | スタートアップ | Why Do Some Startups Chase Growth Before Profit? |

3トピックとも、特定の1件の最近の出来事に依存しない Pool型(Evergreen) 記事として作成した
(現行ニュース記事ではない)。

## 2. 出来上がったもの

- 3トピック × B1/A2 = 6エピソード、すべて音声組み立てまで完成
- Human Review用ページ(3本、トピックごとにB1/A2両方を掲載):
  - [ER-006-POOL-001 公共のベンチ](https://claude.ai/code/artifact/3e69dc86-e4de-4585-8a6a-ee7b878f2075)
  - [ER-006-POOL-002 サブスクリプション](https://claude.ai/code/artifact/6f64f4a9-1385-405c-a916-e47a85cb77cb)
  - [ER-006-POOL-003 スタートアップ](https://claude.ai/code/artifact/60eb7960-bd0e-4c2f-ae21-cc1a3f4d7d5d)

各ページに、B1/A2の音声プレーヤー・記事本文・Fact Check結果・Audio QAサマリー・Needs
Reviewフラグ・Cost/Timeを掲載している。**自然さ・面白さ・聞きやすさ・B1/A2の難易度が適切か
といった主観評価は、Claudeでは判断できないため確定させていない。実際に聞いて確認してほしい。**

## 3. Cost(実測、1USD=160円換算)

### 3-1. トピック別・工程別(Shared/B1/A2)

| トピック | Shared(Research) | B1 | A2 | 実際に使ったCost合計(Actual Pair Production) |
|---|---:|---:|---:|---:|
| POOL-001 ベンチ | ¥5.1 | ¥124.1 | ¥203.6 | **¥332.8** |
| POOL-002 サブスク | ¥4.5 | ¥90.3 | ¥177.2 | **¥272.0** |
| POOL-003 スタートアップ | ¥2.4 | ¥89.6 | ¥186.9 | **¥278.9** |
| 平均 | ¥4.0 | ¥101.3 | ¥189.2 | **¥294.6** |

按分Cost(management用の便宜的な数字。Shared分をB1/A2で50/50に割っただけで、実際に別々に
支払っているわけではない):

| トピック | B1エピソード按分 | A2エピソード按分 |
|---|---:|---:|
| POOL-001 | ¥126.6 | ¥206.2 |
| POOL-002 | ¥92.5 | ¥179.4 |
| POOL-003 | ¥90.8 | ¥188.1 |

A2の方がB1よりコストが高い(平均¥189 vs ¥101)。理由はA2の方が日本語コメント量・Key
Phrase説明が多く、TTS/ASRの呼び出し量が多いため(下記3-2)。

### 3-2. TTS/ASRの内訳(Clean/Actual/Waste、Level別)

| トピック | Level | 種別 | Actual | Clean(推定) | Retry Overhead(推定) |
|---|---|---|---:|---:|---:|
| POOL-001 | B1 | TTS | ¥38.4 | ¥22.1 | ¥16.3 |
| POOL-001 | B1 | ASR | ¥19.5 | ¥11.2 | ¥8.3 |
| POOL-001 | A2 | TTS | ¥94.3 | ¥48.2 | ¥46.2 |
| POOL-001 | A2 | ASR | ¥49.3 | ¥25.2 | ¥24.1 |
| POOL-002 | B1 | TTS | ¥33.6 | ¥20.9 | ¥12.7 |
| POOL-002 | B1 | ASR | ¥16.6 | ¥10.3 | ¥6.3 |
| POOL-002 | A2 | TTS | ¥88.0 | ¥60.4 | ¥27.7 |
| POOL-002 | A2 | ASR | ¥46.1 | ¥31.6 | ¥14.5 |
| POOL-003 | B1 | TTS | ¥25.3 | ¥16.1 | ¥9.1 |
| POOL-003 | B1 | ASR | ¥12.4 | ¥7.9 | ¥4.5 |
| POOL-003 | A2 | TTS | ¥90.2 | ¥46.1 | ¥44.1 |
| POOL-003 | A2 | ASR | ¥46.8 | ¥23.9 | ¥22.9 |

**この表の「Clean」「Retry Overhead」は推定値であり、実測ではない。** 理由: 生ログ
(`raw_usage_log.jsonl`)にはTTS/ASRの呼び出しがどのセグメント(topic_introかcomment_1か
等)に対応するかの記録が無く、1エピソードにつきTTS 1回+ASR 1回を理論上の最小(Clean)と
みなして呼び出し件数から按分する方法しか取れなかった。実測できるのは各Levelの「Actual
Cost合計」のみ。より精密な区分が必要な場合、cl.record()呼び出し側にsegment名を渡すよう
本番コードを改修する必要がある(このPilotでは本番コード自体は無変更のため未実施)。

### 3-3. Rewrite Waste(実測に近い)

Research/Writerの再実行(下記4章参照)は生ログのタイムスタンプの間隔から特定でき、実測に
近い精度がある:

| トピック | Rewrite Waste | 内容 |
|---|---:|---|
| POOL-001 | ¥62.7 | Wikipedia由来の個別事実がFact Checkで否認され、Research再実行 |
| POOL-002 | ¥45.9 | FTC Click-to-Cancel Ruleの2025年失効を反映するためResearch再実行 |
| POOL-003 | ¥0 | Research再実行なし(Ledger整形のみ修正、Research自体は再実行していない) |

### 3-4. 全体合計

- Actual Cost合計(3トピック×B1/A2、6エピソード): **¥883.8**(約$5.52)
- Clean Cost(推定、上記按分方式): ¥336.0
- Rewrite Waste(実測): ¥154.3
- Retry-Fallback Waste(TTS/ASR、推定): ¥393.6
- Operator-error Waste: ¥0(下記5-3参照、実際には課金前にクラッシュしたため無課金)
- 総API呼び出し数: 587件

## 4. Rewrite原因の分類(3区分)

タスク仕様で指定された3区分(個別記事固有／パイプライン共通の恒久修正が必要／サービス仕様
変更が必要)で分類した。**残り17トピックで同じ問題が再発するか**を基準に分けている。

### A. 個別記事固有(Article-specific) — その記事だけ直せば済む

1. **POOL-001(ベンチ)**: Wikipediaの「Hostile architecture」記事から引用した個別の事例
   (Stockholm 2015年のベンチ撤去、Malmö 2010年の日付・「意図的な排除デザイン」という
   断定、Luleå鉄棒の設置)が、本番Fact Checker(実際にWeb検索を使う)による一次情報照合で
   裏付けを得られなかった。三次情報源(Wikipedia)を個別の日付・因果の断定に使ったことが
   原因で、パイプラインの欠陥ではない。`raw_sources.json`を修正し(該当箇所を曖昧化・
   Fact Checker自身が裏付けた情報に置き換え)、Research・Writerを再実行して解消。
   → 残り17トピックでも同種の「三次情報源への依存」は起こり得るが、これはResearch段階の
   出典選定の質の問題であり、都度同じ手順(Fact Checkが弾いたら出典を直して再実行)で
   対応可能。パイプライン自体の変更は不要。

2. **POOL-002(サブスクリプション)**: 記事執筆時点で「FTCのClick-to-Cancel Rule(2024年)は
   現行法である」という前提で書いたが、2025年7月8日に第8巡回区控訴裁判所がこの規則を無効化
   していた(学習データのカットオフ後の実際の法制度変更)。これはEvergreen記事が抱える
   「一見普遍的に見えるテーマでも、時間依存の要素が隠れている」というリスクの実例。
   `raw_sources.json`を修正(規則を「過去に存在した／係争中」と再整理し、無効化の事実を
   追加)し、Research・Writerを再実行して解消。
   → こちらも個別記事固有の事実確認漏れであり、パイプライン変更は不要。ただし今後の
   Poolトピック選定・Research時に「法制度・規制に触れる場合は最新の係争状況を明示的に
   確認する」という運用上の注意点として記録しておく価値がある(仕様変更ではなく運用メモ)。

### B. パイプライン/システム的(恒久修正+regression test実施済み)

3. **POOL-003(スタートアップ)**: Ledgerの`[source: ...]`行に内部ID(`SRC-003/E-001`)しか
   含まれておらず、Writerが記事内で出典に触れる際、著者名・発表年・掲載誌名をLedgerからでは
   なく自身の一般知識から補って記述していた。その記述自体は事実として正しかったが、Ledger
   Deviation Check(記事はLedgerの範囲を超えてはならない)が「Ledgerにない新規Fact」として
   誤検知していた(B1/A2合わせて5件、いずれもMINOR中心)。
   → **これはLedger変換ロジック自体の欠陥であり、残り17トピック全てで再発する。**
   恒久対策として [er006_pool_pilot_01_ledger.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_pool_pilot_01_ledger.py)
   を新規作成し、各Factの`source:`行に著者/組織・発表年・掲載誌を直接埋め込むよう変更。
   Evidence Packスキーマにも`journal_or_venue`フィールドを追加した。
   Regression testとして [er006_pool_pilot_01_ledger_test.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_pool_pilot_01_ledger_test.py)
   を作成し、Source一覧セクションの存在・Factのsource行への著者名/発表年/掲載誌の反映を
   assertで検証している(実行済み、PASS)。
   Ledger再構築後、Writerを再実行したところ逸脱件数は5→3件(B1)、5→1件(A2)まで減少。
   ただしPOOL-003自体のEvidence Packは`journal_or_venue`追加前のデータのままのため、
   残る数件(掲載誌名・著者フルネームの省略)は未解消のまま許容した(2回の書き直し後の
   費用対効果を考慮した判断。詳細は5章)。

### C. サービス仕様変更が必要 — 該当なし

このPilotでは、B1/A2の構成・Support構成・番組設計そのものを変更しなければ解決しない問題は
発生しなかった。**サービス仕様(CURRENT_SPEC.md)は本タスクで一切変更していない。**

## 5. 失敗(Failure)ログ

### 5-1. Fact Check起因の書き直し(4-1参照、詳細は上記)

### 5-2. TTS/ASR STOPPEDセグメント(9件、全エピソード合計)

「STOPPED」は、規定の再試行回数を尽くしてもASR検証に合格しなかったセグメントで、本番の
既存仕様どおり「最後に生成した(未検証の)音声をそのまま採用」して組み立てを継続したもの。
Assembly自体は失敗しておらず、音声に無音の欠落は無い。**ただし音声内容が正確か・不自然でない
かはHuman Review未実施のため、上記Reviewページでの確認が必要。**

| トピック | Level | セグメント | 推定原因 |
|---|---|---|---|
| POOL-001 | B1 | point_two | ASR verdict=FAIL 6回連続(Malmö/MTA等の固有名詞・数字を含む長文で、ASR側が誤認識を繰り返した可能性) |
| POOL-001 | B1 | Key Phrase 2 (英語) | 同上系統 |
| POOL-001 | A2 | full_story_part2 | 標準経路・minimal instruction経路とも6回不合格。ASR側の句読点挿入・大文字化の揺れ(例: "St."と表記されるなど)によるsubstring不一致が主因と推定(ASR false negativeの可能性が高い) |
| POOL-001 | A2 | point_two | 同上 |
| POOL-002 | B1 | comment_2 | ASR verdict=FAIL 6回連続 |
| POOL-002 | A2 | full_story_part2 | POOL-001と同系統(長文・ASR側の表記揺れ) |
| POOL-003 | B1 | Key Phrase 3 (英語、"blitzscaling") | 専門用語("blitzscaling")の発音・ASR認識が難しかった可能性 |
| POOL-003 | A2 | full_story_part1 | 長文セグメント、ASR表記揺れ系 |
| POOL-003 | A2 | Key Phrase 3 (英語、"blitzscaling") | B1と同一原因の可能性(同じ単語がB1/A2両方でSTOPPED) |

**再発するか**: `full_story_part1/2`のような長い英語ニュース本文セグメントでのSTOPPED
(6件中4件)は、ASRの表記揺れによるfalse negativeが疑われるパターンとして、6エピソード中
複数回・複数トピックで再現している。これは個別記事固有ではなく、**長文セグメントに対する
ASR検証ロジックの構造的な弱点である可能性がある**(パイプライン/システム的な論点候補)。
ただしOPEN-05(音声ハルシネーション根本原因)がUNDER_REVIEWのままである(下記6章)のと
同様、このPilot(N=3)だけでは「長文セグメントのASR検証を緩和すべき」と断定するには材料が
不足している。**本タスクの範囲では追加のコードロジック修正は行わず、事象の記録に留めた。**
残り17トピックの実行時にも同様の傾向が続くか観察を推奨する。

`blitzscaling`のようにB1・A2の両方で同じ単語がSTOPPEDになったケース(POOL-003)は、
特定の専門用語の発音がTTS/ASR双方にとって難しい可能性を示す一例。

### 5-3. Operator-error(実装上のミス)

POOL-001のA2音声生成で、本番コードの`JAPANESE_TITLES`辞書(hanshin/health/household用
にハードコードされていた)に新規3テーマの日本語タイトルが登録されておらず`KeyError`で
クラッシュした。ログのタイムスタンプを照合したところ、**クラッシュはA2音声の最初の課金
呼び出しより前に発生しており、無駄になった費用は¥0**だった。修正(`er006_pool_pilot_01_
audio.py`内でランタイムに辞書へ追記、本番ファイル自体は無変更)後、A2音声のみ再実行して
解消。

### 5-4. OpenAI API支出上限ブロック(タスク進行上の中断、Failureではない)

Topic2/3のWriter再実行中に`organization_spend_limit_exceeded`(組織のAPI支出上限)で
中断。これはコード側の不具合ではなくアカウント設定の制約のため、リトライで回避せず作業を
停止してユーザーに報告し、ユーザーが上限を引き上げた後に再実行して解消した。

### 5-5. 発生しなかった失敗タイプ

タスク仕様に挙げられていた失敗タイプのうち、INVALID_ARGUMENT・instruction leakage・
TRUE_CONTENT_MISMATCH・verification failure(Research Verification自体の不合格)は、
このPilotの6エピソードでは一度も発生しなかった。Exception Search(Perplexity、
NEEDS_EXTERNAL_CHECK時のみ発動)も1件も呼び出されていない(全FactがEvidence Pack内で
検証完結)。**これはN=3という少ないサンプルでの結果であり、「これらの失敗はもう起きない」
とは結論できない。**

## 6. 既存Audio Hardening機能の動作確認

| 機能 | 確認状況 |
|---|---|
| Structured Separation | 本番`build_tts_prompt()`を無変更で使用。B1の`point_one_heading`/`point_two_heading`で"english_style_prefix"戦略によるEXACT_MATCH成功ログを確認(例: `attempt 1 (english_style_prefix): asr='Speed needs a dashboard.' verdict=EXACT_MATCH`)。instruction leakage系の失敗は0件で、機能していたと考えられる |
| 日本語短語のphonetic validation | Key Phraseの日本語meaning生成が"reading-safety"経路(Charon音声)で全て実行されたことをログで確認。実際にphonetic不一致で救われた具体的な1件を個別特定するところまでは今回未実施 |
| 数字/ハイフンの正規化 | 本番コード無変更で適用されている想定だが、このPilotで具体的な発動インスタンスの特定(ログからの抽出)は行っていない |
| Duration anomaly検知 | 今回の6エピソードで異常時間として明示的に検知・却下されたセグメントは確認できなかった(STOPPEDは全てASR verdict=FAILによるもので、durationそのものが原因ではない) |
| Point Notification番号ラベル漏れ防止 | 全エピソードでPoint番号のラベル漏れ報告なし(機能していたと考えられる) |
| Trim safety margin | `attempts_log`のtrim_info(leading/trailing margin)が全セグメントで記録されていることを確認。異常な切り詰めは報告なし |

**OPEN-05(音声ハルシネーション根本原因)は本Pilotでも新たな知見が無く、引き続き
UNDER_REVIEWのまま。**「完全に解決した」とは扱っていない。

## 7. リスク・注意点

- **推定値と実測値の区別**: TTS/ASRのClean/Retry-Waste内訳は推定(セグメント名がログに
  無いため)。Actual Cost合計・Rewrite Waste・所要時間は実測(ログのタイムスタンプ・
  トークン数から直接算出)。
- **所要時間のベンチマーク条件からの逸脱**: タスク仕様は「3トピックを逐次処理」を前提として
  いたが、実際にはTopic1を先に単独でチェックポイント検証してからTopic2・3をまとめて処理する
  進め方を取った(手戻りリスクを早期に発見するため)。そのため生ログの最初〜最後の
  タイムスタンプ差(観測Wall-clock)には、チェックポイント確認やAPI支出上限による中断待ちが
  混入している。今後の見積もりには、各工程の最終実行分だけを合計した`stage_sum_
  CLEAN_RUN_ONLY`(トピックあたり平均約45分、B1+A2合計)を使う方が実態に近い。
- **N=3の限界**: 発生した失敗・書き直しは全て個別に原因を特定し対応したが、サンプル数が
  少ないため「Poolトピック生成はもう安定した」とも「まだ危険」とも断定していない。長文
  セグメントのASR STOPPEDパターン(5-2)は残り17トピックでの再現有無を継続観察したい。
- **主観評価は未実施**: 自然さ・面白さ・聞きやすさ・B1/A2の難易度感については、Human
  Reviewページを実際に聞いて確認してもらう必要がある。Claudeでは判定していない。

## 8. 対象外(このタスクではやっていないこと)

TTS/ASRプロバイダー比較、Personalized episode、Current Affairs記事、Recommendation機能、
UI開発、実ユーザーテスト、残り17トピックを含む20トピック全体の本番投入、サービス価格設定
変更、B1/A2仕様変更 — いずれも未実施。**サービス仕様(CURRENT_SPEC.md / DECISION_LOG.md /
OPEN_ITEMS.md)は本タスクで一切変更していない。**

## 9. 次のステップについて

タスク仕様どおり、このPilot(3トピック)の完了をもって作業を停止する。残り17トピックへの
本番投入は、このReviewページの主観評価結果と合わせてユーザーの判断を待つ。
