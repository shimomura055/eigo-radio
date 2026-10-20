# FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 E2E_PLAN_02(委任_01、2026-10-20)

性質: 正式Production経路の記事生成(text+audio)。新仕様探索ではない。ユーザー決定③(2026-10-20)。

## §0 受入条件の事前固定(実走前。以後変更しない)
- 攻撃主体Fact: Fact本文(英/日)が、サウジ領内(リヤド/アブハ空港・Aramco施設等)またはイエメン周辺への当該期間の攻撃について、実行主体または犯行声明主体として Houthi / Houthis / Houthi movement / Ansar Allah / Ansarallah / フーシ派 / アンサール・アッラー のいずれかを明示するもの。帰属付き(「〜が犯行声明」「連合軍/国連によれば〜」)可。場所言及のみ(「フーシ派支配地域」等)や攻撃と結びつかない言及は該当しない。
- 3段階を分けて記録: (i) Researcher Fact化=`research_ledger/audit/researcher_full_record.json`のfacts / (ii) Ledger登録=VERIFIEDか(AMBIGUOUS/REJECTEDなら理由) / (iii) B3採用=`storyline_b3/fact_selection_evidence.json` `selected_fact_ids`。(iii)Yesのみ下流へ。
- Writer反映: b1b/a2本文に攻撃主体がLedger帰属を保って登場(Grep `Houthi|Ansar ?Allah|Ansarallah|フーシ`)。B3採用済でWriter本文に無い場合のみ `--stage writer --regenerate-stage writer`(+advanced/standard各1回)を1回だけ許可。それでも無ければSTOP。
- 既存Gate(Fact Lock/記号Validator/IOL spec_ok/RF候補/AUW/Audio Validation Gate/style_profile_gate/key_phrase_source_gate)は従来どおり。HR/Lock/BLOCKは迂回せずSTOP。RF候補は件数・内容記録(合否はFable)。
- 日付・帰属CP: Ledger外具体描写0件、数字の帰属、時点明示の有無を記録(合否はFable)。
- Research最大3回(run_mey_02/03/04)。3回ともB3未採用=STOP(B3未採用)。手動Fact挿入・Ledger/B3手編集・`--regenerate-stage storyline_b3`による再抽選は禁止。
- 上限JPY180(本委任の新規支出合算)。次stage前に「既使用+次stage見積」が180超見込みならそのstageを開始せずSTOP。

## §1 開始条件チェック(S0、2026-10-20)
- 当日既使用: `daily_dev_cost_01.py --date 2026-10-20` adopted_jpy=513.24(予定値と一致)。残486.76。
- 出力dir: `er019_output/middle_east_yemen_saudi/` は `run_mey_01` のみ(run_mey_02〜04非存在)。
- runner引数実在: entertainment runner `--stage {research,ledger,storyline_b3,writer,advanced,standard,all}`/`--budget-jpy`/`--run-label`、audio runner `--stage {plan,scaffold,tts,assemble,player,all}`/`--level`/`--budget-jpy`/`--tts-backend`(既定speech_metadata_flash_lite)を`--help`で確認。
- 作業前`git status --porcelain`: 1142行(既存の他run差分。本委任は明示addのみ)。branch=work/post-merge-01。
- T-0: 委任文保存 `docs/pm/delegation_log/2026-10-20_..._委任_01.md`、sha256=3d7a45977694cc86366851ada8f14fcaa6c2e7ebc6459dd2ec3ae9228eeccf64、26036 chars(wc -m)。check_delegation_prompt=FAIL(理由: 「事前指定Grep一覧+追記位置・更新位置の手順」見出し不在。記録のみ・継続)。
