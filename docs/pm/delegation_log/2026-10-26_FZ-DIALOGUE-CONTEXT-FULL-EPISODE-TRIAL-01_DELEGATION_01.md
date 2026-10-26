## 管理ID
FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01(2026-10-26 JST、Phase 0: 原文保存・対象棚卸(2作品×レベル×セリフ数・既存音声の所在)・費用見積・設計(DEV隔離の全編組立)・Opus条件Aレビュー依頼文・感情情報LLM(Phase 1a)まで。TTS生成はOpusレビュー後の委任_02)。**並行**: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_01(Lane A: `er121_*`+共有SSOT所有)・委任_02(Lane B: `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/`所有)が稼働中。**本委任は共有SSOT(`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)を編集しない**(追記文案をRESULT_PACKETへ)。本委任の所有=`docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/`(新規)、`er118_fz_full_episode_trial_01.py`(新規DEV専用、+test)、`er118_output/fz_full_episode_trial_01/`、`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_*`、`docs/pm/RESULT_PACKET_FZFE1.md`。既存`er118_fz_dialogue_context_tts_trial_01.py`は読取・import再利用のみ(編集する場合は後方互換を保ちRound 1/2 test 54件PASS維持)。gitは`git commit --only <paths>`(index.lock競合時30秒待ち再試行、3回失敗なら未commitで報告)。

## 性質/到達上限Status/禁止事項
- 性質: Trial(DEV専用経路)。到達上限: VALIDATED(限定)/REJECTED/USER_DECISION_REQUIRED(Fable・ユーザー判定)。Production採用・Production公開物の上書き・既存音声差替え禁止。
- 禁止: 正式ProductionのPrompt・TTS設定・音声生成方式・Gate・閾値・reuse keyの変更、新flagの追加、Round 1/2の文脈・感情付与方式(CONTEXT区画書式・EMOTION_DEVELOPER rule 1〜10・leakage検査・ASR検査)の変更、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用上限(本委任): 上限¥5(Guardrail、感情情報LLMのみ。作品×レベル分、各1 call)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。TTS生成は本委任で禁止。
- Opus独立技術レビューGate: **条件A該当**(DEV隔離での全編組立=新しい処理フロー)。本委任で依頼文を作成し、実装(組立コード)の前にFableがOpusへ回す。感情情報LLM(Round 1/2と同一)と棚卸・見積は先行可。
- 時間見込み: 全体60〜90分(棚卸20、見積10、設計+依頼文20、感情LLM+候補一覧15、Git10)。並列化: Y 2レーンと並行(所有分離)。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約79(出典: RESULT_PACKET_FZDC5)/残JPY約921/本委任見積JPY≤2(感情LLM 2〜4 call×約0.1円)/全体見積は本委任で算出(目安: セリフ総数×1 take×約0.53円+ASR+再生成予備。300円以下ならFable自律、超えるなら事前承認)/改善見込み中/承認区分: C:承認済みscope内(ユーザー2026-10-26指示)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

## ユーザー指示(原文)
次の原文を**一字も変えず** `docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_USER.md` に保存する(先頭に「ユーザー指示原文(2026-10-26、Fable経由で逐語保存)」の1行を付けてよい):

```
# Family Z｜文脈・感情付きTTS 全編通し試聴Trial

## 1. 目的・承認範囲

これまでの『賢者の贈り物』『開いた窓』『猿の手』の比較Trialでは、一部のセリフで感情表現の改善が確認された一方、効果のばらつきも大きかった。

ユーザー評価：
「場面によって良くなっている感じはある。ただ、ばらつきも大きい」

次の段階として、**実際の作品全体を通して聴いた場合に、文脈・感情付きTTSが品質向上につながるか**を検証する。

対象は以下の2作品。

- 『猿の手』
- 『走れメロス』

**Status：追加Trial承認済み。到達可能StatusはVALIDATED（限定）／REJECTED／USER_DECISION_REQUIRED。Production採用は未承認。**

正式ProductionのPrompt・TTS設定・音声生成方式は変更しない。

## 2. 音声生成条件

### ① セリフ部分

両作品とも、対象となるセリフ音声をすべて文脈・感情付き方式で新規生成する。

- 『猿の手』：前回A/B Trialで生成したセリフ音声を流用しない。
- 『走れメロス』：セリフ音声を全件新規生成する。
- 既存の確定本文・Voice・承認済み速度設定を維持する。
- 前後の会話・地の文・話者・場面・感情を参照してStyle指示を生成する。
- 文脈情報を実際の発話本文に混入させない。
- セリフごとの感情表現だけでなく、同じ登場人物の演技の一貫性も重視する。

前回Trialの文脈・感情付与方式を基本とし、比較条件を勝手に変更しないこと。

### ② セリフ以外

地の文・その他の音声は、既存の品質合格済み音声を再利用してよい。

不要な再生成は行わない。

既存音声の再利用により比較条件が変わる場合は、その範囲を明示すること。

### ③ 対象レベル

両作品の既存完成版で利用可能なStandard／Advancedを対象とする。

既存音声・本文・Voice設定を確認し、現在存在するレベル構成に従う。未制作レベルを追加する必要はない。

## 3. 完成物

作品ごとに、新規生成したセリフ音声を既存の地の文音声と組み合わせ、**最初から最後まで通して聴けるTrial版**を作成する。

試聴ページには以下を用意する。

1. 文脈・感情付きTrial版の通し再生。
2. 既存Production版の通し再生（比較用）。
3. セリフごとの個別再生・比較。
4. セリフ本文と前後の文脈。
5. Standard／Advancedの区別（該当する場合）。

ユーザーが作品全体の自然さ、感情の連続性、地の文とセリフのつながりを比較できる構成にする。

Production公開物をTrial版で上書きしないこと。

## 4. 品質検証

以下を重点的に確認する。

**A. 表現品質**
- セリフの感情が場面に合っているか。
- 感情表現が過剰になっていないか。
- 前後のセリフと演技がつながっているか。
- 地の文からセリフへの切り替わりが自然か。
- 通しで聴いたとき、現行版より物語への没入感が増すか。

**B. 安定性**
- 同一人物の演技に大きなばらつきがないか。
- 感情の強いセリフと弱いセリフで効果がどう異なるか。
- 文脈指示によって不自然な速度変化・長いポーズが発生していないか。

**C. 基本品質**
- ASR逐語一致
- 読み飛ばし・言い直し・不自然な反復
- 文脈情報の音声混入
- 音声結合・ポーズ・音量の不整合
- 既存の必須音声品質Gate

既存の承認済み品質基準を変更しないこと。

## 5. 量産単価・速度への影響

今回の重要な検証項目とする。

次の数値を記録する。

- 文脈・感情情報の生成費用
- 追加Style指示によるTTS費用増分
- セリフの初回生成成功率
- 品質NG件数・再生成回数
- 再生成を含むセリフTTS総費用
- 従来方式に対する1記事セット当たりの推定増加額
- 完成までの所要時間への影響

今回のTrialでは地の文を再利用するため、実際のTrial支出と、通常量産時の想定原価を区別すること。

**量産単価70円／記事セットを維持できるか、超過するなら何円程度か**を評価する。

単に「追加Style費用は0.1〜0.2円」とするのではなく、再生成増加による費用・時間も評価する。

## 6. 実行・予算管理

- 既存音声・既存本文・過去Trialデータを最大限再利用する。
- セリフ音声だけを新規生成する。
- 独立した準備・検証作業は並列化する。
- 不要な待機や日付分割を避ける。
- API呼び出し回数と費用を事前見積もりし、予算内で最も効率的に実施する。
- 開発費は既存の承認済み日次予算・個別予算枠を遵守する。
- 今回の2作品全セリフの生成・検証に必要な費用が承認済み枠を超える場合は、超過実行せず報告する。
- 品質・安全のSTOP条件を維持する。

## 7. 完了条件・報告

以下をまとめて報告すること。

1. 『猿の手』Trial版の通し試聴URL。
2. 『走れメロス』Trial版の通し試聴URL。
3. 既存Production版との比較方法。
4. セリフごとの感情表現・安定性の評価。
5. ASR・音声品質検査結果。
6. 実費・再生成回数・想定量産単価・制作時間への影響。
7. Fable独立評価。
8. SSOT・Git反映状況と残課題。

Trialの機械評価とユーザーの試聴評価を区別すること。

ユーザー試聴前に、正式Production採用や既存音声の差し替えを行わないこと。

**今回の最終判断は、ユーザーが2作品を通して聴いた後に行う。**

その時点で効果が十分ならProduction採用を検討し、改善が不安定なら現行方式維持または別方式への転換を検討する。
```

## KPI provenance欄
本委任=棚卸(既存Production記録のreuse読取)+感情LLM(fresh)。TTS/ASR指標は委任_02で fresh。E2E自己確認: No(Trial)。

## Opus台帳更新
該当なし(新規依頼文を作成するのみ)。

## 事前指定Read一覧
- Round 1/2の方式正本: `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/{DESIGN_01,DESIGN_02,PREREGISTERED_CRITERIA_02,OPUS_REVIEW_01,EVAL_02,TRIAL_RESULT_02,BUDGET_LOG_02}.md`(§見出しをGrepし必要節のみ)、`er118_fz_dialogue_context_tts_trial_01.py`: Grep `def |WORKS|ALLOWED_NAMES|generate_arm|style_for_arm|build_context_block|leakage_check|extract_context|redirect_production_sinks|style_prefix_override` → 再利用する関数の署名。
- 対象作品の既存完成版: 『猿の手』『走れメロス』のZ Production run(Glob `er026_output/**/monkeys_paw*`・`er026_output/**/melos*`、`er0*_output/**/*melos*`、`user_test/*monkey*`・`user_test/*melos*`、OPEN_ITEMS Grep `猿の手|Monkey|メロス|Melos` → 該当行の証跡path)。各レベル(Std=a2?/Adv=b1b)の本文(segment_plan)・dialogue clip一覧(話者・Voice・語数・attempt・ASR状態)・narration clipの所在・組立記録(無音長・gain)・公開mp3の所在。Melosは「最終runが別配置」(SELECTION_02.mdの不選定理由)のため、公開ページ(`user_test/`)から逆引きして正本runを確定。
- Z組立の正本: `er026_*`/`er063_*`の組立関数(Grep `def assemble|concat|silence|0\.2|0\.5|gain|dialogue` → 行番号のみ)。Production sink隔離: `er113` `redirect_production_sinks`。
- `docs/pm/RESULT_PACKET_FZDC5.md`(全文)。

## 事前指定Grep一覧+追記位置・更新位置の手順
1. 原文保存(最初に)。
2. 棚卸(`INVENTORY_01.md`): 作品×レベルごとに、存在するレベル、dialogue clip数・話者別件数・語数分布、narration clip数、正本run path、公開ページURL、既存clipのASR状態(PASS/WARNING)、Voice割当、速度設定(Std dialogue速度仕様v2等の承認値)、Round 2で使った猿の手8 clip(流用禁止の対象)を表に。
3. 費用・時間見積(`BUDGET_PLAN_01.md`): セリフ総数×1 take×TTS実測単価(Round 2: 26.20円/50 call=0.524円/call)+ASR(OpenAI+Azure、Round 2実測1.60円/50clip)+感情LLM(作品×レベル各1 call、Round 2実測約0.1円)+再生成予備(Production実績の初回成功率から。猿の手/メロスの既存run attempt分布を使う)。合計がFable自律枠(案件300円以下)に収まるか、収まらない場合の削減案(例: レベルを1つに絞る)を提示。通常量産時の想定原価(地の文を含む1記事セット)への増分見積の算式も先に定義(§5の7項目の測定方法と、実Trial支出との区別)。
4. 設計(`DESIGN_01.md`): (a)セリフ全件のctx生成(Round 2と同じ`generate_voice_body_wide_margin(style_prefix_override)`直接呼出・DEV sink・Trial専用key。1 take/clip、NG時はProductionと同じretry上限で再生成し回数を記録。速度加工は既存承認値をR2と同じ方法で適用)、(b)同一人物の一貫性=方式変更なし(CONTEXTに話者名は既に含む。新規指示の追加はしない。評価項目として話者別の指標ばらつきを測る)、(c)**DEV隔離の全編組立**: Production組立関数をimportして入力clipだけ差し替え、出力は`er118_output/fz_full_episode_trial_01/<work>/<level>/`へ。Production dir・Master Store・manifest・reuse telemetryへ一切書かないことをどう保証するか(sink redirect+書込前assert+test)。既存Production版の通し音声は公開mp3を参照(再生成しない)。比較条件の差(地の文は同一、セリフのみ差替、無音・gainは同一規則)を明記。(d)試聴ページ: 通し再生×2(Trial/Production)、セリフ個別A/B、本文+前後文脈、レベル区別、noindex・PAGE_NOTICE、`user_test/fz_full_episode_trial_01/`。(e)評価(`PREREGISTERED_CRITERIA_01.md`): 機械指標は事前登録02の指標を流用(話速・F0幅・RMS・duration)し、新規に「話者内ばらつき(同一話者のctx clip間の指標CV)」「不自然な速度変化・長ポーズ(clip内無音>700ms件数、Round 2の無音検出閾値)」「地の文→セリフ境界のRMS段差」を**観測前に**定義。Status写像: C(基本品質)に1件でも不成立(leakage>0、ASR不一致で再生成上限到達等)→REJECTED候補、Cが全成立→USER_LISTENING_PENDING(最終はユーザー試聴)。A/Bは人手評価項目として列挙(機械で代替しない)。
5. Opus依頼文(`OPUS_REVIEW_REQUEST_01.md`): 論点を絞る=①DEV隔離の全編組立でProduction汚染が起きない設計か ②比較条件の同一性(地の文再利用・無音/gain規則) ③費用会計(実Trial支出 vs 量産想定原価の区別・再生成の扱い) ④事前登録指標の妥当性 ⑤既存er118との責務分離。
6. Phase 1a(有料、≤5円): `PHASE1_GO.json`(cap_jpy=5、scope=Phase 1a)を作成し、作品×レベルごとに感情情報LLM(Round 2と同一EMOTION_DEVELOPER・schema・gpt-6-luna、全dialogue clipを対象、1 call/作品レベル。clip数が多くschema上限に当たるなら分割し回数を記録)を実行、`EMOTION_CANDIDATES_01.md`(Fableレビュー用。Round 2と同形式: 英文・前後文脈・LLM出力・根拠引用・状態)を生成。決定論検査(逐語一致・固有名詞・強度語)の結果件数。
7. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_01.md`(Nは621前後、`--index -1`不可、「FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01」を含むもの)。

## 実行コマンド全文
- `py docs/pm/tools/daily_dev_cost_01.py`
- `py tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 --run-dir er118_output/fz_full_episode_trial_01 --out er118_output/fz_full_episode_trial_01/stop_check_委任_01.json`
- 感情LLM: 新script `er118_fz_full_episode_trial_01.py` に `llm --work <monkeys_paw|melos> --level <a2|b1b>` を実装(既存`er118_fz_dialogue_context_tts_trial_01.py`のEMOTION_DEVELOPER・検査関数をimport)し `$env:PYTHONUTF8=1; .venv\Scripts\python.exe er118_fz_full_episode_trial_01.py llm --work monkeys_paw --level b1b` 等を存在するレベル分実行(`PHASE1_GO.json`無しで起動拒否、`gen`/`assemble`は未実装または拒否のまま)。
- test: `$env:PYTHONPATH="netblock_harness_01"; .venv\Scripts\python.exe -m pytest er118_fz_full_episode_trial_01_test_01.py er118_fz_dialogue_context_tts_trial_01_test_01.py -q`(接続試行0、Round 1/2 test 54件PASS維持)
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_01.md --json-out docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_01.md_check.json`
- secret grep: `git grep -n -I -E "(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|BEGIN (RSA|OPENSSH) PRIVATE KEY)" -- docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 er118_fz_full_episode_trial_01.py er118_fz_full_episode_trial_01_test_01.py docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_USER.md`

## SSOT追記文(本委任は編集しない。文案のみRESULT_PACKETへ)
- OPEN_ITEMS新規行案: 「| OPEN-<次番号> | FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 [種別=Trial、Status=PHASE0_DONE_AWAITING_OPUS_A、分類=修正へ進む(ユーザー指示済みTrial)] ユーザー指示(原文=…_USER.md、Round 1/2評価『場面によって良くなっている感じはある。ただ、ばらつきも大きい』)による全編通しTrial(猿の手・走れメロス、セリフ全件をctx方式で新規生成、地の文は既存再利用、DEV隔離組立、Production上書きなし)。見積<x>円。… |」
- OPEN-516行末追記案: 「ユーザー試聴評価(2026-10-26)=『場面によって良くなっている感じはある。ただ、ばらつきも大きい』→次段階=全編通しTrial(OPEN-<新>)。Status=VALIDATED(限定・部分的効果)ではなくUSER_EVALUATED_PARTIAL(Fable判定は次Trial後)。」

## Git(明示add対象・コミットメッセージ・trailer)
- add対象: `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/{INVENTORY_01,BUDGET_PLAN_01,DESIGN_01,PREREGISTERED_CRITERIA_01,OPUS_REVIEW_REQUEST_01,EMOTION_CANDIDATES_01,BUDGET_LOG_01}.md`、`er118_fz_full_episode_trial_01.py`、`er118_fz_full_episode_trial_01_test_01.py`、`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_{USER,DELEGATION_01}.md`(+_check.json)。PHASE1_GO/raw_usage_log/wav/RESULT_PACKET不追跡。
- メッセージ案: 「FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01: 全編通しTrial Phase 0(棚卸・見積・DEV隔離組立の設計・Opus条件A依頼・感情情報LLM、TTS 0、実費<x>円)」
- `git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。SSOT編集権: なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FZFE1.md`。「現在の状態/何をやったか/何が分かったか/何が残ったか/判断候補/補足」+RESULT_PACKET 4行+判定整合行。必ず含める: 棚卸表(作品×レベル×セリフ数・話者・既存ASR状態・正本run・公開URL)、費用見積(call数×単価、再生成予備の根拠、合計、300円枠内か)、設計の要点(隔離保証・比較条件差分)、事前登録指標、Opus依頼文path、感情候補件数(ACCEPTED/NO_EXPLICIT_CUE/DISCARDED)とレビュー用一覧path、本委任実費(cost log実測)・日次累計、test結果、委任_02(Opus反映→gen→assemble→page→評価)の実行案と所要見込み、commit/push・raw URL、check結果。