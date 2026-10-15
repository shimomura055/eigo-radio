# U5_COST_MANAGEMENT_DESIGN_01: 量産費(70円/記事セット)・日次開発費(原則1,000円/日・JST)の管理設計(Phase 1。提案のみ、未適用)
管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day3 Phase1 委任_E / 2026-10-15 / Status上限: DAY3_PHASE1_DESIGN_COMPLETE
性質: 設計文書。規則・Agent定義・SSOT・Production・script無変更、JPY0(API呼出0。§1の数値は既存ログのread-only集計で得た観測値)。表記: [確認]=本委任で一次ファイルを読んだ/実行した、[推定]、[未確認]。
前提: ユーザー正式判断U5(2026-10-15、原文は`docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3E.md`「ユーザー指示(原文)」U5節)。Day2では非ブロッキング・任意O3だったが、**必須(新単位W9)**に変更された。重要点は『費用を集計するだけでなく、Fableの再計画・モデル選定・Trial設計の判断に費用情報を実際に使わせること』。

## 0. 結論(要約)
1. **重要な事実の訂正**: 『70円/記事セット』も『原則1,000円/日』も、`PM_GOVERNANCE.md`・`PM_BRIEF.md`・`CLAUDE.md`・`CURRENT_SPEC.md`には**定義がない**([確認] Grep 0件)。70円はDECISION_LOG L21038にユーザー指示の一節として登場するのみ。1,000円/日はDay1委任文(`docs/pm/delegation_log/2026-10-14_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_委任_01A.md` L6)で『正式合意済み基本方針』として記述されたが、SSOT化されていない。U5の『既存§7-6の運用』『原則1,000円/日の既存運用』は、**運用実態としては存在するが成文規定はない**。→ 本設計は両者を**成文化**(7-9・15-9の新設)する形になる。これは既存規則の変更ではなく、**ユーザー原文を正本とする新規記録**(DECISION_LOG追記とセット)。
2. **70円/記事セット**: 分母=§15-8『Production 1生成セット』(Family別の正式1生成セット。共通Research/Ledgerは配賦せずセットに全額計上)。含む=記事生成LLM(Research/Ledger/Writer/Fact Check/Support/Key Phrase/canonicalization/gloss再整合)・TTS・ASR検証・retry/fallback/Local Rewrite・Human Review由来の再生成API。含まない=開発Trial費・Trial特有費(15-3)・Claude Code usage(9-10)・人件費。TTSは**Production想定の実行経路(Batch換算、15-5の区分5)で判定**しStandard同期(区分4)を併記。70円は**目標**(Hard gateではない)。新機能・モデル変更・retry追加時は『量産単価影響行』(+JPY/セット)を必須にし、超過見込みなら改善策・代替案・品質影響を検討する。
3. **日次1,000円(JST)**: ソフト上限。**自動停止ルールは新設しない**(7-6維持)。委任前にFableが『当日既使用/残/見積/改善見込み』を確認。1,000円を超える見込み=**実行前にユーザー承認**。JPY100以下のTrialは従来どおりFable判断(7-7)で、**残予算内なら都度ユーザーに回さない**。
4. **既存機構で足りるか**: 足りない。ログは run単位(`raw_usage_log.jsonl` 658ファイル、`cost_log.jsonl` 58ファイル)で日次横断集計がなく、REPORT_LEDGERの費用欄は報告日基準で遅れる。[観測] 2026-10-14: ログ集計JPY1.84(azure STT 26件は単価未登録扱い)に対しREPORT_LEDGER合計JPY7.64、2026-10-15: ログ集計JPY4.07に対しLEDGER合計JPY7.04 → **どちらか片方では過小**になる。→ **最小補強=read-only集計script 1本**(`docs/pm/tools/daily_dev_cost_01.py`、API 0)を推奨。ただし1日の実額は現状数円〜数百円なので、**当日累計500円超または見積100円超のときだけ実行**する運用とし、通常日はREPORT_LEDGER+ACTIVE_TASK `QDC:`行で足りる。
5. **競合・USER_DECISION_REQUIRED候補**: 既存定義の変更を要する競合は**0件**。ただし**ユーザー確認を推奨する具体化2点**(U5-Q1: TTSをBatch換算で判定するか/U5-Q2: 1,000円/日の成文化と『超過見込み=実行前承認』の明記)を§6に記す(どちらも『既存維持+具体化』で、Fable判断で進めることも可能)。

## 1. 既存機構の棚卸し(事実)
### 1-1. 量産費の定義と集計経路
| 項目 | 所在(ファイル:行) | 内容 [確認] |
|---|---|---|
| 1記事あたり総コスト報告 | `PM_GOVERNANCE.md` §15-1 L2777 | 『単位はB1(B1B等)+A2を合わせた1記事一式』 |
| 内訳 | 同 15-2 L2782 | Research/Ledger/Writer/Fact Check/Support/Key Phrase/TTS/ASR/retry/regeneration。粒度が取れない費目は『取得不可(理由)』を明記 |
| Trial特有費の分離 | 同 15-3 L2789、15-5 区分2 | 通常運用では発生しない費用は内数で分離 |
| TTS Standard/Batchの分離 | 同 15-4 L2794、15-5 区分4・5 L2803 | 区分4=Standard同期、区分5=Batch量産換算。`pricing_snapshot.json`の該当tier参照 |
| Production 1生成セット総原価 | 同 15-8 L2855 | Family別標準表(News/Trend/Discovery=共通Research/Ledger+A2+B1、Voices=正式1生成セット)。**50:50配賦禁止**。『Production 1生成セット総原価を主指標』 |
| 開発費/量産単価の別軸 | 同 7-4 L676 | 『Trial/開発=速度優先でStandard同期、量産=コスト優先でBatch』。『Development cost(Trial・開発・検証)とProduction unit cost(量産1記事あたり原価)は別軸』 |
| Claude Code usage | 同 9-10 L1448 | 記事生成API tokenと別項目。週間利用枠%で報告 |
| ログ記録 | `er005_cost_logger.py` L334 `install()` | SDK monkeypatchで1 API call=1 JSONL行。timestampは**UTC**(L83 `datetime.now(timezone.utc)`)。JPY列なし |
| 費用ログの所在 | リポジトリ内 `raw_usage_log.jsonl` **658**ファイル/`cost_log*.jsonl` **58**ファイル [確認: `find`] | run dir単位。管理ID・Trial/Production目的のタグなし(DAY1_D §6) |
| 単価表 | `er005_output/cost_baseline_01/pricing_snapshot.json` | モデル/meter別USD単価。為替は各scriptが`USD_JPY=160`固定(`er019_family_x_audio_production_runner_01.py` L1829) |
| 集計関数 | 同 L1848-1889 `compute_cost_jpy_so_far(cost_log_path)`、L1892 `assert_budget_ok` | token×単価、`cost_usd`が既にあればそれを採用(L1865-1868)、**単価未登録は`PricingNotFoundError`でfail-closed**(L1834-1838)。**`compute_cost_jpy_so_far`の定義は46ファイルにコピーされている** [確認: `rg -l`]。web_search課金は`er012_e_family_entertainment_two_level_runner_01.py` L125 `web_search_call_usd`にのみあり(`web_search_call_count`×単価/1,000)、er019版にはweb_search課金の加算がない [確認: `rg web_search er019_…py` 0件] |
| 手書き集計 | `er052_output/open233_kpi_recovery_02_offline_01/agg_production_set_cost_01.py`、`er026_output/family_z_production_e2e_01/melos/COST_LEDGER_MELOS_01.md` | run/管理ID単位の個別集計。書式は統一されていない。COST_LEDGERは`cost_log.jsonl`にJPY列がなく`compute_cost_jpy_so_far`で再計算(L5-6) |
| 報告台帳 | `docs/pm/REPORT_LEDGER.md` の各行 | 行末近くに『費用JPY…』を記載(管理ID・委任単位。報告日基準) |

### 1-2. 日次開発費に関する既存規定
| 項目 | 所在 | 内容 [確認] |
|---|---|---|
| 予算Cap=暴走防止Guardrail | `PM_GOVERNANCE.md` 7-6 L760-797、`PM_BRIEF.md` L201-205 | 『Cap到達だけではSTOPしない』。STOPは暴走疑い(想定外のAPI大量発火・同じ失敗の無意味なretry loop・原因不明の費用増加・scope外処理・残費用の見通しが立たない・明らかにQCD上不合理)に限定。『数十円を避けるためTrial中断・ユーザー判断増・開発遅延をしない』 |
| JPY100以下のTrial | 同 7-7 L807-814 | 『JPY100以下のTrialはFable判断で承認・実行してよい』。100円超・Production採用・仕様変更はユーザー判断。『費用承認の要否については本決定が優先』 |
| 探索Trial一括承認 | 同 7-8 L816-826 | 低コスト・既存予算内・Production非変更の探索Trialは個別選択肢を逐一確認しない。予算超過はユーザー判断 |
| run単位の予算ガード | 各runnerの`--budget-jpy`/`--approved-budget-jpy`(205ファイル、DAY1_D §4) | run単位のみ。他runの消費を知らない |
| T-3(委任文の費用上限定型文) | `DELEGATION_READ_EFFICIENCY_BLOCK.md` T-3 | 『上限¥X(Guardrail)…』 |
| **日次1,000円(JST)** | **成文規定なし** | `PM_GOVERNANCE.md`/`PM_BRIEF.md`/`CLAUDE.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`をGrepして日次予算の定義は0件。Day1委任文(`delegation_log/2026-10-14_…_委任_01A.md` L6)の『有料API実行費の**日次共有予算1,000円**(日本時間)、増額はユーザー判断』が唯一の記述。DECISION_LOG L20364等の『上限¥1,000』は個別Trialの上限で無関係 |
| **70円/記事セット** | **成文規定なし** | DECISION_LOG L21038に『量産コスト上限70円/記事セット』(KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_01のユーザー指示の一節)がある。`CURRENT_SPEC.md` L2631(2026-10-14追記)にgloss再整合の量産費影響の**評価例**『≒JPY0.03〜0.15/記事セット(70円/セットの約0.05〜0.2%)』、`OPEN_ITEMS.md`に2行の言及 [確認: `rg -c 70円`]。**定義(範囲・分母・判定方法)は未成文**。L2631は4-4の『量産単価影響行』の先行実例(運用上は既に使われているが書式・範囲が揃っていない) |

### 1-3. [観測] 日次集計の既存手段の限界(本委任でread-onlyに実行。scratchpadの一時スクリプト、リポジトリ無変更)
`**/raw_usage_log.jsonl`(658)+`**/cost_log.jsonl`(36)=計694ファイル(`cost_log*.jsonl`全体は58ファイル。試算では完全一致名のみ走査)のtimestampをJST日付で絞り、pricing_snapshotで換算した試算と、REPORT_LEDGERの当日行の費用合計の突合。
| JST日付 | ログ集計(JPY) | ログのレコード数/ファイル数 | REPORT_LEDGER当日行の費用合計(JPY) | 行数 | 所見 |
|---|---|---|---|---|---|
| 2026-10-15 | 約4.07(openai) | 12 / 3 | 7.04(2.49+1.83+1.12+0+1.60+0) | 6 | ログのほうが小さい(ledgerには推定値・ログ外費用を含む) |
| 2026-10-14 | 約1.84(gemini_batch 0.90+openai_asr 0.93)。azure STT 26件は試算スクリプトで単価未登録扱い | 50 / 2 | 7.64(0+0.36+6.1+1.18) | 4 | 同上。FAMILY-XZ…委任_04の『runner実測4.44+推定1.7』のように**ログ外の推定値**がledgerに入る |
→ **結論**: ログだけでは過小(run dir外の費用・推定値・単価未登録モデル)、REPORT_LEDGERだけでは報告遅延と粒度不統一がある。**両方を出し、大きいほうを当日既使用額として採用**するのが保守的で安全。[推定] 通常日の実額は数円〜数十円で、1,000円/日に対して十分小さい。重い日(例: 2026-10-12のMelos E2E、累計JPY108+)にだけ日次横断の把握が効く。

## 2. 70円/記事セットの計算範囲の具体化案(`PM_GOVERNANCE.md` 15-9として新設)
**原則: 既存維持+具体化。既存の15-1〜15-8の定義は1文字も変更しない。**
### 2-1. 分母
**『記事セット』= §15-8『Production 1生成セット』(Family別の正式1生成セット)**。News/Trend/Discovery=『共通Research/Ledger+A2+B1』、Voices=『そのFamilyの正式1生成セット』。共通Research/Ledgerは**A2/B1へ配賦せず**、セット総原価に全額を計上する(15-8の50:50配賦禁止を維持)。Trendのように1runでA2+B1を生成する場合は『Production 1生成セット(A2+B1)』で1セット。
- 15-8の標準表に載っていないFamily(例: Family X Coffee、Family Z Fiction)は、**初回の原価測定を行う委任で『そのFamilyの正式1生成セットの構成』を明記してから**表に追加する(Fable判断。ユーザーが各Familyで別目標を指示した場合のみ差を設ける)。DAY1_D §5 ③のとおり、DECISION_LOG内の『1生成セット総原価』は¥99.01〜¥840.74で定義が揃っていない [確認: DAY1_D]。**70円に対する現在位置は未確定**(ベースライン測定が必要。本設計では測らない)。
### 2-2. 含む/含まない表
| # | 費目 | 70円に | 根拠 | 計上方法・備考 |
|---|---|---|---|---|
| 1 | Research/Ledger(LLM、web_search課金) | **含む** | 15-2、15-8 | 共通費。配賦しない。web_search手数料も含める(`web_search_call_usd`、T-GAP-01) |
| 2 | Writer(A2/B1)・Fact Check・Support・Comment生成 | **含む** | 15-2 | stageタグ(`raw_usage_log.jsonl`の`stage`)で内訳表示 |
| 3 | Key Phrase選定・canonicalization・日本語gloss生成・**gloss再整合(corrected、Production採用後)** | **含む** | 15-2『Key Phrase』 | 新機能のため量産単価影響評価の対象(4-4)。OPEN-358(canonicalizationのLLM費用ログ欠落)は既知の計上漏れ候補 [確認: OPEN_ITEMS L867] |
| 4 | TTS(音声生成) | **含む** | 15-2、7-4 | **判定値=15-5区分5(Batch量産換算)**、区分4(Standard同期)を併記。正式リリース前でStandardで実行しても、70円判定はProduction想定の経路で行う(7-4『量産=Batch』)。Batchが適用できない経路は実行経路で判定し注記。**U5-Q1** |
| 5 | ASR検証(OpenAI ASR/Azure STT) | **含む** | 15-2『ASR』 | Azure STTは`cl.azure_stt_cost_usd`で計上。単価未登録はfail-closed |
| 6 | 自動retry・fallback・regeneration・Local Rewrite | **含む** | 15-2、15-5 区分3 | 『通常(retryなし)』と『実績(retry込み)』の両方を示す。retry/Rewriteによる上振れは内数で明示(15-5 区分3) |
| 7 | Human Review由来の再生成API費用 | **含む(内数)** | 15-5 区分3 | Human作業時間(人件費)は**含まない**(API費用ではない) |
| 8 | 失敗・不採用になった試行の費用 | **仕様確定後のProduction run内なら含む** | 15-6 | 仕様変更・Trial・調査目的のrunで発生した費用は『Trial特有/異常対応』(15-3)として別枠。**run開始時の目的(Production/Trial)をRESULT_PACKET費用行に明記**(ログに目的タグがないため、DAY1_D §6の不足を運用で補う) |
| 9 | 再利用資産(Master Audio Store、固定Welcome等) | **そのセットで実際に発生した分のみ** | 15-8 | 再利用で0円の部分は0。再利用資産の**初回生成費は初回セットに計上し、償却しない**(保守的)。reuse率を別行で併記 |
| 10 | 開発Trial・A/B比較・calibration・評価モデル実行 | **含まない** | 15-3、7-4 | 別軸の『開発費』。ただし新方式の**量産単価影響の見積に使った実測値**は影響評価の根拠として引用してよい |
| 11 | Claude Code usage | **含まない** | 9-10 | 週間利用枠%で別報告 |
| 12 | 為替 | USD_JPY=160固定を継続 | 既存script全般 | 変更する場合は全script・ledgerに波及するため別判断 |
| 13 | 単価 | `pricing_snapshot.json`の該当tier | 15-4 | 未登録モデルは実行前に公式単価を登録(25-2) |
### 2-3. 判定の方式(目標であり停止条件ではない)
- **70円は目標(Target)**。Hard gateにはしない(U5原文『目標』『目標超過見込みの場合は、改善策・代替案・品質への影響を検討する』)。品質(Q)＞納期(D)＞量産単価(C)の序列は変わらない(Charter)。
- **変更時の事前評価(必須)**: 新機能・モデル変更・retry追加・Prompt拡張のとき、設計時の委任文・Opus依頼文・Production採用提案に次の1行を必ず記す:
  `量産単価影響: +JPY<w>/セット(根拠: 追加call数/セット×平均token×単価、retry期待増=発生率×再生成費)。現行ベースラインJPY<b>→予測JPY<p>/目標70円。`
  `w≧+JPY1/セット`のときは記録し許容可否をFableが判断(『恒久的な1〜2円増も軽視しない』、Day1合意)。
- **超過見込み時**(予測p>70円): ①改善策(call削減・モデル/effort調整・キャッシュ・既存再利用)②代替案(複数)③品質への影響、を比較して提示する。70円超のまま採用提案する場合は『重大な品質・費用トレードオフ/コストへの重要な影響』(10-1 UDR維持範囲)としてユーザー判断。
- **事後評価**: Production run後は15-8の標準表で『Production 1生成セット総原価』を報告し、70円との差を併記する。直近の実測値は15-8表(報告)の積み上げで追跡する(新台帳は作らない)。
- **同じ失敗を繰り返さない**: 量産単価に悪影響の変更は、QDC記録の費用欄#6に`+JPY/セット`を載せ、再計画(11-6)の判断材料にする。

## 3. 日次1,000円(JST)の運用設計(`PM_GOVERNANCE.md` 7-9として新設)
### 3-1. 定義
**開発費(日次)** = JST暦日(00:00〜24:00)に発生した**有料API実行費の合計**(LLM/TTS/ASR/検索手数料等)。Trial・比較・調査・検証、および**正式リリース前のProduction経路の実行**(再生成・失敗を含む)を含む。Claude Code usageは含まない(9-10)。ログのtimestampはUTCなので+9時間でJST日付に変換し、**呼出単位**で日付を割り当てる(日付をまたぐrunは分割)。量産単価(15-9)の集計とは別の軸で、同一の支出が両方に現れうる(二重計上ではなく二つの見方)。
性質: **原則(ソフト上限)**。到達しても自動STOPしない(7-6を維持)。**新しい強制停止ルールは作らない**(U5『ユーザー承認なしで別の強制停止ルールへ変更しないこと』)。
### 3-2. 当日既使用額の把握手段
| 段階 | 手段 | 精度 | 使う場面 |
|---|---|---|---|
| 1(追加コード0) | ①前委任の`RESULT_PACKET`費用行(Sonnetが記載)と`ACTIVE_TASK.md`固定ヘッダ`QDC:`行の`当日費用=<JST日付> <累計>/1,000` ②`docs/pm/REPORT_LEDGER.md`の当日行(`rg -n "^- <日付> \|" docs/pm/REPORT_LEDGER.md`)の費用合計。FableはRead/Grepで確認できる | 報告遅延あり・並行タスクのACTIVE_TASK断片化(`ACTIVE_TASK_ROLL*.md`等)でやや不正確 | 通常日(当日累計500円未満、見積100円以下) |
| 2(最小補強) | `docs/pm/tools/daily_dev_cost_01.py`(read-only、API 0)。**Sonnetが実行**(FableとHaikuのtoolsにBashがない: `sandwich-pm.md` L4、`haiku-worker.md` frontmatter) | ログ+ledgerの両方を出力し大きいほうを採用 | 当日累計500円超、または見積100円超、または並列タスクが多い日 |
**採用値**: 段階1と2の取得値のうち**最大値**を当日既使用額とする(保守側)。取得できない費用(ログ外・推定)は『未捕捉』として列挙し、確認できなかった事実を推定で埋めない。
**Fableが読む場所**: 委任文の性質欄の費用行(3-4)、`RESULT_PACKET`費用行、`ACTIVE_TASK.md`の`QDC:`行。Fable自身はBashを持たないため、日次集計の実行はSonnetに委任し結果を1行で書かせる。
### 3-3. 最小補強案: 集計script 1本の是非
- **既存scriptで代替できるか(先に確認)**: できない。`compute_topic_cost.py`(theme単位)・`er005_stage7_cost_compute.py`・`agg_production_set_cost_01.py`(run単位)・`compute_cost_jpy_so_far`(46コピー、1ログ単位)はいずれも**日付絞り込み・複数ログ横断をしない** [確認: 先頭部とdef確認]。
- **提案(W9b、任意だが推奨)**: `docs/pm/tools/daily_dev_cost_01.py`(PM層の既存置き場。`check_delegation_prompt.py`と同じ`docs/pm/tools/`)。仕様:
  - 入力: `--date YYYY-MM-DD`(JST、既定=今日)、`--repo-root`、`--ledger docs/pm/REPORT_LEDGER.md`、`--json-out`。
  - 処理: `**/raw_usage_log.jsonl`・`**/cost_log*.jsonl`を走査し、`timestamp`(UTC)→JSTで日付一致の行を集計。換算は`er019 compute_cost_jpy_so_far`と**同じ規則**(`cost_usd`があれば採用、なければtoken×`pricing_snapshot.json`、`USD_JPY=160`、web_search=`web_search_call_count`×単価/1,000、azure STTは`er005_cost_logger.azure_stt_cost_usd`、**単価未登録は0円にせずunpricedとして件数・モデルを列挙**)。
  - 出力: 総額JPY、provider別、run dir別上位N、ledger当日行の合計、`採用値=max(ログ,ledger)`、**未捕捉の種別**(run dir外・ログ外課金・Batch未完了・単価未登録・推定値)の列挙、走査ファイル数。read-only(ログを書き換えない)。
  - 作らないもの: 実行時ガード、共有ledger、runnerへの組み込み、自動停止。
  - 見積り: 実装+unit test(合成ログで日付境界・JST変換・unpriced・ledger突合)で約1.0〜1.3h、JPY0。
  - 重複/コピー問題: 46コピーの`compute_cost_jpy_so_far`は変更しない。新scriptは**pricing読込を自前で持ち、既存runnerをimportしない**(import副作用回避)。
- **採用判断の目安([推定])**: 通常日は段階1で足りる。しかし(a)並列タスクがある日、(b)重いTrial日、(c)U5『Fableは当日の既使用額・残予算を把握』を**決定的な手順**にしたい、の3点から段階2を用意しておく価値がある。費用対効果が低い日は使わない(『当日累計500円超または見積100円超のときだけ』)ので、運用負荷は小さい。

### 3-4. Fableが委任前に確認する欄(`DELEGATION_STANDARD_TEMPLATE.md`の性質欄に1行追加)
`費用/日次: 当日(JST)既使用JPY<y>(出典: <RESULT_PACKET|LEDGER|script>)/残JPY<1,000-y>/本委任見積JPY<e>(根拠: call数×単価、上限=Guardrail)/改善見込み<高|中|低>(11-6)/承認区分: <A:Fable判断可|B:ユーザー承認要|C:承認済みscope内>`
- 既存のT-3定型文(『上限¥X(Guardrail)…』)は**変更しない**。本行はT-3の前に置く追加情報。
- 費用$0の委任(本件のような設計・docs)は『JPY0』と書くだけでよい(軽量)。

### 3-5. ソフト上限の扱いと承認要否(既存Gateを弱めない)
| ケース | 条件 | 動作 | 根拠 |
|---|---|---|---|
| 1 | 見積e≦JPY100 かつ y+e≦1,000 | **Fable判断で実行可**(都度ユーザー確認なし) | 7-7、U5『費用の小さなTrialをその都度ユーザー判断に回さない』 |
| 2 | e>JPY100(y+eの大小に関わらず) | 従来どおりユーザー判断(承認済みの一括承認[7-8]の範囲内なら不要) | 7-7、7-8(変更なし) |
| 3 | **y+e>1,000(日次超過見込み)** | **実行前にユーザー承認**(STOP→承認依頼)。依頼に超過額・理由・改善見込み・安価な代替・QDC影響を付ける | U5『予算超過や追加承認が必要な場合はSTOPする』、Day1合意『増額はユーザー判断』 |
| 4 | 実行中に当日累計が1,000円に到達/超過 | **自動STOPしない**(7-6)。承認済みscope内・原因把握済み・異常retryでない・残作業明確・追加費用合理的なら超過を記録して継続。**新規Trial・新規runは開始しない**(ケース3の承認が先)。暴走疑いはSTOP。12-2(blocker)として即時報告 | 7-6維持 |
| 5 | ユーザーが個別に承認した予算(例: 「E2E追加上限JPY300」)のrun | その承認が有効(22節ユーザー指示優先)。当日累計には加算。新規Trialは3の扱い | 22節、7-6 |
| 6 | 見積不能 | 委任文のGuardrail上限を見積として扱う | T-3 |
→ 7-6『Cap到達=自動STOPではない』・7-7・7-8・T-3・各runの`--budget-jpy`は**1文字も変更しない**。7-9は『新規開始前の確認義務』と『超過見込み時の承認要否』を追加するのみ(**弱体化なし、強制停止の新設なし**)。
→ ケース3の『y+e>1,000は事前承認要』は、7-7(JPY100以下はFable判断)を**置き換えない**。7-7の『100円以下』は引き続き都度承認不要だが、**日次累計が上限に近いとき**だけ追加の確認(承認)が入る。これはU5『予算超過や追加承認が必要な場合はSTOP』の具体化。

## 4. 費用情報を判断に使う具体ルール
### 4-1. 再計画時(11-6のR5と接続): 残予算×改善見込み×見積
| 改善見込み | 当日残≧見積 | 当日残<見積 |
|---|---|---|
| 高 | 続行(同アプローチ) | 範囲縮小(標本・段階を絞る)、または承認依頼(ケース3) |
| 中 | **検証を安価化して続行**(既存logの再利用・offline replay・mock・小標本)。見積を下げられない場合のみそのまま | 別案(安価な代替)、または承認依頼 |
| 低 | 同アプローチの続行は不可 → 再計画(安価な代替から) | **STOP(E1)**。費用を理由に惰性で続けない |
『同じ失敗を惰性的に繰り返さない』(U5)は、QDC記録#5『改善見込み』と#6『費用』を並べて書かせることで担保する(惰性反復=改善見込み『低』の同一アプローチ再委任の禁止、11-6)。
### 4-2. モデル選定(25節との関係)
- 評価・Trial用途は**最新世代の最上位/推奨系が原則**(25-1)。**『安いから』『前に使ったから』は例外理由にならない**(25-2)。→ 費用は**降格の第一手段にしない**。
- 費用が制約の場合の調整順: ①標本数・run数・段階(offline先行・既存log再利用)を減らす ②見積をGuardrailとして明示 ③それでも収まらない場合に限り、25-1の例外2.『API制約・互換性・速度・費用上限など実務上の制約』として旧/下位モデルを使い、**実行前に例外種別と理由を明記**(25-2)。
- 本番ラインのモデル選定は別判断(25-1 4)。ライン組み込み候補の評価では、**候補ごとの量産単価影響(+JPY/セット)を必ず比較表に載せる**(15-9、4-4)。
- 評価・Trialの報告には従来どおり使用モデル名/最新か/最新でない場合の理由(25-3)+費用(見積→実測)を記載する。
### 4-3. Trial設計: 見積→実測→差分の記録先(新ファイルなし)
| 段階 | 記録先(既存) | 内容 |
|---|---|---|
| 見積 | 委任文の性質欄『費用/日次』行(3-4) | call数×単価の式、Guardrail上限 |
| 実測 | `RESULT_PACKET`費用行+run dirの`raw_usage_log.jsonl` | 実測JPY、purpose(Production/Trial)の明記 |
| 差分 | `REPORT_LEDGER.md`の当該行の費用欄に『見積JPYx→実測JPYy』を併記(列は増やさない) | 差が±50%または±JPY10を超えたら、当該管理IDの`DECISION_LOG.md`エントリに補正メモ1文 |
### 4-4. 量産単価影響評価の記載場所
設計時の委任文(性質欄)、Opus依頼文のpacket(a)欄(`OPUS_CONTEXT_PACKET_TEMPLATE.md`に1行追加、W7)、Production採用提案(条件C)。形式は2-3の1行。

## 5. 変更前/変更後の実文表(Phase 2が機械的に適用できる粒度)
### 5-A. 新設(既存文は変更しない): `PM_GOVERNANCE.md` 7-9、15-9
- 挿入位置: 7-9=7-8末尾(`7-8`の『初回適用』行=L826)の直後、`## 8.`(L828)の前。15-9=15-8末尾(『参考内訳として併記する。』L2885)の直後、`---`(L2887)の前。
- 7-9本文(案、Phase 2はこの枠を挿入):
<!-- RULE_7_9_BEGIN -->
### 7-9. 日次開発費(原則1,000円/日・JST)の運用(2026-10-15ユーザー正式判断、PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 U5)

**ユーザー方針(逐語)**: 「開発費: 日次予算：原則1,000円／日（JST）。既存§7-6の運用と矛盾しないようにする。Fableは当日の既使用額・残予算・次のTrial見積を把握し、残予算と改善見込みから追加Trialの可否を決める。同じ失敗を惰性的に繰り返さない。費用の小さなTrialを、その都度ユーザー判断に回さない。予算超過や追加承認が必要な場合はSTOPする。…なお、原則1,000円／日の既存運用を、ユーザー承認なしで別の強制停止ルールへ変更しないこと。ソフト上限として扱う場合も、既存の費用Gateと停止条件を維持し、超過時の承認要否を明確にする。」

**定義**: 開発費(日次)=JST暦日に発生した有料API実行費(LLM/TTS/ASR/検索手数料等)の合計。Trial・比較・調査・検証、および正式リリース前のProduction経路の実行(再生成・失敗を含む)を含む。Claude Code usageは含まない(9-10)。ログのtimestampはUTCなのでJSTへ変換し、呼出単位で日付を割り当てる。量産単価(15-9)とは別の集計軸。

**性質**: 原則(ソフト上限)。到達しても自動STOPしない(7-6を維持)。新しい強制停止ルールは作らない。7-5・7-6・7-7・7-8・15節・各runの予算ガード・T-3は変更しない。

**Fableの確認義務**: 新規のTrial・run・追加委任を開始する前に、当日(JST)既使用額・残・本委任の見積・改善見込みを確認し、委任文の性質欄に1行で記す。把握手段は(1)前委任のRESULT_PACKET費用行とACTIVE_TASK `QDC:`行(2)REPORT_LEDGERの当日行(3)日次集計script(`docs/pm/tools/daily_dev_cost_01.py`。当日累計500円超または見積100円超のとき実行)。採用値は取得できた値の最大値。取得できない費用は『未捕捉』と明記し、推定で埋めない。Fable自身はBashを持たないため、集計の実行はSonnetへ委任する。

**承認要否**: (1)見積100円以下かつ当日累計+見積が1,000円以内=Fable判断で実行可(7-7)(2)見積100円超=従来どおりユーザー判断(7-7。7-8の承認済み範囲内を除く)(3)当日累計+見積が1,000円を超える見込み=実行前にSTOPしてユーザー承認を求める(超過額・理由・改善見込み・安価な代替・QDC影響を付ける)(4)実行中に1,000円へ到達しても自動STOPしない(7-6)。承認済みscope内・原因把握済み・異常retryでない・残作業明確・追加費用合理的なら超過を記録して継続し、新規Trial・runは開始しない。暴走疑いはSTOP(7-6)(5)ユーザーが個別に承認した予算のrunはその承認が有効(22節)。当日累計には加算する。

**判断への利用**: 再計画(11-6)では、改善見込みと当日残で続行・安価化・別案・STOPを決める。同じ失敗を惰性的に繰り返さない(改善見込み『低』の同一アプローチの再実行は不可)。評価用途のモデル選定は25節に従い、費用は降格の第一手段にしない(標本・段階の調整を先に行い、旧/下位モデルは25-1の例外として実行前に明記する)。見積と実測の差は委任文・RESULT_PACKET・REPORT_LEDGERに残し、差が±50%または±JPY10を超えたら補正メモを残す。
<!-- RULE_7_9_END -->
- 15-9本文(案):
<!-- RULE_15_9_BEGIN -->
### 15-9. 量産単価目標(70円/記事セット)の対象範囲(2026-10-15ユーザー正式判断、PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 U5)

**ユーザー方針(逐語)**: 「量産費: 目標：70円／記事セット。既存PM_GOVERNANCE.md §15-1／§15-8を基準として、記事セットの分母、対象API・TTS・retry・fallback等の費用範囲を具体化する。新機能・モデル変更・retry追加時は、量産単価への影響を評価する。目標超過見込みの場合は、改善策・代替案・品質への影響を検討する。」

**分母**: 『記事セット』=15-8『Production 1生成セット』(Familyごとの正式1生成セット)。共通Research/LedgerはA2/B1へ配賦せず、セット総原価に全額を計上する。15-8の標準表にないFamilyは、初回の原価測定の委任で正式1生成セットの構成を明記してから追加する。

**含む**: 記事生成LLM(Research/Ledger・Writer・Fact Check・Support・Key Phrase・canonicalization・日本語gloss・gloss再整合)・TTS・ASR検証・自動retry/fallback/regeneration/Local Rewrite・Human Review由来の再生成API費用(内数)・web_search手数料。**含まない**: 開発Trial・A/B比較・calibration・評価モデル実行(15-3の『Trial特有』)・Claude Code usage(9-10)・人件費(Human Review作業時間)。仕様確定後のProduction run内の失敗・再生成は含み、仕様変更・調査目的のrunは『Trial特有/異常対応』として別枠にする(run開始時の目的をRESULT_PACKETの費用行に明記)。再利用資産は、そのセットで実際に発生した費用のみを計上し、再利用資産の初回生成費は初回セットに計上する(償却しない)。

**判定値**: TTSは15-5の区分5(Batch量産換算)で判定し、区分4(Standard同期)を併記する。為替はUSD_JPY=160固定、単価は`pricing_snapshot.json`。retryは『通常(retryなし)』と『実績(retry込み)』を示す。

**性質**: 目標であり停止条件ではない(品質＞納期＞量産単価、Charter)。変更時の評価は必須: 新機能・モデル変更・retry追加・Prompt拡張では、委任文・Opus依頼文・Production採用提案に『量産単価影響: +JPY<w>/セット(根拠)。現行JPY<b>→予測JPY<p>/目標70円』を記す。+JPY1/セット以上は記録して許容可否をFableが判断する。予測が70円を超える見込みの場合は、改善策・代替案(複数)・品質への影響を比較して提示し、70円超のまま採用を提案する場合は『コストへの重要な影響』(10-1)としてユーザー判断とする。Production run後は15-8の標準表で総原価を報告し、70円との差を併記する。
<!-- RULE_15_9_END -->
### 5-B. 既存文への追記(参照のみ)
| # | 位置 | 変更前(逐語) | 変更後(案) |
|---|---|---|---|
| E1 | `PM_GOVERNANCE.md` 7-6末尾 L796-797 | `ループ上限(11節)・Opus診断1回上限・Gate 1〜7・Human Review Lock等、`⏎`予算Cap以外の既存安全装置も本決定によって変更・緩和されない。` | `11節の問題解決運用(11-6)・Opus診断1回上限・Gate 1〜7・Human Review Lock等、予算Cap以外の既存安全装置も本決定によって変更・緩和されない。日次1,000円の運用は7-9、量産単価目標は15-9。`(U2のB5と同一編集) |
| E2 | `PM_GOVERNANCE.md` 15-8末尾 L2883-2885 | `…Production記事(量産)の報告では、本15-8のFamily別`⏎`「Production 1生成セット総原価」表を主指標とし、15-5の5区分等は`⏎`参考内訳として併記する。` | 末尾に1文: `70円/記事セット目標の対象範囲は15-9。` |
| E3 | `PM_BRIEF.md` L201-205(予算Cap) | `予算Cap(費用上限)は「暴走防止のためのGuardrail」であり、Cap到達だけを`⏎`理由に自動STOPしない(継続条件・STOP条件・優先順位は`⏎``` `docs/pm/PM_GOVERNANCE.md` ```` 7-6、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`)。` | 末尾に追記: `日次開発費(原則1,000円/日・JST)は7-9、量産単価目標(70円/記事セット)は15-9。新規Trial・runの開始前に当日の既使用額・残・見積を確認し、1,000円を超える見込みの場合は実行前にユーザー承認を求める。` |
| E4 | `DELEGATION_STANDARD_TEMPLATE.md` 性質欄(L16〜26)の末尾 | `…並列化判断[並列実行する作業/直列化する場合の理由]を1〜2行で記す[PM_GOVERNANCE 8-X、2026-10-06]。**)` | 追記: `**費用/日次の1行[当日JST既使用/残/本委任見積/改善見込み/承認区分、PM_GOVERNANCE 7-9]と、量産単価に影響する変更では「量産単価影響」の1行[PM_GOVERNANCE 15-9]を記す。**` |
| E5 | `DELEGATION_STANDARD_TEMPLATE.md` Fable自己チェック(L106-114)の末尾 | `- [ ] 時間見込み・並列化判断あり(主要タスク、PM_GOVERNANCE 8-X)` | 追記: `- [ ] 費用/日次の1行あり(当日既使用・残・見積。PM_GOVERNANCE 7-9)` |
| E6 | `PM_BRIEF.md` 固定ヘッダ書式 L226-279(`QDC:`行はU2のW6と共通) | (U2のW6と同じ編集) | `QDC: 見込み=<高中低> 進捗=<前進/横ばい/後退> 当日費用=<JST日付> <累計>/1,000 次=<一手>` |
| E7 | `PM_GOVERNANCE.md` 9-0 第5節『次の行動・費用』 L1092-1093 | `5. **次の行動・費用** — 次に何をするか / 必要費用 / 最後にユーザーが答える`⏎`   事項だけを列挙` | `5. **次の行動・費用** — 次に何をするか / 必要費用(必要なら当日(JST)累計/残と、量産単価影響) / 最後にユーザーが答える事項だけを列挙` |
| E8 | `OPUS_CONTEXT_PACKET_TEMPLATE.md` (a)欄(W7) | (承認状況欄追加と同じ編集) | `量産単価影響の1行[15-9]`を1行追加 |
| E9 | `docs/pm/tools/daily_dev_cost_01.py`+`daily_dev_cost_01_test_01.py`(W9b、任意・推奨) | (新規。`check_delegation_prompt_test_01.py`と同様の配置) | 3-3の仕様。Phase 2は実装後にunit testとregression(`run_project_regression.py`は不要、`.venv`でtest単体)で確認 |
(注) `check_delegation_prompt.py`の必須キーワード・固定ブロックラベル(`管理ID`/`性質`/`事前指定Read一覧`等)は変更しない。E4,E5は見出し文字列を変えない。

## 6. 競合・USER_DECISION_REQUIRED候補
**既存定義の変更を要する競合: 0件**。次の2点は『既存維持+具体化』だが、解釈にユーザー価値判断が含まれうるため、Fableの受入またはOpus条件Aレビューでの確認を推奨(ブロッキングではない)。
- **U5-Q1【確認推奨・Fable判断可】70円のTTS判定基準**: 本案=Batch量産換算(15-5 区分5)で判定、Standard同期(区分4)併記。根拠: 7-4『量産=コスト優先でBatch』『Production unit costとDevelopment costは別軸』。代替=実行経路そのままの『今回実測』で判定(正式リリース前はStandardが多く70円超になりやすい)。推奨=本案。判断が割れる場合のみユーザーへ。
- **U5-Q2【確認推奨】1,000円/日の成文化と『超過見込み=実行前承認』**: 1,000円/日はSSOT未成文のため、U5原文を正本として7-9に記録する(DECISION_LOG追記とセット)。『y+e>1,000は実行前にユーザー承認』はU5原文『予算超過や追加承認が必要な場合はSTOPする』『超過時の承認要否を明確にする』の具体化であり、7-7(100円以下はFable判断)・7-6(自動STOPしない)と整合する。ユーザーが『超過時もFable判断で継続可』を望む場合のみ変更が必要(現文はU5原文に従う安全側)。
- **補足(競合ではない)**: (a)Day1/Day2では日次1,000円の『ハード停止』案(全runner共通ledger)を『各runner改修が大きい』として見送った。本設計も**ハード停止は導入しない**(U5が禁止)。(b)7-5(4)『想定外の全再生成はAPI前にSTOP』は7-6の暴走検知と二重基準(Day2 RULE_CHANGE_MATRIX R25/C7)だが、U5の範囲外で変更しない。(c)OPEN-358(canonicalizationのLLM費用ログ欠落)は70円の計上漏れ要因として既知。解消は本件の対象外(Open Item継続管理)。
