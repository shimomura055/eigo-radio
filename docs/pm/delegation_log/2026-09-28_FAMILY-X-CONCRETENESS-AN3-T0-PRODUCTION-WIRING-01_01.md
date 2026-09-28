## 管理ID

FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(Phase A=設計・既存仕様確認のみ、委任 _01)。一時ファイル `docs/pm/ACTIVE_TASK_AN3.md` / `docs/pm/RESULT_PACKET_AN3.md`(commitしない)。並行: SSOT反映Agent 1件(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md` 編集中)→ SSOT 4点+PM_GOVERNANCE は編集権なし・読み取りのみ(Grep)。本タスクの所有: 新規 `docs/pm/design_family_x_concreteness_an3_t0_production_wiring_01.md`、delegation_log。**Phase A では Production code・Prompt・SSOT・Trial script を一切変更しない(設計書のみ新規作成)**。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。API支出 **上限¥0**(LLM/TTS/ASR 呼び出し禁止。必要なら実行前STOP)。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: Production Wiring の Phase A(設計)。ユーザーは **AN3-T0(A3+N2+現行英語化Prompt)を `APPROVED_FOR_PRODUCTION` と正式決定済み**。到達上限Status: Phase A 完了時点では `APPROVED_FOR_PRODUCTION`(未配線)のまま。`PRODUCTION_WIRED` は Phase B 後の Fable Gate 3 判定のみ。
- ユーザー正式思想(逐語、設計書冒頭に転記): 「細かい数字・時刻・過度な精度は極力使わず、記事理解に本当に必要な数字だけ最小限残す。固有名詞も同様に、理解上必要なものだけ残す。」 **「数字を0にする」とは絶対に定義しない。** AN2よりAN3を選んだ理由は「0件だから」ではなく「実本文で必要情報を残しながら不要な具体性をより強く落とせたため」。
- 禁止: T1(Trial限定の英語化側抑制追記)をProductionへ混入させない/現行英語化Promptは変更しない/Family A等の共有Promptへ影響を出さない/新しい大規模Validator仕様を勝手に設計しない(必要なら「必要」と報告のみ)/Family固有の新QA機構の新設。ユーザー向け表記は Standard/Advanced。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Read。全文Readは `er037_family_xy_concreteness_control_trial_01.py` の Prompt定数部と設計書のみ可。
G-1: git出力は `--porcelain`/`--stat`/`--short` で最小化。
F-1: transcript退避不要。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_01.md_check.json` を実行し結果1行記録(FAILでも内容改変してPASSさせない)。
T-2: TTSなし。T-3: API支出なし。

## ユーザー指示(原文抜粋、Phase 1)

「Production Wiring Checklist: Family X Production初回Writer経路へAN3相当を実装/R1/R2で数字・固有名詞を再前景化しない既存方針との整合/retry・fallback・regenerationでも同じ仕様が維持される/DEV/Trial scriptだけに残さない/T1をProductionへ混入させない/現行英語化Promptは変更しない/Family A等の共有Promptへ不用意な影響を出さない/runtimeでProduction正式pathの発火を確認/Essential Fact・因果関係のRegression確認/CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS更新/Trial-02のstatus反映/必要Git commit・push/approved内容と実挙動一致確認。 数字カウンタの誤認是正: Trial評価用カウンタが漢数字を取りこぼして『0』と表示した件について、少なくともREPORT/SSOT上の表現を訂正すること。Production QAとして数値カウンタを使うなら、Arabic numeral/漢数字/パーセント等の日本語表記/日付/金額をどう扱うか確認し、誤った『数字0』を成功条件にしない。新しい大規模Validator仕様が必要なら勝手に拡張せず報告すること。」

## Phase A の作業(設計書 `docs/pm/design_family_x_concreteness_an3_t0_production_wiring_01.md` を新規作成)

1. **Existing Spec Check(Grep先を記録)**: (a) Family X Production の JA 初回Writer経路(Storyline+B3 Fact選定 `er019_family_x_storyline_b3_fact_selection_01.py` → JA Writer O R1→R2 `er019_family_x_ja_writer_o_r1_r2_01.py` → Advanced化 `er003_v1_n3_01_advanced_adaptation_generate.py` の想定。Grep `REVISION_INSTRUCTIONS|WRITER_O|SYSTEM_PROMPT|def build_.*prompt|previous_response_id` で実際の関数名・Prompt定数名・呼び出し順を表にする)。Production runner(`er019_family_x_audio_production_runner_01.py` 等、Grep `writer_o|ja_writer|generate_ja|storyline`)から見た正式path、retry/fallback/regeneration/Local Rewrite/segment再生成の各pathが同じ Prompt 定数を通るかを表で示す。 (b) その Prompt 定数が Family A/B/Y/Z と共有か(Grep `from er019_family_x_ja_writer_o|import .*WRITER_O|REVISION_INSTRUCTIONS` を `er0*.py` 全体で)。 (c) `CURRENT_SPEC.md` の Family X Writer/R1→R2/Advanced化/Spoken-first Number Treatment(Family Aのみ)/OPEN-20(固有名詞密度目標 REJECTED)の記述(Grep `Family X|R1|R2|Number Treatment|OPEN-20|固有名詞|数字`)→ AN3 との衝突有無。OPEN-20 は「密度目標(数値目標)」の REJECT であり、A3/N2 は定性的抑制指示である点を確認し、衝突なしと言えるかを根拠付きで判定(衝突する場合はSTOP報告)。 (d) `DECISION_LOG.md`/`OPEN_ITEMS.md` の OPEN-217/218/220/224、FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01/02 エントリ(Grep)。
2. **Trial資産の逐語抽出**: `er037_family_xy_concreteness_control_trial_01.py` の A3・N2 の Prompt 追記文(逐語)と AN(A+N)の結合方法、Trial での注入位置(system/user/どの段階=初回Writerのみか R1/R2 にも入れたか)。`er039_family_xy_concreteness_control_trial_02.py` の T0/T1 定義(T1 文言は「混入禁止対象」として逐語で設計書に列挙)。
3. **配線設計**: Production 初回 Writer Prompt への AN3 追記の**最小 diff**(逐語、挿入位置、定数名案 例 `CONCRETENESS_CONTROL_AN3_BLOCK`、`prompt_version`/`writer_prompt_version` 等の既存バージョン識別子があれば bump 案)。R1→R2 REVISION_INSTRUCTIONS に「数字・固有名詞を再前景化しない」旨が既にあるか/無ければ最小追記案(ユーザーの「既存方針との整合」要件)。retry/fallback/regeneration/Local Rewrite の各 path が自動的に同じ定数を通ることの根拠(通らない path があれば列挙)。Advanced化 Prompt は**無変更**と明記。runtime evidence 案(Production run の audit/`writer_result.json` 等に Prompt 定数の sha256/version が記録される既存仕組みの有無、無ければ最小の記録追加案)。
4. **Regression 設計**: 既存 `run_deviation_check()`(Ledger Deviation Check)を主判定に、Hormuz/Meta の Production path 再生成(Phase B、JA+Advanced、TTS なし)で Essential Fact/因果の MAJOR 0 を確認する計画と想定費用(Trial-02 実測 ¥16.9/8セルを根拠に概算)。Prompt 定数 sha256 不変 assert の既存テスト(er037/er039 test)が Production 定数変更で **意図的に失敗する**ことへの対処方針(テスト側の期待値更新=正当、を明記)。
5. **数字カウンタの誤認是正(設計のみ)**: er037/er039 のカウンタ実装(Grep `def count_|numer|digit|re\.compile`)を確認し、漢数字(七月十三日/二割/翌日/一バレル八十五ドル超 等)の取りこぼしを事実として記録。REPORT/SSOT の「AN3 は数字 0」表現の訂正文案(「Arabic数字 0、漢数字は未計測。実本文には必要な数字が残存」)。Production QA として数値カウンタを使うか否かの判断材料: 既存 Production に数値カウンタ QA があるか(Grep `Number Treatment|spoken_first|count_numbers` in `er0*.py`)→ 無ければ「本配線では数値カウンタを成功条件にしない(Deviation Check を主判定)」を推奨案とし、Arabic/漢数字/%/日付/金額の扱いは将来 Validator 仕様として **設計せず必要性のみ報告**。
6. **Trial-02 status 反映案・SSOT 文案**(Phase B で反映): CURRENT_SPEC 追記文案(Family X Writer 節、ユーザー正式思想を逐語、「数字0を成功条件にしない」)、DECISION_LOG 文案(ユーザー正式決定 AN3-T0 `APPROVED_FOR_PRODUCTION`、AN2/T1 不採用、カウンタ誤認訂正)、OPEN_ITEMS 文案(OPEN-224[T1 MAJOR]→T1不採用によりCLOSE案、OPEN-220→現行英語化Prompt維持決定により DEFERRED 案、OPEN-217/218 は Family Y 側のため据え置き)、REPORT_LEDGER 行案(Trial-02 → `APPROVED_FOR_PRODUCTION`[AN3-T0のみ]、Wiring-01 新行)。
7. **リスク・Fable/ユーザー確認事項**: 共有 Prompt への影響、Family A/B/Y/Z への波及、費用、STOP 候補。

## 事前指定Read一覧

- `er037_family_xy_concreteness_control_trial_01.py`: Prompt定数部(Grep `A3|N2|PATTERN|BLOCK` → 該当範囲)
- `er039_family_xy_concreteness_control_trial_02.py`: T0/T1定義(Grep `T1|SUPPRESS|BLOCK`)
- `docs/pm/design_family_xy_concreteness_control_trial_01.md` / `..._02.md`: 注入位置・結合方法の節
- `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_REPORT.md`: カウンタ節・AN3 本文(Grep `数字|カウンタ|七月|二割`)
- `er019_family_x_ja_writer_o_r1_r2_01.py`: Prompt定数・R1→R2(Grep 上記)
- `er019_family_x_audio_production_runner_01.py`: JA writer 呼び出し(Grep 上記)
- `er003_v1_n3_01_advanced_adaptation_generate.py`: 入力が JA 記事のみであることの再確認(Grep `ADVANCED_VOCAB_RULE_V2_BLOCK|def generate`)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記1〜5の各Grepパターン。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md` は Grep+該当行範囲Readのみ(全文Read禁止、編集禁止)。
- 追記位置: 設計書 `docs/pm/design_family_x_concreteness_an3_t0_production_wiring_01.md` を新規作成(既存設計書は変更しない)。
- 更新位置: なし(Phase A はコード・SSOT無変更)。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_01.md_check.json`
- Production無変更の証拠: `git status --porcelain -- "er0*.py" "er003_v1_translator_briefs/" CURRENT_SPEC.md`(本タスク由来の差分なし。他タスクの既存差分は列挙のみ)

## SSOT追記文

設計書 §6 に文案のみ(Phase B で反映)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): 設計書、delegation_log+`_check.json`。SSOT編集権: なし。
- メッセージ: `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01: Phase A 設計書(既存仕様確認・最小diff案・Regression計画・数字カウンタ誤認訂正案)`、trailer `Management-ID: FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_AN3 + handback、目安30行)

1 Existing Spec Check 結果(正式path表、共有有無、OPEN-20 との衝突判定) 2 A3/N2 逐語と Trial 注入位置、T1 逐語(混入禁止対象) 3 最小 diff 案(逐語)と通過 path 一覧・通らない path 4 R1→R2 整合の現状と追記要否 5 runtime evidence 案 6 Regression 計画と想定費用 7 数字カウンタ誤認の事実と訂正文案、Production QA カウンタの推奨(成功条件にしない) 8 SSOT 文案の所在 9 リスク・STOP 候補・Fable/ユーザー確認事項 10 commit hash・raw URL。
