# plan_01: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 実行計画(委任_01、2026-10-07 19:10 JST、API ¥0、Production変更なし)

到達上限Status=`PLAN_READY`(Fable照合後に実行委任)。本書は計画のみ。生成は未実行。

## 1. 裏取り結果(事実のみ、出典付き。推測は書かない)

### (a) 「従来版Control」(E2E_02の比較基準)の正確な構成
- E2E_02の従来版 = `LEDGER-POLYSEMY-NOTE-TRIAL-04 Control rep1`(REPORT §94-3 表見出し「従来版=TRIAL-04 Control rep1」)。実体: `er052_output/open233_polysemy_trial_04/runs/<slug>/control/rep1/`(5テーマ。費用 `.../runs/cost_control_p1.json`・`cost_control_p2.json`)。
- Writer経路: DEV wrapper `er052_open233_polysemy_nb_dev_01.py`(env `OPEN233_B3_VARIANT=control`=B3 promptの差替なし)→ production runner `er019_family_x_entertainment_production_runner_01.main()`(B3→JA R0/R1/R2→phase2でEN)。固定台帳をコピーして使い、Researcher/Ledger段は実行しない(research_calls=0をassert)。台帳=`er052_output/open233_polysemy_trial_02/ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt`(sha先頭: meta ea0ce587/hormuz 9bd6834e/space_weapons f172a253/sewer 42faae06/ai_control 256c6721。E2E_02 `ledger/FREEZE.json` の `base_sha256` と全5テーマ一致、実測確認)。
- B3のnotes転写方式: **CURRENT_SPEC.mdに「Notes for writer」の転写規則は無い**(grep 0件。`notes_for_writer` は L1536 Fact Safety行の別文脈のみ)。実装側 `er019_family_x_storyline_b3_fact_selection_01.py` のprompt(L60-)に notes 専用の指示は無く(`notes` grep 0件)、台帳全文(`ledger_text`、notes_for_writer行を含む)を渡して「必要最小限のFactを簡潔にまとめた」`selected_fact_brief` をB3モデルが自由に作る=**要約転写(逐語指示なし、LLM裁量)**。ユーザー決定文「要約転写で渡す仕様、逐語でなくてよい」と実装は整合。(§97のT1=要約転記が「従来相当」。)
- Checker構成: `00a_base_checker_config.md` の「ユーザー確認済み」(1)〜(5)と、runnerの承認構成(41キー)。**現行runnerの `apply_open233_approved_flow_switches()` 結果が `er052_output/open233_prod_e2e_02/approved_switches_dump_worker1.json`(00aが指す実測)および E2E_02 run の `checker/approved_switches_dump_after_p01.json` と完全一致(True/True、差分{})** を本計画作成時にdry-runで確認(`approved_switches_dump_plan_dryrun.json` に保存)。承認構成のうちS1/disclosure_gap/hook_aware/Stage1 coverage_union系は00a「未確認」(包括承認またはFable判断)のまま=固定して「現状ON」。
- スイッチ: `OPEN233_B3_VARIANT`(control/nb)、`OPEN233_NOTE_PREFIX`、`OPEN233_RUNS_ROOT`(いずれもDEV wrapperのenv)。Checker側は承認スイッチ既定(`runner.apply_open233_approved_flow_switches()`→`assert_open233_approved_flow_switches()`)のみで、Trial専用のCheckerスイッチは無い。
- 1記事原価(円、TTSなし): TRIAL-04 Control 5本=平均¥9.28(P1 ¥24.66+EN ¥4.75+Checker ¥17.00=¥46.40/5)。E2E_02 P2 10本=平均¥11.04(最小¥7.78、最大¥16.74=space_weapons rep2、`er052_output/open233_allfact_note_e2e_02/cost.json`)。
- 実行時間(E2E_02、10並列時): 1 runあたり約8〜15分(例 meta rep1 10:26→10:34、space_weapons rep2 10:29→10:43、`nb_provenance_phase1.json`/`checker/budget_state_checker_after_p01.json` の時刻)。

### (b) 固定多義語Noteの本文と差し込み方、META-ROLLBACK TRIAL-01/02 runner との違い
- Note全文(逐語、§91-1): 「注意(多義): この表現は多義的なので、単語だけで機械的に解釈・翻訳せず、原文の文脈・主体・対象・前後関係から意味を確定して記事化すること。」
- 差し込み: **台帳のMUSE-HC-012のnotes_for_writer欄末尾** に ` / ` 区切りで追記(既存notes「『サービス全体を停止した』とは書かない。…」は保持)。notes以外の差分0(`er052_output/open233_meta_rollback_minimal_note_01/ledger/diff_report.md` PASS、付与note数1)。台帳: `.../open233_meta_rollback_minimal_note_01/ledger/nb/research_ledger/verified_fact_ledger.txt`(sha `cfd6d7023c23…`、全run一致、FREEZE.json)。briefへの転記はDEV wrapperの `OPEN233_B3_VARIANT=nb`(B3のuser promptに「引き継ぎ規則」ブロックを追記)が担う。
- **重要な事実(要Fable判断1)**: 0/12を出した当時の引き継ぎ規則ブロックは「台帳のnotes_for_writerに『注意(多義):』で始まる注意がある場合、その注意文を…そのままbriefの該当箇所の直後に1行で引き継ぐ」(sha先頭 `abd16d9a073c`、REPORT §92-1・`nb_provenance_phase1.json` rep2/rep7で確認、旧テンプレ文を再構成してsha一致を検算)。しかしDEV wrapperは E2E_02 Phase A の commit 1fefd10f で規則文を「notes_for_writerが『{prefix}』**で始まる場合**、その内容全体を…」へ変更済みで、現在の既定出力sha先頭は `0797ba7a`(dry-runで確認)。HC-012のnotesは「『サービス全体を…』」で始まるため、**現行wrapperのままprefix=`注意(多義):` で回すと規則が発火しない可能性があり、0/12と同一条件にならない**。
- runnerの違い: META-ROLLBACK TRIAL-01/02 = phase1のみ(`--phase phase1 --budget-jpy 8`、B3→JA R0/R1/R2まで、EN・Checkerなし)、Metaのみ、台帳nb、`OPEN233_B3_VARIANT=nb`、評価はJA R2のみ(3値)。本件 = phase1+phase2(EN+Checker)まで、5テーマ、Metaのみnb+Note、他4テーマはcontrol(Noteなし)、評価はJA R2/EN Checker前/EN最終。

### (c) Production入口でControl+Checker+多義語Noteを通せるか
- Checker部分は `run_checker_after_p01.py`(DEV薄ラッパ)が `runner.apply_open233_approved_flow_switches()` と `runner.assert_open233_approved_flow_switches()` を呼び、**未パッチの Production関数 `runner.run_instance`** を呼ぶ(OPEN-238 runtime evidence `runtime_evidence/tools/run_wired.py` と同一方式。provenanceの `entry="runner.run_instance (Production function, unpatched…)"`、`dev_patch_module_loaded=false`、`switches_equal_ref_e2e02=true`)。DEV wrapperのphase2が `run_checker_after_p01.py` をsubprocessで呼ぶ(`er052_open233_polysemy_nb_dev_01.py` main末尾)。
- 通せる: Control(variant=control)・Meta Note(variant=nb + 台帳nb)とも同一wrapperで phase1→phase2(EN+Checker)が通る(両variantの `--dry-run` を本計画作成時に実行、¥0、out_dirは未作成で確認)。必要なTrialスイッチは既存の3 env のみ。**ただし(要Fable判断1)のとおりMeta Noteの0/12再現には旧引き継ぎ規則が必要**。
- 注意(事実): Checker全体は PRODUCTION_WIRED 未(OPEN-238 precheck修正のみ PRODUCTION_WIRED、§99-6)。通常の量産日次経路にChecker常設はなく、「Production入口」=Production関数 run_instance・承認スイッチ不変をDEV薄ラッパ経由で呼ぶ意味(E2E_02/OPEN-238 runtime evidence と同じ)。

### (d) 00aの構成が PRODUCTION_WIRED 前であることの確認
- 00a結論(1行目): 「Status=APPROVED_FOR_PRODUCTION・**PRODUCTION_WIRED未**(DECISION_LOG L19990)」。ACTIVE_TASK UDR-deferred/OPEN_ITEMS L727 とも整合(`OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01` 9/20停止・残11 run再開せず)。
- **00a時点との差(事実)**: 00aは2026-10-06。その後 2026-10-07 に OPEN-238 precheck修正(`extract_percentages_strict`、commit 874dd6e2)がrunner/precheckへ配線され PRODUCTION_WIRED確定(§99)。E2E_02(10/07午前、従来版・P2とも)は配線**前**のprecheckで走っている。本件のCheckerは配線**後**(承認スイッチは不変=41キー一致)。E2E_02従来版との比較では「precheck分数語偽陽性が解消された分」の差が混入しうる(OPEN-238 Regression: 26 run で発火2→0他不変、§99-3)。

## 2. 要Fable判断(勝手に埋めない。実行委任前に決定が要る)
1. **Meta Noteの引き継ぎ規則**: (A)旧規則を再現(DEV wrapperに規則文選択のenvを足し、`transfer_block_sha256=abd16d9a…` をassertする。0/12と同一条件。実装=DEV wrapperへの最小追加+test、Production外)、または (B)現行規則のまま(HC-012のnotesが『注意(多義):』で始まらず発火しないため、Noteがbriefへ届かない恐れ。到達はbrief転記チェックで検証)、または (C)現行規則+prefixを『注意:』にして「notes全体を逐語転記」(E2E_02 P2方式。0/12とは別条件)。**推奨=(A)**(累積0/22の分母を統一できる)。
2. **MetaのvariantとB3転記の「従来版」との整合**: ユーザー決定「現行B3(要約転写)」に対し、Meta Noteは `variant=nb`(逐語転記ブロックを追加するDEV処理)で届ける設計(0/12の条件)になり、Metaだけが「現行B3+Note逐語転記」、他4テーマは純粋な現行B3(要約転写)となる。よって「Meta=Note転記の効果」と「他4=Controlの再確認」は同一のbrief生成条件ではない。これでよいか(または variant=control+台帳noteのみ=要約転写でNoteが落ちうる設計にするか)の確認。推奨=nb(Noteの到達が再現条件)。
3. **precheck修正の混入**: 上記(d)のとおり本件のCheckerはOPEN-238配線後。E2E_02従来版との直接比較を厳密な同条件とみなさず、「現行Production相当」の測定として扱ってよいか。
4. **Rollback評価対象の段**: 過去の0/12はJA R2のみ判定。本件は主指標を JA R2(過去と比較可能)とし、EN Checker前/最終(rubric 4節『悪い方を採用』)も併記する設計(preregistration 3節)。これでよいか。
5. **出力レイアウトの軽微な差**: 指示の `runs/<slug>/<rep>/` に対し、DEV wrapperが `out_dir` に `/<variant>/` を要求する(`runs_root/<slug>/<variant>/rep<k>`)ため、`runs/<slug>/<variant>/rep<k>/`(meta=nb、他=control)とする。
6. **評価用スキーマの追加**: B3 article_schemaに任意フィールド `checker_rewrites`・`rollback_labels` を追加(判定基準は不変)。Checker最終ENをs2_enとして扱う読み替えもREADMEに記載。第2評価者X(Metaのrollback label-only)の追加を提案(評価者間不一致の検出用)。
7. **JA側へのCheckerの効果**: Checkerは現状ENのみ書換(実測: `en_text_after_rewrite`のみ)。JA残存NG(OPEN-239)は⑦で記録のみ。

## 3. run構成表(計18本)
| テーマ(slug) | variant/台帳 | Note | rep | 本数 | out_dir |
|---|---|---|---|---|---|
| meta | nb / `open233_meta_rollback_minimal_note_01/ledger/nb/...`(sha cfd6d702…) | HC-012固定最小Noteあり | 1〜10 | 10 | `runs/meta/nb/rep<k>` |
| hormuz | control / `open233_polysemy_trial_02/ledgers/hormuz/control/...`(sha 9bd6834e…) | なし | 1〜2 | 2 | `runs/hormuz/control/rep<k>` |
| space_weapons | control(sha f172a253…) | なし | 1〜2 | 2 | `runs/space_weapons/control/rep<k>` |
| sewer | control(sha 42faae06…) | なし | 1〜2 | 2 | `runs/sewer/control/rep<k>` |
| ai_control | control(sha 256c6721…) | なし | 1〜2 | 2 | `runs/ai_control/control/rep<k>` |
- 共通: topic=`er052_output/open233_polysemy_trial_02/ledgers/<slug>/topic.txt`、`--ledger-txt` は上記台帳(コピーして使用、sha一致をwrapperがassert)。run ID=`<slug>/<variant>/rep<k>`。LLMにseed指定は無い(再現性は台帳sha・プロンプトsha・モデルIDで固定。非決定性は記録するのみ)。
- Checker instanceは `run_checker_after_p01.py` の既定(Before `meta_run03_advanced` のinstance値踏襲、3テキストのみ当該runへ差替。E2E_02と同一)。
- `repNN` は新規ディレクトリのみ(既存out_dirがあればwrapperがSTOP=混線防止)。

## 4. スイッチ構成・provenance
- env(全run共通): `OPEN233_RUNS_ROOT=er052_output/open233_control_checker_polysemy_trial_01/runs`、`PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`。Meta: `OPEN233_B3_VARIANT=nb`(+判断1の結果に応じた規則文選択env、sha assert付き)、他4: `OPEN233_B3_VARIANT=control`。
- Checker: 承認スイッチ既定(41キー、不変。各runの `checker/approved_switches_dump_after_p01.json` と `checker_after_provenance.json` が自動保存される)。
- 実行前provenance(`er052_output/open233_control_checker_polysemy_trial_01/provenance.json`): git HEAD、runner/precheck/er019 B3/wrapper のsha256とdirty有無、`dev_patch_module_loaded=false`、承認スイッチdumpとE2E_02 dumpの一致、`PRECHECK_MODE=number_only`、`FLOOR_MODE=number_only`、モデルID、起動時刻(OPEN-238 runtime evidence と同形式)。
- 公開しない: TTS・公開処理は呼ばない(phase1/phase2/Checkerのみ)。Production承認スイッチは変更しない。

## 5. 実行方法(並列4・単層。実行委任で `tools/driver_ccp.py` を作る。流用元 `er052_output/open233_b3_trial_01/tools/driver_stage2.py`)
- 単層ThreadPoolExecutor(max_workers=4)。1タスク=18 run のうち1本の phase1→phase2 を連続実行(brief待ちは不要=B3もwrapper内)。
- コマンド要旨(1 run、Meta nb の例。他4は variant=control・台帳・slug差替):
  - phase1: `python er052_open233_polysemy_nb_dev_01.py --phase phase1 --slug meta --theme "<topic.txt>" --ledger-txt <台帳> --out-dir <runs>/meta/nb/rep<k> --budget-jpy 8 --yes-run-paid`
  - phase2(EN+Checker): 同 `--phase phase2 --budget-jpy 15 --checker-budget-jpy 15 --yes-run-paid`(`--no-checker` は付けない。E2E_02は checker既定¥10で、最大実績¥9.68と余裕が薄いためcheckerを¥15へ。予算上限の引き上げのみで挙動は不変)
- guard(driver、毎phase開始時と終了時に評価):
  - 累計見込み **¥480** 到達で新規phaseを開始しない(全rep dir の phase1/EN cost.json と checker `run_cost_jpy` の合計+失敗試行の推定を累計に含む)。
  - 1 run実費 **¥25** 超でSTOP(最大実績¥16.74)。
  - infra連続失敗(Gate STOP以外)3でSTOP(Gate STOPは観測結果として数えない=B3 Trialと同方針)。
  - メモリ降格 4→2→1(WinError 1455/MemoryError検知、未完了runは削除して同枠再実行、並列1でも再発で1回のみ再試行しSTOP)。
  - 停止run(JA_FACT_CHECK_STOP/LEDGER_DEVIATION等のWriter内部Gate)は **既存の安全装置を回避しない**。同枠1回のみ再実行(E2E_02と同方式、停止分の費用は累計に含む)。1回目のGate STOPは③でカウント。再実行上限は全体で4(infra/Gate合算)。上限超過はSTOPして報告。
  - メモリ監視 `memmon.py` を並行起動(流用)。
- 並列化の理由(開発時間最小化原則): 18本は互いに独立(別out_dir・別state)、条件同一性は台帳sha・env固定で保てる。並列4は依頼上限かつメモリ降格実績(10並列で1455の再発歴)を踏まえた値。直列化する要素=なし(rate limit/メモリのみ降格で対応)。

## 6. 費用・時間見積
- 費用: 18本 × 実績平均¥9.3〜11.0 = **¥167〜199**、上振れ(最大実績¥16.74×18)=¥301が上限目安。再実行枠: 最大4回×約¥6=約¥24。**期待¥200前後、最大でも約¥330**(上限¥500・guard ¥480の範囲内)。評価インスタンス(Claude)は¥0。
- 時間: 1 run 8〜15分(平均約12分)。18本/並列4 = 4.5波→**実行約55〜70分**(再実行・メモリ降格込みで最大約120分)。評価: 評価者3本が各6記事、並行して約30〜40分/本+rollback_X(10記事label-only)約15分。全体の見込み約2〜2.5時間。
- 並列化による短縮: 直列(約3.6時間)→並列4(約1時間)=約2.6時間短縮。評価も3並列+rollback_X並行。

## 7. 出力レイアウト
```
er052_output/open233_control_checker_polysemy_trial_01/
  provenance.json                 # 実行前(上記4節)
  runs/<slug>/<variant>/rep<k>/   # wrapper標準の出力(ja_writer/, b1b/, checker/, storyline_b3/selected_brief.md, cost.json, nb_provenance_phase{1,2}.json 等)
  runs/_logs/                     # 各phaseのstdout log
  runs/driver_result.json cost.json manifest.json(brief転記チェック・Note到達の記録を含む)
  eval/blind/<slug>/<code>/       # make_eval_pack_ccp.py が生成(盲検コピー。b1b/article.md=Checker最終EN、b1b/pre_checker.md=Checker前)
  eval/eval_pack/                 # README_EVALUATOR.md、assignment_ccp_{A,B,C}.md、assignment_rollback_X.md、schema、template
  eval/_private/                  # MAP_ccp.json、run_facts.json、assignment_balance_ccp.json(評価者非公開)
  eval/articles/ eval/notes/ eval/rollback_x/   # 評価者の出力
  eval/HUMAN_REVIEW_PACK.md       # 人間確認パック(テンプレ human_review_pack_template.md)
```
- 詳細証跡は上記ディレクトリ(新規。本件は新管理IDのため既存er0XX_output構造の`er052_output/open233_*`命名に従う)。REPORT反映は実行完了後の別委任(本委任ではSSOT編集禁止)。

## 8. 実行委任に渡すべき事項(Fable照合後)
1. 要Fable判断1〜6の決定。判断1が(A)なら、DEV wrapperに旧引き継ぎ規則を選べる最小追加(既定挙動は不変)+test(`er052_output/open233_polysemy_trial_02/tests/test_nb_dev_01.py` へ追加)を先に行い、phase1 dry-runで `transfer_block_sha256=abd16d9a…` を確認。
2. 事前登録(preregistration_01.md)を実行前にコミット済みであること(結果を見て基準を変えない)。
3. 実行前dry-run(18コマンド `--dry-run`、¥0)→ provenance.json作成 → driver_ccp.py起動(`DRYRUN` モード併設)。
4. 各run後に `check_brief_transfer.py`(E2E_02流用: `er052_output/open233_allfact_note_e2e_02/tools/check_brief_transfer.py`)でMetaのNote到達を記録(HC-012が選択されたrunのみ)。
5. 18本完了後 `python docs/pm/control_checker_polysemy_trial_01/tools/make_eval_pack_ccp.py`(完了数が18でなければSTOPする)→評価委任(A/B/C+rollback_X、盲検)→全員分揃ってからMAP開封・集計。
6. 評価パック生成scriptは合成fixture(既存E2E_02の完了run18本相当を複製)で動作確認済み(割当6/6/6、決定論性OK、Meta 10本のrollback_X割当)。
