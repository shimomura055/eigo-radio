## 管理ID

FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_01(ユーザー正式採用 APPROVED_FOR_PRODUCTION: Family Y Voice候補表[男性5・女性5]とVoice 1=Puckを正式Production経路へ配線し、runtime evidenceを取得。目標PRODUCTION_WIRED[判定はFable])。並行タスク衝突確認: 並行Agent 5件(TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01X/01Y/01Z[read-only、`docs/research/TTS-RETRY-…/`]、KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01[`er124_*`]、PM-SSOT-SYNC-06[SSOT編集中])。あなたの所有ファイル=`er121_family_y_*.py`(Voice表・Voice割当に関わる箇所のみ)、Y Voice Registry/設定ファイル(所在はGrepで特定)、新規test `er121_family_y_voice_table_test_01.py`、`docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/**`、`er121_output/family_y_production_01/<slug>/run_voice_puck_ev_01/`(新規run dir)、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_YVT1.md`。**SSOT編集権なし**(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER/UDR/Opus台帳は編集しない。文案はRESULT_PACKETへ)。`er063_*`(Family Z)・`er019_*`(X)・共通核(`er003_*`/`er012_b_*`/`er020_*`)は編集しない。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: **Production配線**(ユーザー承認済み仕様の実装)。到達上限Status=実装+runtime evidence取得(EVIDENCE_COLLECTED)。**PRODUCTION_WIRED判定はFable**。
- 禁止: 既存の完成音声・公開ページ・既存run dir(`run_01`等)の変更・差し替え(ユーザー原文「既存の完成音声を無断で差し替えない。今後の制作に適用する」)。Family Zの Voice表・Algiebaの変更(ユーザー原文「Family Zは変更しない」「共通仕様の統一を理由に、Family ZのAlgiebaを削除したりPuckへ変更したりしない」)。Voice選定アルゴリズムの新設(下記「設計上の線引き」)。`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`禁止。
- 費用: 上限¥60(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 費用/日次: 当日(JST 2026-10-26)既使用約JPY510(出典: RESULT_PACKET_YM7 276.13+CHKW2 9.48+CHKW3 1.67+午前分約214+FZ 40.31等)/残約JPY490(別途KP Trial Cap80進行中)/本委任見積JPY10〜25(根拠: Y Voice 1 segment[Std/Adv各1 segment]のTTS+ASR、Trial実績2.34円/take×retry見込み×2レベル+組立Gate。上限=Guardrail 60)/改善見込み高/承認区分: C(ユーザー本日正式採用・案件300円以下・日次1,000円以内)。
- Opus独立技術レビューGate(11-3): **非該当見込み**(承認済みVoice表のRegistry反映+既存経路の設定変更。ただし、Yに「候補表からの選定機構」が存在せず新設が必要と判明した場合は条件A該当=**実装前にFableへ報告してSTOP**[RESULT_PACKETに設計案を書いて終了])。
- 修正範囲の線引き(11-8): 範囲内=承認済みVoice表(男性Puck/Schedar/Fenrir/Orus/Iapetus、女性Zephyr/Kore/Leda/Sulafat/Erinome、Voice 1=Puck、AlgiebaはY候補から除外)のRegistry・Production経路・test・evidence・Dangling Reference(Algieba参照の残存)の是正。範囲外=Voice選定方式・Style・減速・retry規則の新設/変更、Voice 2/3の割当変更(現行Voice 2=Zephyr、Voice 3=Schedarは表内のため**変更しない**。変更が必要に見える場合は判断候補として報告)。
- 時間見込み: 全体約2〜2.5h(現状把握30分/Registry・経路変更+test 45分/runtime evidence 30分/文書化・commit 20分)。並列化: 現状把握と同時にtest雛形を先行。有料runは直列(1 run dirで Std→Adv の順、起動間隔150秒以上)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_DELEGATION_01.md` をN=655から順に試し、先頭が「## 管理ID」+「FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_01」で始まるものを採用(同時刻にPM-SSOT-SYNC-06も送られているため先頭一致を必ず確認。`--index -1`不可)。ユーザー指示原文(下記全文)を`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md`へ逐語保存(**あなたが作成**。SYNC-06 Agentはこれを参照する。作業の最初に作ること)。

## ユーザー指示(原文)

# Claude Codeへの指示｜Family XYZ 進行案件の決定反映・Closeout

## 1. 今回のユーザー決定：Voice候補

**Family YのVoice候補変更を正式採用（APPROVED_FOR_PRODUCTION）。**

| No. | Family Y 男性 | Family Y 女性 |
|---|---|---|
| 1 | Puck | Zephyr |
| 2 | Schedar | Kore |
| 3 | Fenrir | Leda |
| 4 | Orus | Sulafat |
| 5 | Iapetus | Erinome |

- AlgiebaはFamily Yの候補から除外。
- Family Y Voice 1はPuckを採用。
- 男性5名・女性5名の候補構成を正式仕様に反映する。
- Voice Registry、正式Production経路、必要なテスト、runtime evidence、SSOT/Gitまで整合させ、**PRODUCTION_WIRED**を目指す。
- 既存の完成音声を無断で差し替えない。今後の制作に適用する。
- Trialで判明したポーズ・再生成率の問題も記録する。

**Family Zは変更しない。**

| No. | Family Z 男性 | Family Z 女性 |
|---|---|---|
| 1 | Algieba | Zephyr |
| 2 | Schedar | Kore |
| 3 | Fenrir | Leda |
| 4 | Orus | Sulafat |
| 5 | Puck | Erinome |

ユーザーはFamily ZのAlgiebaの声を気に入っており、**Family YとFamily ZのVoice候補差分を明示的に許容した。**

この差分は承認済みFamily固有仕様としてCURRENT_SPEC／DECISION_LOG等に記録すること。

共通仕様の統一を理由に、Family ZのAlgiebaを削除したりPuckへ変更したりしない。

## 2. Chunk分割｜Family XYZ

承認済み仕様は以下。

- Family X／Y：段落境界で分割、0.2秒ポーズ。
- Family Z：おおむね70語を目安に段落境界で分割、0.2秒ポーズ。
- Standard／Advancedの両方に適用。
- Standardの既存約6%減速を維持。

**Family X/Z：** 正式runtimeで発火確認済み。残るSSOT/Git反映と証拠の最終照合を完了させる。

**Family Y：** 正式承認・配線済みだが、現行本文が1段落固定のため実記事ではChunkが発火しない。

したがって、**Family YはPRODUCTION_WIREDと判定しない。**

現状をOPEN-527等に正確に記録する。本文の段落構成や分割方式は未承認のまま変更しない。

## 3. Family Z｜文脈・感情付きTTS＋Fallback

承認済み仕様：

1. 1回目：文脈・感情付きTTS
2. 1回目NG：同方式で即時再試行
3. 2回目NG：10分待機
4. 3回目：従来方式のTTS
5. 3回目もNG：承認済みの後続回復処理との整合を確認

文脈・感情付きTTS本体および3回目Fallbackまでは正式runtime検証済み。

ただし、Local Rewriteは未配線であり、現行ではHuman Review／STOPに進む。

SSOT/Gitの最終反映を完了し、Local Rewriteについては次項の調査結果と照合すること。

Local Rewriteの新仕様を独断で追加しない。

## 4. Family XYZ｜Retry・Fallback・Local Rewrite全体調査

別途依頼済みの調査を継続する。

全Family・Standard／Advanced・全音声部位について、以下を星取表で整理する。

- 通常TTSの回数・再試行条件
- Fallbackの有無、種類、発動条件
- Local Rewriteの有無、発動条件
- Rewrite後の再TTS・品質検査
- Human Review／STOP条件
- retry／fallback／regeneration／resumeとの整合
- Rewriteを適用しない理由と、その承認・設計記録
- 承認済み仕様と正式Production実装の一致・不一致

特にRewrite不適用の理由は、既存記録で確認できるものと、Claude/Fableの新たな見解を区別すること。

差異は、承認済みの例外／仕様不一致／理由不明・未承認に分類する。

**本件は調査のみ。結果を待たずに無断でRewriteの仕様変更・Production改修を行わない。**

## 5. Key Phrase｜フレーズ7件＋単語3件Trial

既に指示済みのTrialを継続する。

- X「AIの仮想の島」
- X「英国の電車マナー」
- Z「猿の手」
- 各Standard／Advanced、計6レベル
- フレーズ・表現・Idiomを7件、単語を3件要求
- 各レベル2回実行して生成ばらつきも確認

**目的は10件を強制確保することではない。**

返答不足・Gate除外を見込んで多めに要求し、最終的に質の高い候補を6〜7件程度確保できるか評価する。

現行方式と、候補数・単語の拾い上げ・学習価値・品質・原価を比較する。

ProductionのPrompt・Gate・Human Review候補は変更しない。

Trial完了時はVALIDATED／REJECTED／USER_DECISION_REQUIREDに分類し、正式採用はユーザー判断を待つ。

## 6. PM Gate・QCD・完了条件

品質 ＞ Delivery ＞ 量産単価。

独立して進められる作業は並列化し、SSOTやコードの競合がある場合のみ必要な部分を調整する。

承認済み予算・日次上限1,000円（JST）を遵守し、不要な有料生成・追加Trialを行わない。

各案件についてFableが独立して受入評価する。

**PRODUCTION_WIREDの判定条件：**

- 承認済み仕様に一致
- 正式初回Production経路への実装
- retry／fallback／regeneration／resume整合
- 正式runtimeの発火証拠
- 必須Regression／Validator／integration test PASS
- actual model_id・routing等の必要な証拠
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- Git反映
- 未承認仕様やDangling Referenceがないこと

ユーザー承認済みでも、実装・runtime・記録のいずれかが未確認ならPRODUCTION_WIREDとしない。

**報告は案件別に、現在Status、完了事項、未完了事項、QCD影響、必要なユーザー判断のみを簡潔に示すこと。**

特に、Family Y/ZのVoice候補差分は今回正式に許容されたものであり、今後これを未承認の仕様不一致として扱わないこと。

(原文ここまで。本委任の対象は§1[Y Voice表]のみ。§2〜§5は別委任)

## 設計上の線引き(Fable指示)

1. **現状把握(API 0)**: Family YのVoice割当がどこに定義されているか(Grep `Algieba|Zephyr|Schedar|voice_name|VOICE|registry` in `er121_*.py`、`docs/research/FAMILY-Y-VOICES-DESIGN-01/**`、json/yaml設定、`CURRENT_SPEC.md`のFamily Y Voice節[Grep `Family Y.*Voice|Voice 1|Algieba`]、Z側の候補表の書式=`CURRENT_SPEC.md:1563`周辺)を特定。Yに「候補表(男性5/女性5)」という構造が既にあるか、固定3 Voice(V1/V2/V3)のみか、を事実として記録。
2. **反映方針**: (a)Yに候補表構造がある→表を承認値に置換(Algieba除外、男性1=Puck、Iapetus追加、女性5名)。(b)固定3 Voiceのみ→Voice 1の値をAlgieba→Puckへ変更し、候補表は「承認済み候補プール」としてRegistry/設定に**データとして**追加(読み取り専用の参照値。選定アルゴリズムは新設しない)。Voice 2=Zephyr/Voice 3=Schedarは表内のため不変。Voice 1〜3以外に候補表を参照する経路が必要と判明した場合(=新機構)は実装せずFableへ報告。
3. **Dangling Reference**: Y経路内の`Algieba`参照(コード・test・固定文字列・試聴ページ生成・Voice card)を全件Grepし、Production経路の残存は是正、Trial成果物(`docs/research/FAMILY-Y-VOICE1-*`、`user_test/family_y_voice*`)は履歴として**変更しない**。Z経路(`er063_*`、Z Voice表)のAlgiebaは変更しない。
4. **test**: 新規`er121_family_y_voice_table_test_01.py`(承認表との完全一致、Voice 1=Puck、Algieba非含有、Z表不変[er063側の表を読んで`Algieba`が男性1に残ること]、既存run_01のresults/公開ページを変更していないこと[sha比較]、Y/Z差分が意図的である旨のassert message)。既存er121回帰(`run_project_regression.py --pattern "er121*_test_*.py"`、遮断harness下`.venv`)で旧Voice値を固定していたtestは承認値へ更新(更新箇所を列挙)。
5. **runtime evidence(有料)**: 既存Y記事(`er121_output/family_y_production_01/redelivery_fee/`等、run_01が存在するslug)の**新規run dir** `run_voice_puck_ev_01` で、Voice 1 segment(Std/Adv)を正式CLI(`er121_family_y_runner_01.py --stage tts_a2`/`tts_b1b`+`--only-segments <Voice 1 segment id>`)で生成し、(i)actual voice name=Puck(raw_usage_log/results/audit内のvoice/model_id/routing)、(ii)Style/減速/Gate/組立が従来どおりPASS、(iii)retry/fallback/resume整合(同引数再起動で新規API 0回)、(iv)Voice 2/3のcacheが無い新run dirで他segmentが再生成されないこと(`--only-segments`で範囲限定。範囲限定不可なら実行前にSTOPし報告=T-2追記(4))、を取得。公開dir・run_01は無変更。起動前に`py tools\stop_scope_check_01.py`(rc=0)、起動間隔150秒以上(Get-Date記録)、同一run 5分3回禁止。全起動`TTS_EXECUTION_MODE=STANDARD`、`--budget-jpy 60`相当があれば明示。
6. **Trialで判明した問題の記録**: OPEN-533(Algieba Repetition旗率72%・take OK率38%)に対し、Puckの実績(fresh 24/24・平均1.21 attempt/take)と、本evidence runでの実attempt数を`EVIDENCE_01.md`に併記(SSOT文案に含める)。
7. **成果物**: `docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/{CURRENT_STATE_01,DESIGN_01,FIX_01,EVIDENCE_01,COST_01}.md`+`evidence_01.json`。

## KPI provenance欄

該当: runtime evidence=fresh(production_formal_path: 正式CLI `er121_family_y_runner_01.py` 経由、新規run dir)。E2E自己確認: Yes(Voice 1 segmentについてfresh Production初回path)。他segmentは生成しない(reuse無し・対象外)。

## Opus台帳更新

該当なし(新機構が必要と判明した場合のみFableが条件Aで起票)。

## 事前指定Read一覧

- `er121_family_y_audio_01.py`: Grep `Algieba|Zephyr|Schedar|voice|VOICE|registry` → 各±20
- `er121_family_y_runner_01.py`: Grep `def stage_tts|only_segments|--only-segments|budget|voice` → ±20
- `er121_family_y_structure_01.py`: Grep `voice|Voice` → ±10(segment idとVoice番号の対応)
- `CURRENT_SPEC.md:1550-1580`(Z Voice表の書式)、Grep `Family Y|Voice 1|Algieba|Voice card` → 該当行±10のみ(全文読込禁止)
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_01/VOICE_CARDS_01.md` 全文(短い想定)
- `docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/RESULT_01.md:1-20`、`DESIGN_01.md`: Grep `起動|コマンド|runner|--only` → ±10(Y正式CLIの起動実例の参照)
- `docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_01.md`: Grep `Y Std|driver|write_level_inputs|only_segments` → ±10(Y正式CLIの制約=本文を記事から再生成する点の確認)
- `er063_family_z_audio_01.py`: Grep `Algieba` → 該当行のみ(Z表不変の確認用、編集禁止)
- `OPEN_ITEMS.md`: Grep `OPEN-531|OPEN-533|OPEN-527` → 該当行のみ

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `Algieba` in `er121_*.py`, `*.json`(repo root・`docs/research/FAMILY-Y-*`以外)、`user_test/family_y_production*`生成コード → Production経路の残存一覧を`CURRENT_STATE_01.md`へ
- Glob `er121_output/family_y_production_01/*/run_01/` → evidence用slugの特定(公開済み記事を優先。選んだslugと理由を記録)
- Grep `voice` in `er121_output/family_y_production_01/<slug>/run_01/a2/results*.json` → actual voice記録フィールド名の特定(evidence (i)の照合キー)
- 成果物は`docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/`に新規作成

## 実行コマンド全文

- STOP確認: `py tools\stop_scope_check_01.py`
- 回帰(遮断harness、`.venv`): `.venv\Scripts\python.exe run_project_regression.py --pattern "er121*_test_*.py"`(harness起動方法はCHUNK委任_02/03の`regression_z/`記録に合わせ、使ったコマンドを全文記録)。新規test単体: `.venv\Scripts\python.exe -m pytest er121_family_y_voice_table_test_01.py -q`(遮断下)
- evidence run(有料、slug/segment idは実値へ置換して記録): `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er121_family_y_runner_01.py --slug <slug> --run run_voice_puck_ev_01 --level a2 --stage tts_a2 --only-segments <voice1_segment_id> --budget-jpy 60` → 150秒以上空けて `--level b1b --stage tts_b1b` → 150秒以上空けて同引数で再起動(API 0確認) → 必要なら`--stage gate,assemble`(公開pagesは実行しない)。runnerの実引数名が異なる場合は`--help`で確認し実値で記録。
- run_01/公開dir不変の確認: `git status --porcelain -- user_test/ er121_output/family_y_production_01/<slug>/run_01/` → 空
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。以下をRESULT_PACKET_YVT1.md(9)に文案として記載(Fableが次回syncで転記):
- CURRENT_SPEC Family Y Voice節: 承認表(男性5/女性5)・Voice 1=Puck・Voice 2=Zephyr・Voice 3=Schedar・「Family Zとの候補差分(Z男性1=Algieba、Z男性5=Puck)はユーザーが2026-10-26に明示的に許容した承認済みFamily固有仕様。共通仕様統一を理由に変更しない」・Status=<EVIDENCE_COLLECTED|PRODUCTION_WIRED(Fable判定)>・evidence path・既存完成音声は差し替えない(今後の制作に適用)。
- DECISION_LOG 1件、OPEN-531=CLOSED(採用Puck)、OPEN-533追記(Puck実績)。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: 変更した`er121_family_y_*.py`、Registry/設定ファイル、新規test、更新した既存test、`docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/`配下(md/json、wavなし)、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_{USER,DELEGATION_01}.md`(+check.json)。run dir配下はwav/raw_usage_log/STOP/lock不追跡(既存.gitignore規則に従う。evidenceの写しは`docs/research/.../evidence/`へjson/mdで)。RESULT_PACKETはaddしない。
- commit(2回可): ①`FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_01: Family Y Voice候補表(男性5/女性5)・Voice 1=Puckを正式経路へ反映(Algieba Y除外、Z不変、test、Production未公開)` ②`… evidence(Voice 1 Puck Std/Adv 正式CLI、実費<x>円、再起動API 0)`
- trailer: `Delegation: FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_YVT1.md`: (0)T-0結果・index、(1)現状(Y Voice定義の所在・構造[候補表あり/固定3 Voice]・Algieba参照の全件)、(2)反映内容(ファイル:行、方針(a)/(b)のどちらか)、(3)test(新規・更新・回帰件数・接続試行0)、(4)runtime evidence(ユーザー原文§6のPRODUCTION_WIRED判定条件9項目それぞれに対する証拠の有無をチェックリスト形式で。actual voice/model_id/routing・retry/resume整合・Gate・組立・費用)、(5)Dangling Reference結果、(6)run_01/公開dir不変の証拠、(7)Trial問題の記録(Algieba vs Puckのattempt実績)、(8)費用(起動時刻・間隔・実費・Cap比)、(9)SSOT文案、(10)判断候補(あれば)、(11)RESULT_PACKET必須4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物と目的適合[ユーザー原文§1の各行との対応]/撤去・残置)+「判定整合: 重大NG=<なし|あり>」1行、(12)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。