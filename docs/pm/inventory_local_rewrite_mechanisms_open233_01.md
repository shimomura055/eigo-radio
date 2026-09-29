# 既存 部分Rewrite/Local Rewrite 機構 棚卸し(OPEN-233 Self-Recovery Flow 設計前提調査)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_05)
作成日: 2026-09-30
性質: read-only調査。API呼び出しなし、¥0。Production非接続・コード変更なし。

## 0. 要旨(結論を先に)

- 英語(EN)記事の「Ledger逸脱MAJORの文単位Local Rewrite」機構は、
  **既にProduction稼働中**(`er010_ledger_local_rewrite_09.py`)。ただし
  現状の呼び出し元は Family B 系(`er003_v1_n3_01_articles_generate.py`
  のN3-01直接生成パイプライン、`er012_b_family_voices_writer_generic_01.py`
  の`run_ledger_deviation_and_local_rewrite`)のみで、**Family X の
  Standard(no-heading)/Advanced(忠実英訳)生成経路
  (`er003_v1_n3_01_standard_a2_generate.py`/
  `er003_v1_n3_01_advanced_adaptation_generate.py`)には配線されていない**。
  Family Xの現行retryは「記事全文をmust-fixブロック付きで1回だけ全文
  再生成」(`build_must_fix_block`/`must_fix`引数、
  `er012_e_family_entertainment_two_level_runner_01.py`が呼び出し元)のみ。
- JA側には、文単位のLocal Rewrite機構は**存在しない**。JA
  (`er019_family_x_ja_writer_o_r1_r2_01.py`)の既存回復手段は
  Original/R2各段の「must-fixブロック付き1回だけ全文(その段)再生成」のみ
  (段単位、文単位ではない)。JA→EN不整合(origin=ja_source MAJOR)を検知
  した場合の既存経路は「案B」(JA Original段への差し戻し全文再生成→
  R1→R2→EN側再整合、カスケード全体を回す)であり、JA本文の対象文だけを
  局所修正しEN側だけ再整合する機構は無い。
- TTS(音声)レベルの「発音NGspanのみのLocal Rewrite」機構
  (`er020_tts_retry_local_rewrite_01.py`)も別途Production稼働中だが、
  これはASR比較による発音問題span特定+Lunaによる自然な英語QAが目的で、
  Ledger/事実逸脱の局所修正とは別ドメイン(直接の再利用対象ではないが、
  「置換失敗時は原文復帰」等のguard設計思想は参考になる)。

## 1. 棚卸し一覧(機構名・Production利用状況)

| # | 機構 | ファイル:関数/主要オブジェクト | Production利用状況 |
|---|------|--------------------------------|---------------------|
| 1 | EN Ledger Deviation Checker本体 | `er003_v1_en_direct_vfl_01_generate.py::run_deviation_check` | PRODUCTION_WIRED(全Family共通コア、hook_aware/prior_issues/origin対応) |
| 2 | EN 文単位Local Rewrite primitive | `er010_ledger_local_rewrite_09.py`(`rewrite_ng_item`/`locate_target_sentence`/`extract_point_context`/`apply_rewrites`/`apply_diff_qa_to_resolved_rewrite`) | PRODUCTION_WIRED(Family B系のみ) |
| 3 | EN Local Rewrite cycle制御(記事全体) | `er003_v1_n3_01_articles_generate.py`(N3-01直接生成、L1147-1317) | PRODUCTION_WIRED(N3-01直接生成=Family B系) |
| 4 | EN Local Rewrite cycle制御(Family B generic writer) | `er012_b_family_voices_writer_generic_01.py::run_ledger_deviation_and_local_rewrite` | PRODUCTION_WIRED(Family B) |
| 5 | Family X EN 全文must-fix retry(Standard) | `er003_v1_n3_01_standard_a2_generate.py::build_must_fix_block`/`generate_family_x_no_heading_prompt` | PRODUCTION_WIRED(Family X、段=全文単位、1回のみ) |
| 6 | Family X EN 全文must-fix retry(Advanced) | `er003_v1_n3_01_advanced_adaptation_generate.py::build_must_fix_block`/`build_family_x_faithful_translation_prompt` | PRODUCTION_WIRED(Family X、段=全文単位、1回のみ) |
| 7 | Family X/E 全体オーケストレーション(must-fix retry呼び出し元) | `er012_e_family_entertainment_two_level_runner_01.py::_must_fix_from_deviations`ほか | PRODUCTION_WIRED |
| 8 | JA Original/R2 must-fix全文(段単位)retry | `er019_family_x_ja_writer_o_r1_r2_01.py::build_must_fix_block`/`build_original_prompt`/`generate_original`/`generate_r2` | PRODUCTION_WIRED(NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01) |
| 9 | JA→EN不整合時の「案B」(JA Original差し戻し全文再生成) | `er019_family_x_ja_writer_o_r1_r2_01.py`(`original_must_fix`引数、FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01[W6]) | PRODUCTION_WIRED(カスケード全体再生成、局所ではない) |
| 10 | Family X構造Gate(3分割・見出し・段落数) | `er003_v1_n3_01_scaffold_generate.py::split_family_x_article_text_v2` | PRODUCTION_WIRED(status値で返す設計、失敗時は呼び出し側が1回だけmust-fix retry) |
| 11 | TTS発音NGspan Local Rewrite(Production) | `er020_tts_retry_local_rewrite_01.py::run_local_rewrite_recovery` | PRODUCTION_WIRED(Connected Speech 5role限定) |
| 12 | TTS Local Rewrite原型(cooldown+span特定) | `er020_tts_cooldown_local_rewrite_trial_01.py` | VALIDATED Trial(#11の移設元、read-only参照のみ) |
| 13 | TTS Local Rewrite 7-Gate自然英語QA原型 | `er020_tts_local_rewrite_natural_english_qa_trial_02.py` | VALIDATED Trial(#11の移設元) |
| 14 | Full Story専用TTS Local Rewrite回復 | `er003_v1_sing01_news_tail_fix.py`(`generate_news_narration_wide_margin`専用) | PRODUCTION_WIRED(#11の呼び出し元の1つ) |
| 15 | Local Rewrite差分QA(受理直後の再検証) | `er010_ledger_local_rewrite_09.py::run_diff_qa_for_accepted_rewrite`/`apply_diff_qa_to_resolved_rewrite` | PRODUCTION_WIRED(OPEN-141、Fact Checker A'+Ledger再確認) |
| 16 | Local Rewrite原型ルール策定Trial(歴史) | `er009_n1_full_writer_ledger_integration_08.py`、`er009_n1_local_rewrite_rule_trial_07.py` | 過去Trial(#2のREWRITE_SYSTEM_PROMPT/3段階escalationの由来) |
| 17 | Local Rewrite再利用のEvidence確認Script | `er012_open131_fact_attribution_local_rewrite_evidence_01.py` | 過去Evidence(新機構ではなく#2の検証のみ) |
| 18 | En ASR意味的同等性チェッカー(TTS後、事実逸脱とは別軸) | `er021_en_asr_semantic_equivalence_production_01.py`ほか | PRODUCTION_WIRED(ASR発音検証、Local Rewriteの入力にはならない) |

## 2. 詳細(再利用可否を含む主要機構のみ抜粋)

### 2.1 `er010_ledger_local_rewrite_09.py`(EN局所Rewrite第一候補)

- **用途**: Ledger Deviation Checker(Hook-aware)がMAJORと判定した箇所を、
  記事全体の再生成ではなく対象文(前後1文をcontextとして参照するのみ)に
  限定して書き換える。
- **対象範囲・修正単位**: 文単位(`locate_target_sentence`: exact
  substring→word-overlap>=0.25 fallback)。対象文が属する見出し区切り
  section全文(`extract_point_context`)を参考contextとして渡す
  (見出しが無い本文=Family Xのno-heading Standardでも、Title行から次の
  見出しまでを1sectionとして扱うため、汎用的に動作する設計)。
- **入力**: Verified Ledger全文、対象文、Checkerのissue/explanation/
  フラグ(`vfl01.DEVIATION_FLAG_KEYS`)。**rewrite_hint/rewrite_kind
  (delete/replace_with_ledger_value/narrow_scope)は入力に無い**
  (REWRITE_SYSTEM_PROMPTは「弱める(soften)」という固定方針のみを持ち、
  Checkerが「削除すべき」「Ledger値で置換すべき」と判定したケースを
  区別する経路が無い)。
- **出力・差し戻し**: `apply_rewrites()`が`article_text.replace(
  original_ng_sentence, final_text, 1)`という単純文字列置換。**ここに
  既知のギャップがある**: `if r["final_text"] and r["original_ng_sentence"]
  in updated:`という条件のため、`final_text`が空文字列(=完全削除)の場合は
  適用されずスキップされる(削除系rewrite_kindをそのまま流すと無言で
  変更なしになる、要修正)。
- **再検証**: 各attempt後にwindow(before+target+after)を
  `run_deviation_check`へ再投入(`use_target_sentence_matching=True`で
  対象文自身のdeviationのみに絞る再分類ロジックあり、誤って隣接文の
  逸脱で対象文のrewriteをblockしない設計)。受理直後にさらに
  `apply_diff_qa_to_resolved_rewrite`で差分QA(Fact Checker A' web_search
  + Ledger再確認)。cycle全体では記事全文を`run_deviation_check`へ
  再投入(prior_issues未使用、素のfull recheck)。
- **retry構造・上限**: 文単位3回(`MAX_REWRITE_ATTEMPTS=3`、
  attempt1=issue提示→attempt2=flags/explanation追加→attempt3=
  scope-safe fallback)。記事全体cycle上限も3回(`MAX_REWRITE_CYCLES=3`、
  同じ定数を別軸で流用、独自の新定数は作られていない)。両方尽きても
  MAJOR残存の場合はNG_REVIEW_REQUIRED(fail-closed、無限ループなし)。
- **guard**: 対象はMAJORのみ(MINOR対象外)。新Fact追加・因果反転・
  比較/時系列反転を禁止するprompt制約。Family X固有の構造Gate
  (`split_family_x_article_text_v2`)との整合チェックは**組み込まれて
  いない**(Family B系はheading構造が異なるため、このGate自体を意識する
  必要がなかった)。
- **Production利用状況**: MANAGEMENT_ID系列
  `ER-010-NO9-PRODUCTION-INTEGRATION-FINAL-09`ほか。呼び出し元は
  `er003_v1_n3_01_articles_generate.py`(N3-01直接生成)と
  `er012_b_family_voices_writer_generic_01.py`(Family B generic writer)の
  2箇所のみ。Family X(Standard no-heading/Advanced忠実英訳)からは
  **呼ばれていない**。
- **今回のEN局所Rewriteへの再利用可否**: **改修要(第一候補として採用
  推奨)**。`locate_target_sentence`/`split_sentences`/
  `extract_point_context`/`run_diff_qa_for_accepted_rewrite`はそのまま
  流用可。新設が要るのは(a)rewrite_hint/rewrite_kindをpromptへ渡す
  attemptテンプレートの追加(既存3段階escalationとは別に、あるいは
  attempt1のテンプレートへrewrite_kind別の指示を条件分岐で追加)、
  (b)`apply_rewrites`の空文字列(削除)対応、(c)Local Rewrite後に
  Family X構造Gate(`split_family_x_article_text_v2`)を必ず再実行する
  呼び出し側ロジック(er010自体は変更せず、Self-Recovery Flow側で
  ラップする)。

### 2.2 Family X 現行EN retry(`er003_v1_n3_01_standard_a2_generate.py`
    / `er003_v1_n3_01_advanced_adaptation_generate.py`)

- **用途**: Ledger Deviation MAJOR検出時、記事全文(Standard/Advanced
  各段)をmust-fixブロック付きで1回だけ丸ごと再生成する。
- **対象範囲**: 全文(段落保持を強調する指示はpromptへの文言追加のみ、
  構造を機械的に保証するものではない)。
- **retry上限**: 1回のみ(既存コメント「1回だけmust-fixで再生成」)。
  尽きればSTOP(JAFactCheckStopError相当、または
  NG_REVIEW_REQUIRED)。
- **再検証**: `run_deviation_check(..., prior_issues=must_fix_used)`で
  「前回指摘の各項目が解消されたか」を明示的に再確認(`
  all_prior_issues_resolved`)。これは既にPrior Issues Recheckの実装例
  として存在する(Self-Recovery Flow Stage 3の「prior_issues利用」は
  ここから流用可能)。
- **今回のEN局所Rewriteへの再利用可否**: 全文再生成という設計自体は
  Self-Recovery Flowが避けたい方式(構造Gateを壊すリスク・コスト増)。
  ただし**`prior_issues`によるRecheckパターンはそのまま流用可**
  (`run_deviation_check(..., prior_issues=[...])`のインターフェースは
  既存のまま呼べる)。

### 2.3 JA側(`er019_family_x_ja_writer_o_r1_r2_01.py`)

- **既存**: Original/R2各段の「must-fixブロック付き1回だけ全文(その段)
  再生成」のみ。文単位のJA Local Rewriteは存在しない。
- **JA→EN不整合時**: English側Deviation Checkが`origin=ja_source`と
  判定したMAJORは、「案B」としてJA Original段全体を`original_must_fix`
  で差し戻し1回だけ全文再生成し、R1→R2→EN側を再度通す(カスケード全体
  再生成、局所ではない)。
- **今回のJA局所Rewriteへの再利用可否**: 既存に文単位JA Local Rewrite
  機構は無い。er010のロジック(`locate_target_sentence`/
  `split_sentences`)は正規表現が英語の文末記号(`.!?`)とキャピタル文字
  前提のため、日本語(句点`。`区切り、大文字小文字の区別なし)には
  **そのまま使えない**(新設要、ただし新設するのは「日本語版の文分割+
  対象文特定」という薄い置き換えで足り、Local Rewrite全体のretry/guard/
  差分QAの骨格はer010と同型で流用できる)。既存の「JA must-fix(全文)+
  局所指示」で代替できるかについては、対象claimが1件のみでJA全文の
  他部分に影響が及ばないと分かっている場合、全文must-fix retryでも
  実質的に対象文以外は変わらない可能性はあるが、**全文再生成は
  Advanced忠実英訳・Standard要約の再カスケード(R1→R2→EN再生成)を
  誘発しコスト・構造Gate再確認の範囲が広がる**ため、Self-Recovery Flow
  が意図する「最小差分」の目的には合わない。JA文単位Local Rewrite新設は
  正当化できるが、EN側(#2.1)の枠組みを日本語向けに薄く移植する形に
  限定すべき(独自のretry/guard設計を新たに発明しない)。

## 3. 継承すべきguard/retry/再検証(Self-Recovery Flowがそのまま引き継ぐべきもの)

1. 対象はMAJORのみ、MINORは記録のみで対象外(er010既存方針)。
2. 文単位retry上限3回+記事全体cycle上限3回という「二軸の独立カウンタ」
   設計(新しい上限値を独自に発明せず、既存`MAX_REWRITE_ATTEMPTS`/
   `MAX_REWRITE_CYCLES`と同じ根拠付けの手法を踏襲)。
3. 受理直後の差分QA(`apply_diff_qa_to_resolved_rewrite`、Fact Checker
   A' web_search + Ledger再確認)は、対象文の書き換えが新たな事実逸脱を
   生んでいないかを¥0近い追加コストで確認する既存の安全装置であり、
   Self-Recovery Flowでも同型のstep(EN側は流用、JA側は同型で新設)を
   入れるべき。
4. `evaluate_target_sentence_status`(target-sentence-matchingで隣接文
   の逸脱に巻き込まれず対象文自身の逸脱のみで受理判定、ambiguous時は
   安全側でwindow全体判定へフォールバック)は誤rejectを防ぐ既存の
   洗練されたロジックであり、そのまま流用すべき。
5. TTS Local Rewrite(#11)の「置換失敗時は原文復帰」的設計思想
   (`select_final_candidate`がNoneならHUMAN_REVIEW_LOCKED、`retts_fn`が
   OK以外ならHUMAN_REVIEW_LOCKED_RETTS_FAILEDとして人間レビューへ
   フォールバックし、silent failで出荷しない)は、EN/JA Local Rewrite
   双方の「cycle上限到達時はNG_REVIEW_REQUIRED」という既存方針と同じ
   fail-closed思想であり、Self-Recovery Flowでも維持すべき。
6. `prior_issues`を使った「前回指摘の各項目が個別に解消されたか」の
   明示的Recheck(#2.2)は、Self-Recovery Flow Stage 3の全文Recheckへ
   統合すべき(単なる新規MAJOR件数の増減比較だけでなく、対象claim自体が
   解消されたかを個別に確認できる)。

## 4. 二重実装リスク(既存設計と競合・重複しそうな点)

- **最大のリスク**: Family Xに「新しい局所Rewriteモジュール」をゼロから
  設計すると、Family B系で既にProduction稼働中のer010と機能的に
  ほぼ同一(文特定・3段階escalation・差分QA・cycle制御)のロジックが
  二重実装される。er010は既にsection抽出がheading非依存で汎用設計
  (Main Story/In One Line等どのsectionでも動作する旨がコメントに明記)
  のため、**Family Xでもimportして再利用するのが筋**であり、新規モジュール
  ではなくer010への薄い拡張(rewrite_kind対応・空文字列削除対応・
  呼び出し側でのFamily X構造Gate再確認ラッパー)で足りる可能性が高い。
- Family Xの既存「1回だけmust-fix全文retry」(#2.2)と、新設する
  「局所Rewrite」が両方存在すると、MAJOR検出時にどちらを先に試すか
  (優先順位)を明確に設計しないと、二重のretry経路が並存し呼び出し側の
  分岐が複雑化する。設計書では「局所Rewriteが第一選択、局所Rewrite
  cycle上限到達時のみ既存の全文must-fix retry(1回)にフォールバック」
  という既存Family B系のMain Story固定原則
  (CURRENT_SPEC.md該当箇所「Stage 1再生成[全文書き直し]とLocal
  Rewrite[局所修正]は区別し、後者は既存安全装置の通常動作として扱う」)
  と同型の優先順位を明記すべき。
- JA側で新設する場合も、既存の`build_must_fix_block`/
  `JAFactCheckStopError`という段単位retry機構と、新設するJA局所Rewrite
  が両方存在することになる。呼び出し順序(局所Rewriteを先に試し、
  対象文特定不能・cycle上限到達時のみ既存の段単位must-fix退避)を
  明示しないと、EN側と同様の二重経路問題が起きる。

## 5. 設計書(`docs/pm/design_open233_self_recovery_flow_01.md`)§5 改訂指示案

(本委任は当該ファイルを編集しない。次の委任者[Fable/委任_06以降]への
指示メモとして記載する。)

1. §5冒頭に「既存機構棚卸し結果」への参照(本ファイルへのリンク)を
   追加し、EN局所Rewriteは`er010_ledger_local_rewrite_09.py`を第一候補
   として拡張する方針であることを明記する(新規モジュール名を先に
   確定させない)。
2. Stage 3のEN側実装方針を「新設モジュール」から「er010拡張」へ書き換え:
   (a) `rewrite_ng_item`のREWRITE_ATTEMPT系テンプレートへ
   rewrite_kind別分岐(delete/replace_with_ledger_value/narrow_scope)を
   追加する版を新設する(既存3テンプレートは無変更のまま、Family X
   専用の新テンプレート関数として追加する案が既存互換性を壊さない)。
   (b) `apply_rewrites`の空文字列(削除)対応を明記する(既存関数の
   バグ修正として、Family B系の既存動作[削除ケースは実際には
   発生していない]に影響しないことを確認したうえで直す)。
   (c) Local Rewrite適用後、`split_family_x_article_text_v2`による
   Family X構造Gate再確認を呼び出し側(Self-Recovery Flow固有のラッパー
   関数)に追加する(er010自体は変更しない)。
   (d) 記事全体recheckに`prior_issues`(§2.2で確認したインターフェース)
   を渡し、対象claim個別の解消確認を追加する。
3. Stage 3のJA側実装方針を「既存に無い」ことを前提に、
   「er010のロジック骨格(文特定+3段階escalation+差分QA+cycle制御)を
   日本語文分割(句点`。`区切り)向けに薄く移植する」という新設範囲を
   明記する。JA→EN再整合は、対象文がJA本文の1文に閉じている場合のみ
   ローカル反映し、EN側(Standard/Advanced)の対応箇所も同一の局所Rewrite
   (§2.1改修版)で追随させる設計とし、案B(JA全文再生成カスケード)は
   JA局所Rewriteのcycle上限到達時のみのフォールバックとして位置付ける。
4. §4節で言及される優先順位を明示: 局所Rewrite(第一選択、cycle上限
   3回)→上限到達時のみ既存の段単位/全文must-fix retry(1回、
   フォールバック)→それでも解消しなければNG_REVIEW_REQUIRED
   (既存fail-closed方針を維持)。

## 6. 出力ファイル・費用

- 新規作成: `docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`
  (本ファイル)。
- 費用: ¥0(API呼び出しなし、read-only grep/read調査のみ)。
- git add/commit/pushは本委任では行わない(次の委任でcommitする)。
