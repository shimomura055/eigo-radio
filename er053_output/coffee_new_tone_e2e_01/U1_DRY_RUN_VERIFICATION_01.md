# U-1限定受入(案b) 乾式検証 01(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_05、2026-10-11)
API課金0(LLM/TTS/ASR呼出なし)。実装: `er019_family_x_entertainment_production_runner_01.py`(worktree `C:/Users/tensh/eigo-radio-tone`、branch feature/coffee-new-tone-01、HEAD 1b35eb90+未commit実装)。使用モデル: なし(API呼出0)。

## 1. run dir構成(`er019_output/coffee_prices/run_e_tone_01/`、git非管理)
`python er053_approved_master_rundir_builder_01.py --origin-dir <主ツリーE原本> --out-dir er019_output/coffee_prices/run_e_tone_01`
- 複製元: `C:\Users\tensh\eigo-radio\er052_output\ja_article_quality_model_allocation_trial_01\runs_02\coffee_prices\E`
- 方式: shutil.copyfile(バイト完全コピー)+コピー後に全ファイルsha照合(21ファイル全一致)。コピー非対象: raw_usage_log.jsonl/cost_ledger_maq_01.jsonl/usage.json/export/原本トップruntime_evidence.json。
- 複製ファイル生sha表(origin==copy):

| file | sha256 |
|---|---|
| `ja_writer/factlock/r0.md` | `ffeadb28c0bb28ac219efdeb7b8081466cdb47bf486a2d91f3aadd2694915de3` |
| `ja_writer/factlock/r0_meta.json` | `f1b7a742f31a5bb2980d664fcd1b96e5dd4d6153b16e0638275436c1d6efbdb0` |
| `ja_writer/factlock/r0_with_tags.md` | `b1445483496ba80a98f632553954d5a111683dc1733f08547af6a2f945693a55` |
| `ja_writer/factlock/r1.p1.md` | `3a5f023ac5d4fa25409e6dd066b6440babcc325a38af631fb05ec02a65f994d1` |
| `ja_writer/factlock/r1.raw.md` | `5c79adca698de1a9881e39e6fad45cd52332f1ac59f8f2cb6d13da1436a2ff4b` |
| `ja_writer/factlock/r1.response.json` | `4073f29dcffbd540c70f5bab87b5d3643316e1627b2587801eb174642a0ed850` |
| `ja_writer/factlock/r2.raw.md` | `d3af58221a0b35a4eba9cb90a880d5c7e31e3a8cce140880379dbed7ff1b199c` |
| `ja_writer/factlock/r2.response.json` | `7986b83b5522c854cb3ee891642b0b29a97aa092688f0cb14d5a514b41b1dd21` |
| `ja_writer/original.md` | `ffeadb28c0bb28ac219efdeb7b8081466cdb47bf486a2d91f3aadd2694915de3` |
| `ja_writer/revision1.md` | `3a5f023ac5d4fa25409e6dd066b6440babcc325a38af631fb05ec02a65f994d1` |
| `ja_writer/revision2.md` | `742e7b6a7fe43f1bd8e6106fc5892720124e0a174c6bb1e0b63e70a5b3eb248a` |
| `ja_writer/runtime_evidence.json` | `241c0401a8c74a416e75c31c7f3ae3303ada607ffead8b0057a3ec4b9edabeae` |
| `research_ledger/verified_fact_ledger.txt` | `e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b` |
| `storyline_b3/annotation.json` | `0f6a298e6ab0ee541e0bdb6ea00fbfde67d0cab27c098679ead5d96a693a354c` |
| `storyline_b3/annotation_manifest.json` | `d5222a3106b6eb146ec1dc81cf88394e40b041148c7f2d6c73a6ce08ed86f0d1` |
| `storyline_b3/fact_selection_evidence.json` | `5327b1a7433e4810771c8fcc4586c5afb4b1d47881ed7d9199936d9c7164b099` |
| `storyline_b3/full_ledger.json` | `fc830d06fa28a081666beb154aa98e0e81c59b993179260ba6efbd226871763c` |
| `storyline_b3/runtime_evidence.json` | `49f0bf574b98e4cd0f50a1cdefc628df2eec86c5d08701e940b0972439b06f8a` |
| `storyline_b3/selected_brief.md` | `5acded774f71033ffba90ca7cb29577d3aca1094458e9f7be9adcd757c5d729b` |
| `storyline_b3/selected_brief_annotated.md` | `249b0c0838c189fd6ba70da9d42ba2fb5e0d3ed0bf9a1a257d3b65183f343425` |
| `storyline_b3/writer_constraints.txt` | `8662255da6f87b37476771fcaa741f0f6818cc70ed82d489f15d0d26edabb2dc` |

## 2. 検証結果
| # | 検証 | 結果 |
|---|---|---|
| 1 | `load_reused_ja_text(run_dir)`(opt-in無し) | 従来どおり`LegacyWriterProvenanceStop`(`U-1 LEGACY_WRITER_PROVENANCE: chain_method='MAQ_TRIAL_W-1'は'W-1'ではありません`)。`ApprovedMasterAcceptanceStop`ではない |
| 2 | `precheck_approved_quality_master(args: stage=all)` | PASS(課金前、記録なし)。ja_source=`approved_quality_master:coffee_prices@742e7b6a7fe4` |
| 3 | `load_reused_ja_text(run_dir, approved_quality_master=<repo>/docs/quality/ja_quality_masters/coffee_prices/E_master_meta.json, slug='coffee_prices')` | **受理PASS、916文字読込**(読込本文のutf-8 sha=`742e7b6a...b248a`=マスターsha)。条件a/b1/b2/b3/b4/c(V1〜V10+annotated sha `249b0c08...`)/d/e/f/g/g2 全PASS |
| 4 | `ja_writer/runtime_evidence.json`のsha(受理前後) | 不変(`241c0401a8c74a416e75c31c7f3ae3303ada607ffead8b0057a3ec4b9edabeae`、chain_method=MAQ_TRIAL_W-1のまま) |
| 5 | `ja_writer/approved_master_acceptance.jsonl` | 1行追記(1実行1行)。内容: decision_ref、runner_version(runner sha `1946c9e3...`)、runner_git_head=`1b35eb90`、meta path/sha(`4b533220...`)、各sha、checks全PASS、registry snapshot、meta user_eval_date=2026-10-11/note、cli、複製元dir+生sha表(現在値と全件一致) |
| 6 | 記録が存在する状態でopt-in無し再呼出 | 従来どおり`LegacyWriterProvenanceStop`(記録は判定入力にならない) |
| 7 | CLI `--approved-quality-master <meta> --stage writer` | `pre.stage`で課金前STOP(`get_client`以前) |
| 8 | CLI `--approved-quality-master <主ツリーのmeta絶対パス>`(repo root外) | `e`で課金前STOP |
| 9 | scratch複製に`run_annotation_producer`(mainが再利用時にも呼ぶ決定論producer)を適用後に事前検証 | PASS。`selected_brief_annotated.md`(`249b0c08...`)/`annotation.json`/`writer_constraints.txt`/`fact_selection_evidence.json`/`revision2.md`/`runtime_evidence.json`は生sha不変、`annotation_manifest.json`のみ再生成でsha変化(`d5222a31...`->`9f1196e3...`、pin対象外)。契約V1〜V10 PASS |

## 3. 備考
- 実run(`--stage all`でAdvanced/Standard英訳生成)は未実施(API課金を伴うため別途ユーザー指示)。
- `er019_output/coffee_prices/run_e_tone_01/`はgit commitしない(autocrlfで再checkout時に生バイトが変わるため。builderで再構成可能)。

## 4. 回帰(run_project_regression.py)
collected=5446 passed=5308 failed=17 errors=75 skipped=38(baseline 02: 5400/5262/17/75/38)。差分は collected +46 / passed +46(新test `er053_u1_approved_master_acceptance_test_01.py` 46件)。FAIL/ERROR行(sort -u)93行は baseline 02 の93行と完全一致(diff空、新規fail 0)。
既存U-1 test(er019_family_x_entertainment_production_runner_01_test_01 / er053_c2 / c4 / c5)は118件PASS(c4は上記CLI許可リスト1要素追加のみ)。
