FABLE-DELEGATION-MARKER: B3RD-PROD-C3-委任_08-20261022

# 委任(FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_08 [C-3]: 記事A「給料が上がると、性格も変わる？」の完成候補化。丸め判断の再実行(1回のみ)→Writer R0/R1/R2→Std/Adv text→text検査→TTS(正式経路、STANDARD)→ASR/Validator/品質検査→組立→ユーザー試聴ページ(新URL、旧ページ保持)→SSOT。費用Guardrail=本委任JPY120以内、案件300円以内。`PRODUCTION_WIRED`判定はFable)

## 0. 運用ルール・並列注意
他agent稼働中: (F-2)`er006_secondary_asr_01.py`の内部警告記録(最小追記)+SSOT、(E-1b)`er097_*`/PNPS docs。KP両方PASS(commit c9de15878)と多語同音救済(d228cbe70)は配線済み=本runのKey Phraseは新仕様(両Provider PASS必須)で生成される。あなたはコードを編集しない(必要なら設定・run引数のみ)。共有ファイル編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。他人の未commit差分(`er011_output/attempt_history.jsonl`、REPORT_LEDGER他人行等)を混ぜない。有料runの再起動禁止(26節)、各有料工程前にSTOPセンチネル確認、開始前に`daily_dev_cost_01.py --date 2026-10-22`で日次累計確認(1,000円以内)。`TTS_EXECUTION_MODE=STANDARD`(理由=Delivery優先。Batch換算原価も15節5区分で併記)。

## 1. 背景と Fable判断
- C-2(run_pp_02、commit 2c9f1027b): text工程完走、丸め0件。委任_07(commit 7455d0460)の調査で、B3入力は旧/Trial/新で同一、134,515人(C2)は同一入力・同一Promptで10回中9回`APPROXIMATE_OK`(実runの1回のみ`EXACT_REQUIRED`)=**Luna判断の揺れ**が主因。overlayは同一B3版で確定値再利用されるため、再判断には`force_rejudge`(既存オプション)が必要。
- **Fable判断**: 記事A再制作の目的(新しい数値丸め判断を適用した完成候補)に照らし、丸め判断のみを**1回だけ**再実行(約0.1円)し、概数が1件以上出ればWriter以降を再実行する。再び0件なら**再試行せず**そこで停止し報告(揺れの恒常対策=新仕様候補はユーザー判断へ)。判断の再実行は`force_rejudge`の正式経路で行い、overlayの履歴(初回=0件、再判断=結果)をprovenanceに残す(隠さない)。
- Advanced s10「personality and income were each measured at least three times」のFact整合疑いは、旧run_pp_01でも同じRFパターン(非Blocking)で、Ledger上は曖昧(真の逸脱と断定不可)。**修正しない**(Fable判断、記録のみ)。
- 日次累計は開始時に確認(直近の把握値≈JPY253)。

## 2. 作業
1. **再判断(1回)**: run_pp_02で`force_rejudge`(judgeのみ)を実行。結果(各中核数値の判定・理由・V1〜V9の適用)をprovenance/`audit/`に保存。**概数0件なら停止**して報告(Writer以降・TTSは行わない)。
2. **Writer以降(概数≥1の場合)**: `--regenerate-stage writer`相当の正式経路でR0→R1→R2→Std/Adv text(+Key Phrases・解説等のscaffold)。P-10決定論数値監査(JA/Adv/Std: 各数値が台帳厳密値かoverlay指定概数か)、Risk Flagger結果(丸め数値文のflag有無)、規則5例外が指定概数のみ、S5タグ漏れ0、P-11証拠((1)status=OK・gpt-6-luna・low、(2)`n_approximate_ok≥1`+R0 Promptに規則8と【概数表記】行[sha]、(3)resume経路API 0、(4)数値監査PASS)を記録。Before/After(**実際に使われた丸めのみ**: 旧run_pp_01本文 vs 新本文)。
3. **音声化**: 正式Production経路でStd/Advの全音声(本文・解説・Key Phrases等)をTTS(STANDARD)→ASR(新仕様: KP英語フレーズは両Provider PASS必須、多語同音救済有効)→Fact Safety/Validator/disfluency QA/M3 Gate等の既存品質検査→組立。HR Lockが発生した場合(例: KP 4回不成立、M3 Gate fallback)は迂回せず、その時点の状態で停止し報告(ユーザー試聴/個別承認が必要)。Store再利用はfail-closed判定に従う。
4. **試聴ページ**: `user_test/paycheck_personality_e2e_02/index.html`(新URL)を公開(Std/Adv結合音声・Key Phrases・text)。旧`paycheck_personality_e2e_01/`は無変更で保持(比較・ロールバック用)。GitHub Pagesで開けることを確認(Gate 7)。
5. **費用**: 実測(usage×正式単価、出典)で工程別(judge/Writer/英訳/RF/TTS/ASR)、記事セット総額、Batch換算、量産時の追加原価(丸め判断≈0.12円+KP dual≈0.65〜0.89円/10KP)を15節5区分で。
6. **SSOT**: OPEN-442→`ARTICLE_A_CANDIDATE_USER_LISTENING_PENDING`(またはHR Lock時のStatus)、OPEN-437へ実走証拠(P-11(2)実run充足)を追記しStatus=`WIRED_PENDING_FABLE`維持(判定はFable)。CURRENT_SPEC数値丸め節に実走証拠の所在を1行。REPORT_LEDGER。`docs/pm/USER_DECISION_REGISTER_01.md`: 新番号で「記事A完成候補(run_pp_02)の試聴受入」UDR(非blocking)と、「丸め判断の揺れ対策(同一入力で2回判断し一致時のみ概数、+0.1円/記事)=新仕様候補」をUDR候補として登録(推奨はFable記入欄)。
7. T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_委任_08.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: B3RD-PROD-C3-委任_08-20261022` を含むAgent tool_useの0始まり通番、260前後)。
8. commit(textまでで1回、音声・ページで1回。大きなwavはgitignore方針に従い、公開に必要なmp3/HTMLはcommit)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_B3RD8.md`へ報告(ユーザー§4の順: Family X正式実装の結果と証拠/V8・S5検証/記事Aで実際に使われた数値のBefore・After/Fact Lock・Ledger・RF・ASR・TTS・品質検査結果/Std・Adv完成音声と試聴URL/記事セット実費と量産追加原価/残存品質問題。+再判断の経緯[初回0件→再判断結果]を明記+RESULT_PACKET 4行+raw URL)。

## 3. 禁止
判断の2回目以降の再実行(1回のみ)、Checker緩和、承認仕様外の変更、旧run_pp_01・旧試聴ページの変更、HR Lockの迂回、Batch実行、費用Guardrail超過、他agent担当ファイルの編集。