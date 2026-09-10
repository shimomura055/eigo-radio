# PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01 精査報告書

管理ID: `PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01`(読み取り専用、¥0、編集・Git・API呼び出し一切なし)。
対象: T-2(Fableへの限定Git権限)、T-3(Ledger研究のWeb検索上限)。**いずれも実施しない。精査結果のみ報告。**

---

## エグゼクティブサマリー

- **T-2**: Fable(`sandwich-pm.md`)は現在`Bash`ツールを一切持たない
  (`tools: Agent(...), Read, Grep, Glob`)。git権限付与は「小さな許可追加」
  ではなく**ツール構成自体の変更**であり、実装コストは軽くない。
- 削減額の大半(60〜70%)は本日既に採用済みの「軽量委任形式」(PM_GOVERNANCE
  11節、2026-09-10適用開始)で回収済み。フル権限化で追加に取れる分は
  1件あたり残り8k〜12k程度(実測2件/日ベースで日次16k〜24k程度)に縮小しており、
  推奨は**現状維持(保留)**。
- **T-3**: News Trial-12実測(検索12回・¥148.6)はコスト構造の73%以上が
  input token(検索本文)由来、Discovery Trial-11実測(検索14回×2段階・
  ¥55.48)はコストの約81%がWeb検索tool自体の定額課金($10/1000回)由来と、
  **モデルにより支配的なコスト要因が異なる**ことを実測で確認した。
- Fact見落としリスクの実測: 除外率はDiscovery 1/16(6.25%)、CAR-T 1/15
  (6.7%)といずれも低い。ただしNews Trial-12は独立Verification段階を
  経ない簡易版(source機械確認4/19件のみ)であり、**2段階検証パターン
  (Discovery/CAR-T型)と単純比較すべきではない**。
- 推奨は**現状維持(保留)。ただし段階的read+既存Ledger再利用優先は
  低リスクで即時実施可能**。検索回数上限・reasoning effort変更は
  Fact Safety(QA相当)に該当しうるためSTOP対象(PM_GOVERNANCE 11節
  STOP必須条件2)。

---

## T-2. Fableへの限定Git権限

### 2-1. 削減効果(見込み)

実測(prior report `PM-TOKEN-EFFICIENCY-DIAGNOSIS-01_REPORT.md`より):
純粋なGit記録専用commit(新規ファイル追加のみ、SSOT編集なし)は
`git show --stat`実測で以下の2件が確認済み。

| commit | 内容 | token | 秒 |
|---|---|---|---|
| `7bc125a` | 分析REPORT 3件の新規追加のみ(diff: +1,052行、削除0) | 27,918 | 25 |
| `3056fa7` | ルーティングREPORT 1件の新規追加のみ | 28,571 | 21 |

本日(2026-09-10)のcommit 10件中、上記2件のみが「純粋Git記録専用」型
(残り8件は`PM-CLOSEOUT-CONSOLIDATION-*`等のSSOT編集を伴う統合commit)。
**重要な切り分け**: consolidation型(150k〜235k/件、本日6件)のtoken消費は
大半がSSOT(`OPEN_ITEMS.md`/`DECISION_LOG.md`等)の読込・精密編集コストで
あり、git add/commit/push自体のコストは末尾のわずかな部分にすぎない。
Fableは`sandwich-pm.md`「自分ではしないこと」により今後もSSOT編集は
できない(sonnet-workerへ委任し続ける)ため、**Git権限付与はconsolidation型
の150k〜235kをほぼ削減しない**。効果があるのは「純粋Git記録専用」型
(本日実績2件/日)のみ。

**軽量委任形式との重複に注意**: `PM_GOVERNANCE.md`11節「Token効率運用」
(1)により、2026-09-10付でこの種のcommitは既に「SSOT/ACTIVE_TASK読込
省略」を委任文で明示する軽量形式が常時適用ルールとなっている
(prior report内の見込み: 28k→8k〜12k、60〜70%減)。
つまり:

- 軽量委任形式のみ(現状の恒久ルール): 1件あたり16k〜20k減、
  2件/日で**日次32k〜40k減**(既に適用中、追加のユーザー承認不要)。
- Git権限をFableへ付与した場合の**追加**削減分: 軽量委任後に残る
  8k〜12k/件(Agent起動オーバーヘッド・システムプロンプト等の固定費)を
  さらに0化できる分のみ。2件/日で**追加日次16k〜24k**。
- 週次見込み(参考、精度は低い): 上記日次値に、実際に「純粋Git記録専用」
  型commitが発生する日数を掛けるべきだが、この分類(純粋Git記録型か
  consolidation型か)はログ上体系的に区別されていない。過去7日間の
  総commit数は226件(2026-09-03〜09-10、`git log --since`実測)だが、
  大半は実装Trial内のSonnet単独作業commitであり「Fable専用Git記録委任」
  型ではない。**週次の正確な見込みは現状のログ体系では算出不可**
  (今後採用する場合、委任種別のタグ付けを`MODEL_ROUTING_TRIAL_LOG.md`に
  追加することを推奨)。

結論: **フル権限化の限界削減効果は、軽量委任形式(既に適用中)と比べて
相対的に小さい(残り8k〜12k/件)**。

### 2-2. 作業重複削減効果

- 重複の実体は「Sonnetが`git status`で対象ファイルを再確認する往復」
  だが、軽量委任形式は委任文に対象ファイル名を明示するため、この重複は
  **既に軽量委任形式単体でほぼ解消される**(Fableが権限を持つかどうかに
  依存しない)。
- Fableが直接git操作をする場合に残る重複削減効果は、Agent起動自体の
  固定費(システムプロンプト・Agent定義読込・`docs/pm/PM_BRIEF.md`等の
  周辺読込)の解消のみであり、これは2-1の「追加8k〜12k/件」に含まれる。

### 2-3. リスク

- **設計思想との整合**: `sandwich-pm.md`は「自分ではしないこと」として
  コード・Prompt・SSOT編集を明示的に禁止しているが、Git操作
  (add/commit/push)は現状この列挙に含まれない(`docs/pm/PM_GOVERNANCE.md`
  1節でも「Fableは自分で編集・実装・Git操作をしない」と明記あり)。
  Git権限付与は**この1節の明文規定そのものの変更**であり、単なる運用
  Tips追加ではない。
- **技術的なホワイトリスト強制は現状存在しない**: `.claude/settings.local.json`
  実測(36行)にはgit関連の許可エントリが一切なく、`~/.claude/settings.json`
  は`"defaultMode": "auto"`。つまり現行sonnet-worker(`tools: ...Bash`)の
  git操作は**技術的な強制ではなく、`CLAUDE.md`/`PM_GOVERNANCE`8節
  (ファイル名指定`git add`のみ、`-A`禁止)という文書規約のみで守られている**。
  Fableへ同様にBashツールを素の形で追加した場合、同じ「文書規約のみ」の
  弱いガードになり、`git add -A`事故・音声バイナリ混入・意図しないファイル
  混入のリスクはsonnet-workerと同水準のまま増える(委任者が増えるだけ
  リスク発生箇所が増える)。
- **push先誤り・commit message規約違反**: 現状はsonnet-workerが都度
  `CLAUDE.md`のcommit message規約を読み実行しているが、Fableが直接
  実行する場合も同様の規約遵守が必要で、技術的な逸脱防止機構は
  ない(スクリプト化しない限り)。

### 2-4. 誤操作時の影響

- 復旧手段は既存と同じ(`git revert`、force pushなし)。`CLAUDE.md`
  「履歴の書き換え(amend、rebase、force push)は必ずユーザーに確認する」
  はFableへ権限を与えても変更されない(維持前提)。
- Fableが直接操作する場合、誤commit発見からrevertまでの間に「PM層が
  誤操作した」という点でGatekeeper機能(Fable自身がSonnet成果物を
  照合する11節の原則)と矛盾しうる(誤操作の検査者と実行者が同一に
  なるため、自己点検が効きにくい)。sonnet-worker実行+Fable照合という
  現行の二層構造は、この点で安全側に働いている。

### 2-5. 責任分界

- 変える場合に変更が必要な箇所: `docs/pm/PM_GOVERNANCE.md`1節(「Fableは
  自分で編集・実装・Git操作をしない」の明文)、`.claude/agents/sandwich-pm.md`
  の`tools:`フロントマター(Bash追加、または専用ツール新設)、10節
  (commit/push運用の主体記述)。
- 変えない場合の代替:
  - **固定script経由の限定委任**(例: `scripts/pm_commit_new_reports.py`
    を新規作成し、ファイル名リスト+commit messageのみを引数に取る、
    `-A`不可・push先は`origin/main`固定・対象拡張子ホワイトリストを
    script内部でハードコード)。この場合でも**Fable自身が呼ぶには
    Bash(または専用tool)をFableの`tools:`へ追加する必要があり**、
    「設定を少し変える」だけでは完結しない。scriptを新規作成する実装
    コストも発生する(現状`scripts/`配下にgit/commit関連の既存scriptは
    確認できなかった)。
  - **haiku-workerでは不可な理由**: `haiku-worker.md`実測で確認した
    tools定義は`Read, Grep, Glob`のみで`Bash`を含まず、かつ本文中に
    明文で「Git操作(add/commit/push等)を一切行わない」と禁止されている
    (2026-09-10新設時点の設計思想として、L0[Haiku]は判断を一切含まない
    read-only作業に限定する方針が明記済み)。Git commitは「diffの内容が
    意図通りか」「stage対象が正しいか」を確認する主体的判断を伴うため、
    L0の設計対象外というのが既存SSOTの立場であり、これを覆すにはL0の
    定義自体の変更(11節のMODEL ROUTING Trial設計変更)が必要になる。

### 2-6. 具体案の比較

| 案 | 内容 | 削減見込み(追加分、既に適用中の軽量委任形式との差分) | リスク | 実装コスト |
|---|---|---|---|---|
| **A. 現状維持+軽量委任形式(既に適用中)** | Fableは委任のみ、sonnet-workerが実行。純粋Git記録型は委任文でSSOT読込省略を明示 | 追加削減なし(既に日次32k〜40k減を確保済み) | 低(現行の安全設計を維持、Gatekeeper二層構造を維持) | ¥0(既に運用中) |
| **B. 固定script経由の限定権限** | `scripts/pm_commit_new_reports.py`等をFableが呼ぶ(拡張子・パスのホワイトリスト、`-A`不可、push先は`main`固定) | 1件あたり追加8k〜12k、2件/日で追加日次16k〜24k見込み | 中(技術的ホワイトリストで`-A`事故は防げるが、Fable自身の判断ミス[誤ファイル指定]は防げない。Gatekeeper自己点検の弱化) | 中(script新規作成+`sandwich-pm.md`のtools変更+設定変更、いずれもユーザー承認必要な1節明文の変更を伴う) |
| **C. フル権限(Bashをそのまま付与)** | Fableに素のBashツールを付与 | Bと同程度の追加削減(git以外の用途にも使えてしまう分、削減効果自体はBと同水準) | 高(git以外の任意コマンド実行が可能になり、`sandwich-pm.md`の設計思想[PM層はコード実行をしない]と根本的に矛盾。技術的ホワイトリストなし) | 低(tools追加のみだが、安全設計上**明確に非推奨**) |

### 2-7. 推奨(決定はユーザー)

**推奨: 案A(現状維持)を継続。** 理由: 軽量委任形式で既に削減額の
大半(60〜70%相当、日次32k〜40k)を確保済みであり、追加で得られる分
(案B想定で日次16k〜24k)は、Gatekeeper二層構造の弱化・SSOT編集は
どのみちsonnet-worker委任が必要という構造的制約・週次見込みの算出不能
という不確実性に対して、投資対効果が明確に高いとは言えない。実施する
場合は案B(固定script、ホワイトリスト)を優先し、案C(フル権限)は
設計思想との矛盾が大きく非推奨。

---

## T-3. Ledger研究のWeb検索上限

### 3-1. 現状のToken使用実測

| Trial | モデル | 段階 | web_search回数 | input token | output token(reasoning) | 費用(実測) |
|---|---|---|---|---|---|---|
| News Trial-12(阪神拡充) | gpt-5.6-sol、reasoning=high | Research単発(独立Verificationなし) | 12 | 110,837 | 8,494(reasoning 6,000) | **¥148.6** |
| Discovery Trial-11(タオル) | gpt-5.6-luna | Researcher | 14 | 102,443 | 11,440(reasoning 5,185) | 内訳下記 |
| Discovery Trial-11(タオル) | gpt-5.6-luna | 独立Verification | 14 | 123,447 | 6,528(reasoning 3,965) | 内訳下記 |
| Discovery Trial-11 Ledger合計(Researcher+Verification) | — | — | 28(2段階合計) | 225,890 | 17,968 | **¥55.48** |
| CAR-T Trial-09(候補検索+Ledger作成) | 既存`ER-003-EN-DIRECT-VFL-01`経路踏襲 | 候補検索+Researcher→Verification | 不明(本タスクでは未実測) | 不明 | 不明 | ¥13.73+¥44.16=**¥57.89** |

出典: `er011_output/news_ledger_enrichment_ab_trial_12/raw_usage_log.jsonl`
(実測1行、`web_search_call_count:12, input_tokens:110837, output_tokens:8494,
reasoning_tokens:6000`)、`er011_output/discovery_generalization_towels_trial_11/raw_usage_log.jsonl`
(実測2行、`stage:researcher`/`stage:verification`)、両cost_summary.json、
`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09_REPORT.md`(CAR-T、L40-41)。
Household v5は`OPEN_ITEMS.md`(155行付近)に「Ledger v5、N=3×A2/B1B×2条件=
12本、実測¥127.3」の記載を確認したが、これは記事生成N=12本を含む合算費用で
Ledger調査単体の費用ではなく、本タスクでは単体切り出し未実施(不明）。

**コスト構造の実測分解(公式pricing、`er005_output/cost_baseline_01/pricing_snapshot.json`)**:

| モデル | input単価/1M | output単価/1M | web_search単価 | Newsの内訳($) | Discoveryの内訳($) |
|---|---|---|---|---|---|
| gpt-5.6-sol | $5.00 | $30.00 | $10/1000回 | input $0.554(59.6%)/output $0.255(27.4%)/検索fee $0.12(12.9%)、合計$0.929 | — |
| gpt-5.6-luna | $0.20 | $1.20 | $10/1000回 | — | input $0.045(13.0%)/output $0.022(6.2%)/検索fee $0.28(**80.8%**)、合計$0.347 |

**重要な発見**: 「検索本文がinput tokenの大半」という前提は**input token
自体としては妥当**(公式pricing注記: "search content tokens separately
billed at model input rate")。ただし**総コストに占める支配要因はモデルに
より逆転する**。reasoning強化モデル(sol、reasoning=high)は
token単価が高いためinput+output token(合計87%)が支配的、廉価モデル
(luna)はtoken単価が極めて低いため**Web検索tool自体の定額課金
(1000回あたり$10)が支配的(81%)**。検索回数上限は、lunaのような
廉価モデルではコストに**ほぼ線形かつ確実に効く**(検索feeがcount×$10/1000で
決まるため)一方、solのようなreasoning強化モデルでは検索本文量・reasoning量
にも依存し、単純な線形比例では説明しきれない部分が残る。

### 3-2. 上限設定の削減見込み

- **Discovery(luna)型**: 検索14→8(43%減)なら、検索fee($0.28→$0.16)は
  ほぼ確実に43%減。token側も検索結果本文が短くなれば連動して減る可能性が
  高いが未検証。総コストの81%を占める検索feeが線形に効くため、**見込み
  削減は40%前後(高信頼度)**。
- **News(sol)型**: 検索12→8(33%減)の場合、input tokenが検索回数に比例して
  減ると仮定すれば input $0.554→$0.369、検索fee $0.12→$0.08。
  **reasoning出力(output 8,494token中6,000がreasoning)は検索回数ではなく
  reasoning effort設定に依存する別要因**であり、検索回数を減らしても
  reasoning tokenが同程度減るとは限らない(未検証)。
  - output token不変と仮定(保守的): 総コスト$0.929→$0.704(**24%減**)。
  - output tokenも比例して減ると仮定(楽観的): 総コスト$0.929→$0.619
    (**33%減、検索回数の減少率と同水準**)。
  - **実際の削減率はこの24〜33%の範囲内と見込むのが妥当**(reasoning
    effortを別途medium等へ下げない限り)。
- reasoning effort high→medium引き下げの影響は**本タスクでは未検証**
  (ユーザー指示どおり明記のみ)。

### 3-3. Fact見落としリスク

- **検索順とfact出典の対応**: 両Trialのraw_usage_log・research_raw_result・
  verified_fact_ledger_structuredのいずれにも「何回目の検索クエリが
  どのfactを生んだか」の対応ログは存在しない。**特定不可**(ユーザー
  指示どおり明記)。
- **CONFIRMEDに至らなかった候補の割合(実測)**:
  - Discovery Trial-11: Researcher下書き16件→Verification結果
    VERIFIED(CONFIRMED)15件・AMBIGUOUS 1件・REJECTED 0件。
    **除外率 1/16 = 6.25%**。
  - CAR-T Trial-09: CONFIRMED 14件・AMBIGUOUS 1件(「99.7%の分母定義
    不明」が理由)。**除外率 概算1/15 = 6.7%**。
  - News Trial-12: raw_research出力を実測grepした結果、`[CONFIRMED_FACT]`
    タグが7件のみでAMBIGUOUS/REJECTEDタグは1件も存在せず(独立
    Verification段階自体が実施されていない、単発Research呼び出しの
    まま採用)。Report自身も「**確認方法の限界**」として明記しており、
    `url_citation`で機械確認できたsourceは19件中4件のみ、残り15件は
    モデルの自由記述引用(未再訪問)、全entryのconfidenceを「中」に
    格下げしている(`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12_
    REPORT.md` L96-102実測)。
- **含意**: News Trial-12はDiscovery/CAR-T型の「Researcher→独立
  Verification→CONFIRMEDのみ採用」という2段階パターンを経ておらず、
  **検証の頑健性が異なる簡易版**である。検索回数上限を導入する場合、
  この2つのパターンを同列に扱うべきではない。2段階パターン
  (Discovery/CAR-T)はVerification段階自体が独立re-checkの役割を持つため
  上限設定の余地を相対的に議論しやすいが、News Trial-12型の単発
  Research(独立Verificationなし)は既に検証の安全マージンが薄く、
  ここへさらに検索回数上限を課すのは**追加のFact Safetyリスクを重ねる**
  ことになる。

### 3-4. 再Trial・再確認コスト(参考値)

- News Trial-12条件A(fact 5件のみ)は、N=4時点で最終NG率100%(2/2)、
  N=12まで拡大しても最終NG率83.3%(5/6)で高止まり(`FAMILY-A-NEWS-
  STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12_REPORT.md`実測、L20/L370-371)。
  これは「Ledger調査そのものを削った場合」の直接コストではなく
  「fact供給不足による記事生成retry・NG増加」の参考値だが、fact供給を
  絞りすぎることの下流コスト(retry・NG率上昇)を示す実例として有用。
  条件B(fact12件、通常のWeb検索量)ではNG率33.3%(2/6)まで改善している。
- **含意**: 検索回数上限をむやみに強く絞ると(例: Ledger内usable fact数が
  現状の12件規模から5件規模まで実質的に減る場合)、Ledger調査コストの
  削減(¥148.6の一部)以上に、記事生成retry増加によるコスト増・NG率
  悪化を招く可能性がある。上限は「現状のfact供給量を大きく下回らない
  範囲」に留めるべきという設計制約になる。

### 3-5. 安全に導入できる上限/段階的read方式(検討案、未実施)

- **既存Ledger再利用の優先**(既にPM_GOVERNANCE 11節Token効率運用(4)で
  常時適用ルール化済み、新規承認不要): 同一テーマの再調査費用を¥0化する。
  最も確実でリスクが低い削減策であり、既に適用中。
- **段階的read(タイトル/要約→必要な本文のみ取得)**: 現行の
  `web_search` tool呼び出しは、OpenAI側がtool内部で検索・本文取得を
  行う仕組みであり(`tools=[{"type": "web_search"}]`を1回のresponses.create
  呼び出しに渡す設計)、アプリ側で「まずタイトルだけ取得→選別→本文取得」
  という2段階制御を挟む余地があるかは、既存関数(`er002_ja_web_research_r3.py`
  等)のtool呼び出し設計次第であり、**本タスクの読み取り範囲では実装可否を
  確定できない**(要追加調査)。
- **テーマ別上限・検証段階は削らない**: 3-3の分析から、Verification段階
  (独立re-check)の検索は安全性の根幹であり削減対象から除外すべき。
  上限を検討する場合はResearcher(下書き収集)段階に限定するのが相対的に
  安全側。
- **QA/Validator変更への該当判定**: Ledger作成(Researcher/Verification)
  はFact Safety(事実精度)の直接的な担保プロセスであり、
  `PM_GOVERNANCE.md`11節STOP必須条件2「QA・Validator・閾値の変更」に
  **該当しうる**(prior報告と同じ判定を本調査でも維持)。検索回数上限・
  reasoning effort変更のいずれも、Fact Safetyの検証網羅性に影響しうる
  パラメータであるため、**ユーザー判断必須**。

### 3-6. 推奨(決定はユーザー)

**推奨: 現状維持(保留)。** 理由: (1) 既存Ledger再利用の標準化
(¥0化)で新規調査コスト自体が既に発生頻度ベースで大きく減っている
(11節Token効率運用(4)、承認済み・適用中)。(2) News Trial-12型
(簡易・未検証Verification)とDiscovery/CAR-T型(2段階検証)の安全性が
異なるため、一律の検索回数上限を今設定すると、より脆弱なパターン
(News型)へ余計なリスクを重ねる可能性がある。(3) 削減見込み自体は
Discovery(luna)型で40%前後・News(sol)型で24〜33%と有意ではあるが、
Fact Safety直結のQA相当パラメータでありSTOP必須条件に該当する。導入する
場合は、まずVerification段階を含む2段階パターンへの統一(News Trial-12型
の簡易版を標準としない)を先行させ、そのうえでResearcher段階に限定した
小幅な上限(例: 14→10程度)をN数を増やしたTrialで検証してから判断する
方式を推奨する。

---

## QCD

- **Quality**: 全数値はraw_usage_log.jsonl・cost_summary.json・
  run_metadata.json・既存REPORT・pricing_snapshot.jsonの実測値に基づく
  (grepで生ログを直接確認)。推定箇所は本文中に「見込み」「未検証」
  「特定不可」を明記。CONFIRMED/AMBIGUOUS内訳・News Trial-12の検証限界は
  実測(raw_research grep+既存Report記載)で確認済み。
- **Cost**: 本タスクは読み取り専用・¥0(API呼び出し・Git操作・編集なし)。
- **Delivery**: T-2/T-3両方の調査・比較表・推奨(決定はユーザー)を
  1回のSonnet委任内で完了。追加調査が必要な項目(週次git頻度の正確な
  分類ログ、段階的read方式の実装可否、Household v5単体費用)は本文中に
  明記済み。
