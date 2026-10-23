FABLE-DELEGATION-MARKER: FAMILY-X-NEWS-2ARTICLES-E2E-02-委任_01-20261023

# 委任_01: Family X 新規2記事(記事A 2026年イグ・ノーベル賞/記事B 英国の電車スピーカー再生対応)— 承認済み正式Production経路でのE2E制作(Std/Adv完成候補+試聴ページ公開)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-X-NEWS-2ARTICLES-E2E-02_委任_01.md`(N≈340〜350、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FAMILY-X-NEWS-2ARTICLES-E2E-02_USER.md` に逐語保存。
3. ACTIVE_TASK.md: 別agent2本(FAMILY-Z-SOURCE-FIDELITY 委任_05=Z本文配線、FAMILY-Y 委任_04=DEV Trial)が並行。編集直前に再読込し、「並行タスク: FAMILY-X-NEWS-2ARTICLES-E2E-02 委任_01」の1行追加のみ。**TTS/ASR段の直前/直後に同行へ「有料run(TTS)進行中/終了(時刻)」**。他agentの同行に「有料run(TTS)進行中」があればMaster Audio Store競合回避のためTTS段のみ待機(5分間隔・最大30分)。
4. 予算確認: 本日(2026-10-23 JST)累計は約170円+並行Trial(Family Y上限250円、Z配線約17円)。本案件見込み約110〜270円(前回2記事実測 A 54.06/B 131.61円が参考)。**案件300円以内・日次1,000円以内を開始前に見積で確認**し、超過見込みなら開始前STOP報告。実費は記事別・工程別に`raw_usage_log`/cost.json出典で記録。

## 1. ユーザー指示原文(逐語)
```
# Claude Code / Fableへの指示
## Family X 新規2記事制作 — 正式Production E2E

### 1. ユーザー決定

Family Xで新たに以下の**2記事を制作する**。

当初1記事の予定だったが、ユーザー判断により2記事へ拡大する。

**記事A:ゴキブリのミルクに、鼻のかみ方? 今年も珍研究が受賞**
- テーマ:2026年イグ・ノーベル賞
- 珍しい研究の具体的な内容と、その研究に取り組んだ理由・科学的意義を紹介する。
- 単なる受賞研究の羅列ではなく、意外性・ユーモア・知的好奇心を重視する。
- 事実と演出を明確に区別し、研究結果を誇張しない。

**記事B:電車でスピーカー再生する人たちに英国が厳しい対応?**
- テーマ:英国の公共交通機関でイヤホンを使わず音楽・動画などを再生する行為への対応
- 実際に何が問題視され、どのような規制・取り締まりが行われているのかを確認する。
- 法律・規則、提案段階の施策、実施済みの対応を混同しない。
- 公共マナーや文化の違いを、軽快で興味深い記事に仕上げる。

両記事とも、最新の信頼できる原典を確認し、記事の事実関係を確定すること。

### 2. 制作範囲

**承認済みのFamily X正式Production経路で、両記事をStandard/Advancedセットで完成候補まで制作する。**

- Researchから記事生成、Key Phrase、音声生成、品質検査、最終組立まで、既存の正式Production仕様を適用する。
- 承認済みの音声速度、Voice、Key Phrase、ASR検査、発音同等性、数字の丸めなどの仕様を維持する。
- 必要十分な品質に達したら追加の磨き込みやTrialを行わず完成させる。
- 既存の完成記事や他FamilyのProductionには影響を与えない。

### 3. QCD・進行方針

**品質(Q)>納期・速度(D)>量産単価(C)** を遵守する。

- 2記事は独立して進められる工程を並列化し、全体の完成時間を最小化する。
- 不要な日付分割、待機、逐次処理を避ける。ただし音声Storeなど共有資源の競合には配慮する。
- 既存成果・キャッシュを活用し、不要なAPI呼出、再生成、重複検査を抑える。
- 量産単価70円/記事セットの目標を意識し、実費を記事別・工程別に記録する。
- 既存の承認済み開発予算・日次上限を守る。2記事への拡大だけを理由に予算上限を自動的に増額しない。
- 承認済み仕様内の不具合は、原因分析から修正・再検証まで自律的に解決する。
- 新仕様の採用、品質基準の変更、予算・Scope超過、重大な品質問題など承認が必要な場合のみ停止して報告する。

### 4. 試聴ページ

両記事それぞれについて、ユーザーが最終試聴できる公開ページを用意する。

- Standard/Advanced切替
- 全編通し再生
- パート別再生
- 全スクリプト(Preview、Comment、本文、In One Line等)
- Key Phraseと意味・解説
- 開発者向けの不要な情報は表示しない

既存の承認済み試聴ページ形式を再利用し、ページ制作自体に余分な工数をかけないこと。

### 5. 完了報告・受入条件

2記事とも正式Productionでの制作・品質検証・試聴ページ公開まで完了させ、Fableの独立評価後にまとめて報告すること。

報告内容:

1. 記事A/Bそれぞれの内容の要約
2. Standard/Advancedの試聴URL
3. 品質検査結果、正式runtime evidence
4. 承認済みProduction仕様との整合確認
5. 記事別の制作費用・制作時間・主なコスト要因
6. Fableの独立受入判断
7. 残存リスク・未解決Open Item・SSOT/Git反映状況

「Production経路での制作完了」と「ユーザー最終試聴PASS」は区別すること。

**原則として途中のユーザー判断待ちは設けず、2記事の完成候補・試聴ページ公開まで一気通貫で進める。**

ただし、承認境界やSTOP条件は厳守する。既存仕様の範囲で解決できる技術的問題は、ユーザーへ逐次転送しない。
```

## 2. 前提(前回E2Eの手順を踏襲)
- 前回: `docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-01/RESULT_01.md`、委任文 `docs/pm/delegation_log/2026-10-22_FAMILY-X-NEWS-2ARTICLES-E2E-01_委任_01.md`(手順・コマンド・run dir規約・ページ生成script `er019_nws_final_page_01.py`/再生検証 `er019_nws_play_verify_01.py`、ページ標準検査)。同じ正式経路・同じ手順で実施(コード変更0が原則)。
- 現在の正式仕様(前回以降の追加分、すべてPRODUCTION_WIRED・既定ON): KP品質改善①②(保護撤去・CMU登録語のみ選定、OPEN-458)、er109同音・異表記救済(X/Z scope、OPEN-459)、PNAP、KP3V、KPFT 3件、Std 6%減速(X本文)、値ガード、HR Lock、`TTS_EXECUTION_MODE=STANDARD`。**flag・Prompt・閾値の変更は不可**。
- slug案: 記事A `ig_nobel_2026`、記事B `uk_train_speaker_playback`(既存slugと衝突しないことをGlobで確認)。run id `run_nws_02`(前回と区別)。
- テーマはユーザー指定済み(13節の候補提示は不要)。JAタイトル・本文はWriterが生成(ユーザー記載タイトルは「テーマ名」として扱い、Writer出力を上書きしない)。
- 事実確認: Research(web_search)→Fact Ledger(VERIFIED/AMBIGUOUS/REJECTED)→B3で、記事A=受賞研究の内容・理由・意義を原典(Improbable Research公式・一次報道)で確定、「ゴキブリのミルク」「鼻のかみ方」が2026年受賞研究として実在するかをLedgerで確定(実在しない/年が異なる場合はLedgerに従い、ユーザーのテーマ文言に合わせて事実を曲げない。その場合は報告で明示)。記事B=英国の規制・提案・実施済み対応(例: 議会提案・鉄道会社の規則・罰則)の区別をLedgerで確定し、未確定事項はFact Lock規則に従い断定しない。
- 既存記事・他Familyへの影響0(新規run dirのみ。Master Audio Storeへは通常どおり登録)。

## 3. 作業
1. テキスト段(2記事並列): research→ledger→B3→writer R0〜R2→Adv英訳→Std簡易化→RF。Ledger結果・AMBIGUOUS・B3採用Factを記録。
2. 音声段(TTSはStore競合回避のためA→B直列、scaffoldは並列可): scaffold(Preview/Comment/KP選定[KPFT 3件・CMU gate]/gloss/解説)→TTS→ASR(3層)→gate→assemble。STOPセンチネル確認rc=0、HR Lock到達時は迂回せず報告(ただし既存仕様内で自律解決できるもの=例: 誤Lockの原因が既知の不具合、は原因分析→修正→再検証まで実施)。有料runの再起動禁止(26節)。
3. ページ: 前回と同形式で `user_test/<slug>_e2e_01/index.html`(Std/Adv切替・通し・パート別・全スクリプト・KP意味解説・開発者情報非表示)。commit/push後HTTP200+Playwright全audio再生+ページ標準検査。
4. 品質観察(合否はFable): 事実と演出の区別、誇張の有無(記事A)、法律/提案/実施の区別(記事B)、PASS_WITH_WARNING箇所(耳確認推奨箇所の特定)、PNAP発火、KP投票結果、er109発火有無、RF候補。
5. 費用: 記事別・工程別(Research/Ledger/B3/Writer/英訳/RF/scaffold/TTS/ASR/読み調査)を出典付きで。1回限り費用(Ledger新規登録等)を分離して定常見込みを算出。所要時間も記録。
6. 証跡: `docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-02/RESULT_01.md`(前回RESULT_01と同じ構成)、評価json。
7. SSOT: OPEN_ITEMS新item(Status=`E2E_COMPLETE_CANDIDATE_PENDING_USER_LISTEN`)、UDR(2記事試聴PASS/NG、未回答)、DECISION_LOG(ユーザー決定・テーマ)、REPORT_LEDGER。commit(明示add、wavはpushしない、mp3のみ)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 4. 禁止
- Production .py/Prompt/flag/閾値の変更、追加Trial・磨き込み、ユーザー記載タイトルの強制、事実の誇張、HR Lock/STOP迂回、有料run再起動、案件300円/日次1,000円超過、他記事・他Familyへの影響。

## 5. 報告(docs/pm/RESULT_PACKET_FXN2.md、同内容を最終報告で)
(1)記事A/Bの内容要約(JAタイトル・構成・KP) (2)試聴URL (3)品質検査結果・runtime evidence(Ledger、Gate、ASR、KP投票、PNAP、er109、HR、PASS_WITH_WARNING箇所) (4)承認済み仕様との整合(flag/コード変更0) (5)記事別費用・時間・主なコスト要因・定常見込み (6)品質観察(事実/演出、法律/提案/実施の区別、耳確認推奨箇所) (7)commit・raw URL・SSOT (8)残件 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。