# SCHEMA_CONTRACT_02 文法選定仕様変更(Top1/Top2提示・1件選択)の契約差分(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05A)

Status: CONTRACT_FIXED(`SCHEMA_CONTRACT_01.md`からの**差分のみ**。記載の無い項目は01のまま)。API 0。
根拠: ユーザー正式決定2026-10-27「文法選定仕様の正式変更【全Family共通】」(APPROVED_FOR_PRODUCTION。逐語は委任文`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_05A.md`の「ユーザー指示」節)。Trial-08の順位付け・Prompt・解説品質は無変更。

## 1. 定数(01 §7の公開API名は不変。値の意味だけ変更)
| 名前 | 旧 | 新 | 意味 |
|---|---|---|---|
| `PREGEN_MAX`(er120) | 8 | **2** | 提示=事前生成の対象数 = Trial-08順位のTop1/Top2(`candidates[:PREGEN_MAX]`。順位付けは既存`select_tiered`で無変更) |
| `GRAMMAR_MAX`(er120 / er128) | 2 | **1** | ユーザー選択の上限。2件同時選択は禁止。0件はomit |
| `TOP_N`(er120) | 2 | 2(意味=提示上限と注記) | 提示数。選択数ではない |
| 候補1件 | | 1件提示・1件生成 | 数合わせの追加はしない。0件は0件 |

## 2. 差分
- `grammar_explanations_v1`: `pregen_max=2`、`items`はTop1/Top2のみ(3位以降は`skipped_over_cap`に件数/idを記録。**生成しない**)。既存ファイルに3位以降のitemがあっても有効性検査は従来どおり(提示はTop1/Top2のみ)。
- `grammar_human_review_v2`: `selection.candidate_ids`長さ**≤1**。`pick`のidsが2件以上=`Part2ReviewError`(`_pick_ids`)。`omit`=0件(`zero_reason`は01のまま)。`verdicts`はTop1/Top2のみ。`decision.explanation_sha_by_id`=提示したTop1/Top2のid別sha。
- `part2_grammar_v2` result: `items`長さ**≤1**(`_require_fresh_part2_v2`が2件以上の旧結果を`Part2Stale`=再選定要)。レンダラは旧2件結果の読取互換のためN件対応のまま残置(新規生成は1件以下)。
- 凍結`confirmed_grammar_frozen`(v2形式のまま)`items[]`≤1。sidecar `confirmed_grammar.json`(v2): `items`≤1、新フィールド `status`(`confirmed`|`pending`。欠落=confirmed)・`presented_ids`(Top1/Top2のid、rank順)・`max_select=1`・`confirmed_after_pending`(KP先行確定後の後追い確定のとき`true`)。
- `form_grammar_bundle`(wiring所有・無変更。`PREGEN_MAX`参照で自動的にTop1/Top2になる): `items`≤2、`n_not_generated`=3位以降の件数。
- フォームデータJSON(exporter): `grammar[]`≤2(Top1/Top2、各`rank`/`ai_recommended`)に加え、`grammar_max_select=1`・`grammar_present_max=2`・`grammar_presented_ids[]`・`grammar_candidates_sha256`・`grammar_text_sha256`(文法候補docのsha。AI島Std/Advの照合用)。
- フォーム送信payload `selection.grammar[]`: **≤1**。2件=ISSUE(rc=4)。Top1/Top2(`presented_ids`)にないid=ISSUE。解説全文は事前生成物と逐語一致(01 §5のまま)。
- CLI: `grammar-select --choice pick --ids`は1件。`grammar-pregen --all-candidates`は**撤去**(argparseが拒否)。

## 3. KP先行確定モード(新設)
- `confirm --from-form <payload> --grammar-pending`: KP/KW(区分①②③)だけを確定・保護。`selection.grammar[]`は使わず**無視**(件数を`grammar_payload_ignored`に記録)。文法reviewは触らない(PENDINGのまま=再選定待ち。**0件として確定しない**)。
  - `rec["grammar"] = {"status":"pending", "path_rel":<pending sidecar|null>, "sidecar_sha256", "pending_since", "reason", "payload_grammar_ignored", ...}`。study dirがあれば`status=pending`・`items=[]`のsidecarを作る(既存の確定sidecar/凍結は`RECONFIRM_SUPERSEDED`へ退避)。study dirが無ければrecordの印のみ。
  - `grammar_state()`はpending=None(文法の保護なし。`guard_grammar`は選定操作を拒否しない)。KPの保護(G0〜G4のKP部分・`guard`)は通常どおり有効。
- `confirm --grammar-from-form <payload>`: pendingのレコードへ文法だけを後から確定。検証(何も書く前): payloadのlevel・KP候補sha・(payloadにKP区分があれば)確定済みKP区分との一致 / 文法は≤1・`presented_ids`内・解説全文逐語一致 / 文法study dir必須(0件でも候補docが無ければ拒否=「次の一手」付き)。実行: KPロック→`gr.apply_form_selection`(0件=omit)→sidecar(`status=confirmed`,`confirmed_after_pending=true`)→KPレコード(`revision`+1・historyに`grammar_confirmed`・`items`/`content_sha256`/`confirmation_id`/`comment`/`confirmed_by`/`origin`は不変)。
  - 冪等: 既に同じ文法(同じid集合)で確定済み=変更なし(`unchanged=true`)。別の内容(別id/0件↔1件)=`CliError`(確定後不変。変更はrevoke)。
  - pendingのままのfinalize: 文法reviewがPENDINGなので`Part2PendingReview`(rc=4待機)/`require_final`=`Part2NotConfirmed`。0件で最終確定しない。
