# 委任_09 結果(FACTLOCK-ASTRA-E2E-TRIAL-01、2026-10-09、Status=PARTIAL: 統合6/10、4テーマ要Fable判断)
## 1 成果物
ベース `er052_output/factlock_astra_e2e_trial_01/`: annotation/ANNOTATION_SUMMARY_01.md、AUDIT_SUMMARY.md、check/(修正後)・check_prefix/(修正前)、out/{A,B}/<slug>/(annotated.md・annotation.json・transcript.jsonl・audit*)、out/merged/<slug>/(統合6)、final/<slug>/(統合6: selected_brief_factlock.md・annotation.json・fact_selection_evidence_factlock.json)、audit/、b3_v2_judge.json、stage_r/{hormuz,streaming_price}/storyline_b3_v2/(v1は無改変)、stage_r/FROZEN_INPUTS_SHA256.json(v2追記)、prompts/(hormuz・streaming_priceはv2、v1は`_v1.md`)、PROMPT_SHA256.json。新規script: annotation/{make_final_01,build_prompts_v2_09,freeze_v2_09,run_audits_01,audit_extra_01,audit_bash_detail_01,b3_v2_judge_01,make_summary_01}.py、stage_r/run_b3_v2_09.sh。commit hash・raw URL は末尾。
## 2 テーマ別(修正後)
| テーマ | A | B | 統合 | 分割一致率 | 中核Jaccard | 判定線 | 監査(隔離/ツール規律) |
|---|---|---|---|---|---|---|---|
| byd_recall | PASS | PASS | PASS | 1.00 | 1.00 | 超え | 隔離OK / B=Bash使用 |
| central_bank_mortgage | PASS | PASS | PASS | 0.80 | 1.00 | 超え(境界) | 隔離OK / B=Bash |
| hormuz | FAIL(事実0件) | FAIL(同) | 未統合 | - | - | - | 隔離OK / 規律OK |
| inbound_tourism | FAIL | FAIL | 未統合 | - | - | - | 隔離OK / B=Bash |
| meta | PASS | PASS | PASS | 1.00 | n/a(中核0件記事) | 分割のみ超え | 隔離OK / B=Bash |
| openai_copyright | PASS | PASS | PASS | 1.00 | 1.00 | 超え | 隔離OK / A,B=Bash |
| semiconductor_earnings | FAIL(AMBIGUOUS台帳ID F1のみ) | FAIL(同) | 未統合 | - | - | - | 隔離OK / 規律OK |
| small_bag | PASS | PASS | PASS | 1.00 | 1.00 | 超え | 隔離OK / A=Bash |
| space_weapons | PASS | PASS | PASS | 1.00 | 1.00 | 超え | 隔離OK / A,B=Bash |
| streaming_price | FAIL(AMBIGUOUS台帳ID F07のみ) | STOP(§4(ii)「3種」) | 未統合 | - | - | - | 隔離OK / 規律OK |
統合6件は統合版検査PASS、flags空。final JSON 6件は check_json(元evidence比)PASS。事実数/中核周辺/cap_dropped/unmapped_claims/B3形式は ANNOTATION_SUMMARY_01.md。
## 3 問題テーマとB3 v2
- hormuz: v1は『Storyline重複行+素材段落』(箇条書き0、台帳外の数字「25」[約25時間])。v2(¥0.418)は箇条書き4行、重複行・素材行なし、台帳外の数字0、選択ID HF-002/006/007/009(全VERIFIED)。同じ問題なし -> 再注記の価値あり。
- streaming_price: v1は段落1、台帳外の数字「3」(3種)。v2(¥0.322)は段落1(箇条書きなし。ただし仕様上は段落先頭に`- `挿入で注記可能)、台帳外の数字0。ただし選択IDは v1と同じF01-F04,F06,F07で **AMBIGUOUS F01・F07を含む** -> 既存規則(VERIFIED以外はFAIL)のため再注記してもcheck FAILになる(後述6-1)。
- v2プロンプト4本は A/B同一検証OK(PROMPT_SHA256.json、ab_all_identical=true)。
- 他の問題: inbound_tourism は注記者側の形式エラー(概念統合で`8月`と`2019年8月`を別概念、分類漏れ`01/02/03/06`)+AMBIGUOUS台帳ID F06。semiconductor/streaming A は AMBIGUOUS ID参照のみが唯一のFAIL理由。
## 4 「・」行頭の判定
inbound_tourism で「・【事実N】」は d_sequence PASS(FACT_LINE_RE は`-`と`・`の両方を読む)。変換不要。仕様§2「箇条書き1行を1事実」は記号を限定せず、「・」は元briefの文字で追加・削除なし。§7の「`- ` の直後」は注記者の挿入行の記述。判定: 許容。置換は行わず、仕様変更もなし。
## 5 バグ修正(スクリプト。前後の結果を両方保存: 修正前 annotation/check_prefix/、修正後 annotation/check/、修正前スクリプト annotation/prefix_scripts/)
- P1 b3_annotation_check_01.py parse_ledger: `[AMBIGUOUS - 断定禁止...]` 形式のstatus行を読めず、AMBIGUOUS記録が「台帳に存在しないID」扱いだった。status後ろの任意文字を許す正規表現に修正。
- P3 同 align(): 段落形式で『。+空行』の直後に`- 【事実N】`を入れる定義済み挿入(仕様§1「`。`と改行の直後」)を、`。\n`1改行限定で拒否していた。`。\n+`に拡張。
- P4 b3_annotation_merge_01.py extract_output: 区切り直前の余分な末尾空行(注記者の出力に混入)を1改行へ正規化。
- 効果: 修正前 PASS 7/19(+STOP1) -> 修正後 PASS 12/19(+STOP1)。修正後も check テスト40件 OK。
- P2(未適用): 『status が VERIFIED でない台帳IDへの紐付けは FAIL』(既存テスト test_non_verified_ledger_id_in_facts_fails が規定)をAMBIGUOUS許容へ緩める案は、自動承認判定で拒否されたため実施せず(検査緩和にあたる)。Fable/ユーザー判断事項。
## 6 未確認・Fable判断要
1. AMBIGUOUS台帳ID: B3がAMBIGUOUS記録を選択したテーマ(inbound F04,F06 / semiconductor F1 / streaming F01,F07)は、既存規則では注記者が正しくIDを書いても検査FAILになる。PREREGISTRATION v2.2 5-12(『注記者はstatusで扱いを変えない。AMBIGUOUS由来NGは別集計』)と矛盾。(a)検査規則をAMBIGUOUS許容へ変更するか、(b)当該テーマを注記不能として入替えるか、判断が必要。semiconductorはこの1点を除きA/Bとも検査PASS。
2. inbound_tourism: 注記者A/B双方に概念統合・分類漏れの形式エラー。RUN_ANNOTATION §6の再委任(1回)の対象。私は注記者を起動できないため未実施。
3. hormuz は v2プロンプトで再注記、streaming_price は(1)の判断後。
4. ツール規律: 9/20の注記者がWriteでなくBashでreply.mdを書込み(隔離=他ファイル非参照は20/20維持)。既存監査2本は固定文言の例外Writeを想定せず20/20が形式上VIOLATION(自分のプロンプトパスが参照禁止語に該当する不整合含む)。補助監査で分離評価(AUDIT_SUMMARY.md)。
5. 実行環境メモ: 指定の tasks\*.output は0バイト、実体は同セッションの subagents\agent-*.jsonl(20/20一意に特定)。
6. 本委任で b3_annotation_check_01.py / b3_annotation_merge_01.py を修正した(委任_05 のrunnerが import している場合に影響し得る。テスト40件は通過)。
7. central_bank_mortgage は分割一致率0.80ちょうど(判定線の境界)。
8. 統合版の注記内容は機械統合のみ(手直しなし)。meta は中核数値0件の記事。
## 7 所要時間・API支出
所要 約1時間(推定)。API支出 ¥0.74(hormuz B3 ¥0.418 + streaming_price B3 ¥0.322、luna。上限¥3以内)。証跡 stage_r/<slug>/storyline_b3_v2/_run/{cost.json,raw_usage_log.jsonl,stdout.log,entry_point.json}。Astra・Writer以降は未実行。
