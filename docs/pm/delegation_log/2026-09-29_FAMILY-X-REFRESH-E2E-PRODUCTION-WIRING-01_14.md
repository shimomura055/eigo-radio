## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Closeout / Fable Gate 3 判定の SSOT 反映、委任 _14)。一時ファイル `docs/pm/ACTIVE_TASK_RFC.md` / `docs/pm/RESULT_PACKET_RFC.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`、HEAD `c84f070c` 以降)。**SSOT 4 点(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)+REPORT_LEDGER は本タスクが編集権を持つ(直列化)**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。費用 ¥0(API 呼び出しなし)。コード・Prompt 変更禁止。

## Fable Gate 3 判定(前提、逐語で SSOT に反映)

**判定: Family X Production 経路の配線は Gate 3 PASS(Meta × Standard/Advanced の runtime evidence に基づく)。以下の承認済み仕様を `PRODUCTION_WIRED` へ格上げする。**
根拠(Fable が evidence を直接照合): `er019_output/family_x_audio_production_wiring_01/meta__run_03/{a2,b1b}/audit/tts_generation_results.json` で reuse 21 件(a2 10/b1b 11)、Advanced KP 全 5 rank で explanation voice=Aoede・Variant B 文言(`measured pace, without dragging`)・`phrase_repeat` 5 件・english と同一 master_audio_id、固定 shell の master_audio_id 10 件(welcome `aa130472d437ac80b7cdd474` 含む)、a2 の J3 文言(「落ち着いた、自然な話し言葉…」)、`style_version` 記録、`HEADING_READOUT`/`NG_ACCEPTED_AFTER_RETRY` 0 件。REPORT §E2E Meta run_03 の Gate 表(13+9+ユーザー指定)全 PASS、Pages 7 項目全 PASS、試聴 URL `https://shimomura055.github.io/eigo-radio/user_test/family_x_refresh_e2e_01/index.html`。
**スコープ注記(条件緩和ではない)**: 当初の E2E 対象は Hormuz+Meta の 2 記事。Hormuz はユーザー指示(2026-09-29)により deferred / non-blocking として保留(3 run 連続の ja_source MAJOR、Checker 問題として OPEN-233 へ切り離し)。Gate 3 は「Production 経路全体の完成可否」を Meta で判定し、Hormuz 個別未完と混同しない(ユーザー指示)。Hormuz 未完が抵触する点=「2 記事完成」の当初スコープのみ。配線側の Standard/Advanced 非対称は無い(Hormuz の非対称は Checker 判定差由来)。

PRODUCTION_WIRED へ格上げする仕様(各 evidence を併記):
1. AN3-T0 具体性制御(A3+N2、Original 側のみ、reminder なし)— `concreteness_an3_block_sha256=067030ff…` が Hormuz run_02/03・Meta run_03 で一致。OPEN-228 の順序条件(見出し廃止+3 分割 → 採用 → 整理 → 配線完了)を満たした。
2. 可変 Role Style JA=J3 / EN=E2(Japanese Title・preview・comment・full_story・in_one_line・**KP 日本語意味**を含む)+cache version guard(`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`)+Advanced 英語経路 runtime evidence。
3. 固定フレーズ Champion 10 件(welcome=A 現行、他 9 件 `v3_champion_2026_09_29`)の Production Master Store reuse(TTS call 0)。
4. 新記事構造(途中 Heading 廃止/忠実英訳/段落境界 3 分割/Comment1→body1→Comment2→body2→Comment3→body3→Comment4→In One Line/Heading Readout 撤去/In One Line 短文/Deviation MAJOR → must-fix 1 回)。
5. Key Phrase 音声構造(Standard: Phrase → 日本語意味(J3) → 同一 Phrase/Advanced: Phrase → 英語解説(text 仕様+Variant B、Aoede) → 同一 Phrase、再掲は reuse で TTS call 0)。
6. Opus L2 是正 5 件(KP 解説 fail-closed、KP cache text/version guard、Standard 構造 Gate 対称化、TTS backend fail-fast、er012_e 非 writer stage 封鎖)。
7. 案B(ja_source MAJOR → JA must-fix 差し戻し 1 回、fail-closed)— runtime evidence: Hormuz run_03 で発動・JA 再生成 1 回で Advanced COMPLIANT(その後 Standard で別 MAJOR → 設計どおり STOP)、Meta run_03 では非発動(Advanced 初回 COMPLIANT)。**暫定 retry 拡張であり Checker 問題の正式解決ではない**旨を維持。

## SSOT 反映内容

### CURRENT_SPEC
- Family X の各該当小節の Status を `PRODUCTION_WIRED`(2026-09-29、Gate 3=Meta run_03、REPORT 参照)へ更新。Hormuz deferred の注記。`PRODUCTION_WIRED` の根拠 evidence パスを 1 行ずつ。
- Family X 運用上の既知制約を追記: 「audio runner の `source_dir` は `er019_output/{slug}/{run}` 固定で、writer 段の `--out-dir` と不一致の場合はファイルコピーが必要(OPEN-234、コード未変更)」。
### DECISION_LOG
- 新エントリ: Fable Gate 3 判定(上記逐語)、Hormuz deferred の理由(ユーザー指示: Family X を必要十分に閉じ GPT-6 Trial を早く開始、Hormuz の Checker 挙動を追い続けない)、Meta で証明できたこと、PRODUCTION_WIRED 格上げ 7 件、費用 A 実測(本管理ID 累計 ≈ ¥48.08: run_01 ¥0.99/run_02 ¥5.07/Hormuz run_03 ¥10.35/Meta run_03 ¥31.68)、費用 B(記事あたり: KP 解説 +1 LLM +5 TTS、Phrase 再掲 0、Heading Readout −2 segment、Master reuse 0、Comment 4 本化、案B 発動時のみ +¥5〜6)。
### OPEN_ITEMS
- **OPEN-228**: `CLOSED (SUPERSEDED)`(新構造で旧 gate は Family X 新経路から到達不能、er012_e 非 writer stage 封鎖済み、Meta run_03 で runtime 確認)。
- **OPEN-230**: 新構造の PRODUCTION_WIRED に伴い更新(CLOSED または残論点のみ残す。内容を Grep して判断・理由記録)。
- **OPEN-233**(deferred): 追加 Evidence を追記 — Hormuz run_01(HF-006)/run_02(HF-011changed_causality)/run_03(HF-009 ×2: Advanced 段は案B で解消、Standard 段で再発=同一 JA を Advanced が COMPLIANT・Standard が ja_source MAJOR とした矛盾判定、origin 判定の信頼性論点)、Meta run_03(Advanced COMPLIANT、Standard translation MAJOR → must-fix 1 回で解消)、Hormuz は deferred / non-blocking で保留中、再開順序(Meta E2E/Closeout → GPT-6 Trial → Routing 判断 → OPEN-233 再開)を再掲。
- **OPEN-234 新設**(`OPEN (non-blocking for wiring / blocking for unattended 量産)`): audio runner `source_dir` と writer `--out-dir` の不一致(手動コピー運用、Hormuz/Meta run_03 で実施)。恒久対応(CLI 引数追加等)はユーザー判断。
- **Hormuz の Status**: `DEFERRED (non-blocking)` を OPEN-233 内に明記(別番号は立てない)。
- GPT-6 Trial 準備: `docs/pm/gpt6_trial_preparation_01.md`(commit e6475a24)へのポインタを OPEN-233 と DECISION_LOG に記載。
### REPORT_LEDGER
- `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` を「Gate 3 PASS(Meta)、PRODUCTION_WIRED 7 件、Hormuz deferred」で登録/更新。`docs/pm/gpt6_trial_preparation_01.md` を準備資料として登録。
### REPORT
- `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` 末尾に §Closeout(Fable Gate 3 判定逐語、PRODUCTION_WIRED 7 件表、Closeout 10 項目充足表[SSOT 反映済みへ更新]、費用 A/B 確定値、Hormuz deferred、OPEN-228/230/233/234 の最終 Status、GPT-6 Trial 開始可否=準備完了(未確認事項: 一部 Role の実測 model_id、GPT-6 の model_id・料金))。設計書 §10 Closeout。
- 試聴ページ `user_test/family_x_refresh_e2e_01/index.html` に `file://` リンクが含まれていないことを確認(含まれていれば相対リンクへ修正し、Pages 7 項目のうち HTTP 200・player 存在・mp3 200 を再確認)。

## 固定ブロック

T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_14.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_14.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_14.md_check.json` を実行し結果 1 行記録。T-2: TTS なし。T-3: API 支出なし。E-1/D-1/G-1/F-1 標準。

## 事前指定Read一覧 / 事前指定Grep一覧

- `docs/pm/RESULT_PACKET_RFE4.md`(前委任の SSOT 文案、あれば)、REPORT §E2E Meta run_03(行 1313〜)、`CURRENT_SPEC.md` Grep `Family X|AN3|Champion|Role Style|Key Phrase 音声構造|記事構造|案B|PRODUCTION_WIRED|APPROVED_FOR_PRODUCTION`、`OPEN_ITEMS.md` Grep `OPEN-228|OPEN-230|OPEN-233|OPEN-23[0-9]`(最大番号)、`DECISION_LOG.md` 先頭ヘッダーチェーン、`docs/pm/REPORT_LEDGER.md` Grep `FAMILY-X-REFRESH|gpt6`。
- 更新位置: SSOT 3 点+REPORT_LEDGER、REPORT §Closeout、設計書 §10、index.html(必要時のみ)、delegation_log。

## 実行コマンド全文

- `git pull --ff-only origin main`
- `grep -c "file://" user_test/family_x_refresh_e2e_01/index.html`
- `git diff --stat HEAD`

## Git

- commit 2 つ: (1) REPORT §Closeout+設計書+delegation_log(+index.html 修正時)`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01: Closeout(Fable Gate 3 PASS[Meta run_03]、PRODUCTION_WIRED 7件、Hormuz deferred、費用A/B確定)`;(2) SSOT 3 点+REPORT_LEDGER `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01: SSOT反映(PRODUCTION_WIRED 7件、OPEN-228 CLOSED/SUPERSEDED、OPEN-230更新、OPEN-233追加Evidence、OPEN-234新設、Hormuz deferred、GPT-6準備ポインタ)`。trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`、path 指定 add、push。

## 報告(RESULT_PACKET_RFC + handback、目安25行)

SSOT 更新箇所(小節名・OPEN 番号・Status)/PRODUCTION_WIRED 7 件の記載確認/OPEN-228・230・233・234 の最終 Status/index.html の file:// 確認結果/Closeout 10 項目の充足/commit hash 2 件・raw URL/STOP 有無。
