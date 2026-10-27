# 委任_02(W2): X/Y/Z×Std/Adv 全6経路のLR・Fallback実装確認(ユーザー原文 §4)

共通事項: `docs/pm/delegation_log/2026-10-27_LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01_委任_00_COMMON.md`(必読・遵守)。
成果物: `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/W2_SIX_ROUTES_01.md`。読取専用・API 0。

## 対象と基準
基準=統一仕様(`CURRENT_SPEC.md:3148-3220`、`ROW_MAPPING_01.md`の49行9 policy、`er127_tts_block_policy_01.PROFILES`)。対象=X Std/Adv・Y Std/Adv・Z Std/Advの**本文音声**(Full Story/Voices/Narration。chunk経路を含む)。前回監査`TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/REPORT_01.md`と統一後evidence`EVIDENCE_{X,Y,Z}_01.md`を起点に、**統一後の現行HEADコード**で再照合する(前回監査は統一前の結果なので差分を明示)。

## 6経路×確認項目の表(ユーザー原文§4の10項目)
各セルに「コード配線(file:line)/単体・結合test(test名)/runtime evidence(run path・日付)/未観測」を区別して記入:
- LRの適用対象(role)と発火条件(③NG後、深さ1、NO_NG_SPAN等の即HR)
- 通常TTSとFallbackの試行回数・順序(①②→180秒→③、LR後①'②'→180秒→③')
- Minimal(短文)instructionの使用条件(③のみか)。Adv③の短文Style新規適用の確認
- Fallback時の実際のPrompt/Style(保存record `style_prefix`/`instruction_type`の実値)
- LR後のTTS試行回数・Style(元role Style維持か=OPEN-312の解消状況)・ASR検査(書換え後の文が正解原稿か)
- Stdの減速後ASR再検証(各attempt内での実施、減速後NG→次attempt)
- LR成功後の状態遷移(`RESOLVED_BY_LOCAL_REWRITE`/status OK/`LR_REWRITTEN`警告/`local_rewrite_recovery`記録)
- Human Reviewへの移行条件(終端NG→HRQ 1行、LR不可→即HR、技術STOPは除外)
- M3/Y gate/Z gateによる採用制限(③採用・LR採用がBLOCKされるか、承認解除手段)
- retry/fallback/regeneration/resume(消費済みattempt再実行なし、残り待機のみ、LR LLM再実行なし、原稿sha stale)

## 追加確認
- AI島run(`ai_island_temple__run_form_prod_01`)のattempt列が統一仕様のどのpolicy(EN_LR_STD/EN_LR_ADV)で動いたかを実データで示す(W1と重複可、こちらは経路観点)。
- 統一仕様の「未観測」項目(X STOP/Y chunk経路/Zセリフ終端Std/X-Adv-5/Z-Std-3/Z-Adv-7)の現状(その後の実runで観測されたか)。
- 統一後にLRが実発火したrun一覧(X/Y/Z、`local_rewrite_recovery`を持つ`tts_generation_results.json`/Z entryをGrep。2026-10-26以降)。
- 所見のA/B/C分類、判断候補、Fableへの要約10行。
