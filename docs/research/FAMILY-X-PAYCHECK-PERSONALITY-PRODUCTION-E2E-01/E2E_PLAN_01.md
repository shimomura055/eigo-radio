# FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 E2E_PLAN_01(委任_01、2026-10-21)

性質: 正式Production経路の記事生成(text+audio)。既存承認済み仕様の再利用。新仕様探索ではない。Detective Trial Pattern A/B/CはProduction不採用につき適用しない(Prompt/コード変更0)。

## §0 受入条件(CP)の事前固定(実走前。以後変更しない)
- CP-A1(因果断定なし): Std/Adv本文・In One Line・Key Phrases・Std日本語Supportに「収入増加が性格を変えた/引き起こした」の断定(英: caused/makes you/turns you into 等、日: 〜させる/〜になる[断定])が無い。相関/先行関係/因果を区別した表現(associated with / tends to come with / followed by 等)。
- CP-A2(双方向・効果の小ささ): Ledgerに「双方向の関連」「効果は小さい」のFactが登録され(Researcherが一次研究から取れた場合)、B3採用・本文に反映されているか。反映されていない場合は「反映なし」と記録(強制挿入禁止)。
- CP-A3(一次研究の確認): 一次研究(掲載誌・著者・研究対象[サンプル規模・国]・手法[メタ分析/縦断]・限界)をLedgerに帰属付きで登録したか。PsyPostのみで一次研究未到達ならその事実を記録(Research再試行の判断材料。Prompt変更禁止)。
- CP-A4(過度な一般化なし): 「給料が上がると冷たい人間になる」型の一般化・性格変化の方向/大きさの誇張が無い。
- CP-A5(読者接続): 研究の意外性+読者の仕事・生活との結び付け(観測記録。合否はFable)。
- CP-A6(Ledger外事実・帰属): 本文の数値・固有名詞・因果はLedger内かつ帰属保持。RF候補の件数・内容を記録(合否はFable)。
- Research再試行条件: 一次研究の基本Fact(掲載誌または著者、研究対象/手法、効果の大きさの性質)がLedgerに無い、またはB3採用Factが一次研究由来を含まない場合に限り、同一条件で再試行(最大2回: run_pp_02/03)。語数・文体理由の再試行禁止。
- regeneration: CP-A1/A4違反をSonnet CPで検出した場合に限り `--stage writer --regenerate-stage writer`(+advanced/standard)を1回だけ。2回目は不要でSTOP(Fable判断)。
- 禁止: 手動Fact挿入・Ledger/B3手編集・`--regenerate-stage storyline_b3`・HR/Lock/BLOCK迂回・有料run kill後再起動。
- T-3 Guardrail JPY150(本記事新規支出合算)。次stage前に「既使用+次stage見積」が150超見込みならそのstageを開始せずSTOP。

## §1 開始条件(S0、2026-10-21)
- 当日既使用: `docs/pm/tools/daily_dev_cost_01.py --date 2026-10-21` adopted_jpy=90.54(委任文記載73.47+並行agent分。本記事の新規支出は0)。
- 出力dir `er019_output/paycheck_personality/` 非存在確認済み。stop_scope_check rc=0(stop=false)。
- runner引数実在: entertainment `--stage {research,ledger,storyline_b3,writer,advanced,standard,all}`/`--regenerate-stage`/`--budget-jpy`/`--run-label`、audio `--stage {plan,scaffold,tts,assemble,player,all}`/`--level {a2,b1b,both}`/`--budget-jpy`/`--tts-backend`。
- 作業前 `git status --porcelain`=1137行(既存他run差分。明示addのみ)。branch=work/post-merge-01。
- T-0: 委任文 `docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_委任_01.md` sha256=dd78564cc676462a1b96b317392d83990dab6d40b372e6407a6196005f8c8575。check_delegation_prompt=FAIL(見出し名不一致=既知偽陽性)。ユーザー原文は記事B agent保存済みで本文一致(本文2586 chars、sha256=07f85daa4d877f58d831ddc59ea57ed21421cccf207d012e5952b0fd21bf26cf)につき保存skip。
