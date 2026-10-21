# ANNOTATION_FIX_01(決定論annotation producer: ドット区切りバージョン表記の整合是正)

管理ID: FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_02 / 11-8範囲内の不具合是正(Fable判定済み)。API 0・費用0円。

## 1. 何が問題だったか
- `run_byus_01`のLedger F14(L90付近)に「アプリバージョン26.10.10以上」。`er053_b3_deterministic_producer_01.py`の数値パターン`NUM = \d[\d,]*(?:\.\d+)?`は小数部を1段しか許さず、抽出器(SURF_RE)が「26.10」と「10以上」の2表面に分割した。
- 注記器`find_all`は「直前が`.`/直後が`.`+数字なら部分一致として除外」する既存規則(5.5の中の5を除く)のため、分割された両表面を本文中で認めず、内部検査`b_numbers`/`e_sidecar`がFAIL -> `ANNOTATION_PRODUCER_FAILED`(課金前STOP、`console_text_01.txt`)。抽出器と注記器が同一表記を別単位で扱う自己矛盾。

## 2. 何を変更したか
- `er053_b3_deterministic_producer_01.py:169` `NUM`: `(?:\.\d+)?` -> `(?:\.\d+)*`(ドット区切り数値列を1トークン最長一致。26.10.10 / 1.2.3 / 5.5。NUM_C・RANGE・「第N回」・SURF_RE本体は無改変でNUM経由で追従)。コメントに管理IDと理由1行。
- 「26.10.10以上」は既存の`NUM + UNIT* + HEDGE_POST`の読み取りで1表面「26.10.10以上」になる(接尾語[以上]は既存HEDGE_POST)。`find_all`は無改変(同一表面を出現と認め、「26.10」「10以上」等の部分一致は従来どおり拒否)。
- 承認済み設計は不変: producer失敗=課金前STOP、注記なしfallbackなし。受理面・閾値・方式の新設/拡大なし。
- 回帰test: 新規`er053_b3_deterministic_producer_dotted_version_test_01.py`(6件。旧版では3件FAIL=再現、新版6 PASS)。`er053_b3_deterministic_producer_01_test_01.py`のPortFidelity(Trial原文byte一致)にNUMのみ`DOCUMENTED_DIVERGENCE`(差分は`?`->`*`のみ、と固定)。
- rules_sha256固定箇所の更新: `er019_family_x_b3_min2_test_01.py:30` `RULES_SHA256_BEFORE`(旧値をコメントに残して新値へ)、`er083_b3_background_fact_trial_01_test_01.py`(履歴run_mey_01のannotation.jsonは旧sha入りのため、旧shaを現行shaへ置換して比較。他はbyte同一を要求)。

## 3. 何が改善されるか
`run_byus_01`が`ANNOTATION_PRODUCER_FAILED`せず全5検査(a_alignment/b_numbers/c_core_peripheral/d_tags/e_sidecar)PASS(offline確認済み、n_facts=4, n_number_surfaces=4)。今後ドット区切りバージョン・小数列を含む記事で同種のSTOPが出ない。

## 4. リスク・注意点
- rules_sha256: 旧 `525f2309b5212e68a5891794e7fa6194fb25cbf92f1954727c286796597910d8` -> 新 `3b4b7fdf8dc6816cf8368b538c4b85485dba33ed2a114a8319b13a060050f723`。以後の新規runのannotation manifest/sidecar(spec_sha256)は新値。記事A(`paycheck_personality/run_pp_01`)のtext工程は本是正前(旧値525f2309...)で完了済み。記事Aの注記artifactは旧shaのまま(出力内容は下記の通り新旧同一)。
- 出力不変の証明(旧版producer[変更前ファイルの複製]と新版を同一入力[Ledger+selected_brief+evidence]でoffline実行、rules_sha256/generated_at/それに依存するsha欄を除き比較): `coffee_prices/run_fxpw_01`・`middle_east_yemen_saudi/run_mey_02`・`paycheck_personality/run_pp_01` の3 runで注記済みmd・sidecar(annotation.json)・writer_constraints.txt・manifest(checks)・evidenceが全てバイト同一(DIFF files=[])。さらに新版出力は各run dirの既存成果物ともバイト同一(annotated md・sidecar[spec_sha除く])。
- 既存er053 producer関連test(producer/contract/wiring c2,c4,c5/c2 removal/c3 audio guard/b3_min2)177 PASS。er083の2件(`production_modules_unchanged_vs_git_head`等)は未commit差分を検出する設計のためcommit後に解消(commit前のみFAIL)。
