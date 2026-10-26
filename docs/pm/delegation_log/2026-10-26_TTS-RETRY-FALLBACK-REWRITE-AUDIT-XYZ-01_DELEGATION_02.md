## 管理ID

TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02(統合: 委任_01X/01Y/01Zの成果物を1本の報告`REPORT_01.md`へ統合し、星取表①②の全Family・全部位版、部位別フロー、A/B/C分類一覧、QCD優先順位、OPEN起票候補を確定。加えて優先事実確認=Y-F01[Y runnerのStyle profile `default`固定]。read-only・API 0・JPY0)。並行タスク衝突確認: 並行Agent 2件(FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01[`er121_*`編集+有料run]、FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01[read-only])。あなたの所有ファイル=`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/{REPORT_01,Y_F01_STYLE_PROFILE_CHECK_01}.md`、`consolidated_01.json`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_02.md`(+check.json)、`docs/pm/RESULT_PACKET_TRA2.md`。FAMILY_X/Y/Z_01.md・COMMON_CORE_01.mdは**編集しない**(矛盾があればREPORT_01で指摘)。SSOT編集権なし。コード編集禁止。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: read-only統合・事実確認。到達上限Status=調査完了(AUDITED)。
- 禁止: 有料API、コード/SSOT/run dir編集、推測による理由付け(根拠なしは「理由不明・記録なし」)、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。Fable/Sonnetの技術的見解は「所見(事実ではない)」欄に分離。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(調査)。統合後にFableが任意レビューの要否を判断。
- 修正範囲の線引き(11-8): 修正なし。
- 時間見込み: 約1.5h(3文書の突合40分/Y-F01確認20分/REPORT作成30分)。並列化: なし(統合は直列)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_02.md` をN=659から順に試し、先頭が「## 管理ID」+「TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02」で始まるものを採用(`--index -1`不可)。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md`(全文保存済み。最初に全文Read)。最終報告の構成(§9)は次の順: 1結論(XYZのRewrite/Fallback仕様は整合しているか)/2全Family・全音声部位の星取表①/3 Rewrite不適用理由と承認根拠の星取表②/4 Family・部位別の実際の処理フロー/5発見した仕様不一致・未配線・理由不明箇所/6 QCD影響と優先順位/7 Fable独立評価(欄を空ける)/8必要なユーザー判断事項(本当に判断が必要なものだけ)。完成条件=「ユーザーが星取表を見れば、XYZそれぞれの音声部位について『何回失敗すると、何が起こり、なぜそうなっているのか』を理解できる状態」。後続指示(2026-10-26 §3/§4、`…FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md`): 「Local Rewriteは未配線であり、現行ではHuman Review／STOPに進む。…Local Rewriteについては次項の調査結果と照合すること。Local Rewriteの新仕様を独断で追加しない。」「特にRewrite不適用の理由は、既存記録で確認できるものと、Claude/Fableの新たな見解を区別すること。差異は、承認済みの例外／仕様不一致／理由不明・未承認に分類する。本件は調査のみ。」

## 統合の指示

1. **用語統一**: 3文書の用語(通常TTS上限/Retry/Fallback種類ラベルF-Style・F-Model・F-Voice・F-Prompt・F-Tech/LR/HR/STOP/cooldown/「通常n+Fallback m+LR後k=総N」)が揃っているかを突合し、ズレは統合表で統一(どの文書のどの表現を正としたかを脚注)。共通核の記述(COMMON_CORE_01の関数表L1〜L8、`enable_connected_speech_equivalence_layer`1本でLR+cooldownが連動)と、Y/Zの呼出し記述が矛盾しないか確認。矛盾があれば**コードで再確認**(ファイル:行)して正を決める。
2. **星取表①(全Family・全部位)**: X 16行+Y 19行+Z 14行を1表(Family→レベル→部位の順)。列はユーザー指定10列+「生成関数(L番号)」「runtime証拠」の2列を末尾に追加。各セルは事実のみ。
3. **星取表②(Rewrite適用有無と理由)**: 全部位。理由区分(ユーザー明示不採用/承認済み仕様として対象外/技術的制約/適用漏れ・配線漏れ/記録なし)と根拠資料(ファイル:行、逐語引用は短く)、分類A/B/C。Zセリフ(dialogue)は、ユーザー原文「NG → 既存のLocal Rewrite処理へ」とJ-1(Fable判断)・Opus同調・後続のユーザー認識「LRは未配線で現行はHR/STOP…調査結果と照合…新仕様を独断で追加しない」を時系列で並べ、事実として「ユーザー承認による除外ではなく、既存LRが無い状態でFableがHR/STOP直行を選んだ(J-1)。ユーザーは後日その状態を認識し、採否判断を本調査後へ保留」と記す(分類はユーザー判断待ち=C、11-8ではD候補)。
4. **部位別フロー(§4)**: 共通フローをまとめ、差異がある部位だけ個別に。Z dialogue ctx(通常ctx2+F-Prompt1+LR後0=総3、技術エラー別枠)、X/Y/Z narrator・本文(Std: 通常2+F-Style1+LR後1=総4、Adv: 通常3+LR後1=総4)、日本語(通常2+F-Style1=総3、LRなし→HR)、KP phrase(MINIMAL2+ENGLISH_LOCK2=総4、LRなし)、KP解説(総3)、shell固定英語、Y Std chunk等。
5. **不一致・理由不明一覧(§5)**: 3文書の発見(X: OPEN-376再入・OPEN-312/274 Style差・非ASR起因NGでLR不発[新規C]・KP解説/shellの扱い[C]・Std減速後最終NG[C]; Y: Y-F01〜F09; Z: dialogue LRなし[C/D]・M-3(ii)・cooldown STOP sentinel未確認・topic_intro_en未解決[B]・OPEN-274/371)を1表に(ID・Family・部位・分類・重要度[高/中/低]・品質リスク・量産コスト・Delivery影響・既存OPEN重複・推奨対応[修正へ進む/確認/ユーザー判断])。**重複統合**: 同一事象(例: X「非ASR起因NGでNO_NG_SPAN」とY「Repetition QA単独NGでNO_NG_SPAN」[Y-F03])は1件にまとめ、Family横断で記す。
6. **Y-F01の事実確認(優先。`Y_F01_STYLE_PROFILE_CHECK_01.md`)**: (a)`er121_family_y_runner_01.py:37`付近の`STYLE_PROFILE`定義と、それがTTS生成にどう渡るか(Grep `STYLE_PROFILE|style_profile|fx_20261017|default` in `er121_*.py`)、(b)設計・承認側=`docs/research/FAMILY-Y-*/DESIGN_01.md:84`付近・`SPEC_LEDGER_03.md:60`(YL-A01)・`CURRENT_SPEC.md:1699`付近(Grep `fx_20261017|Y化時|配線対象`)・DECISION_LOG(Grep `fx_20261017|Family Y.*Style|YL-A01`)・ユーザー承認原文(`docs/pm/delegation_log/*FAMILY-Y*USER.md` Grep `Style|profile|PD06|S3|E1|K2|P8|P7`)、(c)runtime=redelivery_fee run_01とE-3のaudit(Grep `style_profile|x_gate|checked` in `er121_output/family_y_production_01/redelivery_fee/run_01/**/*.json`、代表数件のみ)で実際に使われたStyle prefix文字列、(d)X側で`fx_20261017`が何を変えるか(PD06/S3/E1/K2/P8-KP/P7の各項目の1行説明=`CURRENT_SPEC.md` Grep `fx_20261017`の節)。結論は「Yは承認上`fx_20261017`継承が仕様(根拠:行)か/`default`が承認済みか/記録なしか」の3択で事実を書き、**再配達記事の完成版をいま制作した場合の影響**(default固定のまま制作=現行公開版と同条件/仕様違反の可能性)を事実ベースで記す。是正は行わない。
7. **OPEN起票候補(§8向け)**: 3文書の候補を重複確認のうえ確定リスト(新規/既存追記、11-8分類)。
8. **ユーザー判断事項(§8)**: 「本当に判断が必要なものだけ」。候補: (1)Z dialogueへのLR新設の要否(選択肢: 新設[3回NG後に書換え→再TTS1回、Opus条件A]/現状維持[HR/STOP]。事実と所見を分離)、(2)非ASR起因NG(Repetition/disfluency)でcooldown後にLR不発→HRとなる件の扱い(a現状維持/b非ASR起因はcooldown省略=2026-09-26「固定10分」と衝突/c LR拡張=新仕様)、(3)Y-F01の結果次第でY Style profileの扱い。技術的に自律解決できるもの(B・配線漏れ)はユーザー判断に上げず「修正へ進む候補」として分ける。
9. `consolidated_01.json`: 星取表①の全行(3 jsonを統合、キー統一)+findings配列。

## KPI provenance欄

該当なし。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md` 全文
- `docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/COMMON_CORE_01.md` 全文、`FAMILY_X_01.md` 全文、`FAMILY_Y_01.md` 全文、`FAMILY_Z_01.md` 全文(統合元。全文Read許可)
- 同dir `family_x_01.json`・`family_y_01.json`・`family_z_01.json`・`common_core_01.json`(統合用)
- `er121_family_y_runner_01.py:25-50`、Grep `STYLE_PROFILE|style_profile` → ±10
- `er121_family_y_audio_01.py`: Grep `style_profile|STYLE_PROFILE|x_gate|fx_20261017` → ±10
- `CURRENT_SPEC.md`: Grep `fx_20261017` → 該当行±8、`CURRENT_SPEC.md:1690-1710`
- `docs/research/FAMILY-Y-*/DESIGN_01.md`(Glob後、Grep `fx_20261017|Style profile|継承`) → ±10、`docs/research/FAMILY-Y-*/SPEC_LEDGER_03.md:50-70`
- `DECISION_LOG.md`: Grep `fx_20261017|YL-A01|Family Y.*Style` → ±5
- `docs/pm/delegation_log/2026-10-1*_FAMILY-Y*USER.md`(Glob): Grep `Style|profile|PD06|fx_` → ±3
- `er121_output/family_y_production_01/redelivery_fee/run_01/b1b/audit/`配下の代表1〜2 json(Grep `style_profile|style_prefix|checked`)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `enable_connected_speech_equivalence_layer` in `er121_family_y_audio_01.py`,`er063_family_z_audio_01.py`,`er019_family_x_audio_production_runner_01.py` → 呼出し数を3文書の記述と突合(件数のみ)
- Grep `NO_NG_SPAN|HUMAN_REVIEW_LOCKED_NO_NG_SPAN` in `er020_tts_retry_local_rewrite_01.py` → 行番号確認(X/Y/Z横断事象の統合用)
- 成果物は`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/`に新規作成(既存ファイルは編集しない)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_02.md --json-out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_02.md_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。OPEN起票候補の確定文案(11-8分類付き)と、OPEN-528/376/312/274/525/371への追記文案を`RESULT_PACKET_TRA2.md`(9)に記載(Fableが転記)。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/REPORT_01.md`、`Y_F01_STYLE_PROFILE_CHECK_01.md`、`consolidated_01.json`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_02.md`、`..._02.md_check.json`。pathspec付きcommit。RESULT_PACKETはaddしない。
- commit message: `TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02: X/Y/Z統合報告(星取表①②全部位・フロー・A/B/C分類・OPEN候補)+Y Style profile事実確認(read-only、API 0)`
- trailer: `Delegation: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/02`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_TRA2.md`: (0)T-0、(1)結論(ユーザー§9-1: 整合しているか、1段落)、(2)星取表①の要約(Family別の総N・LR有無の件数)とREPORT_01への参照、(3)星取表②の要約(分類A/B/C件数、Zセリフの時系列)、(4)フローの差異一覧、(5)不一致・理由不明の確定一覧(統合後ID、重要度順)、(6)QCD影響と優先順位、(7)Y-F01の結論と再配達記事制作への影響、(8)ユーザー判断事項(確定、各選択肢と事実/所見)、(9)OPEN起票・追記文案、(10)3文書間の矛盾と正とした根拠、(11)RESULT_PACKET必須4行+「判定整合: 重大NG=<なし|あり>」、(12)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。