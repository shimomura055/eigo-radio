# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_01(ユーザー2026-10-20正式決定: Azure Phrase List重み2.0のAPPROVED_FOR_PRODUCTION→Production配線+test+改善対策①〜⑧の正式経路適用確認+Family Z「走れメロス」Std/Adv全TTSを正式Production経路で再生成[run_e2e_06]+試聴ページ[完成音声・全文原稿・Key Phrases]+SSOT)。2026-10-20。
並行タスク衝突確認: 並行でFAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_03(er083*、`docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/`、SSOTはOPEN-425/423/424/416行・REGISTER #125/#124/#112行・DECISION_LOG末尾・REPORT_LEDGER)が走る。本委任は**OPEN-424行・上記REGISTER行を編集しない**(本委任は新規OPEN-426・新規REGISTER #126を使い、OPEN-424へは参照のみ)。DECISION_LOG末尾・REPORT_LEDGERは共有プロトコル(編集直前に`git status --porcelain`で他agentのstaged/unstagedを確認→再Grep→自分の行のみ追記→即add→即commit、`.git/index.lock`があれば待つ)。SSOT編集権: あり(`CURRENT_SPEC.md`該当行、`OPEN_ITEMS.md`新規OPEN-426、`DECISION_LOG.md`末尾、`docs/pm/USER_DECISION_REGISTER_01.md`新規#126、`docs/pm/REPORT_LEDGER.md`)。

## Fableの前提共有と決定
- ユーザー決定(逐語は下記原文): 重み1.0→2.0を**APPROVED_FOR_PRODUCTION**。追加Trial・新品質基準は不要。Trial(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01、Fable判定REJECTED)の結果に関わらずユーザーが採用を決定したため、再判断に戻さない。ただし、Trialで観測した副作用(有効負例33wavのうち重み2.0で新規誤PASS+3件、`Mullos`→`Melos`)は**事実としてSSOTと報告に残す**(安全網=既存の`PASS_WITH_WARNING`+試聴リスト運用、変更しない)。
- 実装方針(Fable決定): `er006_secondary_asr_01.py`のAzure PhraseList生成箇所(L70-132、`PhraseListGrammar.from_recognizer`→`addPhrase`)に`phrase_list.set_weight(AZURE_PHRASE_LIST_WEIGHT)`を追加。定数`AZURE_PHRASE_LIST_WEIGHT = 2.0`はProduction既定(**flagや環境変数で切替えない=正式採用のため既定ON**)。SDK 1.50.0の`setWeight`(範囲0〜2)はTrialで送信反映(`speech.context.dgi.bias`)を実証済み(`er084_azure_phraselist_weight_trial_01_lib.py`の呼び方を踏襲)。共有`_AzureShared`経由のためTier3/CS層/非ラテンKP/Secondaryの全Azure呼出に適用され、Family X/Y/Z共通(Cross-Family共通仕様、PM_GOVERNANCE 18節)。L288の誤コメント「SDKは重みAPI非公開」を事実へ訂正。監査記録へadditiveに`azure_phrase_list_weight`(値)と`phrase_list`(語)を記録(既存キー不変、backcompat test)。
- 再生成: 新run `run_e2e_06`をrun_e2e_05から`copy_reusable_run_assets`で作成(writer/plan/support/kpは再利用、tts_b1b/tts_a2は全clip新規)。run_e2e_05は完走済みのためSTOP設置不要(run_e2e_05はそのまま履歴、試聴ページは06で更新)。Cap ¥80(run_e2e_05実績JPY28.79)。1回起動・再起動禁止(26節)。HR Lockが出たら迂回せずSTOP・報告。
- Opus独立技術レビューGate(11-3): 非該当(ユーザー採用決定済み、1定数+1呼出の追加、新構造なし。条件Cは「採用提案前」でありユーザーが既に決定)。
- 費用/日次: 当日既使用JPY143.5(出典RESULT_PACKET_PLW2b.md、並行XRG 委任_03が最大+180)/本委任見積JPY30〜50(run_e2e_06)/承認区分C(ユーザー明示指示・300円以下・日次内)。
- T-3: 上限¥80(Guardrail、`--approved-budget-jpy 80`)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止: (1)A案/A'案/P1/P2・未承認の発音判定ルール追加(⑤は既存判定の維持確認のみ)。(2)原稿の新規書き直し(承認済みRewrite[LR]の既存仕様どおりの発動は妨げない)。(3)Production量産関数以外での音声生成。(4)`git add -A/-u/-f`・amend・rebase・force push・stash。(5)wavのcommit(前例run_e2e_05=json/log/mp3のみ)。(6)OPEN-371(3NGにSecondary障害を含まない)等の未承認項目の実装。
- 修正範囲の線引き(11-8): ①〜⑧の確認で承認済み仕様と実装の乖離(未配線・不完全)を見つけたら、承認済み仕様へ戻す修正→Regression→正式経路検証まで自律実施(範囲内)。受理面・閾値・方式の新設/拡大は範囲外(判断候補として報告)。
- 時間見込み: 全体3.5〜5h(T-0 10分/配線+test+Regression 60分/①〜⑧確認表 60分[並列可]/run_e2e_06 copy+実走 30分[実走約15分]+evidence 30分/試聴ページ確認・補完 30分/SSOT 30分/報告 20分)。並列化: ①〜⑧確認表の作成はrun_e2e_06実走待機中に行う。

## 性質/到達上限Status/禁止事項
- 性質: Production配線(ユーザー承認済み)+正式Production E2E再生成+確認。
- 到達上限Status: `PL_WEIGHT_2_WIRED_MELOS_REGENERATED_PENDING_FABLE`(PRODUCTION_WIRED判定・PM Gate 3/4/5/7評価はFable。ユーザー試聴PASSは別Status=USER_LISTENING_PENDING)。
- 禁止・Cap・線引きは上記。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**保存は打ち直さずsession JSONLから抽出**(`extract_delegation_from_jsonl_01.py --role assistant --tool-use-name Agent --tool-input-field prompt --index <N>`、管理ID行に`FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_01`を含む最初のもの。index走査で特定できなければJSONL行を直接抽出)→`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_委任_01.md`。ユーザー原文は同抽出結果の`---(原文ここから)---`〜`---(原文ここまで)---`を切り出し`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_USER.md`へ(先頭メタ1行`<!-- 受領日: 2026-10-20 / 受領者: Fable(sandwich-pm) / 保存: 委任_01 -->`のみ付加)。文字数・sha256を記録。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、全委任で常時有効): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batch不使用(7-2例外非該当)。T-2追記(7-5)4点: (1)差分再生成は`--only-clips`で可能だがユーザー指示は正式経路での対象音声再生成=**意図的な全clip再生成**(重み2.0の運用証拠を全clipで取る)、(2)run内再利用は新runに`tts_generation_results.json`が無く0、Master Audio StoreはZ経路で不呼出(REGEN_PLAN_01 T-2欄で確認済み)、(3)`--approved-budget-jpy 80`明示、(4)「想定外の全再生成」に該当しない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 定型文は上記に記載済み。

## ユーザー指示(原文)
---(原文ここから)---
# Family Z メロス記事 — Azure Phrase List 2.0正式採用・TTS再生成

## 1. 目的・正式決定

ユーザーは **Azure Phrase Listの重み1.0→2.0を正式採用（APPROVED_FOR_PRODUCTION）** した。

この設定を正式Production経路へ配線し、Family Z「走れメロス」の音声を再生成して完成させる。

あわせて、今回のメロス発音問題を受けて導入・改善した対策が、すべて正式経路に反映されているか確認する。

**品質を守りながら最速で完成させること。追加Trialや新たな品質基準の設定は不要。**

## 2. 作業範囲

1. Azure Phrase Listの重みを2.0に変更し、Productionへ配線する。
2. 既存の発音対策・TTS仕様を維持する。
3. メロス記事の対象音声を正式Production経路で再生成する。
4. ASR判定から音声完成まで確認する。
5. 完成音声・全文原稿・Key Phrasesを確認できる試聴ページを用意する。

**今回、原稿の新規書き直しや、未承認の発音判定ルール追加は行わない。**

ただし、既に承認済みのRewriteが既存仕様どおり発動することは妨げない。

## 3. 今回の改善対策の全件適用確認【重要】

単にコードが存在するだけでなく、今回のメロス記事の正式Production経路で機能することを確認する。

| 確認項目 | 必須の期待動作 |
|---|---|
| ① Rewrite後の原稿同期 | `Melos said` → `He said` とRewriteした場合、最新の `He said` を正本にASR照合する。旧原稿との比較でNGにしない |
| ② TTS retry→Rewrite | 承認済みの順序・発動条件に従い、Rewriteが必要なのにHuman Reviewへ直行しない |
| ③ Pronunciation Ledger | 最新の承認済み固有名詞・許容発音情報を利用する |
| ④ Azure Phrase List | 正式経路で重み2.0を送信する。対象固有名詞は既存仕様どおり登録する |
| ⑤ 同音異表記の許容 | 綴りの違いだけで不必要なNGにしない。既存の承認済み判定を維持 |
| ⑥ 再生成・後続処理 | Rewrite後のTTS、ASR、retry、fallback、regeneration、resumeがすべて最新原稿と整合する |
| ⑦ Human Review | 承認済みの再試行・Rewriteを尽くしても自動解決できない場合のみ、既存の条件に従って送る |
| ⑧ 今回導入したその他の対策 | 上記以外にも今回のメロス問題に関連して承認・修正された対策を、CURRENT_SPEC、DECISION_LOG、実装履歴、過去のTrial報告から洗い出し、適用漏れを確認する |

特に①は、**Rewrite後も古い原稿を参照し続ける不具合が再発していないこと**を実際のテストで確認する。

既存対策が未配線・不完全なら、承認済み仕様に戻す修正として原因究明→是正→再検証まで自律的に実施する。

未承認の新仕様が必要な場合のみUSER_DECISION_REQUIREDで報告する。

## 4. Production実装・検証

- 正式初回経路だけでなく、retry／fallback／regeneration／resumeも対象とする。
- `setWeight(2.0)` が実際のAzure送信条件に反映されていることを確認する。
- Family ZのStandard／Advancedの対象音声を既存の承認済みVoice・Style・話速で生成する。
- 原稿、生成音声、ASR比較対象、判定結果の整合を確認する。
- 必須Regression、Validator、integration testを実施する。
- 正式runtimeの発火証拠、actual model_id、routing、Prompt／Style、実費を記録する。
- 関連する共通仕様への影響を確認し、Family Xなどへの既承認共通対策の配線漏れも点検する。未承認の仕様拡張は行わない。

今回の重み2.0の採用を、理由なく追加Trialや新しい採用判断待ちに戻さないこと。

## 5. 完成・受入条件

次のすべてを満たした状態で報告する。

1. 重み2.0が正式Production経路に配線・検証済み。
2. 今回の改善対策がすべて適用済み、または未適用事項と理由が明示されている。
3. メロス記事の対象音声が完成し、既存の必須品質Gateを通過。
4. 試聴ページから完成音声を再生できる。
5. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitが整合。
6. Fableが実装報告を独立確認し、PM Gate 3・4・5・7に沿って評価。

**ユーザー試聴PASSとPRODUCTION_WIREDは別Statusとして扱うこと。**

## 6. QCD・STOP条件

優先順位は **品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費**。

- 独立作業は並列化し、不要な待機・日付分割・逐次処理を避ける。
- 既存の承認済み仕様と予算枠内の修正は、自律的に完了させる。
- 重み変更による量産単価の増加は原則発生しない想定。実費で確認する。
- 明示STOP、予算上限、重大品質・安全問題、承認範囲外の変更は遵守する。
- 未承認の仕様変更、品質基準変更、重要なQCDトレードオフが必要な場合は停止してユーザー判断を求める。

## 7. 最終報告

技術的な作業履歴よりも、次の事項を優先して簡潔に報告すること。

1. **メロス記事は完成したか。試聴URL。**
2. **今回の改善対策①〜⑧はすべて入っているか。** 未適用があれば具体的に列挙。
3. 重み2.0のProduction配線・runtime証拠・判定結果。
4. 残った問題、Human Reviewの有無と理由。
5. QCD実績、Production Wiring Status、SSOT／Git反映状況。
6. 必要なユーザー判断（ある場合のみ）。

今回の目的は、重み変更の実装だけではなく、**承認済みの発音・Rewrite改善策をすべて反映したメロス記事を完成させること**である。
---(原文ここまで)---

## 作業
W1. **配線**: `er006_secondary_asr_01.py`に`AZURE_PHRASE_LIST_WEIGHT: float = 2.0`(module定数、docstringにユーザー決定日・Trial結果参照)を追加し、PhraseList生成直後に`set_weight`(SDKの実メソッド名を`dir(PhraseListGrammar)`で確認: Trial libでは`setWeight`/`set_weight`のどちらを使ったかを`er084_azure_phraselist_weight_trial_01_lib.py`からGrep)を呼ぶ。PLが空(語なし)の場合は従来どおりPL未作成(bias送信なし)。L288付近のコメントを事実(SDK 1.50.0 `setWeight`あり、範囲0〜2、2026-10-20採用2.0)へ訂正。監査: Secondary判定記録(`asr_judgement.secondary`または`attempt json`のAzure節、既存キー不変)に`azure_phrase_list_weight`と`azure_phrase_list`をadditive追加(`er078_asr_unified_backcompat_07_test_01.py`等の既存backcompat testがPASSすること)。
W2. **test**: 新規`er006_azure_phrase_list_weight_test_01.py`: (a)SDK mockで`set_weight(2.0)`が呼ばれる(PLあり)/呼ばれない(PLなし)、(b)定数が2.0で環境変数・flagに依存しない(`os.environ`書換えでも不変)、(c)監査キーadditive・旧readerが壊れない、(d)**wire evidence**: Trial libのSDK診断ログ方式(`Speech_LogFilename`)を**testではなく**1回限りのDEV確認scriptで実行し、Production関数経由のAzure呼出1回(録音2 wav、約JPY1)で送信JSONの`dgi.bias=2.0`を確認して`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/wire_evidence_prod_01.json`に抜粋保存(ログ本体はcommitしない)。Regression: per-file runner(`er058_output\unified_all_roles_production_wiring_01\patch_03b\run_tests_per_file.py`)で`er006_*_test_*.py`・`er078_*_test_*.py`・`er021_*_test_*.py`・`er020_lr_*_test_*.py`・`er003_lr_*_test_*.py`・`er084_*judge_test_02.py`(golden replay。重み付与後も本番記録の再現が崩れないこと: 記録転写注入なので判定不変の想定)を実行、既知fail 3件(er007 ja_secondary_asr ×2、er020 fullseg ×1)と区別。
W3. **①〜⑧適用確認表**(`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/MELOS_COUNTERMEASURES_APPLIED_01.md`): 各項目に「仕様(CURRENT_SPEC行)/実装(関数:行)/test(名称・件数)/正式経路runtime証拠(run_e2e_05または06の記録)/判定=適用済み/未適用(理由)」。①=`er003_lr_post_rewrite_outer_loop_fzaq8_test_01.py`(4)+fzaq2(18)+fzaq3(11)+`ITEM3_FORMAL_PATH_VERIFY_01.json`+「run_e2e_06でLR発火があれば`post_slowdown_expected_text_source`」。②=`ITEMS23_WIRING_ASSURANCE_01.md`+run_e2e_04 live発火。③=Ledger読取経路(`get_hint_for_text`)とMelos entry(`ec716e185835dba3`)の現状(confidence low→Resolver TTS注入は`min_confidence=medium`で不適用=既存仕様どおり、OPEN-318は別判断)を事実記載。④=W1/W2。⑤=`ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01.md`(既存判定維持、P1/P2未採用)。⑥=③修正の呼出元2箇所+resume/継承(`rejudge_with_current_judge`)。⑦=HR遷移条件(`finalize_a2_slowdown_final_ng`、3NG→LR→減速後NG→HR)の実装とrun_e2e_04/05の挙動。⑧=DECISION_LOG/OPEN_ITEMS/REGISTERを`Melos|メロス|FAMILY-Z-QUALITY-IMPROVEMENT-4|FAMILY-Z-AUDIO-QA`でGrepし、2026-10-19以降に承認・修正された対策(例: FZQI ①KP日本語意味の人称整合/②Std Preview・Comment=Adv方式/③Std Dialogue=Adv同一Style+6%減速/④本文語数400±70、FZAQ ②③、B3関連はX専用で対象外、OPEN-371は未承認=未適用と理由)を列挙し、各々の正式経路適用状況(run_e2e_05記録で確認)を付す。Family X: 共通module(`er006_secondary_asr_01.py`)経由でXも重み2.0が適用されること、③修正のX側呼出元(`er019_family_x_validation_inheritance_01.py:254`)を確認。
W4. **run_e2e_06**: `copy_reusable_run_assets('…/run_e2e_05','…/run_e2e_06',dry_run=False)`(dry-runで件数確認)→`run_e2e_06/writer/provenance.json`の`audio_text_deviations`が空であることを確認(05は空のはず)→`stop_scope_check_01.py --managed-id FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 --run-dir …\run_e2e_06 --out …\run_e2e_06\stop_scope_check_plwp1.json`(rc=0必須、STOP_ALL不在確認)→dry-run→`$env:TTS_EXECUTION_MODE='STANDARD'; …er026_family_z_fiction_production_runner_01.py --run run_e2e_06 --mode real --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD`(1回起動、console→`run_e2e_06/run_plwp1_console.log`)。evidence(`MELOS_REGEN_RUN_E2E_06_RECORD_01.md`): 全clipの`asr_judgement`、Secondary使用clipでの`azure_phrase_list_weight=2.0`記録、Tier3/M1/Eq Layer発動、PASS_WITH_WARNING件数、LR発火有無(+①のlive evidence)、HR有無、part3_c1の転写・判定(run_e2e_05との比較)、actual model_id/voice/style、stage別費用、原稿sha一致、gate/assemble/pages/page_verify結果。
W5. **試聴ページ**: `user_test/family_z_melos_02/`の更新後、standard.html/advanced.htmlに「完成音声の再生」「全文原稿」「Key Phrases」が含まれるか確認。欠けていれば`user_test/family_z_melos_02/review_06.html`(静的、API 0)を追加し、Std/Advの完成音声(mp3)・全文原稿(各Section)・Key Phrases一覧・PASS_WITH_WARNING clip一覧を1ページで確認できるようにする(Production pagesコードは変更しない)。commit/push後`curl.exe -I`で200確認。
W6. **SSOT**: (a)`CURRENT_SPEC.md`: Azure Secondary ASR/PhraseListの仕様行(Grep `Phrase List|PhraseList`、L2089/2139/2141付近)に「Phrase List重み=2.0(`setWeight`、2026-10-20ユーザーAPPROVED_FOR_PRODUCTION、FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01。Trial[FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01、Fable判定REJECTED]で観測した副作用[有効負例33中、重み2.0で新規誤PASS+3]はユーザーが承知のうえ採用。既存のPASS_WITH_WARNING+試聴リスト運用で監視。全Family共通)」を追記。(b)`OPEN_ITEMS.md`新規OPEN-426(Status=配線済み・run_e2e_06結果・PRODUCTION_WIRED判定はFable)。(c)`DECISION_LOG.md`末尾: ユーザー決定(原文パス・sha・文字数)+Fable決定(実装方針・Opus非該当・Cap)+結果。(d)REGISTER新規#126「判断済み(2026-10-20): Azure PL重み2.0 APPROVED_FOR_PRODUCTION(Trial REJECTED判定に対するユーザー裁定)+メロス再生成」。(e)REPORT_LEDGER。ACTIVE_TASK先頭ヘッダ。

## 事前指定Read一覧
- `er006_secondary_asr_01.py`:60-140, 270-300(PL生成・コメント)、Grep `class _AzureShared|def _azure|PhraseListGrammar|addPhrase|add_phrase`→該当範囲
- `er084_azure_phraselist_weight_trial_01_lib.py`: Grep `set_weight|setWeight|Speech_LogFilename|dgi`→該当範囲(呼び方・wire evidence抽出)
- `er084_azure_phraselist_weight_trial_01_judge_test_02.py`(全体、golden replay)
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_WIRING_ASSURANCE_01.md`・`MELOS_REGEN_RUN_E2E_05_RECORD_01.md`(全体)
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/REGEN_PLAN_01.md`:31-101(copy/実走手順)
- `docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/TRIAL_CLOSEOUT_01.md`:1-20, 44-64(副作用の事実)
- `docs/pm/RESULT_PACKET_FZAQ7.md`: Grep `pages|standard.html|advanced.html|Key Phrase`→試聴ページ構成
- `user_test/family_z_melos_02/standard.html`: Grep `<audio|script|Key|key_phrase|本文|原稿`→構成確認
- `er078_asr_unified_judge_01.py`: Grep `asr_judgement|secondary`→監査記録の組立箇所
- `CURRENT_SPEC.md`:2089, 2139, 2141(行のみ)
- `OPEN_ITEMS.md`: Grep `^- OPEN-42[4-6]`(末尾番号)、`docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #12[4-6]`(末尾番号)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep `Melos|メロス|FAMILY-Z-QUALITY-IMPROVEMENT-4|FAMILY-Z-AUDIO-QA` in `DECISION_LOG.md`・`OPEN_ITEMS.md`・`docs/pm/USER_DECISION_REGISTER_01.md`(`-n`、2026-10-19以降のエントリ)→⑧の洗い出し。
- Grep `import er006_secondary_asr_01|from er006_secondary_asr_01` in `*.py`(`*_output`除外)→共通module利用元(Family X/Z/Y)の列挙。
- `CURRENT_SPEC.md`: Grep `Phrase List|PhraseList`→該当行末尾に追記。`OPEN_ITEMS.md`: Grep `^- OPEN-425`→直後にOPEN-426。REGISTER: Grep `^- #125`→直後に#126。DECISION_LOG末尾。REPORT_LEDGER: Grep `FAMILY-Z-AZURE-PHRASELIST`→新行。
- `docs/pm/ACTIVE_TASK.md`先頭ヘッダ5行以内。

## 実行コマンド全文
- 抽出/T-0: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(index走査) → `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_委任_01.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_委任_01.md_check.json`
- 原文sha: `powershell -Command "Get-FileHash -Algorithm SHA256 docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_USER.md | Select-Object -ExpandProperty Hash; (Get-Content -Raw docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01_USER.md).Length"`
- SDKメソッド確認: `.venv\Scripts\python.exe -c "import azure.cognitiveservices.speech as s; print([m for m in dir(s.PhraseListGrammar) if 'eight' in m])"`
- 単体test: `.venv\Scripts\python.exe -m pytest er006_azure_phrase_list_weight_test_01.py er084_azure_phraselist_weight_trial_01_judge_test_02.py er078_asr_unified_backcompat_07_test_01.py -q`
- Regression: `.venv\Scripts\python.exe er058_output\unified_all_roles_production_wiring_01\patch_03b\run_tests_per_file.py --pattern "er006_*_test_*.py" --pattern "er078_*_test_*.py" --pattern "er021_*_test_*.py" --pattern "er020_lr_*_test_*.py" --pattern "er003_lr_*_test_*.py"`(runnerの実引数名は冒頭docstringで確認)
- wire evidence(DEV 1回、約JPY1): `.venv\Scripts\python.exe docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01\wire_evidence_prod_01.py --wav er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\narration\attempts\full_story_part3_c1_attempt2_customa3c4625e.wav --out docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01\wire_evidence_prod_01.json`(Production関数経由でAzureを1回呼び、SDK診断ログから`dgi.bias`を抽出。scriptは本委任で作成)
- copy: `.venv\Scripts\python.exe -c "import er063_family_z_audio_01 as a; r=a.copy_reusable_run_assets('er026_output/family_z_production_e2e_01/melos/run_e2e_05','er026_output/family_z_production_e2e_01/melos/run_e2e_06',dry_run=False); print(r['copied'],r['denied'])"`(先にdry_run=True)
- stop check: `.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_06 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_06\stop_scope_check_plwp1.json`
- dry-run: `.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_06 --mode dry-run --stage all`
- real(1回のみ): `$env:TTS_EXECUTION_MODE='STANDARD'; .venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_06 --mode real --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD`
- Pages: `curl.exe -I https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/`(review_06.htmlを作った場合はそのURLも)
- 費用: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-20`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(origin/main HEADへff-only、`git log --oneline -3 origin/main`で到達確認)

## SSOT追記文
W6のとおり(実値で埋める。PRODUCTION_WIREDは「Fable判定待ち」と書く)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1(配線+test+wire evidence、実走前): `er006_secondary_asr_01.py`、新規test、wire_evidence json/py、delegation_log 2件+check。msg: `FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01 委任_01: Azure Phrase List重み2.0をProduction配線(AZURE_PHRASE_LIST_WEIGHT=2.0、setWeight、監査キーadditive、L288コメント訂正)+test<n>+wire evidence(dgi.bias=2.0)`
- commit 2(run_e2e_06 json/log/md、試聴ページ、①〜⑧確認表)。msg: `… 委任_01: メロス Std/Adv全TTS再生成 run_e2e_06(rc=<n>、clip OK <x>/<y>、PL重み2.0 runtime記録<n>件、LR<有/無>、HR<0/n>、実費JPY<v>/80)+改善対策①〜⑧適用確認表+試聴ページ`
- commit 3(SSOT)。msg: `… 委任_01: SSOT(CURRENT_SPEC PL重み2.0/OPEN-426/DECISION_LOG/REGISTER #126/REPORT_LEDGER)`
- trailer: `Delegation: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/委任_01`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_PLWP1.md`: (1)T-0 (2)配線差分(ファイル:行)・SDKメソッド名・test結果・Regression結果(既知fail区別)・wire evidence(`dgi.bias`値) (3)①〜⑧確認表の判定一覧(適用済み/未適用+理由) (4)run_e2e_06: 開始/終了JST・rc・clip OK数・Secondary使用clipと重み記録・Tier3/M1発動・PASS_WITH_WARNING件数・LR発火(①live evidence)・HR・part3_c1転写/判定(05比較)・model_id/voice/style・費用 (5)gate/assemble/pages/page_verify・試聴URL(全文原稿・KPの有無) (6)Family X共通適用の確認 (7)費用(本委任実費・当日累計)と量産単価への影響 (8)SSOT差分 (9)Git (10)判断候補(あれば、ラベル無し) (11)失敗終了時の最終成果物(rc≠0の場合)と受入記録5項目 (12)一覧外Read理由。判定整合行1行。