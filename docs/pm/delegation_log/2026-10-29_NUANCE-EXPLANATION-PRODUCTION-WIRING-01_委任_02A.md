Fableからの委任_02A(NUANCE-EXPLANATION-PRODUCTION-WIRING-01 Track B: 生成・重複判定の共通module実装+Prompt v3再検証。費用上限¥5)。本プロンプト全文を `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_委任_02A.md` に逐語保存してから開始。

## 0. 最初に(Opusレビューの逐語保存=機械抽出。本文をモデル出力で再生成しない)
`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046\scratchpad\extract_02a.py`(既存。JSONL転写から条件一致の最長文字列を抽出する)を流用・改修し、転写 `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046\subagents\agent-a71d38e7d1812663d.jsonl` から、`## Opus独立技術レビュー(条件A) NUANCE-EXPLANATION-PRODUCTION-WIRING-01 設計` を含み `### 確認できていない範囲` を含む最長文字列を抽出して `docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/OPUS_REVIEW_01.md`(1行目 `# Opus条件Aレビュー(逐語、2026-10-29、転写から機械抽出)`)に保存。転写をRead/catで表示しない(`py -I`で実行、標準出力は行数・sha256のみ)。検証: `grep -c "^\*\*M-"`=10。直ちに単独commit→push(並行02Bが読む)。
`tools/stop_scope_check_01.py --managed-id NUANCE-EXPLANATION-PRODUCTION-WIRING-01 --run-dir docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01 --out docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/stop_check_02A.json`(rc=3で停止。有料呼出前にも再実行)。

## 1. 正本とFable判断
ユーザー原文 `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md` §2A/B・§3・§5。設計 `WIRING_DESIGN_01.md`(§3 schema・§4・§5・§9)、`PROMPT_TRIAL_01.md`(v2)、`OPUS_REVIEW_01.md`。**Fable判断: Opus必須修正M-1〜M-10・推奨R-1〜R-16をすべて採用**(F-1〜F-6はOpus条件付き賛成の形で確定)。本Trackに関わる要点:
- F-1/R-1: ハードNGはKP/Word(①②)のみ。judgeは文法Top1/Top2も評価し`grammar_conflicts`(警告用)を出すが`overlap_check.verdict`には影響させない。
- F-2/R-2: 段1自動NG=「正規化した主表現がKP/Word句と一致」または「複数語のKP/Wordが主表現に連続して丸ごと含まれる」。それ以外の語共有は段2へのヒント+HR表示用`shared_terms`。段2 fail優先、段2 passは自動NGでない段1ヒットに優先。
- M-4: judge `per_item`はid単位で全件必須(欠落・重複=JSON不正扱い→retry 1回→`overlap_unverified`)。verdictは`per_item`から決定論で算出。`against[]`に提示pool全件(exporterと同じ関数で算出、DEFAULT_CAP=12)+文法Top1/Top2。
- M-8: 入力形=「暫定選定+pool最大12件+文法Top2(提示中)」でv3を**同じ8 level**で1回再検証(約¥1.5、各runの`kp_candidates.json`使用)。`focus_terms`はPromptに入れず`expression`から決定論導出。
- M-9: 引用=「本文の連続した1〜2文の逐語部分文字列」、引用符正規化は文法の`norm_body`と同規則。
- R-8: 判定は別Prompt、生成側の`differs_from_kp_word_ja`/`criteria_check`を判定に渡さない。判定Promptに入れ替えテスト+「最も焦点が近い項目の明示」。検査用プローブ5〜6件(Part 1類義語比較型/文法と同焦点/非重複)を固定fixtureに(約¥0.2)。
- R-9: Std(A2)の除外理由を「A2基礎文法の対比」でなく「文法コーナーの領域」に置換、「機能語・頻出表現の語用的含みはStdでも可」「助動詞・構文を含んでも焦点が語用(誇張・婉曲・確信度)なら可」を明記。自己評価`mid`は決定論で0件。
- R-10: 判定出力は圧縮形(id→bool、trueのみ理由)。routing contractにprocess 2件追加、費用集計に含める。
- fail-closed(OK-4/R-5): API障害・JSON不正・引用不一致→`FAILED_TECHNICAL`(本物の0件と区別)、非ブロッキング。
- 不採用/禁止: Part 4、2件以上、自動補充、HR省略、見出し語に「Deeper Understanding」を使わない(見出し=「ニュアンス解説」、Fable判断R-12)。

## 2. やること
1. 新module `er134_nuance_explanation_01.py`(純関数+LLM呼出は`routing.require_model`経由、gpt-6-luna=本番既定): `build_inputs`(本文・暫定KP/Word・pool・文法Top2)、`generate_candidate`(Prompt v3)、`structural_check`(F-2規則、決定論)、`judge_overlap`(別Prompt、per_item全件、圧縮形)、`decide`(verdict決定論、`shared_terms`/`grammar_conflicts`/`overlap_unverified`/`FAILED_TECHNICAL`/`NONE`)、`derive_focus_terms`、`quote_check`(M-9)、schema=`WIRING_DESIGN_01.md §3`+Opus修正。`er006_model_routing_contract_01.py`へprocess追加。
2. テスト `er134_nuance_explanation_01_test_01.py`: 単体U-1〜U-16(TEST_PLAN)+M-4/M-8/M-9/R-2/R-8/R-9/R-15該当(per_item欠落→overlap_unverified、mid→0件、丸ごと包含→自動NG、語共有のみ→段2優先、引用1〜2文逐語、FAILED_TECHNICAL非ブロッキング)。mock LLMで全PASS。
3. v3再検証(有料≈¥1.5+プローブ≈¥0.2): 01bの8 level(AI島/Paycheck/告げ口心臓/宅配 ×Std/Adv)でProduction形入力により`er134`実関数を実行(`NUANCE_TRIAL_PAID=1`相当のガード、一時out_dir、Production results不変)。結果表(候補/0件/FAILED、段1/段2、grammar_conflicts、費用)を `PROMPT_V3_VERIFY_01.md`。品質基準=01b v2と同等以上(at least[Adv]/You should have seen/was linked toの再現または同等候補、Std/Adv不整合の減少)。不十分ならPrompt修正1回まで(同方向の反復はしない)。
4. `docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/TRACK_B_EVIDENCE_01.md`(関数境界・schema最終版・test結果・費用)。
5. commit(新module・test・routing・docs・委任文のみ明示`git add`)→push。並行02B(表示・HR・page_verify)が`er120*/er128*/er121/export_form_data/selection_form_v3`を編集中=本Trackはそれらを編集しない。ACTIVE_TASK(O)行は02Bが更新(本Trackは触らない)。index.lock衝突は数秒待って再試行。
6. `docs/pm/RESULT_PACKET_NXW2A.md`(整合/未承認機能/成果物と目的適合/判断候補/費用実績/commit、`判定整合:`行)。最終回答は短く(test件数・v3結果要約・費用・commit)。

## 3. 範囲(11-8)
範囲内=承認仕様の実装・Opus修正・検証。範囲外=仕様変更(2件以上/自動補充/Part 4/HR省略/文法ハードNG)、公開記事の変更、Family A/B/C。
