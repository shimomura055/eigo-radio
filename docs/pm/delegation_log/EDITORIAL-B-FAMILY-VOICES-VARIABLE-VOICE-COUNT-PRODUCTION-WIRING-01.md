## 管理ID

EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01(OPEN-151)
並行タスク衝突確認: 並行して News B1追加・Trend再生成・Discovery修正(いずれも`er014_output/four_type_observation_01/{news,trend,discovery}/`のみ、Git操作なし、er003/er006/er010経路)が走る。本タスクはer012_*(B-Family)+新規テスト+`er014_output/four_type_observation_01/voices/`+SSOTを扱い、`er014_output/.../{news,trend,discovery}/`と`docs/pm/RESULT_PACKET_4T_{NEWS_B1,TREND_FIX,DISCOVERY_FIX}.md`には触れない・addしない。Git操作は本タスクのみ(SSOT登録タスクCONSOLIDATION-130は完了済み、commit 6f1fcc92)。RESULT_PACKETは`docs/pm/RESULT_PACKET_VOICES_VAR.md`(新規)。`docs/pm/ACTIVE_TASK.md`は固定ヘッダ付きで上書き可。

## 性質/到達上限Status/禁止事項

- 性質: Production配線(Gate 3)。ユーザー正式決定`APPROVED_FOR_PRODUCTION`(OPEN-151、2026-09-14): 「Production Writerを2/3 Voices可変へ一般化する」。到達目標**PRODUCTION_WIRED**。以下の最低限項目が1つでも未確認なら`PARTIAL`(不足項目を列挙)とし、PRODUCTION_WIREDと宣言しない: (1)2V新規topic正式Production path/(2)3V既存挙動のRegressionなし/(3)registry可変voice数/(4)retry・fallback整合/(5)Fact attribution・Comment Contract・Gate辞書整合/(6)2V runtime evidence/(7)3V regression evidence/(8)CURRENT_SPEC/(9)DECISION_LOG/(10)OPEN_ITEMS/(11)Git反映。
- 現状(4TYPE観測で判明、`docs/pm/RESULT_PACKET_4T_VOICES.md`): `er012_b_family_production_runner_01.py`のlevel="a2"/"b1"は承認済み固定記事の音声再配線専用(hash不一致fail-closed)。新規topic Writerは`main_b1_3v()`内`write_new_theme`stage→`er012_b_family_voices_writer_generic_01.run_writer_stage_generic()`のみで、`make_theme_config()`が`len(voice_cards)!=3`を拒否。CURRENT_SPEC L657-659に3V未配線5項目(registry可変voice数シグネチャ・Gate辞書point_three登録・Comment 3V Contract化・mode/level命名・Schedar本採用格上げ承認)。
- 実装方針(仕様変更は承認範囲内=voice数の可変化のみ): `writer_generic`の`voice_cards`を2または3件で受け付ける(2件時はVoice A/B=Algieba/Erinome、既定構造Hook/Voice A/Voice B/Tension/Closing[CURRENT_SPEC L648-658の2V標準構造]に従う。3件時は現行3V挙動と**バイト単位で同一のprompt/config**を生成すること)。registryの可変voice数シグネチャ、Gate辞書(point_two/point_three等)のvoice数依存部分、Comment Contract、Fact attributionの整合を2V/3V双方で確認。新規topicの2V正式入口として`main_b1_2v()`相当(または`--voices 2`引数)をrunnerへ追加(既存`main_a2/main/main_b1_3v`は無変更)。既存の3V保守版Fact Safetyゲート(`VOICE_FACT_SAFETY_GATE_MODE_DEFAULT=True`)・repetition QA(D')・OPEN-141 diff QA等の既存ゲートは2Vでもそのまま通す(緩和禁止)。
- **未承認範囲(STOP)**: Schedar本採用格上げ・mode/level命名の新規決定・音声(TTS)経路の変更・Prompt内容の改善・Gate緩和。これらが必要になったら実装せずUSER_DECISION_REQUIRED。
- Ledger供給: 2V runtime evidenceのtopic「Is personalized news good for us?」(狙い: personalizationの便利さ・relevance vs filter bubble/worldview narrowing/editorial control、双方が強く成立)。B-Familyが要求する入力(Verified Fact Ledger/Reference等)を確認し、他Familyと同じ先例(`er014_output/four_type_observation_01/news/run_news_a2.py`のResearch→Verification構造、web_search)で作成。Sonnet自身の知識で事実を補わない。B-Family固有前処理(OPEN-146 canonical spelling等)が正式pathにあればそのまま実行。
- 3V regression evidence: 既存3V経路が**バイト不変**であることをテストで証明(voice_cards=3で生成されるprompt/config/segment構造を、改修前コードの出力[git stash禁止のため、改修前版を`inspect.getsource`またはHEADのファイル内容を一時ファイルへ書き出して比較する方式]と突合)。オフラインで証明できる場合は3Vの実API再生成は不要。証明できない場合のみ3V 1本を再生成(上限¥100)して既存3V成果物と構造比較。
- レベル: 2V runtime evidenceはB1(新規topic Writerが`b1_3v`系にあるためB1系を優先。A2適応経路が2Vで既に配線済みならA2も生成可、ただし費用上限内)。音声化(TTS)は行わない(本文+Gateまで。TTS工程は無効化フラグで止め、runner改造はしない)。
- 費用上限: 2V runtime evidence ¥150(Research込み)、3V再生成(必要時のみ)¥100、合計¥250。超過見込みで停止し報告。
- 禁止: `git add -A`・`.`・`stash`・`clean`・`amend`・`rebase`・`force push`/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/er003_*・er006_*・er010_*・er013_*の変更/`er014_output/.../{news,trend,discovery}/`のadd。
- STOP条件: 上記未承認範囲/2Vで既存ゲートを通すために緩和が必要/3Vバイト不変が保てない/費用上限。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> Voices 2/3可変Writer — 既存APPROVED項目。別途ユーザーが正式決定済み: Production Writerを2/3 Voices可変へ一般化する。Status: APPROVED_FOR_PRODUCTION。これは未配線のまま忘れないこと。今回の修正作業と競合しない範囲でGate 3を完了し、PRODUCTION_WIREDまで追跡する。最低限: 2V新規topic正式Production path/3V既存挙動のRegressionなし/registry可変voice数/retry / fallback整合/Fact attribution / Comment Contract / Gate辞書整合/2V runtime evidence/3V regression evidence/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/Git反映 を確認。実装途中だけでPRODUCTION_WIREDとしない。
> Voices Topic: Is personalized news good for us? 2 Voicesで生成。テーマは単純な善悪ではなく、personalizationが情報取得を便利・Relevantにする側面/filter bubble / worldview narrowing / editorial controlなどの懸念の双方が強く成立する記事を狙う。ただし既存Voices仕様を優先。
> STOP条件: Voices配線中に未承認仕様が必要になった/新しいUSER_DECISION_REQUIREDが発生した。
> コスト報告: Voices「そのFamilyの正式1生成セット」総原価を主指標(PM_GOVERNANCE 15-8)。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_4T_VOICES.md` 全文(現状分析・行番号付き)。
2. `CURRENT_SPEC.md` L637-660(B-Family Voices仕様、2V標準構造、3V未配線5項目、OPEN-151追記)。
3. `er012_b_family_voices_writer_generic_01.py` 全文(改修対象、構造変更のため全文可)。
4. `er012_b_family_production_runner_01.py`: Grep `^def main|write_new_theme|run_writer_stage_generic|voice_cards|VOICE_CARD|level ==|argparse|add_argument|tts|audio` → 入口・stage定義・voice card定義・TTS工程位置の該当範囲のみRead(L1034-1059含む)。
5. `er012_b_family_editorial_type_registry_01.py`: Grep `^def |voice|VOICE_FACT_SAFETY_GATE_MODE_DEFAULT|point_three|point_two|Gate|gate` → registry・Gate辞書のvoice数依存箇所のみRead。
6. `er012_b_family_voices_theme_ai_screening_01.py` L150-190(3V voice_cards定義・呼び出し例)。
7. `er011_open121_repetition_qa_production_01.py`: Grep `^def |point_three|voice` → 2V/3Vで分岐する箇所のみ。
8. `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`: Grep `^class |^    def test_` → 既存3Vテスト一覧(バイト不変テストの土台)。
9. `er014_output/four_type_observation_01/news/run_news_a2.py`: Grep `def |researcher|verification|verified_fact_ledger` → Research→Verification→Ledger保存の関数範囲のみ(2V evidence用に流用)。
10. `docs/pm/PM_GOVERNANCE.md`: Grep `15-8|Production 1生成セット` → コスト報告形式の該当範囲のみRead。
11. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 実装: `er012_b_family_voices_writer_generic_01.py`(`make_theme_config`のvoice数2/3受付、2V時の構造・voice割当・Comment Contract・Fact attributionの分岐。3V時は改修前と同一出力)、`er012_b_family_editorial_type_registry_01.py`(可変voice数シグネチャ、Gate辞書のvoice数依存登録)、`er012_b_family_production_runner_01.py`(2V新規topic入口の追加。既存main_*無変更)。必要なら`er012_b_family_voices_writer_generic_01.py`内の定数化で対応。
- テスト: 新規`er012_b_family_voices_variable_voice_count_test_01.py`(2V config生成/2V Gate辞書/2V Comment Contract/3Vバイト不変[改修前HEAD版を`git show HEAD:er012_b_family_voices_writer_generic_01.py`で一時ファイルへ書き出しimportして出力比較]/voice_cards=1や4の拒否/retry・fallbackのvoice数非依存)。
- 2V runtime evidence: driver `er014_output/four_type_observation_01/voices/run_voices_2v_b1.py`(Research→Verification→Ledger→2V正式入口呼び出し、TTS無効、費用上限¥150ガード)。出力`er014_output/four_type_observation_01/voices/`(`research/`、`reader_facing_article.txt`[5区切り全文]、`voice_a.txt`/`voice_b.txt`、各Gate/QA生JSON[3Vゲート発火有無を明記]、`raw_usage_log.jsonl`、`cost_summary.json`、`production_set_cost.json`[Voices Production 1生成セット総原価=Research/Ledger+Writer+QA/Gate+retry+rewrite、直接費内訳])。
- SSOT: `CURRENT_SPEC.md`: Grep `OPEN-151` → 追記した段落の直後に「2/3可変Writer配線結果」段落(入口・voice数・構造・Gate整合・evidence・Status)。`OPEN_ITEMS.md`: Grep `^\| OPEN-151 ` → 行末尾に配線結果(Status: PRODUCTION_WIRED or PARTIAL+不足項目)。Grep `^\| OPEN-120 ` → 3Vゲートが2V runで発火した場合はruntime evidenceとして追記(未発火なら「未発火」)。`DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-130` → 直後に新エントリ+索引1行。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: 直近行の直後に2V run 1行。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(管理ID=本タスク、Status、APPROVED未配線=OPEN-151(結果に応じて更新)/OPEN-83/145/146(+OPEN-120)、報告単位Status: Voices可変Writer=<結果> / 4TYPE補完A/B/C=進行中 / Family C=Trial-08 VALIDATED評価待ち)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01.md --json-out docs\pm\delegation_log\EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01_check.json`
2. 改修前版の保存(バイト不変テスト用): `git show HEAD:er012_b_family_voices_writer_generic_01.py > er014_output\four_type_observation_01\voices\writer_generic_before.py`(同様にregistry/runnerも必要なら保存)
3. 新規テスト: `.venv\Scripts\python.exe -m unittest er012_b_family_voices_variable_voice_count_test_01 -v`
4. 関連回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er012*_test_*.py"` および `.venv\Scripts\python.exe run_project_regression.py --pattern "er011*_test_*.py"`
5. 全件回帰(1回): `.venv\Scripts\python.exe run_project_regression.py`(基準: 直近2588件、既知FAIL3件[`er003_test_p2j_investigate`]以外の新規FAILは本タスク起因)
6. 2V runtime evidence: `.venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_b1.py`(driver内でtopic/out_dir/voices=2/budget_jpy=150/TTS無効を固定。全文コマンドと固定値をRESULT_PACKETへ記録)
7. `git status --porcelain` → 明示add → commit → `git push origin main`(classifierブロック時は同一コマンド最大3回再試行)。

## SSOT追記文

- OPEN-151末尾: 「(EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01、2026-09-14) 配線結果: <PRODUCTION_WIRED/PARTIAL(不足項目)>。実装: <入口・可変voice数・Gate辞書・Comment Contract・Fact attributionの整合概要>。3V regression: <バイト不変テスト結果/再生成有無>。2V runtime evidence: <出力dir、topic、Gate/QA verdict、3Vゲート発火有無、model_id>。Voices Production 1生成セット総原価=¥<実費>(Research/Ledger¥、Writer¥、QA/Gate¥、retry¥、rewrite¥)。回帰<件数>。commit <hash>。」
- DECISION_LOG: 「2026-09-14: EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01(OPEN-151)。ユーザー正式決定(APPROVED_FOR_PRODUCTION)に基づき2/3 Voices可変Writerを配線。結果<Status>、Gate 3 11項目照合、evidence、費用、commit。詳細REPORT。」
- CURRENT_SPEC: 上記手順のとおり。PARTIALの場合はPRODUCTION_WIREDと書かない。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: 変更したer012_*ファイル、新規テストファイル、`EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01_REPORT.md`(新規root)、`er014_output/four_type_observation_01/voices/`配下(driver・research・記事・Gate json・cost。`writer_generic_before.py`等の一時比較ファイルは除外)、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01.md`+`_check.json`、`docs/pm/RESULT_PACKET_VOICES_VAR.md`。`er014_output/.../{news,trend,discovery}/`・`docs/pm/RESULT_PACKET_4T_*`・無関係既存差分はaddしない。
- コミットメッセージ: `EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01: Voices Writerの2/3 Voices可変化(OPEN-151)+2V runtime evidence+3V regression+SSOT更新` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_VOICES_VAR.md`に: 1) 到達Status(PRODUCTION_WIRED/PARTIAL/USER_DECISION_REQUIRED)と根拠、2) Gate 3最低限11項目を1つずつ「✓/✗+証跡」、3) 実装概要(変更ファイル・関数・2V/3V分岐・既存main_*無変更の証明[`git diff --stat`])、4) テスト結果(新規/er012/er011/全件)、5) 3V regression evidence(バイト不変テストの比較方法と結果、再生成した場合はその比較)、6) 2V runtime evidence(topic、Ledger CONFIRMED件数、5区切り各語数、各Gate/QA verdict、3V保守版ゲート発火有無、repetition QA、diff QA発火有無、model_id、retry回数)、7) 費用: **Voices Production 1生成セット総原価=¥xx.xx**(直接費内訳、50:50配賦なし)、開発・検証費(3V再生成があれば別計上)、8) API token、9) Open Item候補、10) commit hash・push結果、11) T-0・事前指定外Read・STOP有無、12) ACTIVE_TASK更新済み。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥150+¥100)
- [x] 並行タスク衝突回避あり(news/trend/discovery不可、Git本タスクのみ)
