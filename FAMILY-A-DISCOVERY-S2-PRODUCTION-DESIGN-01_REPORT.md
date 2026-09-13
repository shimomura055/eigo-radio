# FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01

管理ID: FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01
性質: ¥0設計(実装・配線なし)。到達Status: 設計完了 →`USER_DECISION_REQUIRED`(Gate 2)。
現在Status=VALIDATED(Trial)→Production設計着手可であり、**`APPROVED_FOR_PRODUCTION`
ではない**。本REPORTは設計案のみを提示し、Productionコード(`er0*`)は一切変更していない。

## ユーザー指示(原文)

> ユーザーは、S2について追加Trialを先に増やさず、Production設計フェーズへ進むことを
> 承認しました。ただし、これはまだProduction実装・配線承認ではありません。現在Status
> はVALIDATED→Production設計着手可であり、APPROVED_FOR_PRODUCTIONではありません。
> 次は費用ゼロで、S2のProduction設計を詰めてください。設計対象は少なくとも以下です。
> 現行`run_one_pattern`をどう分割するか/Focus→Main Story→Point Role Planning→Point
> 生成、の正式な処理順/retry単位/`STAGE1_MAX_REGENERATIONS`のProduction値案/「通常は
> Main Story固定、ただしLocal Rewrite等の安全装置による修正は例外」という原則/Main
> Story側MAJOR・FAIL時のStage 1再生成条件/Stage 2-3 exhaustion時の扱い/Local
> Rewrite・Point Overlap・Point Value・Directional Precheck・Evidence Compressionとの
> 整合/retry・fallback・regeneration全体での一貫性/News・Trend・Discovery既存
> Productionとの競合・共通化可能性/Fact Checker FAILのlocus分類をProductionでどう
> 扱うか/Dangling Reference有無。設計案には、推奨案だけでなく主要な代替案とQCD上の
> 差も示してください。Productionコードへの実装・配線はまだ行わず、設計完了後にGate 2
> としてユーザー判断を求めてSTOPしてください。

---

## 1. 分割設計

**現行`run_one_pattern`(`er003_v1_n3_01_articles_generate.py` L818-1248)の実態**:
Point Role Planning(トピック+Ledgerのみを入力、Main Story本文は未使用)→
Writer 1回呼び出しで**Main Story+Point One+Point Two全体を一括生成**(
`_generate_and_compress_article`、Evidence Compressionも記事全体に適用)→
Point Overlap/Value QA retryループ(NG時はRole Planning再計画+記事**全体**を
Diagnostic Full Retryで作り直す、`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`)→
Fact Checker A'(FAILはblocking)→ Ledger Deviation+Local Rewrite(
`MAX_REWRITE_CYCLES=3`、局所修正のみ)→ Directional Precheck(non-blocking)。

つまり現行Productionは「Role Planningは事前計画のみ・Main Story本文を見ずに
計画→記事全体を1回で書く」設計であり、S2が検証した「Main Story本文を確定させて
から、その本文を実際に読んでRole Planningする」という順序そのものが存在しない。
したがって分割は**Writer呼び出し自体を2回(Stage1本文のみ/Stage3 Points)に
分けること**が本質であり、単なる関数リファクタリングでは済まない。

代替案:

| 案 | 内容 | 品質 | 安全 | コスト | 納期 | 回帰範囲 |
|---|---|---|---|---|---|---|
| **P1(推奨)** | Discovery専用の新関数(仮`run_one_pattern_staged`)を追加し、既存`run_one_pattern`は**無変更のまま残す**。新しい`editorial_mode`値(例`"discovery_focus_staged"`)を明示指定した場合のみ新関数が呼ばれる(opt-in) | S2 Trialと同等(Discovery限定) | 高。既存モードは新関数を一切呼ばないため既存出力のバイト不変性が自明 | 中。Ledger Loop等の共通処理を新規に切り出す/複製するコストが発生 | 短い。検証対象がDiscovery経路のみ | Discovery(S2採用時のみ)に限定 |
| P2 | `run_one_pattern`内部を段階化し、全`editorial_mode`で同じStage1/2/3骨格を通す | 理論上はNews/Trendにも段階化の恩恵が及ぶ可能性(未検証) | 低〜中。News Major/Daily/Trend Synthesisという安全確認済みの既定経路に直接手を入れるため、既存出力のバイト不変性を毎回テストで証明する必要がある | 低(コード重複なし)だが検証コストが高い | 長い。全editorial_modeの回帰テストが必要 | News/Trend/Discovery/Why全体 |

**推奨: 案P1**。理由: (a)`docs/pm/PM_GOVERNANCE.md`のGate 3チェックリスト
(Production正式初回経路/DEV・Trial-onlyではないこと/既存retry・fallbackとの
整合)を満たしつつ検証範囲を最小化できる、(b)CLAUDE.mdの「速度よりも安定性を
優先」方針に合致し、News/Trendという既に安定稼働している経路に触れない、
(c)「1記事ずつ完結」原則・Gate 4 Dangling Reference Check上、影響範囲を
Discoveryだけに限定した方が判定しやすい。将来News/Trendへ段階化を広げたい
場合は、P1で確立した共通ヘルパー(Ledger Loop関数化等、7節参照)を土台に
P2的統合を改めて検討すればよい(漸進的移行)。

## 2. 正式処理順

```
Focus決定(editorial_type_module_block解決。既存resolve_editorial_type_module_block
          と同じ仕組みで新モード値を追加する想定)
  → Stage 1: Main Story Writer(Title+Main Story+draft In One Line、Point見出しなし)
  → Stage 1 QA: Fact Checker A'(Main Story単体)
             → Ledger Deviation Check + Local Rewrite(Main Story単体、cycle上限=MAX_REWRITE_CYCLES)
             → Directional Fact Precheck(Main Story単体、non-blocking)
  → [blocking判定: NGならSTAGE1_MAX_REGENERATIONSまでStage 1再生成(フィードバック付き)]
  → Stage 2: Point Role Planning(確定したMain Story本文を実際に入力として使用)
  → Stage 3: Point One/Two Writer(Role Plan+Main Story参照)
             → Evidence Compression(Points本文のみ)
             → Main Story(固定)と結合
  → Point Overlap QA・Point Value QA(結合後の記事全体。NG時はStage 2-3のみ再実行、
    POINT_OVERLAP_ARTICLE_RETRY_MAX回まで)
  → 記事全体 Fact Checker A'(FAILはblocking。ただしStage 2-3 exhaustion後の
    フォールバックとしてのみStage 1へescalateする余地あり、5節参照)
  → 記事全体 Ledger Deviation Check + Local Rewrite(cycle上限。MAJOR残存時、
    locate_target_sentenceでlocus判定→Main Story側ならStage 1再生成へescalate、
    Points側/不明ならNG_REVIEW_REQUIRED)
  → Directional Fact Precheck(記事全体、non-blocking)
  → OK/NG_REVIEW_REQUIRED確定。artifact保存(article.md/run_summary.json/audit/*)
```

各Stageの入力・出力・artifact(Trial実装`er011_discovery_focus_s2_full_trial_01.py`
の`out_dir`構成を踏襲):

| Stage | 入力 | 出力 | artifact |
|---|---|---|---|
| Stage1 Writer | topic/Ledger/Focus Module | title_line, main_story_text | `audit/stage1_writer_attempts.json` |
| Stage1 QA | title_line+main_story_text | blocking可否, 確定main_story_text | `stage1_fact_qa.json`, `stage1_ledger_deviation.json`, `stage1_directional_fact_precheck.json` |
| Stage2 Role Planning | 確定main_story_text | role plan(JSON) | `audit/stage2_role_planning_attemptN.json` |
| Stage3 Writer+EC | role plan+main_story_text | points_text(EC後) | `audit/stage3_points_writer_attemptN.json`, `audit/stage3_evidence_compression_attemptN.json` |
| 結合後QA | 記事全体 | Overlap/Value QA結果 | `stage23_overlap_retry_log.json` |
| 記事全体QA | 記事全体 | fact/ledger/directional結果 | `fact_qa.json`, `final_ledger_deviation.json`, `audit/final_directional_fact_precheck.json` |
| 最終 | 確定記事全体 | article.md, run_summary.json | `article.md`, `run_summary.json`, `audit/stage_trace.json` |

## 3. retry単位・しきい値

- **通常**: Stage1固定、Stage2-3のみ再実行(`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`、
  既存値をそのまま流用)。
- **Stage1再生成条件**(いずれか、Trial実装と同一設計):
  (a) 記事全体Ledger Deviation MAJORのclaim_in_articleがlocate_target_sentenceで
      Main Story側に位置し、Local Rewrite cycle上限(`MAX_REWRITE_CYCLES=3`、
      既存値)を尽くしても未解決。
  (b) Stage2-3再実行が`POINT_OVERLAP_ARTICLE_RETRY_MAX`回尽くしてもPoint
      Overlap/Value QAがNGのまま(Main Story側原因切り分け不能時の最終フォール
      バック、1回のみ)。
  (c) 記事全体Fact Checker FAIL(5節の簡略locusルールに従い、Stage2-3
      exhaustion後のフォールバックとしてのみ)。
- いずれも尽きればNG_REVIEW_REQUIRED(fail-closed、無限ループ・黙示的PASSなし)。

**`STAGE1_MAX_REGENERATIONS`のProduction値案**:

| 案 | 値 | コスト影響(概算) | 安全性 |
|---|---|---|---|
| **案1(推奨)** | 1回(Trial実測値と同一) | Trial実測Main Story生成コスト¥15〜20/本に対し、Trialでは0/2本しか発火せず、平均コスト増は小さい。最悪ケース(必ず発火)でもMain Story生成コストは約2倍 | 「無限ループなし・fail-closed」原則を保ちつつMain Story側原因を1回だけ切り分けられる |
| 案2 | 2回 | 最悪ケースで約3倍。既存Diagnostic Full Retry(Stage2-3側)と多重に絡み、想定より生成回数・時間・コストが膨らむリスク | より安全側だが過剰投資になりうる |
| 案3 | 0回 | 追加コストなし | 最も安全・低コストだが、ユーザー指示にある「Main Story側MAJOR・FAIL時のStage1再生成条件」という設計要求そのものを放棄することになる |

**推奨: 案1(`STAGE1_MAX_REGENERATIONS=1`)**。

**Diagnostic Full Retryとの対応関係**: 既存`run_one_pattern`のdiagnostic_full_retry
(`POINT_OVERLAP_ARTICLE_RETRY_MAX`回、記事全体を1単位として全文再生成)は、S2
設計では「Stage2-3(Points)のみの再生成」に**対象範囲を限定**して流用する
(診断プロンプト+Role Planning再計画のロジックはそのまま、対象がPointsのみに
変わる)。Stage1再生成はこれとは独立した新規ループとして扱い、二重にカウント
しない(Trial実装と同一設計、`stage1_regen_attempt`と`retry_attempt`は別カウンタ)。

## 4. Main Story固定原則(仕様文案)

> Stage 2(Point Role Planning)からStage 3(Point生成・結合・Point Overlap/Value
> QA retry)を通じて、Main Story本文(Stage 1で確定した範囲)は原則として一切
> 変更しない。ただし、記事全体に対する既存の安全装置(Ledger Deviation Check +
> Local Rewrite、および差分QA[Fact Checker A' 再実行+Ledger再確認])が、Main
> Story側の1文にMAJOR逸脱を検出し、それを局所的に書き換えて解決する場合は
> 例外として許容する。この場合、書き換え後のMain Story本文は差分QA自体による
> 再検証を経たものとみなし、「Main Story完全固定」原則の違反とはしない。Stage 1
> 再生成(Main Story全体の書き直し)と、Local Rewriteによる局所修正(1文単位)は
> 区別し、前者のみを「原則の例外的発動(=Stage1再生成条件、3節)」として扱い、
> 後者は既存安全装置の通常動作として扱う。

(根拠: Trial実測でA2のMain Story側1文が実際にLocal Rewriteで書き換わった実例
があり[Trial REPORT §7-3]、「完全固定」と「既存安全装置」は両立しない場面が
現実にあることが確認済み。)

## 5. Fact Checker FAILのlocus分類

| 案 | 内容 | 品質 | 安全 | コスト | 備考 |
|---|---|---|---|---|---|
| (i) 厳密分類 | Fact Checkerの`unsupported_specific_claims`各claimを`locate_target_sentence`でMain Story/Points側に分類、Main Story側があればStage1へ | 高(原因を正確に切り分け) | 未検証。Fact Checker出力の文字列形式とLedger Deviationのclaim_in_articleの形式が同一保証がなく、Trialで一度もFAILが発火せず未検証 | 追加呼び出しなし(rule-based、¥0)だが実装・テストコストは中 | 現時点でFAIL自体が実データで未観測 |
| **(ii) 簡略ルール(推奨、Trial採用済み)** | Stage2-3 exhaustion後のみStage1へescalate(3節(c)) | 中(早期の原因特定はしないが誤判定もない) | 高。単純で予測しやすい、fail-closed | 低。実装済み設計をそのまま流用 | Trial実装と同一 |
| (iii) 常にStage1から | Fact Checker FAILは常にMain Story起因とみなし直接Stage1へ | 低(Points側原因でも無駄にMain Story作り直し) | 中 | 低実装だが無駄なコスト増の恐れ | 非推奨 |

**推奨: 案(ii)**。理由: Fact Checker FAILが実データで一度も発火しておらず、
`unsupported_specific_claims`の文字列形式が`locate_target_sentence`の入力に
そのまま使える保証が無い(未検証)。安全側に倒し、まず簡略ルールでProduction
導入し、実データでFAILが発火した際の挙動を観察してから、必要なら案(i)への
高度化を検討する段階的アプローチとする。

## 6. 既存QAとの整合表

| QA機構 | 実行Stage | 実行回数/しきい値 | 既存値のまま? |
|---|---|---|---|
| Fact Checker A'(Main Story単体) | Stage1直後 | `run_fact_checker_with_gates`既存retry仕様 | Yes(既存関数無変更) |
| Ledger Deviation+Local Rewrite(Main Story単体) | Stage1直後 | `MAX_REWRITE_CYCLES=3` | Yes |
| Directional Precheck(Main Story単体) | Stage1直後、non-blocking | 1回 | Yes(既存関数) |
| Point Role Planning | Stage2 | 1回(Stage2-3 retry毎に再計画) | 既存`run_point_role_planning`はMain Story本文を受け取らない設計のため、**シグネチャ拡張または新関数が必要**(要変更) |
| Evidence Compression | Stage3直後 | 1回(適用可否判定) | 適用範囲がPoints本文のみに変更(既存`run_one_pattern`は記事全体に適用)。**既存デフォルト動作とは異なる新しい適用範囲** |
| Point Overlap QA / Point Value QA | 結合後 | `POINT_OVERLAP_ARTICLE_RETRY_MAX=2` | Yes(既存関数`run_point_overlap_qa_and_regenerate`/`run_point_value_qa`無変更) |
| Fact Checker A'(記事全体) | Stage2-3 OK後 | 既存gates仕様 | Yes |
| Ledger Deviation+Local Rewrite(記事全体) | Fact Checker後 | `MAX_REWRITE_CYCLES=3`+locus判定 | 既存関数+新規locus判定ロジック追加(既存関数自体は無変更、呼び出し側で`locate_target_sentence`を追加適用) |
| Directional Precheck(記事全体) | 最終 | 1回、non-blocking | Yes |
| 差分QA(Local Rewrite内) | Local Rewrite各cycle | 既存仕様(target-sentence-matching既定ON、OPEN-141) | Yes |
| 3V(音声バリエーション) | - | - | 本設計(記事生成)の対象外。別Family(EDITORIAL-B-FAMILY-VOICES-3V)であり無関係 |

## 7. News/Trend/Discoveryとの競合・共通化

**案P1採用時**: 既存モード(News Major/Daily/Trend Synthesis/現行Discovery
非staged)は新関数を一切呼ばず既存`run_one_pattern`を呼び続けるため、バイト
不変性は「新関数へ分岐しない」ことで自明に担保される(既存単体テスト・
回帰テストで確認可能、追加テスト不要)。Ledger Loop等の共通処理を新規に
切り出す場合、既存`run_one_pattern`側のインラインコードは元のまま**据え置き**、
新Staged関数専用に別途関数化する方針を取る(コード重複は増えるが変更ゼロで
安全性を最優先)。

**案P2を将来検討する場合の前提条件**: (a) News/Trendでも段階化に品質上の
メリットがあるとユーザーが判断すること、(b) 既存News/Trend記事のQA基準・
出力フォーマットが変わらないことを回帰テストで保証すること、(c) News/Trend
向けに独立したTrialでVALIDATEDを得ること(現状S2はDiscovery限定で検証済み、
News/Trendでの効果は未検証)。

## 8. Dangling Reference

現状Trial実装は以下のTrial専用ファイルに依存しており、そのままではProduction
化できない:
- `er011_discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK`
  (Focus Module Part A本文)→ Production化時は既存`EDITORIAL_TYPE_MODULE_BLOCKS`
  辞書へ正式追加(新規`editorial_mode`値)し、Trialモジュールへの依存を切る。
- `er011_discovery_focus_part_a_standalone_trial_01_run.run_stage2_role_planning`
  /`run_stage3_points_writer`/`assemble_article`→ Production側モジュールへ
  正式移設(関数名・置き場所はGate2確定後に決定)。
- Trial専用の`extract_stage1_main_story`パーサー、`run_ledger_local_rewrite_loop`
  (共通化ヘルパー)→ Production側で正式関数化(6/7節の重複解消方針に従う)。

Production化後は、Trial専用ファイル(`er011_discovery_focus_s2_full_trial_01.py`
等)はarchive目的でGitに残置してよいが、**Production経路からのimportは一切
残さない**(Gate4 Dangling Reference Check該当ゼロを目指す)。

## 9. Gate 3への準備

**テスト一覧**:
- 分岐テスト(モック): Stage1 blocking→regen成功/Stage1 regen上限到達→NG/
  Stage2-3 exhaustion→Stage1 fallback成功/最終Ledger main_story locus→
  escalation成功/points locus→escalationせずNG(Trialの`GenerateArticleStage
  BranchTests`6ケースを土台に、Production関数名へ更新して再利用)。
- バイト不変テスト: 既存`run_one_pattern`呼び出し経路(News Major/Daily/
  Trend Synthesis/現行Discovery非staged)が、共通ヘルパー抽出等の変更後も
  出力バイト単位で不変であることを確認するテスト。
- 統合テスト: 新Staged関数のend-to-end(モック)テスト、Retry単位・
  `STAGE1_MAX_REGENERATIONS`上限・locus判定の整合性確認。
- runtime evidence: 実データ最低1本(意図的に問題を含むLedgerでMAJORを
  発生させ、Stage1 escalationを実際に発火させるTrial、追加費用要)。

**実データ未検証分岐の検証計画**: 「意図的MAJOR Ledger」Trial1本(推定コスト:
Main Story¥15〜20×2回[初回+Stage1再生成]+Points生成+QA一式、既存Trial実測
から概算¥40〜60/本、A2またはB1B片方のみで十分)でStage1 escalation分岐(a)
を実データ検証する。Stage2-3 exhaustion fallback(b)・Fact Checker FAIL
escalation(c)は、それぞれ別途誘発条件を作った追加Trialが必要(追加費用要、
優先順位はGate2でユーザーが判断)。

## 10. Gate 2判断事項

1. 分割方式: 案P1(Discovery専用新関数、推奨)か案P2(`run_one_pattern`共通
   段階化)か。
2. `STAGE1_MAX_REGENERATIONS`: 案1(=1、推奨)か案2(=2)か案3(=0)か。
3. Fact Checker FAIL locus分類: 案(i)厳密分類か案(ii)簡略ルール(推奨、Trial
   採用済み)か案(iii)常にStage1からか。
4. Trial専用ファイル(`s2_prev`/`t9`等)の扱い: Production化時に正式移設
   (推奨)するか、当面Trialファイルをread-only importし続けるか(Dangling
   Reference残存を許容する暫定案、非推奨)。
5. 実装着手の可否と費用: 上記1-4が決まった後、実装+モックテスト自体は¥0
   (コード変更のみ)。ただしGate3のruntime evidence取得(9節)には追加API
   費用(概算¥40〜60/本×検証本数)が発生する。着手の可否・優先順位・追加
   Trial本数の判断を求める。

---

## SSOT追記文案(編集しない、ユーザー承認後にFableが反映)

**OPEN-135追記案**:
> (FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01、2026-09-13) ユーザー承認により
> S2はProduction設計フェーズへ移行(VALIDATED[Trial]→設計着手可、
> `APPROVED_FOR_PRODUCTION`ではない)。設計成果は
> `FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01_REPORT.md`に記録、Gate2判断待ち
> (分割方式P1/P2、`STAGE1_MAX_REGENERATIONS`値、Fact Checker FAIL locus分類、
> Trial専用ファイル扱い、実装着手可否・費用の5項目、詳細は同REPORT10節)。

**DECISION_LOG.md追記案**(暫定、Gate2で正式決定後に本エントリを確定版へ更新):
> 2026-09-13: FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01。ユーザー承認により
> S2 Production設計フェーズ着手(実装・配線はまだ、`USER_DECISION_REQUIRED`
> [Gate2]でSTOP)。詳細は同REPORT参照。

**CURRENT_SPEC.md案**: 現時点では編集しない。Gate2でユーザーが分割方式等を
決定した後、「## Discovery Focus S2(Production)」節を新設し、確定した処理順
・retry単位・`STAGE1_MAX_REGENERATIONS`値・locus分類ルールを正式記載する
(Gate3配線完了後に`PRODUCTION_WIRED`化)。

---

## 事前指定外Read(理由)

なし(T-1: 事前指定Read/Grep一覧の範囲内で完結)。
