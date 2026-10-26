## 管理ID

TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01X(Family X担当。並行で委任_01Y[Family Y]・委任_01Z[Family Z]が同時に走る。あなたはFamily Xの全音声部位+共通核[X/Y/Zが共用する生成・retry・cascade・HR関数]の記述を担当)。並行タスク衝突確認: 並行Agent 4件(委任_01Y、委任_01Z、PM-SSOT-SYNC-04[SSOT編集中]、KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01[`er124_*`/`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/`])。あなたの所有ファイル=`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/FAMILY_X_01.md`、`family_x_01.json`、`COMMON_CORE_01.md`、`common_core_01.json`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_{USER,DELEGATION_01X}.md`(+check.json)、`docs/pm/RESULT_PACKET_TRA1X.md`。これ以外は作成・編集しない(SSOT編集権なし。コード編集禁止)。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: **read-only調査・比較・問題整理**。到達上限Status=調査完了(AUDITED)。Production変更・新規Trial・有料API実行・音声生成は**禁止**(API 0、JPY0)。
- 禁止: コード・Prompt・SSOT・run dirの編集、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。**推測による理由付け禁止**: 根拠(ファイル:行・文書・commit)が見つからない場合は「理由不明・記録なし」と書く。Claude/Sonnetの技術的見解は必ず「所見(事実ではない)」欄に分離する。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(調査のみ。統合後にFableが任意レビューを判断)。
- 修正範囲の線引き(11-8): 本委任は修正なし。発見した不一致は分類B/Cとして報告のみ。
- 時間見込み: 全体約2h(共通核の読解50分/X部位別の到達経路確認40分/SSOT・履歴照合20分/文書化10分)。並列化: Family Y/Zは別Agentで並列。共通核はあなたが正本を書き、Y/Z Agentは自Familyの呼出し方のみを書く(統合はFableが後続委任で実施)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01X.md` をN=651から順に試し、先頭が「## 管理ID」+「TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01X」で始まるものを採用(同時刻に01Y/01Zも送られているため先頭一致を必ず確認。`--index -1`不可)。ユーザー指示原文(下記)を`..._USER.md`へ逐語保存(**X担当のあなたのみ**が_USER.mdを作成。Y/Zは作成しない)。

## ユーザー指示(原文)

# 【調査指示】Family XYZ共通｜TTS Retry・Fallback・Local Rewrite・Human Review仕様の全体棚卸し

**管理対象：Family X／Y／Z、Standard／Advanced**
**Scope：調査・比較・問題整理のみ。Production変更・新規Trial・有料API実行なし。**

## 1. 目的

Family Zの文脈・感情付きTTS Production Wiring報告で、3回NG後にLocal Rewriteを行わずHuman Review／STOPへ進むことが判明した。

一方、Family X等にはLocal Rewriteが存在しており、Family・音声部位によって処理が異なる。

今回、XYZ全体について以下を整理する。

1. どの音声部位にLocal Rewriteが適用されているか。
2. Rewriteがある場合、**何を契機に、どの条件で発動するのか**。
3. Rewriteがない場合、**なぜないのか。承認済みの意図的な差異なのか、未実装なのか**。
4. TTS Retry・Fallbackの仕様と、その発動順序・条件。
5. 最終的にHuman Review／STOPへ進む条件。
6. 承認済み仕様と正式Production実装の一致・不一致。

**推測による理由付けは禁止。根拠が見つからない場合は「理由不明・記録なし」と明記する。**

## 2. 対象範囲

Family X／Y／Zの正式Productionで音声化されるすべての部位を対象とする。

例：

- Family X：本文、Comment、In One Line、Key Phrase等
- Family Y：Lead、Voice 1〜3、Tension＋Closing、Key Phrase等
- Family Z：地の文、登場人物のセリフ、Key Phrase等

上記は例示であり、実際のProduction音声構成を確認して完全な一覧を作成すること。

Standard／Advancedで処理が異なる場合は分けて記載する。

特に、本文、セリフ、Key Phrase、短い定型音声等で共通生成関数が異なる場合、その差異を省略しない。

## 3. 星取表①：Family別・音声部位別の全体比較

以下の形式で一覧化する。

| Family | レベル | 音声部位 | 通常TTS上限 | Retry条件 | Fallback有無・種類 | Rewrite有無 | Rewrite発動条件 | 最終NG時 | 仕様・実装一致 |
|---|---|---|---|---|---|---|---|---|---|
| X | Std/Adv | 本文 | 実態 | 実態 | 実態 | ○/× | 条件 | HR/STOP等 | 判定 |
| Y | Std/Adv | Voice | 実態 | 実態 | 実態 | ○/× | 条件 | HR/STOP等 | 判定 |
| Z | Std/Adv | セリフ | 実態 | 実態 | 実態 | ○/× | 条件 | HR/STOP等 | 判定 |

この表を全音声部位について埋めること。

**必ず確認する事項**

- TTS試行上限と、技術エラーによる再試行の扱い
- ASR NG、発音NG、内容不一致、無音・異常音声など、Retryを発動する具体的条件
- Primary／Secondary ASRの判定との関係
- 同じStyleで再試行するのか、Style・モデル・音声設定が切り替わるのか
- Fallbackが何回目に、どの条件で発動するのか
- Fallback後もNGの場合に何が起こるか
- Local Rewriteの発動条件
- Rewrite後の再TTS回数と検査内容
- Human Review／STOPへ進む条件
- Human Review Lock・retry・regeneration・resume時の扱い

「3回NG」と表現する場合も、通常TTSの3回なのか、Fallbackを含む3回なのか、Rewrite後の試行を含むのかを区別すること。

**Fallbackは単なる有無ではなく、何から何へ切り替える方式なのかを明記する。**

## 4. 星取表②：Local Rewriteの適用有無と理由

特にRewriteがない部位を重点的に調査する。

| Family | 音声部位 | Rewrite | 不適用・例外の理由 | ユーザー承認の有無 | 根拠資料 | 分類 |
|---|---|---|---|---|---|---|
| X | 部位名 | ○/× | 記録に基づく理由 | 有/無/不明 | 文書・該当箇所 | A/B/C |
| Y | 部位名 | ○/× | 同上 | 同上 | 同上 | 同上 |
| Z | 部位名 | ○/× | 同上 | 同上 | 同上 | 同上 |

理由は次のように区別する。

- ユーザーが明示的にRewriteを不採用とした。
- 品質保護などの理由で、承認済み仕様として対象外にしている。
- 実装当時の技術的制約から未対応となっている。
- 共通仕様の適用漏れ・Production配線漏れ。
- 設計・承認記録に理由が存在しない。

「セリフだから書き換えられない」「原作保護のため」といった説明は、**実際の設計・承認根拠が存在する場合だけ、既存の決定理由として記載すること**。

Claude/Fableの新たな解釈や技術的見解は、事実・承認済み仕様とは別欄に区別する。

## 5. 発動フローの明示

Family・音声部位ごとに、以下のような形式で実際の処理順序を示す。

**記載例（正式仕様を意味しない）**

通常TTS①
→ NGなら通常TTS②
→ NGならFallback TTS③
→ NGならLocal Rewrite
→ 書換え後TTS＋ASR
→ NGならHuman Review／STOP

実際には各Family・部位について、現行の正確なフローを記載すること。

共通するフローはまとめてよいが、差異がある箇所を省略しない。

また、同じ「Fallback」という名称でも、Style変更、モデル変更、技術エラー救済など目的や動作が異なる場合は区別する。

## 6. 承認済み仕様・過去経緯との照合

以下を確認する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- PM_GOVERNANCE
- 過去のユーザー承認・不採用記録
- 過去のLocal Rewrite関連Trial・設計・Opus/Fableレビュー
- 正式Productionコード
- retry／fallback／regeneration／resume経路
- Production runtime evidence
- Git変更履歴

特に、2026-10-19のLocal Rewrite発動条件に関するユーザー決定、および今回のFamily Z文脈・感情付きTTSの正式採用内容と照合すること。

「共通仕様」と「Family・部位固有仕様」を分類し、後から追加した仕様によって古いルールが残存・矛盾していないかも確認する。

コードの存在だけでPRODUCTION_WIREDと判断しない。正式経路の到達性と既存runtime evidenceを確認し、実走証拠のないものは未検証と明記する。

## 7. 差異・問題の分類

発見した違いを次の3種類に分類する。

**A：承認済みの合理的な差異**

- ユーザー承認または正式仕様の根拠あり
- 実装が仕様と一致
- 原則として現状維持

**B：承認済み仕様との不一致**

- 配線漏れ、不具合、古いルールの残存等
- 修正の必要性と影響範囲を明示
- 今回は修正せず、原因と解決方針を報告

**C：未承認・根拠不明の差異**

- 実装上は異なるが、承認された理由が見つからない
- 意図的な例外かどうか判断できない
- 必要なユーザー判断事項を整理

問題の重要度・品質リスク・量産コスト・Deliveryへの影響も併記すること。

## 8. 調査・報告の進め方

- 追加の有料Trialや音声生成は実施しない。
- 既存コード・SSOT・Git・runtime evidenceを使ったread-only調査とする。
- 独立したFamily別調査は原則並列化する。
- 情報不足による曖昧さは残さず、確認できるところまで自主的に掘り下げる。
- ただし、新仕様の無断採用やProduction修正は行わない。
- OPEN_ITEMSへの反映が必要な未解決事項は提案し、既存記録との重複を確認する。

## 9. 最終報告の構成

以下の順番で報告すること。

1. **結論：XYZのRewrite／Fallback仕様は整合しているか**
2. 全Family・全音声部位の星取表①
3. Rewrite不適用理由と承認根拠の星取表②
4. Family・部位別の実際の処理フロー
5. 発見した仕様不一致・未配線・理由不明箇所
6. QCD影響と優先順位
7. Fable独立評価
8. 必要なユーザー判断事項（本当に判断が必要なものだけ）

**本調査の完成条件は、ユーザーが星取表を見れば、XYZそれぞれの音声部位について「何回失敗すると、何が起こり、なぜそうなっているのか」を理解できる状態にすること。**

単にRewriteの○×を列挙するだけで終了しないこと。

なお、今回の調査結果を踏まえた仕様統一やProduction改修は、別途ユーザー判断を経て実施する。

(原文ここまで)

## 固定用語・判定基準(X/Y/Z Agent共通。統合時の突合のため必ずこの語で書く)

- **通常TTS上限**: 同一設定(Style/モデル/Voice/Prompt方式)での最大試行回数。技術エラー(429/5xx/timeout)の再試行が別枠なら「品質NG n回+技術エラー別枠m回」と分けて書く。
- **Retry**: 品質NG(ASR不一致・発音NG・内容不一致・無音/異常音声・Repetition等)を契機とする同一設定での再TTS。契機ごとに判定関数名:行を書く。Primary/Secondary ASRの関係も書く。
- **Fallback**: 設定切替を伴う再TTS。種類ラベル固定: `F-Style`(Style prefix/profile切替)、`F-Model`(TTSモデル/backend切替)、`F-Voice`(Voice切替)、`F-Prompt`(Prompt方式切替。例: Z ctx→legacy)、`F-Tech`(技術エラー救済の再試行)。何回目に・どの条件で・何から何へ、を書く。
- **Local Rewrite(LR)**: 本文テキストの局所書換え後に再TTS。発動条件・書換え回数上限・再TTS回数・再検査内容(ASR/発音/意味保持)を書く。
- **HR**: Human Review queue登録(ファイル名:行)+Lock(種類)。**STOP**: run停止(STOP file名・解除権限)。両方なら「HR+STOP」。
- **cooldown**: 待機(秒・位置)。
- **仕様・実装一致**判定の語: `一致` / `不一致(B)` / `仕様記録なし(C)` / `runtime証拠なし(未検証)`。runtime証拠は`docs/research/**/RUNTIME_EVIDENCE*`・`EVIDENCE*`・`er0XX_output/**/attempt_history*`等の実在pathで示す。
- **分類A/B/C**: ユーザー原文§7の定義どおり。
- **「3回NG」の数え方**: 必ず「通常n+Fallback m+LR後k=総N」の形で書く。
- **事実/所見の分離**: 表の各セルは事実(ファイル:行・文書)のみ。技術的見解・新解釈は`## 所見(事実ではない)`節に分けて書く。

## X担当の調査範囲

1. **Family Xの正式Production音声構成の完全一覧**: `er019_family_x_audio_production_runner_01.py`のstage/segment定義(Grep `SEGMENT|segment_id|stage_|def stage`)から、Std(a2)/Adv(b1b)で音声化される全部位(本文Part、Comment、In One Line、Key Phrase解説、単語解説、Lead/Outro等の定型音声、日本語音声[ja ASR cascade]等)を列挙。各部位が呼ぶ生成関数(`er003_v1_n3_01_tts_generate.py`の`generate_a2_segment_with_slowdown`/通常generate、`er012_b_family_voices_production_01.py`、chunk経路`er117_*`、KP解説の生成経路等)をファイル:行で特定。
2. **共通核(COMMON_CORE_01.md、あなたが正本)**: `er003_v1_n3_01_tts_generate.py`(試行ループ・ASR判定・Repetition・無音/異常検査・Style切替・`prior_generations`)、`er020_tts_retry_local_rewrite_01.py`(LR発動条件・書換え上限・再TTS・`COOLDOWN_SECONDS=600`・`maybe_cooldown_before_attempt`)、ER-011 cascade(`er011_*`: 3回上限・`record_outcome`・累積15回・HR queue `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`・Lock)、ja ASR cascade(`er007_*`: `er007_output/ja_asr_cascade_01/human_review_queue.jsonl`)、`er012_b_family_voices_production_01.py`(`attempt_hook`既定None :520付近、`style_prefix_override`)、STOP/RESTART_STORM/RUN_LOCK機構(`tools/stop_scope_check_01.py`・`--clear-stop`)。各関数の「入口引数で挙動が変わる点」(例: LRが引数/flagで有効化されるのか、呼出し側が渡さなければ無効か)を明記=Y/Zで「LRなし」が「共通関数の引数未指定」なのか「別関数」なのかを判別できる形にする。
3. **2026-10-19のLR発動条件に関するユーザー決定**: `DECISION_LOG.md`をGrep `2026-10-19`+`Local Rewrite|LR|書換え`、`docs/pm/USER_DECISION_REGISTER_01.md`をGrep `Local Rewrite|2026-10-19`、`docs/pm/delegation_log/2026-10-19_*`をGlob → 決定内容を逐語引用し、Xの各部位の実装と照合(一致/不一致)。
4. **X runtime evidence**: `docs/research/`配下でXのretry/LR/HRの実走記録(Glob `docs/research/*LOCAL-REWRITE*/**`、`docs/research/*X*RETRY*/**`、`er011_output/attempt_history.jsonl`のX由来行、`er019_output/**/audit/*retry*|*rewrite*`)を特定し、部位ごとに「実走証拠あり(path)/なし(未検証)」を書く。
5. **星取表①②のX行**と**X部位別フロー**(§5形式)を`FAMILY_X_01.md`へ。`family_x_01.json`には表の各行を構造化(keys: family, level, part, generator_fn, tts_limit, retry_conditions, fallback[type,trigger,from,to], lr[enabled,trigger,max_rewrites,retts,checks], final_ng, cooldown, hr_lock, stop, spec_refs[], runtime_evidence[], match, class, notes_fact, notes_opinion)。
6. **古いルールの残存・矛盾**: 後から追加した仕様(Chunk Std拡張 2026-10-26、2026-10-19 LR決定等)によりXで古いretry規則が残っていないかをGrep(`er019`内の独自retryループ・固定回数定数)で確認。

## KPI provenance欄

該当なし(調査のみ。runtime evidenceの有無は上記4で記載)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `er003_v1_n3_01_tts_generate.py`: Grep `def generate|max_attempts|MAX_ATTEMPTS|attempt|repetition|silence|asr|style_prefix|prior_generations|local_rewrite|rewrite` → 該当def全体と定数±10
- `er020_tts_retry_local_rewrite_01.py`: Grep `def |COOLDOWN_SECONDS|MAX_|rewrite_limit|trigger|def maybe_cooldown_before_attempt` → 各def先頭±40
- `er011_*.py`(Glob `er011_*cascade*.py`,`er011_*retry*.py`): Grep `def record_outcome|MAX_|15|human_review_queue|lock|LOCK` → ±30
- `er007_*.py`(Glob `er007_*cascade*.py`): Grep `human_review|MAX_|fallback` → ±30
- `er012_b_family_voices_production_01.py:500-560`(attempt_hook/style_prefix_override)、Grep `def generate|max_attempts|fallback|rewrite` → ±30
- `er019_family_x_audio_production_runner_01.py`: Grep `def stage_|segment_ids|SEGMENT|generate_a2_segment_with_slowdown|generate_|local_rewrite|rewrite|cascade|human_review|STOP|RUN_LOCK|budget` → 各±25(全文Read禁止、約3,000行)
- `er117_chunk_tts_production_01.py`: Grep `retry|rewrite|CHUNKS_NOT_ALL_VALIDATED|max_attempts` → ±20
- `er119_kp_*.py`(KP解説音声の生成・retry経路): Grep `tts|generate|retry|fallback` → ±20
- `CURRENT_SPEC.md`: Grep `Local Rewrite|Retry|Fallback|Human Review|cooldown|3回|試行上限|Family X` → 該当行±10のみ(全文読込禁止)
- `DECISION_LOG.md`: Grep `2026-10-19|Local Rewrite|LR発動|OPEN-516|OPEN-511` → 該当行±10
- `DECISION_LOG_HISTORY.md`: Grep `Local Rewrite|audio_retry_cascade|ER-011|ER-020` → 該当行±5
- `OPEN_ITEMS.md`: Grep `Local Rewrite|OPEN-516|OPEN-511|OPEN-528|Human Review|retry` → 該当行のみ
- `docs/pm/PM_GOVERNANCE.md`: Grep `Human Review|HR Lock|approve_regenerate|--clear-stop|安全≠成功` → 該当節のみ
- `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/EXISTING_SPEC_CHECK_01.md` 全文、`DESIGN_02.md`: Grep `J-1|Local Rewrite|cooldown` → ±15(Z側の「LR新設せず」判断の根拠と、共通核の説明の突合用)
- `ER-011_REPORT.md`・`ER-020_REPORT.md`(存在すれば): Grep `Local Rewrite|fallback|Human Review|上限` → ±10

## 事前指定Grep一覧+追記位置・更新位置の手順

- Glob `docs/research/*LOCAL-REWRITE*`、`docs/research/*REWRITE*`、`docs/research/*RETRY*CASCADE*`、`docs/pm/delegation_log/2026-10-19_*` → 関連文書一覧を`FAMILY_X_01.md`末尾「参照文書」に列挙
- `git log --oneline --since=2026-10-15 -- er020_tts_retry_local_rewrite_01.py er003_v1_n3_01_tts_generate.py er011_*.py er019_family_x_audio_production_runner_01.py`(変更履歴。出力は`--oneline`のみ)
- 成果物は全て`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/`配下に新規作成(dirが無ければ作成。Y/Z Agentも同dirに別名ファイルを作るので、自分のファイル名以外を作らない)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01X.md --json-out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_01X.md_check.json`
- `git log --oneline --since=2026-10-15 -- er020_tts_retry_local_rewrite_01.py er003_v1_n3_01_tts_generate.py er019_family_x_audio_production_runner_01.py`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。OPEN_ITEMS起票候補(既存OPENとの重複確認済みのもの)を`RESULT_PACKET_TRA1X.md`(9)に文案として記載(11-8分類付き)。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/FAMILY_X_01.md`、`family_x_01.json`、`COMMON_CORE_01.md`、`common_core_01.json`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md`、`..._DELEGATION_01X.md`、`..._DELEGATION_01X.md_check.json`。RESULT_PACKETはgitignored(addしない)。
- commit message: `TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01X: Family X+共通核のRetry/Fallback/Local Rewrite/HR仕様棚卸し(read-only、API 0)`
- trailer: `Delegation: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/01X`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_TRA1X.md`: (0)T-0結果・index、(1)X音声部位の完全一覧(Std/Adv別、生成関数:行)、(2)星取表①X行(全部位)、(3)星取表②X行、(4)X部位別フロー(§5形式、「通常n+Fallback m+LR後k=総N」表記)、(5)共通核の要点(関数ごとの上限・契機・LR有効化の仕組み[引数/flag/別関数]・HR/STOP条件)、(6)2026-10-19決定の逐語引用と照合結果、(7)runtime evidence有無表、(8)発見した不一致・理由不明箇所(分類A/B/C、重要度・品質リスク・単価・Delivery影響)、(9)OPEN起票候補文案(重複確認結果付き)、(10)所見(事実ではない)、(11)RESULT_PACKET必須4行(既存仕様整合/未承認機能の既定値=該当なし/失敗終了時の最終成果物/撤去・残置=なし)+「判定整合: 重大NG=<なし|あり>」1行、(12)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。ユーザー判断候補は`判断候補`表記。