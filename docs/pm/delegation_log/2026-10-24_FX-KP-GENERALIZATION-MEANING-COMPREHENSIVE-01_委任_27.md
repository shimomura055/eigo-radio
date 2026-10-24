MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_27 (2026-10-24, Fable→sonnet-worker)

# 管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_27(課題②/A-1配線のFable受入前是正: Opus条件C必須修正W-03の未充足を是正、W-02相違の是正、全回帰の他agent起因失敗の整備。API 0)

## Fable判断
- 委任_24の照合でA-1に対するOpus必須修正**W-03が未充足**(validatorが `not that bad→not a bad`、`between you and me→between you and someone`、`this year→a year`、`that same X`、`take that good advice→take a good advice`、`excuse me/beats me→someone` を受理)。これは承認済み仕様(A-1)内の不具合是正(区分B)であり、**PRODUCTION_WIRED受入は是正後**とする。配線自体(4128fffeb)は既定ONのまま(revertしない。理由: runtime実測WRONG 0/44で即時の実害は観測されておらず、是正は受理範囲を狭めるだけ)。
- W-02相違(CMU辞書に無い語の簡易規則フォールバック、複数発音の先頭のみ)はOpus案(辞書に無い語は不許可、例外は送出せず安全側=無変更)に合わせる。
- 本文: `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/OPUS_REVIEW_A1_CONDC_01.md`(W-01〜14)、照合 `PROD_WIRING_EVIDENCE_08.md`。

## 作業
 A. **W-03是正**(`er105_kp_fulltext_selector_01.py` の `is_valid_inflection_normalization`/`reference_pair_ok` 周辺、受理範囲を狭めるのみ): Opus案(a)直前語 not/all/like/at/with 等の除外、(b)時間名詞(year/week/weekend/month/morning/time/moment 等)と same/other/very の後続語の除外、(c)不可算判定を後方の語へ拡張(`take that good advice` の advice)、(d)me系固定表現(between you and me / excuse me / beats me / trust me 等)の除外リスト。肯定ケース(`draw that line→draw a line`、`float that idea`、`take that step`、`make that call` 等、委任_20 testの正例)は維持。test追加(上記の否定例全部+正例維持)を `er003_test_kp_possessor_roles_wiring_01.py` または新規testに。templateの文章指示とvalidatorの整合を1行で記録。
 B. **W-02是正**: `starts_with_vowel_sound`(er105:727付近)で辞書に無い語はFalse(不許可=無変更)、辞書例外は捕捉して不許可、複数発音は全て母音始まりの場合のみTrue(保守的)。test追加。
 C. **replay確認**: 委任_20のP-T2 35unitとX/Z正式KP段の保存出力(`er112_output/kp_gm_prod_01/`)に是正後のvalidatorを再適用(API 0)し、CORRECT→KEPT/INVALIDへの変化を表に(意図した狭め以外の変化が0であること)。
 D. **全回帰の整備**(他agent起因の恒常失敗を最小修正、各別commit可。理由と対象管理IDを記録):
   1. er109 StaticIsolation 2件: `docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/{er109_probe_01.py,runtime_evidence_02.py}` が許可リスト外importer→isolation testが `docs/research/` 配下を対象外にするか、allowlistに追加(研究scriptはProduction到達なし)。
   2. er110 `test_no_production_reference`: `er110_family_y_opinion_based_01.py`(Y DEV runner)と `er019_family_x_fx_20261016_wiring_01_test_01.py:702` の文字列が検出される件→testの意図(Productionファイルからer110参照禁止)を確認し、DEV/test由来を除外する最小修正。
   3. er019 `test_fallback_used_consumers_do_not_read_kp_english_entries`: `er019_nws2_eval_01.py`(X評価script)が読取元→read-only評価scriptであることを確認のうえ許可リストに追加(書込みがあれば追加せず報告)。
   4. er020 `test_recorded_candidates`: `er011_output/local_rewrite_recovery/it2/b1b/...part1.json`(Family Y 委任_09Bが書いた)が原因→Y Trialが X系出力dir(er011_output)へ書いた経緯を確認し、testが期待するdata状態に戻す最小対応(ファイル移動/除外設定。Yの成果物は削除せず `er110_output` 側へ退避、参照先があれば更新)。
   5. er026 3件は一時状態(単独42 OK)のため対応なし、記録のみ。
   是正後に `.venv\Scripts\python.exe run_project_regression.py` を再実行し、failed件数と分類を記録(目標: 他agentの一時状態を除き0)。
 E. 記録: `PROD_WIRING_EVIDENCE_09.md`(W-03/W-02是正内容、replay表、回帰結果)、OPEN-474へ1行、DECISION_LOG(Fable判断: 受入は是正後・配線は維持)。「既知3件」の定義を `docs/pm/PM_GOVERNANCE.md` かREPORT_LEDGERでGrepし、見つからなければ本委任の回帰結果を新しい基準線として `docs/research/REGRESSION_BASELINE_2026-10-24.md` に記録(以後「既知」はこれを参照)。
 F. 委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_27.md`(先頭MARKER一致、0始まり)。commit前に `git status` でindex確認→`git commit --only -- <paths>`(`git add -A/-u/-f/-N`禁止、secret grep 0件)→`git push origin HEAD:main`。
 G. 報告 `docs/pm/RESULT_PACKET_KPGM27.md`: W-03/W-02是正の差分要約とtest数、replay変化表、回帰結果(before/after、残存とその帰属)、commit hash・raw URL、4行、判定整合行。