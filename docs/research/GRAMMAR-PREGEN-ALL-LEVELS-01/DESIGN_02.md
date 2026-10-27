# DESIGN_02 文法解説の事前生成(全6経路 = Family X/Y/Z x Standard/Advanced)設計・Opus条件A反映版(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02)

Status: **DESIGN_FIXED**(Opus条件Aレビュー必須修正1〜7を全件採用+Fable判定を反映。実装=核[er120/er119_grammar]は委任_02で完了、adapter/KCP/フォームは委任_03/04)。API 0。
基準: `DESIGN_01.md`(以下D1)。D1の記述は、本書で `[O-n]`(Opus指摘)/`[F-n]`(Fable判定)を付けて置換・追記した箇所を除きそのまま有効。契約=`SCHEMA_CONTRACT_01.md`(F-0、commit 26383d6c7)。
Opus原文=`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_OPUS_RESULT_01.md`。採否=`OPUS_REVIEW_01.md`。
承認済みの解説品質・Prompt(STEPA/STEPB本文・sha)・`eligible7`・Trial-08 Tier・文章量は**無変更**(sha不変をtestで固定)。

## 0. 変更点対応表(D1 -> D2)

| 指摘 | D1の問題 | D2の設計(置換後) | 実装(委任_02) |
|---|---|---|---|
| O-1 重大 | 事前生成物は`ref_ja=None`。`require_fresh_part2`のref_ja_pool照合は、凍結なし経路(auto/CLI確定)で候補文がPart 1引用文と一致すると必ずStale=解消不能STOP | **v2結果は`ref_ja_pool`を署名照合に使わない**。代わりに凍結の有無に関係なく「Part 1訳とStep B訳の食い違い」を同じISSUE(rc=4)で検査(`translation_issues`) | `er120.translation_issues`、`wiring._check_translation`(finalize/require_finalの両方) |
| O-1 中 | ISSUEの解消手段がrevokeだけで行き止まり | 解消手段2つ: (a)別候補を選ぶ/省略 (b)**ユーザー了承で現状のまま進める**(`--user-ref`必須・記録・冪等)[F-1] | `gr.op_accept_translation_diff`、`grammar_translation_issue.json`/`grammar_translation_ack.json` |
| O-1 軽 | 速度(2 level x 最大8 call直列) | まず直列。evidenceで所要時間を測り、2分超ならKP候補生成との並行化を検討(budget guardの原子性確認後)[F-2] | 直列実装(`pregen_explanations`) |
| O-2 | Std本文の候補0件率が高い恐れ(Promptは「Advanced/B1〜B2」固定) | Prompt無変更(D-a維持)。0件は固定文面で正常表示。候補率は委任_02Sで前倒し計測し事実として報告 | 変更なし(Prompt sha不変test) |
| O-3 中 | `legacy_postselect`が「事前生成ファイル無し」に依存=欠落でv2残骸が旧経路へ落ちる | **legacy = review v1 かつ result v1 のみ**。v2成果物があるのに事前生成物が無い=**INTEGRITY**(`Part2IntegrityError`、STOP) | `wiring._is_legacy_postselect/_check_integrity` |
| O-3 追加 | 確定済み・結果なしの旧v1 runで未選択候補にも課金 | 事前生成を**選定済みidだけ**に限定(`source=stepB_generated`明示)。auto(不在宣言)済みならTOP1のみ生成[F-4] | `pregen_stage`(confirmed分岐) |
| O-3 (iii) | reselect後にHR提示前の事前生成を通す状態遷移が未明記 | reselect/NG直後に依頼書を『古い/未完成』へ置換、`pregen_stage`が新候補分のみ生成して依頼書を全候補版へ更新。`grammar-show`/フォームは未生成を出さない | `gr._stale_request_md`、`pregen_stage` |
| O-4 中 | フォームで文法0件を送ると文法reviewがPENDINGのまま行き止まり | **同一ロック内で`omit`を適用**(zero_reason=`form_submission_no_grammar`)。0件の確定もrecordに残す | `gr.apply_form_selection(ids=[])` |
| O-4 中 | ロック順・書込み順・冪等が未定義 | 検証を先に全て済ませ、**KPロック->文法ロック**、書込みは**文法review->sidecar->KPレコード(commit点)**。同じ入力の再送は冪等 | `apply_form_selection`(冪等) / KCP側の呼出順は委任_04 |
| O-4 軽 | `explanations_sha256`をファイル全体shaにすると新候補追加だけで確定が古くなる | `decision.explanation_sha_by_id`(提示した解説のid別sha)。結果組立・検証で選定idのshaを照合 | `finalize_review_record_v2`、`build_result_v2(shown_shas)`、`_require_fresh_part2_v2` |
| O-4 要確認 | HR提示がTOP1/TOP2枠(TOP_N=2「ユーザー正式決定」)から全候補に変わる | ユーザー原文§3「文法候補ごとに…生成」・費用式「0.3円x候補数」から**全候補提示(最大8)が自然な読み**。DECISION_LOGに解釈として記録(SSOT文案)。`TOP_N`の意味(AI推奨=rank1の決定規則)は維持[F-3] | `review_request_v2`(全候補)。SSOT文案=RESULT_PACKET_GPG2 |
| O-5 | X記事別page scriptの共通関数化範囲/Y・Zのleaf性/`_assert_study_ready` | 公開済み記事scriptは書換えない。今後は`public_study_html(level=)`必須+両levelブロック検査(委任_03)。Y/Z新unitは葉ノード。`_assert_study_ready`はpages/page_verifyのみ(`tts_a2`に付けない)[F-5] | `public_study_html(level=)`必須化(核) |
| O-6 中 | 置換検査が「自levelの節に1個」だけでは弱い(取り違えブロックを通す) | **節単位の4者一致**: 共有builderの`<section>`単位で切り出し、`verify_outputs(level, html_text=その節)`が確定・結果・md・HTMLを照合(節内にブロックちょうど1個+決定論描画と一致) | `wiring.verify_outputs`、`g.verify_selection_matches_outputs(section_scoped)`、`g.count_grammar_blocks` |
| O-6 中 | level既定値が暗黙に`b1b`へ落ちる(`or "b1b"`・`discover_dirs()[0]`・`LEVEL_KEY`) | **levelは必須引数**。`LEVEL_KEY`撤去、`discover_dirs(run, level)`は候補doc`level`欄と一致確認(不一致=fail-closed)、`m.LEVEL`はv1読取専用の定数として残し新コード参照0(Grep test) | 全API |
| O-7 | PREGEN_MAX=8/外挿は妥当。遅延生成・上位K件のみは要件違反。将来の2 ITEM/1 call案 | PREGEN_MAX=8を維持。8件超は「他N件・解説未生成」。2 ITEM/1 callは今回実施しない(記録のみ)[F-6] | `skipped_over_cap`、依頼書/フォームの`n_not_generated` |
| O-8 重大 | evidence方式Aの元runに音声・HTMLが無い。Z Advは候補0件経路のみ | 本委任の範囲外(evidence=委任_05)。EVIDENCE_PLAN再設定: 元runの実現性を事前確認(委任_02S)、kp以降を正式runnerで実行、6セルで非0件経路を最低1回、2件採用を1経路で実証、費用上限¥150(案件見積300円以下=AI自律)[F-7] | 後続 |
| O-9 軽 | exporter/`grammar-show`に事前生成不完全時のfail-closedが無い | 不完全・`part2_failed.json`あり・explanations不整合なら**データを出さずエラー** | `gr.require_explanations`、`wiring.form_grammar_bundle`、`gr.render_request_md` |
| O-10 軽 | 実装順序 | F-0スキーマ契約を先行commit -> F-1/F-2/F-3/F-5/F-6/F-8を並行 | SCHEMA_CONTRACT_01(先行commit)済み |

## 1. 工程順(D1 §1を置換。各level独立。X/Y/Zとも同じ骨格)

```
level in {b1b(Adv), a2(Std)} それぞれ:
  本文確定
   -> [A]  part2_cand_<lv>: Step A''(1 call。resumeはextract_signature一致でAPI 0)。levelは必須引数、候補docのlevel欄と一致確認
   -> [A2] part2_expl_<lv>: 全候補(<=8)をStep Bで事前生成(直列・signature一致は再利用)。失敗=part2_failed.json+STOP(rc=3)、再開は未生成分のみ
          (確定済みのrun[auto/旧v1]は選定済みidだけ。stepB_generated)  ※ここまで完了してからでないと待機(rc=4)/フォームに進めない
   -> 待機(rc=4): 依頼書/フォームに「文法名+解説全文」を全候補分表示(KPと1つに統合)
   -> 確定: フォーム(KCP from-form。文法0件=omit)またはCLI(pick ids<=2 / omit / reselect / reextract)。decision.explanation_sha_by_id を記録
   -> [B]  part2_<lv>: finalize = LLM 0 call。凍結値 > 事前生成物 -> part2_result.json(v2: items[]本文出現順)+md。無ければPart2Stale
   -> 使う側(TTS/assemble/pages/player/page_verify)入口: require_final -> 結果v2の検査 + Part 1訳との食い違いISSUE検査
   -> ページ: 共有builderの当該level節にPart 2ブロック(節単位の4者一致検査)
```
- **Step Bの呼出点は`pregen_explanations`の1か所のみ**(Grep testで固定: `generate_explanation(`は定義+1呼出)。`finalize_stage`/`finalize_part2_v2`はLLM関数を引数に持たない。
- **legacy_postselect** [O-3]: review schema v1 かつ result schema v1 の既存runだけ。既存resultを再利用(Step B不要)。それ以外でv2成果物がある場合は事前生成物が必須(無ければINTEGRITY)。
- **v1確定済み・結果なし**(進行中の旧run): reviewはv1のまま(書換えない)、事前生成は選定済みidのみ(`stepB_generated`)、finalizeはv2 result+v1署名で突合。
- 未確定のv1 review: `ensure_grammar_review`がv2へ置換(履歴は引き継ぐ。確定前なので確定内容は書換えない)。

## 2. データモデル
`SCHEMA_CONTRACT_01.md`を正本とする(`grammar_explanations_v1` / `grammar_human_review_v2` / `part2_grammar_v2` / `confirmed_grammar_frozen` v2[KCP所有] / `form_grammar_items`)。

## 3. 指定項目(D1 §3の差分)
- (a)工程順: 上記§1。
- (b)重複防止: 上記§1の3点(単一呼出点・legacy限定・INTEGRITY)+`--regenerate-stage`はD1の表どおり(`part2_expl_<lv>`は確定後guard)。
- (c)HRとフォーム [O-4]: HR依頼書/`grammar-show`/フォームは同一の事前生成物から作り、全候補(<=8)の文法名+解説全文を出す。`pick`(ids<=2)/`top1`/`top2`(単件ショートカット)/`omit`/`reselect`/`reextract`。AI推奨=rank1(`select_tiered`の1件)。AI推奨のみ以外のpickは理由必須(従来のtop2と同じ規則)。
- (d)共通核とadapter: 核は`level`必須。Family差(入力本文・stage台帳・ページ差込点)はadapter(委任_03)。
- (e)KCP M6凍結との接続 [O-4]: 凍結値はlist[item]。wiringは`load_frozen_grammar_items`(KCP v2)があれば使い、v1(単一)のみの間は1件のみ許可・2件以上はfail-closed(KCP複数item化は委任_04)。フォーム確定の検証(`explanation_full == explanations[id].explanation_md`バイト一致・件数<=2・重複なし)はKCP側(委任_04)。
- (f)Trial-08選定: `eligible7`/Tier/`TOP_N`/Prompt sha 不変。AI推奨=rank1。
- (g)費用: D1 §3(g)のとおり(実測ベース増分 X約¥0.9/Y約¥0.8/Z約¥0.34、保守見積でも<=4.6%/記事セット)。evidence費用上限¥150 [F-7]。
- (h)旧規則の撤去: `ADV_ONLY_INVENTORY_01.md`を正本とし、委任_02の核で撤去/置換したもの=`LEVEL_KEY`定数、`b1b`既定値、`discover_dirs(run)[0]`相当の暗黙決定、`run_part2/finalize`からの`generate_explanation`直呼び、旧「選定後のStep B」。残置(v1読取専用)=`LEVEL`定数、`select_from_candidates`/`finalize_review_record`/`build_result`/`run_part2`(v1 legacy orchestrator。Step Bは明示opt-inのみ)。

## 4. retry / fallback / regeneration / resume(D1 §4に追記)
| 事象 | 挙動 |
|---|---|
| 事前生成の構造NG | `_run_llm`の技術retry 1回->失敗でSTOP(`part2_failed.json` stage=`part2_expl_<lv>`)。成功分保持。fallbackなし |
| 事前生成の予算STOP | 成功分保持。部分的な事前生成物では待機/フォームに進まない(fail-closed) |
| resume | 候補/事前生成/finalizeすべてAPI 0(signature一致) |
| v2成果物があるのに事前生成物なし | INTEGRITY(STOP)。旧経路・再生成へ落とさない |
| Part 1訳と【日本語訳】の食い違い | ISSUE(rc=4)。解消=別候補/省略、またはユーザー了承(`--user-ref`必須) |
| 確定後の解説差替え | `decision.explanation_sha_by_id`と不一致=Part2Stale |

## 5. 失敗終了時の最終成果物
- 事前生成STOP: 候補doc+review(PENDING)+部分的な`grammar_explanations.json`+`part2_failed.json`。依頼書は『古い/未完成(操作しないでください)』。TTS/ページ/フォーム用データは作られない。
- ISSUE(rc=4): `grammar_translation_issue.json`(差分と解消手段)。確定record・凍結値は不変。
- どの失敗でも**ユーザーが確定した文法名・解説全文は書き換わらない**。

## 6. Fable判定の記録(Opus指摘とは別に採用した判断)
[F-1] ISSUE解消手段=(a)別候補/省略+(b)ユーザー了承(`--user-ref`必須・記録)。既存`confirm-revise`と同型の保護フロー継続であり新Product原則ではない。発生実績0/28。
[F-2] 速度: 直列で実装し、evidenceで所要時間を計測、2分超なら並行化検討。
[F-3] HR提示: TOP2枠->全候補(最大8、超過分は依頼書に「他N件・解説未生成」)=ユーザー原文§3の解釈としてDECISION_LOGに記録。
[F-4] v1進行中run(確定済み・結果なし)の事前生成は選定済みidのみ(`stepB_generated`)。不在宣言(auto)済みならTOP1のみ生成(任意最適化=採用)。
[F-5] `_assert_study_ready`はpages/page_verifyのみ。Xの公開済み記事scriptは書換えない(履歴)。今後は`public_study_html(level=)`必須+両levelブロック検査。
[F-6] 将来の原価低減(2 ITEM/1 call)は今回実施しない(記録のみ)。
[F-7] evidence費用上限は¥150(案件見積300円以下=AI自律)。

## 7. 新規OPEN(登録文案はRESULT_PACKET_GPG2)の分類
- 核実装とadapter/KCP/フォーム/CLI/evidenceの未配線: **修正へ進む**(同一管理IDの委任_03/04/05で着手。次委任案はIMPLEMENTATION_02 §4)。
- ユーザー判断要: なし(実装方式の範囲内。HR提示の解釈はDECISION_LOG記録で足りる=Opus結論)。
