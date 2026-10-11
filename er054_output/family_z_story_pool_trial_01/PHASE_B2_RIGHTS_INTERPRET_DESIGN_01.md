# PHASE B2 権利情報の解釈・整理工程 設計(乾式のみ実施、有料実行は承認待ち)

driver: `er054_family_z_story_pool_rights_interpret_trial_01.py`(Trial専用、Production非参照)。モデル=`gpt-6-luna`(Routing Trial key `FAMILY_Z_TRIAL_RIGHTS_INTERPRET`、ユーザー指示2026-10-11)。Status上限 `VALIDATED`。

## 1. 位置づけ
Phase B(Pythonの決定論判定、`screening/<ID>.json`)を**置き換えない**。LLMは「整理・要約・未確認事項の明確化・REVIEW解消に必要な確認事項の列挙」だけを行う補助。最終PASSはPython判定+ユーザー確定。

## 2. 入力
Phase B JSON(ハッシュ/保存先等のノイズ除去)= 書誌メタ・権利者ごとのPD計算結果・Z-1チェック・未確認事項(unconfirmed)・decision/decision_reason。入力に無い事実は記憶で補わせない(Prompt禁止+「未確認」と明記)。過去評価結果は一切渡さない。

## 3. 出力schema(strict json_schema)
`rights_state_summary` / `basis_summary` / `subjects[{subject,status_as_given,note}]` / `unconfirmed_clarified[{item,why_matters,blocking_for_final_pass,added_by_llm}]` / `confirmations_needed_to_resolve_review[]` / `llm_concern_level(none|review|ng_concern)` / `concerns[]` / `pass_equivalent`(記録のみ) / `confidence`。**PASS/NG判定欄は無い**。

## 4. Prompt案
developer: 権利確認補助者・最終判定者ではない・判定欄なし・入力に無い事実を補わない・米国PDを日本の根拠にしない・第三者翻訳は別著作物・懸念度のみ回答。user: Phase B JSON+手順1〜8(driver内 `DEVELOPER_MESSAGE`/`USER_TEMPLATE`)。

## 5. 決定論の統合(reconcile)
| 決定論(Phase B) | LLM | 最終(本工程後) |
|---|---|---|
| PASS | 懸念none | PASS(ただし `final_pass_confirmed=False`。ユーザー確定待ち) |
| PASS | 懸念review/ng_concern | **REVIEW_REQUIREDへ降格** |
| PASS | (一次資料未取得 / blocking未確認あり) | REVIEW_REQUIREDへ降格(LLM無関係) |
| REVIEW_REQUIRED/NG | PASS相当・懸念none | **据え置き(昇格不可)** |
昇格経路は存在しない。原作未確認・権利不明を自動PASSしない。

## 6. 記録
`phase_b2_rights_interpret/<model>/<ID>.json`: requested_model/actual_model_id/routing_key/usage/prompt_sha256/developer_message/llm_output/reconcile。費用はraw_usage_log.jsonl。

## 7. 乾式結果
`phase_b2_dry_run/DRY_RUN_SUMMARY.json`(モック10作品、API呼出0): 昇格0件、降格check(L01+concern)=REVIEW_REQUIRED、昇格check(L04+PASS相当)=据え置き、actual_model_id記録OK。
