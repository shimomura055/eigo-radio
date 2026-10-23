FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_10-TRIAL-AUDIT-NG-ROOT-CAUSE-BREAKDOWN-20261023

# FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_10: 既存Trial(Trial_02/Trial_03、必要ならprobe-03/Trial_01)の生データ・Prompt・入力・判定を再確認し、検証実態とNG原因の内訳を明確にする監査。**API 0・新規生成0・仕様変更0・Production配線0・コード変更0**(集計scriptの新規作成は可、既存scriptの変更不可)。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(line 2、KP行)、`.claude/agents/sonnet-worker.md`、ユーザー原文(§9に逐語貼付。T-0で保存)、`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{TRIAL_RESULT_02,TRIAL_RESULT_03,DESIGN_04,OPUS_REVIEW_03,OPUS_REVIEW_04,RULE_CONSISTENCY_01}.md`、`TRIAL_02/{GOLD_LABELS_FINAL_01,REPRESENTATIVE_01,BUDGET_LOG_01}.md`、`TRIAL_03/FABLE_BLIND_RESULT_03.md`、`docs/pm/RESULT_PACKET_KPGM7.md`、`RESULT_PACKET_KPGM8.md`、生データ `er112_output/kp_gm_trial_02/{results.jsonl,judge/,e2e_kp_expl_02.jsonl,summary_02.json,paid_calls.jsonl}`、`er112_output/kp_gm_trial_03/{results.jsonl,sonnet_reference_03_detail.md,fable_blind_std_03.md,fable_blind_std_03_key.json,paid_calls.jsonl}`、Prompt定義 `er112_kp_gm_trial_02.py`/`er112_kp_gm_trial_03.py`(arm定義・入力組立)、`er112_kp_gm_judge_01.py`(判定kind E2/E3定義)、Production側 `er019_family_x_kp_explanation_01.py:54-85,164-178`、`er003_key_words_gloss_alignment.py:300-330,575-612`。

## 1. 背景(Fableが把握している事実。監査で裏取りし、誤りがあれば訂正すること)
- 「59/60」= Opus盲検評価(OPUS_REVIEW_04)における Trial_02 Adv arm **E0@G0**(現行Adv Prompt、入力=G0のStd日本語意味)の難例20 KP×3rep=60出力の、Fable確定gold基準での合否。唯一のNG= `reach for someone's wallet` rep1(入力Std「人の財布に手を伸ばす」=盗む読み→Adv "to move your hand toward another person's wallet to take or use it")。
- 「120件で伝染0」= Trial_03で通常40 KP×Std 3arm(G0/G2/G3)のrep1 glossを入力にして現行Adv Prompt(E0、DEV `call_fn`注入)で生成した説明120本を、**実行層Sonnetが全件目視**した結果(独立Judgeなし)。
- Std: Trial_03 60 KP(難例20+通常40)×G0/G2/G3×2rep=各120出力。Fable盲検(FABLE_BLIND_RESULT_03)のFAIL: G0=3(+境界1)、G2=1、G3=2。Sonnet参考判定は別(G0 FAIL4/G2 3/G3 2 等)。Trial_02のStd(難例20+通常6、rep1、draw a lineのみ3rep)はSonnet Judge+Opus盲検。
- Trial_03 results.jsonlに1行欠損(G3 draw a line rep2)→同入力で1回再実行して補修、台帳も補正行あり。

## 2. 作業
### T-0 記録(API 0)
- ユーザー原文を `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_04.md` に逐語保存(§9をそのまま)。本委任文を `..._委任_10.md` に逐語保存(`Glob **/extract_delegation*` でtoolを探し、あれば使用・MARKER一致確認。無ければ手で全文逐語保存、要約不可)。
- ACTIVE_TASK KP行(自分の行のみ): 委任_10 Status=`TRIAL_AUDIT_IN_PROGRESS(UDR #171はユーザー指示により保留=原因精査後に別途判断)`、報告=`docs/pm/RESULT_PACKET_KPGM10.md`。`docs/pm/USER_DECISION_REGISTER_01.md` UDR #171 を「保留(2026-10-23ユーザー指示: 採用判断は原因精査後に別途)」へ更新。OPEN-474にも1行。
### T-1 調査① Adv英語説明 → `AUDIT_01/ADV_AUDIT_01.md`
2つの検証(A: 難例20×3rep=60 [Opus盲検E0@G0]、B: 通常40×3 Std arm=120 [Sonnet目視])を**明確に分けて**、それぞれ次を表にする:
1. KPの種類(慣用句/句動詞/コロケーション/名詞句…の内訳、X/Z別)、使用Prompt(Production `er019_family_x_kp_explanation_01.py` のPROMPT_SHA256と同一か)、model(gpt-6-luna?)、入力条件(本文1文+Std日本語意味+…)、生成回数(rep)。
2. Advが参照したStd日本語意味(A: G0 rep1〜3のgloss、B: G0/G2/G3 rep1のgloss)を出力ごとに列挙(付表、results.jsonl行番号付き)。
3. 参照したStd意味が「正しい/誤り/薄い」の件数(基準=Fable確定gold[難例]・Fable盲検[Trial_03 Std]。Trial_02のG0 glossはOpus盲検判定を使用。判定が存在しない出力は「未判定」と明記し、推測で埋めない)。
4. AdvのPASS/NG件数(A: Opus盲検、B: Sonnet目視。判定者を必ず併記)。
5. AdvのNGを原因別に分類: (i)Std意味誤りに起因 (ii)Adv生成自体に起因 (iii)両方 (iv)特定不能。判定根拠(入力glossと出力文の対応)を各行に。
6. 59/60の唯一のNG: KP、本文文、Std意味、Adv説明(原文)、NG理由、根拠(results.jsonl行、OPUS_REVIEW_04該当箇所)。
7. 「伝染0件」の検査内容: 誰が・何を基準に・何を確認し(例: 入力glossが誤りの行で出力が誤りを引き継いだか)・何を確認していないか(独立Judge無し、gold無し、rep1のみ 等)。
8. **分母=Std意味が誤っていた出力数、分子=そのうちAdvに波及した数**を、A/B別に明示(Bで誤りgloss入力が0件なら「波及を測れる事例が0件」と明記し、0/120と書かない)。加えて、Trial_02の他のE0交差arm(E0@G2/E0@G3、各22出力)についても同様に整理(Opus盲検結果あり)。
### T-2 調査② Std日本語意味 → `AUDIT_01/STD_AUDIT_01.md`
- Trial_03 G0/G2/G3各120出力について、**Fable最終判定(FABLE_BLIND_RESULT_03)を正とし**、NGを分類: 字義訳NG/語義誤認NG/文法・意味関係NG/その他NG/原因不明。重複なしで「各方式のNG総数=分類合計」となる表。「薄い(△)」は別集計(方式別件数+一覧)。
- Sonnet参考判定との差分表(Fable FAIL/△ vs Sonnet FAIL/△、該当KP・出力)。
- 各NGの実例: KP/本文の用法・意味/実際の日本語出力/正しい意味/NG理由/G0・G2・G3での発生状況(同KPの他方式・他repの出力も併記)。
- `draw a line`: Trial_02(3rep)+Trial_03(2rep)で、方式別に「線を引く」(およびその変種「はっきりと線を引く」「境界線を引く」)の発生回数と、全出力の一覧。
- Trial_02 Std(難例20+通常6、rep1)についても、Opus盲検判定を正として同じ分類表を作る(Sonnet Judge値との差を併記)。
### T-3 整合性・信頼性 → `AUDIT_01/CONSISTENCY_01.md`
- Trial_02/Trial_03/Opus/Fableの判定の照合表(どの数字がどの判定者・どの基準[gold確定前/後]由来か)。暫定Judge値と確定値の混在がある過去報告箇所(RESULT_PACKET_KPGM7/8、TRIAL_RESULT_02/03、Fableのユーザー向け報告で使った数値: 「E0 78%/E1 80%/E4 86%」「G3 96% vs G0 85%」「59/60」「120件伝染0」「FAIL G0=3/G2=1/G3=2」「draw a line 字義 G0 2/5, G2 1/5, G3 0/5」)を列挙し、確定値との差を示す。
- 独立KP数と同一KPの再生成回数の区別(例: Trial_03=60 KP×2rep、Trial_02=難例20×3rep+通常30×1rep 等、正確に)。
- 重複データ・再実行・欠損補修(Trial_03 G3 draw a line rep2の再実行、台帳補正)の集計への影響。
- 推定にとどまる原因は「推定」と明記。既存データから判断できないものは「不明」。
### T-4 報告 → `docs/pm/RESULT_PACKET_KPGM10.md` と `AUDIT_01/AUDIT_SUMMARY_01.md`(同内容)
ユーザー§6の順: (1)検証全体一覧(対象KP数・生成回数・条件・PASS/NG、判定者) (2)Adv NG原因別内訳表 (3)Std G0/G2/G3別・原因別内訳表 (4)代表NG実例(原文・出力・正しい意味) (5)Std誤り→Adv波及の件数と根拠(分母/分子) (6)未判明事項・集計上の限界。結論を先頭に。改善提案は書かない。Fable独立確認用に、主要数値ごとに「根拠ファイル:行番号」を付ける(Fableが生データをGrepで照合できるように)。
### T-5 Git
secret scan(0件確認)→`git diff --cached --name-status`(他agentのstaged変更を巻き込まない)→`git commit --only -- <path…>`→`git push origin HEAD:main`。raw URL添付。

## 3. 禁止
API呼出(LLM/TTS/ASR/検索)一切禁止。既存script・Prompt・Production・er112コードの変更禁止(新規の集計scriptは `er112_output/kp_gm_audit_01/` または `AUDIT_01/` 配下に置く)。推測で数値を埋めない。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。他agentの行(ACTIVE_TASK)を編集しない。
## 4. handback
完了またはblockerで。

## 9. ユーザー原文(逐語)
(本文は `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_04.md` に逐語保存済み。委任文§9の貼付内容と同一。)
