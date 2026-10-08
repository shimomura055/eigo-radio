# DESIGN_E2E_01: FACTLOCK-ASTRA-E2E-TRIAL-01 設計書(委任_01、2026-10-09)

性質: Trial/DEV。到達上限Status=`DESIGN_READY`(実行Go未)。本書作成時点のAPI生成支出=¥0、Production変更なし、既存コード・Prompt・CURRENT_SPEC.md・OPEN_ITEMS.md無編集。`APPROVED_FOR_PRODUCTION`ではなく、E2Eの結果も`MEASURED`止まりでProduction採用は人間ユーザーのみ承認する。
本書の数値は、出典を併記したものだけを「実測/確認済み」とし、それ以外は「見積」「推定」「未確認」と明記する。USD/JPY=160(astra単価正本と同じ)。

## 0. ユーザー決定(2026-10-09、DECISION_LOGに記録)
1. 10記事 / TTS 2本 / 予算上限¥1,000(途中停止を避けるため¥700から引き上げ)。
2. Astra=Standard同期(Flexは別評価、Batchは対象外)。
3. M2は見送り(OFF維持)。
4. 旧4テーマ(META/ホルムズ/宇宙兵器/ミニバッグ)+新6テーマ(候補提示→ユーザー選定)、全記事で旧仕様腕を併走(paired)。
5. 設計書作成へGo(「OKです。開始してください。」)。**実行(API支出)はGo未**。

## 1. 目的・評価対象・指標・比較対象

### 1-1. 評価対象と比較対象
| 評価対象 | 何を見るか | 比較(新=新仕様腕 / 旧=旧仕様腕) |
|---|---|---|
| (1) Writer変更 | Fact Lock R0[Luna]+Astra R1→R2[系列X]が、旧Production Writer(Luna R0→R1→R2)より日本語記事のFact品質を良化するか(面白さは副指標) | 同一台帳・同一B3から生成した新R2 対 旧R2(同時にfresh生成) |
| (2) 翻訳仕様変更(M1/M3) | 要約へのJA+Ledger入力と要約のみ再生成(M1)、changed_actor候補の再分類保護(M3)が、EN段の重大/軽微NG・STOP率を良化するか | 新EN(M1/M3 ON) 対 旧EN(全OFF)。**JA本文が腕で異なるため(1)と交絡する。分離は3節のテレメトリと8節論点1** |
| (3) Checker | 重大/軽微の件数、Rewrite率、Human Review率、費用 | 新腕 対 旧腕(同一Checker構成: 承認スイッチ`OPEN233_APPROVED_FLOW_SWITCHES`、`FLOOR_MODE=number_only`。M3だけ新腕のみON) |

旧仕様腕=「現Production経路」: 同一台帳・同一B3から`er019_family_x_entertainment_production_runner_01.py`のWriter(`jaw.run_ja_writer_o_r1_r2`、gpt-6-luna)→EN(M1/M2/M3全OFF)→Checker。

旧4テーマ(META/ホルムズ/宇宙兵器/ミニバッグ)は、上記の同時fresh旧腕に加えて**過去の凍結出力とも並記**する(参考のみ、条件が違うため判定には使わない)。
- Checker: `er052_output/open233_prod_e2e_02/`(REPORT §81の新仕様9 run。meta_run03_advanced/standard、hormuz_run03_advanced/standard等。実測合計¥31.519、平均¥3.502/run、平均345.5秒/run[`e2e_summary_02.json`])。旧仕様の9 run(frozen)は§81-2〜§81-5の「旧9 run」列。
- Writer: Fact Lock v1の24本(`er052_output/factlock_writer_trial_01/runs/`、`RESULT.md`)、all6/baselineの44本(`er052_output/all6_writer_redesign_necessity_01/runs/`)、Astra Revise matrix(`astra_revise_matrix_01/02`、REPORT §107・§108)。

### 1-2. 指標定義(REPORT §81の集計表と同じ行立て)
集計単位=「1記事の1腕」。Advanced(Family X忠実英訳)とStandard(A2)は別のChecker runとして数え、記事×腕あたり2 run、全体で最大40 run(10記事×2腕×2レベル)。表は§81-2〜§81-5と同形で、新腕/旧腕の2列+差分列。

| 区分 | 指標 | 定義 | 定義元 |
|---|---|---|---|
| A | Checker初回候補 | AI判定の候補(延べ)/うち真に問題(Y)・不要(N)・判断不能/機械判定の候補/重複除外後の総候補/再分類で除外されたclaim数 | §81-2 |
| B | 後段判定 | Stage 2のAI 重大/軽微/問題なし、事後評価の真に重大・不要に重大・真に重大なのに軽微/問題なし、機械判定(数字のみ)の発火と重複、S1 second opinionのBLOCKING化 | §81-3 |
| C | Rewrite率 | Rewrite発生件数/発生run数(分母=Checker run数)、必要/不要の別、再修正が必要だった件数 | §81-4 |
| D | Human Review率 | 出口BLOCKINGありでHuman Review/STAGE4へ到達したrun数 ÷ Checker run数 | §81-4 |
| E | Safety・Cost | 真の重大Fact見逃し(最終本文に未修正で残存)、重大Fact検出(最終本文までに修正)、run別費用・合計・平均、Checker/後段/Rewrite別費用 | §81-5 |
| F | 重大/軽微(最終記事) | 最終EN本文・最終JA本文に残る重大/軽微の件数(記事あたり)。盲検ラベル(7節)による。重大/軽微の線引きはPREREGISTRATION_01.mdで固定 | PREREGISTRATION_01.md |
| G | JA Writer(1) | JA R2のFC(Luna、全台帳、`run_deviation_check(hook_aware=False, include_related_fact_id=True)`)MAJOR/MINOR、決定論指標(字数・段落・問い・記号Gate・台帳外数値)、盲検ラベルの重大/軽微 | astra_revise_matrix_02/DESIGN.md「評価」節 |
| H | EN段(2) | EN deviation check初回のMAJOR数(由来translation/ja_source別、要約/本文別)、EN STOP率(M1後を含む)、M1発火数と解決率、盲検ラベルのEN由来NG | OPEN-243 ANALYSIS_01 §3 |
| I | M3(2) | 保護されたclaim件数、その後のStage 2判定(BLOCKING/QUALITY/ACCEPTABLE)、Rewrite誘発件数と必要/不要 | RESULTS_M123.md V3 |
| J | 副指標 | 面白さ(新R2対旧R2のpairwise、LLM判定+人間確認2〜3記事)、字数、所要時間、記号Gate | RESULT.md §1〜§2 |

## 2. 処理フロー(1記事)

```
[共有: テーマ1件]
 旧4テーマ: 凍結済み台帳・B3を共有dirへコピー(sha256照合、下表)。research/B3のAPI呼び出しなし
 新6テーマ: er019 runnerの run_research_and_ledger → run_storyline_b3 (web_searchあり、1テーマ1回、両腕で共有)
 新腕だけ: 注記版brief(【事実N】+【中核数値】/【周辺数値】)を作成(前提作業h)
[旧仕様腕]  共有ledger + 原本B3(注記なし)
            er019 runner --stage all (既存の再利用分岐: ledger/selected_brief.mdが既にあれば再生成しない)
            Luna R0→R1→R2(現Production、FC+must-fix1回+記号Gate込み) → EN Advanced+Standard(M1/M2/M3全OFF) → Checker
[新仕様腕]  共有ledger + 注記版brief
 W1 Fact Lock R0: Production関数 jaw.run_ja_writer_o_r1_r2 のOriginal段(R0_PROMPT+Fact Lock R0ブロック、gpt-6-luna、
    JA FC Full Ledger、must-fix1回→STOP、記号Gate)をR1直前で打切り(astra_revise_matrix_02/tools/gen_r0_small_bag.py と同手順)
    → タグ照合(測定のみ) → strip_tags
 W2 Astra R1: model=gpt-6-astra、Standard同期(service_tier指定なし=既定)、reasoning={"effort":"high"}、previous_response_id不使用、
    developer/systemメッセージなし。userメッセージ逐語(系列X):
    "以下の記事:\n\n{前段本文}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。"
    (出典: astra_revise_matrix_01/02 の DESIGN.md、run_matrix2.py USER_TMPL。800〜1000字はソフトキャップ=字数を理由にSTOP/再生成しない)
    → JA FC(Luna、全台帳)
 W3 Astra R2: 入力=R1の生出力(Markdown除去前、matrixと同じ)。同条件 → JA FC
 W4 後処理(API無し・決定論): strip_markdown(P1) → 「……」「…」を文末は「。」文中は「、」へ(normalize_ellipsis_pause_ja)
    → 「——」を「、」へ(dash_to_comma) → 記号Gate(detect_prohibited_symbols、記録のみ)
    最終JAを ja_writer/revision2.md として保存(= er019 runnerの「既存JA記事(R2)再利用」分岐に乗せる)
 W5 EN: efam.run_writer_stage (advanced → standard)。OPEN243_M1=1(Advanced枝のみ有効)。
    storyline_line / selected_fact_brief_text = None を渡してJA再確認(案B)を無効化
    (案BはProduction Luna Writerで本文を再生成するため、新腕に旧Writerが混入するのを防ぐ。
     ja_source MAJORは JA_RECHECK_REQUIRED としてSTOP記録=結果の一部。8節論点2)
 W6 Checker(Advanced/Standard各1 run): runner.apply_open233_approved_flow_switches() + FLOOR_MODE=number_only確認
    + OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor (M3)
TTS: 結果確認後に選ぶ2記事のみ、Standard同期(TTS_EXECUTION_MODE=STANDARD、ASR突合込み)。対象はFable/ユーザーが選定。TTS入口スクリプトは未特定(前提作業h2)
```

確認済み根拠(コード): er019 runnerは既存の`research_ledger/verified_fact_ledger.txt`(`run_research_and_ledger`先頭)・`storyline_b3/selected_brief.md`+`fact_selection_evidence.json`・`ja_writer/revision2.md`が揃っていれば再生成せず再利用する(`er019_family_x_entertainment_production_runner_01.py` L91-98、`main`のstoryline/writer再利用分岐)。`efam.run_writer_stage`は`storyline_line`か`selected_fact_brief_text`が`None`のとき案Bを行わず`JARecheckRequiredError`をそのまま送出する(`er012_e_family_entertainment_two_level_runner_01.py` L737-753)。

凍結入力(共有dirへコピー。sha256先頭16桁は本書作成時に`sha256sum`で実測、コピー後に再照合する):
| テーマ | 台帳 | 旧腕B3(原本・注記なし) | 新腕B3(注記版) |
|---|---|---|---|
| META(b2) | `er052_output/factlock_writer_trial_01/runs/meta/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt` ea0ce587e605beea | `er052_output/open233_b3_trial_01/runs/meta/nb/V0/b2/storyline_b3/selected_brief.md` 055b1385b6db97e9 | `er052_output/factlock_writer_trial_01/briefs/meta/b2/selected_brief_factlock.md` d5a6a14c095b5f16(数値0・事実3) |
| ホルムズ(b2) | 同`runs/hormuz/control/b2__factlock__r1/...` 9bd6834e68e7e437 | `open233_b3_trial_01/runs/hormuz/nb/V0/b2/storyline_b3/selected_brief.md` e1f892dffb7ff3cf | `briefs/hormuz/b2/selected_brief_factlock.md` 4ed19d3787d2850c(中核3・周辺4) |
| 宇宙兵器(b2) | 同`runs/space_weapons/control/b2__factlock__r1/...` f172a253f24b99d6 | `open233_b3_trial_01/runs/space_weapons/nb/V0/b2/storyline_b3/selected_brief.md` e29575ffe46ba132 | `briefs/space_weapons/b2/selected_brief_factlock.md` a518cf267fa3be42(中核3・周辺2) |
| ミニバッグ | `er052_output/gpt6_wiring_e2e_01/run_02/research_ledger/verified_fact_ledger.txt` 0cc8ca3f2e73a1f9 | `.../run_02/storyline_b3/selected_brief.md` 55bb9ba3ef209214 | `astra_revise_matrix_02/inputs/small_bag/selected_brief_factlock.md` 0e4fe52ec62bd847 |
META・ホルムズの台帳は`open233_b3_trial_01`側の同名ファイルとsha256一致を確認済み(ea0ce587.../9bd6834e...)。宇宙兵器の`open233_b3_trial_01`側台帳との一致は未確認(実行前に照合)。b2を選ぶ理由=Astra matrix(META b2、ホルムズ b2)と同じ入力に揃えるため(宇宙兵器もb2に統一)。
確認済み事実: 注記は手付け(`er052_output/factlock_writer_trial_01/tools/annotate_briefs.py`のSPEC辞書で記事ごとに中核数値を人手指定)であり、新6テーマ用の自動化は未実装。

### 2-1. 構成スイッチ表(腕ごと)
| スイッチ | 旧仕様腕 | 新仕様腕 | 備考 |
|---|---|---|---|
| JA Writer | 現Production(gpt-6-luna、Luna R0→R1→R2) | Fact Lock R0[Luna]→Astra R1→R2 | |
| `OPEN243_M1` | 未設定 | `1` | Advanced枝のみ。Standardは§4(d) |
| `OPEN243_M2` | 未設定 | 未設定(見送り) | ユーザー決定3 |
| `OPEN233_RECLASSIFY_PROTECT_FLAGS` | 未設定 | `changed_actor` | M3 |
| `OPEN233_APPROVED_FLOW_SWITCHES`(Checker) | 適用 | 適用(同一) | `FLOOR_MODE=number_only`確認 |
| `OPEN243_G3_TELEMETRY_PATH` | 腕別ファイル | 腕別ファイル | 観測のみ、API費用0 |
| JA再確認(案B) | 有効(Production) | **無効**(None渡し→STOP記録) | 論点2 |

プロセス分離: (テーマ,腕,段)ごとに`subprocess`で起動し、環境変数をホワイトリストで明示する(`os.environ`の持ち越しとrunnerモジュールグローバルの汚染を防ぐ)。腕の環境変数が期待値と一致しない場合は開始前にSTOP(provenance違反)。

## 3. M1/M3の寄与分離テレメトリ(別runを増やさない設計)
前提: 2腕比較ではJA本文が違うためM1/M3の効果はWriter効果と交絡する。別runを増やさず分離するため、**新腕のrun内で「もしフラグがOFFだったら」を再構成できるログ**を全件残す。保存先=`<theme>/new/telemetry/`。
- **M1**:
  (i) 初回の要約(M1 ON入力で生成)と、その初回EN検査の全deviation(既存`b1b/audit/deviation_checks/advanced_attempt1.json`)。
  (ii) 要約のみMAJORで再生成が発火した場合の、各attemptの要約・must-fix入力・EN検査結果(既存`advanced_attempt{2,3}.json`、`rejected_advanced_m1_summary_retry.md`)。発火前=attempt1、発火後=最終attemptとして並べる。
  (iii) **影の対照(任意、前提作業i、約¥0.3〜0.6/記事の見積)**: 同じ本文に対し旧入力(`generate_family_x_in_one_line(client,title,body)`)の要約を1回生成して同じEN検査を1回かけ、結果は判定に使わずログのみ。M1(a)=入力追加の有無だけが違う対照が同一本文上で得られる。
  M1(b)(要約のみ再生成)は旧規則(本文ごとmust-fix再生成1回)の反実仮想を安く再現できない。発火件数・解決率・過去実績(従来6/14 対 M1 14/14、REPORT §110 V1)との対比に留め、限界として明記する。
- **M3**: Checker run JSONには`stage1_coverage.candidate_filter`(`n_protected_keys`、`n_excluded_claims`、`verdicts`)が既存(`open233_prod_e2e_02/runs/meta_run03_advanced.json`で確認)。追加で、
  (i) 保護されたclaim本文・fact_id・フラグ・route、
  (ii) **影の再分類(任意、約¥0.05〜0.1/runの見積)**: 保護claimだけを再分類callに通した場合の判定(EXCLUDE/CANDIDATE)をログのみ(後段へ渡さない)、
  (iii) その後のStage 2判定・floor・S1・Rewrite誘発・最終処置、を`m3_protected.jsonl`へ1 claim 1行で出力。
  評価は「保護されて重大が拾えた(便益)」対「保護されて不要なRewriteになった(コスト)」を盲検ラベルと突合する。
- **Optional(論点1)**: 旧JA本文にM1/M3 ONをかけるArm C(旧4テーマ限定、見積約¥36)はWriter交絡を完全に分離できるが予算の追加を要する。実行判断はFable/ユーザー。
- 腕の同定: すべてのrun JSON・telemetryに`arm`、フラグ実値、スクリプトsha256を記録する。

## 4. 前提作業一覧(実装は本委任では行わない)
| 項 | 内容 | 対象ファイル・行(確認済み) | 見積行数 | リスク |
|---|---|---|---|---|
| (a) | gpt-6-astra Standard単価の正式登録(input 10 / cached 1 / output 50 USD per 1M、出典`extracted_pricing.json`、2026-10-08 16:38 JST取得、raw html sha256 161df7d8...)。未登録のままだと`_load_pricing().price()`が`PricingNotFoundError`でfail-closed(`er012_e_family_entertainment_two_level_runner_01.py` L106-118)。routing contractはastraをprocessへ割り当てず`require_model_or_override`(`er006_model_routing_contract_01.py` L163〜)で扱うため契約側の変更は不要 | `er005_output/cost_baseline_01/pricing_snapshot.json`(luna登録例 L228〜L262に倣い3 meter)、`er006_model_routing_pricing_coverage_test_01.py`(L50〜)にテスト追加 | 約36行(JSON)+約15行(test) | Production用単価表の編集。登録=astra採用ではない旨を明記し別commit。cache_write(12.5)は現cost loggerのmeterに無く未登録(本用途で未使用)。guardは`cached_input_tokens`を割引計上せず(L152-153)安全側の過大計上 |
| (b) | 「これ、ちょっと面白くない？」のR0本文冒頭復唱(OPEN-175)への対処。実測: Fact Lock v1のR0 24本中1本(ホルムズ b2 r1、**Astra matrixで使われたR0そのもの**)、all6/baselineのR0 44本中4本(`ja_writer/original.md`をGrepして計数)。原因=`R0_PROMPT`(`er019_family_x_ja_writer_o_r1_r2_01.py` L52)の引用文。Productionプロンプト修正は未承認仕様のため設計上は行わない | 選択肢: A) 検出のみ(新runner側の正規表現、両腕で記録、修正なし)=推奨 / B) 新腕のみR0再生成1回(既存must-fixブロック流用) / C) R0_PROMPT書換え(Production変更=ユーザー承認要) | A: 約15行 / B: 約40行 | B・Cは腕間の非対称や未承認仕様を招く。委任文の(b)(c)の記述が一文に混在していたため、本書は(b)=OPEN-175復唱、(c)=タグ残存と解釈(要確認) |
| (c) | phase2 JA再生成でタグ残存(`RESULT.md` §3: 案B経路で`ja_writer/original.md/revision1.md/revision2.md`がタグ付きで上書きされ、`postprocess_phase1`が1回しか走らず除去されない)。**本設計は案Bを新腕で無効化するため発生しない** | 案Bを新腕でも有効にする場合のみ: `er052_factlock_writer_trial_01_run.py`のpostprocess呼び出し(再生成後にも`strip_tags`+照合を再適用) | 0行(案B無効)/約30〜50行(有効化する場合) | 案Bを無効にすると新腕のja_source MAJORは回復機会なくSTOPし、旧腕(案Bあり)と非対称(論点2) |
| (d) | M1のStandard(A2)分岐。現状`OPEN243_M1`はAdvanced枝のみ(`er012_...runner_01.py` L411・L462・L530、DESIGN_M123.md §1)。Standardは英語Advanced本文のみを入力に`generate_family_x_standard_a2_no_heading`(`er003_v1_n3_01_standard_a2_generate.py` L541)で要約も含め生成し、JA・台帳を見ない。**推奨=今回は実装しない**: Standard用の要約再生成には新しいA2用プロンプトが要り(「12〜18語」ガイドはAdvanced用)、未承認仕様の追加になる。Standard枝のEN NGは過去n=3世代で不足(ANALYSIS_01 §3-4) | 実装する場合: `er012_...runner_01.py` L616〜の`only=="standard"`分岐+`er003_v1_n3_01_standard_a2_generate.py`に要約のみ再生成の関数 | 約60〜90行+新プロンプト1本 | 実装しないとStandardの(2)評価はM3+Writer効果のみで、M1のStandard効果は未測定と明記する。実装する場合は新プロンプト(未承認)のテストと承認が要る |
| (e) | 記号後変換+Markdown除去の組込位置。既存部品を再利用: `strip_markdown`(`er052_step2_astra_r3_01_run.py` L154)、`dash_to_comma`(同L168)、`normalize_ellipsis_pause_ja`(`er003_audio_tts_asr_safety.py` L929)、`detect_prohibited_symbols`(同L1026)。組込=Astra R2出力の直後、FCの前、`revision2.md`保存の前。R2の入力にするR1は生出力のまま(matrixと同一) | 新runner内(既存ファイル変更なし) | 約40行 | matrixのFCはP1(Markdown除去のみ)本文で行われ、本設計はFCを変換後本文で行う(句読点のみの差)。記号Gateは記録のみ=Productionの記号Gate(must-fix再生成)と非対称(論点3) |
| (f) | 2腕並走runner。新規`er052_factlock_astra_e2e_runner_01.py`(仮称): テーマ共有dir管理、旧腕=er019 runnerのsubprocess、新腕=W1〜W6、Checker起動(`er052_output/open233_prod_e2e_01/e2e_run_02.py`の`run_one`/`RunCapHook`を流用し、固定instance表`old.prepare_instances()`の代わりに**生成記事から動的にinstanceを組む**)。fixtureのキー=`id, ledger_text, article_text, source_article_text(=JA R2), include_related_fact_id(=True), hook_aware(=False), baseline_parsed`(`er050_gpt6_checker_comparison_trial_01.py` L133-151)、inst側は`stage1_mode="fresh"`・`substitute_baseline_on_stage1_miss=False`・`s1u_eligible=False`。状態分離: `runner.OUT_DIR`/`BUDGET_STATE_PATH`をworker別、telemetry/G3パスを腕別、出力は`<theme>/<arm>/`に閉じる、書込は一時ファイル→rename(クラッシュ時のNUL埋め対策) | 新規ファイル(既存編集なし) | 約450〜600行+単体テスト約250行 | 最大の新規実装。runnerのモジュールグローバルと環境変数の持ち越しはsubprocess分離で回避。dynamic fixtureで`baseline_parsed=None`が通るかは未確認(¥0 dry-runで確認) |
| (g) | 予算ガードのweb_search未計上差(`E2E_EVIDENCE.md` L44)。**既に是正済み**: OPEN-242(commit 0110d6f1「予算ガードにweb_search課金を計上、run_01/02再計算でcost.jsonと±0.001円」、`web_search_call_usd` `er012_...runner_01.py` L124-130、`compute_cost_jpy_so_far`が加算)。E2E_EVIDENCE.mdのガード値4.70円 対 実費19.105円は是正前の記録 | 本実行前に¥0で再確認: run_02の`raw_usage_log.jsonl`からガード値を再計算し`cost.json`=19.105と一致(±0.01)を確認 | 約20行(確認スクリプト) | 残る穴: (i)astra単価未登録(→(a)必須)、(ii)Checker runnerは別のbudget state(`runner.BUDGET_STATE_PATH`)で動くため3 workerの合計を横断集計する必要、(iii)ガードは未キャッシュ入力単価計上で過大側 |
| (h) | 新6テーマの注記版brief(【事実N】、【中核数値】/【周辺数値】)の作成。現状は人手(`annotate_briefs.py`のSPEC)。新6テーマはSonnet workerが`ANNOTATION_LOG.md`の原則を固定ルールとして作成し、Fableが確認する運用を提案(API費用0) | `er052_output/factlock_astra_e2e_trial_01/`配下に注記ルール文書+テーマ別の注記ログ | 文書+テーマあたり人手約30分(見積) | **再現性の限界**: 注記が人手判断のため量産(Production)へそのまま持ち込めない。注記者バイアス(`RESULT.md` §7「B3が中核数値を選んだ場合の性能」は未検証) |
| (h2) | TTS 2本の入口。er019 runnerはStandardで終了しTTS stageを持たない(同runner L394)。DEV TTS Standard同期の既存スクリプトは本委任では未特定 | 未確認(要調査: `PM_GOVERNANCE.md` 7-1/7-2、`er005_e2e_tts_cost_quality_01.py`等) | 未確認 | TTS費用「約¥40」はFable見積で根拠ファイルは未確認 |
| (i) | M1/M3影の対照ログ(3節)、R0復唱検出((b)案A)、ブラインド化・集計スクリプト | 新runner+`tools/` | 約150行 | 影の対照はAPIを追加で使う(M1約¥0.3〜0.6/記事、M3約¥0.05〜0.1/run、いずれも見積)。判定には使わない |
| (j) | 新腕の失敗・STOP方針(5-3)の確定 | 設計のみ | - | 論点3 |

## 5. 実行計画

### 5-0. 実行前ゲート(Fableの実行Go後)
G0(¥0): 前提(a)(f)(h)(i)の実装・単体テスト・dry-run(API stub)、(g)再確認、メモリ確認。
→ G1(カナリア、見積約¥35〜45・約10分): METAの新腕をEN段(Advanced+Standard)まで1本だけ実行し、フロー破綻(モデルID、タグ残存、記号、STOP、費用)だけを確認(品質評価はしない)。
→ G2(本番)。直列化の理由=新規runnerの初回runtime evidence確認(破綻時の損失を数十円に限定)。

### 5-1. 並列度と割付
単層3並列(worker=プロセス3、各workerがテーマを順に処理)。二重並列(ThreadPool×xargs)は禁止(2026-10-07 PCクラッシュ、WinError 1455の教訓)。各worker開始前と各stage前に空き物理メモリを確認し4GB未満なら待機(前回E2Eの上限60分待機を踏襲)。実測根拠: 前回の単層4並列で最大Private約1.2GB・空き物理≧4.2GB・降格0(ACTIVE_TASK A5記載)。4並列+自動降格はユーザー決定済み(A5)の選択肢だが、本E2Eは3で見積(時間が許容内)。
割付(時間見積で均等化。旧テーマ約29分、新テーマ約36分、6-4):
- W1: META→宇宙兵器→新A→新B(約130分)
- W2: ホルムズ→新C→新D(約101分)
- W3: ミニバッグ→新E→新F(約101分)
旧4テーマを先に(凍結比較ができる)、新6を後に。1テーマ内は直列(旧腕→新腕)。旧腕を先にする理由=安価で、途中停止時に必ず対(paired)で揃う側から止まるため。新テーマのresearchで台帳が使えない場合(例: kept facts<3、API障害が再試行2回後も継続)は、ユーザーが指名する補欠テーマと入替(事前登録)。

### 5-2. 費用・停止条件(前回計画書`e2e_plan_open233_stage1_loop2_01.md`のWaste検知を踏襲、数値は本E2E用の提案)
| 区分 | 閾値(提案) | 動作 |
|---|---|---|
| 累計上限(ユーザー決定) | ¥1,000 | 到達でhard stop。ソフトアラート¥800で新テーマ開始を止めFableへ報告 |
| 見積超過 | 累計が見積(約¥650)×1.3=約¥850を超える見込み | 一時停止してFableへ報告 |
| research+ledger+B3(1テーマ) | 見積約¥15〜17(実測根拠6節)。¥30超でアラート、¥40超でabort | abort時は補欠へ |
| Astra R1+R2(1記事) | 見積約¥27〜34。¥50超で当該記事abort | |
| Checker 1 run | 実測最大¥5.66、平均¥3.50(§81)。¥10超でabort、記録して次へ(前回E2E prod_e2e_01と同じ「abortは記録して継続」) | |
| 新腕1記事合計 | 見積約¥42。¥70超でアラート | |
| 即停止(全体STOP) | (1)provenance違反: 腕のフラグ・モデルIDが期待と不一致(Astra段の`model`が`gpt-6-astra`で始まらない、`fallback_detected`) (2)API失敗>3/run (3)単価未登録例外 (4)出力NUL/破損 (5)予算state不整合 (6)承認スイッチ不一致 (7)新腕でLuna R1/R2呼び出しを検出(旧Writer混入) | |
| 品質起因(Human Review、重大、STOP) | **止めない**(記録のみ。前回E2Eと同じ) | |
Waste検知: 前回の`RunGuard`(call数>80、cycle番号>5、同一claim_identityのRewrite>3)を流用し、abort記録のうえ全体STOP判断はFable。

### 5-3. 新腕の失敗扱い(提案、論点3)
- Astra APIの一時エラー: 最大2回再試行(前回E2Eの技術障害再試行MAX_RETRY=2と同じ。matrixの「retryなし」は測定専用だった)。
- JA FC(R1後・R2後)のMAJOR: **記録のみ**(再生成・STOPしない)。R0は既存のmust-fix1回→STOPを維持。
- 記号Gateの残存: 記録のみ。字数: ソフトキャップのため判定せず記録のみ。
- EN段の`JA_RECHECK_REQUIRED`: STOPとして記録(案B無効)。

### 5-4. 途中停止時の再開
- stage完了マーカー(各stageの出力が存在・非空・NUL無し・JSON妥当)を`<theme>/<arm>/state.json`へ追記専用で記録。再開は未完了stageのみ、完了済みstageのAPI再呼び出しは禁止(R1済みならR2から)。
- 費用台帳はworker別`ledger_costs_worker{N}.jsonl`(追記専用、他workerのファイルは読取のみ)。累計=3ファイルの合計。
- 破損疑い(0バイト、NUL埋め)は当該stageだけ破棄して再実行し、破棄分の費用も台帳に残す。
- 再開時はスクリプトsha256が同一であること(変更した場合は事前登録の「変更禁止」違反として記録しFableへ)。

## 6. 費用・時間見積(**見積**。実測根拠は出典併記)

### 6-1. 単価・実測根拠(確認済み)
- astra Standard 10 / cached 1 / cache write 12.5 / output 50 USD per 1M(Batch・Flexは50%): `er052_output/factlock_writer_trial_01/astra_pricing_01/extracted_pricing.json`(2026-10-08 16:38 JST取得)。USD/JPY=160。
- Astra R1+R2 Standard換算(実測トークン由来)=3記事・系列X・平均約¥31.3/記事(範囲約¥27.1〜33.6。matrix_01のMETA 13.57×2、matrix_02のホルムズ16.54×2・ミニバッグ16.79×2、Standardは旧推定単価の2倍): `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_18_result.md` §5、`astra_revise_matrix_02/eval/COST_MATRIX_02.md`。過去報告のastra「実費」(約¥48.48、約¥64.92)は旧推定単価(5/25=Batch/Flex相当)でStandardの約半分。ダッシュボード請求との突合は未実施=未確認。
- Luna Writer(R0〜R2+FC)約¥1.40: `er052_output/gpt6_wiring_e2e_01/E2E_EVIDENCE.md` run_02 ja_original 0.21+check 0.177+must_fix 0.375+check_retry 0.101+ja_r1 0.215+ja_r2 0.231+ja_r2_check 0.089。
- EN段(Advanced+Standard)約¥0.76: 同上 advanced 0.318+standard 0.443。
- research+ledger+B3: run_02 research 9.214+ledger 7.332+storyline_b3 0.4=約¥16.95(web_search込み)。別run(委任_03 run_01)は10.743+3.847+0.384=約¥14.97。
- Checker: §81の9 run実測 合計¥31.519、平均¥3.502/run(範囲¥1.97〜5.66)、平均345.5秒/run(最大548.7秒)、3並列で総所要1337秒(`open233_prod_e2e_02/e2e_summary_02.json`)。
- Astra所要: R1 31.9/63.4/51.6秒、R2 51.5/46.5/48.3秒、1記事R1+R2平均約98秒(委任_18結果 §4(a))。

### 6-2. 1記事あたり(見積)
| 項目 | 新仕様腕 | 旧仕様腕 | 根拠 |
|---|---|---|---|
| Fact Lock R0 / Luna Writer | 約¥1.4(R0+FC+タグ照合。matrix_02ミニバッグR0実測¥1.39) | 約¥1.4 | 6-1 |
| Astra R1+R2 | 約¥31.3(範囲27〜34) | - | 委任_18 |
| JA FC(R1後・R2後) | 約¥0.35(matrix_02 FC ¥1.33/8本=約¥0.17/本) | (Writer内に含む) | COST_MATRIX_02 |
| EN(Advanced+Standard) | 約¥1.0〜1.5(M1再生成発火で増) | 約¥0.8 | 6-1 |
| Checker(Advanced+Standard 2 run) | 約¥7.0(2×3.5) | 約¥7.0 | §81 |
| 影の対照(M1/M3) | 約¥0.4〜0.7(未実測の見積) | - | |
| 小計 | **約¥42**(範囲約36〜52) | **約¥9.2**(範囲約7〜14) | |

### 6-3. 総額(見積)
| 項目 | 見積 |
|---|---|
| 新仕様腕 10記事 | 約¥420(360〜520) |
| 旧仕様腕 10記事 | 約¥92(70〜140) |
| 新6テーマのresearch+ledger+B3(共有) | 約¥100(¥15〜17×6=¥90〜102) |
| TTS 2本+ASR | 約¥40(**Fable見積、根拠ファイル未確認**。COST_MATRIX_02 §3の「現行1セット約¥52[TTS Standard同期]」も上流出典未確認) |
| **合計** | **約¥650(範囲約¥560〜780)**。Fable事前見積(約¥700)と整合 |
| 上限¥1,000に対する余裕 | 中央値で約¥350、高側でも約¥220 |
最大のブレ要因=Astraのreasoning量(出力トークン)とCheckerの幅(¥1.97〜5.66/run、最大40 run)。

### 6-4. 時間(見積)
1テーマ: research+B3約2〜3分(新6のみ。単独実測は未確認、run_02全体326秒からの上限推定)+旧腕(Writer約2分+EN約2分+Checker 2×345秒)+新腕(R0約1分+Astra約98秒+FC+後処理+EN約2分+M1再試行+Checker 2×345秒)。新テーマ約36分、旧テーマ約29分(いずれも見積)。3並列で割付最長のW1が約130分。TTS・ASRと立上げを含め**約2〜2.5時間**(Fable見積と一致)。

## 7. 評価手順
1. **自動集計(¥0)**: run JSON・cost.json・telemetryから1-2の表A〜E・H・Iを機械集計(§81と同形)。旧4テーマは凍結値を別列で併記。
2. **盲検ラベル**: 新R2/旧R2、新EN/旧ENを腕・順序を隠してコピー(MAPは非公開、git add対象外)。Sonnet worker×3(テーマで分割)が重大/軽微をラベル(`label_source`付き、前回§81のラベル運用に準拠)。Sonnetラベルは推測でありユーザー確認前は確定ではない。
3. **Fable突合**: Sonnetラベルと自動集計・Checker判定を突合し、不一致・重大候補を判定(`confirmed_by`付き)。
4. **ユーザー人間確認(2〜3記事)**: 重大候補があるテーマと、面白さの差が大きいテーマ。提示パックの形式=テーマごとに「元記事(旧Production Writer R2、旧腕)」と「新R2(新腕)」だけを、腕を伏せたX/Yで並べ、R1・FC・Checker結果は載せない(2026-10-08ユーザー指示「提示は元記事＋XYのR2のみ、R1は不要」、`USER_PACK_02.md`形式に準拠)。対応は`_private/MAP.json`、回答後に開示。
5. **Opus条件C**: 結果が「重要変更のProduction採用提案前」に該当する場合、Opus独立レビューを入れる(`PM_GOVERNANCE.md` 11-3)。採用判断は人間ユーザーのみ。
6. 報告: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`に新節(次の空き番号)として記録(新しい証跡置き場は作らない。生データは本ディレクトリ配下の`runs/`)。

## 8. Opus条件Aレビューに出す論点(新しい構造・処理フロー=条件A)
1. **交絡**: 新旧2腕比較ではWriter変更とM1/M3(翻訳仕様)がJA本文の違いを介して交絡する。3節の影の対照で十分か。Arm C(旧JA×M1/M3 ON、旧4テーマ限定で約¥36の見積)を足すべきか。
2. **案B(JA再確認)の扱い**: 新腕で無効化(ja_source MAJORでSTOP記録)にする設計は、旧Production Luna Writerの混入を防ぐ一方、旧腕との非対称と回復機会の喪失を生む。Astra経由のJA再生成を新規に作るのは未承認仕様。どう扱うか。
3. **Production等価性**: 新腕のR2後はFC・記号Gateを「記録のみ」としたが、旧Writerは「FC MAJOR→must-fix1回→STOP」「記号Gate→must-fix」を持つ。新腕を「Trial等価(測定)」と「Production等価(安全装置込み)」のどちらとして評価するか。この選択で新腕のSTOP率と良化の解釈が変わる。
4. **注記briefの人手依存**: 中核数値の指定が人手判断(再現性・注記者バイアス)。新6テーマでは別Sonnet workerが作るが、Production化可能な自動ルールがないままFact Lock効果を評価してよいか。
5. **M1のStandard(A2)枝未実装**: Standard枝のM1効果が未測定になる。Standardの評価範囲をM3+Writerのみと限定して妥当か。実装する場合の新プロンプトは未承認仕様。
6. **統計的限界と判定線**: n=10記事(Checker run最大40/腕20)。重大は床効果(§81は0〜1件)。PREREGISTRATION_01.mdの線引き(符号検定の限界、ties扱い、重大の非対称ルール)は妥当か。LLM(Sonnet)ラベル+同系列モデルFCの自己判定の問題。
7. **コスト・停止設計**: 単一出典のastra単価(ダッシュボード請求未突合)、web_searchが大半を占めるresearch費(両腕で共有)、停止閾値(5-2)と「品質起因では止めない」方針の妥当性、カナリア(G1)の置き方。
