# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_01(記事A「給料が上がると、性格も変わる?」を既存の正式Family X Production経路でResearch→Fact Ledger→B3→Writer→Std/Adv→TTS→Audio QA→Assembly→試聴ページ公開まで完成させる。slug=`paycheck_personality`、run=`run_pp_01`)。
**並行agent 2つ**: (1)記事B `FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_01`(slug `manga_ai_chat_byus`、同じrunner・同じ共有ログ[review_queue/telemetry/attempt_history/pronunciation ledger等 append-only]を同時に使う) (2)`FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01 委任_01`(er087/user_test/family_z_voice_candidates_01/OPEN-430/REGISTER #131)。**共有プロトコル**: SSOT(`OPEN_ITEMS.md`新規行・`docs/pm/REPORT_LEDGER.md`・`docs/pm/ACTIVE_TASK.md`)は編集直前に`git status --porcelain`+末尾再Grep→自分の行だけ追記→即add/commit。`index.lock`は30秒待ち再試行。`git diff --cached --stat`で自分のファイルのみ確認、他agent分が混ざれば`git restore --staged <file>`。他記事のrun dir・page・scriptは触らない。Production共有資源(RUN_LOCK/HR queue等)で競合・待ちが出たら迂回せず待つか記録してFableへ。

## 性質/到達上限Status/禁止事項
- 性質: Production E2E(既存承認済み仕様の再利用)。到達上限=技術完成→`USER_LISTENING_PENDING`(ユーザー試聴PASSは別Status。Fable独立受入判定は完成後にFableが行う)。
- Writer: 現行Production Writer仕様そのまま。**Detective Trial Pattern A/B/Cは不採用・適用禁止**(Prompt/コード変更0)。Prompt探索・モデル変更・追加機構開発・Trial禁止。
- 費用: 本日2026-10-21(JST)既使用JPY73.47(出典 `daily_dev_cost_01.py --date 2026-10-21`実測、RESULT_PACKET_DWA2)+並行Voice Trial(上限¥80)。本記事見積: text 約JPY33〜80(出典: 中東記事 run_mey_02 text 32.514 / E2E-01 text 79.881[E2E_PLAN_02.md §5・§11])+audio 約JPY23〜30(run_mey_02 audio 23.36、HR再試行分含む)=**約JPY56〜110**。承認区分C(ユーザー指示で承認済み、案件見積300円以下、日次内)。T-3 Guardrail=**JPY150**(本記事新規支出合算)。次stage前に「既使用+次stage見積」が150超見込みならそのstageを開始せずSTOP報告。Research再試行は最大2回(初回+2、run_pp_01/02/03)。runnerの`--budget-jpy`はtext 120・audio 70。
- 禁止: 手動Fact挿入・Ledger/B3手編集・`--regenerate-stage storyline_b3`による再抽選・HR/Lock/BLOCK迂回(HR解除は人間のみ)・有料runのkill後再起動(26節。rc≠0で止まったらSTOP報告、再起動はFable判断)・`git add -A`/`-u`/`-f`/stash/amend/rebase/force push・Family A/B/Cコード変更。
- 許可するregeneration(既存機構のみ): 重点品質条件(下記§A)の違反をSonnet CPで検出した場合に限り、`--stage writer --regenerate-stage writer`(+advanced/standard)を**1回だけ**。2回目は不要でSTOP(Fable判断)。TTS/ASRの既存retry cascade・fallback・LR・差分resumeはrunnerの既定どおり。
- Opus独立技術レビューGate(11-3): 非該当(構造変更なし)。
- 時間見込み: text 20〜30分、audio 30〜45分、ページ・SSOT 15分。記事内の並列: Adv/Stdの音声(`--level both`)はrunner既定の順序どおり。
- `TTS_EXECUTION_MODE=STANDARD`。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Read基本。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`全文読込禁止。修正範囲(11-8)=範囲外は受理面・閾値・方式の新設/拡大。
G-1: git出力は`--porcelain`/`--stat`/`--short`で最小化。
F-1: transcript退避不要。
T-0: 委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_委任_01.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_01」を含むindex[同時刻に記事B委任、直前にVoice Trial委任])。`check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行(見出し名不一致FAILは既知偽陽性)。
T-1: `TTS_EXECUTION_MODE=STANDARD`。T-2: TTSあり(Std/Adv)。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-TWO-ARTICLES-PARALLEL-PRODUCTION-E2E_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01(記事A) / FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01(記事B)`の2行、以降一字一句変えない。**記事B agentも同じpathへ保存を試みるので、既に存在しsha256が一致すれば保存をskipし、一致しなければ`_B.md`等を作らずFableへ報告**。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# Family X 新規2記事・並列Production E2E制作

## 1. ユーザー正式決定

以下の2記事をFamily Xで制作する。

**記事A：給料が上がると、性格も変わる？**

- Source：PsyPost（2026-10-20）
- https://www.psypost.org/a-bigger-paycheck-tends-to-come-with-personality-changes-according-to-a-large-scale-analysis-of-psychology-research/
- テーマ：収入の変化と性格特性の関係

**記事B：漫画のキャラクターとAIで会話。物語の楽しみ方が変わる？**

- Source：ITmedia NEWS（2026-10-20）
- https://www.itmedia.co.jp/news/article/2610/20/2000002432/
- テーマ：LINEマンガのAIチャットサービス「byUs」

**2記事を独立したProduction runとして並列制作する。**

既存の正式Family X仕様を使用し、Research → Fact Ledger → B3 → Writer → Standard／Advanced → TTS → Audio QA → Assembly → 試聴ページ公開まで進める。

## 2. 記事Aの重点品質条件

研究結果を「収入増加が性格変化を引き起こした」と断定しない。

元記事では、収入と性格の関係に双方向の関連が示され、効果も小さいと報告されている。

以下を守る。

- 相関・時間的な先行関係・因果関係を区別する。
- 性格変化の方向や大きさを誇張しない。
- 研究対象・手法・限界を一次研究で確認する。
- 「給料が上がると冷たい人間になる」などの過度な一般化を避ける。
- 研究の意外性を生かしながら、読者自身の仕事や生活と結び付ける。

## 3. 記事Bの重点品質条件

発表内容と、実際に確認できたサービスの動作を区別する。

特に以下を確認する。

- 「byUs」と既存の「キャラチャット」を混同しない。
- 2026年10月19日の発表内容と提供状況。
- Official Storyとファンストーリーの違い。
- 原作者が承認した作品を対象とするという条件。
- サービス提供者が公表した利用実績と、独立に確認された事実の区別。

単なるAI機能紹介で終わらせず、**「物語を読む人が、その物語に参加する人になる」**という変化を中心的なAngle候補として検討する。

ただし、このAngleを採用するために、実際には提供されていない機能や利用者の反応を創作しない。

## 4. Writer・Entertainment品質

両記事ともCURRENT_SPECの正式Production Writer仕様を維持する。

- 既存のResearch／Fact Ledger／B3構造を使用する。
- Ledger外の事実・因果関係を創作しない。
- 重要なFactの帰属を保つ。
- エンターテインメント性は高めるが、事実性を犠牲にしない。
- 不自然な比喩、冗長な説明、同内容の反復を避ける。

**直近のDetective改善TrialのPattern A／B／CはすべてProduction不採用。今回のWriterには適用しない。**

## 5. 並列化・QCD

品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費用。

- 2記事のResearch・原稿生成・音声生成を、依存関係と安全条件が許す範囲で並列実行する。
- 同じProduction共有資源を使用する場合は、競合やRUN_LOCKを尊重する。
- 一方の記事の軽微な不具合で、独立したもう一方の進行を止めない。
- 承認済みの品質Gate・retry／fallback／regeneration／resumeを維持する。
- 不要なTrial、Prompt探索、モデル変更、追加機構の開発を行わない。
- 量産単価70円／記事セットを目標とし、記事別に費用を計測する。
- 日次開発予算1,000円（JST）と既存の個別承認枠を遵守する。2記事合計の費用見積を事前確認し、承認枠超過見込み時は超過前にSTOPする。

既存の承認済み仕様内で解決できる不具合は、自律的に原因究明・修正・検証する。

## 6. 完成条件

記事A／Bそれぞれについて以下を満たす。

1. 原典・一次情報と重要Factの確認。
2. Fact Ledger／B3／Writerの整合。
3. Standard／Advancedの原稿完成。
4. 現行Production TTS・Audio QA・Style Gate・必須Validator PASS。
5. Standardの承認済み6%減速の確認。
6. 完成音声・全文スクリプト・Key Phrasesを掲載した試聴ページ公開。
7. 正式runtime evidence、SSOT／Git反映。
8. Fable独立受入判定。

**Production技術完成とユーザー試聴PASSは区別する。**

両記事の完成後は `USER_LISTENING_PENDING` とし、ユーザーの試聴結果を待つ。

## 7. 報告形式

2記事を横並びで、以下を簡潔に報告する。

| 報告項目 | 記事A：収入と性格 | 記事B：漫画AI |
|---|---|---|
| 完成状態 | | |
| 試聴URL | | |
| 重点Fact品質 | | |
| Standard／Advanced音声QA | | |
| 実費・量産単価 | | |
| 所要時間 | | |
| Fable受入判定 | | |
| 未解決事項 | | |

ユーザー判断が必要な重大な問題が生じた場合のみ、該当記事・理由・推奨対応を明示する。

**目的は、既存の承認済みFamily X Production経路を再利用して、2記事を高品質・最短・低原価で完成させること。**
--- 原文ここまで ---

## §A 本記事(記事A)の重点品質条件 → CP化(生成前に`docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/E2E_PLAN_01.md` §0へ固定、以後変更しない)
- CP-A1(因果断定なし): Std/Adv本文・In One Line・Key Phrases・Std日本語Supportに「収入増加が性格を変えた/引き起こした」の断定(英: caused/makes you/turns you into 等、日: 〜させる/〜になる[断定])が無い。相関/先行関係/因果を区別した表現(associated with / tends to come with / followed by 等)になっている。
- CP-A2(双方向・効果の小ささ): Ledgerに「双方向の関連」「効果は小さい」のFactが登録され(Researcherが一次研究から取れた場合)、B3採用・本文に反映されているか。反映されていない場合は「反映なし」と記録(強制挿入禁止)。
- CP-A3(一次研究の確認): Researcherが一次研究(PsyPost記事が紹介する元論文: 掲載誌・著者・研究対象[サンプル規模・国]・手法[メタ分析/縦断]・限界)をLedgerに帰属付きで登録したか。PsyPostのみで一次研究未到達なら、その事実を記録(Research再試行の判断材料にするが、Prompt変更は禁止)。
- CP-A4(過度な一般化なし): 「給料が上がると冷たい人間になる」型の一般化・性格変化の方向/大きさの誇張が無い。
- CP-A5(読者接続): 研究の意外性+読者の仕事・生活との結び付けがある(観測記録。合否はFable)。
- CP-A6(Ledger外事実・帰属): 本文の数値・固有名詞・因果はLedger内かつ帰属保持。RF候補の件数・内容を記録(合否はFable)。
- Research `--theme`(日本語で、Research用topic文字列。事実の創作を誘導しない記述): 「PsyPost(2026-10-20)が報じた、収入の変化と性格特性(ビッグファイブ等)の関係を扱った大規模分析(心理学研究の統合分析)。一次研究の掲載誌・著者・研究対象・手法・効果の大きさ・双方向の関連・限界を確認する。」 `--source-note`にユーザー提示URLを記録(Research promptには使われない仕様)。
- Research再試行の条件(§0に固定): 一次研究の基本Fact(掲載誌または著者、研究対象/手法、効果の大きさの性質)がLedgerに無い、またはB3採用Factが一次研究由来を含まない場合に限り、同一条件で再試行(最大2回)。語数・文体理由の再試行禁止。

## 事前指定Read/Grep一覧
- `docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02/E2E_PLAN_02.md`(直近Production E2Eの手順・記録様式・§5費用・§10音声/ページ/evidence手順、全文可・約100行)と`docs/pm/delegation_log/2026-10-21_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_委任_04.md`(音声〜試聴ページ公開の実行コマンドと検証手順)。
- runner: `er019_family_x_entertainment_production_runner_01.py --help`/`er019_family_x_audio_production_runner_01.py --help`で引数実在確認(E2E_PLAN_02 §1と同じ)。
- 試聴ページ: `er019_mey_page_02.py`(`--run-dir --audio-dir --out`、記事固有文言8箇所)を`er019_pp_page_01.py`へ複製し記事タイトル・slug・管理IDのみ差し替え(UI変更なし)。再生検証は`er019_mey_play_verify_02.py`を`er019_pp_play_verify_01.py`へ複製(URLのみ差し替え)。
- `tools/stop_scope_check_01.py --managed-id --run-dir --out`(STOP時のscope確認、MEYで使用)。
- Std 6%減速の確認方法: Family Xの音声runner/assembleでStd(a2)に減速処理があるかGrep(`slow|tempo|atempo|0.94|1.06|SLOWDOWN`)。あれば実測比(Std尺/Adv尺 or 減速前後)をevidenceから記録。**無ければ「Family X Production経路にStd減速配線なし(Family Z側の仕様)」と事実を記録し、追加しない**(仕様変更禁止)。
- Grep: `OPEN_ITEMS.md`末尾(新規行番号はOPEN-430がVoice Trialで使われる可能性あり→実際の末尾を再Grepして次番号)、`docs/pm/REPORT_LEDGER.md`末尾。

## 実行手順
S0. `daily_dev_cost_01.py --date 2026-10-21`、`git status --porcelain`(件数のみ)、runner `--help`、出力dir `er019_output/paycheck_personality/`非存在確認。T-0・ユーザー原文保存。E2E_PLAN_01.md §0(CP固定)+§1(開始条件)をcommit(push)してから有料run開始。
S1. text: `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er019_family_x_entertainment_production_runner_01.py --theme "<§Aのtheme>" --slug paycheck_personality --out-dir er019_output/paycheck_personality/run_pp_01 --source-note "PsyPost 2026-10-20 https://www.psypost.org/a-bigger-paycheck-tends-to-come-with-personality-changes-according-to-a-large-scale-analysis-of-psychology-research/" --run-label FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 --budget-jpy 120 --stage all`(console→run dir直下`console_text_01.txt`)。`--out-dir`の正確な形はMEY 委任_01/E2E_PLAN_02の実行例に合わせる(run dirが`er019_output/<slug>/<run>`になること)。
S2. text CP(E2E_PLAN_01 §2/§3): Research facts数・web_search回数・model/Ledger VERIFIED/AMBIGUOUS/REJECTED/B3 selected_fact_ids+選定理由/CP-A1〜A6/RF候補/IOL spec_ok/structure/retry/記号Validator/HR。一次研究Fact未到達ならRun 2(run_pp_02)。CP-A1/A4違反はregenerate writer 1回(上記)。
S3. audio: `er019_family_x_audio_production_runner_01.py --slug paycheck_personality --run run_pp_01 --level both --stage all --budget-jpy 70`(MEY 委任_04と同じ形。backend既定speech_metadata_flash_lite、profile既定)。HR/Lock/BLOCK/STOPPEDが出たら迂回せず、`stop_scope_check_01.py`→状況・原因観測・コードreadによる差分resume見積をE2E_PLAN §にまとめてSTOP報告(Fable判断)。
S4. 完成確認: Adv/Std assemble OK、Audio Validation Gate/style_profile_gate/key_phrase_source_gate/AUW結果、Std減速確認(上記)、尺(秒)、LR発火有無、Human Review件数。
S5. ページ: `er019_pp_page_01.py --run-dir ... --audio-dir ... --out user_test/paycheck_personality_e2e_01`(完成音声Std/Adv・全文スクリプト・Key Phrases掲載)。commit/push(`git push origin HEAD:main`)→Pages反映待ち(最大10分)→`er019_pp_play_verify_01.py`で再生evidence(`docs/research/.../pages_play_evidence_01.json`)。URL=`https://shimomura055.github.io/eigo-radio/user_test/paycheck_personality_e2e_01/index.html`。
S6. 費用(15節5区分+15-8の1生成セット総原価、stage別、出典=cost.json/raw_usage_log/`daily_dev_cost_01.py`)、所要時間(JST開始/終了)、runtime evidence一覧(path)をE2E_PLAN §5〜§7へ。
S7. SSOT(共有プロトコル): `OPEN_ITEMS.md`新規行1件(Status `PRODUCTION_TECH_COMPLETE_USER_LISTENING_PENDING` または STOP状態の事実)、`docs/pm/REPORT_LEDGER.md` 1行、`docs/pm/ACTIVE_TASK.md`先頭追記(固定ヘッダ)。CURRENT_SPEC/DECISION_LOG/REGISTERは変更しない(新仕様・新決定なし。ユーザー決定の原文は委任logに保存済み)。
S8. secret scan(`tools/secret_scan_01.py --staged` hits=0)→commit→push→`git log origin/main -1 --oneline`。

## Git
- 明示add: delegation_log(委任_01+_check.json、USER原文[自分が保存した場合])、`docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/*`、`er019_output/paycheck_personality/run_pp_0*/`(text成果物・audit・cost。wav/mp3はMEYでの扱いに合わせる)、audio run dir(`er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01/`、MEYと同じ範囲)、`er019_pp_page_01.py`、`er019_pp_play_verify_01.py`、`user_test/paycheck_personality_e2e_01/`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`。共有ログ(review_queue/telemetry/attempt_history等の既存M)はMEYでの扱いに合わせ、他記事agentの変更を巻き込まない(`git add <path>`はディレクトリ単位でも自記事のものだけ)。
- Commit(段階ごと): `FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_01: T-0+ユーザー原文+CP事前固定(生成前)` / `...: text完了(Research/Ledger/B3/Writer/Adv/Std、実費JPYxx)` / `...: 音声完成+試聴ページ公開+再生evidence+OPEN-4xx`。
- Push: `git push origin HEAD:main`(ローカルbranchは`work/post-merge-01`)。

## 報告(docs/pm/RESULT_PACKET_FXPP1.md 上書き。ユーザー§7の表の記事A列を埋める形+詳細)
1. 完成状態(stage別rc・Status)/2. 試聴URL+再生evidence/3. 重点Fact品質(CP-A1〜A6の観測、B3採用Fact ID・選定理由引用、RF候補、一次研究の到達状況、Research試行回数、regenerate使用有無)/4. Std/Adv音声QA(Gate結果・尺・LR・HR・Std減速の有無と実測)/5. 実費(stage別・5区分・1生成セット総原価、対70円目標)・当日累計/6. 所要時間/7. 未解決事項・判断候補(Sonnetは「判断候補」表記)/8. T-0 check・原文sha256・commit hash・raw URL一覧。末尾に4行判定(既存仕様整合/未承認機能のProduction入り/失敗終了時の成果物/撤去・残置)。STOP時は到達stage・原因観測・既使用額・残作業・差分resume手順を必ず含める。