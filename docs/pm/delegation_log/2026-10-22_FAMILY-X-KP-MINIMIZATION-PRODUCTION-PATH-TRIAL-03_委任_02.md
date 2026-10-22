FABLE-DELEGATION-MARKER: KPMP-CLOSEOUT-AND-FOLLOWUPS-委任_02-20261022

# 委任(FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_02: (A)Fable分類`REJECTED`のCloseout記録[API 0]。(B)副次発見2件の0円確認: (B1)canonicalization INVALID時に`keywords_canonicalized.json`へ旧attemptのKPが残る問題を後段が読むか、(B2)他agentのtestが実STOP/STOP_ALLセンチネルを一時生成していた疑い[有料run誤停止・誤起動の実害])。JPY0)

## 管理ID
FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_02(OPEN-448。並行: `PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_01`(er103設計、OPEN新規行)、`HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_02`(er021系test、OPEN-447)が作業中。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち。`er021*_test*.py`/`er103_*`は触らない)。

## 性質/禁止
- 記録+0円調査(+B1が既存仕様内の明確な不具合なら最小修正可。方式変更は不可)。到達Status: OPEN-448=`REJECTED_FABLE_CLOSED`。Opus非該当。JPY0(API呼出禁止)。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。Production Prompt変更禁止。

## 前委任(委任_01)の受入記録(Gate 7、Fable記入)
- 当初目的(ユーザー原文逐語): 「最小化条件（新Promptの第3条）を現行Production経路のPromptに組み込み、同一14本文・Lunaで現行方式と比較する小規模Trialを行う。事前に見込み費用を算出した上で開始し、結果を報告してください。」
- 最終成果物: `docs/research/FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03/{TRIAL_DESIGN_03,TRIAL_RESULT_03}.md`、`KP_MIN_PRODPATH_COMPARISON_03.xlsx`、`er102_output/kp_min_prodpath_trial_03/`。commit 8decc5ece(決定記録)/374c4e5a6(Trial)。
- 証拠: 本番関数列`sc.run_key_phrases`(er019:411)を同一引数で呼出、Arm Bのみtemplate monkeypatch、同一shortlist。Arm A 14/14成功・Arm B 12/14(canonicalization INVALID 2件=代名詞断片)、平均語数2.167→2.033、評価V/Eは低下、C/U/S/X合計は同等、費用75.67(見積60〜100)、量産原価差+0.036円/セット。
- 一致・不一致: 事前見積→実行→報告=一致。合格基準(遵守同等以上・語数短縮・C/U/S/X上回り・V/E不低下)=未達(成功率低下・V/E低下)。
- 判定: ACCEPTED(Trialとして。結論は不採用)。**逸脱の記録**: 初回起動時にSTOPセンチネル確認(rc=3=STOP_ALL一時出現)の結果を見る前に有料processを2本起動し、直後にkill(usage log 0件、飛行中呼出≤8件・≤約3円は費用表に未計上)。PM_GOVERNANCE 26節(STOP確認後に開始)への手順逸脱として記録(実害=最大約3円)。
- 判定整合: 重大NG=なし/主因=現行DB hybrid経路は候補一覧から選ぶため元々平均約2.1語で短縮余地が小さい+短縮圧力で代名詞断片が選ばれcanonicalization失敗/是正対象=なし(Prompt変更不採用)/STOP理由=なし/提示=なし(ユーザー判断不要)。

## (A) Fable独立評価・Closeout(`TRIAL_RESULT_03.md` §7・§8へ逐語で追記)
### 7. Fable独立評価・Trial終了Status(2026-10-22)
- 分類: **`REJECTED`**(現行Production経路のKP選定Promptへの最小化条件(第3条)追加は不採用)。
- 根拠: (1)現行経路(候補DB照合方式)の出力は元々短く(平均2.17語、4語4件/60、5語超0)、第3条での短縮は平均−0.13語と小さい。(2)一方で短縮圧力により代名詞を含む断片(例`just my personality`)が選ばれ、原形化・一般化(canonicalization)が2/14単位で失敗し、最終KPが得られなかった(現行は14/14)。(3)評価の学習価値V・易しさ除外Eは低下、最小化観点は同等。(4)費用差は+0.036円/セットで無視できるが、品質面で利点がない。(5)ユーザー例示`think up what happens next`は現行Production経路で既に`think up`が選ばれており、他2例は現行経路では選定対象にならない。**先行Trial(全文渡し方式)で見えた「長く焦点のぼやけたKey Phrase」は、現行Productionの方式では元々ほぼ発生していない**。
- 読み方の注意: Arm Aと既存Production KPの一致は61%、A–B間75%で、LLMの非決定性による入れ替わりが約3〜4割ある。各arm 1回実行のため、小さな差は揺らぎと区別できない(本結論は「改善の証拠がない+失敗増」に基づく)。
- Closeout: Production/Prompt/Validator無変更。追加のPrompt案(第3条をcanonicalization側へ/代名詞断片の但し書き)は改善見込み低〜中のため起票しない(ユーザーが望む場合のみ)。
- 逸脱記録: STOP確認結果を見る前の有料process起動(即kill、≤約3円、PM_GOVERNANCE 26節の手順逸脱)。原因=手順順序の誤り。再発防止=runner側でSTOP確認のrc≠0なら起動しないガードを`er102`等のTrial runnerに入れるのではなく、委任文T-3/26節の手順を厳守(記録のみ)。
### 8. ユーザー判断
- 不要(現状維持=Prompt無変更。ユーザーが別案の検討を望む場合のみ指示を受ける)。

## (B) 副次発見の0円確認
- (B1) `keywords_canonicalized.json`の残骸: `er003_v1_n3_01_scaffold_generate.py`(Grep `keywords_canonicalized|CANONICALIZATION_INVALID|run_key_phrases`)と呼出元`er019_family_x_audio_production_runner_01.py:400-430`、Family Z側(`er026_*`/`er063_*` Grep `keywords_canonicalized`)で、canonicalizationがINVALIDを返した後に**後段(TTS/Store/assembly)が当該ファイルを読む経路があるか**を`file:行`で確定。(i)status INVALIDでrunnerが停止/再試行し後段がファイルを読まない→「実害なし」と記録のみ。(ii)後段がstatusを見ずファイルを読む経路がある→Redundancy NG済み旧KPが使われ得る実不具合=**既存仕様内の最小修正**(INVALID時に旧ファイルを`.invalid_<ts>`へ退避 or 書込前に削除、+unit test)を実施し、Regression(`run_project_regression.py --pattern "er003*_test*.py"`と`"er019*_test*.py"`の該当)PASSを確認。Production挙動の方式変更はしない。判断に迷う場合は修正せず選択肢を報告。
- (B2) STOP/STOP_ALLセンチネルのtest由来生成: `tools/stop_scope_check_01.py`が見るセンチネルの実パスを確認し、`*_test*.py`でそのパス(または同名ファイル)を生成/削除するtestをGrep(`STOP_ALL|STOP_NOTICE|stop_scope|sentinel`)。本日14:xx〜(KPMP起動時刻は`er102_output/kp_min_prodpath_trial_03/`のstop_check json参照)にSTOP_ALLを生成したprocessを、test実行ログ・git履歴・ファイルmtimeから特定。実害評価: (a)本物の有料runを誤停止させ得る(STOP_ALLを見て停止)/(b)削除側で本物のSTOP_ALLを消し得る(安全装置の無効化=重大)。(b)の経路が存在すれば**最優先で隔離**(testはtmp配下の別パスを使う)+再発防止test。(a)のみなら隔離+記録。いずれもProductionのSTOP機構自体は変更しない。
- 結果を`docs/research/FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03/FOLLOWUPS_01.md`に記録(file:行・実害区分・修正有無)。

## 更新
- `OPEN_ITEMS.md` OPEN-448: Status→`REJECTED_FABLE_CLOSED`、履歴1文(根拠要点・逸脱記録・B1/B2結果)。B1/B2で修正を行った場合は新規OPEN(最新+1)`FIXED_RECORDED`で記録(OPEN-447の形式に倣う)。
- `DECISION_LOG.md`: 末尾に「FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 Fable分類 REJECTED(2026-10-22)」エントリ(§7要旨、Production無変更、ユーザー判断不要)。
- `docs/pm/REPORT_LEDGER.md`: 1〜2行。
- `docs/pm/ACTIVE_TASK.md`固定ヘッダ(当日費用=2026-10-22 約878/1,000[出典 RESULT_PACKET_KPMP1 875+未計上≤3])。
- T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03_委任_02.md`(Nは`FABLE-DELEGATION-MARKER: KPMP-CLOSEOUT-AND-FOLLOWUPS-委任_02-20261022`を含むAgent tool_useの通番、279前後。先頭行で一致確認)。
- 明示add: 上記+修正ファイル(あれば)+FOLLOWUPS_01.md+delegation_log。commit: `KPMP 委任_02: Fable分類 REJECTED(最小化条件のProduction経路Prompt追加は不採用)記録+副次発見2件の確認<結果要約>、¥0`。push。

## 報告(RESULT_PACKET_KPMP2.md)
(A)記録箇所/(B1)(B2)の結果(file:行・実害区分・修正内容・Regression)/RESULT_PACKET 4行/raw URL。