# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04 委任_01(略称SJS4。Coffee正式E2E完成版のStandard日本語解説[Preview/Comment1〜4]のStyle比較Trial: 基準P2・R2+新規S1〜S8、各2 Take、DEV経路、比較ページ作成)。本日=2026-10-17(JST)。番号04は既存の`er057_aoede_style_trial_03_*`(別Trial)との衝突回避のため。

## 性質/到達上限Status/禁止事項
- 性質: **Trialのみ**(DEV/Trial専用経路)。Production反映はユーザー選定後の別タスク。有料: Gemini TTS+JA ASR。
- 到達上限Status: `TRIAL_GENERATED_USER_LISTENING_PENDING`(機械評価とユーザー聴感評価を分ける。ユーザーPASS扱い禁止。聞こえのよいTakeだけを選んで掲載しない=全Take掲載)。
- 費用上限(T-3): 上限JPY40(Guardrail)。見積=前回Trial(`er057_output/ja_aoede_style_trial_02/cost_actual_01.json`: 80 clip実測JPY13.73)に比例し100 clip≒JPY17〜18+ASR約1.5+retry見込み≒**期待約JPY20/最悪約28**。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。実行前に見積を再計算し、JPY100を超える見込みなら実行せず報告(7-7)。
- 禁止: Production code/Prompt/Style profile/Master Audio Store/`CURRENT_SPEC.md`の変更(読取のみ)/記事・日本語原稿の書換え・再生成/Key Phrase・Full Story・Advancedの生成/P2・R2の名称からの再構成(逐語維持、sha検証必須)/P2・R2への共通指示の付加/候補の追加・削除/Voice・モデル・速度・音量処理の変更(比較する変更はStyleのみ)/`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f/無関係dirty差分のadd/STOPセンチネル操作/Family A・B・C。
- 並行タスク: なし(commitを伴う作業は本委任のみ。ユーザー指示「commitを伴う作業は同時に1つだけ」)。
- Opus Gate(11-3): 非該当(既存Trial方式の再利用、Production変更なし)。
- 時間見込み: 準備(原稿・Style・条件確定)30分/生成100 clip+ASR 20分/連結・ページ・再生確認40分/記録・commit 30分 ≒ 2時間。並列化: 生成はAPI rate limitと費用集計の整合のため単一process直列。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。
T-0補足(厳守): (a)本委任文は**全文**(全節・全見出し)を `docs/pm/delegation_log/2026-10-17_FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04_委任_01.md` へ保存(要約不可。直近2委任で要約保存→check FAILが再発)。(b)下記「ユーザー指示(原文)」節を**一字一句そのまま** `docs/pm/delegation_log/2026-10-17_FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04_USER.md` へ保存し、文字数とsha256を記録。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

## ユーザー指示(原文)
Coffee Standard日本語解説の追加Style Trialをお願いします。まずはTrialのみ実施し、Productionへの反映は私の選定後としてください。

■目的・ユーザー評価

Coffee正式E2E完成版を試聴し、記事・音声とも全体として高評価です。変更希望はStandardの日本語解説（Preview／Comment1〜4）の話し方のみです。

前回TrialではP2・R2が好みに近かった一方、完成版では少しテンションが高く、語尾の調子や一部の抑揚が気になりました。生成ごとのばらつきも考慮して選び直します。

P2・R2の温かみ・親しみやすさ・明瞭さを残し、やや落ち着いた方向に新規8仕様を比較してください。

■比較対象

基準：P2・R2
新規：S1〜S8
計10仕様。

P2・R2は前回Trialの実際のStyle全文をRepoから確認し、逐語で維持してください。名称から推測して再構成しないこと。

前回ページ：
https://shimomura055.github.io/eigo-radio/user_test/coffee_ja_style_trial_02/index.html

■新規Style案

以下の個別指示に、後述の共通指示を付けたものを、各仕様のStyle全文としてください。

S1：P2の穏やかな修正版
温かみのある、親しみやすい自然な話し方で。聞き手に穏やかに語りかけるように、内容に沿った控えめな抑揚をつけてください。ニュース番組としての明瞭さを保ち、全体の明るさは控えめにしてください。文末は力を抜いて自然に収めてください。

S2：R2の穏やかな修正版
身近な人に興味深い話題を伝えるように、温かみのある自然な話し方で。親しみやすさを保ちながら、落ち着いた調子と無理のないリズムで話してください。大切な点にだけ軽く抑揚をつけ、語尾はやわらかく収めてください。言葉は明瞭に伝えてください。

S3：親しみのあるニュースナレーター
温かみと親しみのあるニュースナレーターとして、落ち着いた、明瞭な声で伝えてください。声の調子は安定させ、重要な言葉や対比にだけ控えめな抑揚をつけてください。文末は軽く下げて自然に収め、聞き手が内容を追いやすい流れで読んでください。

S4：身近なニュース解説者
ニュースの背景を身近な人に説明するように、親しみやすく落ち着いた口調で話してください。内容への関心を穏やかに示し、要点や話のつながりを明瞭に伝えてください。説明の途中でテンションを上げず、文末は力を抜いてやわらかく収めてください。

S5：穏やかなニュース系Podcaster
落ち着いたニュース系Podcastのホストとして、温かみのある自然な会話調で話してください。聞き手と話題を共有するような親しみを持ち、内容に沿った穏やかな抑揚と滑らかなリズムで伝えてください。声の明るさは控えめにし、語尾は短く自然に収めてください。

S6：一人の聞き手に向けたPodcaster
関心を持って聞いている一人の相手に、話題を丁寧に伝えるPodcastホストのように話してください。身近で温かい距離感を保ち、落ち着いた普段の会話に近い調子で伝えてください。抑揚は意味を伝えるために必要な範囲にとどめ、文末はやわらかく収めてください。

S7：ニュースの明瞭さ＋Podcastの親しみ
ニュースナレーターの明瞭さと、Podcastホストの親しみやすさを合わせた話し方で。温かみのある落ち着いた声で、聞き手に自然に語りかけてください。要点や対比には軽く抑揚をつけ、それ以外は穏やかな調子を保ってください。語尾を伸ばさず、自然に収めてください。

S8：さらに抑揚を抑えた中間型
ニュースナレーターの明瞭さと、Podcastホストの温かみを持つ、落ち着いた話し方で。声の調子とテンションを穏やかに保ち、重要な点にだけ小さく抑揚をつけてください。親しみはやわらかな声で表し、文末は軽く下げて収めてください。関連する文は滑らかにつないでください。

S1〜S8への共通指示：
句読点は自然な間として扱い、記号だけを理由に声の高さを変えないでください。問いかけは穏やかに読み、語尾を大きく跳ね上げないでください。演技がかった強調は避けてください。

※この共通指示は、基準のP2・R2には追加しないでください。

■原稿・生成条件

・原稿は今回の正式Coffee E2E完成版のStandard Preview／Comment1〜4をそのまま使用。記事・日本語原稿の書き換えや再生成は不要です。
・Voice、モデル、速度、音量処理などは今回の正式版と揃え、比較する変更はStyleのみとしてください。
・ばらつき確認のため、P2・R2を含む全10仕様で、5セクション一式を独立に2回生成してください。Take A／Bを明示してください。
・既存の前回P2・R2音声も参考として残し、「旧原稿・既存音声」であることを明記してください。同一原稿での比較は今回生成するP2・R2を使用します。
・機械評価とユーザーの聴感評価を分け、試聴前にユーザーPASS扱いしないでください。聞こえのよいTakeだけを選んで掲載しないこと。

■試聴ページ

前回「基準P2＋R1〜R8」と同じセンスで、候補名・調整の狙いを明示した比較ページを作ってください。Blind比較にはしません。

各仕様について、以下を掲載してください。
・P2／R2は基準として目立つ表示
・調整内容と狙い
・Take A／Bそれぞれの通し再生（Preview→Comment1〜4）
・各セクションの個別再生
・実際に読み上げた原稿全文
・実際にTTSへ渡したStyle全文（省略なし）
・ASRなど既存の品質確認結果

通し音声の連結・間・音量処理は全候補で揃え、試聴用の連結であることを明記してください。音声だけのページにはしないこと。

■報告

最初に試聴ページURLを提示し、基準2仕様＋新規8仕様、各2 Takeが揃ったこと、生成条件、費用、品質確認結果を簡潔に報告してください。

選定では「一番よかったTake」だけでなく、2 Takeともテンション・語尾・抑揚が許容範囲に収まるかを確認します。

今回はStandard Preview／CommentのStyle比較に限定します。Key Phrase仕様は現状を許容しています。Detective演出の繰り返しは今後の記事で観察する事項とし、今回の改修対象には含めません。

既存の費用上限・実行ルールを守って進めてください。commitを伴う作業は同時に1つだけとしてください。

(ユーザー原文ここまで)

## KPI provenance欄(24節)
- 生成100 clip・ASR結果・費用: `fresh`(DEV Trial経路)。原稿: `reuse`(正式run `coffee_prices__run_fxpw_01` のStd Preview/Comment1〜4、TTSに実際に渡したtext)。P2/R2 Style: `frozen`(前回Trialの逐語、sha検証)。E2E自己確認: No(Trial)。

## Opus台帳更新
該当なし。

## 事前指定Read一覧
1. 前回Trialの実装: `er057_ja_aoede_style_trial_02.py` 全文(短い想定。P2の取得元 `g.D_SPECS["P2"]`、R2本文L28付近、`call_tts_mv`のmodel/voice/language/margin、ASR方式)。`g`のimport先(Grep `^import|^from` → `D_SPECS`定義モジュール)の `D_SPECS["P2"]` 定義行のみRead。
2. 前回Trialの正本記録: `er057_output/ja_aoede_style_trial_02/build_manifest_01.json`(P2/R2のchars・sha256)と、Prompt一覧md(Glob `er057_output/ja_aoede_style_trial_02/*PROMPT*` または `user_test/coffee_ja_style_trial_02/*.md|*.html` 内のStyle全文)。**P2・R2は、この記録のsha256と一致する文字列をそのまま使う**(不一致ならSTOPして報告、推測で補正しない)。
3. ページ生成の前例: `er057_ja_aoede_style_trial_02_build.py` 全文(ページ構成・連結方法・音量処理・ASR表示)。`user_test/coffee_ja_style_trial_02/index.html` 冒頭60行(見た目・注記の書式)。
4. 正式版の生成条件: `er019_family_x_audio_production_runner_01.py` を Grep `SUPPORT_JA|preview|comment_|VOICE_JA|voice_name|language_code|margin|loudness|normalize|slowdown|speaking_rate|a2_` → Std Preview/Comment(SUPPORT_JA role)のTTS呼出パラメータ(model・voice・language_code・margin・後処理[音量正規化・無音trim・減速の有無])を特定し、同一条件を採用(**6%減速はFull Story限定か、Support JAにも適用されるかを必ず確認**し、正式版と同じにする)。関連する共通module(`er006_audio_cost_pilot_02_shared_narration.py`等)はGrepで該当関数のみRead。
5. 正式版の原稿(TTSへ渡した実text): `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/` 配下を Glob `**/a2*/**/*.json` / Grep `"segment_id": "preview"|"comment_1"|"comment_2"|"comment_3"|"comment_4"|tts_text|text_sent` → a2のpreview・comment_1〜4の送信text(sha付き)を特定。`audit/e2e_segment_style_table.json` の該当5 segmentの `style_instruction_id`/`version`/`expected_base_sha`(=Production R2 sha `625826c1…`)も控える。
6. 正式Style profileのR2: `er019_family_x_style_profile_01.py` Grep `SUPPORT_JA|R2` → 定数本文とsha。**前回Trial R2(手順2)とProduction R2のsha一致を確認**。不一致なら両方を報告し、Trialでは「前回Trialの実際のStyle全文」(ユーザー指示)を基準R2として使い、Production版との差分も併記する(STOPは不要、報告事項)。
7. `docs/pm/PM_GOVERNANCE.md` Grep `9-5|Gate 7` → 試聴ページ到達確認(a)〜(m)の該当範囲。

## 事前指定Grep一覧+追記位置・更新位置の手順
- STOPセンチネル: Glob `er057_output/**/STOP*`、root `STOP_ALL`/`STOP_NOTICE*`。存在=開始しない。
- 新規Trial資産(既存を上書きしない): script `er057_ja_support_calm_style_trial_04_gen.py`(生成+ASR+費用)、`er057_ja_support_calm_style_trial_04_build.py`(連結+ページ)、`er057_ja_support_calm_style_trial_04_play_verify.py`(Pages実再生確認、前例 `er057_output/ja_aoede_style_trial_02/play_verify_01.py` を流用)。出力 `er057_output/ja_support_calm_style_trial_04/`(results/asr/cost_actual/build_manifest/PROMPTS_01.md[10仕様のStyle全文+sha+chars]/QUALITY_COMPARISON_01.md/PLAY_EVIDENCE_01.md)。ページ `user_test/coffee_ja_style_trial_04/index.html`+音声(mp3、前例と同形式)。
- 試聴ページ要件(ユーザー指示■試聴ページを全て満たす): 10仕様×Take A/B、P2/R2は「基準」として目立つ表示(背景色・ラベル)、各仕様に「調整内容と狙い」(S1〜S8はユーザー原文の見出し名[例: S1 P2の穏やかな修正版]と1行の狙い)、Take A/Bそれぞれの通し再生(Preview→Comment1→2→3→4、全候補で同一の間[例: 0.6秒無音]・同一の音量処理、ページ上に「試聴用の連結(正式Assemblyではない)」と明記)、各Sectionの個別再生、読み上げ原稿全文、TTSへ渡したStyle全文(省略なし、共通指示を含む最終文字列)、ASR結果(一致率/不一致語、既存JA ASR方式)。別節に「参考: 前回Trial(旧原稿・既存音声)のP2/R2」として前回ページのmp3へのリンク/埋め込み(再生成しない、「旧原稿・既存音声」と明記)。機械評価とユーザー聴感評価の欄を分け、ページ上に「ユーザー試聴前、PASS判定なし」と明記。Blindにしない(候補名表示)。
- SSOT(編集権あり): `DECISION_LOG.md` 直近エントリ(Grep `245cdd6c1|RLCO` 最終出現)の後に本Trialの記録(ユーザー指示原文path・sha、生成条件、費用、Status=TRIAL_GENERATED_USER_LISTENING_PENDING、Production R2は不変)。`OPEN_ITEMS.md` 最終OPEN番号(Grep `OPEN-403`)の次番号で「FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04 | Status=USER_LISTENING_PENDING | 区分=POST_USER_VALIDATION | 内容=基準P2/R2+S1〜S8×2 Take比較、ユーザー選定後に別タスクでProduction反映(現行Production=R2 PRODUCTION_WIRED)」。`docs/pm/REPORT_LEDGER.md` 行追加。`docs/pm/USER_DECISION_REGISTER_01.md` 未回答報告に「#103 Std JA Support Style選定(試聴後)、URL」を追加。`docs/pm/ACTIVE_TASK.md` 固定ヘッダ更新(SJS4追加、他は保持、gitignoreのためaddなし)。
- `CURRENT_SPEC.md`は編集しない。

## 実行コマンド全文
- 事前: `git status --porcelain -- er057_output user_test docs | head -30`、`git log --oneline -2`(HEAD=`245cdd6c1`)、`.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04 --run-dir er057_output/ja_support_calm_style_trial_04`(rc=3なら中止)。
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04_委任_01.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04_委任_01.md_check.json`
- 見積(API 0): `.venv\Scripts\python.exe er057_ja_support_calm_style_trial_04_gen.py --estimate-only --out-dir er057_output/ja_support_calm_style_trial_04`(原稿5 sectionの文字数×10仕様×2 Takeから入力/出力token概算、前回実測比で算出、`COST_ESTIMATE_01.md`へ)。JPY100超見込みなら実行せず報告。
- 生成+ASR: `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er057_ja_support_calm_style_trial_04_gen.py --out-dir er057_output/ja_support_calm_style_trial_04 --takes 2 --budget-jpy 40`(PowerShellは `$env:TTS_EXECUTION_MODE="STANDARD"` を先に設定)。各clipは独立呼出(Take A/Bは同一入力の別呼出、順序はA全件→B全件でも仕様ごとでも可、`take`をresultsに記録)。技術失敗(API error/空音声)のみ1回retry、retry件数を記録。ASRは前回Trialと同じJA ASR方式・モデル。
- 連結+ページ: `.venv\Scripts\python.exe er057_ja_support_calm_style_trial_04_build.py --in-dir er057_output/ja_support_calm_style_trial_04 --page-dir user_test/coffee_ja_style_trial_04`(連結は無音gap固定・音量処理は正式版/前例と同一・全候補同一。通し音声は「試聴用連結」ラベル)。
- secret scan: `.venv\Scripts\python.exe tools/secret_scan_01.py` hits=0。
- commit/push後: `.venv\Scripts\python.exe er057_ja_support_calm_style_trial_04_play_verify.py --url https://shimomura055.github.io/eigo-radio/user_test/coffee_ja_style_trial_04/index.html --out er057_output/ja_support_calm_style_trial_04/play_evidence_01.json`(Pages反映待ち最大10分、HTTP 200・全audio要素再生OK・console error 0)。evidence追加分は2つ目のcommitで可(commitは直列)。

## SSOT追記文
上記Grep手順のとおり(実値で埋める)。

## Git(明示add対象・コミットメッセージ・trailer)
- SSOT編集権: あり(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`は編集しない)。
- 明示add: 新規script 3本、`er057_output/ja_support_calm_style_trial_04/`配下の記録(json/jsonl/md/txt。wavは`.gitignore`準拠で除外、mp3はuser_test側のみ)、`user_test/coffee_ja_style_trial_04/`(index.html+mp3)、`docs/pm/delegation_log/`2件+_check.json、SSOT 2件、`docs/pm/REPORT_LEDGER.md`、`docs/pm/USER_DECISION_REGISTER_01.md`。`RESULT_PACKET_*`・`ACTIVE_TASK.md`・無関係dirtyはaddしない。音声合計>50MBなら事前報告。
- commit message: 「FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04 委任_01: Coffee Std日本語Preview/Comment Style比較Trial(基準P2/R2逐語+S1〜S8、各2 Take、正式原稿・正式TTS条件、DEV経路、試聴ページ coffee_ja_style_trial_04)+ASR+費用記録。Production不変、ユーザー選定待ち」
- push: `work/post-merge-01`でcommit → `C:\Users\tensh\eigo-radio-crbn`で `git pull --ff-only origin main; git merge --ff-only work/post-merge-01; git push origin main` → 主dirで `git merge --ff-only origin/main`。conflictは停止して報告。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_SJS4_1.md`(20行程度):
1. T-0 2行(委任文保存/check結果、ユーザー原文path・文字数・sha256)。
2. **試聴ページURL**(HTTP 200時刻、実再生結果)。
3. 揃い: 10仕様×2 Take×5 section=100 clipの生成成否(欠落・retry件数)。
4. P2/R2の逐語検証: 取得元file:line、chars・sha256、前回Trial記録との一致、Production R2(sha 625826c1…)との一致/差分。
5. S1〜S8の最終Style全文の所在(`PROMPTS_01.md`)と共通指示の付加方法(区切り・順序)、P2/R2に未付加の確認。
6. 生成条件(model/voice/language_code/margin/後処理/減速の有無=正式版と同一であることのfile:line根拠)、原稿5 sectionのsha(正式版送信textとの一致)。
7. ASR結果要約(仕様×Take別の一致率・不一致clip一覧)。機械評価のみ、ユーザー評価欄は空。
8. 費用: 見積(COST_ESTIMATE_01)と実測(cost_actual_01.json: TTS/ASR別、token、retry分)、本日(2026-10-17 JST)累計。
9. 前回P2/R2音声の参考掲載方法(「旧原稿・既存音声」表記の確認)。
10. SSOT追記位置(file:line)、OPEN番号、REGISTER #103。
11. commit hash・push・raw URL一覧。
12. 4行(①既存仕様整合[file:line] ②Production到達経路の未承認機能既定値=変更なし ③最終成果物path・目的適合 ④撤去・残置=なし)。
13. `判定整合: 重大NG=[…|なし] / 主因= / 是正対象= / STOP理由= / 提示=…`。
14. 判断候補(=ユーザーの試聴選定のみ。他は作らない)。

## Fable自己チェック(送信前)
- [x] Read一覧に行範囲/Grepパターンあり [x] 追記位置手順あり [x] コマンドに引数実値あり [x] 禁止事項・費用上限(JPY40 Guardrail、7-7 100円判定)あり [x] 並行衝突回避(commit単独)あり [x] Opus Gate判定(非該当)あり [x] 時間見込み・並列化判断あり [x] 新規委任
