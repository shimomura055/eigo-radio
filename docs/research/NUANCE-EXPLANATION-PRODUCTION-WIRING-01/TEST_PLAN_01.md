# TEST_PLAN_01 ニュアンス解説 Production配線 テスト計画(NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_01a)

設計=`WIRING_DESIGN_01.md`、現状=`CURRENT_STATE_01.md`。本書は計画のみ(実装・実行は後続委任)。受入条件=ユーザー原文§5。
実行環境: `.venv\Scripts\python.exe -m unittest <module> -v`(既存testと同じ。各testは先頭で`import test_state_isolation_01`を行い、共有store・実stateを汚さない)。
新規testは`er134_*_test_01.py`。LLMは全てmock(`call_fn`/`judge_fn`注入)で、実APIはruntime evidence(§7)のみ。

## 1. 方針

- **期待値は新仕様(文法0件=非表示)で書く。旧固定文面(`ZERO_P2`)を期待値にするtestは書かない。** 既存7ファイルの該当assertは是正する(CURRENT_STATE §5)。
- **遡及なし(LEGACY)の不変**: `nuance_spec.json`が無い既存run・既存データのフォーム出力(`AIF1`)・ページ(文法SELECTED時)はバイト不変であることを**実装前に取得したgolden**と比較する(実装着手時に現コードで`compose_study_html`/フォーム`buildReadable`/`makeCode`の出力を固定fixtureへ保存してから変更する)。
- 既存fixture再利用: `er120_part2_mock_01.py`、`er121_family_y_mock_01.py`、`er122_fz_ctx_fakes_01.py`、`er119_test_support_01.py`、`er127_test_fakes_01.py`。

## 2. 単体(core module `er134_nuance_explanation_01.py`)

| ID | 検証 | 期待 |
|---|---|---|
| U-1 | 候補が0件/1件のみ。LLMが2件以上返したmock | 2件目以降は構造検査で拒否(技術retry→それでも不正=`FAILED_TECHNICAL`、2件を採用しない)。schema上`candidate`は単一 |
| U-2 | `candidate:null`+理由のmock応答 | `status=NO_CANDIDATE`、`no_candidate_reason`保存、判定callは**呼ばれない**(call数assert) |
| U-3 | 構造重複: `focus_terms`が暫定選定の`used_form`と完全一致/語列部分一致(所有格・`one's`・屈折差) | Stage 1 fail→`candidate=null`・`overlap_ng`・`rejected_candidate_audit`に全文保存 |
| U-4 | 構造は通るがLLM判定で同一焦点(`same_focus:true`、表現は別) | Stage 2 fail→同上(**文字列一致でなく焦点で落ちる**ことの証明) |
| U-5 | 文中にKP表現が登場するだけで焦点は別(`same_focus:false`) | pass(仕様B「登場自体は問題ない」) |
| U-6 | 暫定選定でなくpoolの別項目と同一焦点 | pass+`pool_conflicts`に当該`candidate_id`が記録される |
| U-7 | 文法Top1と同一焦点/Top2と同一焦点 | Top1(暫定)=fail、Top2=`pool_conflicts` |
| U-8 | 判定LLMのJSON不正×2 | 安全側fail(`overlap_unverified`)で候補破棄。HRに出ない |
| U-9 | `quote_en`が本文に無い/複数文 | 技術失敗(retry後も不正なら`FAILED_TECHNICAL`) |
| U-10 | 応答modelが期待と違う | STOP(fallbackしない)。`routing.require_model`契約 |
| U-11 | `candidate_sha256`の決定性・正規化(空白/引用符) | 同入力で同sha、改変で別sha |
| U-12 | Prompt: 全文に`Part 4`/`Think & Express`/複数テーマ指示を含まない(未承認仕様の暗黙導入防止) | Grepで0件。`prompt_sha`が固定値と一致 |
| U-13 | Prompt isolation: 本文・pool・文法がPromptに載り、Family A/B/Cの定数を参照しない | `er119_isolation_test_01.py`型のimport検査 |
| U-14 | AUTO採用run(`UNREVIEWED_AUTO_ADOPTED`) | 生成0 call・`NO_CANDIDATE(auto_adopted_no_human_review)` |
| U-15 | LEGACY(`nuance_spec.json`無し+KP確定済) | 生成0 call・状態`LEGACY`・待機/表示なし |
| U-16 | N0: 新規run(KP未確定)で`nuance_spec`発行、再実行で不変(冪等)、KP確定後は新規発行しない | マークの発行条件 |

## 3. Human Review(採用・不採用・未回答の保存/反映)

| ID | 検証 | 期待 |
|---|---|---|
| H-1 | フォームJS(`FormLogic`)純関数: 状態`adopt/reject/undecided/n/a`、`nuanceBlocked`、`undecided`で送信/コピー停止、候補なしは`n/a` | node+pythonの往復(既存`TEST_06/07`型) |
| H-2 | `adopt`+選択中KP/Word/文法が`pool_conflicts`に含まれる | JSで送信停止、`confirm`でもISSUE rc=4(何も保存されない=確定レコード・sidecar・文法reviewが不変) |
| H-3 | `AIF2`照合コード: 生成→復元の往復一致。`nuance_spec`無しデータは`AIF1`のまま・出力バイト不変 | golden比較 |
| H-4 | 復元: ニュアンス本文の改変/欠落/決定行の欠如/コード破損 | `RestoreError`(fail-closed、推測復元しない) |
| H-5 | confirm 採用 | `confirmed_nuance.json`(decision=adopted、`confirmation_id`=KP確定レコードと同一、`candidate`逐語、`confirmed_against`)、KP/文法の確定は従来と同一結果 |
| H-6 | confirm 不採用 | decision=rejected。`nuance_result.status=REJECTED`。代替候補を生成しない(生成call数assert=0) |
| H-7 | confirm 未回答(候補ありで`selection.nuance`なし) | ISSUE rc=4。黙って不採用にしない。何も保存しない |
| H-8 | 候補なしrunの確定 | 従来payload(`schema_minor`1)も受理。ニュアンス関連ファイル=`NO_CANDIDATE`のみ |
| H-9 | stale form: 古い`candidates_sha256`/`candidate_sha256`/`text_sha256` | ISSUE rc=4(`raise_issue`型)。確定を黙って上書きしない |
| H-10 | 同一payload再送(冪等)・確定後の別決定 | 同一=変更なし。別決定=拒否(`guard_nuance`、変更はrevoke経由) |
| H-11 | 統合依頼書: KP+文法+ニュアンスのpendingが`review_request.md`1つ・rc=4が1回 | `write_unified_request`出力に3 kind |
| H-12 | CLI `nuance-select`(フォーム非経由): KP未確定は拒否、確定後は採用/不採用が保存 | |
| H-13 | `--grammar-pending`(KP先行確定)時のニュアンス | 文法確定時に併せて検証・確定(pool_conflictsの文法側を確定後に評価) |
| H-14 | 既存KP/Word/文法のHRテスト(`er119_*_test_01`、`er128_*_test_01`、`er128_form_readable_restore_*`、`er119_x/z_wiring_test_01`)全件 | 無変更でPASS(Regressionなし) |

## 4. 表示(DOM/HTML) — ニュアンス{採用/不採用/候補なし/LEGACY} × 文法{採用/0件}

`compose_page_html`と各runnerのページ生成が出力するHTML文字列(および`level_section_html`で切り出した当該levelの節)で検査。

| ニュアンス \ 文法 | 文法 採用(SELECTED) | 文法 0件 |
|---|---|---|
| 採用 | D-1: Part1→文法→ニュアンスの順。見出し各1個 | D-2: 文法見出し・`ZERO_P2`なし。ニュアンスのみ。CSSがニュアンスブロックに付く |
| 不採用 | D-3: 文法のみ。`Nuance`見出しなし | D-4: **study出力が空文字**(Part 1も無い場合)またはPart 1のみ。`<h3>Grammar`なし/`<h3>Nuance`なし |
| 候補なし | D-5: D-3と同一 | D-6: D-4と同一 |
| LEGACY | D-7: 旧出力とバイト一致(golden) | D-8: 文法節のみ非表示(仕様C)。ニュアンス関連はなし |

全組合せ共通の否定検査(`count_empty_study_sections`等): `<section class='study'>`の中身が空/見出しのみ、`<h3>Grammar &amp; Sentence Structure</h3>`の後ろに説明が無い、固定文面「このPartで特に取り上げる難所」、`Nuance`見出しの後ろが空、プレースホルダー(`（なし）`/`候補なし`等)がHTMLにもmdにも**存在しない**。
- D-9: Part 1が空かつ文法0件かつニュアンス採用のとき、`STUDY_CSS`が出力に1度だけ含まれる。3つとも空のとき`<style>`も含まれない。
- D-10: `verify_selection_matches_outputs`/Y・Z `_verify_part2_outputs`/X player検査が、0件で**期待0個**・SELECTEDで**期待1個**を受理し、取り違え(Std結果がAdv節にある等)を従来どおり検出。ニュアンスは`ADOPTED`で期待1個、他で0個。
- D-11: 同一入力で2回描画して同一HTML(決定論)。LLM関数を渡さない・呼べない構造(引数にLLM関数なし)を`inspect.signature`で確認。
- D-12: ページ再構築(Z `--stages provision_shell,gate,assemble,pages,page_verify` / Y `pages,page_verify`)が新規API 0で完了し、採否・表示状態が不変。
- D-13: 開発確認用の個別ページ(Zの`standard.html`/`advanced.html`)にニュアンス/文法ブロックが載らない(試聴`index.html`の各節のみ。`FAMILY_Z_PART2_ON_DEV_DETAIL_PAGE`と同規則)。

## 5. resume / regeneration / retry / fallback

| ID | 検証 | 期待 |
|---|---|---|
| R-1 | resume(同コマンド再実行)×{候補のみ/採用確定/不採用確定} | API 0、候補sha・採否・`nuance_result`不変 |
| R-2 | reselect(KP候補doc変更)×確定前 | 旧候補を`nuance_candidate.<tag>.json`へ退避、N1が1回だけ再実行(call数assert)。上限`RESELECT_MAX`=2 |
| R-3 | reselect×ニュアンス確定済 | 再生成0。確定sidecarは`confirmation_id`で結ばれ、KP revokeが無い限り不変 |
| R-4 | 不採用確定後に制作を再実行 | 次点候補を生成しない(call数0) |
| R-5 | 本文変更(Local Rewrite)×採用確定×`quote_en`が新本文に残る | API 0で`text_sha256`再結合(REBOUND)、採否・表示不変 |
| R-6 | 同×`quote_en`が消えた | ISSUE rc=4。確定を黙って破棄しない。revoke→再選択の案内 |
| R-7 | `--regenerate-stage nuance_cand_<lv>`×確定前/確定後 | 確定前=許可、確定後=`CONFIRMED_CONTENT_LOCKED`拒否 |
| R-8 | `--regenerate-stage kp_<lv>`(確定済みKPから再finalize) | ニュアンス確定は保持 |
| R-9 | KP revoke→reconfirm | 旧sidecarは`RECONFIRM_SUPERSEDED`で退避(削除なし)、新`confirmation_id`で再判断 |
| R-10 | 確定後にKP/Wordが変更(`cmd_revise`/revoke)されpoolと衝突 | N3で`SUPPRESSED`(非表示+記録)。最終レポートに出る |
| R-11 | 技術失敗(`FAILED_TECHNICAL`)×制作継続 | 制作は止まらず(非ブロッキング)、`nuance_failed.json`と最終レポート行。`--regenerate-stage`で再実行可 |
| R-12 | model契約違反・予算超過・STOP通知 | STOP(既存安全装置を迂回しない)。`stop_scope_check`でrc=3相当 |
| R-13 | Y/Z provenance: 本文stage再生成→`nuance_cand_<lv>`がstale(明示再生成なしでSTOP)。`DEPENDENTS`の循環・欠落なし | `UNIT_NAMES`/`DEPENDENTS` testに追加 |
| R-14 | copy-run(run dirを別pathへコピー) | sidecarの`kp_dir_rel`で確定レコードを辿れる |
| R-15 | 既存公開記事(LEGACY)のresume/再構築 | 生成0・待機0。文法0件ページのみ非表示化(仕様C)、他は不変 |

## 6. X/Y/Z × Std/Adv integration(mock LLM)

6経路それぞれ(`level_name`の`b1b`=Adv、`a2`=Std)で、runnerの**正式入口**から(`hooks`で`call_fn`/`judge_fn`/TTSをmock注入。`real`modeを使わない):
- X: `er019_family_x_audio_production_runner_01.main`(`--stage study_text`→`tts`/`assemble`/`player`)、`er019_family_x_listening_page_01`(公開ページ)。流用元=`er120_part2_wiring_integration_test_01.py`(X)、`er019_test_family_x_completion_02_integration.py`。
- Y: `er121_family_y_runner_01`(`--stage kp`→`pages`→`page_verify`)。流用元=`er121_family_y_runner_01_test_01.py`。
- Z: `er026_family_z_fiction_production_runner_01`(`--stage kp`→`pages`→`page_verify`)。流用元=`er026_family_z_e2e_integration_test_01.py`・`er122_fz_ctx_fakes_01.py`。

各経路×{Std,Adv}で以下を1ケースとして通す(計12ケース+Family別の差異ケース):
- I-1: 候補生成→rc=4(KP+文法+ニュアンスが`review_request.md`1つ)→確定(採用)→再実行→ページにニュアンスコーナー1個・Part 1→文法→ニュアンスの順
- I-2: 同、不採用→コーナー無し
- I-3: 同、候補なし(mockが`null`)→コーナー無し・HR待機はKP+文法のみ
- I-4: 文法0件確定(`omit`)×ニュアンス採用/不採用→文法コーナー無し
- I-5: 最大1件(mockが2件返しても1件)、重複NGの候補はHRに出ない
- I-6: Std/Advが別々の候補・別々の採否(片方採用・片方不採用)でもページが各levelの節で独立に正しい
- I-7: LEGACY runの再開で何も変わらない
- Family差異: Xは`ledger`無しのfile判定、Y/Zは`ensure_stage`来歴(`nuance_cand_<lv>`/`nuance_<lv>`)。Z Stdは`display_spec`付きのときのみPart 1あり(`_part1_level_enabled`)の組合せ。

## 7. runtime evidence 計画(正式Production経路で各Family×levelの発火証拠)

目的: 受入条件「各Family・各レベルの正式Production runtimeで発火証拠」(原文§5)。**公開済み記事は変更しない**(evidence専用のcopy-runを新規dirに作る)。

### 7.1 方式
- 既存run(確定済みKP・文法Top2事前生成・音声・ページ素材あり)を**copy-run**して再利用: KP候補・文法事前生成物・TTS音声は再利用(API 0)。
- 対象候補(01bの対象と同じ、既存完成本文): X『AI島』(`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01`)、X『Paycheck Personality』、Z『告げ口心臓』、Y既存完成記事1本(再配達料 `user_test/family_y_production_redelivery_fee_01` の元run)。各Std/Adv=計8 level経路(X×2記事 + Y + Z)。**受入には各Family×Level最低1記事で足りる**(X・Y・Z×Std・Adv=6経路)。
- 手順(1経路):
  1. copy-runを新規dirに作成(元runは不変。公開ページ・`user_test`配下は触らない)。
  2. KP確定を`revoke`(`--actor evidence`相当、`user_ref`=委任文)し、`nuance_spec`を新規run扱いで発行(N0)。
  3. **正式経路の実コマンド**(Xは`--stage study_text`、Y/Zは`--stage kp`)を`--mode real`で実行→N1の実API(gpt-6-luna、生成+判定)。stdout/`usage`/`nuance_candidate.json`(model・prompt_sha・usage・cost)を保存。
  4. 統合依頼書(rc=4)とフォーム用データJSON(exporter `--nuance-study-dir`)を保存。
  5. `confirm --from-readable ... --actor evidence`で採用/不採用の両方を再現(`ACTOR_EVIDENCE`は「ユーザー確定ではない」と記録される。`er128:78`)。採用側・不採用側は**別copy-run**で実施(各1回のN1結果を共有して費用を増やさない)。
  6. 再実行→`nuance_result.json`→ページ生成(Z `--stages provision_shell,gate,assemble,pages,page_verify` / Y `pages,page_verify` / X listening page)。生成HTMLでコーナーの有無・順序・見出し0/1個を検査。
  7. resume(同コマンド再実行)でAPI 0・出力同一を確認。reselect系は1経路のみ(Opus枠を使わず自前で)実機確認。
- 保存先: 既存の`er0XX_output/`構造に準拠。ニュアンス専用の新規置き場は作らず、evidenceは`docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/`配下(本管理IDの既存dir)にRESULT/ログのみ保存し、大きいartifactは各runの出力dirに残す。
- 証拠(各経路): ①実行コマンドとrc、②N1の`usage`(model=gpt-6-luna・input/output/cost)、③`nuance_candidate.json`全文+重複検査結果、④確定sidecar、⑤最終HTMLの該当節(採用側/不採用側)、⑥resume時のAPI 0、⑦既存KP/Word・Part 1/Part 2のdiff(Regressionなし: Part 1/Part 2ブロックの文字列がbefore/afterで同一)。**API param+出力の実物**で判定(記録・test PASSだけで受入しない: memory feedback_acceptance_needs_runtime_evidence)。

### 7.2 費用見積(実測前の上限見積)
- N1: level当たり0.11〜0.21円×6経路(各Family×Std/Adv) = **0.7〜1.3円**。追加でX 2記事目・Z/Y補助+reselect再実行1回: +0.5〜1.0円。
- TTS・文法Step B・KP候補: **再利用(0円)**。再実行が必要になった場合のみ別途(その場合は承認枠を確認)。
- 合計**約1.2〜2.5円**。案件見積300円以下かつ承認済みScope内。日次1,000円に対し0.3%未満。実費は`usage_log`から集計して`RESULT_PACKET`に記載。
- 並列: 6経路は独立(別dir・別プロセス)のためN1実行を並列起動可(`stop_scope_check`を各起動前に実行、RESTART_STORMに注意: 各経路の再起動は委任文の許可回数内)。

## 8. Regression・隔離・Dangling

- R-G1: 既存KP/Word・Part 1・Part 2のtest全件PASS(`er003_kp_general_explanation_01_test_01`、`er120_*`、`er119_*`、`er128_*`、`er121_family_y_*`、`er026_*`、`er019_*`のうち配線に関わるもの)。文法0件の期待値是正後。
- R-G2: `er119_isolation_test_01.py`(ALLOWEDへ`er134`を追加。A/B/Cがer119/er120/er128/er134をimportしないこと、`sc.run_key_phrases`・`run_key_phrase_redundancy_qa`のsha不変)。
- R-G3: Grep: `ZERO_P2`・`特に取り上げる難所`の残存が本体コード0(テストの否定assertを除く)。Productionから`FAMILY-Z-STUDY-TEXT-TRIAL-01`・`run_trial_`・`Part 4`・`Think & Express`の参照0(DEV/Trial専用コードへのDangling Referenceなし)。
- R-G4: `compose_study_html`/`compose_page_html`の全呼出元(X player・X公開・Y・Z)が新引数を渡している(Grepで呼出元を列挙し、渡し漏れ0をtestで確認)。
- R-G5: 既存公開ページ(`user_test/**`)のハッシュが実装前後で不変(ページ再生成・差替えなしの証明)。
- R-G6: 既存のretry/fallback/Gate(Part 2のD4拒否、`RESELECT_MAX`、KP外側retry、`stop_scope_check`)の挙動不変。

## 9. 受入条件(原文§5)との対応

| 受入条件 | 検証 |
|---|---|
| X/Y/Z全レベルの正式初回経路に配線 | §6 I-1〜I-7、§7 |
| 最大1件 | U-1、I-5 |
| 主題重複防止が機能 | U-3〜U-8、H-2、R-10 |
| HRで採用/不採用、結果が反映 | H-1〜H-13、I-1〜I-2 |
| 不採用・候補なしでコーナー消滅 | D-3〜D-6、I-2〜I-3 |
| 文法採用0件でコーナー消滅 | D-2、D-4、D-6、D-8、I-4 |
| 再生成・retry・fallback・resumeで維持 | R-1〜R-15、D-12 |
| 必須Regression/Validator/integration PASS | §8、§6 |
| 各Family・各レベルでruntime発火証拠 | §7 |
| 既存KP/Word・Part 1/Part 2 Regressionなし | H-14、R-G1、§7 ⑦ |
| DEV/Trial専用コードへのDangling Referenceなし | R-G3 |
| SSOT・Git反映 | 実装委任のcloseout |
| Fable独立受入 | 別手順(FableがAPI param+出力実物で判定) |
