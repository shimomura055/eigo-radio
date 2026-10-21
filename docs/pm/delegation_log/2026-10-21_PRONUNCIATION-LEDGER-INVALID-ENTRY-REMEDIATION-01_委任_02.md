# 委任文(Fable→sonnet-worker)

## 管理ID
PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01 委任_02(Fable判定=**PRODUCTION_WIRED**の記録のみ。API 0・費用JPY0・コード変更なし)。並行agent: `FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_07`(読み取り調査、SSOT未編集)。共有プロトコル。

## Fable判定(記録用、変更しない)
- Status: **PRODUCTION_WIRED**(2026-10-21、Fable判定)。根拠: (1)不正5 entry隔離(`ledger_disabled`)+melos hint是正、正当26維持、バックアップsha保存 (2)原因=研究応答の未検証upsert(LLMがfield値を canonical に混入)、発生run特定(2026-09-28 Hormuz、"U.S."/"US"差分の固有名詞扱い) (3)再発防止=登録時自動隔離(`entry_invalid_reason`)+供給側(`get_hint_for_text`/M1 `_c2_candidates`/cascade研究経路)での隔離除外、新test 22件PASS、既存974 PASS(失敗4件は既存・無関係) (4)X/Z共通call site(`get_hint_for_text`)で供給前後比較: "unknown"供給7 segment→0、Melos 16 segment維持、他変化0 (5)golden再判定121 attempt: PASS/NG変化0 (6)既存wav 2本のAzure実呼出で悪化なし(JPY2.6) (7)retry/fallback/resume整合(毎call再読込・M1 snapshot[OF-179]・研究401時はunconfirmed・ER-23整合) (8)重み2.0・ASR判定・閾値不変。
- 付帯(未達ではない・監視): 研究応答が不正だった場合の自動隔離のProduction実発火は、Perplexity 401(#134)のため再現不可=test evidenceのみ。復旧後の初回発火を監視(OPEN-283/OPEN-435と同型のmonitor)。疑義6 entry(ganis/lindberg/kallmeyer/mini/muse/meink)は報告のみ・未是正(Fable: 現時点で供給害なし、是正は別途)。「US/U.S.」表記差が固有名詞扱いになる点は既存挙動の観察(判断候補として記録、提案はしない)。

## 作業
S0. T-0: `docs/pm/delegation_log/2026-10-21_PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01_委任_02.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「LEDGER-INVALID-ENTRY-REMEDIATION-01 委任_02」を含む最新index)。check結果1行。
S1. `OPEN_ITEMS.md` OPEN-436行頭Statusを`PRODUCTION_WIRED(Fable判定2026-10-21、監視: 研究応答不正時の自動隔離はPerplexity復旧後の初回発火で確認)`へ(旧Status保持)、行末に根拠(1)〜(8)+付帯。
S2. `CURRENT_SPEC.md` Ledger節の委任_01注記直後に「【Fable判定 2026-10-21】PRODUCTION_WIRED(根拠=OPEN-436、証跡=docs/research/PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01/)。付帯=研究経路の自動隔離はtest evidenceのみ(Perplexity 401)」を1文追記。
S3. `DECISION_LOG.md`末尾に短い追記エントリ(Fable判定PRODUCTION_WIRED、根拠・付帯)。REPORT_LEDGER 1行、ACTIVE_TASK先頭追記。
S4. secret scan→明示add→commit(`PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01 委任_02: Fable判定PRODUCTION_WIRED記録`)→`git push origin HEAD:main`→到達確認。

## 報告(docs/pm/RESULT_PACKET_PLIR2.md 上書き)
各反映行番号、commit hash、raw URL、4行判定。