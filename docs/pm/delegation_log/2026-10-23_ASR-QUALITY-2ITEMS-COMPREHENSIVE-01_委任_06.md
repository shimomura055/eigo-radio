FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-委任_06-OPEN-479-DIALOGUE-SEGMENT-ID-FIX-AND-OPEN-WINDOW-COMPLETION-20261023

# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 委任_06: Production不具合OPEN-479(Z会話clipで`segment_id`未渡し→`judge_role=None`→PNAP/RETが会話clipで一切動かない)の影響分析→(gate通過時のみ)修正→回帰→『開いた窓』c14 2clip再生成→Gate→組立→試聴ページ→page_verify。費用上限15円。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2、ASR行、FAMILY-Z-SOURCE-FIDELITY行)、`.claude/agents/sonnet-worker.md`、`docs/pm/RESULT_PACKET_ASRQ_B5.md`、`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/B_STAGE_RESULT_01.md`、`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/PHASE4_RESULT_02.md`、`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_委任_05.md`(前委任の制約を継承)、ユーザー原文 `..._USER_02.md`(§1-B/§3、受入条件1「X/Z双方の正式初回Production経路で有効」)。コード: `er012_b_family_voices_production_01.py:553`、`er003_v1_sing01_news_tail_fix.py:205-213`、`er006_secondary_asr_01.py:1181`付近、`er103_proper_noun_alarm_policy_01.py:336`付近、`er011_human_review_lock_01.py:336,474`、`er063_family_z_audio_01.py:748-795,1307-1398`。

## 1. Fable判断
- OPEN-479は「承認済み仕様(PNAP/RETはX/Zの正式経路で有効)と実動作の不一致」=仕様内の不具合。CLAUDE.md原則4により、**影響分析gateを通過した場合に限り**修正(`segment_id`を渡す1箇所)をFable承認済みとして実施してよい。gate不通過なら修正せずSTOPしFableへ。
- 修正の目的はPNAP/RETを会話clipで有効にすることであり、**他の既存判定(Tier1/5role・connected speech・その他role依存層)の会話clipでの挙動を副作用として変えることは承認範囲外**。

## 2. 作業
### T-0 記録・予算(API 0)
委任文逐語保存。ACTIVE_TASKのASR行を 委任_06 Status=`OPEN_479_IMPACT_ANALYSIS`、上限15円、報告=`docs/pm/RESULT_PACKET_ASRQ_B6.md` に更新(自分の行のみ)。当日累計を`daily_dev_cost_01`で確認(上限1,400円、他予約枠: Family Y 残334.25円、KP 70円)。
### T-1 影響分析(API 0) → `docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/OPEN_479_IMPACT_01.md`
1. `segment_id`/`judge_role`/`segment_key` を参照する全ての判定層を列挙し、「roleがNone→解決済み」に変わったとき会話clipで挙動が変わり得る層を表にする(層名/file:line/変化の内容/承認仕様上の期待)。
2. 会話経路でsegment_idが省かれたのが意図的かを確認(`git log -S`/blame、DECISION_LOG・CURRENT_SPECを管理ID・層名でGrep。全文読込禁止)。
3. **再判定replay(API 0)**: 既存Z完成run(『開いた窓』run_sf_prod_01、melos、他Z e2e)に保存されている会話clipのjudgement入力を使い、`segment_id`あり/なしで判定を決定論的に再計算し、PNAP/RET受理以外の判定が変わるclip数を数える。
4. **gate**: (i)変化がPNAP/RETによる受理に限られる、または(ii)それ以外の変化が0件、かつ(iii)会話で意図的にroleを外した設計決定が見つからない → 通過。いずれかを満たさない場合はSTOPし、影響表・件数・該当層・代替案(例: PNAP/RETだけにrole解決を渡す分岐)を付けてFableへhandback(修正しない)。
### T-2 修正(gate通過時のみ)
- `er012_b_family_voices_production_01.py:553` で `review_lock.derive_segment_key(out_path)`(narratorと同方式)の`segment_id`を渡す。最小差分。他の既存Prompt/閾値/flag変更0。
- test追加(会話clipでrole解決・PNAP/RET適用可能、narrator経路不変、X非影響、replay他判定変化0)。er103/er109/er012/er063/er026系suite+`run_project_regression.py`実行。golden hash変化は内容列挙。修正後replay再実行。
### T-3 『開いた窓』完成(TTS直列化、最大45分待機)
保全(`_preserve_20261023_b6/`)。c14 2clip(a2/b1b)を`approve_regenerate`で解除し正式CLIで`--only-clips full_story_part1_c14`をtts_b1b,tts_a2で実行(再起動1回まで)。HR Lockなら止めて報告。正式Gate→assemble→試聴ページ`user_test/family_z_open_window_01/`差替え(確認点3つ)→page_verify→`PHASE4_RESULT_03.md`。
### T-4 SSOT・Git・報告
OPEN-479/472/465、UDR #157、DECISION_LOG、CURRENT_SPEC最小、REPORT_LEDGER。Git: secret_scan→`git commit --only`→`git push origin HEAD:main`。報告=`docs/pm/RESULT_PACKET_ASRQ_B6.md`。

## 3. 禁止・制約
前委任_05の禁止事項を全て継承。修正はgate通過時の1箇所のみ。上限15円無断超過禁止(12円到達で見込み再計算)。
## 4. handback
gate不通過/完了/新HR Lock/予算警告/blocker のいずれかで。
(注: 本ファイルは委任文の要約再掲を含む保存。原文はFable委任メッセージ。)
