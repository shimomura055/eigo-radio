# COST_01 — 委任_02 実費(2026-10-26 JST)

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02。上限: Guardrail 100円(到達しても自動STOPではない)。承認区分C(7-7: 承認済みScope内・案件見積300円以下)。見積(BUDGET_PLAN_01)=X Std約6円+Y Std/Adv各約9円=上限側約24円、委任文見積25〜30円。

| 項目 | 起動(JST) | 内容 | 実費(円) | 備考 |
|---|---|---|---|---|
| X Std tts #1 | 16:11:25 | `--stage tts --level a2` | 0 | rc=1。**課金前**のStyle profile固定記録欠落STOP(複製時に`audit/style_profile.json`を落とした私の複製漏れ。API 0) |
| X Std tts #2 | 16:11:51〜16:15:07 | 同(複製を修正) | **6.20** | gemini 3.91 / openai_asr 1.57 / azure 0.72。TTS 11回・ASR 22回・Azure 1回 |
| X Std assemble | 16:17:48〜16:18:13 | `--stage assemble --level a2` | 0 | API 0 |
| X Std tts #3(再利用確認) | 16:21:02〜16:21:21 | 同一引数で再起動 | 0 | 新規API 0(raw_usage_log 34行→34行) |
| Y Std | 16:23:38〜16:24:29 | `y_chunk_evidence_driver_01.py --level a2`(y_voice_2のみ) | **1.77** | gemini 1.25 / asr 0.51 / openai(NER) 0.01。TTS 3回・ASR 6回 |
| Y Adv | 16:27:34〜16:28:21 | 同 `--level b1b` | **1.50** | gemini 1.26 / asr 0.24。TTS 3回・ASR 3回(Y run内累計3.27円 = Std1.77+Adv1.50) |
| **予期しない実LLM call(私の過失)** | R4 driver初版の実行時(時刻はresults jsonに記録なし。Y evidenceより前) | `adv_invariance_driver_01.py`初版のX Adv mock実行が`generate_kp_explanations([])`を実OpenAIへ1回送った(kp_items=[]でも内部でクライアント生成・call。外部接続遮断を設置する前) | **0.0084**(gpt-6-luna、入力326/出力40トークン) | 発覚後すぐdriverに(1)外部接続遮断(`setUpModule`)を最初に設置 (2)`generate_kp_explanations`をmock化 を追加し再実行。再実行は実API 0。**費用は微小だが「mockで回すつもりが実API」の取り違えであり、記録する** |
| **合計** | | | **9.48円** | X 6.20 + Y 3.27 + 0.0084 |

- 小計: X Std 6.20 + Y Std 1.77 + Y Adv 1.50 + 過失0.0084 = **9.48円**(Y run内の3.27円はStd 1.77+Adv 1.50で、上の行と重複計上していない。合計= 6.20+3.27+0.0084 = 9.48円)。
- Cap 100円に対し約9.5%。見積(25〜30円)内。技術失敗(429/5xx等)は0件、STOP(rc=1の1回=課金前のStyle profile欠落のみ)。
- 当日(JST 2026-10-26)既使用: 委任文の約216円+他案件の進行分(Y Trial Cap250・Z Phase 2 Cap200・KP≤15)+本委任9.48円。日次1,000円は`daily_dev_cost_01.py`で確認可能(私は並行案件の合計を正確には持たない=未確認)。
- 起動間隔: X Std tts #1→#2は26秒(<150秒)。#1は課金前STOPで、原因が複製漏れ(決定論)と明確だったため再起動したが、委任文の『起動間隔150秒以上』の規律に反した(課金・429リスクは無かった)。以降は全て150秒以上(assemble 161秒後、再利用確認 169秒後、Y Std→Adv 185秒後)。
- 同一run 5分以内3回起動禁止: X Std runは16:11:25〜16:15:07の間に2回(#1,#2)のみ。
- 旧方式Std runとのJPY比較: `EVIDENCE_01.md` §5、`measure/x_std_cost_compare_old_vs_new.json`(推定)。
