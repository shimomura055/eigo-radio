## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_07(ユーザー承認(b)「案2/案1+2への最終B3確認パス追加」のTrial harness是正・test・dry-run・Stage 1a補正モード実装・SSOT記録。**有料API呼出ゼロ(JPY0)**。有料のStage 1a補正実行・Stage 1bはOpus条件Aレビュー後の次委任)。並行タスク衝突: なし(BAPEは#106待ちで有料実行なし、S3Wは試聴待ちで作業なし)。commitを伴う作業は本委任のみ。

## 性質/到達上限Status/禁止事項
- 性質: Trial専用harness(`er082_rlct_trial_01_*.py`)の設計是正。到達上限Status=`HARNESS_CORRECTED_DRYRUN_PASS_PENDING_OPUS_A`。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDには到達しない。
- 禁止: 有料API呼出(OpenAI/Gemini/web_search)一切禁止(dry-run=StubClientのみ、`--paid-confirm`を付けない)。Production runner/Prompt/Style/`er002_*`/`er053_*`/`er0XX`のProduction code変更禁止。`er082_output/rlct_trial_01/coffee_prices/*`・`inbound_tourism/M0,M0b,M0p,M1,M2,M3`等の既存Stage 1a成果物の変更・削除禁止(sha snapshotで前後不変を証明)。Research再生成禁止。Family A/B/C禁止。git add -A/-u/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。STOPセンチネル削除禁止。
- Opus独立技術レビューGate(11-3): **条件A該当**(LLM出力を後段で解釈し再度LLMへ返す処理フローの変更=(2)(4)(5))。本委任は「実装+dry-run」まで。有料実行前にFableがOpusレビューを入れる。Sonnetは設計差分を`TRIAL_DESIGN_03.md`として明文化し、Opusが読む前提で書く。
- 時間見込み: 全体約60〜90分(設計文書15/実装25/test+dry-run20/Coffee照合+SSOT+commit15)。並列化: 単一Agent・直列(同一ファイル群編集のため)。
- 費用/日次: 当日(JST 2026-10-17)既使用約JPY284.1(出典: ACTIVE_TASK.md L4=SJS4 41.6+S3W 18.5+RLCT 1a 212.80+任意A 10.88)/残約715.9/本委任JPY0/改善見込み高/承認区分: C(承認済みscope内: ユーザー2026-10-17指示§9「Trial専用harnessの必要な是正」)。
- 前委任(委任_06)のQDC記録: 目的=Stage 1a人手評価(JPY0)/試行=1回/結果=STAGE_1A_EVAL_01.md完成、commit 2030dab41/原因仮説=案2で再選定0回の記事は検証結果が最終B3へ未反映(証拠: inbound M2/M3 Brief同一、F05 AMBIGUOUS断定1件、RESULT_PACKET_RLCT6 L5-6)/改善見込み=高(ユーザーが(b)で設計是正を承認)/費用JPY0/次の一手=本委任。
- 前委任(委任_06)の受入記録(Gate 7): (1)当初目的(ユーザー原文逐語、`..._TRIAL-01_USER.md` L100/L104/L106/L110)=「B3品質 | 面白さ、一貫性、事実との整合」「B3の構成差は、次の3段階で分類する。」「軽微：ストーリーの骨格は同じ。」「構成差の大きさと品質の良し悪しは別々に判定する。」 (2)最終成果物=`docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/STAGE_1A_EVAL_01.md`(commit 2030dab41) (3)証拠=RESULT_PACKET_RLCT6 L3-8(ブラインド手順・構成差3段階・品質3軸・中心Fact断定件数・Verifier再現性) (4)一致=構成差と品質を別軸で判定・3段階分類・全方式掲載は一致。不一致=n=1単一評価者(暫定、原文は評価者数を規定せず) (5)判定=ACCEPTED(暫定評価として。確定評価は5記事完了後)。判定整合: 重大NG=なし / 主因=なし / 是正対象=なし / STOP理由=なし / 提示=可。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 本委任はJPY0のため費用上限[Cap]なし。
**T-0補足(必須)**: 委任文は本文を**全文そのまま**保存する(要約保存はFAIL逸脱として記録される)。保存先=`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_07.md`。加えて下記「ユーザー指示(原文)」節の本文(「# Claude Code／Fableへの指示」から「**結果を報告した時点でSTOPし、Productionへの実装は行わないこと。**」まで)を**一字も省略せず**`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_DESIGN-FIX-1B_USER.md`へ保存し、`wc -m`文字数とsha256をRESULT_PACKETへ記録する。stop_scope_check: `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 --run-dir er082_output/rlct_trial_01 --out er082_output/rlct_trial_01/_stop_scope_check_07.json`(rc=3なら停止して報告)。

## ユーザー指示(原文)
(2026-10-17受領。Fable報告「Stage 1a 評価結果 — 1b開始前にご判断が1件必要です」への回答。選択肢(b)承認。)

# Claude Code／Fableへの指示
## Research／Ledgerコスト最適化Trial — 設計是正・Stage 1b継続

**管理ID：FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01（継続）**

### 1. ユーザー判断

**選択肢(b)を正式承認する。**

案2・案1＋案2に、検証結果を最終B3へ反映する確認パスを追加し、Stage 1bへ進めること。

既存のFamily X仕様である「AMBIGUOUSは断定禁止」「REJECTEDは使用禁止」を維持するためのTrial設計是正であり、新しいProduction仕様の採用ではない。

**今回の到達目標：5記事×4方式のTrial完了・結果報告。Production変更は禁止。**

### 2. 是正内容

現状の案2では、

Research → 未検証FactからB3選定 → 選定Fact検証

の後、REJECTEDが出なければ検証前のB3がそのまま最終確定する場合がある。

これを是正する。

**選定Factの検証完了後、最終B3の確定前に検証結果との整合を必ず確認すること。**

- VERIFIED：通常使用可能
- AMBIGUOUS：不確実性・留保条件をB3に反映。無条件の断定は禁止
- REJECTED：使用禁止。B3による再選定・再構成が必要

選定FactにAMBIGUOUSまたはREJECTEDが含まれる場合は、検証結果・理由・使用上の制約をB3へ返す。

B3にストーリー構成を再評価させ、必要に応じてFactを再選定する。

新たに選ばれたFactは独立検証し、既に検証済みのFactは結果を再利用する。

**REJECTEDを単純削除しただけの不完全なBriefや、AMBIGUOUSを断定したBriefを最終確定してはならない。**

再選定上限は既存Trial設計の最大2回を維持する。上限到達時に品質条件を満たせなければ未成立として扱う。

### 3. Stage 1aの比較条件の整合

Stage 1aの訪日客統計について、案2・案1＋案2に新しい最終B3確認パスを追加実行する。

既存のResearch・Ledger・初回B3を再利用し、必要な確認パスだけを実行すること。

追加費用見込み：約JPY22。

既存成果を破壊せず、修正前後のBrief・採用Fact・品質・費用の差を記録する。

Coffeeについても同じ最終確認条件への適合を照合し、既に検証結果が反映済みなら不要な再生成を行わない。

### 4. Stage 1bの実施

対象3記事：

1. Disney+値上げ
2. OpenAI著作権訴訟
3. FOMC・住宅ローン金利

既存の`TRIAL_DESIGN_02.md`および費用見積v2を基本とし、今回承認した確認パスを加える。

各記事について、次の4方式を比較する。

| 方式 | 内容 |
|---|---|
| 従来方式 | 全Fact検証 → B3 |
| 案1 | 全Fact検証（上限3回）→ B3 |
| 案2 | B3選定 → 選定Fact検証 → 最終B3確認 |
| 案1＋案2 | B3選定 → 上限付き検証 → 最終B3確認 |

同じResearch下書きを使用し、既存Production・過去Trial成果を改変しない。

### 5. コスト比較方法

**過去Production実測との比較に加え、同日・同条件で再実行した従来方式との比較を明示すること。**

少なくとも以下を分けて報告する。

- 過去Production基準（M0）との比較
- 同日・上限なし再検証（M0'）を用いた参考比較
- 自然なB3生成ばらつき（M0b）
- 各改善方式の実測費用
- 再選定・最終B3確認パスの追加費用

M0'がB3を含む完全な同日E2E基準でない場合は、その限界を明記すること。

比較条件が異なる数値を、厳密な同条件比較として扱わない。

**案1の3回上限については、Fact別の上限到達を確認できていないため、検索削減をすべて上限の効果と断定しない。**

検索ツール呼出回数・クエリ数・LLM費用を区別して記録する。

### 6. 品質比較

各方式について以下を評価する。

- VERIFIED／AMBIGUOUS／REJECTEDの判定差
- 既知の誤Factの検出結果
- AMBIGUOUSの断定が残っていないか
- REJECTEDが最終B3に混入していないか
- 最終B3の採用Fact
- ストーリーの主題・展開・結論
- B3構成差（軽微／中程度／重大）
- 面白さ・一貫性・事実整合
- 再選定回数・確認パス費用
- 未成立件数
- Fact Lock／Risk Flaggerとの整合

構成差の大きさと品質低下を混同しない。

Verifierの判定ばらつきによる問題と、案1・案2の方式固有の問題を区別する。

既知の誤判定（Coffee F12、訪日客F12等）は、原因・影響・最終採用の有無を明示する。今回、Production Verifierの改修は行わない。

### 7. 故障注入テスト

既にユーザー承認済みの任意Aを維持する。

- 実施済みCoffeeの結果は再利用
- 未実施の範囲は承認済み設計・費用枠内で実行
- 誤Factの検出漏れを確認
- Productionや元データを変更しない

追加の任意B・任意C・Stage 2は、既存承認範囲外のため自動実施しない。

### 8. 費用・実行管理

既存承認額：

- Stage 1a上限：JPY493
- Stage 1b上限：JPY493
- 任意A上限：JPY54
- **Trial全体上限：JPY1,040**

Stage 1a＋任意Aの既存実測：約JPY223.7。

今回のStage 1a補正とStage 1bを含め、各区分・全体の費用上限を守ること。

追加確認パスの費用を必ず計上する。既存の上限に収まらない見込みが生じた場合はSTOPする。

日次JPY1,000のsoft budgetを維持し、必要に応じて別日に分ける。

Web検索手数料を含めて費用を管理する。

### 9. 作業範囲・禁止事項

許可する作業：

- Trial専用harnessの必要な是正
- Stage 1aの必要最小限の補正
- Stage 1bの承認済み比較Trial
- 費用・品質評価
- Fable独立レビュー
- Trial成果・判断待ち事項の記録

禁止事項：

- Production runner・Prompt・Styleの変更
- 未承認方式のProduction採用
- 新しいコスト削減Trialの追加
- 不要なResearch再生成
- 無関係なFamilyへの変更
- Family A／B／Cの開発
- 承認範囲外の有料検証

commitを伴う作業は同時に1件のみとする。

### 10. STOP・Closeout

既存の費用Gate・品質Gate・STOP条件を維持する。

今回の設計是正が想定どおり機能しない場合、品質条件を緩和して続行しない。

Trial終了後、案1・案2・案1＋案2をそれぞれ以下に分類する。

- REJECTED
- VALIDATED
- USER_DECISION_REQUIRED

**VALIDATEDはProduction採用を意味しない。**

ユーザーの正式採用判断なしにProduction配線へ進まない。

最終報告では、まず以下を簡潔に提示する。

1. 5記事×4方式のコスト削減比較表
2. B3品質への影響
3. AMBIGUOUS／REJECTEDの扱いが適切になったか
4. 案1の検索上限3回の実際の有効性
5. 再選定・確認パスを含む実質削減額
6. 各案のTrial Status
7. ユーザーに必要な採否判断

**結果を報告した時点でSTOPし、Productionへの実装は行わないこと。**

(原文ここまで)

## KPI provenance欄
本委任のdry-run出力は全て`synthetic`(StubClient)。既存Stage 1a実測(`fresh`)は参照のみ・不変。E2E自己確認: No(本委任は有料経路を含まない)。

## Opus台帳更新
`docs/pm/OPUS_FINDINGS_LEDGER.md` OF-RLCT-R-07(AMBIGUOUS断定の測定): 状態を「EVIDENCED(1a暫定)→FABLE_DECIDED(ユーザー承認(b)により確認パス追加=Trial設計是正、2026-10-17)」へ更新する1行を追記(既存行は消さない)。OF-RLCT-R-06(REJECTED機械削除禁止・再選定): 本是正で同じ入口を使う旨を1行追記。

## 是正設計(Fable指定。Sonnetはこの仕様で実装し、`TRIAL_DESIGN_03.md`に明文化する)
**D1. 確定条件(最終B3確認)**: `select_then_verify`の各roundで選定Factの検証を終えた後、次の両方を満たすときのみ`_finalize_sel`へ進む。
  (i) 選定FactにREJECTEDが無い。
  (ii) 選定Factのうち**AMBIGUOUSであるもの全て**が、その選定`sel`を生成したB3呼出の候補Ledger上で既に`[AMBIGUOUS …断定禁止…]`タグ+verification_notes付きで提示されていた(=B3がAMBIGUOUSを知った上で選んだ)。選定Factが全てVERIFIEDなら(ii)は自動的に満たす(B3追加呼出なし。`confirm_pass="NOT_NEEDED_ALL_VERIFIED"`を記録)。
**D2. 確認パス**: (i)または(ii)を満たさない場合、既存の再選定入口(`select_b3_trial(... extra_note=...)`)を使ってB3へ返す。noteは新関数`build_confirm_note(rejected, ambiguous_new, verdicts, draft, unverified_ids)`で生成し、必ず次を含む: REJECTED各ID+理由+「選定禁止」/ AMBIGUOUS各ID+verification_notes+使用上の制約(「このFactを使う場合、Storyline・Briefでは不確実性・留保条件を明示し、無条件の断定をしてはならない」)/ 検証済み他Factの判定/ 未検証候補一覧と「新たに選んだFactだけを独立検証する」/ 「Storyline構成を再評価し、必要ならFactを選び直す」。候補Ledgerは`render_candidate_ledger(draft, verdicts)`で現在の判定タグを反映(既存どおりREJECTEDは本文から外す)。
**D3. 回数上限**: 初回B3の後のB3呼出(REJECTED起因の再選定もAMBIGUOUS起因の確認パスも)を**合算して最大2回**(`max_reselect=2`維持)。2回使い切っても(i)(ii)を満たさなければ`status=UNRESOLVED, reason=RESELECT_LIMIT_REACHED`(内訳に`unmet=["REJECTED_SELECTED"|"AMBIGUOUS_NOT_CONFIRMED"]`)。確定ファイル(research_ledger/storyline_b3)は出さない(既存4-3維持)。
**D4. 記録**: `rounds[*]`に`trigger`(`INITIAL`/`RESELECT_REJECTED`/`CONFIRM_AMBIGUOUS`/`RESELECT_REJECTED+CONFIRM_AMBIGUOUS`)、`ambiguous_selected`、`ambiguous_visible_to_b3`(bool)を追加。result.jsonに`reselect_count`(REJECTED起因回数)と`confirm_pass_count`(AMBIGUOUS起因のみの回数)と`b3_calls_after_initial`(合計)を分けて記録し、費用も`_cost_for`のstage_tag(`b3_reselectN`/`b3_confirmN`)で分離できるようにする(§5「再選定・最終B3確認パスの追加費用」)。
**D5. REJECTED再選定検知**: 既存のUNKNOWN_FACT_ID検知・`B3_TECHNICAL_FAILURE_REJECTED_ID_RESELECTED`はそのまま維持。
**D6. Stage 1a補正モード**(`er082_rlct_trial_01_run.py`に`--correct-from <method>`追加、出力method名は`M2c`/`M3c`): 既存`<article>/M2`(`M3`)を一切変更せず、`<article>/M2c`(`M3c`)を新規作成。再利用=`M2/_work/initial_b3.json`(M3cもM2の初回B3を共有、設計4-1維持)と、元methodの`result.json`→`reselect.rounds`に記録済みのverdicts(元method最終round時点の`verdicts`。result.jsonに`final_verdicts`のverdictしか無い場合はverify_recordsの保存先`_work/verify_*.json`からverification_notesを復元。復元できなければSTOPして報告、推測で補わない)。そこから**D1判定→必要ならD2確認パス→新規選定Factのみ検証(capは元methodに従う)→D1→確定/未成立**を実行。result.jsonに`corrected_from`, `reused_initial_b3_sha256`, `reused_verdict_ids`, `pre_correction_selected_fact_ids`, `pre_correction_storyline_sha256`, `cost_correction_only`, `cost_production_equivalent = 元method cost + correction cost`を記録。Budgetのstage_tagは`1a`(1a上限493の残で管理)。有料実行は本委任では行わず、**dry-runのみ**(`--dry-run --correct-from M2 --article inbound_tourism`等)で経路を確認。
**D7. Coffee適合照合**(JPY0、機械): `coffee_prices/M2/result.json`・`M3/result.json`の`reselect.rounds`を読み、最終`sel`を生成したB3呼出(reselect1)時点で選定Factの各verdictが候補Ledgerに見えていたか(=D1(ii))を判定するscript `er082_rlct_trial_01_conform_check.py`を書き、全method(1a 12件)の`conform_d1 = PASS|FAIL|N/A`と理由(どのFactがAMBIGUOUSで未提示か)を`er082_output/rlct_trial_01/_conform_check_1a_01.json`へ出力。Coffee M2/M3がPASSなら「再生成不要」、FAILなら補正対象として報告(有料実行はしない)。inbound M2/M3は想定FAIL(F05)。
**D8. aggregate**: `er082_rlct_trial_01_aggregate.py`が`M2c`/`M3c`を認識し、表では「案2(確認パス後)」として扱い、修正前M2/M3は「案2(修正前・参考)」行として併記。本番換算費用はD6の`cost_production_equivalent`を使う。1bのM2/M3は新設計(確認パス込み)として通常列。
**D9. test追加**(`er082_rlct_trial_01_test_01.py`): test_r1 全VERIFIED→B3追加呼出0・confirm_pass NOT_NEEDED / test_r2 AMBIGUOUSのみ→確認パス1回・noteにAMBIGUOUS ID+notes+制約文を含む・B3が同じFact集合を返せば確定し`ambiguous_visible_to_b3=True` / test_r3 確認パスで新規未検証Factが選ばれ検証でAMBIGUOUS→2回目の確認パス→確定 / test_r4 確認パス2回で未達→UNRESOLVED、確定ファイル無し / test_r5 REJECTED+AMBIGUOUS混在→1回のnoteに両方、合算回数が2上限 / test_r6 `--correct-from`がM2ディレクトリのsha(manifest)を変えず`M2c`に出力・reused_initial_b3_sha256一致 / test_r7 conform_checkが既存1a result.jsonに対して inbound M2/M3=FAIL、M0/M0b/M1=N/A を返す(Coffeeは実測値どおり)。StubClientに確認パス経路(AMBIGUOUS判定・新規Fact選定)を再現するシナリオを追加。既存test_e/e2/f/j/n/q は維持。
**D10. 設計文書**: `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_DESIGN_03.md`(新規、TRIAL_DESIGN_02からの差分のみ。D1〜D9、ユーザー§2原文の逐語引用、1a補正手順、1b手順[methods順: streaming_price→openai_copyright→central_bank_mortgage、M0b含む、`--other-spend-today-jpy`で当日他支出を渡す、1bは別日(2026-10-18 JST以降)]、費用見積の増分[inbound M2c/M3c 各B3 1回≒11円(1a実測B3単価を`raw_usage_log.jsonl`から算出し出典行を記す)+新規Fact検証があれば+α]、Opusレビュー観点案[D1条件の妥当性・上限合算の妥当性・UNRESOLVED時の安全側・1a補正の再利用忠実性・M3cがM2初回B3共有でよいか])。

## 事前指定Read一覧
- `er082_rlct_trial_01_lib.py`:40-80(定数・PLAN)、:498-560(候補Ledger描画・B3 prompt)、:607-700(`build_reselect_note`/`select_then_verify`/`_finalize_sel`)、:825-925(StubClient)
- `er082_rlct_trial_01_run.py`:26-62、:64-175、:177-230(`run_method`/`_finish`/`jobs_from_args`/`main`)
- `er082_rlct_trial_01_aggregate.py`: Grep `M2|M3|METHODS|def ` → 該当関数のみRead
- `er082_rlct_trial_01_test_01.py`:1-60(fixture)、:106-170(test_e/e2/f)、:227-260(test_j/k/l)
- `er082_output/rlct_trial_01/coffee_prices/M2/result.json`:1-80、`.../coffee_prices/M3/result.json`:1-80、`.../inbound_tourism/M2/result.json`:1-80、`.../inbound_tourism/M3/result.json`:1-80(rounds/verdicts構造の確認のみ)
- `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_DESIGN_02.md`:1-80(4-1〜4-9)
- `docs/pm/RESULT_PACKET_RLCT6.md`全文(15行)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `OPEN_ITEMS.md`: Grep `^\| OPEN-408` → その直後の行に新規OPEN-409、OPEN-410を追加。Grep `^\| OPEN-403` → 同行Status末尾に「2026-10-17 委任_07: ユーザー(b)承認で最終B3確認パス追加(TRIAL_DESIGN_03)、harness是正・dry-run完了、有料1a補正・1bはOpus条件A後」を追記。
- `DECISION_LOG.md`: Grep `RLCT|RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01` で末尾エントリ位置を特定 → 本体末尾に下記SSOT追記文のDECISION_LOGエントリを追加。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#106` → 直後に `#107` 行を追加(判断済み区分)。
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-RLCT-R-07|OF-RLCT-R-06` → 各行の後に状態遷移1行追記。
- `docs/pm/REPORT_LEDGER.md`: Grep `RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01` → 最新行の後に委任_07行を追加。
- `docs/pm/ACTIVE_TASK.md`: 冒頭固定ヘッダを委任_07の内容で上書き(旧ヘッダは「## 前タスク群(保持)」へ退避、PM_BRIEF書式: 管理ID/Status/UDR-blocking/UDR-deferred/APPROVED未配線/STOP条件/次アクション/QDC/承認済み指示/未回答報告/報告単位Status)。
- 委任_05の委任文所在確認: Grep `委任_05` in `docs/pm/delegation_log/2026-10-17_MULTI_S3W05_RLCT05_BAPE02_委任.md`(存在確認のみ、RESULT_PACKETに1行)。

## 実行コマンド全文
1. `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_07.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_07.md_check.json`
2. `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 --run-dir er082_output/rlct_trial_01 --out er082_output/rlct_trial_01/_stop_scope_check_07.json`
3. 事前snapshot: `.venv\Scripts\python.exe -c "import er082_rlct_trial_01_lib as l, json; json.dump(l.integrity_snapshot(['coffee_prices','inbound_tourism']), open('er082_output/rlct_trial_01/_integrity_before_07.json','w'), indent=1)"` に加え、`er082_output/rlct_trial_01/coffee_prices`と`inbound_tourism`配下全ファイルのsha256一覧を`er082_output/rlct_trial_01/_stage1a_tree_sha_before_07.json`へ保存(`lib.tree_listing`を使用)。
4. 実装後 dry-run: `.venv\Scripts\python.exe er082_rlct_trial_01_run.py --dry-run --out er082_output/rlct_trial_01/_dryrun_07 --all-articles --method M2,M3`
5. 補正モード dry-run: `.venv\Scripts\python.exe er082_rlct_trial_01_run.py --dry-run --out er082_output/rlct_trial_01/_dryrun_07 --article inbound_tourism --correct-from M2` と `--correct-from M3`(dry-run時は`_dryrun_07/inbound_tourism/M2`を元として読むか、`--correct-source-root er082_output/rlct_trial_01`で実測dirを**読み取り専用**で参照する。実測dirへ書込み禁止)
6. 適合照合: `.venv\Scripts\python.exe er082_rlct_trial_01_conform_check.py --root er082_output/rlct_trial_01 --out er082_output/rlct_trial_01/_conform_check_1a_01.json`
7. test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er082*_test_*.py"`
8. 事後snapshot: 手順3と同じコマンドで`_integrity_after_07.json`/`_stage1a_tree_sha_after_07.json`を出し、`.venv\Scripts\python.exe -c "import json;a=json.load(open('er082_output/rlct_trial_01/_stage1a_tree_sha_before_07.json'));b=json.load(open('er082_output/rlct_trial_01/_stage1a_tree_sha_after_07.json'));print('IDENTICAL' if a==b else 'DIFF')"` → IDENTICAL必須。
9. aggregate dry確認: `.venv\Scripts\python.exe er082_rlct_trial_01_aggregate.py --root er082_output/rlct_trial_01/_dryrun_07 --out er082_output/rlct_trial_01/_dryrun_07/aggregate.md`(引数名は既存に合わせる)
10. secret scan: `.venv\Scripts\python.exe tools/secret_scan.py --staged`(既存scriptの名称・引数は`Glob tools/*secret*`で確認し実値に置換、hits=0必須)
11. Git: `git -C C:\Users\tensh\eigo-radio add <明示ファイル>` → `git commit -m "<下記>"` → `git -C C:\Users\tensh\eigo-radio-crbn pull --ff-only origin main; git -C C:\Users\tensh\eigo-radio-crbn merge --ff-only work/post-merge-01; git -C C:\Users\tensh\eigo-radio-crbn push origin main` → `git -C C:\Users\tensh\eigo-radio merge --ff-only origin/main`(手順は委任_06と同じ。`git status --porcelain`で無関係差分をstageしていないことを確認)。

## SSOT追記文
- DECISION_LOG.md(末尾): 「2026-10-17 FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 設計是正(ユーザー判断#107): Stage 1a評価で、案2(Select-then-Verify)は再選定が起きない記事で検証結果(AMBIGUOUS)が最終B3へ未反映のまま確定する構造が判明(inbound F05断定1件)。ユーザーは選択肢(b)を正式承認: 案2/案1+2に「最終B3確認パス」(選定FactにAMBIGUOUS/REJECTEDがあれば検証結果・理由・使用制約をB3へ返し再評価、新規Factは独立検証、検証済みは再利用、B3追加呼出は再選定と合算で最大2回、未達=未成立)を追加し1bへ進む。既存Family X仕様「AMBIGUOUS断定禁止/REJECTED使用禁止」を守るためのTrial設計是正であり新Production仕様の採用ではない。1a inboundはM2c/M3cとして確認パスのみ追加実行(見込み約JPY22)、Coffeeは適合照合のみ。設計=TRIAL_DESIGN_03.md。原文=docs/pm/delegation_log/2026-10-17_..._DESIGN-FIX-1B_USER.md(sha256 <実値>)。実装=委任_07(JPY0、dry-run)、有料実行はOpus条件Aレビュー後。」
- OPEN_ITEMS.md 新規: 「| OPEN-409 | **FAMILY-X-LEDGER-VERIFIER-REPRODUCIBILITY-COFFEE-F12-01 [OPEN・非Blocking・区分C・改修なし]**(2026-10-17起票、RLCT Stage 1a評価): 現行Production Verifier(上限なし、gpt-6-luna+web_search)の同日再検証(M0p)で、Coffee F12(BLS季節調整ラベル誤り、2026-10-16正式runではREJECTED検出)がVERIFIEDへ昇格。Trial方式と無関係なProduction側の再現性リスク。今回は選定外で実害なし。ユーザー指示(2026-10-17 §6)によりProduction Verifierの改修は行わない。証拠=STAGE_1A_EVAL_01.md、inbound_tourism/coffee_prices M0p result.json。是正要否はTrial完了後のユーザー判断。 | 区分: POST_USER_VALIDATION | 棚卸し: 未実施 |」
- OPEN_ITEMS.md 新規: 「| OPEN-410 | **RLCT-SELECT-THEN-VERIFY-FINAL-B3-CONFIRM-PASS-01 [IN_PROGRESS・Trial専用]**(2026-10-17起票): 案2/案1+2の最終B3確認パス(ユーザー#107承認)。harness是正・dry-run=委任_07。有料1a補正(M2c/M3c)・1b=Opus条件A後。Production未反映・未承認(Trial設計のみ)。 | 区分: POST_USER_VALIDATION | 棚卸し: 未実施 |」
- USER_DECISION_REGISTER_01.md: 「- #107(判断済み 2026-10-17) RLCT Stage 1b前の案2設計: 選択肢(b)最終B3確認パス追加を正式承認。Trial設計是正でありProduction採用ではない。原文=..._DESIGN-FIX-1B_USER.md。」

## Git(明示add対象・コミットメッセージ・trailer)
- add対象: `er082_rlct_trial_01_lib.py`, `er082_rlct_trial_01_run.py`, `er082_rlct_trial_01_aggregate.py`, `er082_rlct_trial_01_test_01.py`, `er082_rlct_trial_01_conform_check.py`, `er082_output/rlct_trial_01/_conform_check_1a_01.json`, `er082_output/rlct_trial_01/_dryrun_07/**/result.json`と`aggregate.md`(dry-run出力のうちresult.json/aggregate.mdのみ。大きい_workは不要), `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_DESIGN_03.md`, `docs/pm/delegation_log/2026-10-17_..._委任_07.md`(+`_check.json`), `docs/pm/delegation_log/2026-10-17_..._DESIGN-FIX-1B_USER.md`, `OPEN_ITEMS.md`, `DECISION_LOG.md`, `docs/pm/USER_DECISION_REGISTER_01.md`, `docs/pm/OPUS_FINDINGS_LEDGER.md`, `docs/pm/REPORT_LEDGER.md`, `docs/pm/ACTIVE_TASK.md`。`CURRENT_SPEC.md`は変更しない(Production仕様に変更なし)。SSOT編集権: あり(OPEN_ITEMS/DECISION_LOG/REPORT_LEDGER)。PM_GOVERNANCE.mdは編集しない。既存の無関係差分(git status先頭のer005/er006等の M ファイル)は絶対にstageしない。
- commit message: `FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_07: 案2/案1+2 最終B3確認パス(ユーザー#107承認(b))のTrial harness是正+Stage 1a補正モード(--correct-from→M2c/M3c)+適合照合script+test r1〜r7+dry-run+TRIAL_DESIGN_03+SSOT(JPY0、有料実行はOpus条件A後)`
- trailer: `Managed-ID: FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_RLCT7.md`(20行目安)に: T-0結果(委任文・ユーザー原文の保存path・wc -m・sha256・check結果)/stop_scope rc/実装差分の要点(関数名:行)/D1〜D9の各実装状況/test結果(件数、全PASS)/dry-run結果(M2/M3 5記事、M2c/M3c inbound、確認パス発火の有無、UNRESOLVED経路の発火)/conform_check結果(12 method、Coffee M2/M3のPASS/FAIL+理由、inbound M2/M3 FAIL理由=F05)/1a実測dir不変(IDENTICAL)/1a補正の費用見積(B3単価出典行+想定回数、1a残=493-212.80)/1b計画の確認(別日・順序・other-spend)/SSOT更新箇所/commit hash・push結果/secret scan hits/(1)既存仕様整合 (2)未承認機能既定値 (3)失敗終了時の最終成果物 (4)撤去・残置/`判定整合:`行/判断候補(A/B/C/D区分)/QDC(見込み・次の一手)。Opus向けに「設計上の自己懸念」を3点以内で添える。

## Fable自己チェック(送信前)
Read一覧行範囲あり/追記位置手順あり/コマンド実値あり/禁止事項・費用(JPY0)あり/並行衝突なし/Opus条件A該当明記/時間・並列化あり/前委任QDC・受入記録あり/費用日次行あり。
