# U-1 限定受入(案b: 承認済み品質マスター受け入れ)設計書 01

管理ID: FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_02 / 日付: 2026-10-11 / 課金0 / **設計のみ(コード実装なし)**
Status: `IMPLEMENTED_PENDING_USER_PRODUCTION_RUN`(委任_05で実装・test・乾式検証済み。Opus条件Aレビュー GO with required fixes を8節で反映。ユーザー決定①(案b)は`APPROVED_FOR_PRODUCTION`。実run=API課金は未実施)。2〜7節は設計時点の記述で、実装での変更点は8節に集約。
ユーザー決定(2026-10-11): 案bを`APPROVED_FOR_PRODUCTION`。条件=HUMAN_APPROVED_QUALITY_MASTER確認/本文・メタ sha一致/許可対象・出所を厳密限定/`MAQ_TRIAL_W-1`来歴を改変しない/既存U-1の目的・保護範囲維持/Trial成果物を無条件にProductionへ流入させない。実装前にOpusレビュー(安全性・監査可能性・U-1整合)。
worktree: `C:\Users\tensh\eigo-radio-tone`(feature/coffee-new-tone-01)。

## 1. 現行U-1の目的・判定条件・保護範囲
- 目的: W-1(新Writer)来歴のないJA記事、または現行の注記済みB3契約と整合しないJA記事を、通常Production経路で再利用・混入させない(CURRENT_SPEC.md「U-1 / U-2」節 L1182-1184、`PRODUCTION_WIRED` 2026-10-11)。
- 実装: `er019_family_x_entertainment_production_runner_01.py` `load_reused_ja_text(out_dir)`(L233-257)、例外 `LegacyWriterProvenanceStop`(L196)。呼出元は同runner main L435(`ja_writer/revision2.md`が存在し、`--regenerate-stage writer`でも`--stage writer`でもない場合のみ)。
- 判定条件(全て満たす場合のみ`ja_writer/revision2.md`を返す):
  1. `ja_writer/runtime_evidence.json`が存在する(無ければ`LEGACY_WRITER_PROVENANCE` STOP)。
  2. `chain_method == w1.CHAIN_METHOD`(= `"W-1"`、`er053_family_x_factlock_ja_writer_01.py` L36)(違えば`LEGACY_WRITER_PROVENANCE` STOP)。
  3. `contract.validate_annotated_b3(out_dir)`(V1〜V10、違反は`AnnotatedB3ContractViolation`)。
  4. `ev.annotated_md_sha256 == annotated.annotated_md_sha256`(違えば`PROVENANCE_MISMATCH` STOP)。
- 保護範囲: 旧Writer記事、Trial/他chain由来の記事、注記がstale/差し替えされた記事のProduction流入を防ぐ。判定は完全一致のみで例外経路はない。
- 本件の事実(INVESTIGATION_01 §4): E案マスターの無変更複製は条件2のみで`LegacyWriterProvenanceStop`。chain_methodだけ"W-1"に書換えた診断複製は条件3・4を通る(=唯一のブロッカーは`chain_method="MAQ_TRIAL_W-1"`)。ただし来歴の書換えは禁止(ユーザー条件)。

## 2. 受け入れ方式(案b)の仕様案
### 2-1 明示opt-in
- runner CLIに `--approved-quality-master <E_master_meta.jsonのpath>` を新設(entertainment runnerのみ)。**既定=未指定=現行と完全同一動作**。環境変数・設定ファイル・既定ONでの有効化は不可。
- `load_reused_ja_text(out_dir, approved_master_meta: str | None = None)`。`None`なら従来動作(分岐は`chain_method != "W-1"`かつopt-inありのときだけ新関数へ入る)。
- opt-inは「再利用(`revision2.md`既存、regenerate/stage writerでない)」経路でのみ有効。`--regenerate-stage writer` / `--stage writer` / `--regenerate-stage storyline_b3` との併用はSTOP(受入記録の対象shaが無効化されるため)。`chain_method=="W-1"`の通常記事にopt-inを付けた場合もSTOP(opt-inの意図不明=曖昧さを残さない)。

### 2-2 受理条件(全て必須、1つでも不一致→`LegacyWriterProvenanceStop`系のSTOP。従来と同扱い=課金前・fail-closed)
| ID | 条件 | 根拠/検査方法 |
|---|---|---|
| a | meta.json `status == "HUMAN_APPROVED_QUALITY_MASTER"`(完全一致)かつ `family=="X"` | `C_reference_meta.json`(次点参照)は不受理 |
| b1 | meta `source_sha256 == saved_sha256 == M`(マスター記録sha) かつ `byte_identical_to_source==true` | meta内部整合 |
| b2 | マスター本文`docs/quality/ja_quality_masters/<slug>/E_master_r2.md`をLF正規化(`\r\n`→`\n`)したsha == M | CRLF対策(2-4) |
| b3 | run dir複製の`ja_writer/runtime_evidence.json.ja_text_sha256 == M` | 4者照合の一部 |
| b4 | run dir `ja_writer/revision2.md`の**生バイト**sha == M(かつ生バイトにCRが無いこと) | CRLF変質コピーの検出 |
| c | `validate_annotated_b3`(V1〜V10)と`annotated_md_sha256`一致は**従来どおり必ず実行**(スキップ・緩和なし)。chain_method分岐の後ろに残す | U-1条件3・4を維持 |
| d | `runtime_evidence.chain_method`が列挙allowlist `{"MAQ_TRIAL_W-1"}` に**完全一致**(集合照合。startswith/部分一致/正規表現/大小無視は禁止) | ユーザー条件 |
| e | meta pathを`realpath`解決し、`<repo root>/docs/quality/ja_quality_masters/<slug>/E_master_meta.json`であること(ディレクトリ構成固定、symlink・`..`・別repo・run dir内metaは不受理) | 出所限定 |
| f | meta `slug` == path上の`<slug>` == runnerの`--slug` | テーマ一致 |
| g(推奨) | コード内pinned registry `APPROVED_QUALITY_MASTERS = {"coffee_prices": {"master_sha256": "742e7b6a...b248a", "chain_method": "MAQ_TRIAL_W-1", "decision_ref": "<DECISION_LOGエントリ名>"}}` にslugが存在し、M・chain_methodが一致 | meta.jsonだけを信頼すると、meta改竄/新規meta追加でゲートが開く。pinによりスコープ拡大が「コードcommit+レビュー」を必要とする。**Opus論点** |
- 現時点の許可対象は`coffee_prices`のE案1件のみ(hormuz/meta E案は別承認・別runであり本設計の対象外。追加は別途ユーザー承認+registry追記)。

### 2-3 来歴の不改変と受理の記録
- run dirの`ja_writer/runtime_evidence.json`は主ツリー原本からの**バイト完全コピー**(shutil.copyfile)で、runnerは一切書換えない(chain_method=`MAQ_TRIAL_W-1`、`override_reason`等もそのまま残る)。
- 受理時、run dirに新規 `ja_writer/approved_master_acceptance.json` を**新規作成のみ(既存があれば内容一致確認、不一致はSTOP。上書き・削除禁止)**。内容: `schema_version`、`accepted_at`(UTC)、`runner`・`runner_version`(runnerファイルsha)、`meta_path`(repo相対)と`meta_sha256`、`slug`、`master_sha256_lf`、`evidence_ja_text_sha256`、`revision2_raw_sha256`、`master_body_raw_sha256_worktree`(autocrlf差の参考値)、`chain_method_observed`、`chain_method_allowlist`、`annotated_md_sha256`(契約検証値)、`runtime_evidence_raw_sha256`(不変性証跡)、`approval_basis`(DECISION_LOGエントリ名=ユーザー正式決定2026-10-11 案b)、`checks`(a〜gの各PASS)。
- 後段の整合: audio runnerの`ensure_rf_record`(`er019_family_x_audio_production_runner_01.py` L1943)の三者sha照合は**英語記事**(`<level>/article.md`のsha: scaffold == source == Review Queue)であり、JA本文shaは対象外。JAは(1)`derive_japanese_title`が`runtime_evidence.json.title`、(2)`_annotation_producer`が`annotation_manifest_producer`を読むのみで、不変コピーなので影響なし。後段のsha guardは無変更で整合し、追加改修は不要。英語記事はこのrunでE案JAから新規生成されるため、新規にRF+Queue記録される。
- `cost.json`/telemetry: 記録のみ(分岐に使わない)。

### 2-4 sha正規化規約(CRLF対策)
- repoは`core.autocrlf=true`。git経由のcheckoutではLF→CRLF変換が起きる(INVESTIGATION §1)。
- **規約**: マスター本文(`E_master_r2.md`、gitに入る)のみ`\r\n→\n`正規化してsha計算する。run dir内ファイル(revision2.md・runtime_evidence.json等)は**生バイトshaそのまま**で比較し、かつrevision2.mdにCR(`\r`)があればSTOP(=LF原本から複製されたことの強制)。
- run dirの作成手順(runner外の別実行層で実施): 主ツリー(`C:\Users\tensh\eigo-radio`)の原本`er052_output/.../runs_02/coffee_prices/E/`から`shutil.copyfile`でバイト完全コピー。コピー後に各ファイルshaを原本と照合(contract V3で使う`selected_brief.md`、annotated md、sidecar、`writer_constraints`、ledger等の全ファイル)。**git経由複製は禁止**。
- 受理判定はmetaの記録sha(LF)とrun dirの実体shaを照合するため、worktree上のマスターmdがCRLFでも誤STOP/誤PASSしない。

### 2-5 ログ/telemetry
- 標準出力: 受理時 `[B3-RUNNER][U-1] APPROVED_QUALITY_MASTER accepted: slug=... master_sha=<12桁> chain_method='MAQ_TRIAL_W-1' decision_ref=...`、不受理時 `[STOP] U-1 APPROVED_MASTER_REJECTED: <失敗した条件ID>=<期待/実測>`。
- `approved_master_acceptance.json`(2-3)に判定の全件を記録。`entry_point.json`相当に`approved_quality_master`(meta path+sha)を追記のみ。
- 受理しても`chain_method`は"MAQ_TRIAL_W-1"のままで、cost.json等に「Writer来歴=MAQ_TRIAL_W-1(承認済みマスター受入)」と記録される。

## 3. U-1の保護範囲が維持される理由(opt-in下の判定表)
| ケース | opt-inなし | opt-inあり(`--approved-quality-master`) |
|---|---|---|
| 旧Writer記事(evidence無) | STOP(現行) | STOP(evidence不在は新分岐の前で従来STOP) |
| 旧Writer記事(chain_method≠allowlist) | STOP | STOP(d不一致) |
| 未承認Trial記事(status≠HUMAN_APPROVED) | STOP | STOP(a不一致) |
| C_reference(次点、承認マスターではない) | STOP | STOP(a不一致) |
| 他テーマの承認マスター | STOP | STOP(f不一致、g未登録) |
| マスター本文とrevision2.mdのsha不一致 | STOP | STOP(b2/b4) |
| evidence ja_text_sha256不一致 | STOP | STOP(b3) |
| 注記stale(annotated sha不一致/契約違反) | STOP | STOP(c、従来検査を維持) |
| chain_method="MAQ_TRIAL_W-1-x"等の類似文字列 | STOP | STOP(d完全一致) |
| meta がrun dir内/別path/symlink | STOP | STOP(e) |
| 通常W-1記事 | PASS | opt-inを付けるとSTOP(意図不明。付けなければPASS) |
| regenerate/stage writerとの併用 | 現行動作 | STOP(2-1) |
- 維持される理由: (1)既定動作は現行と同一(新分岐は`chain_method != "W-1"`かつopt-inありのときだけ)。(2)通常Writer記事のU-1条件はそのまま。(3)新規受理は「ユーザーが人間承認した特定sha・特定出所・特定chain」の閉集合(pin、g)のみで、Trial成果物の一般流入ではない。(4)V1〜V10・annotated sha一致は受理後も実行(c)。(5)全NGは従来と同じ課金前STOP(例外は`LegacyWriterProvenanceStop`のサブクラス`ApprovedMasterAcceptanceStop`を推奨=既存`assertRaises`と整合)。

## 4. 変更対象と影響範囲
- 変更: `er019_family_x_entertainment_production_runner_01.py`のみ。(1) `load_reused_ja_text`にopt-in引数と分岐。(2) 新規内部関数 `_verify_approved_quality_master(out_dir, meta_path, slug)` / `_write_acceptance_record(...)`。(3) `build_arg_parser`に`--approved-quality-master`、main L435の呼出に引数転送、regenerate/stage併用チェック。(4) 定数`APPROVED_QUALITY_MASTERS`(g)。
- 新規test: `er053_u1_approved_master_acceptance_test_01.py`。既存U-1 test(`er019_family_x_entertainment_production_runner_01_test_01.py` L181-193、`er053_c2/c4/c5`系)は無変更で全PASSすること(回帰の根拠)。
- 影響なし(根拠): (1)他Familyは本runnerを呼ばない(U-1はFamily X entertainment runner限定、CURRENT_SPEC L1182)。(2)audio runner・`er033` styles・`contract`・`w1`は変更しない(`w1.CHAIN_METHOD`も不変)。(3)`load_reused_ja_text`の他呼出はtest(`er053_c2/c4/c5`、entertainment test)のみで、既定引数のため動作不変(Grep確認)。(4)opt-in未指定の通常運用のコードパスは現行と同一。(5)Production Prompt・Routing・予算guard・regenerate上限・retry機構には触れない。

## 5. テスト計画(単体。課金0)
1. 受理OK: 合成の承認マスター一式(tmp dir、meta+master+run dir複製)でPASS、返り値=revision2.md本文、`approved_master_acceptance.json`生成、runtime_evidence.jsonが**バイト不変**。
2. NG各条件(a/b1/b2/b3/b4/c/d/e/f/g)を1件ずつ(他は正)、全てStop例外で、acceptance記録が作られないこと。
3. allowlist厳密一致: `"MAQ_TRIAL_W-1 "`(末尾空白)、`"maq_trial_w-1"`、`"MAQ_TRIAL_W-1-X"`、`"W-1"`+opt-in(意図不明STOP)、`None`、空文字。
4. 来歴不変: runtime_evidence.json・revision2.md・meta・マスター本文のshaが処理前後で変化しない(書込はacceptance.jsonのみ)。再実行の冪等性(既存acceptance内容一致ならOK、不一致STOP)。
5. CRLF: revision2.mdがCRLF変換コピー→b4でSTOP、マスター本文のみCRLF(worktree状態)→b2はLF正規化でPASS、meta shaがCRLF値ならSTOP。
6. opt-inなし回帰: `chain_method="MAQ_TRIAL_W-1"`でopt-in無し→従来どおりSTOP(既存U-1 test無変更PASS)。regenerate/stage writer併用STOP。
7. 乾式検証(課金0): 主ツリー原本からのバイト複製run dir(`run_e_tone_01`、scratch)に対し `load_reused_ja_text(out_dir, approved_master_meta=<実際のE_master_meta.json>)` を直接呼出しPASSすること(実体作成は実装レビュー後のみ)。
8. run_project_regression.pyでbaseline(failed=17/errors=75)とFAIL/ERROR集合が完全一致。

## 6. 想定工数・リスク
- 工数: **M**(実装S: 約100〜150行、test M: 20件前後+乾式、Opusレビュー反映・回帰含めM)。
- リスク: (1)meta.jsonのみ信頼だと改竄・新規meta追加で迂回可能→pin(g)で緩和(要レビュー)。(2)CRLF/autocrlfの誤判定→b2/b4の分離規約とテストで緩和。(3)受入記録が後続で参照されず見落とされる→cost.json/entry_pointへの追記で可視化。(4)将来のテーマ追加(hormuz/meta)時のスコープ拡大は別ユーザー承認+registry追記を必須とする(自動拡張なし)。(5)`MAQ_TRIAL_W-1`来歴がProduction記事に残る監査上の扱い(承認根拠はacceptance.jsonとDECISION_LOG)。

## 7. Opusレビュー依頼論点
1. 安全性: 受理条件a〜gが「Trial成果物の無条件流入」を防ぐのに十分か。pinned registry(g)の要否、pinの粒度(sha+chain+slugで足りるか、meta shaも固定すべきか)。
2. 監査可能性: 来歴不改変+acceptance.json追記方式で、後日「なぜMAQ_TRIAL_W-1がProductionに入ったか」を再構成できるか。記録項目の過不足。cost.json等への波及記載。
3. U-1整合: 既存の目的・保護範囲を弱めていないか。契約検証V1〜V10・annotated sha検査を受理後も必ず通す構造(c)になっているか。例外型の扱い(サブクラス/新型)。
4. 迂回経路: (i)opt-inを環境変数/既定/設定で暗黙に有効化できる経路が無いか、(ii)path解決(realpath/symlink/大小/UNC)、(iii)`--stage`/`--regenerate-stage`/resume・再実行時にチェックが飛ばされる経路、(iv)acceptance.jsonを先に偽造して通す経路(「既存と一致確認」で防げるか。そもそも判定は毎回フル再検証でacceptance.jsonを信用しない設計か)、(v)TOCTOU(検証後にrevision2.mdが差し替えられる)の扱い(検証時に読んだバイトをそのまま返却する=同一バイト使用で足りるか)。
5. 運用: W-1通常記事にopt-inを付けたときSTOPとする方針の妥当性。DECISION_LOGへの承認根拠名の記載方法。

## 8. Opus条件Aレビュー(GO with required fixes)の反映と実装(委任_05、2026-10-11)
実装: `er019_family_x_entertainment_production_runner_01.py`(`verify_approved_quality_master` / `precheck_approved_quality_master` / `resolve_approved_master_meta` / `append_approved_master_acceptance_record` / `write_ja_source_audit` / `APPROVED_QUALITY_MASTERS` / `ApprovedMasterAcceptanceStop`)、`er053_approved_master_rundir_builder_01.py`(run dir構成helper)、test `er053_u1_approved_master_acceptance_test_01.py`。

| Opus指摘 | 対応 |
|---|---|
| A1-1 課金前の事前検証(必須) | `main()`で`parse_args`直後(`vfl01.get_client()`・Research・B3・`os.makedirs`より前)に`precheck_approved_quality_master(args)`。a〜g全件検証。`--stage`∈{research,ledger,storyline_b3,writer}・`--regenerate-stage`∈{writer,storyline_b3}・`revision2.md`欠落・`--stop-after storyline_b3`(追加の厳格化: opt-inが黙って無視される経路)はSTOP。通常W-1記事へのopt-inはd(allowlist外)でSTOP。 |
| A1-2 pinned registry(必須) | コード内定数`APPROVED_QUALITY_MASTERS`。coffee_prices E案1件のみ。pin項目=`master_sha256_lf`/`chain_method`/`ledger_sha256`/`selected_brief_sha256_raw`/`runtime_evidence_sha256_raw`/`decision_ref`。run dirの生バイトと照合(g)。加えてmeta `fact_ledger.sha256`・`selected_fact_ids`とsidecar/ledgerを照合(g2)。 |
| A1-4 acceptance冪等性バグ回避 | acceptanceは`ja_writer/approved_master_acceptance.jsonl`へ**追記のみ**(1実行1行、既存行不変)。受理記録は判定の入力にしない(毎回フル再検証)。opt-in無しの再実行は記録があっても従来U-1 STOP。 |
| A1-5 TOCTOU | `revision2.md`・`runtime_evidence.json`は1回だけbytesで読み、そのbytesでsha/CR検査・decodeして返す(`load_text`再読込なし)。testで検証後差替えを注入し検証時bytesが返ることを固定。 |
| A2 後段可視化 | `entry_point.json`に`approved_quality_master`(meta path/sha/slug/master sha/ja_source)、`cost.json`に`ja_source`、b1b/a2の`audit/ja_source.json`に`approved_quality_master:<slug>@<sha12>`を記録(記録専用)。 |
| 例外型 | `ApprovedMasterAcceptanceStop(LegacyWriterProvenanceStop)`。メッセージ先頭に条件ID(`APPROVED_MASTER_REJECTED: <cond>=...`)。 |
| 条件e | `os.path.realpath`+`normcase`+`commonpath`+期待パスとの厳密一致。UNC・`..`・symlink/junction(abspathとrealpathの不一致)・run dir内metaを拒否。path slug不一致は(f以前に)eで拒否。 |

受理記録項目: meta path/sha、各sha(master LF/worktree生/evidence/revision2/annotated/ledger/brief/evidence生)、各条件結果、受理時刻(UTC)、decision_ref、runner version(runner file sha)・runner git HEAD、複製元原本dirと複製全ファイルの生sha表(builderの`approved_master_rundir_build.json`から転記+現在の生sha)、registryスナップショット、meta `user_eval_date`/`note`、CLI引数。

### 8-1 registry値の算出手順(主ツリー原本から、2026-10-11)
原本dir: 主ツリー `C:/Users/tensh/eigo-radio/er052_output/ja_article_quality_model_allocation_trial_01/runs_02/coffee_prices/E/`(コミット`2dde32e6`)。`sha256sum`(生バイト)で算出:
- `master_sha256_lf` = `ja_writer/revision2.md`(=`export/r2.md`=`E_master_r2.md`のLF正規化)= `742e7b6a7fe43f1bd8e6106fc5892720124e0a174c6bb1e0b63e70a5b3eb248a`(`E_master_meta.json`の`source_sha256`=`saved_sha256`と一致)
- `ledger_sha256` = `research_ledger/verified_fact_ledger.txt` = `e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b`(**`E_master_meta.json` `fact_ledger.sha256`と一致を確認**)
- `selected_brief_sha256_raw` = `storyline_b3/selected_brief.md` = `5acded774f71033ffba90ca7cb29577d3aca1094458e9f7be9adcd757c5d729b`(sidecar `brief_sha256`と一致)
- `runtime_evidence_sha256_raw` = `ja_writer/runtime_evidence.json` = `241c0401a8c74a416e75c31c7f3ae3303ada607ffead8b0057a3ec4b9edabeae`
- `chain_method` = `MAQ_TRIAL_W-1`(同evidence)。

registry追加(他テーマ・別マスター)は、コードcommit+レビュー+人間ユーザー承認が必須(自動拡張なし)。

### 8-2 run dir構成手順(git経由禁止)
`python er053_approved_master_rundir_builder_01.py --origin-dir <主ツリー原本E dir> --out-dir er019_output/coffee_prices/run_e_tone_01`。`shutil.copyfile`のバイト完全コピー+コピー後sha照合。対象=research_ledger/verified_fact_ledger.txt・storyline_b3/直下全ファイル・ja_writer/配下全ファイル(計21ファイル)。コピーしない=raw_usage_log.jsonl・cost_ledger_maq_01.jsonl・usage.json・export/・原本トップruntime_evidence.json(新runのコスト集計を汚さない)。既存ファイルは生sha一致のみ許可、不一致はSTOP(上書きしない)。
`er019_output/coffee_prices/run_e_tone_01/`はgit commitしない。理由: `core.autocrlf=true`で別checkout時にLF->CRLF変換され契約V3/ledger sha・revision2.mdのb4(CR検査)が壊れるため(master複製はgit経由禁止)。必要時はbuilderで主ツリー原本から再構成する。なお既存`run_l3_01`等のrun dirは過去commitでtrackedだが、通常Production生成物でありmaster複製ではない。

### 8-3 実装中に判明した注意点
- `run_annotation_producer`(`main`が既存B3再利用時にも毎回呼ぶ決定論producer)は注記artifactを削除して再生成する。scratch複製での乾式確認では`selected_brief_annotated.md`/`annotation.json`/`writer_constraints.txt`/`fact_selection_evidence.json`は生sha不変、`annotation_manifest.json`のみsha変化(再生成)、`annotated_md_sha256`=`249b0c08...`不変、契約V1〜V10 PASS・事前検証PASS。pinned registryの対象は不変のファイルのみ(manifestは含めない)。
- 既存`er053_c4_wiring_test_01.py::test_no_switch_cli_or_env_for_annotation`は`build_arg_parser`のオプション許可リストを固定している。新CLI`--approved-quality-master`の追加に伴い、許可リストへ1要素追加した(同testの`os.environ`/`getenv`不在アサーションは無変更で維持)。
