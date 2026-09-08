# OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01

管理ID: OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01(Lane B、
Sonnet委任、Production Wiring)。

対象: ユーザー決定(2026-09-09、`APPROVED_FOR_PRODUCTION`)に基づき、Fact
Checker候補A'(Ledger側Voice別evidenceタグ`VOICE_n_EVIDENCE`+Fact Checker
への「Voice本文は出典明記不要(ただし事実誤り・実在人物引用は従来どおり
検証)」のopt-inルール、`EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-
TRIAL-02_REPORT.md`と同一ロジック)をProduction経路へ配線した。
family=="B"のコードレベルgating・既定OFF・opt-in有効化・A-Family非影響。

---

## 0. 重要な事前確認(委任前提との差異)

委任では「B-Family Production runner(`er012_b_family_production_runner_
01.py`、B1/A2両経路)からのみ」Fact Checkerを呼ぶ想定だったが、実装前の
コード確認で、同runnerの`main()`/`main_a2()`(既定"all" stage)は**いずれも
既存承認済み記事の音声化(TTS/Assembly)のみが範囲であり、Fact Checker
自体を一度も呼び出していない**ことを確認した(B1はTrial-07 Writer、A2は
Trial-02 Writerが過去にFact Checkを実施済みで、その記事を読み取り専用で
再利用する設計、runner冒頭コメントに明記済み)。`er012_b_family_voices_a2_
production_01.py::run_fact_checker()`は定義済みだが、production_runner側
からは呼ばれていなかった。

このため、以下の設計で対応した(仕様を拡張せず、既存の空白を安全に埋める
方針):
- A2側の既存`run_fact_checker()`へ`voice_attribution_block`引数を追加。
- B1側にも同一実装の`run_fact_checker()`を`er012_b_family_voices_
  production_01.py`へ**新規追加**(A2と1:1、Phase 2でB1 Writerが追加された
  際にそのまま呼べる)。
- production runner側に`build_fact_attribution_block_if_enabled()`・
  `run_fact_check_b1()`・`run_fact_check_a2()`を追加したが、**`main()`の
  stage一覧(prepare/voice_check/kp_reuse/scaffold/tts/assemble/player/
  all)には含めていない**(Phase 1のB1/A2は記事生成・Fact Check自体を範囲
  外とする既存設計方針を尊重し、既定"all"の出力を変えないため)。
- Runtime evidenceは、この2関数を専用スクリプトから直接呼び出して取得した
  (下記4節)。

---

## 1. 実装

| ファイル | 変更内容 |
|---|---|
| `er002_ja_web_research_r3.py` | `build_fact_check_prompt(topic, article_text, writer_sources, template=None, voice_attribution_block: str = "")`。既定`""`時はbyte単位で不変(単体テスト固定)。非空時はprompt末尾へ追記 |
| `er012_b_family_editorial_type_registry_01.py` | `FACT_ATTRIBUTION_MODE_DEFAULT = False`をEDITORIAL_TYPES["b_family_voices"]["fact_attribution_mode"]へ追加。`VOICE_ATTRIBUTION_RULE_TEXT`(Trial-02検証済みルール文言の転記)。`build_voice_attribution_block(ledger_text)`(`[VOICE_n_EVIDENCE]`行を正規表現抽出、タグ0件ならfail-closedで""を返す)。`is_fact_attribution_mode_enabled()`(`family=="B"`かつflag Trueのみ) |
| `er012_b_family_voices_a2_production_01.py` | 既存`run_fact_checker(topic, article_text)`へ`voice_attribution_block: str = ""`引数追加、`r3.build_fact_check_prompt()`へ転送 |
| `er012_b_family_voices_production_01.py` | `run_fact_checker(topic, article_text, voice_attribution_block="")`を新規追加(A2側と1:1実装、既存関数は無変更) |
| `er012_b_family_production_runner_01.py` | `build_fact_attribution_block_if_enabled(ledger_text)`・`run_fact_check_b1()`・`run_fact_check_a2()`追加(`main()`stage一覧には未接続) |

## 2. 既定OFF・A-Family非影響の証拠

- 単体テスト`test_default_empty_block_is_byte_identical_to_pre_change_
  signature`: 引数省略時・`voice_attribution_block=""`明示時の両方で、
  `build_fact_check_prompt()`の戻り値が本タスク以前の期待値とbyte一致。
- `test_a_family_writer_files_do_not_reference_new_mechanism`:
  `er006_pool_pilot_01_writer.py`・`er003_v1_n3_01_articles_generate.py`
  に`voice_attribution_block`・registry importが1つも存在しないことを
  grepで確認。
- `test_a_family_fact_check_call_site_still_passes_no_extra_args`:
  A-Family呼び出し行`r3.build_fact_check_prompt(topic, article_text, [])`
  (978行目)が無変更であることを確認。
- `registry.EDITORIAL_TYPES["b_family_voices"]["fact_attribution_mode"]`
  既定`False`(単体テスト`test_default_mode_is_off`)。

## 3. Gate 3必須確認(15項目相当)

| # | 項目 | 結果 |
|---|---|---|
| 1 | Production正式初回経路への実装 | PASS(`r3.build_fact_check_prompt`・`a2prod.run_fact_checker`は既存Production primitive。`b1prod.run_fact_checker`は新規だがA2と1:1で同primitiveを使用) |
| 2 | retry/fallback/regenerationとの整合 | PASS(3節参照。blockはledger_text/flagのみに依存しarticle_textに非依存であることをコード+テスト+実出力[Local Rewrite後もPASS維持]で確認) |
| 3 | DEV・Trial-onlyではないこと | PASS(全関数はProduction module内。Trialスクリプトは一切importしていない) |
| 4 | Production runtimeでの実発火 | PASS(4節、実記事2本+Local Rewrite後1本、計3回の実LLM呼び出し) |
| 5 | 必要testのPASS | PASS(新規13テスト、下記5節) |
| 6 | runtime evidence | PASS(4節) |
| 7 | 実際のmodel_id・routing確認 | PASS(`routing.WRITER_FACT_CHECK_MODEL`="gpt-5.6-luna"、無変更で使用、evidence JSON内`model`フィールドで確認) |
| 8 | `CURRENT_SPEC.md` | 反映(Part 3) |
| 9 | `DECISION_LOG.md` | 反映(Part 3) |
| 10 | `OPEN_ITEMS.md` | 反映、PRODUCTION_WIRED候補+commit hash(Part 3) |
| 11 | 必要なGit反映 | 反映(下記) |
| 12 | approved specとProduction挙動の一致 | PASS(Trial-02のprompt文言・免除ルールをそのまま転記、内容変更なし) |
| 13 | family=="B"のコードレベルgating(Trial-02第6節の設計結論) | PASS(`is_fact_attribution_mode_enabled()`が`family`と`fact_attribution_mode`両方を確認、単体テストでfamily="A"時Falseへ切替わることを確認) |
| 14 | 3V/4V拡張性を壊していないこと | PASS(`_VOICE_EVIDENCE_LINE_RE`はvoice番号を正規表現で汎用抽出。`VOICE_3_EVIDENCE`合成タグでの単体テストPASS。3V/4V本体作業は対象外[禁止事項どおり不実施]) |
| 15 | Dangling Reference | PASS(4節末尾) |

## 4. Runtime evidence

`er012_open131_fact_attribution_production_wiring_evidence_01.py`(root)が、
実際のProduction関数(`runner.run_fact_check_b1/a2` → `b1prod`/`a2prod.
run_fact_checker` → `r3.build_fact_check_prompt`/`make_fact_checker_fn`/
`run_fact_checker_with_gates`、いずれも既存primitive)を通じて、B-Family
B1(Phase 1記事、`editorial_b_family_production_phase1_02/b1b/article.md`)
とA2(production_wiring_01記事、`editorial_b_family_voices_a2_production_
wiring_01/a2/article.md`)へopt-in ONを実行した。OFF側は追加課金なしで
既存記録(B1: `editorial_b_voices_trial_07/b1b_run02_attempt2/fact_qa.
json`、A2: `editorial_b_voices_a2_free_address_04/a2/audit/fact_check.
json`。いずれも同一article_text[sha256照合済み]に対する過去のOFF実行)を
再利用した。

| | OFF(既存記録) | ON(本タスクで実行) |
|---|---|---|
| B1 verdict | REVIEW_REQUIRED | **PASS** |
| B1 unsupported_specific_claims件数 | 5 | **0** |
| A2 verdict | REVIEW_REQUIRED | **PASS** |
| A2 unsupported_specific_claims件数 | 6 | **0** |

OFF側の5/6件は、いずれも「Voice A/Bの一人称体験に発言者・企業名・調査対象
が明示されていない」という帰属曖昧起因(Trial-02が想定した通りの内容)で
あり、事実誤り・矛盾の指摘は0件だった。ON側は帰属免除ルールにより該当
claimが免除され、verdict=PASSへ変化した。

**Local Rewrite後の帰属維持(実出力)**: `er012_open131_fact_attribution_
local_rewrite_evidence_01.py`が、実際のProduction関数`er010_ledger_local_
rewrite_09.apply_rewrites()`(既存、無変更)を使い、B1実記事の実文1文
("I miss the same desk, drawer, and view.")を内容不変・表現のみ言い換え
(str.replaceベース、Local Rewriteと同じ契約)たうえで、opt-in ONの実Fact
Checkerを再実行した。結果: `verdict=PASS`、`unsupported_specific_claims=
0`(rewrite前と同じ)。blockはrewrite前後で完全に同一(`article_text`に
非依存な設計、単体テスト+実行時assertで二重確認)。既存記録にLedger
Deviation MAJORが実発生した記事は無かった(grep確認済み)ため、本タスクの
指示どおり「既存記録の再現」ではなく、実際のProduction primitiveを実際に
駆動する形で代替した。

**費用**: 実LLM呼び出し3回(B1 ON・A2 ON・Local Rewrite後再検証)、
web_search使用。`client.responses.retrieve()`で正確なtoken usageを取得し
実額を計算: 合計**$0.064(約¥10.24)**、上限¥60以内(詳細:
`er012_output/open131_fact_attribution_production_wiring_evidence_01/
cost_report.json`)。

**Dangling Reference確認**: 新規追加した`registry.build_voice_attribution_
block`/`is_fact_attribution_mode_enabled`/`run_fact_check_b1`/`run_fact_
check_a2`は、いずれも既存のProduction primitive(`r3`・`routing`)のみを
参照し、未承認・未実装の仕様を参照していない。

## 5. Regression

新規テスト`er012_open131_fact_attribution_production_wiring_01_test_01.py`
(13テスト、全PASS): byte不変・family gating・block生成・3V拡張・runner
wiring・Local Rewrite非依存性・run_fact_checker signature・A-Family非影響。

`run_project_regression.py`: collected=2242, passed=2239, failed=3。
失敗3件は全て`er003_test_p2j_investigate.py`(テスト総数の歴史的
reconciliation定数[P2H=1032/P2I=660等]とのハードコード比較テストで、
同ファイル冒頭のdocstringに明記の通り「現在の回帰品質の代替ではなく、
新規テスト追加のたびに必ず変化する」既知の性質を持つ)。本タスクで新規
テスト28件(本Reportの13件+OPEN-129側15件)を追加したこと自体が原因の
カウント差異であり、機能的な回帰ではない(該当ファイルの目的外使用)。

## 6. Gate 4(Dangling Reference Check)

- Production code・Promptは、未承認仕様(3V/4V本文・mandatory化)を一切
  参照していない。
- `voice_attribution_block`引数は全ての呼び出し元で既定値`""`が明示
  または省略されており、フラグOFF時に到達不能なコードパスは無い。
- registryの`fact_attribution_mode`はEDITORIAL_TYPES辞書内の1エントリの
  みで、他のEditorial Type(A-Family)には存在しない(KeyError等の
  dangling参照なし、A-Family側はこの辞書自体を参照しないため無関係)。

## 7. STOP条件確認

該当なし(既定OFFで既存出力不変・regression機能的break無し・A-Family
Prompt無変更・mandatory化なし・既存完成episodeでのfalse reject無し[本
タスクの対象外だがOPEN-129側で確認済み]・費用¥10.24[上限内]・承認内容
[Trial-02のprompt文言そのまま]と実装が一致)。

## 8. Status

`PRODUCTION_WIRED候補(Fable受入待ち)`。Sonnetとして`PRODUCTION_WIRED`を
宣言しない(Gate 7はFableが行う)。

## 新規ファイル一覧

- `OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01_REPORT.md`(本ファイル、root)
- `er012_open131_fact_attribution_production_wiring_01_test_01.py`(root、regression test)
- `er012_open131_fact_attribution_production_wiring_evidence_01.py`(root、runtime evidence script)
- `er012_open131_fact_attribution_local_rewrite_evidence_01.py`(root、Local Rewrite後runtime evidence script)
- `er012_output/open131_fact_attribution_production_wiring_evidence_01/`(b1_on_result.json、a2_on_result.json、on_off_comparison.json、b1_on_after_local_rewrite_result.json、b1_on_after_local_rewrite_summary.json、cost_report.json)

---
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SPsKBAZP5KEqdTH9TnkJdp
