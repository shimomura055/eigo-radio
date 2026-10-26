## 管理ID

TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01Z(Family Z担当。並行で委任_01X[Family X+共通核]・委任_01Y[Family Y]が同時に走る。あなたはFamily Zの全音声部位について、呼出し経路・引数・到達性・runtime evidence・承認記録を担当。共通核[`er003_v1_n3_01_tts_generate.py`/`er020_*`/`er011_*`等]の正本記述はX Agentが書くので、あなたは「Zがどの共通関数をどの引数で呼び、その結果LR/Fallbackが有効か無効か」と、Z固有の文脈・感情付きTTS+Fallback(FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01、PRODUCTION_WIRED 2026-10-26)の正確なフローを書く)。並行タスク衝突確認: 並行Agent 4件(委任_01X、委任_01Y、PM-SSOT-SYNC-04[SSOT編集中]、KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01)。あなたの所有ファイル=`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/FAMILY_Z_01.md`、`family_z_01.json`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Z.md`(+check.json)、`docs/pm/RESULT_PACKET_TRA1Z.md`。これ以外は作成・編集しない(`_USER.md`はX Agentが作る。SSOT編集権なし。コード編集禁止)。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: **read-only調査・比較・問題整理**。到達上限Status=調査完了(AUDITED)。Production変更・新規Trial・有料API実行・音声生成は**禁止**(API 0、JPY0)。
- 禁止: コード・Prompt・SSOT・run dirの編集、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。**推測による理由付け禁止**: 根拠(ファイル:行・文書・commit)が見つからない場合は「理由不明・記録なし」と書く。技術的見解は「所見(事実ではない)」欄に分離する。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(調査のみ)。
- 修正範囲の線引き(11-8): 本委任は修正なし。不一致は分類B/Cとして報告のみ。
- 時間見込み: 全体約1.5〜2h(Z音声構成・呼出し経路40分/FZ ctxフロー+J-1判断の根拠照合30分/承認記録・runtime evidence 30分/文書化20分)。並列化: X/Yは別Agent。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Z.md` をN=651から順に試し、先頭が「## 管理ID」+「TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01Z」で始まるものを採用(同時刻に01X/01Yも送られているため先頭一致を必ず確認。`--index -1`不可)。

## ユーザー指示(原文・要点。全文はX Agentが`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md`へ保存する。作成済みならそれを読む。未作成なら以下の要点で作業し、報告前に再確認)

- 目的: 「Family Zの文脈・感情付きTTS Production Wiring報告で、3回NG後にLocal Rewriteを行わずHuman Review／STOPへ進むことが判明した。一方、Family X等にはLocal Rewriteが存在しており、Family・音声部位によって処理が異なる。」XYZ全体で(1)どの音声部位にLRが適用されているか、(2)Rewriteの契機・条件、(3)Rewriteがない場合の理由(**承認済みの意図的な差異なのか、未実装なのか**)、(4)TTS Retry・Fallbackの仕様と発動順序・条件、(5)HR/STOPへ進む条件、(6)承認済み仕様と正式Production実装の一致・不一致。**推測による理由付け禁止。根拠がなければ「理由不明・記録なし」**。
- 対象: 正式Productionで音声化される**すべての部位**(Z例: 地の文、登場人物のセリフ、Key Phrase等。例示なので実際の構成を確認して完全一覧)。Std/Advで異なれば分ける。共通生成関数の差異を省略しない。
- 星取表①列: Family|レベル|音声部位|通常TTS上限|Retry条件|Fallback有無・種類|Rewrite有無|Rewrite発動条件|最終NG時|仕様・実装一致。必ず確認: TTS試行上限と技術エラー再試行の扱い/Retry発動の具体条件(ASR NG・発音NG・内容不一致・無音/異常音声)/Primary・Secondary ASRとの関係/同一Styleで再試行かStyle・モデル・音声設定が切替わるか/Fallbackが何回目にどの条件で発動し何から何へ切替わるか/Fallback後もNGなら何が起こるか/LR発動条件/Rewrite後の再TTS回数と検査/HR・STOPへ進む条件/HR Lock・retry・regeneration・resume時の扱い。「3回NG」は通常/Fallback含む/Rewrite後含むを区別。
- 星取表②列: Family|音声部位|Rewrite|不適用・例外の理由|ユーザー承認の有無|根拠資料|分類。理由区分: ユーザーが明示不採用/品質保護等で承認済み仕様として対象外/実装当時の技術的制約/共通仕様の適用漏れ・配線漏れ/設計・承認記録に理由なし。**「セリフだから書き換えられない」「原作保護のため」といった説明は、実際の設計・承認根拠が存在する場合だけ、既存の決定理由として記載**。新解釈は別欄。
- §5 発動フロー(部位ごと: 通常TTS①→②→Fallback③→LR→書換え後TTS+ASR→HR/STOP のような形式で現行の正確なフロー)。同名Fallbackでも目的・動作が違えば区別。
- §6 照合先: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/PM_GOVERNANCE/過去承認・不採用記録/LR関連Trial・設計・Opus/Fableレビュー/正式コード/retry・fallback・regeneration・resume経路/runtime evidence/Git履歴。**特に2026-10-19のLR発動条件に関するユーザー決定、および今回のFamily Z文脈・感情付きTTSの正式採用内容と照合**。共通仕様とFamily・部位固有仕様を分類、古いルールの残存・矛盾を確認。コードの存在だけでPRODUCTION_WIREDと判断せず、正式経路の到達性と既存runtime evidenceを確認、実走証拠がなければ未検証と明記。
- §7 分類: A=承認済みの合理的差異(根拠あり・一致・現状維持)/B=承認済み仕様との不一致(配線漏れ・不具合・古いルール残存。修正せず原因と解決方針)/C=未承認・根拠不明(ユーザー判断事項を整理)。重要度・品質リスク・量産コスト・Delivery影響を併記。
- §8: 有料Trial・音声生成なし、read-only、Family別並列、曖昧さを残さず掘り下げ、新仕様無断採用・Production修正禁止、OPEN反映候補は既存記録との重複確認。
- 完成条件: 星取表を見れば各部位について「何回失敗すると、何が起こり、なぜそうなっているのか」が分かること。○×列挙で終わらない。

## 固定用語・判定基準(X/Y/Z Agent共通。統合時の突合のため必ずこの語で書く)

- **通常TTS上限**: 同一設定(Style/モデル/Voice/Prompt方式)での最大試行回数。技術エラー(429/5xx/timeout)の再試行が別枠なら「品質NG n回+技術エラー別枠m回」と分けて書く。
- **Retry**: 品質NG(ASR不一致・発音NG・内容不一致・無音/異常音声・Repetition等)を契機とする同一設定での再TTS。契機ごとに判定関数名:行。Primary/Secondary ASRの関係も書く。
- **Fallback**: 設定切替を伴う再TTS。種類ラベル固定: `F-Style`(Style prefix/profile切替)、`F-Model`(TTSモデル/backend切替)、`F-Voice`(Voice切替)、`F-Prompt`(Prompt方式切替。例: Z ctx→legacy)、`F-Tech`(技術エラー救済の再試行)。何回目に・どの条件で・何から何へ。
- **Local Rewrite(LR)**: 本文テキストの局所書換え後に再TTS。発動条件・書換え回数上限・再TTS回数・再検査内容。
- **HR**: Human Review queue登録(ファイル名:行)+Lock(種類)。**STOP**: run停止(STOP file名・解除権限)。両方なら「HR+STOP」。
- **cooldown**: 待機(秒・位置)。
- **仕様・実装一致**判定の語: `一致` / `不一致(B)` / `仕様記録なし(C)` / `runtime証拠なし(未検証)`。runtime証拠は実在pathで示す。
- **分類A/B/C**: ユーザー原文§7の定義どおり。
- **「3回NG」の数え方**: 必ず「通常n+Fallback m+LR後k=総N」の形で書く。
- **事実/所見の分離**: 表の各セルは事実(ファイル:行・文書)のみ。技術的見解・新解釈は`## 所見(事実ではない)`節に分ける。

## Z担当の調査範囲

1. **Family Zの正式Production音声構成の完全一覧**: `er026_family_z_fiction_production_runner_01.py`(stage定義)と`er063_family_z_audio_01.py`(clip plan: narrator地の文[Std chunk経路含む、2026-10-26配線]、dialogue[登場人物セリフ、`er012_b_family_voices_production_01.py`経由、ctx policy]、Key Phrase解説、単語解説、定型音声[タイトル/導入/締め]、日本語音声等)から、Std(a2)/Adv(b1b)で音声化される全部位を列挙し、各部位が呼ぶ生成関数と**渡している引数**(LR関連引数・`attempt_hook`・`prior_generations`・Style prefix・max_attempts等)をファイル:行で特定。
2. **ZにLRが効くか(部位別)**: `er003_v1_n3_01_tts_generate.py:319`付近(summaryに「Z dialogueにLocal Rewrite未配線」の記録あり)とnarrator経路(`generate_a2_segment_with_slowdown`経由。Chunk委任_03のR7「Local Rewrite(再TTS)は減速前段にあり」の記述=narratorにはLRが到達する?)を確認し、部位ごとに「有効/無効(引数未指定)/別関数で非対応」を事実として書く。**特にセリフ(dialogue)にLRが無い理由**: `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/{EXISTING_SPEC_CHECK_01,DESIGN_01,DESIGN_02,OPUS_REVIEW_01,CLOSEOUT_01}.md`のJ-1判断(「LR新設せずHR/STOP直行、ユーザー原文後段を満たす」)の原文と、ユーザー指示原文`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`の該当箇所(「NG既存Local Rewrite→HR/STOP」「最重要目的は…」等)を**逐語引用**し、「ユーザーが明示的に不採用」「承認済み仕様として対象外」「実装当時の技術的制約」「配線漏れ」「記録なし」のどれに該当するかを**根拠付き**で分類。J-1がFable判断(ユーザー承認ではない)であればその事実を明記。
3. **Z固有フロー(FZ ctx)**: `er122_fz_ctx_policy_01.py`・`er122_fz_ctx_notes_01.py`・`er012_b_family_voices_production_01.py`(`attempt_hook`)・`er020_tts_retry_local_rewrite_01.py`(`COOLDOWN_SECONDS=600`/`maybe_cooldown_before_attempt`)・ER-011 cascade(`record_outcome`、3回上限、累積15回)から、セリフの正確なフロー「1回目ctx→NG即時Retry→2回目ctx→NG 10分cooldown→3回目従来方式(F-Prompt)→NG→HR/STOP」を**コード行で裏付け**、「通常n+Fallback m+LR後k=総N」で表記。技術エラー(429/5xx)の扱い(F-Tech)が品質NGの3回と別枠かも確認。runtime evidence=`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/EVIDENCE_01.md`・`RUNTIME_EVIDENCE_E-*.json`(E-1〜E-6)を部位・経路別に対応付け。
4. **Z narrator(地の文)フロー**: Std(chunk別6%減速・ASR再検証・`FamilyZSlowdownGateStop`)/Adv(chunk)/短い地の文(非chunk)の各経路のretry・Fallback・LR・HR/STOP。runtime evidence=`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_Z_01.md`、`docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md`、`docs/research/FZ-TELL-TALE-HEART-*/`。LR経由の実走証拠の有無(委任_03は「強制NG・LR・exhaustのZ Std実runは未取得、offline testのみ」と報告)を明記。
5. **承認記録との照合**: `CURRENT_SPEC.md`のFamily Z節+新節「Family Z セリフTTS 文脈・感情付き方式+Fallback」(Grep `Family Z|er063|セリフTTS|文脈・感情|Local Rewrite|Human Review`)、`DECISION_LOG.md`(Grep `2026-10-19|Local Rewrite|FZ-CONTEXT|OPEN-528|OPEN-516|OPEN-511|J-1`)、`OPEN_ITEMS.md`(Grep `OPEN-528|OPEN-516|OPEN-511|Local Rewrite|Family Z`)、`docs/pm/USER_DECISION_REGISTER_01.md`(Grep `Family Z|Local Rewrite|2026-10-19|OPEN-528`)。**2026-10-19のLR発動条件のユーザー決定**(`DECISION_LOG.md` Grep `2026-10-19`、`docs/pm/delegation_log/2026-10-19_*` Glob)を逐語引用し、Z各部位と照合(特に「既存LR」がZセリフに存在しない状態で、2026-10-19決定がZセリフを対象に含むのか/含まないのかを原文で確認)。
6. **星取表①②のZ行**と**Z部位別フロー**を`FAMILY_Z_01.md`へ。`family_z_01.json`に構造化(keys: family, level, part, generator_fn, call_args, tts_limit, retry_conditions, fallback[type,trigger,from,to], lr[enabled,how_enabled,trigger,max_rewrites,retts,checks], final_ng, cooldown, hr_lock, stop, spec_refs[], runtime_evidence[], match, class, notes_fact, notes_opinion)。
7. 古いルールの残存・矛盾(FZ ctx追加後、既存Z dialogue retry規則・`legacy` policyのrun単位固定・Chunk Std拡張後のnarrator規則)。

## KPI provenance欄

該当なし(調査のみ)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `er063_family_z_audio_01.py`: Grep `def |generate_a2_segment_with_slowdown|generate_|attempt_hook|prior_generations|policy|legacy|fz_ctx|max_attempts|retry|rewrite|cooldown|human_review|STOP|FamilyZSlowdownGateStop|kind ==` → 各±25(全文Read禁止、約2,000行)
- `er026_family_z_fiction_production_runner_01.py`: Grep `def stage_|generate_|cascade|human_review|STOP|RUN_LOCK|budget|retry` → 各±20
- `er122_fz_ctx_policy_01.py` 全文(短い想定。長ければGrep `def |DEFAULT|legacy|state` ±20)
- `er122_fz_ctx_notes_01.py`: Grep `def |STOP|retry|再試行` → ±20
- `er012_b_family_voices_production_01.py:500-560`、Grep `def generate|attempt_hook|max_attempts|fallback|rewrite|cooldown` → ±25
- `er003_v1_n3_01_tts_generate.py:300-340`(:319付近のZ dialogue LR未配線の記述)、Grep `def generate|local_rewrite|rewrite|max_attempts|prior_generations` → シグネチャ±15
- `er020_tts_retry_local_rewrite_01.py`: Grep `def |COOLDOWN_SECONDS|def maybe_cooldown_before_attempt` → シグネチャ±15
- `er011_*cascade*.py`(Glob): Grep `def record_outcome|MAX_|15|human_review_queue` → ±20
- `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/EXISTING_SPEC_CHECK_01.md` 全文、`DESIGN_02.md`: Grep `J-1|Local Rewrite|cooldown|HR|STOP|M-7` → ±20、`OPUS_REVIEW_01.md`: Grep `Local Rewrite|J-1|HR` → ±10、`CLOSEOUT_01.md`: Grep `Local Rewrite|J-1|Deferred` → ±10、`EVIDENCE_01.md:1-80`
- `docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`: Grep `Local Rewrite|HR|STOP|最重要|3回|cooldown|10分` → ±5(逐語引用用)
- `CURRENT_SPEC.md`: Grep `Family Z|er063|セリフTTS|文脈・感情|Local Rewrite|Human Review` → 該当行±10のみ(全文読込禁止)
- `DECISION_LOG.md`: Grep `2026-10-19|Local Rewrite|FZ-CONTEXT|OPEN-528|OPEN-516|OPEN-511` → 該当行±10
- `OPEN_ITEMS.md`: Grep `OPEN-528|OPEN-516|OPEN-511|Local Rewrite|Family Z` → 該当行のみ
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `Family Z|Local Rewrite|2026-10-19|OPEN-528` → ±5

## 事前指定Grep一覧+追記位置・更新位置の手順

- Glob `docs/research/FZ-*/**/*.md`、`docs/research/*LOCAL-REWRITE*/**` → Grep `Local Rewrite|Human Review|retry|fallback|セリフ|dialogue` → 関連箇所を「参照文書」に列挙
- Glob `docs/pm/delegation_log/2026-10-19_*` → LR決定の原文特定
- `er011_output/attempt_history.jsonl`: Grep `family_z|er063|melos|tell_tale|monkey` → 件数と代表行のみ(全文Read禁止)
- `git log --oneline --since=2026-10-01 -- er063_family_z_audio_01.py er012_b_family_voices_production_01.py er122_fz_ctx_policy_01.py er122_fz_ctx_notes_01.py`
- 成果物は`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/`配下(dirが無ければ作成。X/Y Agentも同dirに別名ファイルを作るので自分のファイル名以外は作らない)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Z.md --json-out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Z.md_check.json`
- `git log --oneline --since=2026-10-01 -- er063_family_z_audio_01.py er012_b_family_voices_production_01.py er122_fz_ctx_policy_01.py er122_fz_ctx_notes_01.py`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。OPEN起票候補(重複確認済み。既存OPEN-528 Deferred「Zセリフ用LR新設要否」との重複に注意)を`RESULT_PACKET_TRA1Z.md`(9)に文案として記載。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/FAMILY_Z_01.md`、`family_z_01.json`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01Z.md`、`..._01Z.md_check.json`。RESULT_PACKETはaddしない。
- commit message: `TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01Z: Family ZのRetry/Fallback/Local Rewrite/HR仕様棚卸し(セリフctx+Fallback・地の文chunk経路、read-only、API 0)`
- trailer: `Delegation: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/01Z`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_TRA1Z.md`: (0)T-0結果・index、(1)Z音声部位の完全一覧(Std/Adv別、生成関数:行、呼出し引数)、(2)星取表①Z行(全部位)、(3)星取表②Z行(セリフのLR不適用理由は根拠逐語引用付き・分類)、(4)Z部位別フロー(§5形式、「通常n+Fallback m+LR後k=総N」表記、F-Prompt/F-Tech等のラベル付き)、(5)ZでLRが有効/無効になる仕組み(事実)、(6)2026-10-19決定とFZ正式採用内容の逐語引用と照合結果、(7)runtime evidence有無表(E-1〜E-6対応、LR経路の未検証を明記)、(8)発見した不一致・理由不明箇所(分類A/B/C、重要度・品質リスク・単価・Delivery影響)、(9)OPEN起票候補文案(重複確認結果付き)、(10)所見(事実ではない)、(11)RESULT_PACKET必須4行(既存仕様整合/未承認機能の既定値=該当なし/失敗終了時の最終成果物/撤去・残置=なし)+「判定整合: 重大NG=<なし|あり>」1行、(12)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。ユーザー判断候補は`判断候補`表記。