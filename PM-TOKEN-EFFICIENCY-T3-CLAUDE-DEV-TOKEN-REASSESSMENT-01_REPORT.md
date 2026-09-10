# PM-TOKEN-EFFICIENCY-T3-CLAUDE-DEV-TOKEN-REASSESSMENT-01 精査報告書

管理ID: `PM-TOKEN-EFFICIENCY-T3-CLAUDE-DEV-TOKEN-REASSESSMENT-01`(読み取り専用、¥0、編集・Git・API呼び出し一切なし)。
対象: **開発Line(Fable/sonnet-worker/opus-consultant/haiku-worker)が消費する
Claude Token / weekly limit**(Production/API費用ではない)。前身の
`PM-TOKEN-EFFICIENCY-T2-T3-ASSESSMENT-01_REPORT.md`は論点がProduction API
費用寄りにずれていたとユーザーが判定(2026-09-11)したことを受けた再評価。

---

## 要点(5行)

1. **T-1(OPEN_ITEMS.md分割)は「全文を毎回読む」運用には効くが「本文+履歴を両方読む」運用には効かない**: 全文読込は694,768字(before)→315,706字(after、本体のみ)で約54%減。ただし新設`OPEN_ITEMS_HISTORY.md`(389,564字)まで両方読むと合計705,270字で**restructure前とほぼ同水準(むしろ微増)**。効果はGrep等で特定OPEN-XXX行だけを狙い読みする運用に最も強く出る(後述)。
2. **単一行Grep読込の最悪ケースは実測で85〜90%減**: OPEN-120/121/135行の最大行長が57,003〜65,580字(before)→6,753〜9,542字(after)に縮小(実測)。ただし「固定ヘッダのみ」読込は元々988字前後で軽量なため、この観点での削減効果はほぼゼロ。
3. **repo内最大のToken源はOPEN_ITEMS.mdではなくDECISION_LOG.md**(1,334,377字、現行OPEN_ITEMS.md本体の約4.2倍、restructure前OPEN_ITEMS.mdの約1.9倍)。T-1はDECISION_LOG.mdを一切対象にしておらず、**未着手の最大リスクとして残存**している(実測)。
4. **Opus L2レビュー1件の入力規模は実測で約45万字(≈20.5万token)**: 直近の3V Phase1 Opus L2レビューはコード8ファイル(379,435字)+Sonnet REPORT本文(72,789字)を参照(ファイルパス・行番号引用から実測確認)。これがOpus起用1件あたりの支配的なToken要因であり、Opus出力自体(REPORT約2万字)よりはるかに大きい。
5. **直近7日間(2026-09-04〜09-11)で222 commit・153件のREPORT新規/更新(現存合計約288万字)**。カテゴリ別ではTRIAL系(61件・123万字)が件数・合計字数とも最大、次いでPRODUCTION-WIRING系(19件・35.6万字)。OPUS-L2系は件数(3件)・出力(6.1万字)は少ないが1件あたりの入力側負荷(上記4)が突出して重い。

---

## 1. T-1効果実測

### 1-1. アクセスパターン別token概算(文字数/2.2)

| アクセスパターン | before(commit `6a39015`) | after(現行) | 差分 |
|---|---|---|---|
| (a) OPEN_ITEMS.md全文読込 | 694,768字 ≈ **315,804 token** | 315,706字 ≈ **143,503 token**(本体のみ) | **-54.6%** |
| (a') 本体+`OPEN_ITEMS_HISTORY.md`両方全文読込 | (該当ファイルなし) | 705,270字 ≈ **320,577 token** | **beforeよりわずかに増**(+1.5%) |
| (b) Grep 1行取得: OPEN-120最大行 | 65,580字 ≈ **29,809 token** | 6,753字 ≈ **3,069 token** | **-89.7%** |
| (b) Grep 1行取得: OPEN-135最大行 | 57,003字 ≈ **25,910 token** | 9,542字 ≈ **4,337 token** | **-83.3%** |
| (b) Grep 1行取得: OPEN-121最大行 | 65,580字 ≈ **29,809 token** | 6,753字 ≈ **3,069 token** | **-89.7%** |
| (c) 固定ヘッダのみ(冒頭10行) | 657字 ≈ **299 token** | 988字 ≈ **449 token** | ほぼ変化なし(むしろ微増、注記文追加のため) |

実測出典: `git show 6a39015:OPEN_ITEMS.md`と現行`OPEN_ITEMS.md`/`OPEN_ITEMS_HISTORY.md`を`wc -c`・`grep -n`で直接比較(本タスクで実測、Git操作は読取専用の`git show`のみ)。

**解釈**: T-1の効果は「全文を漫然と読む」よりも「Editツールで特定OPEN-XXX行を書き換える」運用のほうに強く効いている。これは1-2で実証する(commit diff実測)。逆に「本体だけでは文脈が足りず履歴ファイルも読みにいく」運用が定着すると、削減効果は消える(むしろ2ファイル分のオーバーヘッドがわずかに乗る)。**現時点でSonnet/Fableが実際に`OPEN_ITEMS_HISTORY.md`をどの頻度で読みにいっているかは、本タスクの範囲(REPORT記述からの推定)では特定できなかった**(新設ファイルのため参照実績が浅い)。

### 1-2. Edit/diffコストへの効果(新規実測、より強いシグナル)

SSOT編集を伴うConsolidation型commitのOPEN_ITEMS.md diffサイズを比較(`git show <commit> -- OPEN_ITEMS.md | wc -c`実測):

| commit | 時期 | 内容 | OPEN_ITEMS.md diff文字数 |
|---|---|---|---|
| `6a39015`(before restructure) | 2026-09-10 | News Trial-12+OPEN-140是正 | **333,875字** |
| `8eccf5e`(before restructure) | 2026-09-10 | ユーザー回答10項目反映 | **143,276字** |
| `b358b85`(after restructure) | 2026-09-11 | 3V Phase1b+Opus L2レビュー2件+TTS retry+T2-T3評価 | **68,767字** |

**解釈**: Editツールは`old_string`の完全一致が必要なため、restructure前は「3,000字超の1行」を丸ごと`old_string`/`new_string`として往復させる必要があり、diffが膨張していた。restructure後は該当行が数千字規模に収まるため、同種のConsolidation編集でもdiffが大幅に小さい(`b358b85`は複数の並列成果を統合した回でもむしろ`6a39015`の約1/5)。これはT-1の効果の中で**最も再現性が高く、測定しやすいシグナル**である。

### 1-3. 直近タスク3件での代表ケース(REPORT/DECISION_LOG記述からの推定)

1. **Consolidation型(直接編集)**: `PM-CLOSEOUT-CONSOLIDATION-71`(commit `6a39015`、restructure前)はOPEN-135行を含む複数行を書き換えており、上記1-2の333,875字diffが示すとおり、旧形式の巨大単一行の全体を毎回読み書きしていたと推定される。同種の`PM-CLOSEOUT-CONSOLIDATION-72`(commit `b358b85`、restructure後)は68,767字と大幅に軽量化(実測)。
2. **Trial型(SSOT非接触)**: `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12_REPORT.md`・`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11_REPORT.md`はいずれも本文中で`OPEN_ITEMS.md`を「編集禁止対象」として言及するのみで、Trial実行自体はOPEN_ITEMS.mdを読み書きしない(実測、grep該当箇所は境界宣言のみ)。この型はT-1の影響を受けない。
3. **Opus L2レビュー型**: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01-OPUS-L2-REVIEW-01_REPORT.md`はOPEN_ITEMS.mdに一切言及がない(grep該当なし、実測)。Opusへの委任はコード・Sonnet REPORTのみを入力としており、OPEN_ITEMS.mdはスコープ外(詳細は2-4節)。

---

## 2. 重複読込の実態調査(5観点、推定を含む)

### 2-1. Ledger/Research結果の重複読込

- **実例**: `verified_fact_ledger.txt`/`verified_fact_ledger_structured.json`はrepo全体で**43ファイル実測**(`find`実測)。サイズは15,354字〜50,600字/件(実測、`du -b`)。
- **重要な切り分け**: これらのファイルは主に`er0XX_*.py`スクリプトが`open().read()`でGPT系API呼び出しのprompt本文へ読み込む(実測、`grep "verified_fact_ledger" *.py`で20件超のスクリプトを確認)。**これはProduction/Trial API(GPT)のtoken消費であり、Claude開発Token消費ではない**。前身REPORT(T2/T3)がここを混同していた可能性がある論点であり、本タスクでは明確に区別する。
- **Claude開発Token側の実態**: REPORTファイル33件が`verified_fact_ledger`という語を含むが、実測確認した`OPEN-140-THEME2-LEDGER-ID-CONSISTENCY-FIX-01_REPORT.md`はファイルパス引用のみで、Ledger本文を丸ごと引用してはいない(実測、grep -C2で確認)。**Sonnetが調査のためにReadツールでLedger全文(15K〜50K字)を1回読む行為自体は各タスクで発生していると推定されるが、複数タスク間で同一Ledgerを繰り返し読んだ具体的な回数は、本タスクの読み取り範囲(REPORT記述)では特定できない**(測れないことを明記)。
- **頻度(推定)**: Ledger関連の修正・検証タスク(OPEN-140、HOUSEHOLD-LEDGER-*、FAMILY-A-*-LEDGER-*等)はREPORT件数ベースで直近では10件前後/月規模。

### 2-2. Fable/Sonnet/Opus間の同一context再読

- **委任文へのSSOT本文転記**: `sandwich-pm.md`は`tools: Agent(...), Read, Grep, Glob`のみでBashを持たず、Fableが委任文を書く際にSSOT本文を転記しているかどうかは本タスクでは直接確認できない(委任文自体はログに残らない設計)。**測れない**。
- **各Agentが同じREPORTを全文読む箇所**: 実測で確認できたのは、Opus L2レビュー(3V Phase1)が「Sonnet REPORT本文(72,789字)+コード8ファイル(379,435字)」を読んだ痕跡(ファイルパス・行番号引用、実測)。これはSonnetが実装時に既に読んでいたコードとほぼ同一集合であり、**Sonnet→Opusの引き継ぎ時に同一コードが2回(Sonnet実装時+Opusレビュー時)Claude開発Tokenとして計上される構造**が実測で確認できる。
- **頻度**: 直近7日でOpus L2レビューは3件実測(3V Phase1/Phase1b/Discovery Trial-11)。1件あたり平均入力規模は上記3V Phase1の例(約45万字≈20.5万token)を参考値とすると、3件で概算60万字級(推定、他2件は個別未計測)。

### 2-3. 巨大Ledger全文読込(SSOTサイズ上位、実測)

repo直下(`.git`除く)のテキスト系ファイルサイズ上位(実測、`du -b`+`sort -rn`):

| ファイル | サイズ(実測) | token概算 |
|---|---|---|
| `DECISION_LOG.md` | 1,334,377字 | **606,535 token** |
| `OPEN_ITEMS_HISTORY.md` | 389,564字 | 177,075 token |
| `CURRENT_SPEC.md` | 375,040字 | 170,473 token |
| `OPEN_ITEMS.md`(現行) | 315,706字 | 143,503 token |
| `EDITORIAL-B-FAMILY-VOICES-TRIAL-04_REPORT.md` | 99,123字 | 45,056 token |
| `docs/pm/PM_GOVERNANCE.md` | 100,059字 | 45,481 token |

**重要な発見**: `DECISION_LOG.md`は**repo内最大の単一ファイル**であり、restructure前のOPEN_ITEMS.md(694,768字)よりもさらに大きい(約1.9倍)。CLAUDE.mdのcompact復帰手順(7)は「`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`の全文読込は禁止」と既に明記しており、**全文読込自体は既存ルールで抑止されている**。ただし本タスクで実測した限り、DECISION_LOG.mdには「3,000字超の巨大単一行」問題やGrep最悪ケースの縮小余地(T-1相当の構造分割)が未実施であり、**Grepで特定エントリを引く際の最悪ケース行長を実測すべき対象として残っている**(本タスクでは実測未実施、追加調査が必要)。

### 2-4. Opusへ渡すcontext過多(実測、3件中1件を詳細確認)

- **3V Phase1 Opus L2レビュー**(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01-OPUS-L2-REVIEW-01_REPORT.md`): 出力REPORTは20,424字(小さい)だが、本文中のファイルパス・行番号引用から、以下8ファイルを読んだことが実測確認できる。
  - `er012_b_family_editorial_type_registry_01.py`(33,399字)
  - `er012_b_family_production_runner_01.py`(89,633字)
  - `er012_b_family_voices_a2_production_01.py`(48,488字)
  - `er012_b_family_voices_production_01.py`(55,685字)
  - `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`(50,241字)
  - `er011_human_review_lock_01.py`(33,954字)
  - `er011_open129_structural_completeness_production_wiring_evidence_01.py`(13,013字)
  - `er012_editorial_b_voices_3v_audio_trial_01.py`(55,022字)
  - 合計: **379,435字**
  - さらに元のSonnet REPORT `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01_REPORT.md`(72,789字)も読んでいる(前提として引用)。
  - **合計入力規模: 452,224字 ≈ 205,556 token**(Opus自身の出力20,424字は含まず)。
- `opus-consultant.md`には入力ファイル数・規模を制限する記述が一切ない(実測、全文確認)。「診断結果は簡潔にまとめて返す」という**出力側**の節約指示はあるが、**入力側の絞り込み指示はゼロ**。
- **含意**: Opus 1件あたりの支配的コストは出力ではなく入力(コード全文読込)であり、委任範囲を論点関連の差分・抜粋に絞れるかどうかが最大のレバー。

### 2-5. 長いResearch結果の必要以上の引き継ぎ(実例、文字数付き)

News Ledger拡充A/B Trial-12を例にした実測チェーン:

| 段階 | ファイル | 文字数(実測) | token概算 |
|---|---|---|---|
| 1次(Trial REPORT) | `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12_REPORT.md` | 32,801字 | 14,910 token |
| 2次(DECISION_LOG該当エントリ、`PM-CLOSEOUT-CONSOLIDATION-71`) | `DECISION_LOG.md` L10907-11041 | 10,140字 | 4,609 token |
| 3次(OPEN_ITEMS.md該当パラグラフ) | `OPEN_ITEMS.md` 冒頭News Trial-12記述部分 | 2,165字 | 984 token |

**解釈**: このチェーン自体は32,801→10,140→2,165と段階的に圧縮されており(それぞれ前段の約31%・21%)、**単純な全文コピペではなく実際に要約が機能している**(前身T2/T3報告と異なり、本タスクでは「連鎖が悪い」と断定する実測は得られなかった)。**リスクは圧縮そのものではなく、3段階すべてが別々のタスク・別々のAgent呼び出しで存在し続け、後続タスクが「どの段階を読むべきか」判断できず安全側で全段階(合計45,106字)を読みにいく可能性**にある。この判断ロジック自体は本タスクの読み取り範囲では確認できない(推定)。

---

## 3. 削減案とリスク(採用判断はユーザー)

| 観点 | 削減案 | 期待削減量(概算/週、根拠) | リスク | 実装コスト |
|---|---|---|---|---|
| 2-1 Ledger重複 | Ledger要約カード(fact一覧+confidenceのみ、1KB程度)を既存Ledgerと並置し、Claude開発Agentの調査時はまず要約カードを読む運用を委任文で明示 | 調査系タスク1件あたり15K〜50K字→1K字程度に圧縮(実測差分ベース)、10件/月規模なら概算150K〜500K字/月の削減見込み(推定、未実装) | 要約カードとLedger本体の不整合(Reconciliation漏れ)、要約カード自体の保守負荷 | 小(script追加+運用ルール1行) |
| 2-2 Sonnet→Opus再読 | Opus委任文に「Sonnet REPORTの該当節のみ抜粋」を必須化、コード全文ではなく`git diff`相当の変更差分のみを渡す | 3V Phase1の実例(45.2万字)がdiffベースなら数万字規模まで縮小可能性(推定、diff生成には別コスト) | Opusが変更箇所以外の既存コード文脈を見落とし、L2レビューの網羅性が低下する(Fact Safety類似のQA機能低下リスク) | 中(委任文テンプレート変更+diff抽出手順の整備) |
| 2-3 巨大SSOT全文読込 | `DECISION_LOG.md`もT-1同様の構造分割(3,000字超エントリの履歴切り出し)を検討 | T-1のOPEN_ITEMS.md実績(全文-54%、Grep最悪ケース-85〜90%)を参考に同等規模の削減見込み(推定、DECISION_LOG.mdは巨大単一行問題の有無を本タスクで未確認) | SSOT正確性低下・エントリ分割時の参照リンク切れ、DECISION_LOG.mdは時系列の意思決定履歴であり分割の仕方次第で経緯追跡が困難になる | 中〜大(1,334,377字の構造分析+分割作業自体が大きなSonnet委任になる) |
| 2-4 Opus context過多 | `opus-consultant.md`に「入力ファイル数上限」または「変更差分限定」の指示を追加 | 3V Phase1実例ベースで1件あたり最大20万token規模の入力を数万token規模に圧縮できる可能性(推定) | Opusの診断精度低下(2-2と同じリスク)、PM_GOVERNANCEの「Opusは診断目的で原因・選択肢・影響範囲を整理」という役割と矛盾しうる(範囲を絞りすぎると影響範囲評価ができない) | 小(agent定義への1文追加、ただし判断基準の設計は別途必要) |
| 2-5 Research結果の引き継ぎ | 委任文テンプレートに「OPEN_ITEMS.md該当行のみ参照、DECISION_LOG該当エントリ・元REPORTは詳細確認が必要な場合のみ読む」という段階的read方針を明記 | 定量化は困難(読む/読まないは委任者[Fable]の判断次第)。実例チェーン(45,106字)の最終段(2,165字)だけで足りるタスクが多ければ削減効果は大きい(推定) | SSOTの参照粒度が粗くなり、詳細確認を省略した結果の事実誤認・Reconciliation漏れ | 小(運用ルール明記のみ、PM_GOVERNANCE 11節への追記が必要) |

**共通リスク**: いずれの案も「要約・省略」を伴うため、`PM_GOVERNANCE.md`のFact Safety・Reconciliation原則と潜在的に衝突しうる。特に2-2/2-4(Opus入力の絞り込み)はOpusの役割そのもの(「原因・選択肢・影響範囲」を広く見る診断層)と矛盾する可能性があり、慎重な検討が必要(採用判断はユーザー)。

---

## 4. weekly limitとの対応(推定)

- **直近7日間(2026-09-04〜09-11)実測**: commit数**222件**(`git log --since`実測)、この期間に新規作成/更新されたREPORT.mdファイル**153件**(現存分のみ、削除・リネーム分は含まず)、現存合計**2,879,700字**(実測、`wc -c`合計)。
- **DECISION_LOG.md増分**: この7日間の全diffの追加行(`+`行)合計**1,149,009字**(実測、`git log -p`)。
- **OPEN_ITEMS.md増分**: 同期間の追加行合計**5,136,835字**(実測)。この値が突出して大きい理由は、restructure前(2026-09-04〜09-10)のConsolidation型commitが巨大単一行を繰り返し書き換えていたため(1-2節の`6a39015`実例333,875字が複数回発生した結果と推定)。**T-1実施後(2026-09-10以降)はこの種の増分が大幅に縮小していると推定されるが、期間を跨いだ按分計算は本タスクでは未実施**。
- **カテゴリ別REPORT件数・合計字数(実測、ファイル名パターンマッチ)**:

| カテゴリ | 件数 | 合計字数 | 1件あたり平均 |
|---|---|---|---|
| TRIAL系 | 61件 | 1,231,372字 | 20,186字/件 |
| PRODUCTION-WIRING系 | 19件 | 355,516字 | 18,711字/件 |
| AUDIO系 | 14件 | 250,238字 | 17,874字/件 |
| OPUS-L2系 | 3件 | 60,589字 | 20,196字/件(**ただし入力側の実測は1件で約45万字**、2-4節参照) |

- **推定(タスク種別の重さ)**: **出力字数ベース**ではTRIAL系がカテゴリ合計で最大(頻度×平均サイズの両方が高い)。ただし**入力側**まで含めると、OPUS-L2系は件数こそ少ないが1件あたりの実効Token消費(出力2万字+入力45万字=計47万字規模)がTRIAL系(1件平均2万字)の**20倍以上**になりうる(2-4節の実測1件を根拠とした推定、他2件のOpus L2レビューは個別未計測のため一般化には注意)。**Consolidation型commit**(統合SSOT反映、REPORTファイルを新規作成せずDECISION_LOG/OPEN_ITEMS.mdへ直接反映するため上表のREPORT集計には含まれない)も、1-2節の実測(diff 68,767字〜333,875字)からTRIAL系と同等〜それ以上の負荷を持つカテゴリとして別枠で考慮すべき(直近7日で`PM-CLOSEOUT-CONSOLIDATION-*`パターンのcommitは`git log`実測で48件確認、うち1件あたりのdiff規模はSSOT編集量に依存し実測値のばらつきが大きい)。

---

## QCD

- **Quality**: 全数値は`wc -c`・`git show`・`git log -p`・`grep -c`・`du -b`によるrepo内直接実測に基づく(本タスクで新規実測)。前身T2/T3報告からの再掲は「実測(prior report...)」等で明示。推定箇所は「推定」「測れない」を本文中に明記。token概算は文字数/2.2の単純換算であり、実際のTokenizer挙動(日本語・コード混在時の分割特性)とは乖離しうる近似値。
- **Cost**: 本タスクは読み取り専用・¥0(API呼び出し・Git操作・編集なし、`git show`/`git log`は読取専用コマンド)。
- **Delivery**: T-1効果実測(1)・重複読込5観点実測(2)・削減案とリスク表(3、採用判断はユーザー)・weekly limit対応推定(4)を1回のSonnet委任内で完了。`DECISION_LOG.md`のGrep最悪ケース実測・`OPEN_ITEMS_HISTORY.md`実際の参照頻度・Opus L2レビュー残り2件の入力規模実測は、本タスクの範囲では未実施(追加調査が必要な項目として明記)。
