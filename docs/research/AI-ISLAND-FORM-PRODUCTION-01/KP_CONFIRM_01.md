# KP_CONFIRM_01 KP先行確定(AI-ISLAND-FORM-PRODUCTION-01 委任_02)

## 状態: 未実行(委任_03へ引継ぎ)
理由: 委任文の到着確認 `git log origin/main -3 -- er128_kp_confirmed_content_01.py` の最新は `dafd60693`(GRAMMAR-PREGEN 委任_04)で、`--grammar-pending`を含むコミットは**origin/mainに未到着**。作業ツリー上では`er128_kp_confirmed_content_01.py`/`er120_part2_grammar_production_01.py`/`er119_kp_human_review_cli_01.py`に`cmd_from_form(..., grammar_pending=...)`等の未コミット変更(委任_05A作業中)が見えるが、他Agentの未完成・未コミット実装に対して確定(不可逆な保護レコード作成)を実行しない(委任文の手順どおり)。

## 準備済み(確定の前提はすべて満たしている)
- 保存payload(ユーザー確定の逐語): `payloads/ai_island_temple__{a2,b1b}__user_confirmed_01.json`(sha16: a2=`aec83b8cbf53df86` / b1b=`e2fdc0b1f2914fe0`)。`schema_version:2`、`selection.{key_phrase,extra_explanation,meaning_display}`=3/2/5、`selection.grammar:[]`、`grammar_status:"pending_reselection"`、`article.{text_sha256,candidates_sha256}`=ユーザー値。
- 照合: `CONFIRMATION_CHECK_01.md`(SHA10/10・20件一致・不一致0)。er128のfrom-form検証(used_form/japanese_gloss/official/candidates_sha256/text_sha256)と同一条件を満たすことを事前確認済み。
- 新run(旧runを破壊しない): `er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01` = `run_ai_01`のコピー(本文・audit等)+候補docは`run_kp75_ev_01/{a2,b1b}/key_phrases/kp_candidates.json`を使用。OPEN-526の旧PENDING review(7件)は新runに持ち込まない(旧run `run_ai_01`/`run_kpbf_ev_01`/`run_kp75_ev_01`に残置=破壊しない)。**run dirは05A到着後に作成**(未作成。KP review生成はer119のrunner経由が必要なため、05Aのpending対応後に一緒に行う)。

## 実行コマンド(05A到着後、`--help`で`--grammar-pending`を確認してから)
```
py er128_kp_confirmed_content_01.py confirm --from-form docs/research/AI-ISLAND-FORM-PRODUCTION-01/payloads/ai_island_temple__a2__user_confirmed_01.json  --run <run_form_prod_01> --level a2  --by user --user-ref docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_02.md --grammar-pending
py er128_kp_confirmed_content_01.py confirm --from-form docs/research/AI-ISLAND-FORM-PRODUCTION-01/payloads/ai_island_temple__b1b__user_confirmed_01.json --run <run_form_prod_01> --level b1b --by user --user-ref docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_02.md --grammar-pending
```
確認項目: `audit/confirmed_selection.json`のsha・`actor=user`・文法`pending`(0件確定でない)・10件=payloadと一致。
