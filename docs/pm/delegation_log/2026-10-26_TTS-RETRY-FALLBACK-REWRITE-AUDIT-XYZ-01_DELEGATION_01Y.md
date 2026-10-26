## 管理ID

TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01Y(Family Y担当。並行で委任_01X[Family X+共通核]・委任_01Z[Family Z]が同時に走る。あなたはFamily Yの全音声部位について、呼出し経路・引数・到達性・runtime evidence・承認記録を担当。共通核[`er003_v1_n3_01_tts_generate.py`/`er020_*`/`er011_*`等]の正本記述はX Agentが書くので、あなたは「Yがどの共通関数をどの引数で呼び、その結果LR/Fallbackが有効か無効か」を書く)。並行タスク衝突確認: 並行Agent 4件(委任_01X、委任_01Z、PM-SSOT-SYNC-04[SSOT編集中]、KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01)。あなたの所有ファイル=`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/FAMILY_Y_01.md`、`family_y_01.json`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Y.md`(+check.json)、`docs/pm/RESULT_PACKET_TRA1Y.md`。これ以外は作成・編集しない(`_USER.md`はX Agentが作る。SSOT編集権なし。コード編集禁止)。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: **read-only調査・比較・問題整理**。到達上限Status=調査完了(AUDITED)。Production変更・新規Trial・有料API実行・音声生成は**禁止**(API 0、JPY0)。
- 禁止: コード・Prompt・SSOT・run dirの編集、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。**推測による理由付け禁止**: 根拠(ファイル:行・文書・commit)が見つからない場合は「理由不明・記録なし」と書く。技術的見解は「所見(事実ではない)」欄に分離する。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(調査のみ)。
- 修正範囲の線引き(11-8): 本委任は修正なし。不一致は分類B/Cとして報告のみ。
- 時間見込み: 全体約1.5h(Y音声構成・呼出し経路40分/承認記録・runtime evidence照合30分/文書化20分)。並列化: X/Zは別Agent。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Y.md` をN=651から順に試し、先頭が「## 管理ID」+「TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01Y」で始まるものを採用(同時刻に01X/01Zも送られているため先頭一致を必ず確認。`--index -1`不可)。

## ユーザー指示(原文・要点。全文はX Agentが`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md`へ保存する。作成済みならそれを読む。未作成なら以下の要点で作業し、報告前に再確認)

- 目的: XYZ全体で(1)どの音声部位にLocal Rewriteが適用されているか、(2)Rewriteの契機・条件、(3)Rewriteがない場合の理由(承認済みの意図的差異か未実装か)、(4)TTS Retry・Fallbackの仕様と発動順序・条件、(5)HR/STOPへ進む条件、(6)承認済み仕様と正式Production実装の一致・不一致。**推測による理由付け禁止。根拠がなければ「理由不明・記録なし」**。
- 対象: 正式Productionで音声化される**すべての部位**(Y例: Lead、Voice 1〜3、Tension+Closing、Key Phrase等。例示なので実際の構成を確認して完全一覧)。Std/Advで異なれば分ける。共通生成関数の差異を省略しない。
- 星取表①列: Family|レベル|音声部位|通常TTS上限|Retry条件|Fallback有無・種類|Rewrite有無|Rewrite発動条件|最終NG時|仕様・実装一致。必ず確認: TTS試行上限と技術エラー再試行の扱い/Retry発動の具体条件(ASR NG・発音NG・内容不一致・無音/異常音声)/Primary・Secondary ASRとの関係/同一Styleで再試行かStyle・モデル・音声設定が切替わるか/Fallbackが何回目にどの条件で発動し何から何へ切替わるか/Fallback後もNGなら何が起こるか/LR発動条件/Rewrite後の再TTS回数と検査/HR・STOPへ進む条件/HR Lock・retry・regeneration・resume時の扱い。「3回NG」は通常/Fallback含む/Rewrite後含むを区別。
- 星取表②列: Family|音声部位|Rewrite|不適用・例外の理由|ユーザー承認の有無|根拠資料|分類。理由区分: ユーザーが明示不採用/品質保護等で承認済み仕様として対象外/実装当時の技術的制約/共通仕様の適用漏れ・配線漏れ/設計・承認記録に理由なし。「セリフだから」等の説明は実際の設計・承認根拠がある場合だけ記載。新解釈は別欄。
- §5 発動フロー(部位ごと: 通常TTS①→②→Fallback③→LR→書換え後TTS+ASR→HR/STOP のような形式で現行の正確なフロー)。同名Fallbackでも目的・動作が違えば区別。
- §6 照合先: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/PM_GOVERNANCE/過去承認・不採用記録/LR関連Trial・設計・Opus/Fableレビュー/正式コード/retry・fallback・regeneration・resume経路/runtime evidence/Git履歴。**特に2026-10-19のLR発動条件に関するユーザー決定**とZ ctx正式採用内容と照合。共通仕様とFamily・部位固有仕様を分類、古いルールの残存・矛盾を確認。コードの存在だけでPRODUCTION_WIREDと判断せず、正式経路の到達性と既存runtime evidenceを確認、実走証拠がなければ未検証と明記。
- §7 分類: A=承認済みの合理的差異(根拠あり・一致・現状維持)/B=承認済み仕様との不一致(配線漏れ・不具合・古いルール残存。修正せず原因と解決方針)/C=未承認・根拠不明(ユーザー判断事項を整理)。重要度・品質リスク・量産コスト・Delivery影響を併記。
- §8: 有料Trial・音声生成なし、read-only、Family別並列、曖昧さを残さず掘り下げ、新仕様無断採用・Production修正禁止、OPEN反映候補は既存記録との重複確認。
- 完成条件: 星取表を見れば各部位について「何回失敗すると、何が起こり、なぜそうなっているのか」が分かること。○×列挙で終わらない。

## 固定用語・判定基準(X/Y/Z Agent共通。統合時の突合のため必ずこの語で書く)

- **通常TTS上限**: 同一設定(Style/モデル/Voice/Prompt方式)での最大試行回数。技術エラー(429/5xx/timeout)の再試行が別枠なら「品質NG n回+技術エラー別枠m回」と分けて書く。
- **Retry**: 品質NG(ASR不一致・発音NG・内容不一致・無音/異常音声・Repetition等)を契機とする同一設定での再TTS。契機ごとに判定関数名:行。Primary/Secondary ASRの関係も書く。
- **Fallback**: 設定切替を伴う再TTS。種類ラベル固定: `F-Style`(Style prefix/profile切替)、`F-Model`(TTSモデル/backend切替)、`F-Voice`(Voice切替)、`F-Prompt`(Prompt方式切替)、`F-Tech`(技術エラー救済の再試行)。何回目に・どの条件で・何から何へ。
- **Local Rewrite(LR)**: 本文テキストの局所書換え後に再TTS。発動条件・書換え回数上限・再TTS回数・再検査内容。
- **HR**: Human Review queue登録(ファイル名:行)+Lock(種類)。**STOP**: run停止(STOP file名・解除権限)。両方なら「HR+STOP」。
- **cooldown**: 待機(秒・位置)。
- **仕様・実装一致**判定の語: `一致` / `不一致(B)` / `仕様記録なし(C)` / `runtime証拠なし(未検証)`。runtime証拠は実在pathで示す。
- **分類A/B/C**: ユーザー原文§7の定義どおり。
- **「3回NG」の数え方**: 必ず「通常n+Fallback m+LR後k=総N」の形で書く。
- **事実/所見の分離**: 表の各セルは事実(ファイル:行・文書)のみ。技術的見解・新解釈は`## 所見(事実ではない)`節に分ける。

## Y担当の調査範囲

1. **Family Yの正式Production音声構成の完全一覧**: `er121_family_y_runner_01.py`(stage定義、`stage_tts`、`write_level_inputs`)と`er121_family_y_structure_01.py`(5段落契約: Lead/Voice 1〜3/Tension+Closing等)、`er121_family_y_audio_01.py`(segment→生成関数の呼出し、Std減速、chunk経路`_load_y_body_chunks`)から、Std(a2)/Adv(b1b)で音声化される全部位(Lead、Voice 1〜3本文、Voice紹介行、Tension+Closing、Key Phrase解説、単語解説、定型音声、日本語音声等)を列挙し、各部位が呼ぶ生成関数(`er003_v1_n3_01_tts_generate.py`のどの関数か、`er012_b_family_voices_production_01.py`経由か、KP解説経路か)と**渡している引数**(LR関連引数・`attempt_hook`・`prior_generations`・Style prefix・max_attempts等)をファイル:行で特定。
2. **YにLRが効くか**: 共通関数側にLR機構がある場合、Yの呼出しでそれが有効になる条件(引数・flag・別関数)を確認し、「有効/無効(引数未指定)/別関数で非対応」を事実として書く。
3. **Y固有のretry規則**: `er121_*`内の独自retryループ・固定回数定数・Repetition QA(Voice 1 Algiebaで旗率72%が観測されたQA)・「最終attempt前10分cooldown」(summaryに記録あり。実装箇所をGrep `cooldown|600`)・Fallback(Style/Voice/モデル切替の有無)・HR/STOP条件(HR queue登録先・Lock・`FAMILY-Y`固有STOP)。
4. **承認記録との照合**: `CURRENT_SPEC.md`のFamily Y節(Grep `Family Y|Y Voice|er121`)、`DECISION_LOG.md`(Grep `Family Y|FAMILY-Y|Local Rewrite|2026-10-19`)、`OPEN_ITEMS.md`(Grep `OPEN-484|OPEN-527|OPEN-531|Family Y`)、`docs/research/FAMILY-Y-*/`配下の設計・Opusレビュー(Glob、Grep `Local Rewrite|retry|fallback|Human Review`)、`docs/pm/USER_DECISION_REGISTER_01.md`(Grep `Family Y|Local Rewrite`)。**2026-10-19のLR発動条件のユーザー決定**(`DECISION_LOG.md` Grep `2026-10-19`、`docs/pm/delegation_log/2026-10-19_*` Glob)を逐語引用し、Y各部位と照合。
5. **Y runtime evidence**: `er121_output/family_y_production_01/**/audit/`、`er011_output/attempt_history.jsonl`のY由来行(Grep `family_y|er121`、件数と代表行のみ)、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`のY由来行(+2件がY Trial由来と記録あり)、`docs/research/FAMILY-Y-*/**/RUNTIME_EVIDENCE*|EVIDENCE*|RESULT*`で、部位ごとに「retry/Fallback/LR/HRの実走証拠あり(path)/なし(未検証)」。
6. **星取表①②のY行**と**Y部位別フロー**(§5形式)を`FAMILY_Y_01.md`へ。`family_y_01.json`に構造化(keys: family, level, part, generator_fn, call_args, tts_limit, retry_conditions, fallback[type,trigger,from,to], lr[enabled,how_enabled,trigger,max_rewrites,retts,checks], final_ng, cooldown, hr_lock, stop, spec_refs[], runtime_evidence[], match, class, notes_fact, notes_opinion)。
7. 古いルールの残存・矛盾(Chunk Std拡張 2026-10-26後のY経路、Y Voice Trialで観測された規則との差)。

## KPI provenance欄

該当なし(調査のみ)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `er121_family_y_runner_01.py`: Grep `def stage_|write_level_inputs|generate_|cascade|human_review|STOP|RUN_LOCK|budget|retry|cooldown` → 各±25
- `er121_family_y_structure_01.py:100-200`(段落契約・segment定義)
- `er121_family_y_audio_01.py`: Grep `def |generate_a2_segment_with_slowdown|generate_|attempt_hook|prior_generations|style|max_attempts|retry|rewrite|cooldown|600|repetition|human_review|STOP` → 各±25(全文Read禁止)
- `er003_v1_n3_01_tts_generate.py`: Grep `def generate|local_rewrite|rewrite|max_attempts|attempt_hook|prior_generations` → defシグネチャ±15のみ(詳細正本はX Agent)
- `er020_tts_retry_local_rewrite_01.py`: Grep `def ` → シグネチャ一覧のみ(どの入口からLRが呼ばれるかの確認用)
- `er012_b_family_voices_production_01.py`: Grep `def generate|attempt_hook|max_attempts|fallback|rewrite` → ±20
- `CURRENT_SPEC.md`: Grep `Family Y|er121|Y Voice|Local Rewrite|Human Review` → 該当行±10のみ(全文読込禁止)
- `DECISION_LOG.md`: Grep `2026-10-19|Local Rewrite|Family Y|FAMILY-Y` → 該当行±10
- `OPEN_ITEMS.md`: Grep `OPEN-484|OPEN-527|OPEN-531|Family Y|Local Rewrite` → 該当行のみ
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `Family Y|Local Rewrite|2026-10-19` → 該当行±5
- `docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/DESIGN_01.md`、`docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/DESIGN_01.md`: Grep `retry|fallback|Repetition|cooldown|Production.*規則` → ±10(Production retry規則の記述と実装の突合)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Glob `docs/research/FAMILY-Y-*/**/*.md` → Grep `Local Rewrite|Human Review|retry|fallback` → 関連箇所を「参照文書」に列挙
- Glob `docs/pm/delegation_log/2026-10-19_*` → LR決定の原文特定
- `git log --oneline --since=2026-10-01 -- er121_family_y_audio_01.py er121_family_y_runner_01.py`
- 成果物は`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/`配下(dirが無ければ作成。X/Z Agentも同dirに別名ファイルを作るので自分のファイル名以外は作らない)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Y.md --json-out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Y.md_check.json`
- `git log --oneline --since=2026-10-01 -- er121_family_y_audio_01.py er121_family_y_runner_01.py`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。OPEN起票候補(重複確認済み)を`RESULT_PACKET_TRA1Y.md`(9)に文案として記載。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/FAMILY_Y_01.md`、`family_y_01.json`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Y.md`、`..._01Y.md_check.json`。RESULT_PACKETはaddしない。
- commit message: `TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01Y: Family YのRetry/Fallback/Local Rewrite/HR仕様棚卸し(read-only、API 0)`
- trailer: `Delegation: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/01Y`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_TRA1Y.md`: (0)T-0結果・index、(1)Y音声部位の完全一覧(Std/Adv別、生成関数:行、呼出し引数)、(2)星取表①Y行(全部位)、(3)星取表②Y行、(4)Y部位別フロー(§5形式、「通常n+Fallback m+LR後k=総N」表記)、(5)YでLRが有効/無効になる仕組み(事実)、(6)2026-10-19決定の逐語引用と照合結果、(7)runtime evidence有無表、(8)発見した不一致・理由不明箇所(分類A/B/C、重要度・品質リスク・単価・Delivery影響)、(9)OPEN起票候補文案(重複確認結果付き)、(10)所見(事実ではない)、(11)RESULT_PACKET必須4行(既存仕様整合/未承認機能の既定値=該当なし/失敗終了時の最終成果物/撤去・残置=なし)+「判定整合: 重大NG=<なし|あり>」1行、(12)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。ユーザー判断候補は`判断候補`表記。