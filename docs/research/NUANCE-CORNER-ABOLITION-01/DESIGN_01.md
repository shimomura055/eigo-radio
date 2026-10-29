# DESIGN_01 現行ニュアンス解説コーナーの撤去設計(NUANCE-CORNER-ABOLITION-01 委任_01、2026-10-30、設計のみ・Production code未編集・API 0)

前提: ユーザー決定(原文=`docs/pm/delegation_log/2026-10-30_NUANCE-CORNER-ABOLITION-01_USER.md`)=①ニュアンス解説廃止・v3 REJECTED・ニュアンス以外の承認済み仕様は維持・過去完成記事の本文/音声は不変・遡及撤去の未承認一括変更なし ②One Step Furtherは別仕様(本設計に含めず、配線もしない) ③Y姓記事は最終完成承認保留。影響範囲=`IMPACT_01.md`。

## 1. 方針(Fable既定案に沿う)
**生成・HR・表示をProductionから恒久撤去する。flag(既定OFF)方式は採らない**(廃止は承認済み。flagは「戻せる未承認機能」用の仕組みで、撤去対象に適用すると死コードと検査が残り、削減目的に反する)。
核心: **既存のLEGACY経路(`nuance_spec.json`無し)が既に「生成0・待機0・表示0・期待ブロック0」を全工程で保証している**(IMPACT §0-1)。これを唯一の経路にするので、新しい分岐やflagは増えない。

## 2. 撤去の2段(委任_02で1委任・2 commit)
- **Step A(振る舞い撤去=小差分・最優先)**: 3 runner(er019/er121/er026)からN1呼出・finalize・nuance引数・`nuance_pending`・page検査のnuance期待値を削除。`er120_part2_wiring_01.py`/`er120_part2_grammar_production_01.py`のnuance引数・表示関数を削除。フォームexporter/V3フォーム/`form_logic.js`/`cmd_from_form`/CLI/`er119_kp_wiring`のnuance分岐を削除。End User adapter schemaからnuance撤去。**この時点で、既存run(specあり)でも生成0・HR0・表示0になる**(ファイルを読まない=fail-closed、§3)。
- **Step B(死コード整理)**: `er134_nuance_explanation_01.py`削除、`er128`のnuance関数群、`er119_kp_human_review_01`のnuance列、`er006`のprocess2件、専用test6本、混在testのassert編集、`er119_isolation_test`リスト修正、`derive_assets`のJ9-J11。
Step AとBを分ける理由: Step A単体で目的(以後ニュアンスが出ない・費用が出ない)を達成でき、Step Bはtest PASSの下で機械的に進められる。雪女との競合時間を短くできる(§7)。

## 3. 旧データの扱い(読取互換=「存在しても読まない・表示しない」)
| 旧データ | 扱い |
|---|---|
| run内の`nuance_spec.json`/`nuance_candidate.json`/`nuance_failed.json`/`confirmed_nuance.json`/`nuance_result.json`/`nuance_redundancy_alarm.json` | 削除しない(過去記録の保全)。読まない。pages/page_verify/HR再出力のいずれも参照しない |
| 確定record `rec["nuance"]`(Y姓run_02) | `_nuance_problems`撤去により検査されない。再確定(revise/rebind)時の`prev["nuance"]`引継ぎ(er128:301)も撤去=新recにnuanceキーは残らない |
| 旧AIF2コード/`schema_minor=2`・`selection.nuance`付きpayload(旧V3フォームで回答済みの場合) | **明示エラーで拒否**(`NUANCE_CORNER_ABOLISHED: フォームを再取得してください`)。黙って無視しない(回答内容が反映されたと誤認させないため)。X 4記事はHR待ち=未回答のため実害想定なし(要確認: 4 formの回答有無はFable/ユーザー) |
| 旧`article.json`の`nuance`配列/dev `index.html`の「ニュアンス解説」節 | End User adapterが**節を検出したらSTOP**(`ENDUSER_NUANCE_CORNER_ABOLISHED`=旧ページからの再derive防止)。新スキーマは`nuance`キーなし |
| 公開済みenduserスナップショット(5ディレクトリのapp.js/article.json) | 過去成果物として不変(データ0件の分岐は不活性) |

## 4. 逆流防止ガード(最小限残す)
`NUANCE_HEADING`定数と`count_nuance_blocks`(Y/Zのpage_verify)を**「ニュアンス解説ブロックが0個であること」の検査**として残す(旧期待「採用時のみ1」→「常に0」)。理由: 廃止後に旧run成果物やキャッシュがページへ混入する経路があれば、静かに復活せず検出できる。コスト=関数1つ+数行。Opus論点Q2(ガード残置vs完全Dangling撤去)。

## 5. Family別・level別の正式経路(Step A後)
| Family | 初回経路 | resume/retry/regeneration | 変更点 |
|---|---|---|---|
| X(er019) | scaffold→(KP/文法HR待機rc=4)→player。ニュアンスのN1・pending・player入口finalizeを削除 | rc=4待機はKP/文法のみ。`nuance_enabled`引数・`nuance_call_fn/nuance_judge_fn`削除 | er019:793-811,925,1021-1067,3951,4110-4132 |
| Y(er121) | kp→…→pages→page_verify。`_nuance_cand_step`/`_assert_nuance_final`削除 | `summary["nuance_cand_*"]`が出ない。旧summaryは読まない | er121:35,594-663,1061-1102,1325-1336 |
| Z(er026) | 同上 | 同上 | er026:1238,1897-1929,2233-2311,2729-2731 |
| 全level | Std(a2)/Adv(b1b)共通。level別の差異なし(level別が増えない) | | |
共有経路(`er120_part2_wiring.compose_page_html`/`verify_outputs`/`expected_blocks`)を1か所修正すれば3 Familyに及ぶ構造のため、3 runnerの各呼出元修正+共有1か所で完結。Family A・B・C非接触(`er119_isolation_test_01`で確認、er134削除に合わせ更新)。

## 6. 個別対象の扱い案
- **Y姓記事(未承認候補・承認保留)**: 本文・音声・TTS・gateは不変。Step A後に`py er121_family_y_runner_01.py --stage pages`→`--stage page_verify`(API 0)を再実行し、`user_test/family_y_production_surname_choice_01/index.html`のニュアンスブロックを2→0へ、`enduser/data/article.json`の`nuance`を空/キー削除へ。End User版は`er135`のproduce手順(API 0)で再生成。※OPEN-598は「ニュアンス暫定反映は廃止対象」と記録済み。OSF採否前でも本文・音声不変の表示撤去のため、承認保留と矛盾しない(Fable判断で実施時期を指定。実施しない場合は旧ページが「廃止対象のニュアンス入り候補」のまま残る旨を注記)。
- **Family X 4記事(HR待ち)**: Step A後に`export_form_data_01.py`(`--nuance-study-dir`なし)で8フォームdata(`user_test/selection_form_v3/data/*__prod.json`)を再出力(API 0)→V3フォーム再提示。KP/文法の候補・提示順・sha(candidates_sha/text_sha)はニュアンス非依存のため不変の見込み(委任_02で比較して確認)。HR依頼書(readable/request)もニュアンス節なしに再生成。ユーザーへの再提示物は「フォーム更新(ニュアンス欄が消えただけ)」。
- **完成承認済み記事(月/メロス/再配達料/藪の中)**: 全て表示0件=変更不要。公開ページ・音声・本文は一切触らない。
- **雪女(Z、制作中)**: §7。
- **DEV `user_test/dev_enduser_page_01`(仮データ)**: 提案=DEV app.js/style.css/data(`ai_island.json`・`moon.json`)のnuance部分もStep Bで撤去(`derive_assets_01`のJ9-J11とrev01-e/app.jsと同期させないと、derive時に置換元が見つからずSTOPするため)。DEVは本番非公開の検証用。
- **Trial/evidence(docs/research)・OSF Trial**: 不変。

## 7. 並行Worker・スケジューリング
- 雪女のer026 runnerは、Pythonがprocess起動時にimport済みのため、実行中のprocessはファイル編集の影響を受けない。次のresume/段起動から新コード(ニュアンスなし)になる=混在状態は起きない。
- **雪女がKP stageを廃止実装より先に実行した場合**: 新規KP review作成でspecが発行され、候補1件×2level(約¥0.47)とHR項目が出る。廃止実装後はspec/候補を無視(§3)するため誤表示・誤停止はないが、費用とHR項目の分だけ無駄。→推奨: Step A(特にer026の呼出削除、約30行)を雪女のKP stage前に入れる。雪女workerとer026編集の競合は「編集前にFableが雪女workerの段境界を確認→Step Aのer026部分だけ先行commit」で回避(競合時は解消せず報告)。
- OSF Trial: Trial専用ファイルのみ編集=競合なし。Step Aは`tools/osf01_*`を変更しない。
- X 4記事HR待ち: Step A後のフォーム再出力まで、ユーザーへ現行フォームの回答を促さない(Fable運用)。

## 8. 検証計画(委任_02)
1. **新規「廃止ガード」test 1本**(`er136_nuance_abolition_test_01.py`案): (a)3 runner+共有builderに`er134`importが無い (b)`nuance_spec.json`+`nuance_result.json(ADOPTED)`を置いたcopy-runでも`compose`出力・`verify_outputs`・End User adapter出力のニュアンスが0 (c)旧AIF2/`schema_minor=2`が`NUANCE_CORNER_ABOLISHED`で拒否 (d)End Userに旧「ニュアンス解説」節が残っていればSTOP (e)Dangling Grep(Production `*.py/*.js`に`er134_nuance`/`nuance_spec`/`finalize_nuance`が無い)。
2. 回帰: 混在test編集後に`er120_*`/`er119_*`/`er121_*`/`er026_*`/`er135_*`/`er128_*`/`er019_*`/`er053`/`er054`/`er009_*routing*`の全関連testがPASS(ベースライン=撤去前の同一test群のPASS件数を記録)。
3. **copy-run(API 0)**: X(moon系 or X4のcopy)/Y(surname run_02 copy)/Z(copy)で`pages`段→ニュアンスブロック0・`page_verify` PASS。specありcopyとspecなしcopyの出力が同一であること(spec無視の証明)。
4. End User: adapter produceがPASS(`er135_enduser_page_test_01`+`er135_enduser_page_verify_01`、nuanceなしスキーマ)。
5. **runtime evidence(実記事)**: Y姓記事のpages再実行(index.html/article.jsonからニュアンス0を実測)、Family X 4記事のフォーム再出力(8 data JSONに`nuance_spec`無し、V3フォームをnodeでレンダ[`form_node_check.js`既存]して欄が無い・送信可)、雪女のplan/KP段(新規KP review作成後も`nuance_spec.json`が作られない・N1呼出0=API呼出ログにNUANCE process無し)。
6. Dangling Grep: `rg -i "nuance|ニュアンス解説"`をProduction `*.py/*.js/*.html`に対して実行し、残存は(a)文法見出し`意味・ニュアンス・表現効果`(b)Family Y/Writerの(nuance)語(c)ガード`NUANCE_HEADING/count_nuance_blocks`(d)`NUANCE_CORNER_ABOLISHED`拒否のみであること。
7. SSOT: CURRENT_SPEC(`:1997`のHR-SELECTION-FLOW行のニュアンス重複判定部、`:2119-2120`ニュアンス解説PRODUCTION_WIRED節、`:2195,2696,3278-3279`の言及)を「廃止(撤去済み)」へ、OPEN-600(仕様②のニュアンス部分)、OPEN-609/610/611/617、DECISION_LOG。Git反映。

## 9. 削減見込み
| 項目 | 現状 | 撤去後 |
|---|---|---|
| 記事費用 | 約¥0.47/記事セット(生成¥0.17-0.33/level+判定)。70円の約0.7% | ¥0 |
| E2E予算見積 | er121/er026 `nuance:1.0`円/level/stage | 約¥2/記事の見積減 |
| HR項目 | Std/Adv各最大1項目+重複アラーム行 | 0(KP/文法HRは不変) |
| 検査 | N1(構造/引用/重複判定)・N3確定・page期待数/順序/dev detail・End User corner・HR validators・AIF2 | ガード1個のみ |
| コード | 本体1,177行+配線約700行+test約2,600行/134件 | ガードtest数十行 |
| 時間 | LLM2回/level+HR判断 | 0(実測は委任_02で取得) |
品質影響: ユーザー決定により現行ニュアンスの学習価値不足が理由=学習コンテンツ純減。ニュアンス以外の承認済み仕様は不変(Part 1/Part 2文法・KP・Word・HR flow仕様①・KP側の仕様②)。One Step Furtherの追加は別仕様変更=本設計に含めない。

## 10. 論点(Opus条件Aレビュー用)
- Q1 旧データを「読まない」(§3)で十分か。specファイルが残るrunで、将来の別機能(OSF採用時)が同名ファイルを再利用して衝突しないか。→OSFは別名前空間にする前提で良いか。
- Q2 逆流防止ガード(`count_nuance_blocks`)の残置は妥当か、完全撤去してDangling Grepのみにすべきか(推奨: 残置)。
- Q3 旧AIF2コードを明示拒否(推奨)か、黙って無視か。HR回答済みフォームが存在する場合の扱い。
- Q4 `er006` PROCESS_MODEL_MAPの2 processを撤去(推奨・3 testの「追加のみ」閉集合も更新)か、停止済み注記で残置か。過去usage logの再集計に影響しないこと(`er053_cost_aggregate_01.py`は`PROCESS_MODEL_MAP`を参照しない=確認済み)。
- Q5 Step A/B分割と、雪女er026編集のタイミング(§7)で未承認変更の混入・STOP迂回が無いか。
- Q6 Y姓記事のpages再生成を、OSF採否前(承認保留中)に行ってよいか(本文・音声は不変、ニュアンス表示のみ消える)。
- Q7 DEV仮データまで撤去するか(推奨)、DEVは残置するか。
