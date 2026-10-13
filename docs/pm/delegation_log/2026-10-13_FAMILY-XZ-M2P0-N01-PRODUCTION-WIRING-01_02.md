## 管理ID

FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02(修正1回目: Opus条件A/C必須修正1〜9の反映→Production実装→回帰→Family X Coffee runtime evidence(KP M2P0再生成+Full Story N01音声化+試聴ページ)→Family Z配線+mock→SSOT)。並行タスク: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_02(`er068_*`、SSOT編集中の可能性)。本委任はSSOT編集権あり(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)。SSOT編集は最終工程で、直前に`git status --porcelain`で他agentの未commit変更を確認し、あれば60秒×5回待ち、残っていても自分の変更行のみ追記・自分の変更ファイルのみ明示add。一時ファイル: `docs/pm/ACTIVE_TASK_XZW.md`/`docs/pm/RESULT_PACKET_XZW.md`(追記)。`.git/index.lock`存在時は30秒待ち×3回、commit前に`git fetch origin && git merge --ff-only origin/main`(不可なら`git pull --no-rebase`、conflict時は両追記保持)。

## 性質/到達上限Status/禁止事項

- 性質: Production実装(ユーザー正式決定: M2P0・N01=`APPROVED_FOR_PRODUCTION`、Family X/Z)。Family X: 実装→回帰→Coffee音声化までGO。Family Z: 実装(N01配線)+mock/dry-runのみ(記事再生成・音声化STOP、M2P0はZ-1でSTOP=着手しない)。
- 到達上限Status: Family X=`PRODUCTION_WIRED`(Production Wiring Checklist 1〜11全充足時のみ。1つでも欠ければ「配線済み・未完了」と明記)。Family Z=`配線済み・runtime未確認`(`PRODUCTION_WIRED`にしない)。
- 費用: 上限¥80(Guardrail。soft stop ¥60。Fable承認済み。Coffee 1記事: KP再生成+KP音声+Full Story Std/Adv N01+ASR。期待¥21〜27、最悪¥57)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。**無制限再生成の禁止**: KP再生成は1レベル1回まで(NGでも引き直さない)、TTSは既存retry上限(標準2回+fallback1回=通算3回)内のみ、上限到達でSTOPしFableへ報告。予算Guardが全stage(KP LLM・TTS・ASR・Azure)を集計しているかを実行前に確認し、TTSのみなら全stage累計で止める仕組みを入れる(Opus必須9)。
- 禁止: ユーザー未承認の仕様変更、新Prompt探索・追加Trial、M2P0以外のKP方式/N01以外の音声Prompt、Validator・ASR判定・速度/ポーズ基準・retry/fallback/STOP条件・Std 6%減速・減速後再検証の緩和/無効化、Family Z Previewの先行採用、Family Zの記事再生成・音声化・KP再生成、Z側M2P0の実装(Z-1 STOP)、未承認の連結発音改善ロジック(er065/er068系)の混入、`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`のsource・値表示、秘密値の出力、`*.wav`・`**/telemetry.jsonl`・`**/evidence_*/**/*.log`・`words/`のadd、`ACTIVE_TASK*.md`/`RESULT_PACKET*.md`のcommit、Melos run_e2e_02配下・Master Store(手動編集)・HR Lock・attempt_history(手動編集)への書込、外部停止プロセスの再起動、監督ループ/`timeout`ラッパ、有料runのkill、Batch TTS。
- STOP条件: 承認範囲を超える仕様変更が必要/予算Guardrail暴走疑い/Parity Gate(Opus必須3)不一致で原因未特定/M2 snapshot回帰不一致(2回照会案Aへ逃げず原因特定までSTOP)/Family X Full Storyが既存retry上限内で合格しない(HR経路は既存どおり。その場合は音声化未完として報告)/`STOP_NOTICE`/`STOP`/`STOP_ALL`。
- STOP確認義務: 開始時に`er026_output/family_z_production_e2e_01/`・Family X run dir配下の`STOP_NOTICE`/`STOP`/`STOP_ALL`を確認し記録(旧記録は非適用)。
- Opus独立技術レビューGate判定: 条件A/Cレビュー済み(本委任は反映+実装)。
- 時間見込み: 180〜240分(実装・test 90/Coffee run 60/ページ・evidence 30/SSOT・git 30)。並列化: KP実装とN01実装は独立(先にN01→KPの順でも可)。Coffee runはStd/AdvのKP stageを**直列**実行(Opus Q7: Wiktionary 429回避、外部rate limitを理由に並列化しない)。
- 最新モデル原則: Production同一モデル(TTS `gemini-3.8-flash-lite-tts`/Aoede、KP `gpt-6-luna`)。model_id実測を記録。
- T-2: `TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示。実行前に(1)差分再生成(KP+Full Storyのみ)が対象コード上で可能か確認、(2)音声再利用キャッシュ(Master Store)の有無を確認し、Preview・Comment・IN_ONE_LINEは再利用、(3)`--budget-jpy 80`を明示、(4)想定外の全再生成と判明したらAPI実行前にSTOP。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

(E-1/D-1/G-1/F-1/T-0/T-2/T-2追記/T-3は委任文どおり。全文は委任_01保存分および本文参照)

## ユーザー指示(原文)

委任_01と同一(`docs/pm/delegation_log/2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01_01.md`「ユーザー指示(原文)」節を参照。全文保存済み)。

## Opusレビュー結果と Fable判断(反映必須)

総合判定: 修正してから委任_02へ進む。必須1〜9:
1. demoted_allowはB'方式: 拡大照会の生の結果を先頭60のkeyに絞り、純関数の後処理(build_hits→gate_and_merge→既存語除外→refine)を再実行し、Stage1由来の`matched_dbs==["wiktionary"]`かつ`db_categories==["multiword_term"]`の候補を足す。照会は1回。生の結果の取り出しは**coreの戻り値へ`results`キーを追記する(追記のみの共有module変更、既存戻り値は不変、testで固定)**=Fable判断。snapshot回帰で不一致なら2回照会へ逃げず原因特定までSTOP。
2. M1パラメータを省略せず明記: `phrase_cap=20`、`realign=True`、`u2="tierH+S"`、`r2/r3=True`、`u3_exclude/u3_annotate=True`、順序`default`(phase2_run_03 L124-125)。設計書の「cap15/cap15の外側」は誤りとして訂正。M2は予約枠追加後にU2(Tier-H)を再計算し元候補も削る(machine L146-149)点を明記(「M1+3件」ではない)。CURRENT_SPEC転記文言も同様。
3. Parity Gateは最終Promptで判定: rows shaに加え、Trial `build_ctx`記録の`prompt_sha256`(M2P0 msg全文)とProduction経路のメッセージshaの一致をGateにする。Trialは候補行をspan補正の前に組み立て、Productionは後なので、注釈のcandidate_id対応表は補正後の`shortlist_with_ids`から作り、補正で除外された候補への参照は捨てる。予約枠候補のevidence文字列(`placeholder_title[...]`/`rule_poss_pattern`、machine `ev_text`)も移植。
4. M2内部例外をfallbackで隠さない: Wiktionary通信失敗とM2内部例外を別reason_code(`M2_SUPPLY_EXCEPTION`)でtelemetry記録、testで区別。Fable判断: M2内部例外は既存どおりStrategy L fallbackに乗せる(新STOP条件は追加しない=新仕様回避)。ただしevidence合格条件は`kp_backend_used=db_hybrid`かつ`kp_supply=m2`とし、fallbackした場合はM2P0未発火として報告。
5. N01 default化はB': `FAMILY_X_ROLE_STYLE_EN`定数(17ファイル参照)を直接書き換えない。案Cのprofile機構(sha検証・固定記録・M2/M5/M3 Gate)を使い、`resolve_run_profile`で「記録なし・CLI指定なし・run stateなし」の新規out_dirをN01 profileへ解決させる。既存out_dirはM2 run state検知で課金前に止まるので`--style-profile default`明示でresume。defaultのbyte一致test(N-4)は期待値を意図的に更新。
6. Coffeeはdefault経路ではrunできない: Std Preview/Comment(R2)再利用+Adv KP解説(P3)再生成のため「N01+R2+P3」結合profileを明示CLIで指定。Checklist 11の照合表では「FULL_STORYがN01に解決されるのは同じ関数・同じ定数を通る(runtimeで確認)/defaultのprofile選択はtestと¥0 dry-runで確認」と書き分ける。
7. Family Z N01差替えのresume混在対策: 既存Z run dir(Melos等)はPD8生成済み。run単位でstyle labelを記録し、不一致ならSTOPする仕組みを入れる(Fable判断: 記録+不一致STOPを採用。安全側の追加であり既存Gateの緩和ではない)。test化。新規Z runでなければN01にならないことを明記。
8. 速度・ポーズは既存基準で合否: 既存Productionの速度/ポーズ基準値と出典をEVIDENCEに明記し合否判定。自動化基準が無い場合はその旨を明記し、Trial参照値(Std 157±6 WPM[減速後]/Adv 167±6、文末平均≤498/593ms、長無音≥800ms≤1)を参考値として実測を併記(新Gateは作らない)。Full Story各partが通常attempt(N01)で合格したかfallback take(N01でない)で合格したかをpartごとに記録し、fallback合格partはN01発火evidenceにしない。
9. 予算上限の対象範囲確認(上記「費用」欄)。
推奨(採用): byte parityを2段(純関数は逐語copy+source sha固定[Er028方式]、組立部分は出力一致)/runtime evidenceにProduction実送信PromptとTrial M2P0 Promptの差分(¥0、一致必須ではなく差分報告)+fragment_risk付き候補が最終KPに選ばれたかの記録/`shortlist_cache`にpairs/m2メタ保存+cache hit時の注釈同一test(S-3拡張)。
Q5条件(採用): `--scaffold-only kp`は(i)`sc.run_key_phrases(..., kp_backend=kp_backend)`呼出は既存`run_theme_scaffold`内の同じ行を通す(support生成ブロックのみskip)(ii)`record_scaffold_article_sha`と`scaffold_run_summary`/`kp_backend_used`記録維持(iii)support成果物(sha照合済みcopy)がout_dirに無ければSTOP(iv)KP再生成は1レベル1回。
Q6(採用): Std減速instructionは連結しない逐語方式(X/Zとも)。Zの現行`PD8_A2SLOW`連結から変わる点をSSOTに明記。
Q7(採用): Std/Adv KP stageは直列、OPEN-337実装まで複数記事KP並列禁止(SSOT運用注意として記載)。
Fable暫定判断F-1〜F-5はOpus賛成(F-1はB')で確定。

## 事前指定Read一覧 / 事前指定Grep一覧+追記位置・更新位置の手順 / 作業内容 / 実行コマンド全文 / SSOT追記文 / Git / 報告(RESULT_PACKET項目)

(原文どおり。作業内容: 1実装(M2供給module・core `results`追記・selector挿入・N01 profile・resolve_run_profile・Z narrator N01+style label不一致STOP・`--scaffold-only kp`・予算Guard全stage集計・fallback/減速/再検証/Gate/retry無変更) 2テスト(TEST_PLAN_01のM/S/N/Z mock+既存回帰ベースライン/実装後) 3 Family X Coffee runtime evidence(上限¥80、`EVIDENCE_01.md`+json、`CHECKLIST_01.md`) 4 Family Z mock/dry-run 5 SSOT・`FINAL_REPORT_01.md`(10項目)。Git: コミット3つ、trailer `Managed-ID: FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01`、明示addのみ。報告項目(0)〜(9))
