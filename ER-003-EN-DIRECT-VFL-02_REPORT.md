# ER-003-EN-DIRECT-VFL-02 実行報告(A01 + ADD03 Cross-topic Stress Test)

**管理ID: ER-003-EN-DIRECT-VFL-02**
**実施日: 2026-08-12**
**ステータス: `PROTOTYPE / EXPERIMENT`(A01・ADD03限定の実験系。Production仕様は変更していない。採否はユーザー判断待ち)**

## 重要な前置き: 初回実行でスクリプトのバグを発見・修正した

初回実行(A01・ADD03とも1回ずつ)では、**両記事ともfact checkerがFAILと判定**した。
原因を調査したところ、**筆者(本エージェント)側のスクリプト実装ミス**であることが
判明した。ER-003-EN-DIRECT-VFL-01のResearcherプロンプトテンプレートには、
【今回、特に構造化して含めるべきFact】節にA02固有の内容(Overnight curfew・
autoplay・pilot 309人等)がハードコードされており、これをtopic文字列だけ差し替えて
そのまま再利用した結果、ADD03のResearcher呼び出しにもこの指示が混入し、
実際に**ADD03のFact Ledger(26件中20件)が無関係なUK SNS curfewの話題で
汚染された**(A01は汚染の影響が実害として現れなかったが、同じ欠陥のあるプロンプトを
使用していた)。

この汚染自体は最終記事本文には出力されなかった(writerが無関係facts を無視した
ため)が、「記事ごとに独立したFact Ledgerを持つ」という受入条件2を実質的に
満たしていなかったため、**プロンプトを修正した上でA01・ADD03とも再実行した**。
本報告の主結果は、この修正後の再実行を指す。初回(バグあり)の生成物は
`er003_output/en_direct_vfl_02_run1_prompt_bug/`に証拠として保持している。

この件と、初回のfact checker FAIL自体の原因(下記)は独立した2つの問題である。

## A. Executive Summary

| | 初回実行(プロンプトにバグあり) | 再実行(修正後) |
|---|---|---|
| A01 fact status | FAIL(試合統計の不一致) | **PASS** |
| ADD03 fact status | FAIL(intraday高値の不正確な確定) | **PASS** |
| Ledger compliance | 両記事ともLEDGER_COMPLIANT(0件) | 両記事ともLEDGER_COMPLIANT(0件) |
| 追加Run | — | A01・ADD03とも1回追加実行(理由: 初回FAIL、かつスクリプトバグ修正のため) |

**再実行(修正後)の結果、A01・ADD03とも成功**。ERROR-1型(制度・データscope誤り)・
ERROR-2型(数字scope誤り)に相当する重大な誤りは検出されず、Ledger逸脱も
両記事とも0件だった。

## B. A01

### Fact Ledger概要
- Researcherが30件のFactを収集(Web検索15回)、独立Verificationで**30件全件VERIFIED**
  (AMBIGUOUS・REJECTEDともに0件)
- 得点者・アシスト・得点時刻(55分/85分/90+2分)・途中出場(81分)・試合統計
  (シュート数15対5、xG 1.47対0.46、ポゼッション56.5%対35.2%、パス成功数)を
  FIFA公式Post Match Statistics Report等から構造化

### Article
- タイトル: "England Saw the Final—Then Messi Opened the Door"
- **word count**: 354語(soft target 289〜391語の範囲内)

### Fact QA
- **`PASS`**(独立fact checker、Web検索7回、矛盾・未確認主張ともに0件)
- 初回実行でFAILの原因だった「シュート数14本」(FIFA公式記録は15本)は、
  Researcher段階でのSource選定強化(重点確認事項へ「最も確定的な一次資料を
  優先」を追加)により、再実行では正しい15本が採用された

### Ledger deviation
- `LEDGER_COMPLIANT`(逸脱0件)

### 9観点QA
- Fact accuracy・Meaning precision: 良好(FIFA公式データと一致)
- Grammar・Idiomaticity: 問題なし
- News narration naturalness: "England could almost see the World Cup
  final."という導入は、Sourceにない具体的場面描写ではなく、試合展開全体への
  評価的な一文であり、Fact claimと直接結びついていない
- Editorial engagement: 高い(前半の緊張感→55分の先制→85分の同点→90+2分の
  決勝点という時系列を保ちながら展開)
- Master-style transfer: 短い断定文("England 1-0 Argentina.""1-1.""90+2
  minutes. Argentina 2-1 England.")を要所に配置し、阪神masterのリズムに
  近い構成を維持
- Point differentiation: Point One(統計面から見たアルゼンチンの優位)、
  Point Two(メッシの無得点での試合支配)と、明確に異なる切り口
- Downstream B1/A2 suitability: 良好

## C. ADD03

### Fact Ledger概要
- Researcherが12件のFactを収集(Web検索20回)、独立Verificationで**12件全件VERIFIED**
  (AMBIGUOUS・REJECTEDともに0件)
- 7/13(20%通航料発表・Brent終値$83.30)→7/14(撤回発表・Brent終値$84.73)の
  時系列を各Factのdate_or_periodで正確に保持。intraday高値については、
  速報段階の数値と確定値を区別する重点確認指示により、記事側は「初期の
  高い水準まで戻った」という表現にとどめ、初回実行のような特定の
  intraday高値の断定を避けている

### Article
- タイトル: "'Twenty Percent—Then Never Mind': Hormuz Fee Reversal Fails to Calm Oil"
- **word count**: 418語(soft target 346〜468語の範囲内)

### Fact QA
- **`PASS`**(独立fact checker、Web検索13回、矛盾・未確認主張ともに0件)
- $34M/$32Mという通航料試算は、記事自身が「シナリオであり実際の請求では
  ない」と明記しており、fact checkerもこの位置付けを妥当と評価
- IMO理事会の見解について、記事は「これがトランプ氏の方針転換を引き起こした
  という証拠はない」と明示し、因果関係を過剰に強めていない

### Ledger deviation
- `LEDGER_COMPLIANT`(逸脱0件)

### 9観点QA
- Fact accuracy・Meaning precision: 良好
- Grammar・Idiomaticity: 問題なし
- News narration naturalness: 良好、ニュース記事として自然
- Editorial engagement: 「20%という数字が具体的な制度の中身を欠いていた」
  という切り口を軸に展開し、続きを聞きたくなる構成
- Master-style transfer: "Still, the number was large enough to make
  markets imagine the bill." "Then came the reversal." "The market
  briefly exhaled—but did not relax."など、短い断定文を要所に配置
- Point differentiation: Point One(20%という数字の制度的な空洞)、
  Point Two(市場が織り込んでいたのは通航料以上の危険)と、明確に
  異なる切り口。**7/13→7/14のflashback構造は再発していない**(過去の
  ER-003-A2-SCRIPT-FINAL-01で問題になった構成上の課題)
- Downstream B1/A2 suitability: 良好

## D. Cross-topic評価

| Topic | Genre | Fact result | Ledger result | Style result |
|---|---|---|---|---|
| A02(英国SNS規制) | 制度 | PASS(Run-1)/PASS(Run-2)、2/2回 | LEDGER_COMPLIANT、2/2回 | Hook/Rhythm/Editorial engagement/Master-style transfer維持(ER-003-EN-DIRECT-VFL-01) |
| A01(ワールドカップ) | スポーツ | 初回FAIL→再実行PASS | LEDGER_COMPLIANT、2/2回 | 維持(B節) |
| ADD03(Brent原油) | 経済 | 初回FAIL→再実行PASS | LEDGER_COMPLIANT、2/2回 | 維持、flashback構造再発なし(C節) |

3ジャンル(制度・スポーツ・経済)すべてで、**最終的にVFL方式がFact Check PASS・
Ledger deviation 0件で成立**した。ただしA01・ADD03は初回実行でFAILしており、
A02のように1回目から安定してPASSしたわけではない点には留意が必要(E節)。

## E. 比較Artifact

A01・ADD03のVFL記事全文(先頭から読める配置)、word count、fact QA結果、
既存Natural English Source(参考比較用、後段)、9観点QA・Ledger逸脱記録を
まとめた。

**URL**: https://claude.ai/code/artifact/b5ca5389-dbb7-4ae7-9cf9-7c87f6c96fe5

リポジトリ内の原本: `er003_output/en_direct_vfl_02/comparison.html`

## F. Production非変更確認

- **CURRENT_SPEC.md**: 無変更
- **R4 Production prompt**: 無変更。今回のスクリプトも新規の独立ファイル
  (`er003_v1_en_direct_vfl_02_generate.py`)であり、VFL-01・R4・P1Bの関数を
  読み取り専用でimportして使用した(プロンプトのバグ修正もこの新規ファイル内で
  行い、`er003_v1_en_direct_vfl_01_generate.py`自体は変更していない)
- **ER-003-P1B**: 無変更
- **A方式・B方式・VFL方式の正式採用状態**: 変更なし
- **B1/A2 Production生成・TTS/audio**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない。A01/A02/ADD03の音声更新は今回も
  実行していない(夜間まとめ処理のため意図的保留のまま)

## 発見した技術的問題と対応(受入条件15に対応)

**問題**: VFL-01のResearcherプロンプトテンプレートを再利用した際、
記事固有の「特に構造化して含めるべきFact」節がA02専用にハードコードされて
いたことに気づかず、そのままtopicだけを差し替えて使用した。結果、ADD03の
Fact Ledger(初回)に無関係なA02トピックのFactが26件中20件混入した。

**対応**: `er003_v1_en_direct_vfl_02_generate.py`内に、記事非依存の
汎用部分(役割・Source優先順位・出力形式)とA01/ADD03固有の重点確認事項を
明確に分離した新しいプロンプト構築関数を実装し、A01・ADD03とも
「このテーマと無関係な他のトピックのFactは一切収集しない」という明示的な
歯止めも追加した上で再実行した。初回(バグあり)の生成物は削除せず、
`er003_output/en_direct_vfl_02_run1_prompt_bug/`へ移動して証拠として保持している。

## G. 次のDecision

以下から提案する。

1. VFL英語直接方式をProduction候補として仕様化する
2. さらに別Topicで検証する
3. 問題が出た記事のみVFLを調整して再テストする
4. A方式へ戻る

3ジャンルすべてで最終的にFact Check PASS・Ledger deviation 0件という結果は
選択肢1を支持する材料になり得る。一方で、A01・ADD03は(スクリプトのバグとは
別に)初回実行でFact Check FAILを経験しており、A02の2/2回PASSほど安定した
初回成功率ではなかった点は正直に申し添える。Fact Ledgerの精度(特にA01の
試合統計のような、複数のSourceで数値が食い違いうる領域)には、今回追加した
「最も確定的な一次資料を優先する」指示が有効だったが、これが他のトピックでも
一貫して機能するかは、今回の1回の追加実行だけでは十分に立証されていない。
最終判断はユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_en_direct_vfl_02_generate.py`(新規) | A01・ADD03向けVFLパイプライン(記事ごとに独立)。VFL-01・R4のProduction関数を読み取り専用でimport |
| `er003_output/en_direct_vfl_02_run1_prompt_bug/`(新規) | 初回実行(プロンプトバグあり、両記事FAIL)の全成果物。証拠として保持 |
| `er003_output/en_direct_vfl_02/A01/`(新規) | 再実行(修正後)のA01: Fact Ledger・Verification・article.md・fact_qa.json・ledger_deviation.json・diagnostics.json・audit/ |
| `er003_output/en_direct_vfl_02/ADD03/`(新規) | 同上、ADD03 |
| `er003_output/en_direct_vfl_02/run_summary.json`(新規) | 再実行の要約 |
| `er003_output/en_direct_vfl_02/comparison.html`(新規) | 比較Artifact原本 |

## 受入条件24項目

| # | 条件 | 結果 |
|---|---|---|
| 1 | A01とADD03を対象にしている | PASS |
| 2 | 記事ごとに独立したFact Ledgerを作っている | PASS(発見したバグの修正後、確認済み) |
| 3 | Ledgerを独立Verificationしている | PASS |
| 4 | VERIFIED/AMBIGUOUS/REJECTEDを区別している | PASS(両記事とも全件VERIFIED) |
| 5 | Writerは日本語阪神master全文を使用している | PASS |
| 6 | Writerは英語直接生成している | PASS |
| 7 | Writerは原則Web検索しない | PASS |
| 8 | Ledger外Fact追加禁止を維持している | PASS(両記事ともLedger deviation 0件) |
| 9 | A01の人物・得点・得点順・時系列を検証している | PASS(B節) |
| 10 | ADD03の日付・数字scope・因果・時系列を検証している | PASS(C節) |
| 11 | 各記事で独立Fact Checkerを実施している | PASS |
| 12 | 各記事でLedger deviation checkを実施している | PASS |
| 13 | 各記事で9観点QAを行っている | PASS(B・C節) |
| 14 | 初回は各記事1回生成を基本としている | PASS |
| 15 | 追加Runを行った場合は理由を記録している | PASS(前置き節・「発見した技術的問題」節) |
| 16 | best-of目的の複数生成を行っていない | PASS(追加Runは技術的バグ修正+FAILによるもの) |
| 17 | A01・ADD03を読める比較Artifactを作成している | PASS(E節) |
| 18 | Production仕様を変更していない | PASS(F節) |
| 19 | B1/A2/TTS/audioを生成していない | PASS(F節) |
| 20 | OPEN-35を変更・CLOSEしていない | PASS(F節) |
| 21 | モデル・reasoning・Web検索回数を記録している | PASS(B・C節、各jsonファイル) |
| 22 | Ledger全Sourceを記録している | PASS(fact_ledger_draft.json、各factにsource_url) |
| 23 | 変更・新規ファイル一覧を報告している | PASS(上表) |
| 24 | Git操作を行った場合はcommit/push状態を報告している | 本報告の末尾を参照 |
