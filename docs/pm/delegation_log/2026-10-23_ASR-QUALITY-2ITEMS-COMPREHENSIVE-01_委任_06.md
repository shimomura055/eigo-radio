FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-委任_06-OPEN-479-DIALOGUE-SEGMENT-ID-FIX-AND-OPEN-WINDOW-COMPLETION-20261023

# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 委任_06: Production不具合OPEN-479(Z会話clipで`segment_id`未渡し→`judge_role=None`→PNAP/RETが会話clipで一切動かない)の影響分析→(gate通過時のみ)修正→回帰→『開いた窓』c14 2clip再生成→Gate→組立→試聴ページ→page_verify。費用上限15円。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2、ASR行、FAMILY-Z-SOURCE-FIDELITY行)、`.claude/agents/sonnet-worker.md`、`docs/pm/RESULT_PACKET_ASRQ_B5.md`、`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/B_STAGE_RESULT_01.md`、`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/PHASE4_RESULT_02.md`、`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_委任_05.md`(前委任の制約を継承)、ユーザー原文 `..._USER_02.md`(§1-B/§3、受入条件1「X/Z双方の正式初回Production経路で有効」)。コード: `er012_b_family_voices_production_01.py:553`、`er003_v1_sing01_news_tail_fix.py:205-213`、`er006_secondary_asr_01.py:1181`付近、`er103_proper_noun_alarm_policy_01.py:336`付近、`er011_human_review_lock_01.py:336,474`、`er063_family_z_audio_01.py:748-795,1307-1398`。

## 1. Fable判断
- OPEN-479は「承認済み仕様(PNAP/RETはX/Zの正式経路で有効)と実動作の不一致」=仕様内の不具合。CLAUDE.md原則4により、**影響分析gateを通過した場合に限り**修正(`segment_id`を渡す1箇所)をFable承認済みとして実施してよい。gate不通過なら修正せずSTOPしFableへ。
- 修正の目的はPNAP/RETを会話clipで有効にすることであり、**他の既存判定(Tier1/5role・connected speech・その他role依存層)の会話clipでの挙動を副作用として変えることは承認範囲外**。

## 2. 作業
### T-0 記録・予算(API 0)
委任文逐語保存(前委任と同じ抽出手順、`..._委任_06.md`、MARKER一致確認)。ACTIVE_TASKのASR行を 委任_06 Status=`OPEN_479_IMPACT_ANALYSIS`、上限15円、報告=`docs/pm/RESULT_PACKET_ASRQ_B6.md` に更新(自分の行のみ)。当日累計を`daily_dev_cost_01`で確認(上限1,400円、他予約枠: Family Y 残334.25円、KP 70円)。
### T-1 影響分析(API 0) → `docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/OPEN_479_IMPACT_01.md`
1. `segment_id`/`judge_role`/`segment_key` を参照する全ての判定層を列挙(Grep: `judge_role`, `segment_key`, `derive_segment_key`, `ROLE_NOT_APPLICABLE`, `FULL_STORY`, Tier1/5role、connected speech 等)し、「roleがNone→解決済み」に変わったとき会話clipで挙動が変わり得る層を表にする(層名/file:line/変化の内容/承認仕様上の期待)。
2. 会話経路でsegment_idが省かれたのが意図的かを確認(`git log -S`/blame、DECISION_LOG・CURRENT_SPECを管理ID・層名でGrep。全文読込禁止)。意図的な設計決定があればその根拠を記す。
3. **再判定replay(API 0)**: 既存Z完成run(『開いた窓』run_sf_prod_01、melos、他Z e2e)に保存されている会話clipのjudgement入力(primary/secondary転写・canonical・audit)を使い、`segment_id`あり/なしで判定を決定論的に再計算し、PNAP/RET受理以外の判定が変わる(PASS→NG、NG→PASS、warning種別変化、HR/LR発動変化)clip数を数える。
4. **gate**: (i)変化がPNAP/RETによる受理(アラーム付き受理)に限られる、または(ii)それ以外の変化が0件、かつ(iii)会話で意図的にroleを外した設計決定が見つからない → 通過。いずれかを満たさない場合はSTOPし、影響表・件数・該当層・代替案(例: PNAP/RETだけにrole解決を渡す分岐)を付けてFableへhandback(修正しない)。
### T-2 修正(gate通過時のみ)
- `er012_b_family_voices_production_01.py:553` で `review_lock.derive_segment_key(out_path)`(narratorと同方式)の`segment_id`を渡す。最小差分。他の既存Prompt/閾値/flag変更0。
- test: 会話clip経路でroleが解決されPNAP/RETが適用可能になること、narrator経路不変、X非影響、replayの「他判定変化0」を固定するtestを追加。er103/er109/er012/er063/er026系suite+`run_project_regression.py`(`er0*`,`er1*`)実行。golden hash変化があれば内容を列挙(version文字列・PNAP受理以外の変化は不可)。
- 修正後、T-1の replay を再実行し結果一致を記録。
### T-3 『開いた窓』完成(TTS直列化: 他行の「有料run(TTS)進行中」待機、最大45分)
- 保全(run_sf_prod_01の現状を `_preserve_20261023_b6/` へ)。c14 2clip(a2/b1b)を `approve_regenerate`(根拠=USER_02 §1-B/§3・Fable承認・本委任)で解除し、正式CLIで `--only-clips full_story_part1_c14` を tts_b1b,tts_a2 で実行(再起動1回まで)。累計TTSカウンタ(現在6/15)を記録。受理basis(Ledger[Perplexity自動登録済みBertie confidence=low]/entity_table/secondary)をclip別に記録。
- 新たなHR Lockなら止めて報告(迂回なし)。
- 正式Gate(speed v2含む)→assemble(Std/Adv全編)→試聴ページ `user_test/family_z_open_window_01/` 差替え(全体・個別・スクリプト整合、確認点3つ=c12 speciality英式/米式、c2 Bertie、c14 Bertie を明記)→page_verify→`PHASE4_RESULT_03.md`。
### T-4 SSOT・Git・報告
- OPEN-479(原因・影響分析・修正・test・replay結果)、OPEN-472(Z evidence: 会話経路での発火有無を追記)、OPEN-465、UDR #157更新(完成版試聴待ち)。DECISION_LOG(Fable承認の不具合修正、approve_regenerate)。CURRENT_SPECは必要最小限(会話clipでもPNAP/RET有効の明記1行)。REPORT_LEDGER。
- Git: `secret_scan --staged` hits=0 → `git diff --cached --name-status` → `git commit --only -- <path…>` → `git push origin HEAD:main`。wav/raw_usage_log追跡禁止。raw URL添付。
- 報告=`docs/pm/RESULT_PACKET_ASRQ_B6.md`: (0)gate判定と根拠 (A)①②Z evidence最終(会話経路含む) (B)『開いた窓』完成状況・最終試聴URL・確認点 (C)費用出典付き・時間 (D)Closeout(手段/目的の区別、残リスク)。使用model名・最新か。

## 3. 禁止・制約
前委任_05の禁止事項を全て継承(`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止、PIDは自分のもののみ、Gate/HR Lock/STOP迂回禁止、Ledger手動登録禁止、`TTS_EXECUTION_MODE=STANDARD`、秘密情報出力禁止)。修正はgate通過時の1箇所のみ。上限15円無断超過禁止(12円到達で見込み再計算)。
## 4. handback
gate不通過/完了/新HR Lock/予算警告/blocker のいずれかで。