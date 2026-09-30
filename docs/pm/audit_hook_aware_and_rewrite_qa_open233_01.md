# Hook-aware仕様 再監査 / Rewrite後QA資産 再利用棚卸し(OPEN-233 委任_14 作業A)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_14、iteration6)
作成日: 2026-09-30
性質: read-only調査(A-1はgrep+既存jsonの机上判定、A-2はgrep+既存doc突合)。
API呼び出しなし、¥0。Production非接続・コード変更なし。

## A-1. Hook-aware仕様の再監査

### A-1-1. Production仕様の正確な範囲(HOOK_CLAUSE)

`er003_v1_en_direct_vfl_01_generate.py` L564-609(`ER-010-NO9-PRODUCTION-
INTEGRATION-FINAL-09`で正式採用)。要旨:

- 緩和対象は **changed_scope と changed_comparison の2種類のみ**。
- 緩和条件は以下すべてを満たす一文であること: (a) rhetorical
  question・語りかけ・場面描写・attention grabberとして機能している、
  (b) Ledger内で既に確認されている状況・選択肢を会話的に言い換えている
  だけである、(c) 新しい具体的Factを追加していない。
- 上記2種類以外の **8種類**(changed_fact/changed_causality/
  changed_certainty/changed_number/changed_actor/changed_negation/
  changed_time/unsupported_new_claim)は、Hookかどうかに関わらず常時通常
  判定する。「Hookだから何を書いてもよいわけではない」と明記。
- `hook_aware`は既定`False`。呼び出し側が明示的に`hook_aware=True`を渡した
  場合のみ有効(`run_deviation_check`のkeyword引数)。

### A-1-2. hook_aware=Trueの呼び出し元(実配線状況)

`hook_aware=True`をgrepで確認した実際の呼び出し元は
`er003_v1_n3_01_articles_generate.py`(N3-01直接生成、Family B系)のみ。
`er012_e_family_entertainment_two_level_runner_01.py`(Family X/Eの
Standard/Advanced生成経路)からの呼び出しでは`hook_aware`引数を渡して
おらず、既定`False`のまま(未配線)。つまり **Family X(Hormuz/Meta記事が
属する経路)自体が現行ProductionでHook-awareを使っていない**。

OPEN-233 Self-Recovery/Checker系Trial(`er051_open233_checker_trial_variant_
01.run_trial_deviation_check`、Self-Recovery Flowの`stage1_fresh`/
`stage1_union_screen`が呼ぶ)も同様に`hook_aware`引数を渡しておらず、
`False`のまま(grep確認: `er051_open233_checker_trial_variant_01.py`内に
`hook_aware`という文字列自体が存在しない)。

**結論**: Family X(Hormuz/Meta)記事は、Production・Trialのいずれの経路でも
Hook-aware判定を受けていない。これは意図的な未配線ではなく、単に
「Family B向けに作られたHook-aware判定を、Family X/E系の呼び出しへ
配線し忘れている」状態に近い(N3-01直接生成はFamily B系のみが使う経路)。

### A-1-3. Meta neg1(ユーザー指摘例)の机上判定

REPORT §14実測データ(`er052_output/open233_self_recovery_flow_runner_01_
iter5/instances_s1/neg1_meta_b3prod_a2.json`)を読むと、neg1の実際に
BLOCKINGとなったclaimは以下:

> "A call seemed to come from an AI agent. But as the conversation went
> on, the voice was not AI at all. It was a person. Meta had run a test
> that caused exactly this surprise."

このclaimのStage1判定フラグは **changed_fact=true, changed_certainty=true,
unsupported_new_claim=true**(issue: 「記事は受信者が通話中にAIでなく
人間だと気づいたという体験を提示し、そのテストが驚きを引き起こしたと
述べているが、Ledgerは契約労働者が一部のMuse通話に応対したことは確認
しているが、受信者がこの『気づき』を体験したことまでは確認していない」)。
**changed_scope/changed_comparisonのいずれにも該当していない。**

**重要な監査結論(ユーザー例への当てはめ)**: 現行Production HOOK_CLAUSE
(changed_scope/changed_comparisonの2種類のみ緩和)を、たとえ
`hook_aware=True`でこのclaimへ適用したとしても、**neg1は緩和対象外の
8種類[changed_fact/changed_certainty/unsupported_new_claim]に該当して
おり、BLOCKINGのまま変わらなかったはずである**。ユーザーが「Meta例は
Rewrite不要だった可能性が高い」と判断した直感自体は編集判断として理解
できるが、「Hook-aware判定を適用していれば防げていた」という前提は
Production HOOK_CLAUSEの実際の緩和範囲とは一致しない。

これは2026-09-30ユーザー新方針item2で示された新基準「確認済みFactから
自然に導ける演出・解釈は許容、新しい具体的Factの発明はNG」を、
Production HOOK_CLAUSEよりも**広い**基準として新設する必要があることを
示す(既存Production仕様をそのまま拡張適用しても解決しない)。ただし
「受信者が驚いたという体験」を新しい具体的Fact(個別の主観的事実)と
見るか、Ledgerの一般的傾向の自然な言い換えと見るかは編集判断であり、
本委任ではFableへ判定材料として提示するにとどめ、独自にBLOCKING/QUALITY
を確定させない(§2 Fable判定は「changed_scope/changed_comparisonのみ緩和」
という狭い範囲を明示的に指定しており、それを超える緩和はUSER_DECISION_
REQUIRED相当の仕様拡大に当たるため)。

### A-1-4. 既知のDangling/非整合(Opus L2 #1指摘の確認)

`docs/pm/opus_l2_review_open233_checker_trial_01.md` L221:
`HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE`は`DEVIATION_PROMPT_TEMPLATE.replace(
"【判定ルール】", HOOK_CLAUSE + ...)`で生成されるが、V4-Aは「changed_number/
actor/negation/comparisonは該当すれば他カテゴリと重複してでも必ずtrueに
する」と指示しており、changed_comparisonについて**正面から矛盾する**
(Opus所見、未解消のまま現在に至る)。

**OPEN-233 Self-Recovery Flow独自の新たな非整合(本委任で発見)**: 上記
Production側の矛盾とは別に、Self-Recovery Flowのdeterministic floor
(`FLOOR_FLAGS`)は`changed_comparison`を含む。これは「Stage1がchanged_
comparison=trueと判定したclaimは、Stage2 LLMの材料性判定に関わらず無条件
でBLOCKINGへ強制する」という既存のfail-closed安全装置である。Hook-aware
緩和をchanged_comparisonにも適用しようとすると、この既存floor(Safety
側の安全装置)を弱めることになり、governance「既存の安全装置を独自判断で
回避・無効化しない」に抵触する。

### A-1-5. 本委任での統合方針(§2 Fable判定の実装、意図的な縮小を含む)

- Stage2の入力に`section_type`(title/hook/in_one_line/body)を決定論的に
  付与する(`detect_claim_section_type`、¥0、既存`locate_best_sentence`
  を再利用)。
- Hook-aware post-hoc downgrade(`apply_hook_aware_downgrade`)を
  **changed_scope単独発火時のみ**に限定して実装した(§2原案は
  changed_scope/changed_comparisonの2種類を指定していたが、
  changed_comparisonはSelf-Recovery Flow自身のdeterministic floorに
  含まれる安全装置であり、独自判断での緩和はgovernance違反となるため、
  本委任ではchanged_scopeのみへ意図的に縮小した)。
- 判定はLLMのHook解釈に依存しない決定論的post-hoc方式とした
  (Stage2 promptそのものは変更していない)。理由: (1) 新しいSafety関連の
  判断をLLMの自由記述解釈に委ねるとfail-closedの再現性が下がる、(2) 既存
  floor/2-of-2/cite-or-releaseと同じ「決定論的post-hoc」アーキテクチャに
  統一した方が監査・regression testが容易、(3) API呼び出しを増やさず¥0で
  実装できる。
- **本統合はMeta neg1のケースを解決しない**(§A-1-3のとおり、neg1の実際の
  flagはchanged_scope単独ではない)。changed_certainty/unsupported_new_
  claimを含むより広い緩和が必要かどうかは、Safety側の誤降格リスクを
  伴う判断であり、本委任の範囲を超える。Fable/ユーザーへの提示事項として
  §14以降のiteration6報告に明記する。

## A-2. Rewrite後QA資産の再利用棚卸し

`docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`(委任_05、
既存)が既に機構棚卸しを行っている。本節はそれを踏まえ、Production
`er010_ledger_local_rewrite_09.py`のRewrite後QA要素が、OPEN-233
Self-Recovery Flow(`er052_open233_self_recovery_flow_runner_01.py`)側で
どこまで再利用されているかを表にする。

| Production QA要素(er010) | 内容 | OPEN-233での再利用状況 |
|---|---|---|
| 修正対象文+前後1文のwindow(`extract_point_context`) | 対象文とその前後1文だけを切り出してQAに渡す、局所性を保つ設計 | **未使用**。OPEN-233は`run_recheck`で常に記事全文を再投入する(`prior_issues`で対象claimの解消有無だけを個別確認する設計、windowではなく全文を毎回使う点が異なる)。全文再投入は「隣接claimへの巻き込みリスクは低いがコストが高い」という異なるtrade-offを選んでいる(既存設計、本委任では変更しない) |
| Fact Checker A'(web_search、`run_diff_qa_for_accepted_rewrite`) | Rewrite受理直後に対象文+前後1文をFact Checker A'(web検索込み)へ再投入し、新たな事実誤りを生んでいないか確認 | **未使用**(grep確認: `er052_open233_self_recovery_flow_runner_01.py`に`fact_check`/`r3\.`/`web_search`の参照なし)。web_search呼び出しはコスト・所要時間が不確定なため、本委任のGuardrail(¥65)内では新規追加を見送った。Phase2で検討すべき項目として記録する(抜け落ちとして今回は埋めない、理由: 予算超過リスク) |
| Ledger Deviation Checker再確認(`vfl01.run_deviation_check(..., hook_aware=True)`、window単位) | 対象文+前後1文のwindowだけをLedger Checkerへ再投入 | **部分的に代替あり**。OPEN-233の`run_recheck`は記事全文でLedger Checker相当(V4A)を再実行しており、windowではなくより広い(全文)チェックを行っている。対象文個別の解消確認は`prior_issues`/`all_prior_issues_resolved`で実施(§A-2表の次項) |
| `evaluate_target_sentence_status`(対象文自身の逸脱か、隣接文の逸脱かを分離判定) | 対象文と前後1文それぞれの逸脱を分離し、対象文自身が解消していれば隣接文の残存逸脱でRewriteをblockしない | **未使用、今回埋めなかった抜け落ち**。OPEN-233の`run_recheck`は全文recheckの`overall_status`/`all_prior_issues_resolved`のみを見ており、対象文と前後文の問題を機械的に分離していない。ただし全文recheckは対象文以外の逸脱も含めて`LEDGER_DEVIATION`を返しうるため、Family Xのようにclaim単位で個別に「このclaimは解消したがこの記事には別の未解消逸脱がある」ケースを区別できない場合がある。cite-or-release(`remaining_sentence`必須化、委任_13)は「未解消の根拠となる文」を機械検証する点で類似の目的を部分的にカバーしているが、対象文/隣接文の分離そのものではない。本委任では新規実装を見送った(理由: 全文recheckアーキテクチャ自体の変更が必要でスコープが大きい、Phase2課題として記録) |
| `apply_diff_qa_to_resolved_rewrite`のblocking条件(FAIL/LEDGER_DEVIATIONのみ不受理、REVIEW_REQUIREDは記録のみ通過) | 機械的な受理/不受理の閾値 | OPEN-233は`recheck_confirm`のcite-or-releaseで同種の閾値思想(機械検証できない未解消は解消扱いへ上書き)を独自に実装済み(委任_13)。系統は異なるが「fail-closedを緩めない厳格化」という設計思想は共通 |
| `MAX_REWRITE_ATTEMPTS=3`(文単位)+`MAX_REWRITE_CYCLES=3`(記事全体)の二軸retry | 段階的escalation(3段階)+記事全体cycle上限 | **部分的に再利用・本委任で拡張**。OPEN-233は記事全体cycle上限(`MAX_CYCLES`/`HARD_MAX_CYCLES`)を既存踏襲。文単位のescalation段数は、本委任(B-3)で最小変更ラダー(単語・接続詞→1文→段落→全文の4水準)へ拡張した(既存の「3段階escalation」という設計原則[小さい範囲から順に試す]を踏襲しつつ、水準の中身をユーザー新方針item3の6段ラダーに合わせて再設計) |

### A-2まとめ(そのまま使える/拡張すべき/抜け落ち)

- **そのまま使える(既に使っている)**: 記事全体cycle上限、fail-closed
  retry上限到達時のSTAGE4_ESCALATION、prior_issuesによる個別解消確認。
- **拡張すべき(本委任で実施)**: 文単位escalationの段数(3段階→最小変更
  ラダー4水準、B-3)。
- **抜け落ち(今回は埋めなかった、理由付き)**: (1) Fact Checker A'
  web_searchによる差分QA(予算・所要時間の不確定性のため見送り、Phase2
  課題)、(2) `evaluate_target_sentence_status`型の対象文/隣接文分離判定
  (全文recheckアーキテクチャの変更が必要でスコープが大きいため見送り、
  Phase2課題)。

## 3. 費用・変更範囲

- 費用: ¥0(API呼び出しなし、read-only grep/JSON参照のみ)。
- 変更ファイル: 本ファイルの新規作成のみ。Production/既存Trialコードは
  無変更。
