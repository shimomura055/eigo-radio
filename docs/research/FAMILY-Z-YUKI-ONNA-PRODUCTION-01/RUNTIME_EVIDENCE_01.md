# RUNTIME_EVIDENCE_01 (FAMILY-Z-YUKI-ONNA-PRODUCTION-01 委任_02、2026-10-30)

## 起動(JST、`er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01/run_launch_log.jsonl`)
| # | 起動時刻 | PID | --stages | 所要 | rc |
|---|---|---|---|---|---|
| 1 | 07:58:43 | 30708 | seed_check,writer,std_adjust,plan | 約2分42秒(終了08:01:25) | 0 |
| 2 | 08:02:13 | 37300 | support,kp | 約10分(終了08:12) | 4(KP_REVIEW_PENDING、HR待機) |
- 共通: --story yuki_onna --run run_yo_prod_01 --mode real --approved-budget-jpy 60 --tts-execution-mode STANDARD。各起動前にstop_scope_check rc=0(07:58頃・08:02:09)。
- **規律逸脱(自己申告)**: 起動1の終了(08:01:25頃)から起動2の開始(08:02:13)まで約48秒で、起動規則「各起動≥150秒」を満たさなかった(300秒窓内の起動数は2で≤2は順守。RESTART_STORM保護・STOP・rcエラーは未発動、影響なし)。実質的な副作用は観測されず、以後の起動はなし。
- Seed凍結: `er026_output/family_z_production_e2e_01/yuki_onna/seed/`(seed.json sha256 13d86f74cc5e..., primary_text_excerpt.md 95dba57bbdf7...)。seed_check通過(source_essentials 5件)。

## モデル・Prompt sha・retry(`writer/provenance.json`、cost_log.jsonl)
| 段 | model(要求=実際) | prompt sha256(先頭12) | 出力sha(先頭12) | attempts | 費用(円) |
|---|---|---|---|---|---|
| writer r0 | gpt-6.1-sol (effort high) | 791e9b12182d | 7e628cab54e8 | 1 | 4.74 |
| writer r1 | gpt-6.1-sol | 41c9095fe852 | 0deac00fd943 | 1 | 3.48 |
| writer r2(Adv最終) | gpt-6.1-sol | cf2c96743a50 | 09031ab9f23c | 1 | 2.67 |
| std_adjust | gpt-6.1-sol | 704dbce4009e | 4b9135ddbf08 | 1(auto_regenerated無し) | 5.46 |
| plan(段落分割+話者判定) | gpt-6-luna | - | - | 3呼出(Adv段落分割1[Stdはadv境界を写像]+話者判定Std/Adv各1、全success) | 0.13 |
| support | gpt-6-luna | - | - | 8呼出(全success) | 0.42 |
| part2_cand(a2/b1b) | gpt-6-luna | - | - | 各1 | 0.33 |
| kp+kp_gloss_alignment | gpt-6-luna | - | - | kp12+gloss4(全success、失敗0) | 3.52 |
| nuance_cand(a2/b1b、廃止決定済みだが現行配線で生成=費用のみ記録) | gpt-6-luna | - | - | 各2 | 0.43 |
- 最新世代モデル原則: Writer=gpt-6.1-sol、補助=gpt-6-luna(本番ライン指定のrouting、検証用の旧モデル不使用)。
- retry/fallback/LR/再生成の発動: 全API呼出success=true・失敗0(cost_log.jsonl 37行)。Writer再生成(--regenerate-stage)なし。std_adjustの警告は soft gate "STD_AVG_SENT_LEN_NOT_SHORTER:8.87 vs adv 8.80x0.85" のみ(failures空、既存の軽微警告)。support_stdのlint warnは LISTEN_INSTRUCTION(preview/comment_1)と comment_2×comment_3 の4gram重複(`launch2.log`) — 既存Gateの警告で再生成は発動せず。
- Gate除外: KP候補 "woodcutters" がCMU発音辞書未登録でGate除外(a2/b1b各1件、補完候補で補填。藪の中と同一事象)。

## 費用
- 本委任(起動1+2): 約21.18円(cost_log.jsonlからer009単価で再計算。起動1の累計=16.48円[runner出力spent_jpy]、起動2追加=約4.70円)。TTSは未実行。
- 案件累計(ZY01 API 0円+本委任): 約21.2円 / Cap150円。本日(JST)の他案件費用は本Workerから把握できず「未確認」(本案件分のみ21.2円)。見込み(≈20〜30円)内。
