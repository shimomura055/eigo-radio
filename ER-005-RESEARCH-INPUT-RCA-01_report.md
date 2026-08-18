# ER-005-RESEARCH-INPUT-RCA-01 完了報告

**Baseline Research入力経路の復元**
実施日: 2026-08-18
新規API呼び出し・Research再実行・CURRENT_SPEC変更は行っていません。既存artifact(committed JSON/script/report)のみを調査しました。

証拠区分の凡例:
- `CONFIRMED_FROM_ARTIFACT`: git commit済みのファイル(script/JSON log/report)から直接確認
- `CONFIRMED_FROM_SESSION_TRANSCRIPT`: 同一セッション内で実際に実行した処理(WebSearch tool呼び出し等)で、ファイルとしては保存されていないが会話履歴として確認できるもの
- `INFERRED`: 直接証拠はないが、artifact/transcriptの整合性から妥当と判断
- `NOT_RECORDED`: どの記録にも残っておらず、確認不能

---

## 共通の発見(両テーマに共通する構造的事実)

**最重要の発見**: Sol Researcherが実際にWeb Researchを開始する直前に受け取っていたのは、単なる「AKB48」「子育てに関する最新の研究」というキーワードではなく、**既に具体的な結論(記事の核心的Fact)を含んだ、高度に事前調査済みのBrief**でした。真の「keywordだけからの0ベースResearch」ではなく、「既に人間相当の下調べが済んだ状態からの検証・拡張作業」だったことが、両テーマで確認できました。これは元のCost Baseline / Model比較の数値解釈に影響する構造的事実です。

---

## Parenting

### 1. 最初のユーザー相当入力は何だったか

`CONFIRMED_FROM_SESSION_TRANSCRIPT`(このセッションの会話履歴内、ER-005-COST-BASELINE-01タスク仕様の原文)

> COST-ARTICLE-02：子育てに関する最新の研究
> ユーザー指定：「子育てに関する最新の研究」
> キーワードだけを入力として...

原文はファイルとして保存されておらず、セッションの会話ログにのみ存在します。

### 2. Topic Selectionを誰/何が行ったか

`CONFIRMED_FROM_SESSION_TRANSCRIPT`。**Sol(Production Researcher)ではなく、私(Claude Code/本アシスタント)が行いました。** eigo-radioのProduction API(OpenAI/Gemini/Azure)は一切使わず、Anthropic側のWebSearchツール(本プロジェクトのコスト計測対象外)で実施しました。

### 3. Topic Selection時にどのWebSearchを使ったか

`CONFIRMED_FROM_SESSION_TRANSCRIPT`。実行した検索クエリ(順不同、確認できた範囲):

- `child development parenting study 2026 university research findings`
- `Dunedin Study social mobility parenting quality sensitive parenting cognitive stimulation 2026`

これらはAnthropicのWebSearchツールによるもので、eigo-radioのraw_usage_log.jsonlには一切記録されていません(記録対象外のtoolのため)。

### 4. Researcherへ渡された実際のResearch Brief / prompt全文

`CONFIRMED_FROM_ARTIFACT`(`er005_output/cost_baseline_01/parenting/research/ledger_draft_raw.json`の`prompt`フィールド、原文のまま)

```
今回のテーマについて、Webで調査し、Verified Fact Ledgerの下書きを作成してください。

【今回のテーマ】
2026年3-4月号のChild Development誌(Vol.97 Issue 2、DOI 10.1093/chidev/aacaf050)に掲載された、ニュージーランドDunedin Studyのコホート追跡研究(Islam, Jaffee, Belsky, Hancox, Poulton, Ramrakha, Wertz)。出生から追跡された参加者のうち719人が親になった時点(平均32.7歳)で、3歳の3歳の子どもに対する養育行動(sensitivity・cognitive stimulation)を測定し、親自身の社会階層の世代間変化(上昇移動/安定低位/安定高位)との関連を検証した。上昇移動した親は、安定して低いSESの親より養育の質が高かったが、一貫して高いSESの親より低かった。

【役割】
あなたはResearcherです。以下を行いません:
- 記事本文を書く
- Narrativeを作る
- 比喩を考える
- 阪神マスターのstyleを模倣する
あなたが行うのは、Factだけを収集・整理することです。

【Source優先順位】
1. 政府・規制当局等の一次資料
2. 公式調査・報告書
3. 信頼できる二次資料
一次Sourceで確認できるFactを、二次Sourceだけで確定しないでください。

【特に注意して構造化すべき観点(今回のテーマに当てはまる場合のみ)】

1. 対象範囲: 年齢・人数・期間・地域等、Factが適用される範囲(scope)を数値の母集団と混同せずに特定する
2. 制度・仕様の適用条件: default設定なのか常時適用なのか、変更・例外が認められるか等、時間的・条件的scopeを明確にする。一次資料内で表現が揺れている場合は、より明確な一次Sourceを追加で検索する。それでも確定できない場合は、断定せずambiguityフィールドへその旨を明記する
3. 数値の内訳: ある数字が全体を指すのか、特定のサブグループ・条件を指すのかを明確にする。一次資料で直接確認できる場合のみnumeric_valueとして確定し、確認できない場合は推測で数字を作らず、numeric_valueをnullにしてambiguityへその旨を記録する
4. 観察・相関・因果の区別: 変化・効果・傾向等について、観察・報告なのか、相関なのか、Source自身が因果関係を主張しているのかを、causal_strengthで区別する。Sourceより強い因果表現(caused/produced/proved等)を後工程のwriterが使わないよう、causal_strengthとnotes_for_writerで明示する

【出力形式】
各Factについて、fact_id・claim・subject・date_or_period・scope・conditions・numeric_value・
numeric_scope・causal_strength・source_title・source_url・source_type・support_level・
ambiguity・notes_for_writerを埋めてください(該当しない項目はnullで構いません)。
数字・期間・対象範囲があるFactについては、該当項目を必ず明示してください。
```

**注記(`CONFIRMED_FROM_ARTIFACT`)**: 【今回のテーマ】の文中に「3歳の3歳の子どもに対する」という重複表記が実際に含まれたまま送信されています(編集時の誤字がそのまま本番投入されていた)。Ledgerの品質自体には支障が出ていませんが、事実として記録します。

developer roleへ渡された指示文(`RESEARCHER_DEVELOPER_MESSAGE`、`CONFIRMED_FROM_ARTIFACT`、`er003_v1_en_direct_vfl_01_generate.py`):

> あなたはFact Researcherです。記事本文・Narrative・比喩は一切書かず、構造化されたFactだけを収集・整理してください。

### 5. そのBriefを誰/どのモデルが生成したか

`CONFIRMED_FROM_SESSION_TRANSCRIPT` + `CONFIRMED_FROM_ARTIFACT`(`er005_stage1_research_generate.py`の`TOPICS["parenting"]`)。**私(Claude Code)が、上記WebSearch結果を手動で要約・執筆しました。** Sol・Luna等のProduction Writerモデルは一切関与していません。

### 6. Briefには研究前には本来未知であるFactがどこまで入っていたか

`CONFIRMED_FROM_ARTIFACT`(Brief本文とLedger成果物の比較)。**Briefの時点で、記事の核心的結論がほぼ全て含まれていました**:
- 論文誌名・巻号・DOI
- 著者名(Islam, Jaffee, Belsky, Hancox, Poulton, Ramrakha, Wertz)
- 参加者数719人・平均年齢32.7歳
- 中心的知見そのもの(「上昇移動した親は安定低位より高いが安定高位より低い」)

Researcher(Sol)が実際に新規発見した主な付加価値は、**統計的詳細**(サンプル内訳の人数・パーセンテージ、測定手法の細部、observational designの限界表現等)であり、記事の骨格となる「何が起きた/分かったか」という核心Factは、Research開始前から既に確定していました。

### 7. Sol Researcher自身がtopic選定・editorial判断を行った部分はどこか

`INFERRED`(Ledger内容とBriefの差分から)。Topic(どの論文を扱うか)そのものの選定は行っていません。Sol自身が行った判断は、(a) Brief記載の中心的知見を裏付ける一次資料(academic.oup.com等)への到達方法の選択、(b) Brief未記載だった統計的細部(具体的なp値・効果量等、実際にはLuna比較実験の方が顕著)をどこまで深掘りするかの範囲判断、(c) 因果強度(causal_strength)の分類判断、に限られます。

### 8. SolがWeb Researchを開始する直前に保持していた情報(原文)

`CONFIRMED_FROM_ARTIFACT`。4節に示したprompt全文がそのまま該当します。加えてAPI呼び出しパラメータ(`er005_stage1_research_generate.py`および`er003_v1_en_direct_vfl_01_generate.py`から確認):
- model: `gpt-5.6-sol`
- reasoning effort: `high`
- tools: `web_search`(ツール定義のみ、この時点で検索結果は未取得)
- 出力形式: JSON Schema(`FACT_LEDGER_JSON_SCHEMA`)で構造化Factの配列を強制

---

## AKB48

### 1. 最初のユーザー相当入力は何だったか

`CONFIRMED_FROM_SESSION_TRANSCRIPT`(ER-005-COST-BASELINE-01タスク仕様の原文)

> COST-ARTICLE-01：AKB48
> ユーザー指定：「AKB48」
> キーワードだけを入力として、現在ニュース価値・面白さがある具体的なトピックをResearch段階で選定する。

### 2. Topic Selectionを誰/何が行ったか

`CONFIRMED_FROM_SESSION_TRANSCRIPT`。Parentingと同様、**私(Claude Code)がAnthropic側のWebSearchツールで行いました**。Sol/Production APIは不使用です。

### 3. Topic Selection時にどのWebSearchを使ったか

`CONFIRMED_FROM_SESSION_TRANSCRIPT`。実行した検索クエリ(確認できた範囲):

- `AKB48 2026年8月 ニュース`
- `AKB48 好きish 伊藤百花 近藤沙樹 14歳 初選抜`

### 4. Researcherへ渡された実際のResearch Brief / prompt全文

`CONFIRMED_FROM_ARTIFACT`(`er005_output/cost_baseline_01/akb48/research/ledger_draft_raw.json`の`prompt`フィールド、原文のまま)

```
今回のテーマについて、Webで調査し、Verified Fact Ledgerの下書きを作成してください。

【今回のテーマ】
AKB48の68thシングル『好きish』(2026年8月19日発売)。センターを務める伊藤百花は前作『名残り桜』に続く2作連続センターで、同一メンバーの2作連続単独センターは2014年の渡辺麻友以来12年ぶり。同シングルでは20期研究生・近藤沙樹(14歳)がAKB48史上最年少で初選抜入りした。

【役割】
あなたはResearcherです。以下を行いません:
- 記事本文を書く
- Narrativeを作る
- 比喩を考える
- 阪神マスターのstyleを模倣する
あなたが行うのは、Factだけを収集・整理することです。

【Source優先順位】
1. 政府・規制当局等の一次資料
2. 公式調査・報告書
3. 信頼できる二次資料
一次Sourceで確認できるFactを、二次Sourceだけで確定しないでください。

【特に注意して構造化すべき観点(今回のテーマに当てはまる場合のみ)】

1. 対象範囲: 年齢・人数・期間・地域等、Factが適用される範囲(scope)を数値の母集団と混同せずに特定する
2. 制度・仕様の適用条件: default設定なのか常時適用なのか、変更・例外が認められるか等、時間的・条件的scopeを明確にする。一次資料内で表現が揺れている場合は、より明確な一次Sourceを追加で検索する。それでも確定できない場合は、断定せずambiguityフィールドへその旨を明記する
3. 数値の内訳: ある数字が全体を指すのか、特定のサブグループ・条件を指すのかを明確にする。一次資料で直接確認できる場合のみnumeric_valueとして確定し、確認できない場合は推測で数字を作らず、numeric_valueをnullにしてambiguityへその旨を記録する
4. 観察・相関・因果の区別: 変化・効果・傾向等について、観察・報告なのか、相関なのか、Source自身が因果関係を主張しているのかを、causal_strengthで区別する。Sourceより強い因果表現(caused/produced/proved等)を後工程のwriterが使わないよう、causal_strengthとnotes_for_writerで明示する

【出力形式】
各Factについて、fact_id・claim・subject・date_or_period・scope・conditions・numeric_value・
numeric_scope・causal_strength・source_title・source_url・source_type・support_level・
ambiguity・notes_for_writerを埋めてください(該当しない項目はnullで構いません)。
数字・期間・対象範囲があるFactについては、該当項目を必ず明示してください。
```

developer role指示文はParentingと同一(共通テンプレートのため)。

### 5. そのBriefを誰/どのモデルが生成したか

`CONFIRMED_FROM_SESSION_TRANSCRIPT` + `CONFIRMED_FROM_ARTIFACT`(`er005_stage1_research_generate.py`の`TOPICS["akb48"]`)。**私(Claude Code)が手動執筆しました。**

### 6. Briefには研究前には本来未知であるFactがどこまで入っていたか

`CONFIRMED_FROM_ARTIFACT`。Parenting以上に顕著で、**Briefの時点で記事の中心的主張(伊藤百花の2作連続センター、「12年ぶり」記録、近藤沙樹の年齢・初選抜)がほぼ全て確定済み**でした。Researcherが実際に新規追加した情報は、選抜メンバー16人の氏名一覧、パッケージ形態、著者(AKB48公式)発表の正確な日付程度に限られます。

**重要な例外(Sol独自の価値、`CONFIRMED_FROM_ARTIFACT`)**: Briefには「AKB48**史上**最年少で初選抜入りした」と明記されていましたが、Sol Researcherは独立検索により、これが不正確であること(現役メンバー内での最年少であり、歴代では松井珠理奈11歳228日・奥真奈美11歳237日という先例があること)を**自ら発見し訂正しました**(最終Ledger FACT-06)。これはBrief記載内容をそのまま鵜呑みにせず、Researcher自身が独立検証の役割を果たした具体的な証拠です。

### 7. Sol Researcher自身がtopic選定・editorial判断を行った部分はどこか

`INFERRED`。Topic選定はゼロ(完全に事前決定済み)。Editorial判断としては、(a) 上記6節の「史上最年少」表現の訂正、(b) どの補助情報(パッケージ形態等)を含めるかの取捨選択、に限られます。

### 8. SolがWeb Researchを開始する直前に保持していた情報(原文)

`CONFIRMED_FROM_ARTIFACT`。4節のprompt全文がそのまま該当。APIパラメータはParentingと同一(model=gpt-5.6-sol、reasoning effort=high、tools=web_search、構造化JSON出力)。

---

## 実際の入力経路には「やり直し」があった(両テーマ共通の補足)

`CONFIRMED_FROM_ARTIFACT`(discardedファイルの存在)。現在committedされている「最終・クリーンな」Brief/Ledgerに至るまでに、実際には複数回の実行がありました:

| テーマ | 試行 | 内容 | 証拠 |
|---|---|---|---|
| AKB48 | 1回目 | Topic引数が正しく渡らないコード側の不具合により、**AKB48と無関係な旧テーマ(英国のSNS規制)がそのまま実行された** | `NOT_RECORDED`(このRaw JSON自体は後続の実行で上書きされ、ファイルとして残っていません。当時のログ確認による記録のみ) |
| AKB48 | 2回目 | Topic引数は修正されたが、Researcher prompt template自体に旧テーマ固有の「特に構造化すべきFact」節がハードコードされたまま残っており、AKB48(6件)と旧テーマ(18件)の**Factが混在**した | `CONFIRMED_FROM_ARTIFACT`(`ledger_draft_raw_CONTAMINATED_discarded.json`、fact_id `AKB48-001`〜`006`+`UK-NIGHT-SNS-*`等18件、計24件) |
| AKB48 | 3回目(採用) | Prompt templateのハードコード部分を除去した後の実行。AKB48関連15 Factのみ、クリーン | `CONFIRMED_FROM_ARTIFACT`(現行`ledger_draft_raw.json`) |
| Parenting | 1回目 | Topic引数は正しく渡ったが、Prompt templateのハードコードが未修正のため、Parenting(16件)と旧テーマ(19件)の**Factが混在** | `CONFIRMED_FROM_ARTIFACT`(`ledger_draft_raw_CONTAMINATED_discarded.json`、fact_id `CD-001`〜`016`+`UKP-*`/`PILOT-*`計19件、計35件) |
| Parenting | 2回目(採用) | Template修正後の実行。クリーン | `CONFIRMED_FROM_ARTIFACT`(現行`ledger_draft_raw.json`) |

最終的に採用されたBrief/Ledgerは上記の「3回目」「2回目」であり、本報告の4節・6節・7節・8節はこの採用版に基づいています。

---

## 総括

| 項目 | Parenting | AKB48 |
|---|---|---|
| 最初の入力 | キーワード「子育てに関する最新の研究」(`CONFIRMED_FROM_SESSION_TRANSCRIPT`) | キーワード「AKB48」(同上) |
| Topic Selection実施者 | 私(Claude Code)、Anthropic WebSearch使用 | 同左 |
| Sol/Production APIのTopic Selection関与 | なし | なし |
| Briefの事前確定度 | 高い(核心的知見は確定済み) | 非常に高い(核心的主張はほぼ確定済み) |
| Sol Researcherの実質的な価値 | 統計的細部の発見・検証 | 補助情報の追加、および1件の重要な訂正(史上最年少ではないことの発見) |
| 実行のやり直し回数 | 2回(1回破棄) | 3回(2回破棄、うち1回は証拠未保存) |

**この構造は、ER-005-COST-BASELINE-01およびER-005-MODEL-AB-01Aで測定された「Research Cost」が、真の意味での0ベース調査コストではなく、「既に具体的結論を含むBriefの検証・補強コスト」であったことを意味します。** 将来Customized Daily Deliveryで真にキーワードのみからTopic選定を自動化する場合、今回測定していない「Topic Selection自体のコスト」(現在は私自身の作業として費用$0扱い)が新たに発生する可能性が高く、これは既存のOPEN_ITEMS/DECISION_LOGの該当箇所(TOPIC_SELECTION_AUTOMATION = OUT_OF_SCOPE_FOR_MODEL_AB_01A、ER-005-LLM-COST-STRUCTURE-AUDIT-01-R1の枠組み)と整合します。

Production側コード・CURRENT_SPEC.mdは変更していません。新規API呼び出しも行っていません。
